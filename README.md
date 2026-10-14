# Library

The one-page site at <https://library.ab-labs.io/> that gathers AB//LABS' public resources: the [AI-Enhanced OSINT](https://github.com/atlas-bear/osint-ai-guide) guide, the [Maritime and Supply Chain OSINT Tools](https://github.com/atlas-bear/osint-tools) list, the [Recommended Reading](https://github.com/atlas-bear/recommended-reading) list, and the tools and platform we build.

## How it is built

`data/resources.yml` lists the resources. `python scripts/build.py` renders `docs/index.md` and one listing file per group from it, and [Quarto](https://quarto.org/) builds the page, drawing each card with `docs/resource-card.ejs`. GitHub Actions checks that the page matches the data, builds the site in strict mode, lints the Markdown and checks the links, and deploys on every push to `main`.

To add or change a resource, edit `data/resources.yml`, run the script and open a pull request. The page itself is generated; please do not edit it by hand.

## Search index

`scripts/build_search.py` builds `docs/search-index.json`, the one index behind the search box on every site: the pages and sections of each site (from the `search.json` Quarto publishes with it), every tool on the tools list and every title on the reading list (from the listing files in their repositories), and the resources on this page. It runs at deploy time and the file is not committed. The Library rebuilds on every push here, when a site tells it a deploy has finished (a `repository_dispatch` event of type `site-deployed`, sent from the site's publish workflow with the `LIBRARY_DISPATCH_TOKEN` secret), and every Monday morning as a catch-all. To add a site, add it to `SITES` in the script and give it the script tag the [theme](https://github.com/atlas-bear/quarto-theme) README describes.

## Licence

MIT. The resources the page links to carry their own licences.
