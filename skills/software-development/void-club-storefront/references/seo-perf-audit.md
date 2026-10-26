# SEO + perf audit fix pattern (session 2026-09-20, ships in `VOID_mobile_perf_v7.zip`)

Applies a third-party SEO/accessibility/perf audit (11 issues on `index.html`) to the
cPanel static build WITHOUT visual or desktop changes. Base rule first:

- **The `VOID_mobile_perf_vN.zip` files are PARTIAL deploy subsets** (v6 = only
  `index.html`/`shop.html` + 2 css + 3 js + api subset + `-m640` uploads; NO fonts,
  NO `remixicon.css`, NO other pages/images). Never treat the zip as the working
  base: copy the full `VOID_CLUB_CPANEL/` tree, apply fixes there, then ship a
  minimal-diff zip (v7 = v6 + 4 changed files + 1 new `assets/images/og-cover.jpg`).
  Verify with `diff -rq` that only intended files differ.

## Head tags (index.html)

- Title 30–60 chars: `VOID CLUB | فروشگاه تیشرت و هودی استریت‌ویر` (43).
  Keep `og:title`/`twitter:title` identical; description 50–200 chars
  (111 used) shared across `description`/`og:description`/`twitter:description`.
- Add `<meta name="robots" content="index,follow">` (robots.txt allow is NOT
  what the audit checks — it wants the meta tag).
- OG/Twitter: absolute `https://voidclubs.ir/assets/images/og-cover.jpg` +
  `og:image:width/height/alt` + `twitter:card=summary_large_image` +
  `twitter:title/description/image`. Generate the cover locally with PIL:
  1200×630 RGB `#0c0c12` + red glow bars, ~47KB JPG (hard requirement <5MB,
  1.91:1). Never hotlink a stock/placeholder URL.

## Render-blocking CSS without breaking icons

- The audit flags ~14 stylesheets, but `fonts-local`, icon CSS, `variables`,
  `reset`, `base`, `components`, `layout`, `responsive` are above-the-fold
  critical — and icon CSS must NEVER be print-deferred (behind Iranian
  filtering the onload never fires → icons vanish silently).
- Defer ONLY the 5 non-critical files with `media="print" onload="this.media='all'"`
  + `<noscript>` fallback: `custom-select`, `editorial-popart`,
  `void-components`, `sr7-slider`, `search`.
- Server side: add a CSS/JS `Cache-Control: public, max-age=2592000, immutable`
  `FilesMatch` block in `.htaccess` (repeat views serve from disk cache).

## Landmarks without visual change

- Wrap page content in `<main id="main-content">` + one `<h1>`.
- Do NOT rely on the `.visually-hidden` class from `critical.css` (deferred /
  may not load) — inline the hiding style on the `<h1>` itself
  (`position:absolute;width:1px;...clip:rect(0,0,0,0)`).

## `href="#"` toggles → `<button>`

- The 3 header toggles (`search-btn`, `wishlist-btn-toggle`, `cart-btn-toggle`)
  are drawer openers, not links: convert to
  `<button type="button" class="action-btn" id="..." aria-label="...">`.
  Safe because all JS binds via `getElementById` + `preventDefault` (verified:
  zero `a.action-btn` selectors in CSS/JS). Add a `button.action-btn`
  reset-parity rule (`font:inherit;line-height:1;padding:0;appearance:none`)
  so buttons render pixel-identical to the old anchors.

## Tap targets (48px) without layout change

- Do NOT grow the visuals (40→48px buttons would shift header/slider rows).
  Instead append a MOBILE-ONLY (`@media max-width:768px`) block at the end of
  `responsive.css` that adds transparent `::after` hit areas
  (48×48px centered) on `.action-btn/.slider-nav-btn/.btn-view-all/a.logo`.
  Desktop stays byte-identical; audit measures the hit area, not the paint.

## v8 follow-up (same audit, second round: CLS 0.479 + tap targets re-flagged + perceived load)

