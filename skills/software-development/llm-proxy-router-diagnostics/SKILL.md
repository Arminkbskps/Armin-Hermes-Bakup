---
name: llm-proxy-router-diagnostics
description: "Diagnose 9router/LiteLLM and upstream provider failures."
version: 1.3.0
---

# LLM Proxy Router Diagnostics & Health Recovery

Use when diagnosing, configuring, or recovering local multi-provider LLM routers (such as 9router, LiteLLM, or OmniRoute) when upstream providers fail, combos break, or client requests return errors.

## 1. Database & State Inspection Procedure

For 9router, state lives in SQLite at `~/.9router/db/data.sqlite` (Linux) or `%APPDATA%\9router\db\data.sqlite` (Windows):

```bash
python3 - << 'EOF'
import sqlite3, json

conn = sqlite3.connect("/home/daytona/.9router/db/data.sqlite")
cursor = conn.cursor()

# 1. Active provider connections & relay pools
print("=== ACTIVE CONNECTIONS ===")
for r in cursor.execute("SELECT id, provider, name, isActive, data FROM providerConnections WHERE isActive=1").fetchall():
    d = json.loads(r[4])
    proxy_pool = d.get('providerSpecificData', {}).get('proxyPoolId')
    print(f"[{r[1]}] {r[2]} | Pool: {proxy_pool} | Error: {d.get('lastError')}")

# 2. Check combo definitions
print("\n=== COMBOS ===")
for r in cursor.execute("SELECT name, models FROM combos").fetchall():
    print(f"Combo: {r[0]} -> {r[1]}")
EOF
```

## 2. Systematic Upstream Error Code Matrix

When requests fail, test each connection directly via `POST http://127.0.0.1:20128/v1/chat/completions` with a minimal prompt:

| Error Signature | Root Cause | Remediation |
|---|---|---|
| `401 {"error":"API key required for remote API access"}` | Client sending invalid or missing key. **Trap**: Hermes CLI redacts `sk-...` keys in terminal output to `sk-xxx...yyyy`; do not mistake terminal redaction for literal dots. Verify key byte length or encode via `base64 -w0` before editing. | Check `SELECT key FROM apiKeys WHERE isActive=1` and ensure exact match in client `.env` / `config.yaml`. |
| `403 [antigravity] VALIDATION_REQUIRED` (`Verify your account`) | Google flagged Antigravity OAuth session for interactive checkpoint verification (frequent on cloud/datacenter IPs). | **Do NOT just log into Gmail** — standard login does not clear this checkpoint. Extract the tokenized `validation_url` from `error.details[].metadata.validation_url` (contains `plt=...` and redirects to `auth_success_gemini`). **Multi-account hijack trap**: Open in an Incognito/Private window signed into the *flagged account only*; otherwise Google evaluates the link against the browser's default profile and falsely reports success while the connection stays 403. Alternatively, deactivate flagged connections (`UPDATE providerConnections SET isActive=0 WHERE id=?`) so healthy accounts handle traffic. |
| `429 [antigravity] Resource has been exhausted` | Gemini Code Assist 5-hour or daily rolling sliding-window quota exhausted for that Google account. | Query exact reset timestamp via `v1internal:retrieveUserQuota` (see below) to know when the window lifts, or rotate to a fresh Google account. |
| `401 {"type":"AuthError","message":"Missing API key."}` | Upstream terminated anonymous free tier (e.g. OpenCode). | Model requires paid API key. Remove from free combos. |
| `403 {"type":"FreeTierError","message":"...only be used from within OpenCode"}` | Upstream added desktop client telemetry verification. | Do not route automated agent requests to this model; switch combo to official providers. |
| `401 {"error":"Unauthorized...re-authenticate"}` | OAuth session expired or refresh token revoked (e.g. Cline WorkOS). | Mark connection inactive or re-authenticate via the web dashboard (`/dashboard/providers`). |
| `400 credit insufficient balance: balance=0` | Provider account balance exhausted (e.g. b.ai). | Replenish credits or disable connection in `providerConnections`. |
| `403 insufficient_user_quota` | Aggregator wallet depleted (e.g. AIHubMix). | Recharge wallet or point downstream agent to alternate provider. |
| `404 model_retired` or `410 Gone` | Upstream provider deprecated the model ID (e.g. Groq, NVIDIA, AIHubMix). | Probe provider's `/v1/models` live endpoint and update combo to the active model ID. |
| `404 No active credentials for provider: <name>` | Name collision between a custom node and a native built-in provider (e.g. `atria`). | Route using the exact node ID prefix (`openai-compatible-chat-<uuid>/<model>`) or use an explicit combo entry. |
| `502 fetch failed (cause: ECONNREFUSED 127.0.0.1:<port>)` | Local reverse-engineered helper daemon stopped (e.g. Chat2API on port 2026). | Start the background daemon or remove the dead connection from active pools. |

