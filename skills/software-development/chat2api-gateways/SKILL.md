---
name: chat2api-gateways
description: Deploy and consume reverse-engineered Chat-to-API gateways.
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [chat2api, api-gateway, reverse-engineering, chatgpt, deepseek]
    related_skills: [windows-python-project-setup]
---

# Chat-to-API Gateways

## Overview
Chat-to-API gateways reverse-engineer the official web interfaces of AI chatbots (such as ChatGPT, DeepSeek, Claude, and Kimi) to expose standard OpenAI-compatible API endpoints (e.g., `/v1/chat/completions`). This enables free or low-cost access to state-of-the-art models by piggybacking on web sessions, cookie states, or official command-line runners.

## When to Use
- When you need to integrate leading web chat-bots (ChatGPT, DeepSeek, Perplexity, Kimi, Qwen) into custom clients, bots (like Bale or Telegram bots), or developer tools (like Cline/Roo-Code) without paying for official API tokens.
- When you want to utilize free models (like GPT-3.5 or DeepSeek-R1 free tiers) programmatically.

## Don't use for:
- Production-critical environments with strict SLA/uptime requirements (web-interface changes can break reverse-engineered endpoints unexpectedly).
- Processing highly sensitive user data (passing tokens/cookies through unofficial gateway proxies exposes credentials if not hosted securely).

## Prerequisites
- Docker (recommended for deployment) or Python/NodeJS depending on the gateway selected.
- Valid credentials for the target web service:
  - **ChatGPT**: `AccessToken` (extracted from `chatgpt.com/api/auth/session`) or `RefreshToken` (extracted from login flow cookies).
  - **DeepSeek/Kimi/Others**: Session cookies or browser profile directories.

## Popular Gateways
1. **lanqian528/chat2api** (ChatGPT focused)
   - *Best for*: Free/Plus/Team ChatGPT accounts.
   - *Deployment*: Docker `lanqian528/chat2api:latest` or Python.
2. **xiaoY233/Chat2API** (Multi-provider focused)
   - *Best for*: DeepSeek, GLM, Kimi, MiniMax, Qwen, Perplexity, Z.ai.
   - *Interface*: Electron-based GUI or headless CLI/Docker.
3. **Hello-Application-XH/HelloDeepseek** (Cloudflare Workers & DeepSeek focused)
   - *Best for*: Hosting a DeepSeek Web to OpenAI-compatible API gateway directly on Cloudflare Workers (using KV for configuration and automatic PoW challenge solving).
4. **fuergaosi233/claude-code-proxy** (Claude focused)
   - *Best for*: Wrapping the official Claude Code CLI tool as an OpenAI-compatible endpoint.
5. **hmjz100/Z.ai2api** (Z.ai / GLM-4.5 focused)
   - *Best for*: Converting Z.ai web chat to OpenAI-compatible API.
   - *Features*: Anonymous mode (visitor tokens), customizable reasoning/thinking extraction formats (`reasoning`, `think`, `strip`, `details`), and vision image uploads (when logged in).
   - *Deployment*: Local Python setup or Go equivalent (`kbykb/OpenAI-Compatible-API-Proxy-for-Z`) for Render/Docker deployment.

## Procedure

### Step 1: Extract Credentials
To proxy a logged-in account, obtain the session tokens:
- **ChatGPT AccessToken**: Log into chatgpt.com, then open `https://chatgpt.com/api/auth/session` in your browser. Copy the `accessToken` value.
- **ChatGPT RefreshToken**: Look in your browser cookies under the domain `.chatgpt.com` for the secure cookie key `__Secure-next-auth.session-token`.
- **DeepSeek Web Credentials**: Session tokens/accounts can be configured directly in Cloudflare Workers using a KV namespace (e.g., config format: `{"keys":["your-bearer-api-key"],"accounts":[{"email":"your-email@example.com","password":"your-password"}]}`).
- Keep these credentials secure and rotate them periodically (some gateways automate refresh token rotation).

### Step 2: Deploy the Gateway (Local or Cloudflare Workers)
- **Local/Docker (lanqian528/chat2api)**:
```bash
docker run -d \
  --name chat2api \
  -p 5005:5005 \
  -e TZ=Asia/Tehran \
  lanqian528/chat2api:latest
```
- **Cloudflare Workers (Hello-Application-XH/HelloDeepseek)**:
  1. Clone the repository and install dependencies.
  2. Create a KV namespace: `npx wrangler kv namespace create DEEPSEEK_CONFIG` (use `--remote` or add it to `wrangler.jsonc`/`wrangler.toml`).
  3. Set up configuration JSON inside the created KV namespace key `config`:
     ```bash
     npx wrangler kv key put --namespace-id=<your_namespace_id> config '{"keys":["sk-your-bearer-api-key"],"accounts":[{"email":"your-email","password":"your-password"}]}' --remote
     ```
  4. Run `npx wrangler deploy` to push it to Cloudflare.
  
  *Wrangler Proxy Tip*: When executing Wrangler commands in local environments that utilize proxies (e.g. MSYS/Bash), if Wrangler OAuth challenges fail with `403 Forbidden` or HTML error pages from Cloudflare, run the command by clearing the proxy environment variables temporarily: `HTTP_PROXY="" HTTPS_PROXY="" ALL_PROXY="" npx wrangler login`.

