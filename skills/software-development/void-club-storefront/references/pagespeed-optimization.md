# PageSpeed Insights & Core Web Vitals Optimization for VOID CLUB

## 1. CrUX "No Data" vs Lighthouse Lab Score
- **"Discover what your real users are experiencing: No Data"**:
  - PageSpeed Insights shows CrUX (Chrome User Experience Report) field data collected from real Chrome users with telemetry enabled over a rolling 28-day window.
  - New domains, niche stores, and low-traffic sites lack the minimum volume threshold (thousands of eligible monthly pageviews) required for statistical significance.
  - "No Data" is NOT an error, penalty, or indexation problem. It disappears automatically once traffic reaches Google's threshold.
- **Why Mobile (51) vs Desktop (82) Differs**:
  - Lighthouse Mobile emulates a mid-tier phone (Moto G Power / G4) with a **4x CPU slowdown** and a throttled 4G network (1.6 Mbps download, 150ms round-trip latency). Desktop uses unthrottled fast CPU and high bandwidth.
  - Scores are weighted: Total Blocking Time (TBT) 30%, Largest Contentful Paint (LCP) 25%, Cumulative Layout Shift (CLS) 25%, First Contentful Paint (FCP) 10%, Speed Index (SI) 10%. Heavy JS, multi-megabyte media payloads, and render-blocking assets penalize mobile exponentially more than desktop.

## 2. VOID CLUB Storefront Bottlenecks & Proven Fixes

### A. Oversized Emblem Logo (Memory, CLS & LCP)
- **Problem**: `assets/images/void_club_emblem.png` was **3162 × 3162 px (568 KB)**, rendered in `.site-header` at `height: 28px`. On mobile, the browser decodes a 10-megapixel image (~40MB RAM footprint) just for a 28px navbar emblem.
- **Fix**: Downscale for web to high-DPI retina 500 × 500 px (33 KB) or 112 × 112 px (6 KB) using Lanczos in PIL. Add explicit `width="28" height="28"` to all `<img>` tags in navbar across all HTML pages to eliminate layout shift (CLS).
- **Watermark Warning**: Do NOT resize `assets/images/void_logo_black.png` or `void_logo_white.png` — they are used by `api/lib_upload.php` as source assets for product watermarks. Only optimize web display assets.

### B. Hero Slider Multi-Video Eager Preload Bug (The 8+ MB Mobile Killer)
- **Problem**: When multiple hero banners are videos (e.g. `097c0db251c7.mp4` [854 KB], `8d74bed3f9fd.mp4` [3.7 MB], `afabe0d5e8e0.mp4` [3.5 MB]), a bug in `sr7-slider.js` ran `video.setAttribute('src', wantUrl); video.load()` inside `slides.forEach` unconditionally for ALL slides on initial load. On throttled 4G (1.6 Mbps), downloading 8.1 MB of video simultaneously stalled the mobile network, pushed LCP to 13.0s, and spiked main-thread work to 30.1s.
- **Fix**:
  - In `js/sr7-slider.js` within `sr7GoTo`, guard the video source attachment inside `if (isActive)`:
    ```javascript
    const video = s.querySelector('video');
    if (video && wantUrl) {
      if (isActive) {
        if (!video.getAttribute('src') || video.getAttribute('src') !== wantUrl) {
          video.setAttribute('src', wantUrl);
          try { video.load(); } catch (e) {}
        }
        // play logic...
      } else {
        try { video.pause(); } catch (e) {}
      }
    }
    ```
  - Result: Non-active slides remain with `preload="none"` and no `src`, saving 7.2+ MB on initial page load.

### C. Invisible Hover Images on Mobile Touchscreens
- **Problem**: For every product card, `app.js` rendered both the primary image and the hover image (`product-card-img-hover`). While CSS hides hover images on touch devices via `@media (hover: none) { display: none !important; }`, modern mobile browsers (especially Chrome) still prefetch `loading="lazy"` images within a 1250px scroll threshold of the viewport. This caused mobile phones to fetch 10+ MB of invisible hover images.
- **Fix**:
  - In `js/app.js` within `cardMediaTag`:
    ```javascript
    if (isHover) {
      if (typeof window !== 'undefined' && window.matchMedia && window.matchMedia('(hover: none)').matches) {
        return '';
      }
      return `<img src="${url}" class="${cls}" alt="${safeTitle}"${lazyAttr} onerror="window.__vcMediaFail(this,'hover','${safeTitle}')">`;
    }
    ```
  - Result: Eliminates 50% of product image requests on phones and tablets.

### D. Font Waterfall via CSS `@import`
- **Problem**: Line 1 of `css/variables.css` loaded Google Fonts via `@import url('https://fonts.googleapis.com/css2?family=Outfit:...&family=Vazirmatn:...&display=swap')`. `@import` inside CSS creates a sequential network waterfall (HTML → variables.css → Google Fonts CSS → woff2 files) and requested 14 separate font weights (300 to 900).
- **Fix**:
  1. Remove `@import` from `variables.css`.
  2. In `<head>` across HTML files, use direct preconnect:
     ```html
     <link rel="preconnect" href="https://fonts.googleapis.com">
     <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
     <link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&family=Vazirmatn:wght@400;600;700;800&display=swap">
     ```
  3. Only request essential weights (400, 600, 700, 800) instead of all 7 weights.