## 3. Combo Failure Traps

1. **The Single-Provider Combo Trap**: If a combo (e.g. `newModels` or `zen`) contains only models from one upstream source that changes its policy (e.g. OpenCode), the entire combo will break simultaneously.
   - **Fix**: Update the `combos` table in SQLite to chain multi-provider fallbacks:
     ```sql
     UPDATE combos SET models = '["ag/gemini-3.8-flash-high", "ag/gemini-3.7-flash-medium", "atria/Atria-Dawn-Preview"]' WHERE name = 'newModels';
     ```
2. **Hermes Config Sync**: New or updated combos in 9router SQLite do not appear in Hermes `/model` until `~/.hermes/config.yaml` is re-synced (`providers.9router.models` and `model_aliases`).
3. **Antigravity Multi-Account Degradation Trap**: In multi-account `antigravity` pools, 9router defaults to round-robin. If any account in the pool gets flagged with Google's `VALIDATION_REQUIRED` (403), requests hitting that account fail immediately and poison the entire combo via cooldowns.
   - **Critical Probe Pitfall**: Do NOT rely on `v1internal:loadCodeAssist` to test account health — it returns HTTP 200 even for accounts locked with 403 `VALIDATION_REQUIRED` or quota-exhausted with 429. Probe the actual generation endpoint:
     ```bash
     curl -s -X POST https://cloudcode-pa.googleapis.com/v1internal:generateContent \
       -H "Authorization: Bearer <ACCESS_TOKEN>" \
       -H "Content-Type: application/json" \
       -H "User-Agent: antigravity/ide/2.22.0 darwin/arm64" \
       -d '{"project": "aicode-consumers", "model": "gemini-2.5-flash", "request": {"contents": [{"role": "user", "parts": [{"text": "hi"}]}]}}'
     ```
     Flagged accounts return 403 `VALIDATION_REQUIRED` (with the `validation_url` needed to unlock); exhausted accounts return 429; healthy accounts return 200 with generated text.
   - **Inspect Quota Reset Time**: For 429 accounts, retrieve the exact reset timestamp via:
     ```bash
     curl -s -X POST https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota \
       -H "Authorization: Bearer <ACCESS_TOKEN>" \
       -H "Content-Type: application/json" \
       -H "User-Agent: antigravity/ide/2.22.0 darwin/arm64" \
       -H "X-Client-Name: antigravity" \
       -H "X-Client-Version: 2.22.0" \
       -d '{}'
     ```
     Returns `buckets[].resetTime` (ISO 8601 UTC) and `remainingFraction` for each model bucket (e.g. `gemini-3.8-flash-*`, `claude-*`).
   - **Fix**: Deactivate flagged/exhausted connections via `UPDATE providerConnections SET isActive=0 WHERE id=...` so only healthy accounts handle traffic.

## 4. OpenCode Free Unlimited Mode (No API Key)

The `opencode` provider is `category:"free"` with `noAuth` — clearing its stored key switches it to unlimited free-lane mode (`Bearer public` + desktop headers). An API key on this provider imposes caps and paywalls instead of removing them.

