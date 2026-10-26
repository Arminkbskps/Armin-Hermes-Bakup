# 9router Configuration & Provider Routing Reference

This reference documents internal architecture, configuration patterns, database schema, and troubleshooting recipes for **9router** (local LLM proxy router) and upstream providers.

---

## 1. Internal Architecture & Database Schema

9router stores its state in an SQLite database located at:
- **Windows:** `%APPDATA%\9router\db\data.sqlite` (`C:\Users\<user>\AppData\Roaming\9router\db\data.sqlite`)
- **Linux:** `~/.9router/db/data.sqlite` (under `$HOME`)
- **Default Port:** `20128` (dashboard at `http://127.0.0.1:20128/dashboard`, API at `http://127.0.0.1:20128/v1`)

### Key Tables:
1. `settings` (`id INTEGER PRIMARY KEY, data TEXT NOT NULL`):
   - Global routing strategies, capacity adapters, combo models, and **`providerStrategies`**.
   - Structure for routing a provider through a proxy pool or relay:
     ```json
     {
       "providerStrategies": {
         "opencode": {
           "proxyPoolId": "<proxy-pool-uuid>",
           "fallbackStrategy": "round-robin",
           "stickyRoundRobinLimit": 1
         },
         "cline": {
           "proxyPoolId": "<proxy-pool-uuid>",
           "fallbackStrategy": "round-robin",
           "stickyRoundRobinLimit": 1
         }
       }
     }
     ```
2. `proxyPools` (`id TEXT PRIMARY KEY, isActive INTEGER, testStatus TEXT, data TEXT, ...`):
   - Stores proxy nodes (Vercel Relay, Cloudflare Worker relay, HTTP/SOCKS5 pools).
   - Data structure:
     ```json
     {
       "name": "vercel-relay",
       "proxyUrl": "https://your-vercel-relay.vercel.app",
       "type": "vercel",
       "strictProxy": false,
       "lastError": null
     }
     ```
   - When `type` is `"vercel"`, `"cloudflare"`, or `"deno"`, 9router sets headers:
     `x-relay-target: https://<upstream-host>`
     `x-relay-path: /path/to/endpoint`
3. `providerNodes` & `providerConnections`:
   - Used for custom and OAuth-based connections.
   - Fields in `data`: `prefix`, `baseUrl`, `apiKey`, `accessToken`, `refreshToken`, `expiresAt`, `connectionProxyUrl`, `proxyPoolId`.
4. `combos` (`id TEXT PRIMARY KEY, name TEXT UNIQUE NOT NULL, kind TEXT, models TEXT NOT NULL, createdAt TEXT NOT NULL, updatedAt TEXT NOT NULL` — 6 columns):
   - Stores user-facing combo routing lists. `models` is a JSON array of model identifiers (e.g. `["cl/deepseek/deepseek-v4-flash", "cl/openrouter/free"]`).
   - NOTE: there is NO `description` column (older notes said otherwise) — it is `kind`. Any manual `INSERT` must supply all 6 values or SQLite fails with `table combos has 6 columns but N values were supplied`.

---

## 2. Built-in (Native) vs. Custom Providers

### Pitfall: Native Provider Name Collision
In 9router's Next.js server bundle, certain providers are **hardcoded / native** (e.g. `opencode`, `openrouter`, `antigravity`, `cline`, `groq`, `gemini`, `nvidia`).
- **Do NOT** add a "Custom Provider" with prefix `opencode` or `oc`. If you do:
  1. 9router's internal dispatcher intercepts requests to `opencode/*` or `oc/*` and routes them according to its built-in provider definition, bypassing your custom baseUrl.
  2. The custom connection validation will fail with:
     ```text
     Invalid API key or base URL
     ```
     because 9router attempts to test `${baseUrl}/models` against OpenAI specs while native providers might require specific headers or are `noAuth: true`.

