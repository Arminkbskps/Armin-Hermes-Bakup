# 9router OAuth Refresh Failures ("Token expired and refresh failed")

Error signature from provider connection Test/Validate:
```text
Token expired and refresh failed
```
This is an **OAuth-layer** failure (Cline, Claude, Gemini-CLI, Antigravity, Kiro, Codex...), NOT a wrong 9router API key. The access token is past `expiresAt` and the background `POST` to the upstream refresh endpoint failed.

## 1. How the refresh path works (v0.5.81, chunk 827.js `s(a)` / 3943.js `fp`)

- Expiry check `fp(provider, record)`: returns expired when `expiresAt - now < refreshLeadMs`, or when `maxRefreshAgeMs` passed since `lastRefreshAt`.
- Cline refresh call:
```text
POST https://api.cline.bot/api/v1/auth/refresh
{"refreshToken": "<25-char token>", "grantType": "refresh_token", "clientType": "extension"}
```
- On non-OK response `s(a)` returns `null` → caller emits `Token expired and refresh failed`. No status body is surfaced, so you must reproduce manually.

## 2. Check these FIRST (in order)

1. **Dead local proxy env is the #1 cause.** 9router inherits `http_proxy/https_proxy/all_proxy` from its parent shell. If they point at a VPN/proxy port that is no longer listening (e.g. `127.0.0.1:10808` with nothing on it), EVERY refresh dies with connection-refused while the user thinks "internet works".
   ```bash
   env | grep -i proxy
   powershell -Command 'Get-NetTCPConnection -State Listen | Where-Object { $_.LocalPort -eq 10808 } ...'
   curl -v -m 12 https://api.cline.bot/api/v1/users/me        # follows env proxy -> expect "Failed to connect ... 10808"
   curl -s -m 12 --noproxy '*' https://api.cline.bot/api/v1/users/me  # bypass -> 403 means reachable (auth wall, not network)
   curl -s -m 10 --noproxy '*' https://www.google.com            # 200 = direct internet OK
   ```
2. **Read the stored OAuth state** (`%APPDATA%\9router\db\data.sqlite`, table `providerConnections`, JSON in `data` column — there is no `testStatus` column, it lives inside `data`):
   ```python
   import sqlite3, json
   db = r'C:/Users/<user>/AppData/Roaming/9router/db/data.sqlite'
   con = sqlite3.connect(db); cur = con.cursor()
   cur.execute("SELECT name, data FROM providerConnections WHERE provider='cline'")
   for name, data in cur.fetchall():
       j = json.loads(data)
       print(name, '| expiresAt:', j.get('expiresAt'), '| testStatus:', j.get('testStatus'),
             '| lastError:', str(j.get('lastError'))[:120])
   ```
   All-expired `expiresAt` + `lastError: Token expired and refresh failed` confirms the class.
3. **Check per-provider proxy strategy** (`settings.data -> providerStrategies`): a provider with NO `proxyPoolId` uses the process env proxy (or direct). One routed through a `vercel`/`cloudflare` relay pool bypasses the local proxy entirely:
   ```python
   cur.execute('SELECT data FROM settings')
   j = json.loads(cur.fetchone()[0])
   print(j.get('providerStrategies', {}).get('cline'))     # often {} -> env-proxy dependent
   print(j.get('providerStrategies', {}).get('opencode'))  # example with proxyPoolId set
   ```

## 3. Fixes (pick one)

- **A. Restart the local proxy** (VPN/V2Ray/Nekoray) so the configured port listens again, then press Test/Validate on the connection in the dashboard.
- **B. Run 9router proxy-free** when direct internet reaches the upstream (verified by the `--noproxy` 403/200 probes above):
  ```bash
  unset http_proxy https_proxy HTTP_PROXY HTTPS_PROXY all_proxy ALL_PROXY
  # restart 9router from the same shell
  ```
  Or exempt just the upstream: `NO_PROXY="$NO_PROXY,api.cline.bot,cline.bot"`.
