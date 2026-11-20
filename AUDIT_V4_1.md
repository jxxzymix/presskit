# JXXZY V4.1 — Signature Racing | Release audit

## Remote baseline and blocker
- Main: `d91d687a7799291b54968dee961347e662270b23`.
- Previous V4 deployment run `44683874030` failed at Playwright installation: the default Ubuntu 26.04 runner was not supported by Playwright 1.57.0.
- Before the failed browser step, CI confirmed 46/46 original assets, 35 actual image dimensions, full EPK 22 pages/41 image references/45 links, quick EPK 3 pages/3 image references/4 links. No V4 deployment followed this run. Last successful deployment inspected was V3.
- Both Git tree creation and Contents API update were denied with HTTP 403. No remote writes performed by this revision. No history rewrite.

## Remediation
| Priority | Finding | Change |
|---|---|---|
| P0 | Unsupported default runner | Pin Ubuntu 24.04; preserve the browser deployment gate |
| P0 | Unavailable PDF artifact after a browser failure | Upload verified photo PDFs before browser installation; deployment itself still blocked on tests |
| P0 | Unwanted vocabulary in active source and PDF | Replace branding with Signature Racing; add case-insensitive build scan for source and current PDF text/metadata; reject proof PDFs in production |
| P1 | Duplicate home/section serials, breadcrumbs, footer copy | Remove redundant visible text and streamline homepage |
| P1 | Long flat More menu | Group 15 secondary links into Music & media, Promoters, About & settings |
| P1 | Navigation language implied full translation | Explicitly label partial translation; use element-level language attributes; mark original ID biography |
| P1 | Player collapse state and reserved space | Persist collapsed state during enhanced navigation and reduce unused footer space |
| P1 | Gallery control focus and share fallback | Keyboard focus restoration and fallback without false send confirmation |
| P1 | Motion status mismatch with reduced motion / data saver | Expose constrained status rather than implying full animation |
| P2 | Service-worker cache growth and cross-project deletion risk | Scope cache names and routes; cap non-shell entries; avoid range requests; preserve offline shell |
| P2 | Mobile touch targets and dropdown group styling | Refine responsive CSS, focus states and animation |

## Evidence for this revision
- 46 HTML pages; 3219 local references checked, zero errors under package/manifest mode. Original binary assets not present locally; preserve existing checkout.
- Node syntax checks for active JavaScript and service worker passed.
- Case-insensitive branding scan of active source/package and both locally generated proof PDFs: zero findings.
- Chromium layout test logged 242 page-width checks and no detected overflow or heading clipping; combined execution was interrupted afterward. A separate interaction-only rerun passed all ten groups with no JS exceptions. See `browser-results.json`. Test scope uses actual HTML, CSS and JS with image placeholders, in-memory storage and no live HTTP navigation or external playback.
- Current local PDFs are marked proofs. Production strictly generates photo EPKs from original assets and verifies them before artifact or publication. Historical PDFs remain in repository but are not staged for V4.1.

## Outstanding verification / data
Actual asset rendering, persistence across real URLs, third-party playback, Safari/iOS, PWA install/offline behavior, accessibility tooling and Lighthouse must be tested in CI or on real devices. Full bilingual content and verified release BPM/dates, event dates and photographer credits require original data. Static booking does not confirm inquiries and has no backend. The package is a release candidate; do not claim a successful deployment until the new CI run completes.
