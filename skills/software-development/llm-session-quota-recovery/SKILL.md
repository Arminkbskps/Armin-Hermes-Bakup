---
name: llm-session-quota-recovery
description: "Triage 429 quota exhaustion and context bloat cascades."
version: 1.2.0
---

# LLM Session Quota & Context Bloat Recovery

Use when an agent or downstream messaging bot (Telegram, Discord, Slack) repeatedly reports `429 Resource has been exhausted`, `Rate limit exceeded`, or burns massive token budgets (e.g., 100k-250k+ tokens on a simple greeting), or when multi-account proxy routers experience cascading pool failures.

## 1. The Context Bloat & Cascade Mechanism

Downstream chat gateways retain conversation history across turns. When a session accumulates dozens of messages and verbose tool outputs without being reset, or when hundreds of skills inflate the system prompt:
1. **Per-Turn Payload Explosion**: Every user message (even a single word like "hi") transmits the entire context (`system_prompt` + all uncompacted `messages` + tool logs). A 150k-250k token context is sent on *every turn*.
2. **Burst Limit Trigger**: Provider free or developer tiers (such as Gemini Code Assist / Antigravity) enforce tight Tokens-Per-Minute (TPM) or sliding-window burst limits. A single 200k+ token payload instantly triggers HTTP 429 `RESOURCE_EXHAUSTED`.
3. **Router Cascade Storm**: If the client connects through a proxy router (9router, LiteLLM) with a Round-Robin fallback strategy across multiple provider accounts, the router immediately retries the bloated payload against account 2, account 3, etc. A single user message burns through the quota of every account in the pool within seconds.

## 2. Diagnostic Procedure

### Step 1: Inspect Session Size and System Prompt
On the agent host, inspect the active session in SQLite (`~/.hermes/state.db`):

```bash
python3 - << 'EOF'
import sqlite3, os, datetime

conn = sqlite3.connect(os.path.expanduser("~/.hermes/state.db"))
c = conn.cursor()

# Check active session token usage
print("=== RECENT SESSIONS ===")
for r in c.execute("SELECT id, source, message_count, input_tokens, last_activity_at FROM sessions ORDER BY last_activity_at DESC LIMIT 3").fetchall():
    t = datetime.datetime.fromtimestamp(r[4]).strftime("%Y-%m-%d %H:%M:%S") if r[4] else "N/A"
    print(f"[{r[1]}] {r[0]} | msgs: {r[2]} | tokens: {r[3]} | last: {t}")

# Check active message character count
row = c.execute("SELECT id FROM sessions ORDER BY last_activity_at DESC LIMIT 1").fetchone()
if row:
    sid = row[0]
    total_chars = c.execute("SELECT SUM(length(content)) FROM messages WHERE session_id=? AND active=1", (sid,)).fetchone()[0] or 0
    msg_count = c.execute("SELECT COUNT(*) FROM messages WHERE session_id=? AND active=1", (sid,)).fetchone()[0] or 0
    print(f"\nActive Session ({sid}): {msg_count} messages, {total_chars:,} chars in history")

# Check system prompt size
h = c.execute("SELECT system_prompt_hash FROM sessions WHERE id=?", (sid,)).fetchone()[0]
if h:
    prompt_len = c.execute("SELECT length(prompt) FROM system_prompts WHERE hash=?", (h,)).fetchone()[0] or 0
    print(f"System prompt length: {prompt_len:,} chars")
EOF
```

If `messages` + `system_prompt` exceed 100,000 characters, context bloat is the primary driver of 429 errors.

### Step 2: Probe Individual Provider Accounts Directly
Do not rely on passive health checks like `v1internal:loadCodeAssist`, which return HTTP 200 even when generation is blocked or exhausted. Test the actual generation endpoint directly with a minimal payload:

```bash
# Direct generation probe (Antigravity example)
curl -s -X POST https://cloudcode-pa.googleapis.com/v1internal:generateContent \
  -H "Authorization: Bearer <ACCESS_TOKEN>" \
  -H "Content-Type: application/json" \
  -H "User-Agent: antigravity/ide/2.22.0 darwin/arm64" \
  -d '{"project": "aicode-consumers", "model": "gemini-2.5-flash", "request": {"contents": [{"role": "user", "parts": [{"text": "ping"}]}]}}'
```