### Solution:
- For providers with native support in 9router, use the **built-in provider** instead of creating a custom OpenAI-compatible node.
- To route native providers through an upstream proxy/relay (e.g. to bypass Iranian IP blocks or geo-restrictions), assign the `proxyPoolId` in `settings.data -> providerStrategies.<providerName>.proxyPoolId`.
- NEVER change the relay on your own initiative: the user explicitly vetoed auto-switching (Sept 2026 — the watchdog used to flip opencode vercel↔cloudflare every 250k tokens and the user saw it jump without asking). The relay stays EXACTLY as selected in the dashboard; automation may only report which pool is active, never write `proxyPoolId`.

### Stealth-model case study: `union-alpha` (Sept 2026)
- A free anonymous "stealth" model appeared 16 Sept 2026 on OpenRouter (`stealth/union-alpha`, 256K ctx, multimodal, frontier-class coding) and on OpenCode Zen (`union-alpha`, "Union Alpha Free", advertised ~1 week free).
- It vanished from the Zen catalogue days later (gone from the 74-model `/zen/v1/models` list and from opencode.ai docs — verified by relay fetch + Exa web search via the `agent-reach` skill). Direct chat returns `401 ModelError: Model union-alpha is not supported`.
- Lesson: when a Zen model 404s/401s with "not supported", check the LIVE upstream model list through the relay BEFORE touching local config — limited-time stealth models get pulled server-side and no local fix helps.

---

## 3. OpenCode Zen Free Tier Gate & 403 Bypass

### Error Signature:
```text
HTTP 403: {"type":"error","error":{"type":"FreeTierError","message":"Error from provider (Console): OpenCode's free tier can only be used from within OpenCode"}}
```

### The Upstream Gates:
OpenCode Zen (`https://opencode.ai/zen`) enforces strict verification on free tier models (`mimo-v2.5-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`, `ling-3.0-flash-fin-free`, `muse-spark-1.3-contributor-free`):
1. **Session Format:** Header `x-opencode-session` must be a 30-character string matching regex `^ses_[0-9a-f]{12}[0-9A-Za-z]{14}$`.
2. **Client Identification:**
   - `User-Agent: opencode/1.18.31 (win32 x64; node22.23.2)`
   - `x-opencode-client: cli` (or `desktop`)
   - `x-opencode-request: req_<32hex>`
   - `x-opencode-project: prj_<24hex>` (or `global`)
   - `authorization: Bearer public`
3. **Agent-Shaped Body:**
   - `stream: true` (mandatory upstream)
   - `tools`: Must include function tools named `bash` and `read`.
   - `tool_choice: "none"` (or `"auto"`)

### 9router Native Integration & 0.5.95+ Resolution:
- **In 9router v0.5.95+**: OpenCode is natively updated in chunk `6249.js` / `458.js` to route models (`muse-spark-1.2-contributor-free`, `muse-spark-1.3-contributor-free`) with `targetFormat: "openai-responses"`.
- Requests route directly to `https://opencode.ai/zen/v1/responses` with:
  1. Header `x-opencode-client: cli` (or `desktop`)
  2. Generated `x-opencode-session: ses_<12hex><14alphanumeric>` (30 chars)
  3. `tools` formatted as `{type: "function", name: "bash", parameters: {type: "object"}}` and `read`
  4. `tool_choice: "auto"`
- **Upgrade Resolution**: If 9router is running on an older version (e.g. 0.5.81) and throws 403 `FreeTierError` or `ModelError` on OpenCode, simply upgrade to latest:
  ```bash
  sudo npm install -g 9router@latest
  sudo systemctl restart 9router
  ```
  In 0.5.95+, both streaming and non-streaming responses through `oc/muse-spark-1.3-contributor-free`, `zen`, and `newModels` combos resolve cleanly without third-party proxy shims.

