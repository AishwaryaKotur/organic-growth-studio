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


## V1.4 Search Performance
Use Google Search Console to export a Performance CSV for a selected property/date range, then upload it in the **Search performance** tab. The app summarizes clicks, impressions, CTR and (when present) average position. This is a CSV import workflow, not a direct Google OAuth/API connection. Standard query/page CSV exports are supported; bulk export workbooks may need to be exported as a single CSV first.

## V1.5 AI Visibility
Download the AI visibility CSV template, test the same buyer prompts manually in the listed AI platforms, record brand mentions and cited URLs, then upload the completed CSV in the **AI visibility** tab. The app calculates mention rate and platform summaries when the expected columns are present. It does not automatically query AI platforms or guarantee complete/representative results.

## Security and interpretation
- Do not upload credentials or confidential customer information.
- Search Console data should be exported only by someone authorized to access the property.
- AI visibility results are manually observed and vary by prompt, date, account, region and model.
- SEO diagnostic scores and visibility rates are descriptive signals, not ranking or revenue guarantees.
