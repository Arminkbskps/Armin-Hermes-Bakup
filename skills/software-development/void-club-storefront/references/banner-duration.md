# Banner per-slide duration (session 2026-09-11)

User requirements: banner FA/EN titles must NOT be mandatory (only the
image/video is required); each banner gets its own display time; unset =
6s; long videos cut at the duration; short videos advance early; images
use the duration exactly.

## DB layer (`api/schema.sql`, `api/lib_db.php`, `api/api.php`)

- New column `banners.duration` (MySQL `INT NULL DEFAULT 6`,
  SQLite `INTEGER NULL DEFAULT 6`). Add to `schema.sql` + the
  `vc_sqlite_init()` mirror table.
- Auto-migration `vc_ensure_banner_duration($pdo)` in `lib_db.php`
  (same pattern as `vc_ensure_category_parent` / `vc_ensure_product_type`):
  `SELECT duration ... LIMIT 1`, on failure `ALTER TABLE ... ADD COLUMN`
  with the sqlite/mysql branch. Call it at the TOP of the banners route
  in `api.php` so legacy installs self-heal on first hit.
- Sanitizer (used in POST, PUT, and serializer — keep all three in sync):
  blank/invalid → 6, clamp 1..60:
  ```php
  $dur = 6;
  if (array_key_exists('duration', $b) && $b['duration'] !== '' && $b['duration'] !== null) {
      $dur = (float)$b['duration'];
      if (!is_finite($dur) || $dur <= 0) $dur = 6;
      $dur = max(1, min(60, $dur));
  }
  ```
- `vc_banner_public()` returns `'duration' => $dur` (always a number, never
  null) so the slider never has to guess.
- POST inserts the `duration` column; PUT accepts `duration` in the
  field list (blank string = leave unchanged); add `'duration'` to the
  foreach field list.

## Admin form (`account.html` + `handleCreateBanner` in `js/app.js`)

- FA title (`#adm-b-title`) and EN subtitle (`#adm-b-subtitle`): remove
  `required`, label them optional. Delete the
  `if (!title || !subtitle)` guard — only `image_url` is mandatory.
  Send `title: title || null, subtitle: subtitle || null` (same for
  `button_text` — CTA is optional too, NOT defaulted to «مشاهده دراپ»).
- New `#adm-b-duration` number input (min 1, max 60, default value 6)
  + 4s/6s quick buttons. JS: `parseFloat(...)`, non-finite/≤0 → 6,
  clamp 1..60, always POST `duration`.
- Admin banner list row shows a duration badge
  (`${b.duration ? parseFloat(b.duration) : 6} ثانیه`) so the admin can
  see each slide's timing at a glance.

## Slider (`js/sr7-slider.js`, `css/sr7-slider.css`)

- Timeout chain, NOT `setInterval`: `sr7ScheduleNext(module)` computes
  `sr7SlideDurationMs(banner)` for the CURRENT slide and
  `setTimeout(() => sr7GoTo(sr7Current + 1), waitMs)`. Every `sr7GoTo`
  starts with `sr7StopAutoplay()` (now `clearTimeout`). This is what
  makes per-slide timing possible at all.
- Video tags: NO `loop`, NO `autoplay` attribute. `sr7GoTo` drives
  playback: active → `muted=true; currentTime=0;
  loop=(slides.length<=1); play()`; inactive → `pause()` + detach the
  old `video._sr7EndedHandler`.
- Short video (shorter than duration): per-slide `ended` listener
  advances immediately. Metadata may not be loaded when the slide
  starts — handle both cases: if `readyState>=1`, shrink `waitMs` to
  `min(duration, video.duration)`; else attach a one-shot
  `loadedmetadata` handler that re-arms the timer with the shorter wait.
- Long video: the outer timeout fires first and cuts it — nothing
  special needed beyond removing `loop` (loop would otherwise restart
  the video instead of advancing).
- Single-banner slider: `loop=true`, no timer (`sr7Banners.length<=1`
  returns early in `sr7ScheduleNext`).
- Bullet progress bar: CSS uses
  `animation: sr7-progress var(--sr7-dur, 6s) linear forwards;`
  and JS sets `--sr7-dur` inline per active bullet (updated again in the
  `loadedmetadata` shrink path).
- Bump `sr7-slider.js?v=` in `index.html` (and any page loading it)
  after slider changes — stale cached slider = old fixed-6s behavior.

## Acceptance checklist

- Create banner with NO titles → 200, slide renders full-bleed, no text layer.
- `duration` blank → API returns `duration: 6`; slider advances at 6s.
- Image with duration=4 → advances at ~4s, bullet bar finishes at ~4s.
- 20s video with duration=6 → cut at ~6s (never loops).
- 3s video with duration=6 → advances at ~3s.
- Legacy DB (no `duration` column) → first banners call adds it, no data loss.