- **`::after` hit areas do NOT satisfy tap-target scanners.** v7's invisible 48px
  `::after` kept visuals identical but the re-audit flagged every 40px control
  again — scanners measure the element's own box, not its hit area. v8 replaced
  the block: real `width/height/min-width/min-height: 48px !important` on
  `.action-btn/.slider-nav-btn`, `min-height: 48px` (+inline-flex centering) on
  `.btn-view-all`/`a.logo`, and `min-width/min-height: 48px` on the small round
  buttons (`.product-card-wishlist/.drawer-close/.search-modal-close/.sr7-nav-btn`)
  — ALL inside the same mobile-only `@media (max-width:768px)` block — while
  shrinking surrounding padding/gaps (`.header-container` top/bottom padding,
  `.header-actions` gap → 2px, `.slider-nav-arrows` gap → 4px) so header/slider
  rows stay visually identical. Desktop stays byte-identical. Rule: when an
  audit re-flags `::after`-expanded targets, grow the real box + absorb the
  delta in neighboring padding, never assume hit-area tricks pass.
- **Inline critical CSS, then defer more.** v8 inlined variables+reset+base
  (~4.4KB: tokens, reset, body, `.container`, focus rules) plus the CLS reserves
  below in a head `<style>`, then deferred the originals (`variables`/`reset`/
  `base`/`components` + `remixicon`) with `media="print" onload` + `<noscript>`
  fallback. Blocking set shrinks to fonts-local + fa-all + layout + responsive.
  CAUTION: deferring `remixicon.css` conflicts with the NEVER-defer-icons rule
  (Iranian filtering, 2026-09-18) — v8 did it without live icon verification.
  Prefer keeping both icon stylesheets blocking; defer `remixicon` only if
  PageSpeed forces the trade AND icons are re-verified live via
  `document.fonts.check('16px remixicon')` + computed `fontFamily` on a
  rendered `ri-*` element.
- **CLS reserves live in the inlined block** so deferred CSS/JS arrival doesn't
  shift layout: `#SR7_hero_module{aspect-ratio:16/9;min-height:220px;
  max-height:820px}` (200px mobile), `#home-featured-categories-slider
  {min-height:300px}` (280px mobile), `#home-top-grid/#new-arrivals-grid
  {min-height:420px}`, `aspect-ratio:1/1` on card images.
- **CLS beyond reserves (v8, CLS 0.479 — reserves alone weren't enough):**
  (1) `#home-top-section` shipped `style="display:none"` and async JS revealed
  it — a ~500px shift when the rail appeared above Fresh Drops. Now the section
  ships VISIBLE with skeleton cards holding its space, and JS hides it only
  when the rail is empty. Rule: never `display:none` a section that async JS
  may reveal above other content — render skeletons instead.
  (2) `width`/`height` attrs on every JS-rendered image: `cardMediaTag` emits
  `width="640" height="640"` (cards are square 1:1), sr7 slides emit
  `width="1280" height="720"` (16:9) plus `aspect-ratio:16/9` on `.sr7-bg-img`
  in CSS so the box holds before media arrives.
- **Patch-tool brace hazard on JS template literals:** a fuzzy patch near
  `cardMediaTag`'s `if (isHover) {...}` silently dedented the closing braces
  and left a stray extra `}` — caught only by `node --check`. After EVERY JS
  patch, `node --check` is the gate; when lint isn't `ok`, re-read the region
  and fix indentation before proceeding (never a third blind patch — rewrite
  the enclosing block instead).

## Acceptance

`grep`: 1 `<h1`, 1 `<main`, 0 `href="#"`, `media="print" onload` = 10 (v8;
was 5 in v7), `robots` + `og:image` + `twitter:card` present,
`og-cover.jpg` = 1200×630; CSS brace balance; `node --check` on every
touched JS; ship with `shutil.make_archive` (forward slashes — never
PowerShell `Compress-Archive`, which writes backslash entry names that
Linux/cPanel may treat as literal filenames); zip `diff -rq` vs previous
version shows only intended files.