### Step 3: Configure Authorization and Rotation
To use your custom tokens, pass them in the header of your API requests to the gateway:
- **Header**: `Authorization: Bearer <your_access_token_or_refresh_token>`
- The gateway acts as a proxy, extracting your token from the `Bearer` header to make requests to the web interface.

### Step 4: Consume in Code
Send requests to the local gateway at `http://localhost:5005/v1` exactly as if it were the official OpenAI API:

```python
import openai

client = openai.OpenAI(
    base_url="http://localhost:5005/v1",
    api_key="your_access_token_here"  # Or your refresh token
)

response = client.chat.completions.create(
    model="gpt-4o",  # Gateways map models based on token type
    messages=[{"role": "user", "content": "Hello!"}],
    stream=True
)

for chunk in response:
    print(chunk.choices[0].delta.content or "", end="")
```

## Pitfalls
- **Python Version Compatibility (3.11 vs 3.12+)**: Many modern gateways (such as `Z.ai2api`) or AI-generated scripts use Python 3.12+ f-string syntax (e.g., nested double-quotes inside f-strings like `f"data: {json.dumps({"id": 1})}"` or backslashes in expression parts). Running these in Python 3.11 or lower environments will raise `SyntaxError: unterminated string literal` or `SyntaxError: f-string expression part cannot include a backslash`.
  - *Fix*: Replace nested f-string JSON serialization with string concatenation: `yield "data: " + json.dumps(...) + "\n\n"`. Avoid backslashes within `{}` braces by using standard concatenation: `"\n\n" + val.lstrip('\n')`.
- **WAF & Slider Captchas (e.g., Z.ai)**: Sites protected by Alibaba/Tencent/Cloudflare WAFs often return `FRONTEND_CAPTCHA_REQUIRED` and launch interactive slider puzzle challenges. Automated headless browser environments will trigger bot protection and fail to render/solve these.
  - *Mitigation*: Look for legacy or backend-specific endpoints (e.g., `/api/chat/completions` instead of Svelte-specific `/api/v2/chat/completions`) which might skip frontend captcha checks, or run the gateway locally while manually extracting verified cookies and tokens from a real browser.
- **Cloudflare & WAF Blocks**: Official web interfaces frequently update their Cloudflare rules. If requests return `403` or `429`, the gateway's IP might be flagged, or the proxy script needs an update.
- **Session Expiration**: Refresh tokens generally expire after 14-30 days if not active or if logged out from the browser.
- **Strict Rate Limits**: Web platforms restrict frequency. Mitigate this by using the gateway's built-in token rotation/pooling features, supplying a list of multiple credentials.

## Verification
1. Send a simple health check or models list request to the gateway:
   ```bash
   curl http://localhost:5005/v1/models -H "Authorization: Bearer <token>"
   ```
2. Confirm the response returns a valid list of supported models in JSON format.

## Support Files
- `references/opencode-zen-free-tier-gate.md` — OpenCode Zen free tier 403 FreeTierError
  reproduction and bypass: session ID shape gate (^ses_[0-9a-f]{12}[0-9A-Za-z]{14}$),
  Responses API vs chat/completions protocol routing, agent tool merging pitfall (Hermes
  custom tools omitting bash/read stubs), 9router Vercel Relay binding in SQLite, fast
  combos-only endpoint routing, and 429 rate limit fallback chaining.
- `references/g4f-noauth-fallback.md` — using the `g4f` Python library directly as a
  no-auth fallback (explicit provider selection, skipping `needs_auth` providers that
  die with `NoValidHarFileError`, requesting `gpt-4o`). Read it before writing any
  `g4f.ChatCompletion.create(...)` call without a gateway.
- `references/9router-318-newbuild-patch.md` — always-inject 318 patch variant for FRESH
  9router installs (different chunk path/guard than the old build), recursion pitfall,
  fresh-image preconditions (logs dir, nvm PATH), better-sqlite3 combo audit, and
  verify-by-real-chat-with-tools rule.
- `references/key-cooldown-cascade.md` — recurring-outage pattern when rotating API
  keys with uniform cooldown-on-error (one transient 503 sleeps every key → "no
  active key" cascade); status-code-differentiated cooldowns + retry queue fix.
- `references/9router-dashboard-password.md` — 9router dashboard auth internals:
  bcrypt hash in `settings.data.password`, `123456` default when unset,
  reset-password CLEARS (doesn't set), no CLI setter, live-db discovery via
  /proc env+cwd, and the secret round-trip check (truncated writes mimic bad credentials).
