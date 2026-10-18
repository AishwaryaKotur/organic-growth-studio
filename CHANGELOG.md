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

## 3.2 — Public landing/auth experience
- Reworked the unauthenticated screen into a responsive two-column SaaS landing/auth layout with an original violet/mint visual identity and product UI illustration.
- Added explicit, high-contrast sign-in/create-account tab states and clearer input placeholders.
- Updated the standalone HTML preview to mirror the same landing-page layout and visual language. The HTML form is a visual preview only; real authentication is in Streamlit.
- No fabricated performance numbers are shown in the preview illustration; the health score is intentionally blank until a real crawl is performed.

## v3.3 — Authentication contrast fix
- Explicitly force authentication input wrappers, password/email fields, placeholders, and password-visibility controls to use white surfaces and dark readable text.
- Restore clear, accessible inactive/active tab colors and consistent form submit button styling.
- Hardened standalone preview form inputs against inherited dark styles so preview and app share the same light-field design.
- Python syntax check and all 9 automated tests passed. Browser rendering of Streamlit remains unverified in this build environment.

## V3.5 — Authentication field contrast fix

- Added final, high-specificity light-theme overrides for Streamlit BaseWeb input shells and nested wrappers.
- Added explicit autofill styling so browsers do not turn entered email/password fields dark.
- Changed focused input treatment to a soft green focus ring and styled password visibility controls to remain light.
- Browser verification is still required because Streamlit is not installed in the restricted build environment.
