# V4 implementation and verification ledger

Baseline: published V3 commit `6e904a03cec21506395fba85d94f8db0be712a27`.

|Requirement|Status / evidence|
|---|---|
|Responsive editorial layout|Implemented; local Chromium layout test across primary and detail routes|
|Navbar mobile/desktop|Implemented; EPK and booking visible; mobile dock; Settings available|
|Music library|Implemented; search, platform filter, sort, alternate layout, details, random track, queue|
|My Garage / hash / gallery bugs|Implemented; local tests for save/remove and filtered gallery, URL navigation gate runs in CI|
|Player across internal pages|Implemented using same-origin HTML swap; cross-page behavior test provided for CI, not locally verified; external players not tested|
|Playback queue|Manual previous/next, add/remove/reorder; not auto-advance or guaranteed streaming|
|Live archive|Actual seven entries, searchable; lack of verified dates, additional flyers, videos and metadata remains|
|Booking|Wizard, contact checks, event type, timezone, optional budget, preview, local brief; no confirmation or backend|
|Rider / production|Original technical and hospitality data, checklist, illustration, promoter resources|
|PDF EPK|22-page + 3-page marked local layout proof; strict build on GitHub embeds original photos/official logo/artworks and verifies image count. Not yet generated with real assets locally.|
|Web EPK|Original source content retained, additional links, print restores hidden track/photos; actual print pagination not tested on Safari|
|SEO|Canonical, per-page title, Open Graph, Twitter metadata, JSON-LD, sitemap, robots for personal pages; Search Console/hreflang not verified or complete|
|Language|Navigation and selected UI strings ID/EN plus original bilingual bio; full body translation outstanding|
|PWA|Manifest icons, offline fallback and same-origin cache; actual installation/service-worker tests outstanding|
|Refactor|Data catalog/artist JSON, shared JS and CSS, generated detail pages; full static template generator outstanding|
|CI|One strict deployment path including asset checks, PDF checks, Playwright; pending execution on GitHub|
|Motion|41 distinct @keyframes definitions across active stylesheets; runtime effect count is not equal to definition count. Three modes and reduced motion/data-aware controls.|
|Actual device / Lighthouse / axe|Not verified. No fabricated metrics.|

## Local proof
242 page-width combinations (22 main routes at nine widths and 22 release pages at two widths), zero overflow/heading checks flagged, zero JS exceptions, ten interaction groups passed. All tests use the same HTML/CSS/JS with substituted missing image geometry and mocked local storage; no external traffic. Real HTTP navigation was blocked. CI is intended to use real source assets, a routed browser test origin, and actual location/storage behavior, but third-party embeds remain mocked. Browser results need to be checked after deployment.

## Release caveats
Source ZIP does not contain original 46 binary assets; preserve the clone and hydrate from the original pinned source if required. Original logos/photos are not replaced with third-party stock art. The package includes PDF proofs only; publish strict photo PDFs through the build. This is a release candidate, not verified final stable. No remote push performed by the assistant. Missing facts (BPM, year, career dates, photography credits, verified upcoming shows) are intentionally not invented.