- **C. Route the provider through an existing relay pool** (same pattern opencode uses): set `providerStrategies.<name>.proxyPoolId` to the vercel/cloudflare pool UUID in 9router settings.
- Only if refresh still fails after network is fixed: Disconnect + reconnect OAuth (refresh token itself may be revoked). A freshly created 9router API key never fixes this error.

## 4. Pitfalls

- Do NOT confuse the 9router dashboard API key with the upstream OAuth token — regenerating the API key does nothing for this error.
- Do NOT run two 9router versions at once (e.g. NVM global `0.5.81` vs bundled `0.5.55`): check `where.exe 9router` and which PID listens on 20128 before debugging tokens.
- `python urllib` in a proxy-polluted shell also fails with `WinError 10061` — re-run probes with `urllib` bypass or `curl --noproxy '*'` to separate "proxy dead" from "upstream dead".
- **Windows Registry Proxy Leak:** On Windows, `urllib.request` consults `Internet Settings\ProxyServer` in the Windows registry even after `os.environ` proxy vars are cleared. For localhost/relay calls, you MUST install an explicit empty `ProxyHandler`:
  ```python
  urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
  ```
  Without this, any background Python service (like `retry_shim.py` or `watch_router.py`) attempting to reach `127.0.0.1:20128` will silently route through the dead proxy (e.g. `10808`) and loop in connection errors.
- **Deactivate revoked accounts immediately:** When a Cline account's refresh token is revoked upstream (`HTTP 400 invalid_grant`), set `isActive=0` and `testStatus='error'` in `providerConnections` so 9router's priority sort excludes it; otherwise it stays #1 and blocks downstream consumers.

## 5. Cline-specific findings (verified Sept 2026, 9router v0.5.81)

- **Direct access to `api.cline.bot` is geo-blocked from Iranian IPs at the WAF layer** — `POST /api/v1/auth/refresh` returns `403 Forbidden` HTML for node, browser, AND curl User-Agents alike. For Cline, a `--noproxy` 403 does NOT mean "reachable, auth wall" — it means blocked. The identical refresh through the Vercel relay returned `200` with fresh tokens. Fix C (relay route) is the reliable path for Cline, not just an option.
- **Chat needs the `workos:` token prefix.** 9router's runtime refresh (`refreshCline`, chunk `318.js`) stores `accessToken` as `workos:<jwt>`, but tokens written by the older test path (chunk `827.js`) lack it. A fresh but unprefixed token passes refresh/validate yet fails chat with `401 Unauthorized: ... re-authenticate your Cline account`. Fix in `data.sqlite`:
  ```python
  if at.startswith('eyJ') and not at.lower().startswith('workos:'):
      j['accessToken'] = 'workos:' + at
  ```
