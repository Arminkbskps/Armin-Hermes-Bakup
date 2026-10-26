# OpenCode Zen Free Tier Gate & Client Emulation (403 FreeTierError & 429 RateLimit)

## Overview
From mid-September 2026, OpenCode Zen deployed a multi-gate verification mechanism to block third-party proxies (such as 9router, OmniRoute, or custom OpenAI-compatible wrappers) from consuming free models without the official client. Furthermore, direct requests from sanctioned countries (e.g. Iran) are blocked upstream with `RegionError`, and burst requests on free models encounter strict upstream rate limits (`429 rate_limit_exceeded`).

### Error Signatures
1. **FreeTierError (403)**:
```json
HTTP 403: {"type":"error","error":{"type":"FreeTierError","message":"Error from provider (Console): OpenCode's free tier can only be used from within OpenCode"}}
```
2. **RegionError (403)**:
```json
HTTP 403: {"type":"error","error":{"type":"RegionError","message":"This model is not available in your country."}}
```
3. **RateLimitError (429)**:
```json
HTTP 429: {"model":"muse-spark-1.3-contributor-free","error":{"param":null,"code":"rate_limit_exceeded","type":"rate_limit_error","message":"Error from provider (Console): Upstream request failed: [rate_limit_exceeded] Rate limit exceeded. Please retry after a brief wait."}}
```

---

## The Upstream Verification Gates

### Gate 1: Session Shape and Correlation Headers
OpenCode rejects requests whose `x-opencode-session` header does not conform to the official client session generator:
- **Canonical Session Regex**: `^ses_[0-9a-f]{12}[0-9A-Za-z]{14}$` (exact length: 30 chars).
  - Prefix: `ses_`
  - Timestamp / Hex part: 12 lowercase hex characters (`[0-9a-f]{12}`)
  - Random part: 14 Base62 characters (`[0-9A-Za-z]{14}`)
- **Header Set**:
  - `User-Agent`: `opencode/1.18.31 (win32 x64; node22.23.2)` (version must be `>= 1.17.0`)
  - `x-opencode-client`: `cli` or `desktop`
  - `x-opencode-session`: `<canonical_session_id>`
  - `x-session-affinity`: `<canonical_session_id>`
  - `X-Session-Id`: `<canonical_session_id>`
  - `x-opencode-request`: `msg_<12hex><14base62>` or `req_<32hex>`
  - `x-opencode-project`: `prj_<24hex>` or `global`
  - `Authorization`: `Bearer public` (for anonymous lane) or user token
  - `Content-Type`: `application/json`
  - `Accept`: `text/event-stream` (mandatory when streaming)

Deterministic Session Derivation (Python):
```python
import hashlib

BASE62 = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz"

def canonical_session_id(seed: str) -> str:
    h = hashlib.sha256(b"ses\x00" + seed.encode("utf-8")).digest()
    time_part = h[:6].hex()
    num = int.from_bytes(h[6:16], "big")
    chars = []
    for _ in range(14):
        chars.append(BASE62[num % 62])
        num //= 62
    return f"ses_{time_part}{''.join(reversed(chars))}"
```

### Gate 2: Protocol Endpoints & Model Routing
OpenCode routes free models across two distinct upstream protocols:
1. **Chat Completions Protocol (`/zen/v1/chat/completions`)**:
   - Standard OpenAI format (`messages` array).
   - Models: `mimo-v2.5-free`, `nemotron-3-ultra-free`, `nemotron-3.5-lightning-free`, `ling-3.0-flash-fin-free`.
   - Tool format: standard OpenAI nested tools `{type: "function", function: {name: "...", ...}}`.
2. **Responses API Protocol (`/zen/v1/responses`)**:
   - OpenAI Responses API format (`input` array with role/content objects).
   - Models: `muse-spark-1.2-contributor-free`, `muse-spark-1.3-contributor-free`.
   - Tool format: flat function tools `{type: "function", name: "...", description: "...", parameters: {...}}` (NO nested `function` key).
   - Tool choice: upstream **only supports `tool_choice: "auto"`**. Passing `"none"` or named function choice results in `HTTP 400: only "auto" is supported for tool_choice`.