### E. Render-Blocking External Icon CSS — SUPERSEDED (do NOT apply)
- **Status (2026-09-18):** the `media="print" onload="this.media='all'"` lazy pattern below is BANNED for this project. Behind Iranian filtering the CDN stylesheet never arrives and `onload` never fires, so icons vanish permanently with zero console errors («آیکون ها لود نمی شن»). Icon CSS is now SELF-HOSTED (`assets/icons/remixicon.css` + `fa-all.css`, fonts in `assets/webfonts/`) via plain `<link rel="stylesheet">` tags — see the Icon architecture subsection in SKILL.md. Kept here only as a cautionary record; never reintroduce it as a PageSpeed fix.

### F. Un-deferred Scripts & High Total Blocking Time (TBT)
- **Problem**: 8 `<script src="...">` tags at the bottom of `index.html` (including 5,400+ line `app.js`) lacked `defer`. When parsed on a 4x throttled mobile CPU, JS evaluation locked the main thread for 400-800ms.
- **Fix**: Add `defer` attribute to all `<script src="...">` tags and increment cache-busting queries (`?v=`).

### G. Mobile `-m640` thumbnail pipeline + eager-LCP plain-src (sessions 2026-09-20)
- **Pattern:** phones (≤768px via `matchMedia`) load `-m640` WebP thumbs (~30–50KB) generated once with PIL LANCZOS (width 640, quality 78); desktop serves the byte-identical original URL. Fallback `__vcMobFail` retries the full file once on thumb 404, so cards never render broken.
- **Helpers:** `vcMobThumb(url)` in `js/app.js` (shared by product cards, home categories, `thumbOf` search thumbs); every new upload auto-generates its `-m640` twin server-side in `api/lib_upload.php` (`vc_make_thumb`), so no manual per-upload work is ever needed.
- **Critical srcset trap (caught via PSI re-run):** NEVER put `srcset="thumb 640w, full 1600w"` on the LCP/eager image. On high-DPR phones (DPR 3) the browser computes effective pixels (slot × DPR, e.g. 90vw×3 = 1166w) and picks the FULL file — the PSI re-run showed the full 211KB downloading despite the thumb existing. LCP/eager images get a PLAIN `src="thumb"` with NO srcset; non-eager cards keep srcset as fallback. Same rule in `sr7-slider.js`: first-slide hero video uses `preload="metadata"` on mobile (`auto` on desktop).
- **Delivery constraint:** the agent has NO direct host access — ship changed files + thumbs as a ZIP for the user to Extract in cPanel `public_html`, bump `?v=` forward on every touched JS/CSS, and re-verify live headers (`Cache-Control`) after extract.
- **API cache headers:** `GET /api/categories` uses `public, max-age=30` (same as `/products`), NOT `no-store` — PSI flags uncached API JSON. Admin edits appear within 30s max.

### H. Host cache headers differ per content-type — verify with a full GET
- **Finding:** on the live host, `webp` thumbs serve `Cache-Control: public, max-age=604800` + `Expires`, but hero `mp4`s serve NO `Cache-Control`/`Expires` at all — same `.htaccess`, same host. PSI flags the mp4s "Cache: None" so every visit re-downloads megabytes. Shared-hosting module gaps are per-type, not global (`mod_expires` honored for images, ignored for `video/mp4`).
- **Recipe:** never trust `.htaccess` by reading it — verify per content-type with a FULL 200 GET (`curl -D - -o /dev/null 'https://host/uploads/x.mp4'` vs the same for a `webp`). `HEAD` can answer from a different path and `-r 0-0` range requests return 206 with stripped headers; only the full GET shows what PSI sees.
- **Mitigations when the host won't cache video:** (1) per-dir `uploads/.htaccess` `<FilesMatch>` cache rules (closer to the files, survives root rewrites); (2) bandwidth-side fixes needing no host cooperation — first-slide hero video `preload="metadata"` on mobile (§G), non-active slides `preload="none"` + `data-sr7-src` (§B); (3) re-test PSI only after confirming the live header changed.

### I. Nested template-literal backtick errors point at the WRONG line
- **Symptom:** `node --check` reports `SyntaxError: Unexpected token 'class'` on an `<img class=...>` line inside a template literal — but that line is fine. Root cause is an extra/missing backtick in a nested `${... ? `...` : `...`}` ternary 1–3 lines ABOVE (seen: stray trailing backtick after `</video>`), which terminates the outer literal early so the following HTML parses as JS.
- **Rule:** when a syntax error points INSIDE a template literal, count backticks at the literal BOUNDARIES above the reported line instead of editing the reported line. `node --check <file>` is the authority — a patch-time lint fragment can flag the same cascade; fix the boundary, then re-run `node --check`.