### Legacy 9router (v0.5.80 - v0.5.90) The "Agent Tools" Pitfall:
In stock 9router `chunks/318.js`, tool injection was conditioned on:
```javascript
Array.isArray(b.tools) && 0 !== b.tools.length || w(b, !0)
```
When downstream AI agents (Hermes, Cline, Roo-Code) pass their own tool definitions (e.g. `terminal`, `read_file`), `b.tools` is non-empty, causing 9router to **skip** running `w(b, !0)`! Upstream OpenCode Console inspects `tools`, notices `bash` and `read` are absent, and immediately rejects the call with `403 FreeTierError`.
- **The Legacy Fix**: In `.next-cli-build/server/chunks/318.js`, replace:
  ```javascript
  Array.isArray(b.tools)&&0!==b.tools.length||w(b,!0)
  ```
  with:
  ```javascript
  w(b,!0),b.tool_choice="auto"
  ```
  Function `w` will merge `bash` and `read` into `b.tools` alongside the agent tools and force `tool_choice="auto"`. (Or simply upgrade to 9router 0.5.95+).

---

## 4. Troubleshooting "Invalid API key or base URL" in 9router

When this error appears for a connection:
1. Inspect `providerConnections` in `data.sqlite`:
   ```sql
   SELECT id, provider, authType, name, data FROM providerConnections;
   ```
2. Check `data.providerSpecificData.baseUrl`. Common causes:
   - Double slashes (e.g. `http://127.0.0.1:8085//v1` instead of `http://127.0.0.1:8085/v1`).
   - Endpoint expects `/models` but baseUrl already includes trailing `/v1/` or `/v1/chat/completions`.
   - The connection was assigned a broken/inactive proxy pool (`proxyPoolId` pointing to an unreachable relay).
   - A custom connection was created for a service that 9router already handles natively (remove the custom connection and use the native one).

---

## 5. Headless / Remote 9router: Dashboard Auth, API Keys & Quick Tunnel

When running 9router headlessly on a remote Linux server or container:

### 1. Data Directory Resolution on Linux
- 9router resolves its config directory as `~/.9router/` based on `process.env.HOME`.
- If launched by a non-root user or from `/home/user`, the active SQLite database is `/home/user/.9router/db/data.sqlite` (NOT `/root/.9router/`). Verify with `lsof -p <9router-pid> | grep sqlite`.

### 2. Dashboard Password Authentication
- If `settings.data -> password` is unset, default password is `process.env.INITIAL_PASSWORD || "123456"`.
- To set or change the password directly:
  1. Hash with `bcrypt` (12 rounds): `bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()`.
  2. Update `settings` table: `UPDATE settings SET data = json_set(data, '$.password', '<hash>') WHERE id = 1;`.
- Login endpoint: `POST /api/auth/login` with `{"password": "..."}`. Returns `200` with `Set-Cookie: auth_token=...`.

### 3. Remote Access & API Key Enforcement
- When accessed over any remote hostname (e.g. Cloudflare tunnel), `middleware.js` enforces API key authentication on `/v1/*` routes:
  `{"error":"API key required for remote API access"}` (401).
- Keys must exist in `apiKeys` table and have matching `machineId`.
- **Recipe to generate a native valid API key headlessly**:
  Log in via `POST /api/auth/login` to get the `auth_token` cookie, then:
  ```bash
  curl -s -X POST "http://localhost:20128/api/keys" \
    -H "Content-Type: application/json" \
    -H "Cookie: auth_token=<cookie>" \
    -d '{"name": "Remote Tunnel Key"}'
  ```
- Use the resulting key as `Authorization: Bearer <key>` or `x-api-key: <key>`.

### 4. Zero-Registration Quick Tunnel (TryCloudflare)
- Run without an account:
  ```bash
  nohup cloudflared tunnel --url http://localhost:20128 --no-autoupdate > /var/log/tunnel.log 2>&1 &
  ```
- Read public URL: `grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /var/log/tunnel.log | head -1`.
- Note: Quick tunnel URLs rotate on process restart. Add a keepalive script to cron (`*/5 * * * *`).

---

## 6. Integrating Hermes Agent with 9router Combos