- **HTTP 200**: Account is healthy and has remaining quota.
- **HTTP 429**: Quota exhausted on Google's sliding window. Inspect exact reset time:
  ```bash
  curl -s -X POST https://cloudcode-pa.googleapis.com/v1internal:retrieveUserQuota \
    -H "Authorization: Bearer <ACCESS_TOKEN>" \
    -H "Content-Type: application/json" \
    -H "User-Agent: antigravity/ide/2.22.0 darwin/arm64" \
    -H "X-Client-Name: antigravity" \
    -H "X-Client-Version: 2.22.0" \
    -d '{}'
  ```
  Look for `buckets[].resetTime` (ISO 8601 UTC) and `remainingFraction`.
- **HTTP 403 `VALIDATION_REQUIRED`**: Google flagged the OAuth grant for interactive verification. See Section 4.

## 3. Remediation Steps

1. **Immediate Context Purge**:
   Instruct the user to send `/new` or `/reset` in the messaging channel (Telegram, Discord). This immediately archives the bloated session and starts turn count from zero.
   *Pitfall*: If sent during an in-flight error loop or gateway restart storm, verify that `gateway_routing` in `~/.hermes/state.db` or `gateway.log` actually recorded the session reset.
2. **Prune Skill Overhead**:
   If `system_prompt` exceeds 50k characters, check `ls ~/.hermes/skills/`. Bulk installations of specialized skills (e.g. medical, radiology, bio) inject thousands of lines of schema into the system prompt. Remove unneeded skills to drop base prompt tokens by 80%.
3. **Configure Conservative Compression**:
   When using custom router models (e.g. `9router`), Hermes cannot infer the model's native context window and defaults to `compression.threshold_tokens: null`. Explicitly configure conservative thresholds in `~/.hermes/config.yaml`:
   ```bash
   hermes config set model.context_length 64000
   hermes config set compression.threshold_tokens 28000
   hermes config set compression.protect_last_n 8
   hermes config set compression.proactive_prune_tokens 10000
   ```
   This prevents context from exceeding free/developer tier burst limits even during long uninterrupted sessions.
4. **Isolate Degraded Router Connections**:
   In `~/.9router/db/data.sqlite`, temporarily mark exhausted (429) or checkpointed (403) connections as inactive:
   ```sql
   UPDATE providerConnections SET isActive = 0 WHERE id = '<degraded_connection_id>';
   ```
   This prevents the router from wasting round-robin retries and triggering cooldowns on healthy connections.

## 4. Google OAuth Checkpoint Recovery (`VALIDATION_REQUIRED`)

When Google's anti-bot engine flags an Antigravity/Cloud Code OAuth grant, it returns HTTP 403 with `VALIDATION_REQUIRED`:
- **Pitfall: Normal Gmail Login Does Not Work**: Logging into Gmail or Google Account normally does NOT clear the checkpoint. The block is tied specifically to the Gemini Code Assist application grant.
- **Extract Link**: Retrieve the tokenized `validation_url` directly from `error.details[].metadata.validation_url`.
- **Multi-Account Browser Hijack Pitfall**: The URL contains a bare `&authuser` parameter without an account index. If opened in a browser where another Google account is default, Google evaluates the verification against the wrong account, redirects to `auth_success_gemini`, and reports success while leaving the target account locked in 403.
- **Enforce Incognito Isolation**: The user must open an Incognito / private browsing window, log in explicitly with the targeted Google account first, and then paste the validation link (or append `&authuser=<email>`).
- **Ephemeral Token**: The `plt=...` token inside the link expires in minutes. Run the API probe immediately before giving the URL to the user.
- **Relay Pool Binding for Datacenter IPs**: Adding fresh Google accounts to 9router directly from a cloud/datacenter IP (AWS/Daytona) triggers immediate `VALIDATION_REQUIRED` on the very first generation call. Bind fresh connections to an established relay pool (`proxyPoolId` e.g. Vercel relay or Cloudflare worker) before making requests.
