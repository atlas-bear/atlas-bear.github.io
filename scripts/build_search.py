#!/usr/bin/env python3
"""Build the Library's search index: one JSON file of documents from every site.

The theme's library-search.js fetches this file and searches it in the browser.
Sources, in the order the results are grouped:

- the pages and sections of each site, from the search.json Quarto publishes
  with every site;
- every tool on the tools list and every title on the reading list, from the
  listing files in their repositories (one document per entry, so a tool or a
  book is a result in its own right, not just the page it sits on);
- the resources on this page, from data/resources.yml.

    python scripts/build_search.py            # writes docs/search-index.json

The file is generated at deploy time and is not committed. If a site cannot be
fetched, its documents are taken from the index already published; if that is
missing too, the build fails rather than publish an index with a site missing.
"""
import datetime
import json
import pathlib
import re
import sys
import time
import urllib.request

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / "docs" / "search-index.json"
LIVE = "https://library.ab-labs.io/search-index.json"
UA = "atlas-bear-library-search/1.0 (+https://github.com/atlas-bear/atlas-bear.github.io)"
SITES = [
    ("library", "Library", "https://library.ab-labs.io/"),
    ("guide", "AI-Enhanced OSINT", "https://library.ab-labs.io/osint-ai-guide/"),
    ("tools", "Maritime and Supply Chain OSINT Tools", "https://library.ab-labs.io/osint-tools/"),
    ("reading", "Recommended Reading", "https://library.ab-labs.io/recommended-reading/"),
]
LISTINGS = {
    "tools": ("https://raw.githubusercontent.com/atlas-bear/osint-tools/main/docs/listing.yml", "tool"),
    "reading": ("https://raw.githubusercontent.com/atlas-bear/recommended-reading/main/docs/listing.yml", "title"),
}


def fetch(url, tries=3):
    last = None
    for i in range(tries):
        try:
            req = urllib.request.Request(url + ("&" if "?" in url else "?") + f"v={int(time.time())}", headers={"User-Agent": UA, "Cache-Control": "no-cache"})
            with urllib.request.urlopen(req, timeout=60) as r:
                return r.read().decode("utf-8")
        except Exception as e:  # noqa: BLE001
            last = e
            time.sleep(3 * (i + 1))
    raise RuntimeError(f"{url}: {last}")


def slug(text):
    return re.sub(r"[^a-z0-9]+", "-", str(text).lower()).strip("-")


def clean(text):
    return re.sub(r"\s+", " ", str(text or "")).strip()


def sections(key, base):
    """One document per page or section from the site's own search index."""
    docs = []
    for e in json.loads(fetch(base + "search.json")):
        text = clean(e.get("text"))
        if not text and not e.get("section"):
            continue
        docs.append({
            "id": f"{key}:{e['href']}",
            "source": key,
            "type": "section" if e.get("section") else "page",
            "title": clean(e.get("section")) or clean(e.get("title")),
            "section": clean(e.get("title")) if e.get("section") else "",
            "meta": "",
            "text": text,
            "url": base + e["href"],
        })
    return docs


def entries(key, base, url, kind):
    """One document per tool or title from the repository's listing file."""
    docs = []
    for e in yaml.safe_load(fetch(url)):
        cats = e.get("categories") or []
        docs.append({
            "id": f"{key}:{e['path']}:{slug(e['title'])}",
            "source": key,
            "type": kind,
            "title": clean(e["title"]),
            "section": clean(cats[0]) if cats else "",
            "meta": clean(e.get("subtitle")),
            "text": clean(e.get("description")),
            "url": base + e["path"],
        })
    return docs


def resources():
    with (ROOT / "data" / "resources.yml").open(encoding="utf-8") as fh:
        groups = yaml.safe_load(fh)["groups"]
    docs = []
    for g in groups:
        for r in g["resources"]:
            docs.append({
                "id": f"library:{slug(r['title'])}",
                "source": "library",
                "type": "resource",
                "title": clean(r["title"]),
                "section": clean(g["title"]),
                "meta": "",
                "text": clean(r["line"]),
                "url": r["site"],
            })
    return docs


def previous(key):
    """The documents of one source from the index already published, as a fallback."""
    try:
        data = json.loads(fetch(LIVE))
        return [d for d in data["docs"] if d["source"] == key] or None
    except Exception:  # noqa: BLE001
        return None


def main():
    docs, problems = [], []
    for key, title, base in SITES:
        got = []
        try:
            if key == "library":
                got = resources()
            else:
                got = sections(key, base)
                if key in LISTINGS:
                    got += entries(key, base, *LISTINGS[key])
            print(f"{key}: {len(got)} documents")
        except Exception as e:  # noqa: BLE001
            print(f"{key}: {e}", file=sys.stderr)
            got = previous(key)
            if got is None:
                problems.append(key)
            else:
                print(f"{key}: reused {len(got)} documents from the published index", file=sys.stderr)
        docs += got or []
    if problems:
        print(f"build failed: no documents for {', '.join(problems)}", file=sys.stderr)
        return 1
    out = {
        "built": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "sources": [{"key": k, "title": t, "url": u} for k, t, u in SITES],
        "docs": docs,
    }
    OUT.write_text(json.dumps(out, ensure_ascii=False, separators=(",", ":")) + "\n", encoding="utf-8")
    print(f"wrote {OUT.relative_to(ROOT)}: {len(docs)} documents, {OUT.stat().st_size // 1024} KB")
    return 0


if __name__ == "__main__":
    sys.exit(main())