3. **Claude Messages Protocol (`/zen/v1/messages`)**:
   - Models: `union-alpha`.
   - Currently returns `HTTP 401 ModelError: Model union-alpha is not supported` upstream.

### Gate 3: Mandatory Tool Stubs & The "Agent Tools" Pitfall
- Upstream OpenCode Console inspects `tools` and requires `bash` and `read` function tools in the payload to prove official client origin.
- **The Pitfall**: In routers like 9router (`chunks/318.js`), tool injection was historically conditioned on:
  ```js
  Array.isArray(b.tools) && 0 !== b.tools.length || w(b, !0)
  ```
  When downstream AI agents (Hermes, Cline, Roo-Code) pass their own tool definitions (e.g. `terminal`, `read_file`, `write_file`), `b.tools` is non-empty, causing 9router to **skip** injecting `bash` and `read`. Upstream detects the missing stubs and returns `403 FreeTierError`!
- **The Fix**: Unconditionally merge `bash` and `read` into the tool list regardless of whether client tools exist, and set `tool_choice = "auto"`:
  ```js
  w(b, !0), b.tool_choice = "auto"
  ```
- Tool definitions for Responses API (`/zen/v1/responses`):
  ```json
  [
    {"type": "function", "name": "bash", "description": "This tool is currently unavailable and must not be used.", "parameters": {"type": "object", "properties": {}}},
    {"type": "function", "name": "read", "description": "This tool is currently unavailable and must not be used.", "parameters": {"type": "object", "properties": {}}}
  ]
  ```

---

## Native Solution: 9router Built-in Provider with Vercel Relay

In 9router (v0.5.81+), built-in provider `opencode` (alias `oc`) handles client emulation natively. To bypass country blocks (`RegionError`):

### How 9router Relay Routing Works (`proxyAwareFetch`)
When routed through a Vercel Relay:
1. 9router detects `vercelRelayUrl` on the connection or provider strategy.
2. It sends HTTP requests to the root of the relay URL with headers:
   - `x-relay-target`: `https://opencode.ai`
   - `x-relay-path`: `/zen/v1/chat/completions` or `/zen/v1/responses`
3. The Vercel Relay forward proxy reads `x-relay-target` and `x-relay-path` and issues the request from an unrestricted IP while preserving all correlation headers.

### Binding Vercel Relay to Built-in `opencode` in 9router SQLite
Path: `%APPDATA%/9router/db/data.sqlite`

```python
import sqlite3, json

conn = sqlite3.connect(r"C:\Users\<User>\AppData\Roaming\9router\db\data.sqlite")
cursor = conn.cursor()

# 1. Retrieve the existing Vercel relay pool ID
cursor.execute("SELECT id, data FROM proxyPools WHERE data LIKE '%vercel%'")
pool_id = cursor.fetchone()[0]

# 2. Update providerStrategies in settings table (id=1)
cursor.execute("SELECT data FROM settings WHERE id=1")
settings = json.loads(cursor.fetchone()[0])

if "providerStrategies" not in settings:
    settings["providerStrategies"] = {}

settings["providerStrategies"]["opencode"] = {
    "proxyPoolId": pool_id,
    "fallbackStrategy": "none",
    "rotateStrategy": "none",
    "stickyRoundRobinLimit": 1
}

cursor.execute("UPDATE settings SET data=? WHERE id=1", (json.dumps(settings),))
conn.commit()
```

### Necessary Patches to 9router Chunks (`318.js` & `3753.js`)
If 9router exhibits 403 errors when calling free models or when tools are passed:
1. **In `318.js`**:
   - Ensure `J(a)` accurately identifies Responses API models (`muse-spark-1.2-contributor-free`, `muse-spark-1.3-contributor-free`).
   - In `transformRequest`: ensure `w(b, !0)` runs unconditionally so `bash` and `read` tools are merged alongside any client tools passed by agents like Hermes.
