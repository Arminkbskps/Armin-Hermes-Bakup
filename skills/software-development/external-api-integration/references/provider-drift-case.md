# Provider Drift Case (2026-09-22, site-summarizer)

Real session where two "stable" assumptions broke at once.

## 1. AI Studio format rotation

- Old belief: Gemini keys start with `AIza…`, REST endpoint is
  `generativelanguage.googleapis.com/v1beta/models/<model>:generateContent`,
  models like `gemini-1.5-flash` / `gemini-3.1-flash-lite` are valid.
- Reality found live: user-provided key started with `AQ.…` (53 chars);
  all REST `generateContent` calls returned HTTP 403 with an HTML error page.
- User correction (verbatim): AI Studio shipped a new API —
  `from google import genai; client = genai.Client(api_key=...);
  client.interactions.create(model="gemini-3.8-flash", input=...)`.
- Lesson: I wrongly told the user the `AQ.` key was invalid based on the
  remembered `AIza` prefix. The user tested directly and proved the key
  worked — the breakage was my outdated endpoint/SDK, not their key.
- Fix applied: `_chat_google` rewritten SDK-first
  (`google-genai` Interactions API, model `gemini-3.8-flash`) with REST
  fallback; SDK pinned in `requirements.txt`; model ID moved to
  `config/settings.json` default.

## 2. Cloudflare WAF blocked headerless PUTs

- Symptom: CI workflow `summarize.yml` showed green runs but summaries never
  reached the Worker; after adding per-item logging + `SystemExit` on failure,
  the step finally failed loudly.
- Local reproduction: `urllib.request.Request(..., method='PUT')` with only
  `Content-Type` + `Authorization` returned **HTTP 403, ~6.5KB HTML body**
  (Cloudflare challenge page). Adding
  `User-Agent: site-summarizer-ci` → HTTP 200 immediately.
- Diagnosis transcript (local, no proxy):
  `PUT no-UA -> 403 (6697-byte body)` /
  `PUT with UA -> 200 {"ok":true}`.
- Fix: one-line header addition in the workflow Push step; same header
  (`Mozilla/5.0 (compatible; site-summarizer/1.0)` or project UA) on every
  server-to-server call touching Cloudflare.

## 3. Secret-sync gap (same session)

- Admin panel saved keys to Worker D1, but CI only read GitHub Secrets
  (empty) → provider silently fell back to slow `g4f`. Fix: Sync step reads
  `/api/settings` from Worker and exports `AI_PROVIDER / GOOGLE_MODEL /
  OPENROUTER_MODEL / GOOGLE_API_KEY / OPENROUTER_API_KEY` to `GITHUB_ENV`
  with `::add-mask::`; removed shadowing empty `env:` block on the run step.

## 4. Silent-success push loop (same session)

- Old Push step caught per-site exceptions with `print('fail')` and exited 0
  → weeks of phantom green runs. Fix: count `ok/fail`, `print('PUT failed
  for <id>: <e>')`, and `raise SystemExit('::error::push failed…')` when
  `fail > 0`.
