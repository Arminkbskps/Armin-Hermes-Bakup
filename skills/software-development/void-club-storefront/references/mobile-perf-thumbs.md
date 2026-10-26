# Mobile perf: `-m640` thumbnails + hero-video defer (session 2026-09-20)

PSI mobile (Moto G + Slow 4G) on an image/video-heavy storefront: Performance
66 → 67 with FCP 1.5s → 1.2s and image savings 1715KB → 611KB. Remaining
ceiling is hero mp4s with `Cache: None` (4.6MB of 5.9MB payload) — needs host
cache cooperation or video recompression, not more image work.

## 1. Mobile-only thumbnails, desktop byte-identical

- Name thumbs `<base>-m640.<ext>` next to the original (PIL: resize width>640
  → 640 via LANCZOS, WEBP quality 78 method 6 / JPEG 78 progressive).
- `vcMobThumb(url)`: only when `matchMedia('(max-width: 768px)')` matches AND
  URL matches `^uploads\/.+\.(webp|jpg|jpeg|png)$` → thumb URL, else original.
  Desktop output stays byte-identical (user constraint: never break desktop).
- `window.__vcMobFail(el, kind, title)`: on thumb 404 (missing backfill),
  retry once with `data-vc-full` (original URL), then delegate to the normal
  failure handler. Cards never render broken.
- Auto-generate on upload: `vc_make_thumb()` in `api/lib_upload.php` next to
  the WebP conversion, so new uploads always have a thumb (backfill is
  one-shot for old files only).

## 2. The DPR srcset trap — use PLAIN src for LCP/mobile cards

With `srcset="thumb 640w, full 1600w" sizes="(max-width:768px) 90vw"`, a DPR3
phone computes 90vw×3 ≈ 1350w → picks the 1600w FULL file even though the slot
is ~500px. PSI caught card #2 downloading 185KB despite its 44KB thumb.
Fix: mobile cards (and especially the eager LCP card) use plain
`src="<thumb>"` with NO srcset. Verified in PSI report HTML: LCP img shows
`src="...-m640.webp" ... fetchpriority="high"`.
- First card (LCP candidate): `fetchpriority="high" decoding="async"`, no
  `loading="lazy"`. Others keep `loading="lazy"`.

## 3. Hero video defer on mobile (videos stay, desktop unchanged)

First-slide video on phones: `preload="none" + data-sr7-src` instead of
`src + preload="auto"`; `sr7GoTo()` already lazy-activates (sets src + `load()`
+ `play()` when the slide shows), so playback just starts slightly later while
  the 3.7MB mp4 no longer fights the LCP image for Slow-4G bandwidth. Desktop
  keeps `src + preload="auto"`. Requires `mobile_image_url` fallback chain
  (`data-desk`/`data-mob`) to stay intact.

## 4. mp4 cache by FILE EXTENSION, not MIME type

Host served webp with `Cache-Control: public, max-age=604800` (mod_expires
works) but mp4 with NO cache header despite `ExpiresByType video/mp4` in root
`.htaccess` — the host's handler doesn't map the MIME type. Fix in
`uploads/.htaccess`: `<FilesMatch "\.(mp4|webm|mov|m4v)$">` +
`ExpiresDefault "access plus 30 days"` (+ `Header set Cache-Control` under
mod_headers). Verify live: `curl -D - -o /dev/null <mp4-url> | grep -i cache`.
If still None, the host ignores uploads-level htaccess → cPanel cache manager
or a support ticket for mod_headers/mod_expires.

## 5. Cheap API cache win

`GET /api/categories` was `Cache-Control: no-store` → `public, max-age=30`
(same trade-off `/products` already used). PSI "unclaimed" LCP delay
(resource load delay 3580ms → 1090ms) partly comes from the image URL being
discoverable only after the API + JS render.

## 6. Valid PSI runs: VPN OFF + Incognito

User's VeePN + SingleFile extensions injected 430KB/665KB and 155ms main
thread into the lab run (TBT 0 → 440ms, CLS/FCP swinging run to run). Always
ask for VPN-off Incognito retests before trusting score deltas.

## 7. Mangled-thumb 404 diagnostic

A 404 like `wm_7dfa0a7d6a08-m6a0.webp` (vs real `wm_7dfa047d6a08.webp`) means
the DB filename differs from the on-disk file — check DB vs disk first, don't
blame the regex. Also: files uploaded AFTER the backfill naturally lack thumbs
(grep disk before assuming the pipeline broke).
