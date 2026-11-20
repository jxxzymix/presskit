# JXXZY V4 — Signature Motorsport

Independent artist experience inspired by motorsport, without affiliation with BMW. This update is designed as an overlay on the existing `jxxzymix/presskit` checkout; preserve its original binary assets. The 2026 V3 source was the baseline (`6e904a0`).

## Apply from Termux

```sh
cd "$HOME/presskit" && git pull --ff-only origin main
unzip -o "$HOME/storage/downloads/JXXZY_Racing_V4_Signature_Motorsport.zip"
git add -A
git status
git commit -m "feat: Signature Motorsport V4 artist experience and photo EPK pipeline"
git push -u origin main
```

No Python or Node install is required on the phone. GitHub Actions installs build tools, restores missing original assets if necessary, verifies image dimensions, produces the full 22-page PDF and 3-page quick PDF with original photos and artwork, checks static links and JavaScript syntax, runs Chromium tests against actual repository assets with external media mocked, and only then deploys. The two PDFs in this ZIP are clearly marked **layout proofs**, not the final artist photographs edition. The production build replaces them; use Actions artifact `JXXZY-V4-Final-EPK` or the deployed download links to get the finished PDFs. The old PDFs and source media may remain in Git history but the V4 published build only stages the current referenced assets. Manual deployment uses the same workflow. No force push.

## Features

- 22 primary/secondary pages and 22 individual release detail pages, plus 404 and offline.
- Responsive navigation, direct EPK access, mobile dock, search and settings. English/Indonesian navigation and selected labels; bios in both languages. Full site translation is not complete.
- One maintained release data file (`data/catalog.json`), generated catalog script, and snapshot HTML. Existing HTML pages must be updated when adding or removing tracks; full component-based static generation is not complete.
- Persistent in-document platform iframe during enhanced internal navigation; queue reorder and manual next/previous, local favorites and history, local preference reset, share links, playlist-link export (platform URLs, not local audio files). Actual streaming, autoplay and end-of-track events are subject to third-party platform restrictions; continuous playback is not guaranteed on full reload or external navigation. Queue advancement is manual.
- Gallery filter and correct filtered counter, image zoom, keyboard and swipe. Live archive search. No unverified dates, BPM, duration, year or performance metrics added.
- Three-step booking brief, contact validation, preview, local text download; no backend, payment or confirmed booking state.
- Promoter toolkit, illustrative stage plan, web EPK and two PDF editions. Stage plan is not an engineering drawing.
- Three visual modes, respects device motion/data constraints, CSS motion effects and local preferences. Manifest and basic same-origin offline cache; no promise of offline music or PDF streaming.

## Local development (optional)

`python -m pip install -r requirements-build.txt` then `python hydrate_assets.py`, `python tools/prepare_site.py`, `python tools/build_epk.py`, `python tools/verify_pdf.py`, `python check_site.py --require-assets`. Run `python -m playwright install chromium`; `FULL_TEST=1 python tests/browser.py --real-assets`. You can use `python -m http.server 4173` to preview the static pages.

## Evidence and limitations

See `AUDIT_V4.md` and `browser-results.json`. Local Chromium proof used actual candidate HTML/CSS/JS with image substitution and in-memory storage because browser navigation was blocked. It did not verify real hosting, external streaming, actual photos or OS-level device layout. CI must pass with original assets and real URL routing before deployment. PDF proof has placeholder frames; production gate refuses proofs or missing original images. Real-device Safari, Lighthouse, axe, external URL availability, full language translation, full catalog metadata and backend booking are still outstanding.
