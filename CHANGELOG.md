# Changelog

## Guided Diagnostics build — 2026-10-19
- Replaced the post-login multi-tool navigation with a guided URL → scope → diagnostics workflow.
- Runs Site Health (SEO) first and AI Search Health technical-readiness checks second.
- Added ten AI/search ecosystem rows based on robots.txt user-agent rules, plus checks for sitemap.xml, llms.txt, structured-data coverage, content structure and internal linking.
- Findings explain evidence, how to fix the issue, possible SEO benefit, possible AEO benefit and expected gain with explicit uncertainty.
- Added persistent diagnostic report history and CSV exports for page evidence and the fix plan.
- Updated the interface to a distinct botanical palette (forest, citron, warm ivory) rather than copying another vendor's branding or exact UI.
- Added deterministic tests for SEO scoring bounds and AI-readiness report structure.
- Clarified limitations: technical AI readiness is not live AI-answer visibility; scheduled scans, direct AI queries and provider integrations are not implemented.


## V4.1 — Single-input diagnostic flow
- Removed user-facing crawl-scope and maximum-page controls.
- The user enters one website URL; the app normalizes the scan to the entered hostname and discovers accessible same-origin pages automatically.
- Set the crawl ceiling internally to 50 HTML pages as a safety/performance guardrail.
- Updated report language, sidebar steps, README and standalone preview to match the simplified flow.
- The report still discloses how many pages were actually inspected; this is a bounded crawl, not a guarantee of complete site coverage.


## V4.2 — Automatic discovery and scan reliability
- Accepts a bare domain or full URL and normalizes it to the hostname root.
- Seeds the crawl with same-origin sitemap URLs discovered from robots.txt and common sitemap paths, then follows internal links.
- Follows sitemap indexes within bounded limits (10 sitemap files, 500 candidate URLs); external sitemap URLs are excluded.
- Parses robots.txt once per crawl instead of re-downloading it for every page.
- Persists enough coverage metadata to preserve partial-scan warnings when a report is reopened.
- Added regression tests for bare-domain input, sitemap parsing, malformed XML and rejecting cross-origin sitemap URLs.
- Automated suite: 17 tests passing; Python compilation passed. Browser rendering and a live crawl remain unverified in this environment.