- **The dashboard Test/Validate button uses the DIRECT path, not the relay** — it can stay red even when chat via relay works. First verify with a real `POST http://127.0.0.1:20128/v1/chat/completions` call (a `200` reply is the ground truth, not the Test button color); for the permanent fix see §7 (patch `p`/`s` in `827.js` to route through `u()`).
- **Refresh HTTP 400 = refresh token revoked server-side** — no retry or relay will save it. Set that connection `isActive=0` (round-robin then uses only healthy accounts) and re-do OAuth (Disconnect + Connect) in the dashboard.
- **Model name forms:** `cl/anthropic/claude-sonnet-4.6` (slash form) routes to Cline; the dashed form (`cl-anthropic-...`) 404s with `No active credentials for provider: openai`.
- **Manual relay refresh recipe** (when dashboard Test can't reach upstream): `POST <relay-url>` with JSON body `{"refreshToken","grantType":"refresh_token","clientType":"extension"}` plus headers `x-relay-target: https://api.cline.bot`, `x-relay-path: /api/v1/auth/refresh`; write back `accessToken/refreshToken/expiresAt/lastRefreshAt/testStatus`. Always back up `data.sqlite` first.

## 6. Why dashboard Test stays red while chat works (v0.5.81, chunk 827.js)

- Test entry is module `66328` (`F` → `w(connectionId)`): loads the connection via `Mc`, resolves proxy via `(0,e.B)(connection.providerSpecificData||{})`, then calls `t(connection, proxyConfig)` (or `v` for apikey).
- Inside `t`, the Cline branch uses two helpers that **hardcode direct `fetch` and ignore the proxy-config arg**: `p(token)` → `GET https://api.cline.bot/api/v1/users/me`, and `s(record)` → `POST .../auth/refresh`. The generic helper `u(url, opts, proxyConfig)` (which honors `vercelRelayUrl`/connection proxy) is used by every other branch but NOT by `p`/`s`.
- Consequence: setting `settings.providerStrategies.cline.proxyPoolId` fixes the **chat** path (runtime chunk `318.js` honors it) but does NOT fix Test. Test-green requires a code patch making `p`/`s` route through `u()` with the resolved proxy config; until then, accept red-Test/green-chat and verify with a real `POST http://127.0.0.1:20128/v1/chat/completions` call.
- `w()` reads the relay from **per-connection** `providerSpecificData.proxyPoolId`, not from `settings.providerStrategies` — don't confuse the two levels when debugging Test vs chat.
- Function map in `827.js`: `p` = users/me probe, `s` = refresh dispatcher, `t` = test orchestrator, `u` = proxy-aware fetch wrapper, `w` = connection test + DB writeback (`testStatus/lastError/newTokens` into the `data` JSON column).

## 7. Cline Test-button patch (applied Sept 2026, still UNVERIFIED end-to-end)

Patch script (idempotent asserts, backs up first):
`C:\Users\Radon System\AppData\Local\Temp\patch_827.py` → patches
`.../9router/app/.next-cli-build/server/chunks/827.js` (sha `44ac1702…` →
`8507c4b5…`, backup `827.js.bak-20260919`). 8 replacements:

1. `p(a)` → `p(a,B=null)` routed through `u(url, opts, B)` (users/me via relay).
2. `s(a)` → `s(a,B=null)`; cline branch uses `u(l.lB.refreshUrl, …, B)`.
3. Refreshed cline token gets the `workos:` prefix at write time (matches runtime).
4. `t()`: captures the resolved proxy config as `B=b` (renamed call-site vars
   `C`/`d` to avoid TDZ shadow of the inner lowercase `b` lambdas) and passes `B`
   into every `s(...)` / `p(...)` call (expiry-refresh, gemini retry, cline
   validate, post-401 paths, generic retry).

Caveats for the next session:
- The respawned server (tray auto-restart) serves the patched file from disk, but
  **dashboard Test has NOT been clicked / verified green yet** — do that first.
- `w()` resolves the relay from **per-connection** `providerSpecificData.proxyPoolId`
  (see §6), NOT from `settings.providerStrategies.cline`. If Test still fails
  after the patch, copy the vercel `proxyPoolId` (`cbb8ae02-…`) into each cline
  connection's `providerSpecificData` as well.
- Rollback: restore `827.js.bak-20260919` over `827.js` while the server is stopped.
- Upstream `npm install -g 9router` / version bump will overwrite the patch —
  re-apply `patch_827.py` (asserts will fail loudly if upstream changed the code).

## 8. Windows install-path + relay-selection notes

- `C:/nvm4w/nodejs/node_modules/9router` and `C:/nvm_root/v22.22.0/node_modules/9router` can be the SAME file (junction). Verify with `os.path.samefile(p1, p2)` / SHA-256 before patching — one backup + one patch covers both paths.
- Relay choice matters: the Vercel relay returned `200` for the Cline refresh while the Cloudflare relay returned `403 error 1010 (browser_signature_banned)` for the identical request. Test each relay with the real refresh payload before assigning `proxyPoolId`.
- Always back up before direct writes: `cp data.sqlite data.sqlite.bak-YYYYMMDD` and `cp 827.js 827.js.bak-YYYYMMDD`. `data.sqlite` has `-shm`/`-wal` sidecars — copying while 9router runs is fine for a rollback snapshot, but restore only while the server is stopped.
- Minified-chunk search recipe: `grep -rl <term> <9router>/app/.next-cli-build/server/chunks/` to locate the chunk, then `node --input-type=module` + `JSON.stringify(slice)` to print unicode-safe snippets on Windows.
