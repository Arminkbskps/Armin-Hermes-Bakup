# Printify Integration (Telegram bot)

End-to-end flow: token entry → validate → shop picker → products → product →
image → color → process → upload-back. Every step is a callback branch; a saved
token with no usable flow is a bug, not a feature.

## Auth

- Base `https://api.printify.com/v1`, header
  `Authorization: Bearer <token>` (+ `User-Agent`).
- Reuse the bot's `_detect_proxy()` for these `httpx` calls (server = direct,
  filtered local shell = proxy).

## Token entry (validate immediately)

- `GET /shops.json` on the pasted token:
  - 4xx → show the error text, keep `awaiting=pf_token` so retry is one message.
  - 0 shops → "valid but empty".
  - 1 shop → auto-select, jump to product list.
  - N shops → shop-picker keyboard (`pfshop:<id>`).

## Product list (paginated, two response shapes)

- `GET /shops/{id}/products.json?page={p}&limit=8`.
- Response may be a bare list OR a paginated dict
  (`data/total/last_page/current_page`) — handle both, else pages silently break.
- Keyboard: one button per product (`pf:prod:<shop>:<pid>`) + prev/next
  (`pf:prods:<shop>:<page>`).

## Product detail → artwork-first pick (no AI needed)

- `GET /shops/{id}/products/{pid}.json` returns TWO image lists — never treat
  them as one:
  - `print_areas[].placeholders[].images[]` = the ORIGINAL transparent
    artwork files (each has `id` = upload_id, `name`, `width/height`).
    This is Printify's own "download without background" option — use it FIRST.
  - `images[]` (`src`, `position`) = rendered MOCKUPS (opaque product photos).
    Show them only as previews / fallback.
- Detail keyboard sections depend on user priority (default: mockups first as
  👕 primary buttons `pf:mock:<shop>:<pid>:<idx>` with `mock_label()`, artwork
  ✨ last `pf:art:<shop>:<pid>:<n>`, style=success). Artwork path needs NO
  background removal.
- Resolve artwork bytes via `GET /v1/uploads/{upload_id}.json` → `preview_url`
  → download that URL (`pf_get_transparent()` returns bytes + file_name).
  If `preview_url` is missing, fail loudly — don't silently fall back to mockup.
  Verified live: `preview_url` is a FRESH storage URL and differs from the
  product's embedded `placeholders[].images[].src` (a raw S3 link that can
  expire) — always re-fetch `/uploads/{id}.json` instead of reusing the
  embedded `src`; the uploads endpoint also returns `file_name` (use it for
  the output filename). Occasional spurious 401s on endpoints that succeed on
  immediate retry: retry once before telling the user the token is bad.
- Shops list may include EMPTY shops (0 products) — handle "no products found"
  with a change-shop button instead of an error state.

## Recolor (user downloads nothing)

- Color keyboard reuses the main palettes + HEX-custom + random (shared
  `pf_color_keyboard2(prefix, back_cb)` builder; separate `pfhexa:` / `pfhexm:`
  awaiting states for artwork vs mockup so the HEX reply routes correctly).
- Artwork path (`pf_process_art`): `preview_url` bytes are already transparent
  → plain `apply_background()` (direct recolor), no `has_transparency` gate,
  no rembg. Send as Document → archive → quota → stash
  `pf_last={shop,pid,upload_id,color}`.
- Mockup path (`pf_process_image`) is FALLBACK only: `src` files are opaque,
  so run the SMART pipeline (`has_transparency()` → recolor, else flood
  removal → recolor) and warn the user the result won't be as clean as the ✨
  artwork path. Same pipeline feeds the upload-back step — never branch them.
- Upload-back ref encodes the kind: `pf:up:<shop>:<pid>:m<idx>` (mockup) vs
  `pf:up:<shop>:<pid>:<upload_id>` (artwork). Artwork upload-back re-resolves
  via `pf_get_transparent()` + direct recolor; mockup via smart pipeline.
- When the user says "Printify already has a no-background download, drop the
  AI" — they are right: delete rembg/onnxruntime from requirements, keep only
  Pillow+numpy+httpx. AI removal was the wrong fix for mockups; the right fix
  is never downloading mockups for recoloring in the first place.

## Mockup naming: real labels, never "other" (user-driven)

- Users may want the MOCKUPS themselves recolored (folded shirt, hanging,
  lifestyle shots) — not the transparent artwork. When they say so, FLIP the
  product page: mockups FIRST (primary section), artwork LAST.
- `images[].position` is often the useless string `"other"`. The REAL name
  lives in `camera_label=` inside each `src` URL
  (`.../mens-tee.jpg?camera_label=folded`). Extract it:
  `src.split("camera_label=")[1].split("&")[0]`.
- Keep a `MOCK_LABELS_FA`-style map for known labels
  (`front→Front`, `folded→Folded`, `hanging-1→Hanging 1`,
  `lifestyle-2→Lifestyle 2`, `front-collar-closeup→Collar (closeup)`,
  `size-chart→Size chart`, `duo→Duo view`...); unknown labels fall back to
  the raw label with dashes/underscores prettified — NEVER display "other".
  If no `camera_label` and no useful `position`, use `View N`.
- Products can have 30+ mockups (front, back, folded, hanging ×N, lifestyle,
  person-N, sleeve closeups, size chart...). Cap the keyboard (~16 first)
  with a "N total, showing first 16" note row.
- Mockup recolor reality (verified with vision review): flood-fill removal on
  a mockup leaves white halo/fringe at garment edges. Mitigate with a
  mask-erode + blur step (MinFilter ≈5px then GaussianBlur ≈1.2, threshold
  ~140) before `putalpha` — cheaper than rembg and visibly cleaner edges.
  Set expectations in UI text: mockups = recolor-with-cleanup, artwork =
  direct-clean.

## Upload-back to Printify

- `POST /uploads/images.json` with
  `{"file_name": "bg_<hex>.png", "contents": <base64 png>}` → returns `id`.
- Show the new ID with a `CopyTextButton` so the user can attach it to the
  product in the Printify dashboard (API upload alone doesn't relink variants).
