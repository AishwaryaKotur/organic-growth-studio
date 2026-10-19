# Organic Growth Studio — Guided Diagnostics Build

A Streamlit diagnostic prototype built around one primary workflow (V4.2):

**Enter one URL → automatic page discovery → Site Health (SEO) → AI Search Health → follow an evidence-backed fix plan.**

The interface is intentionally simplified. It no longer asks users to navigate a collection of separate SEO tools before they can understand their website.

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
pip install -r requirements-dev.txt
python -m pytest -q
streamlit run app.py
```

Create an account from the sign-in screen. After sign-in, enter one public website URL and run the diagnostic. The app accepts a domain with or without `https://`, normalizes to the hostname root, discovers pages from homepage links and same-origin sitemap files, and keeps the page limit internal as a safety guardrail.

## What this build actually checks

### 1. Site Health — SEO
- Automatic bounded same-origin HTML crawl seeded by homepage links and same-origin sitemap URLs found in robots.txt or common sitemap paths. The internal cap is 50 HTML pages; users do not configure it. robots.txt is parsed once per crawl for page-level decisions.
- HTTP status, title, meta description, H1 structure, canonical, noindex, image alt attributes, visible text length, JSON-LD presence and internal/external links.
- Findings show observed evidence and suggested actions.
- SEO score is a transparent internal heuristic—not a Google score or ranking forecast.

### 2. AI Search Health — technical readiness
- Checks `/robots.txt`, sitemap locations declared in robots.txt, common sitemap paths, and `/llms.txt`. Sitemap indexes are followed within bounded limits.
- Parses robots directives for ten AI/search ecosystems: OpenAI/ChatGPT Search, Anthropic/Claude, Perplexity, Google AI Overviews/Gemini, Microsoft Copilot/Bing, Meta AI, Apple, Amazon, You.com and Brave.
- Reviews crawled page signals such as structured data, headings, visible content and internal links.
- Provides fixes with separate potential SEO and AEO/AI-search benefits.
- Stores report evidence and provides CSV exports.

**Important:** AI Search Health measures technical access and content-readiness signals. It does not automatically query ChatGPT, Claude, Gemini, Perplexity or other assistants, and does not prove that a brand appears in their answers. Actual AI-answer visibility tracking still requires repeatable manual observations or a reliable, permitted data provider. A bot being allowed in robots.txt is not proof that the bot crawled, indexed, trained on, or cited the site.

## Data and cost

- No paid API key is required for the guided diagnostic checks.
- Website checks use public HTTP responses and HTML.
- The app does not render JavaScript, measure real-user Core Web Vitals, access a proprietary backlink/keyword database, or guarantee search/AI outcomes.
- `ui_preview.html` is an interactive standalone design preview. Its example report is explicitly illustrative and does not run a website crawl. The Streamlit app runs the actual diagnostic code.

## Deployment to Streamlit Community Cloud

1. Put `app.py`, `requirements.txt`, `.streamlit/config.toml`, and this README in the GitHub repository connected to the app.
2. Configure the deployed app to use `app.py` as the entry point.
3. Commit and push the intended release; Streamlit rebuilds the app from the connected repository.
4. Run the workflow on a staging deployment before replacing the current production app.

## V4.2 implementation notes

- The report stores whether the internal crawl limit was reached, so reopening a saved report preserves its partial-coverage warning.
- Sitemap discovery is bounded to 10 sitemap files and 500 candidate URLs before the 50-page crawl ceiling is applied. Sitemap entries are discovery hints, not proof of indexability.
- A bare domain such as `example.com` is accepted and defaults to HTTPS.

## Limitations before commercial launch

This is a functional prototype, not a production-hardened multi-tenant SaaS product.

- The crawler is bounded and not a full browser-rendered or large-scale crawler. Review SSRF protections and rate limits before public launch.
- Robots and sitemap checks are based on standard root paths; sitemap discovery from robots.txt and sitemap indexes is not yet comprehensive.
- AI platform rows show robots.txt permission signals, not verified crawler traffic or live AI answer results.
- No automatic daily/weekly scans, scheduled jobs, email alerts or continuously refreshed AI answer monitoring are implemented.
- Search Console OAuth/API, direct AI-provider APIs, third-party keyword/backlink data, Stripe billing and white-label agency accounts are not implemented in this guided build.
- SQLite may not persist reliably on ephemeral hosting. Move to managed PostgreSQL with migrations/backups before serving paying clients.
- Authentication is prototype-grade: no email verification, password reset, MFA or formal security review.
- Run only against websites you own or are authorized to assess. Respect robots directives, site terms and applicable laws.

## Included files

- `app.py` — Streamlit app and diagnostic engine
- `ui_preview.html` — interactive, clearly labelled UI preview
- `tests/` — deterministic helper and diagnostic tests
- `requirements.txt` — runtime dependencies
- `requirements-dev.txt` — test dependencies
- `PRODUCT_BUILD_BLUEPRINT.md` — broader product roadmap and launch gates
