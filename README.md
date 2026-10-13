# Atlas Bear Library

The one-page site at <https://atlas-bear.github.io/> that gathers Atlas Bear Labs' public resources: the [AI-Enhanced OSINT](https://github.com/atlas-bear/osint-ai-guide) guide, the [Maritime and Supply Chain OSINT Tools](https://github.com/atlas-bear/osint-tools) list, the [Recommended Reading](https://github.com/atlas-bear/recommended-reading) list, and the tools and platform we build.

## How it is built

`data/resources.yml` lists the resources. `python scripts/build.py` renders `docs/index.md` from it, and [MkDocs Material](https://squidfunk.github.io/mkdocs-material/) builds the page. GitHub Actions checks that the page matches the data, builds the site in strict mode, lints the Markdown and checks the links, and deploys on every push to `main`.

To add or change a resource, edit `data/resources.yml`, run the script and open a pull request. The page itself is generated; please do not edit it by hand.

## Licence

MIT. The resources the page links to carry their own licences.