When configuring Hermes Agent (or its Telegram gateway) to consume 9router Combos, follow this exact pattern in `~/.hermes/config.yaml` (and `~/.hermes/profiles/<name>/config.yaml`):

### 1. Avoid Name Collisions with Built-in Providers
- Do NOT name your provider key `router` under `providers:` in `config.yaml`. Hermes maps `router` to built-in `ramp_router` (`AuthError: No usable credentials found for provider 'router'. Set RAMP_ROUTER_API_KEY`).
- Use `9router` as the provider key: `_shadowed_by_builtin("9router")` returns `False`.

### 2. Suppress the 1,100+ Raw Model Probe (`discover_models: false`)
- By default, Hermes probes `http://127.0.0.1:20128/v1/models` which returns every underlying provider model (1,150+ models), overwhelming the interactive Telegram `/model` keyboard.
- Set `discover_models: false` under `providers.9router` and explicitly declare the combo names in `models:`:
  ```yaml
  providers:
    9router:
      name: 9router
      base_url: http://127.0.0.1:20128/v1
      api_key: ${OPENAI_API_KEY}
      discover_models: false
      models:
        Antigravity: {}
        claude: {}
        NVIDIA: {}
        Cloudflare: {}
        gem: {}
        Cline: {}
        b.ai: {}
        newModels: {}
        orcarouter: {}
        zen: {}
        atria: {}
  ```

