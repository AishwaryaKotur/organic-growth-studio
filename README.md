# Organic Growth Studio — V1.3 (SEO + AI SEO Recommendations)

A Streamlit starter product for authorized website audits. V1.3 adds optional AI-assisted recommendations grounded in crawler findings and user-provided business context.

## Features
- Crawls a configurable number of same-origin HTML pages, checks robots.txt, and uses a configurable delay.
- Normalizes common tracking parameters while preserving other query parameters.
- Checks HTTP status, titles, meta descriptions, H1, canonical, noindex, image alt attributes, rough text volume, JSON-LD presence, and internal/external link counts.
- Findings include evidence, recommended action, why it matters, potential impact, effort, and confidence.
- Optional AI recommendations: context-aware explanations, fixes, draft metadata/content examples and verification steps. The model receives selected page metadata and up to 25 findings, not the full page HTML.
- Exports the existing audit workbook and allows AI recommendations to be downloaded as CSV.
- AEO readiness remains a manual checklist; this version does not query AI answer engines or verify citations.

## Run locally
Requires Python 3.10+ and internet access.
1. Unzip the package and open a terminal in the folder.
2. Run `pip install -r requirements.txt`.
3. Run `streamlit run app.py`.
4. Open the local URL shown in the terminal.

## Configure AI
Set `OPENAI_API_KEY` in your environment or in Streamlit Community Cloud → App settings → Secrets, for example:

```toml
OPENAI_API_KEY = "your-api-key-here"
```

Never commit a real API key to GitHub or put it in source code. OpenAI API usage is billed separately from ChatGPT subscriptions. AI recommendations are optional; the audit works without a key. Model output may be wrong, so review every recommendation before implementation. The app sends the target website URL, user-entered business context, selected page metadata and up to 25 audit findings to the configured API. Do not send confidential or personal data.

## Limitations
No JavaScript rendering, Search Console/GA4 integration, backlink analysis, field Core Web Vitals, or automated AI-answer/citation monitoring. The diagnostic score is a triage heuristic only. Crawling is limited to fetched HTML pages. Audit only sites you own or are authorized to assess; respect robots directives and rate limits. Never promise rankings, AI citations, traffic or revenue.
