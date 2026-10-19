# Organic Growth Studio V4.2 — Single URL diagnostic engine

## User workflow
Enter one website URL (a bare domain is accepted) and click **Run website diagnostic**. The app normalizes to the hostname root and runs:
1. Site Health (SEO)
2. AI Search Health (technical readiness)
3. Combined evidence-backed fix plan

No page-limit or crawl-scope controls are shown to the user.

## Engine improvements
- Homepage and internal-link discovery plus same-origin sitemap discovery from robots.txt/common sitemap paths.
- Sitemap index parsing, bounded to 10 sitemap files and 500 candidate URLs.
- Internal scan ceiling of 50 HTML pages, with partial-coverage disclosure when reached.
- Robots policy is fetched and parsed once per crawl.
- Saved reports reconstruct their coverage warning from stored crawl notes.
- Same-origin restrictions are applied to sitemap URLs; external sitemap entries are ignored.

## Verification performed
- `python -m py_compile app.py`: passed.
- `python -m pytest -q`: 19 passed.
- ZIP integrity: verified after packaging.

## Not verified / not included
- Streamlit browser rendering and live website crawl were not run in this environment because Streamlit is not installed here and package-index network access has previously failed.
- AI Search Health checks technical access/readiness; it does not query ten assistants or claim live brand visibility.
- No scheduled scans, live AI answer tracking, Search Console OAuth, paid keyword/backlink datasets, billing, or production-grade multi-tenant security are included.