- Prefer empty `apiKey` on `provider='opencode'` for unlimited free models (`oc/muse-spark-1.3-contributor-free`); back up `data.sqlite` first, then `UPDATE providerConnections SET data=json-cleared, updatedAt=datetime('now') WHERE provider='opencode'`.
- Keep paid `opencode-zen` (`isActive=0`) disabled while the free lane is in use so routing never drifts onto the metered transport.
- Restart with `pm2 restart 9router --update-env`, wait for `GET /api/version` to answer, verify `GET /v1/models` lists the `oc/*-free` IDs, then `pm2 save` so the router auto-starts after reboot.
- Prove the lane with one live `POST /v1/chat/completions` on the combo before reporting success.

## 5. Reporting Rule

Deliver 9router operations as one consolidated message (state, what changed, live verification, what remains) — never piecemeal progress updates while tools run.

## 6. Headless Google OAuth Account Provisioning for Antigravity

When connecting new Google accounts for Antigravity headlessly (e.g. from chat or remote terminal without access to 9router's Next.js web dashboard):

1. **Authentication Gate**: 9router's internal REST endpoints under `/api/oauth/*` reject unauthenticated calls with 401. To bypass headlessly, mint an HS256 JWT using `~/.9router/jwt-secret` (or pass `x-9r-cli-token` if CLI auth is set):
   ```python
   import hmac, hashlib, base64, json, time
   secret = open('/home/daytona/.9router/jwt-secret').read().strip().encode('utf-8')
   now = int(time.time())
   h = base64.urlsafe_b64encode(b'{"alg":"HS256","typ":"JWT"}').decode().rstrip('=')
   p = base64.urlsafe_b64encode(json.dumps({"iat": now, "exp": now + 86400}).encode()).decode().rstrip('=')
   sig = base64.urlsafe_b64encode(hmac.new(secret, f"{h}.{p}".encode(), hashlib.sha256).digest()).decode().rstrip('=')
   auth_cookie = f"auth_token={h}.{p}.{sig}"
   ```

2. **Generate Authorization URL**:
   Call `GET http://localhost:20128/api/oauth/antigravity/authorize?redirect_uri=http://localhost:8080/callback` with `Cookie: {auth_cookie}`.
   - It returns `{authUrl, state, codeVerifier, codeChallenge, redirectUri}`.
   - **Targeting Specific Accounts**: Append `&login_hint=<email>` to `authUrl` so Google opens the account selection pre-filled with the intended Google email.
   - Store `{state, codeVerifier, redirectUri, email}` locally for the exchange step.

3. **Complete Token Exchange**:
   After the user authorizes in browser and copies the redirected URL (`http://localhost:8080/callback?state=...&code=4/0A...`), extract the `code` parameter and execute:
   ```bash
   curl -X POST http://localhost:20128/api/oauth/antigravity/exchange \
     -H "Cookie: auth_token=<JWT>" \
     -H "Content-Type: application/json" \
     -d '{"code": "<AUTH_CODE>", "redirectUri": "http://localhost:8080/callback", "codeVerifier": "<VERIFIER>", "state": "<STATE>"}'
   ```
   9router will exchange the code with Google, retrieve the associated Google Cloud project ID, create the active record in `providerConnections`, and immediately begin routing requests to the new account.

4. **Immediate Post-Exchange Health Check & Validation Unlock**:
   Immediately run a probe against `https://daily-cloudcode-pa.googleapis.com/v1internal:generateContent` with the new access token.
   - If Google returns HTTP 403 `PERMISSION_DENIED` with `reason: "VALIDATION_REQUIRED"`, extract the `validation_url` from `error.details[].metadata.validation_url` (carries the live security challenge ticket `plt=...`).
   - Send this exact link to the user to complete verification in their browser under that account.
   - Once verified, re-probe — the account transitions to HTTP 200 without re-exchanging tokens.
