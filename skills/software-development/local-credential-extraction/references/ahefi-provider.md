# Case Study: ahefi.com as a custom 9router provider (Sept 2026)

Session: user asked to pull the API key out of the VS Code extension `ahefi.ahefi`
and load it into 9router. Key extraction itself is covered by the parent skill's
companion `local-credential-extraction`; this file records the provider quirks.

## Provider facts

- Base URL (OpenAI-compatible): `https://ahefi.com/v1`
  - Extension normalizes any base URL by appending `/v1` when missing
    (`/v\d+$/` test in its `n5t()` helper) — so `https://ahefi.com` works too.
- Auth: `Authorization: Bearer sk_live_nn_...` (standard).
- Custom headers the extension may send (optional, not required by the API):
  `x-ahefi-client: vscode`, `x-ahefi-client-token: <config>`,
  `X-Ahefi-Task-ID`, `X-Ahefi-Mode`.
- Account/management API lives on a DIFFERENT prefix: `https://ahefi.com/api/vscode/*`
  (`/me`, `/keys`, `/usage`, `/logs`, `/billing/plan`) and requires the
  **account session token** (a JWT-ish string stored in SecretStorage as
  `ahefi.account.token`), NOT the API key — API key there returns
  `{"error":{"code":"bad_token"}}`.
- Models at time of writing (4): `gpt-6-luna`, `claude-opus-4-8`,
  `claude-opus-4-6`, `claude-haiku-4-5`. Fetch live via `/v1/models`; the
  extension's cached `cache/ahefi_models.json` holds a much longer stale list —
  trusting it will produce `model_not_found` for models like `gpt-4o-mini`.
- Non-existent paths (`/v1/messages`, `/v1/responses`, `/v1/me`) return the
  Next.js SPA HTML page with HTTP 200 — treat HTML as "route missing", not success.

## Triage that separated key-fault from provider-outage

1. `GET /v1/models` → 200 with the 4 models ⇒ key + base URL valid.
2. `POST /v1/chat/completions` for ALL 4 models, stream true/false, with and
   without extension headers → HTTP 502 `{"code":"upstream_error"}` in ~6s each.
3. Cross-checked with the provider's own `/api/vscode/logs` (account token):
   every row `status:"error", error_code:"upstream_error"` for the day —
   including requests made from inside VS Code itself.

Conclusion recorded for the user: key/plan fine (Power plan), upstream broken
server-side; adding it to 9router now would show Test failures that are NOT a
picking-wrong-baseUrl problem. Re-test later before touching config.

## 9router placement notes

- Prefix `ahefi` has no collision with 9router's native/hardcoded providers
  (`opencode`, `openrouter`, `cline`, `groq`, `gemini`, `nvidia`, `antigravity`),
  so a plain Custom OpenAI-compatible connection is safe — the native-collision
  failure mode described in the parent reference does not apply here.
- If chat later fails only in 9router while direct curl works, suspect the
  proxy/relay pool (`connectionProxyUrl`/`proxyPoolId`) rather than the key.