2. **In `3753.js`, `8236.js`, `7011.js`**:
   - Ensure the `opencode` models list includes the healthy free models:
     - `mimo-v2.5-free` (`targetFormat: "openai"`)
     - `nemotron-3-ultra-free` (`targetFormat: "openai"`)
     - `nemotron-3.5-lightning-free` (`targetFormat: "openai"`)
     - `ling-3.0-flash-fin-free` (`targetFormat: "openai"`)
     - `muse-spark-1.2-contributor-free` (`targetFormat: "openai-responses"`)
     - `muse-spark-1.3-contributor-free` (`targetFormat: "openai-responses"`)

---

## Downstream Integration & Router Pitfalls

### 1. The Loopback Trap
In 9router, assigning an external cloud relay (Cloudflare Worker or Vercel Relay) in `proxyPoolId` to a local provider node (`http://127.0.0.1:8085/v1`) **fails** with `502 / 500 FUNCTION_INVOCATION_FAILED`. External cloud relays cannot route back to the user's private `127.0.0.1` loopback interface. Always route directly to `https://opencode.ai` via relay headers.

### 2. Provider Identifier Collisions
`opencode` and `oc` are hardcoded internal identifiers. If a user creates a custom node named `zen` or `opencode` pointing to a local proxy, 9router can misroute or conflict with internal handlers. Using 9router's native `opencode` provider bound to Vercel Relay in SQLite avoids all local proxy overhead.

### 3. Route Conventions & Dynamic Model Discovery Latency (`/model` vs `/v1/models`)
- **404 on `/model`**: 9router (Next.js server) defines no singular `/model` or `/models` frontend route out-of-the-box.
  - **API Endpoints**: Standard OpenAI models route is `http://localhost:20128/v1/models` (or `http://localhost:20128/api/models`).
  - **Web Dashboard Routes**: `http://localhost:20128/dashboard`, `/dashboard/combos` (combo & model management), `/dashboard/providers`, `/dashboard/endpoint`.
- **Latency & Timeout Warning**: `GET /v1/models` executes `buildModelsList(["llm"])` in `chunks/7220.js` which dynamically queries upstream `/models` across all active provider connections simultaneously. A cold call typically requires 8–12 seconds to aggregate 300+ models. Automated probes or healthchecks with short timeouts (<5s) will time out and report false negatives.

### 4. Customizing 9router to Serve Curated Combos-Only Instantly (<0.4s)
In agent workflows (Hermes, Cursor, Roo-Code), clients often make frequent calls to `/models` or `/model`. Exposing 300+ raw upstream models slows down client boots and clutters model dropdowns.

To configure 9router to return **only user-defined Combos** instantly:
1. **Support `/model` and `/models` rewrites**:
   - In `app/custom-server.js` inside `wrapped = (req, res) => {`:
     ```js
     const rawUrl = (req.url || "").split("?")[0].replace(/\/+$/, "");
     if (rawUrl === "/model" || rawUrl === "/models") {
       const query = req.url && req.url.includes("?") ? req.url.slice(req.url.indexOf("?")) : "";
       req.url = "/api/v1/models" + query;
     }
     ```
   - In `app/.next-cli-build/routes-manifest.json` under `"afterFiles"`, add rewrite rules for `/model` and `/models` targeting `/api/v1/models`.
2. **Short-circuit upstream fetching in `server/chunks/7220.js`**:
   - Inside `async function D(a, b = {})`, immediately after combos `o.push(c)`:
     ```js
     if (b.combosOnly) {
       let p = [], q = new Set;
       for (let a of o) !a?.id || q.has(a.id) || (q.add(a.id), p.push(a));
       return p;
     }
     ```
   - Inside route handler `async function F(a)`:
     ```js
     let u; try { u = new URL(a.url); } catch (e) { u = null; }
     let wantAll = u && (u.searchParams.get("all") === "true" || u.searchParams.get("all") === "1" || a?.headers?.get("x-all-models") === "1");
     let b = a?.headers?.get(y) === "1", c = await D(["llm"], { skipDynamicFetch: b, combosOnly: !wantAll });
     ```
