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
