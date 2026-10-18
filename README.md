# Organic Growth Studio V3.1 — Preview-aligned Streamlit UI

A Streamlit-based organic growth workspace with a redesigned, preview-aligned light SaaS interface and real project-backed workflows: technical SEO auditing, optional OpenAI recommendations, Search Console CSV imports, manually recorded AI visibility observations, competitor homepage comparisons, action tracking, and project/audit history.

## Run locally

Python 3.10+ recommended.

```bash
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

Open the local URL shown by Streamlit. Create an account from the sign-up screen.

## Enable AI analysis

Set a secret/environment variable:

```toml
OPENAI_API_KEY = "your-api-key"
OPENAI_MODEL = "gpt-4.1-mini"
```

For Streamlit Community Cloud, put these in App → Settings → Secrets. Never commit API keys. API usage is billed separately from a ChatGPT subscription.

## Deploy to Streamlit Community Cloud

1. Upload `app.py`, `requirements.txt`, and `README.md` to the root of a GitHub repository.
2. In Streamlit Community Cloud, create/redeploy the app using `app.py` as the main file.
3. Configure the OpenAI secret only if you want AI recommendations.
4. Create an account and a project.

## Features included

- Account registration/sign-in with PBKDF2 password hashing (prototype-grade auth)
- Multiple projects per account, local SQLite persistence
- Limited same-origin HTML crawler, robots.txt check, request delay and public-host checks
- SEO checks: HTTP status, title, description, H1, canonical, noindex, image alt, text volume, JSON-LD presence, internal links
- Findings with priority, evidence and recommended action
- Optional OpenAI grounded audit recommendations
- Search Console CSV import and query summaries
- Manual AI visibility observation tracking with mention/citation rates
- Competitor homepage on-page signal comparison
- Action center, task status tracking, audit and AI report history
- CSV exports

## Important limitations — read before commercial use

This is a V3 product prototype, not a fully production-hardened SaaS service.

- AI visibility tracking is manual; there is no automatic querying of ChatGPT, Gemini, Perplexity or Google AI Overviews.
- Search Console integration imports CSV exports; OAuth/API connection is not implemented.
- Competitor analysis is limited to public homepage HTML; there is no keyword database, backlink index, search-volume provider or rank tracker.
- Subscription table/UI is informational only. Stripe payments, webhooks, entitlements and invoices are not implemented.
- Scheduled scans and notifications are not run automatically. Use an external scheduler/worker and email provider before promising recurring reports.
- SQLite is appropriate for a single-user/small prototype. Streamlit Community Cloud local storage may be ephemeral; use managed PostgreSQL and persistent storage for real client data.
- Authentication lacks email verification, password reset, MFA, session hardening and formal security review. Do not use this prototype to store sensitive data or present it as enterprise-secure.
- The crawler has conservative protections but has not undergone a security audit. Audit only sites you own or have explicit permission to assess.
- SEO findings and scores are heuristic. They do not predict rankings, traffic, AI citations or leads.
- The app does not render JavaScript, measure field Core Web Vitals, access backlinks, or automatically modify websites.
- Respect site terms, robots directives, privacy requirements, API terms and data-provider licenses.

## Recommended production hardening

1. Move authentication to a mature identity provider or add verification/reset/MFA.
2. Move data to managed PostgreSQL and add tenant-level authorization tests.
3. Add a background worker and scheduler for crawling and notifications.
4. Implement Google OAuth/Search Console API with explicit consent.
5. Add approved AI-search data sources or clearly documented manual observation workflows.
6. Integrate Stripe checkout and webhook-verified subscription entitlements.
7. Add monitoring, backups, rate limits, security review, privacy policy and terms of service.

## Project layout

- `app.py` — Streamlit application
- `requirements.txt` — dependencies
- `README.md` — setup, deployment and limitations


## Product build blueprint
See `PRODUCT_BUILD_BLUEPRINT.md` for the full feature specification, acceptance criteria, architecture requirements, and production launch gates. `ui_preview.html` remains the original static visual reference. The Streamlit interface has now been restyled to follow its visual language and its Overview/feature hierarchy. Streamlit-native components mean it is not pixel-identical to standalone HTML, but the hosted Python app—not the HTML mockup—is the source of truth for functionality. The live interface uses project-backed data and avoids the mock metrics from the preview.

## Run tests

```bash
python -m pip install -r requirements.txt
python -m pip install pytest
python -m pytest -q
```

The tests cover actual helper-function definitions from `app.py` without launching the Streamlit UI.

## Current implementation boundaries (read before client use)

- **Implemented:** user registration/sign-in for a prototype, project-scoped SQLite records, a bounded same-origin HTML diagnostic crawl, heuristic issue list with evidence and suggested actions, CSV import for exported Search Console data, manual AI-answer observations, homepage-level competitor signal comparison, task tracking, CSV downloads and history.
- **Optional paid integration:** OpenAI API-powered recommendations, only when an API key is configured. API use is billed separately by the provider.
- **Not implemented:** Search Console OAuth/API sync, automated live checks across ChatGPT/Perplexity/Gemini, reliable backlink/keyword databases, scheduled crawling, notifications, Stripe billing, team roles, managed database, enterprise SSO, formal security audit, or production-grade account recovery/rate limiting.
- **Diagnostic score:** heuristic, based on detected issues. It is not a Google metric and does not predict rankings, citations or leads.

## Deployment and security gates

This is a preview/early validation build, not a production SaaS for sensitive customer data. Before inviting paying customers, configure persistent private storage, backups, HTTPS and secrets; add rate limiting and account recovery; harden DNS/IP validation against rebinding; set explicit crawl limits and robots behavior; add monitoring and dependency scanning; run tests against a staging deployment; and obtain a security review. Do not commit API keys or customer exports to Git.

On Streamlit Community Cloud, local SQLite files may not be durable across rebuilds/redeployments. Use a persistent database/storage service before relying on this for business-critical data.
