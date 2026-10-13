#!/usr/bin/env python3
"""Render the Library page from data/resources.yml.

Writes docs/index.md (the page, with one Quarto listing per group) and one
docs/listing-<group>.yml per group (the cards, rendered by resource-card.ejs).

    python scripts/build.py          # rewrite the generated files
    python scripts/build.py --check  # exit 1 if any generated file is out of date
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "resources.yml"
DOCS = ROOT / "docs"
HEADER = "<!-- GENERATED FILE. Do not edit by hand. Edit data/resources.yml and run: python scripts/build.py -->\n\n"


def slug(text):
    s = re.sub(r"[^\w\s-]", "", text.strip().lower())
    return re.sub(r"\s+", "-", s)


def load():
    with DATA.open(encoding="utf-8") as fh:
        groups = yaml.safe_load(fh)["groups"]
    errors = []
    for g in groups:
        if not g.get("title") or not g.get("resources"):
            errors.append("a group needs a title and resources")
        for r in g.get("resources", []):
            for k in ("title", "line", "site", "repo", "badge"):
                if not r.get(k):
                    errors.append(f"{r.get('title', '?')}: missing {k}")
            for u in [r.get("site"), r.get("repo")] + [l.get("url") for l in r.get("links", [])]:
                if u and not str(u).startswith("https://"):
                    errors.append(f"{r.get('title', '?')}: link must start with https:// ({u})")
            if "—" in r.get("line", ""):
                errors.append(f"{r.get('title', '?')}: em dash in line")
    if errors:
        raise SystemExit("build failed:\n" + "\n".join(errors))
    return groups


def links_html(r):
    links = []
    if r["site"] != r["repo"]:
        links.append(f'<a href="{r["site"]}">Website</a>')
    links.append(f'<a href="{r["repo"]}">Repository</a>')
    links += [f'<a href="{l["url"]}">{l["label"]}</a>' for l in r.get("links", [])]
    return " · ".join(links)


def listing_yaml(group):
    rows = [{"title": r["title"], "line": r["line"], "site": r["site"], "repo": r["repo"],
             "badge": r["badge"], "links_html": links_html(r)} for r in group["resources"]]
    return ("# GENERATED FILE. Do not edit by hand. Edit data/resources.yml and run: python scripts/build.py\n"
            + yaml.safe_dump(rows, allow_unicode=True, sort_keys=False, width=1000))


def page(groups):
    listings = "".join(
        f"  - id: {slug(g['title'])}\n    contents: listing-{slug(g['title'])}.yml\n    template: resource-card.ejs\n    sort: false\n"
        for g in groups)
    out = ["---", 'title: "Library"',
           'description: "Public guides, lists and tools from AB//LABS, gathered on one page."',
           "listing:", listings.rstrip("\n"), "toc: false", "---", "", HEADER.rstrip("\n"), "",
           "Everything [AB//LABS](https://ab-labs.io) publishes in the open, on one page: a guide to using AI in intelligence work, "
           "a verified list of maritime and supply chain OSINT tools, a cited reading list, and the tools and platform "
           "we build. Each card opens the resource; the repository link is where to propose changes.", ""]
    for g in groups:
        out += [f"## {g['title']}", "", f"::: {{#{slug(g['title'])}}}", ":::", ""]
    out += ["## Who we are", "",
            "[AB//LABS](https://ab-labs.io) provides intelligence and support across maritime, defence and logistics: vessel tracking "
            "and port assessments, operational intelligence before and during deployments, threat and risk analysis, and advisory work "
            "on building analytical capability. The tools and lists on this page come out of that work.", "",
            "AB//LABS began as Atlas|Bear Labs, the technical side of [Atlas|Bear](https://atlasbear.co), and is now a company of its own. "
            "The two still work together, and our repositories keep the `atlas-bear` name on GitHub for now. Atlas|Bear's "
            "[Academy](https://www.atlasbear.academy) runs the professional development programmes our people teach on, and much of what "
            "is on this page is used each year at the [Summer School on Illicit Trade](https://www.rug.nl/education/summer-winter-schools/illicit-trade).", "",
            "[Atlas|Bear](https://atlasbear.co) provides intelligence advisory and operational support to organisations deploying people, "
            "technology and capital in difficult markets, with the fieldwork, logistics and professional services that need specialist "
            "knowledge. Every Atlas|Bear engagement supports independent fieldwork, impact investment and critical projects in vulnerable "
            "communities worldwide, simply by operating within its network.", "",
            "The [Atlas|Bear Academy](https://www.atlasbear.academy) runs training and professional development for people who want to do "
            "this work well, online and in person; our people teach on it. [The Mombasa Method](https://www.atlasbear.academy/course/the-mombasa-method) "
            "is its flagship on-demand programme. For custom training, write to [courier@atlasbear.co](mailto:courier@atlasbear.co).", "",
            "## Contributing", "",
            "Every resource has an issue form for proposals and corrections, written criteria for what goes in, and a changelog. "
            "We sweep the guide and the lists twice a year, in spring and autumn, and release each sweep. Pull requests are welcome; "
            "the repositories explain the format. Please keep to our [community guidelines](https://github.com/atlas-bear/.github/blob/main/profile/COMMUNITY_GUIDELINES.md).", "",
            "## Contact", "",
            "[support@ab-labs.io](mailto:support@ab-labs.io) for anything about these resources. "
            "[Waterline](https://maraiq.substack.com/) is our newsletter.", ""]
    return "\n".join(out)


def outputs(groups):
    files = {DOCS / "index.md": page(groups)}
    for g in groups:
        files[DOCS / f"listing-{slug(g['title'])}.yml"] = listing_yaml(g)
    return files


def main():
    files = outputs(load())
    if "--check" in sys.argv:
        stale = [str(p.relative_to(ROOT)) for p, want in files.items()
                 if not p.exists() or p.open(encoding="utf-8", newline="").read() != want]
        if stale:
            print(f"out of date: {', '.join(stale)}. Run: python scripts/build.py", file=sys.stderr)
            return 1
        print(f"generated files match data/resources.yml ({len(files)} files)")
        return 0
    for p, want in files.items():
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("w", encoding="utf-8", newline="") as fh:
            fh.write(want)
    print(f"wrote {len(files)} files")
    return 0


if __name__ == "__main__":
    sys.exit(main())
