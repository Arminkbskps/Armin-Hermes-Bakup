# Free bg-removal: public HF Space (verified live 2026-09-10)

Use when a bot must cut a background with zero budget and no heavy local dep.
Chain order in `remove_background()`: rembg local (if installed) → free public
Space (no token, needs `gradio_client`) → border-sampled flood fallback.
Empty/missing Space path must fall through to flood with zero user-facing hang.

## Working endpoint (live-verified)

- Space: `not-lain/background-removal` (BiRefNet, ~2900 likes) via `gradio_client`
- Call: `Client("not-lain/background-removal").predict(image_url, api_name="/text")`
- Input is a **URL string**, not bytes — upload bytes to a temp host first, then
  pass the URL. Returns a **list of 2 paths**: `[0]` RGB preview (NO-ALPHA),
  `[1]` RGBA transparent PNG (`A:(0,255)`, 1200×1200 from a 51KB mockup JPG).
- Pick by iterating `reversed(paths)` and returning the first entry that passes
  `has_transparency()`; log + None when none qualifies (flood takes over).
- Timing on desktop CPU: Space call ~6.6s, full
  `apply_background_smart(raw, "#240046")` → `removed_hf` in ~10.6s.
- Wrap the Space call in its OWN timeout SEPARATE from the handler ceiling:
  `ThreadPoolExecutor(max_workers=1).submit(_remove_bg_hf, ...)` +
  `fut.result(timeout=120.0)`; on `TimeoutError` cancel and fall to flood.
  Without this, a sleeping/queued Space outlasts the user's patience while the
  spinner sits on one static message — the #1 "stuck with no news" complaint.
- Progress in stages, not one static spinner: edit the status message after
  DOWNLOAD ("✅ downloaded, AI cutting...") so a stuck job is locatable from
  the user's screenshot alone. Add per-stage `log.info` with elapsed seconds
  (`download done ... in %.1fs`, `process done: mode=%s ...`) — without these,
  a host-side stall is undebuggable after the fact.
- Deps: add `gradio_client>=1.0.0` to `requirements.txt` (host: reinstall).
  `gradio_client` reads proxy from ENV (`HTTP_PROXY`/`HTTPS_PROXY`) — set from
  `_detect_proxy()` before constructing the client; its `Client.__init__` takes
  `token=`, NOT `hf_token=`.

## Temp-upload bridge (the Space takes URL only)

- `uguu.se` (`POST https://uguu.se/upload`, field `files[]`) works; parse
  `json()["files"][0]["url"]`. Verified live 2026-09.
- `catbox.moe` returned `412 Invalid uploader` from the test network — keep as
  second fallback, not primary. `0x0.st` returned `503 uploads disabled`
  (anti-spam shutdown) — do not use.

## Dead ends (do not repeat, verified 2026-09-10 with a valid user token)

- HF Inference Router `POST /models/briaai/RMBG-1.4` (and `Xenova/modnet`,
  `smnslt/bg-removal`, `failgood/bgremoval`) → `400
  {"error":"Model not supported by provider hf-inference"}`. Same for
  `fal-ai` / `replicate` / `together` provider prefixes. Legacy
  `api-inference.huggingface.co` → SSL EOF through the test proxy. A valid
  `HF_TOKEN` does not fix this — the models are simply not served serverless
  right now. Re-verify with a one-shot POST before building on the Router.
- Official Space `briaai/BRIA-RMBG-1.4` `/predict` → `AppError` (upstream
  exception, show_error off), with and without token. Skip it.
- Gradio API discovery differs by version: gradio 4.16 serves `/info` (404 on
  `/gradio_api/info`); gradio 5.x serves `/gradio_api/info`. When a Space 404s
  on one, try the other before concluding it is dead.

## Caption mode

Return method `"hf"` so `apply_background_smart()` reports `removed_hf`;
add `"removed_hf"` to the mode→FA map or the caption lookup KeyErrors.

## Smoke test (mockup JPG ~51KB → 1200×1200)

- `gradio_client` missing → `_remove_bg_hf` returns None immediately, full
  pipeline → `removed_flood` (~1.75–2.8s desktop CPU).
- Space live → `removed_hf`, RGBA alpha `(0,255)`, ~10s end-to-end.