### 4. New Dashboard Combos Don't Appear in `/model` Until Config Is Re-Synced
- Combos created in the 9router dashboard land ONLY in SQLite (`combos` table). The Telegram `/model` picker reads from Hermes `config.yaml` — `providers.9router.models` + the `custom_providers` entry named `9router` + `model_aliases` — NOT from the DB. A new combo is invisible in chat until all three are re-synced (verified live: a fresh `Anti` combo existed in DB while config still listed stale `zen`/`atria` that weren't even in the DB anymore).
- Sync FROM the DB (source of truth), never by hand — hand edits drift. Recipe (needs PyYAML; on hermes hosts use the venv python — system `python3` often lacks `yaml`):
  ```python
  import sqlite3, yaml
  db = sqlite3.connect('/home/user/.9router/db/data.sqlite')
  combos = sorted(r[0] for r in db.execute('SELECT name FROM combos'))
  cfg = yaml.safe_load(open('/home/user/.hermes/config.yaml'))
  cfg.setdefault('providers', {}).setdefault('9router', {})['models'] = {n: {} for n in combos}
  for cp in (cfg.get('custom_providers') or []):
      if isinstance(cp, dict) and cp.get('name') == '9router':
          cp['models'] = list(combos)
  valid = set(combos)
  kept = {k: v for k, v in (cfg.get('model_aliases') or {}).items()
          if isinstance(v, dict) and v.get('model') in valid}
  have = {v['model'] for v in kept.values()}
  for n in combos:
      if n not in have:
          kept[n.lower()] = {'model': n, 'provider': '9router',
                             'base_url': 'http://127.0.0.1:20128/v1'}
  cfg['model_aliases'] = kept
  m = cfg.get('model') or {}
  if m.get('default') not in valid:
      m['default'] = 'newModels' if 'newModels' in valid else combos[0]
      cfg['model'] = m
  yaml.safe_dump(cfg, open('/home/user/.hermes/config.yaml', 'w'),
                 sort_keys=False, allow_unicode=True)
  ```
- Back up `config.yaml` first (`cp config.yaml config.yaml.bak-<ts>`), then verify round-trip: re-read the file and assert all three lists equal the DB combo list.
- NO gateway restart needed for list changes — the gateway re-reads `config.yaml` on every `/model` call. To make it self-healing, hook the sync script into the periodic backup loop (run sync BEFORE tar, so backups also carry the fresh config).
- Non-destructive test: INSERT a fake combo (all 6 columns!), run sync, assert it appears in all three lists, then restore the DB from a backup copy and re-sync to roll back clean.

---

### 5. Add Direct Aliases to Avoid Provider Ambiguity
- Certain combo names (like `claude`) collide with Hermes built-in provider aliases. Typing `/model claude` would otherwise attempt to route to Anthropic directly without an Anthropic API key.
- Populate `model_aliases:` so that both typed `/model <name>` commands and button clicks resolve directly to `9router`:
  ```yaml
  model_aliases:
    antigravity:
      model: Antigravity
      provider: 9router
      base_url: http://127.0.0.1:20128/v1
    claude:
      model: claude
      provider: 9router
      base_url: http://127.0.0.1:20128/v1
    zen:
      model: zen
      provider: 9router
      base_url: http://127.0.0.1:20128/v1
    newmodels:
      model: newModels
      provider: 9router
      base_url: http://127.0.0.1:20128/v1
  ```

---

## 7. Cline Provider Architecture, Token Refresh & Combo Failures

### 1. Cline Authentication Format
- Upstream endpoint: `https://api.cline.bot/api/v1/chat/completions`
- Token format: Authorization header MUST format tokens as `Bearer workos:<token>` (or `Bearer <token>` if already starting with `workos:`). In 9router `chunks/827.js`, function `clineHeaders` enforces this prefix.
- Refresh endpoint: `POST https://api.cline.bot/api/v1/auth/refresh` with body:
  ```json
  {"refreshToken": "<token>", "grantType": "refresh_token", "clientType": "extension"}
  ```

### 2. The Multi-Account Round-Robin 401 Trap
- When multiple Cline connections exist in `providerConnections`:
  If even **ONE** connection has a revoked or expired refresh token (e.g. upstream returns `{"data":"","error":"failed to refresh token: invalid_grant","success":false}`), 9router will intermittently pick that connection during round-robin dispatch.
- Symptom: Downstream clients receive:
  ```text
  HTTP 401: {"error":"Unauthorized: Please make sure you're using the latest version of Cline and re-authenticate your Cline account."}
  ```
- **Remedy**:
  1. Probe all Cline connections in `providerConnections` via the refresh endpoint.
  2. For any connection returning `invalid_grant`, immediately set `isActive = 0` or delete the row from SQLite:
     ```sql
     DELETE FROM providerConnections WHERE provider = 'cline' AND name = 'revoked-account@example.com';
     ```
  3. Update remaining connections with refreshed `accessToken`, `refreshToken`, and `testStatus = 'active'`.

### 3. Single-Model Rate Limit Trap (429 INFERENCE_CAP_ERROR)
- Free accounts have strict daily limits on specific models (e.g. `z-ai/glm-5.3-flash`: `Daily free limit reached on model ... Try again in 33m`).
- If the `Cline` combo contains only `["cl/z-ai/glm-5.3-flash"]`, hitting the cap breaks the entire combo.
- **Remedy**: Configure multi-model fallback chaining in the `combos` table:
  ```sql
  UPDATE combos SET models = '["cl/deepseek/deepseek-v4-flash", "cl/openrouter/free", "cl/z-ai/glm-5.3-flash"]' WHERE name = 'Cline';
  ```
  Both `deepseek/deepseek-v4-flash` and `openrouter/free` provide stable, zero-cost completions through Cline.

---

## 8. Server-to-Server Migration & Telegram Polling Safety

When migrating a Hermes Agent profile and 9router instance between cloud sandboxes (e.g. Superserve, Daytona, VPS):

### 1. Direct Server-to-Server Streaming (Bypassing Slow Local Context)
- Passing large tarballs through local shell buffers or command-line strings triggers `argument list too long` (E2BIG) errors.
- Use ephemeral single-use upload endpoints directly from the source sandbox:
  ```bash
  # Source sandbox:
  curl -s -F "reqtype=fileupload" -F "time=1h" -F "fileToUpload=@/tmp/user1_hermes.tar.gz" https://litterbox.catbox.moe/resources/internals/api.php
  # Destination sandbox:
  curl -s -L <url> -o /tmp/hermes.tar.gz && tar -xzf /tmp/hermes.tar.gz -C /home/user/.hermes
  ```

### 2. Telegram Bot Polling Conflict (409 Conflict)
- Telegram bot API allows only ONE active long-polling connection (`getUpdates`) per bot token at a time.
- If two Hermes gateway processes poll the same token simultaneously (source server + destination server), both experience constant connection cycling:
  `httpx.RemoteProtocolError: Server disconnected without sending a response.`
- **Mandatory Sequence**:
  1. Identify and cleanly terminate the gateway PID on the old sandbox (`kill -9 <old-gateway-pid>`).
  2. Clean lock files on destination (`rm -f /home/user/.hermes/gateway.* /home/user/.hermes/*.sock`).
  3. Start the gateway on the destination sandbox.

---

## 9. Multi-Tenant & Multi-User 9router Isolation & Credential Sanitization

When separating a single 9router instance across multiple users or sandboxes (e.g. moving one user's private setup to a new server while creating a dedicated, sanitized instance for another user):

### 1. Provider Definitions (`providerNodes`) vs. Private Credentials (`providerConnections`)
- Custom OpenAI-compatible or Anthropic-compatible providers have their interface definitions stored in `providerNodes`:
  `('openai-compatible-chat-<uuid>', 'openai-compatible', '<name>', '{"prefix":"...","baseUrl":"..."}')`
- Individual user keys, tokens, and OAuth sessions live in `providerConnections` (`apiKey`, `accessToken`, `refreshToken` inside JSON column `data`).
- **Sanitization Rule**: To leave a provider shell available for another user without leaking your private credentials:
  1. KEEP the provider metadata in `providerNodes` (`WHERE name = '<provider>'`).
  2. DELETE all credential rows for that provider from `providerConnections`:
     ```sql
     DELETE FROM providerConnections WHERE provider = 'openai-compatible-chat-<uuid>';
     ```
  3. The provider will remain defined and selectable in the dashboard, but with zero stored keys or accounts.

### 2. Purging Personal OAuth & API Connections
To ensure no private emails, Google OAuth sessions, or paid API keys remain accessible to the second user:
```sql
-- Keep only anonymous / public providers (e.g. opencode):
DELETE FROM providerConnections WHERE provider != 'opencode';

-- Delete custom provider definitions that the second user should not see:
DELETE FROM providerNodes WHERE name NOT IN ('atria');

-- Retain only anonymous combos in SQLite:
DELETE FROM combos WHERE name NOT IN ('newModels', 'zen');
```

### 3. Cleaning Up `providerStrategies` in `settings`
The `settings` table contains routing maps and proxy pool links (`providerStrategies`). Clean out references to deleted providers:
```python
import sqlite3, json
con = sqlite3.connect('/home/user/.9router/db/data.sqlite')
row = con.execute('SELECT data FROM settings WHERE id=1').fetchone()
s = json.loads(row[0])
s['providerStrategies'] = {
    'opencode': s['providerStrategies'].get('opencode', {
        'proxyPoolId': '<relay-pool-id>',
        'fallbackStrategy': 'round-robin',
        'stickyRoundRobinLimit': 1
    })
}
con.execute('UPDATE settings SET data=? WHERE id=1', (json.dumps(s),))
con.commit()
```

### 4. Updating Downstream Hermes Client Configuration
When removing personal combos (`Antigravity`, `claude`, `NVIDIA`, etc.), the downstream Hermes agent configuration (`~/.hermes/config.yaml` or `~/.hermes/profiles/<profile>/config.yaml`) must be synchronized:
1. Update `model.default` to point to a surviving combo:
   ```yaml
   model:
     default: newModels
     provider: 9router
     base_url: http://127.0.0.1:20128/v1
   ```
2. Update `providers.9router.models`, `custom_providers`, and `model_aliases` to match only the available sanitized models (`newModels`, `zen`, etc.).
3. Restart the Hermes gateway process (`kill -9 <pid>` and re-run) so the agent turn machinery re-warms with valid model schemas.
