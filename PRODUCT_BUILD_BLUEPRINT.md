# Organic Growth Studio — Product Build Blueprint

## Product promise
A guided organic-growth workspace that helps a business understand technical SEO health, improve content clarity, measure search performance, observe AI-search visibility, compare public competitor signals, and turn findings into a verifiable action plan.

This is an original implementation informed by common feature categories in the market. It must not copy Semrush code, exact UI, private datasets, or proprietary scoring.

## UX principles
1. Start with one question: "What website do you want to improve?"
2. Translate technical terms into plain language and provide an expandable explanation.
3. Every issue should show: affected URL, evidence, impact hypothesis, recommended fix, effort, confidence, and validation steps.
4. Separate measured data, AI-generated hypotheses, and manually recorded observations.
5. Never show fabricated performance metrics. Demo fixtures must be labelled "sample data".
6. Do not promise rankings, traffic, leads, or AI citations.
7. Keep "Run audit", "Import Search Console data", "Track AI answer", and "Create action" as obvious primary actions.
8. Provide keyboard accessibility, mobile-friendly layouts, loading states, empty states, error recovery, and CSV/report exports.

## Product modules and acceptance criteria

### 1. Onboarding and projects
- Guided setup: website URL, business category, target customer, primary offer, location/market, competitors, goals.
- Explain what is needed and why.
- Multi-project support and project-specific data separation.
- Clear permissions and consent before connecting external services.

### 2. Site health and technical audit
- Crawl authorized public sites with conservative request limits and robots.txt handling.
- URL discovery through internal links and XML sitemap.
- Report HTTP status/redirect chains, titles, meta descriptions, headings, canonicals, robots directives, indexability, image alt, internal links, orphan candidates (only if sitemap + crawl coverage supports it), hreflang, structured data validation, mixed content, broken links, duplicate metadata, URL patterns, and basic resource/page-size checks.
- Test AI bot access by parsing robots.txt for documented user agents; distinguish robots permission from actual platform usage/citation.
- Use a transparent severity model and explain the score formula.
- Support crawl limits, exclusions, crawl notes, retries and respectful rate limits.
- JS rendering, true field Core Web Vitals, backlink intelligence and massive-site crawling require additional services/infrastructure and are not implied by basic HTML crawling.

### 3. AI-assisted analysis and content optimization
- Optional OpenAI API, with key stored server-side.
- Provide business context and audit evidence to the model.
- Produce recommendations with evidence citations to the app's own crawl data, uncertainty, effort and validation.
- Content optimizer should accept an existing URL/text, target audience, topic and search intent; return proposed title/meta/H1, outline, missing subtopics, FAQ candidates and revision notes.
- Do not claim a suggested schema or FAQ is guaranteed to produce rich results.
- Keep model/version, generation timestamp and input data provenance in report metadata.

### 4. Search performance
- Initial MVP supports Search Console CSV import with schema validation and date/query/page dimensions.
- Production integration requires Google OAuth consent, Search Console API, token storage, refresh/revocation and privacy documentation.
- Show clicks, impressions, CTR and average position over time, with filters and query/page opportunity views.
- Distinguish Search Console data from estimated third-party data.

### 5. Competitor intelligence
- User enters competitor domains.
- Basic mode compares public on-page HTML and visible content.
- Better mode needs licensed keyword/backlink/rank data provider or first-party integrations; do not invent search volumes, backlinks, ranking positions, or competitor AI mentions.
- Present content gaps only when evidence exists.

### 6. AI visibility
- Track exact prompts, platform, date, market/language, observed answer, brand/competitor mentions, citations, sentiment and evidence URL.
- Manual evidence collection is the initial mode.
- Automated tracking requires approved API/provider coverage, rate/cost limits, platform terms compliance, and reproducible sampling. Different answers can vary by time, account, location and model version.
- Report sample size and coverage; don't present small samples as universal visibility.

### 7. Action center
- Turn findings into tasks with priority, owner, due date, status, effort, verification method and notes.
- Re-crawl to validate observable technical fixes.
- Keep human approval before changing production websites.

### 8. Reporting
- Executive report and detailed CSV/XLSX/PDF exports.
- Trend comparisons between completed audits.
- White-label reports require configurable brand assets.
- Scheduled reporting requires a background worker and email provider.

### 9. Commercial / SaaS
- Auth provider, verified email, password reset/MFA, tenant isolation, audit logs, usage quotas.
- Managed PostgreSQL, migrations, backups, retention/deletion.
- Stripe or another payment processor with server-verified webhooks and entitlements; UI alone is not billing.
- Worker/scheduler for crawls, queues and email notifications.
- Error monitoring, abuse prevention, secrets management, privacy policy, terms, DPA where needed, and security review.

## Current included prototype — honest status
The included `app.py` is a functional Streamlit prototype with basic account registration, projects, limited HTML crawling, heuristic SEO findings, optional OpenAI recommendations, Search Console CSV import, manual AI visibility observations, public competitor homepage checks, action tracking, audit history, and exports.

It is NOT yet a production-ready commercial SaaS. In particular, automatic AI-platform tracking, direct Google OAuth/API connection, licensed keyword/backlink data, Stripe billing, background scheduling, robust authentication, and durable managed storage are not implemented. The HTML preview is a visual mockup; its demo metrics are illustrative and its buttons do not call the backend.

## Recommended delivery gates (before public launch)
- Gate A: UX test with 5 non-SEO users; at least 4 can complete project setup and interpret one issue without help.
- Gate B: crawler test suite on owned test sites covering redirects, robots, noindex, canonicals, malformed HTML, slow responses, private IP rejection and oversized responses.
- Gate C: AI test suite verifies evidence-grounding, no invented metrics, and helpful fix instructions.
- Gate D: data integration tests for CSV edge cases and Google OAuth if added.
- Gate E: security review for tenant isolation, secrets, authentication, SSRF, abuse/rate limits and backups.
- Gate F: pricing/entitlements/webhook tests before collecting money.
- Gate G: production observability, support process, data retention and privacy/legal review.

## Deployment note
Do not replace the current public app until a staging deployment passes the delivery gates. Keep a rollback commit/tag. Streamlit Community Cloud's local file persistence may not be suitable for production client data; use managed storage for commercial operation.
