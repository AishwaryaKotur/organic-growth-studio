# Organic Growth Studio — V1.1 (SEO + AEO)

Local-first starter product for authorized SEO audits and structured AEO readiness reviews.

## Features
- Crawls a configurable number of same-origin HTML pages, checks robots.txt and uses a conservative request delay.
- Checks HTTP status, title, meta description, H1, canonical, noindex, image alt attributes, rough text volume, JSON-LD presence and internal/external link counts.
- Creates prioritized SEO findings.
- Includes an AEO readiness checklist covering crawler access, entity clarity, answer-ready content, source transparency, structured data, third-party corroboration, buyer-prompt baselines and conversion paths.
- Exports an Excel workbook with Summary, Page Audit, SEO Findings and AEO Checklist sheets.

## Run locally
Requires Python 3.10+ and internet access on the machine running the audit.
1. Unzip the package.
2. In a terminal, open the extracted folder.
3. Run `pip install -r requirements.txt`
4. Run `streamlit run app.py`
5. Open the local URL shown in the terminal.

## Limitations
AEO readiness is a manual checklist. This version does not automatically query AI answer engines or verify citations. It also lacks JavaScript rendering, Search Console/GA4 integrations, backlink analysis, field Core Web Vitals, and keyword clustering. The diagnostic score is a heuristic, not a Google metric or ranking predictor.

Audit only sites you own or are authorized to assess. Do not bypass access controls, robots directives or rate limits. Validate findings before implementation; never promise rankings, AI citations, traffic or revenue. Use least-privilege access and never put passwords/API secrets in reports.