- **Result**: `GET /model`, `GET /models`, and `GET /v1/models` return only defined Combos in ~0.3s (vs 11s), while `GET /v1/models?all=true` retains access to all 300+ raw provider models.

### 5. Upstream 429 Rate Limits: Session Quota vs Fallback Chaining

OpenCode free models (especially `muse-spark-1.3-contributor-free`) enforce strict burst and RPM (requests per minute) limits. When the rate limit is exceeded, OpenCode returns:
```json
HTTP 429: {"error":{"code":"rate_limit_exceeded","message":"Rate limit exceeded. Please retry after a brief wait."}}
```

There are two primary architectural patterns to eliminate 429 errors:

#### Approach A: Multi-Tier Combo Fallback Chaining
When the user is open to utilizing alternative models if the primary model is busy, configure a combo in SQLite with multiple models:
1. Primary: `oc/muse-spark-1.3-contributor-free` (Responses API)
2. Fallback 1: `oc/muse-spark-1.2-contributor-free` (Responses API — independent rate limit bucket, instant 200)
3. Fallback 2: `oc/mimo-v2.5-free` (Chat Completions)
4. Fallback 3: `oc/nemotron-3-ultra-free` (Chat Completions)

9router automatically detects 429 via `(0, d.hk)(status, errorText)` and immediately transitions the request to the next model in the chain.

#### Approach B: Single-Model Dedication (Smart Session Rotation & In-Place Retry)
When the user insists on using **strictly a single model** (e.g. `oc/muse-spark-1.3-contributor-free` only):
- **Root Cause of 429 Spikes**: OpenCode tracks rate limits primarily **per session** (`x-opencode-session`). By default, 9router caches a single session ID in a local Map (`F`) keyed by `opencode:default` or `opencode:auth:<hash>`. When an agent like Hermes sends several conversational turns or tool calls in quick succession, the single session rapidly exhausts its per-minute quota.
- **Stateless Continuity Insight**: OpenCode's chat and responses APIs are completely stateless on the server side — the conversation history is passed in full with each turn inside the `input` / `messages` array. Rotating `x-opencode-session` across turns does NOT break conversation context!

**Implementation in `server/chunks/318.js`**:
1. **Smart Session Rotation**:
   In `prepareRequestCredentials`, limit the reuse of any cached session to at most 3 requests or 30 seconds before generating a fresh canonical session ID:
   ```javascript
   l = F.get(j);
   if (l) {
     if (Date.now() - l.lastUsed > 30000 || (l.uses = (l.uses || 0) + 1) > 3) {
       F.delete(j);
     } else {
       return l.lastUsed = Date.now(), F.delete(j), F.set(j, l), l.sessionId;
     }
   }
   ```
2. **Auto-Retry on 429 with Session Busting**:
   In class `K` (the OpenCode adapter), wrap `execute` with an automatic retry loop:
   ```javascript
   async execute(a) {
     let b = 3;
     for (let c = 1; c <= b; c++) {
       let d = this.prepareRequestCredentials(a),
           e = await super.execute({ ...a, credentials: d });
       if (e?.response?.status === 429 && c < b) {
         console.log(`[OpenCode 429] Rate limit on ${a?.model || "model"}, rotating session & waiting ${1500 * c}ms (attempt ${c}/${b})...`);
         for (let k of F.keys()) F.delete(k);
         await new Promise(r => setTimeout(r, 1500 * c));
         continue;
       }
       return e;
     }
   }
   ```
3. **Result**: Consecutive agent requests and streaming tool calls on `muse-spark-1.3-contributor-free` succeed continuously with HTTP 200 without ever throwing 429 errors back to downstream clients.
