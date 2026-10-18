# Organic Growth Studio V2.0 — Organic Growth Workspace

A Streamlit application for authorized website audits and an SEO + AEO workflow. V2.0 consolidates the existing audit, optional AI recommendations, Search Console CSV analysis and manual AI visibility tracking, and adds an editable action center.

## What's included

- **Technical SEO audit:** crawls a capped number of same-origin HTML pages; checks robots.txt, uses a configurable delay, and reports HTTP status, title, meta description, H1, canonical, noindex, image alt attributes, rough text volume, JSON-LD presence and internal/external links.
- **Safer URL fetching:** normalizes common tracking parameters, preserves other query parameters, blocks private/local targets, and validates redirect destinations before requesting them.
- **Evidence-based findings:** includes evidence, recommended action, why it may matter, effort and confidence; severity remains a triage heuristic and requires human review.
- **Action Center:** editable status field for each finding, exportable as CSV. Task status is session-only; export the CSV to preserve it. No persistent database is included.
- **Optional AI recommendations:** uses OpenAI API to draft context-aware explanations and proposed fixes from selected audit evidence and business context. Configure `OPENAI_API_KEY`; AI remains optional.
- **Search performance:** import a standard Google Search Console Performance CSV and inspect clicks, impressions, CTR, average position and query opportunities where columns are available. This is CSV import, not a direct Google OAuth/API connection.
- **AI visibility tracking:** download a template, manually run fixed buyer prompts on selected AI platforms, record mentions/citations/competitors, then upload results for mention-rate summaries. This does not automatically query AI platforms.
- **Exports:** Excel audit workbook, AI recommendation CSV, action plan CSV, normalized Search Console CSV, and AI visibility template/results CSV.

## Run locally

Requires Python 3.10+ and internet access.

1. Extract the ZIP and open a terminal in this folder.
2. Install dependencies: `pip install -r requirements.txt`
3. Start the app: `streamlit run app.py`
4. Open the local URL shown in the terminal.

## Optional AI setup

Set `OPENAI_API_KEY` in your environment or Streamlit Community Cloud → App settings → Secrets:

```toml
OPENAI_API_KEY = "your-api-key-here"
```

Never commit a real key to GitHub or include it in screenshots. OpenAI API usage is billed separately from ChatGPT subscriptions. The AI feature sends the website URL, user-provided business context, selected page metadata and up to 25 findings to the configured API. Do not send confidential or personal data. Review every suggestion before implementation.

## Deploying to Streamlit Community Cloud

Upload the files in this folder to the root of your GitHub repository and set the main file path to `app.py`. Keep the repository private while testing. The app currently has no user authentication, tenant isolation, persistent database, billing or per-client access controls; do not expose it as a public multi-client service until these are implemented.

## Limitations and responsible use

- No JavaScript rendering, direct Search Console API/OAuth, GA4 integration, backlink index, field Core Web Vitals, persistent projects/task history, or automatic AI-platform querying/citation verification.
- The diagnostic score is a heuristic triage aid, not a Google metric, ranking forecast or guarantee.
- Search Console data must be exported by an authorized property user. AI visibility is manually observed and varies by prompt, date, location, account and model version.
- Audit only public sites you own or are authorized to assess. Respect robots.txt, site terms and reasonable crawl rates. Do not promise rankings, AI citations, traffic or revenue.
