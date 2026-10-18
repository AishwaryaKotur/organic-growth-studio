# Changelog

## Product hardening pass — 2026-10-19

- Added automated unit tests for URL normalization, same-origin boundaries, HTML SEO evidence extraction, malformed JSON-LD handling, issue evidence/action generation, and password hashing/verification.
- Added explicit product/data-source boundaries and a pre-launch checklist to the deployment documentation.
- Preserved the ₹0-initial-data-budget approach: the audit uses public HTML and robots.txt; Search Console data is currently imported from a user-exported CSV; AI visibility entries are manually observed; optional AI recommendations require a separately billed API key.

This release does not add automated third-party AI platform monitoring, direct Search Console OAuth, recurring crawls, billing, email alerts, or managed multi-user production infrastructure.
