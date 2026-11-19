# JXXZY Racing Artist Experience V3

Independent motorsport-inspired JXXZY artist experience. Carbon Motorsport / Studio trim, original media, real multipage site, and a redesigned web EPK and downloadable PDF. No affiliation with BMW is claimed.

## Pages
Home, Profile, Music, Shows, Gallery, Riders, Media, Booking, EPK, My Garage (collection), and 404.

## Experience
- Responsive navbar, mobile quick-access dock, active page state, keyboard-friendly global search and command palette.
- Carbon Motorsport and Studio visual trim; motion pause and reduced-motion support.
- 28 new CSS keyframe definitions in experience.css, including dedicated EPK animations. Existing base CSS remains.
- 14 SoundCloud tracks and 8 YouTube sets; platform filter, live search, sort, list/grid view, random discovery, click-to-load player modal and share.
- My Garage local saved collection; photo categories, image viewer and keyboard navigation.
- Booking brief preview and completion indicator; handoff to WhatsApp or email, no automatic sending.
- Rider checklist, promoter assets, EPK chapter navigation and print styling.
- New 15-page PDF (A4): biography, genres, set journey, linked catalog, selected appearances, event formats, riders, production checklist, promoter copy, asset links, brand and booking. The PDF uses original verified source text and typographic design, with official photo links instead of embedded photos because binary image downloads were unavailable. The old PDF is not deleted from the repository.

## Update existing repo (Termux)
Download and extract this ZIP into the existing clean checkout `~/presskit` on main. Retain original assets. Commit and push. Python and Node are not required on the phone; the Pages workflow validates source and original assets server-side before deployment. Do not force push.

## Local development
`python hydrate_assets.py` to restore missing original assets (requires internet); `python check_site.py --require-assets` to validate. `python -m http.server 4173` for local preview. Node syntax: `node --check assets/racing.js`, `node --check assets/catalog.js`, `node --check assets/experience.js`.

## Verification limits
Chromium layout tests used inlined real HTML/CSS/JS with substituted local image geometry, fallback fonts, blocked external requests and mocked localStorage. No real photo/video render, third-party player delivery, live booking delivery, actual Safari/iOS or production deployment was verified. PDF rendered and visually inspected in Poppler. Source package contains new PDF and code but not original multimedia binaries; retain existing repo assets. See VERIFICATION.txt. No remote push performed.
