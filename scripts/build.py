#!/usr/bin/env python3
"""Render docs/index.md, the one page of the Atlas Bear Library, from data/resources.yml.

    python scripts/build.py          # rewrite docs/index.md
    python scripts/build.py --check  # exit 1 if docs/index.md is out of date
"""
import pathlib
import re
import sys

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
DATA = ROOT / "data" / "resources.yml"
PAGE = ROOT / "docs" / "index.md"


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


def card(r):
    links = [f"[Website]({r['site']})" if r["site"] != r["repo"] else None, f"[Repository]({r['repo']})"]
    links += [f"[{l['label']}]({l['url']})" for l in r.get("links", [])]
    links = " · ".join(x for x in links if x)
    badge = f"![Last commit](https://img.shields.io/github/last-commit/{r['badge']})"
    return (f"- **[{r['title']}]({r['site']})**\n\n"
            f"    ---\n\n"
            f"    {r['line']}\n\n"
            f"    {links}\n\n"
            f"    {badge}\n")


def render(groups):
    out = ["---", "hide:", "  - navigation", "  - toc", "---", "",
           "<!-- GENERATED FILE. Do not edit by hand. Edit data/resources.yml and run: python scripts/build.py -->", "",
           "# Atlas Bear Library", "",
           "Everything Atlas Bear Labs publishes in the open, on one page: a guide to using AI in intelligence work, "
           "a verified list of maritime and supply chain OSINT tools, a cited reading list, and the tools and platform "
           "we build. Each card opens the resource; the repository link is where to propose changes.", ""]
    for g in groups:
        out += [f"## {g['title']}", "", '<div class="grid cards" markdown>', ""]
        out += [card(r) for r in g["resources"]]
        out += ["</div>", ""]
    out += ["## Who we are", "",
            "[Atlas Bear](https://atlasbear.co) provides intelligence advisory and operational support to organisations working in "
            "difficult markets, with a focus on international trade, maritime security and supply chains. Atlas Bear Labs is where we "
            "build and share tools, and the [Atlas Bear Academy](https://www.atlasbear.academy) is where we teach. Much of what is on "
            "this page is used each year at the [Summer School on Illicit Trade](https://www.rug.nl/education/summer-winter-schools/illicit-trade).", "",
            "## Contributing", "",
            "Every resource has an issue form for proposals and corrections, written criteria for what goes in, and a changelog. "
            "We sweep the guide and the lists twice a year, in spring and autumn, and release each sweep. Pull requests are welcome; "
            "the repositories explain the format. Please keep to our [community guidelines](https://github.com/atlas-bear/.github/blob/main/profile/COMMUNITY_GUIDELINES.md).", "",
            "## Contact", "",
            "[support@atlasbear.co](mailto:support@atlasbear.co) for anything about these resources. "
            "[Waterline](https://maraiq.substack.com/) is our newsletter.", ""]
    return "\n".join(out)


def main():
    text = render(load())
    if "--check" in sys.argv:
        current = PAGE.open(encoding="utf-8", newline="").read() if PAGE.exists() else ""
        if current != text:
            print("docs/index.md is out of date. Run: python scripts/build.py", file=sys.stderr)
            return 1
        print("docs/index.md matches data/resources.yml")
        return 0
    PAGE.parent.mkdir(parents=True, exist_ok=True)
    with PAGE.open("w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    print("wrote docs/index.md")
    return 0


if __name__ == "__main__":
    sys.exit(main())
