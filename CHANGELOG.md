# Changelog

## V3.1 — Preview-aligned Streamlit UI — 2026-10-19

- Restyled the real Streamlit app with the preview's light SaaS palette, dark workspace sidebar, card-like metrics, typography, section headers, and navigation hierarchy.
- Reworked Overview around the preview's guided first steps and website-health panel, using actual saved project data rather than illustrative sample metrics.
- Renamed the Reports navigation entry to match the preview while retaining audit/report history functionality.
- Added an application breadcrumb header and preview-aligned section headers to the main workflows.
- Kept existing backend workflows and limitations explicit; no fake metrics or unimplemented automation were added.
- Validation: Python compilation passed; automated tests passed (9/9). This is not a claim of pixel-perfect rendering or full browser/end-to-end UI testing.

## Product hardening pass — 2026-10-19

- Added automated unit tests for URL normalization, same-origin boundaries, HTML SEO evidence extraction, malformed JSON-LD handling, issue evidence/action generation, and password hashing/verification.
- Added explicit product/data-source boundaries and a pre-launch checklist to the deployment documentation.
- Preserved the ₹0-initial-data-budget approach: the audit uses public HTML and robots.txt; Search Console data is currently imported from a user-exported CSV; AI visibility entries are manually observed; optional AI recommendations require a separately billed API key.

This release does not add automated third-party AI platform monitoring, direct Search Console OAuth, recurring crawls, billing, email alerts, or managed multi-user production infrastructure.

## UX correction — 2026-10-18
- Added a Streamlit light theme configuration so deployment defaults do not force dark/default styling into the app.
- Reworked primary and secondary button CSS for high contrast, consistent radius, hover feedback and accessible text contrast.
- Updated sign-in and empty-project screens to use the same branded visual language as the dashboard.
- Fixed dashboard action buttons to navigate directly to the selected workspace page by synchronizing the sidebar navigation state on rerun.
- Automated tests still cover helper functions; Streamlit browser rendering could not be run in this environment because package-index DNS/network access is unavailable.

## V3.4 — Distinctive visual system and light-field correction
- Replaced the generic violet/blue gradient identity with an original forest-green, citron, coral and warm-paper palette across the app and HTML preview.
- Reworked authentication into an asymmetric two-panel experience with a branded growth-signal visual and separate workspace form.
- Added explicit light backgrounds and readable text/placeholder colors for password, email and text fields, including BaseWeb wrapper elements that can otherwise retain a dark theme.
- Restyled tabs and primary/secondary actions for clear contrast and visible active states.
- Kept real data and demo-preview labeling distinct; no live metrics are fabricated by the login page.
- Automated tests and Python compilation pass. Streamlit browser rendering remains unverified because Streamlit is unavailable in this build environment.
