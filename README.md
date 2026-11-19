# JXXZY Racing Artist Experience V2.1 — UI/UX revision

Nine real pages plus 404. Independent motorsport-inspired identity; no BMW affiliation is claimed. Original music, photography, biography, riders, PDF and official channels are preserved. Based on V2 deployed commit `90490dc04bafd5359dd4708c3dcb9aca9514a843` (home, CSS and JS blob hashes confirmed against upstream).

## Upgrade using the existing repository
Extract the ZIP **over the existing `presskit` checkout**, keeping all original files under `assets/` and `.git/`. This ZIP contains source and an asset manifest, not the 45 original binary assets. If starting separately, run `python hydrate_assets.py` (network required). The existing checkout already contains original files; no need to reinstall Python or Node on Android to push. GitHub Actions validates JS and checks all original assets before deployment.

- `git add -A && git commit -m "fix: premium responsive JXXZY V2.1 UI UX" && git push origin main`
- Watch GitHub Actions; do not use force push. The old manually dispatched deployment workflow, if present in the repository, should not be run concurrently.
- Local optional validation: `python check_site.py --require-assets`, `node --check assets/racing.js`, `python -m http.server 4173`.

## Changes
New navigation, CTA hierarchy, controlled type scale, mobile-first hero, gallery next/previous and keyboard, track search/filters and empty state, EPK table of contents, safer booking form, same-origin media, reduced-motion, pause on hidden tab/out of view, stricter deployment validation. Original PDF remains unchanged. Booking hands off to WhatsApp/email; it does not submit automatically.

## Verification and limits
See `AUDIT_V2_1.md` and `VERIFICATION.txt`. Browser tests used Chromium with inlined original page markup, CSS and JS, substituted image geometry and fallback fonts, blocked external connections, no real media. Live website, Safari/iOS and actual artwork cropping, external playback, real booking delivery and final PDF rendering require deployment/device verification. No push was performed from this environment.
