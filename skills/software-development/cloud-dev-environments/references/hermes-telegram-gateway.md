# Hermes Agent Messaging Gateway → Telegram (verified runbook)

End-to-end verified: `hermes gateway run` + Telegram long-polling on a headless
Linux sandbox, DM isolation per user, `hermes chat -q` through a local OpenAI relay.

## Official wiring (from Hermes docs)

- Create the bot with @BotFather → token looks like `123456789:ABCdef...`.
- Manual config: append to the profile's `.env` (NOT config.yaml — secrets live in `.env`):

  ```
  TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrSTUvwxYZ
  TELEGRAM_ALLOWED_USERS=123456789   # comma-separated numeric IDs for multi-user
  ```

- Start: `hermes gateway run` (foreground; use `nohup ... &` + log file on hosts
  without systemd). Expect `[Telegram] Connected to Telegram (polling mode)` in the log.
- Get a numeric user ID from @userinfobot (send it anything, it replies with the ID).

## Pairing Approval Flow
When `TELEGRAM_ALLOWED_USERS` is not pre-set in `.env`, Hermes defaults to secure Pairing mode.
- A new user sending a message receives:
  `Hi! I don't recognize you yet... Your pairing code: <CODE> (valid for 1 hour). If you run this bot, open a terminal and run: hermes pairing approve telegram <CODE>`
- Approve via CLI:
  ```bash
  hermes pairing approve telegram <CODE>
  ```
- **$HOME / Multi-User Root Pitfall**:
  `hermes pairing approve` checks `$HOME/.hermes/platforms/pairing`. If the gateway runs under `/home/user` while commands execute as `root` (`HOME=/root`), running `hermes pairing approve` writes to `/root/.hermes` instead, reporting `No pairing data found` and leaving the active gateway unapproved. Always ensure `HOME=/home/<target_user>` or pass explicit `-p <profile>`.
- **Headless Live Approval (Zero Restart)**:
  `PairingStore.is_approved()` dynamically re-reads `{HERMES_HOME}/platforms/pairing/{platform}-approved.json` on every inbound message. You can approve a user immediately without stopping or restarting the running gateway process:
  ```python
  import json, time
  path = '/home/user/.hermes/platforms/pairing/telegram-approved.json'
  with open(path, 'w') as f:
      json.dump({str(user_id): {"user_name": "User", "approved_at": time.time()}}, f, indent=2)
  ```
- To make access permanent without re-pairing on fresh deployments:
  ```bash
  echo "TELEGRAM_ALLOWED_USERS=<user_id>" >> ~/.hermes/.env
  ```

## DM session isolation is the default

- `group_sessions_per_user: True` in the gateway config — each Telegram user's DM
  gets its own session automatically. Two allowed users chatting with the same bot
  do NOT see each other's history. No extra config needed for "separate memory per person"
  at the conversation level.

## Caveat: shared long-term memory file vs. Two-Bot Complete Isolation

- Conversation history is per-user, but the long-term memory file (`MEMORY.md`)
  is shared across users on one profile.
- **Two-User Complete Isolation ("ایزوله کامل با دو بات")**:
  When two users require 100% separate long-term memories and private tool contexts:
  1. Create two separate bots via @BotFather (e.g. `@bot_user1` and `@bot_user2`).
  2. Map them to isolated Hermes profiles:
     - Profile 1 (default): `~/.hermes/.env`
       ```env
       TELEGRAM_BOT_TOKEN=<token_1>
       TELEGRAM_ALLOWED_USERS=<user_1_id>
       ```
     - Profile 2 (`user2`): `~/.hermes/profiles/user2/.env`
       ```env
       TELEGRAM_BOT_TOKEN=<token_2>
       TELEGRAM_ALLOWED_USERS=<user_2_id>
       ```
  3. Start either via multiplexed gateway (`hermes gateway run` under default profile)
     or start two independent gateway processes specifying the `--profile` flag:
     `nohup hermes --profile user2 gateway run > /var/log/hermes-user2.log 2>&1 &`.
  4. Each profile maintains its own `MEMORY.md`, `USER.md`, `state.db`, and skills.

## Configuring 9router Combos & In-Chat `/model` Switching on Telegram

When connecting Hermes Telegram Gateway to a 9router or proxy instance hosting custom combos (e.g., `Antigravity`, `claude`, `zen`, `NVIDIA`, etc.):

1. **Avoid the 1000+ Raw Model Flood (`discover_models: false`)**:
   By default, Hermes probes `/v1/models`. In 9router, that endpoint returns every raw model from all connected providers (often 1,000+ items), making the Telegram inline picker completely unusable on mobile.
   Fix: Set `discover_models: false` under `providers.<slug>` and explicitly list the combos in `models:`.
2. **Provider Slug Collision Pitfall**:
   Naming the custom provider `router` in `config.yaml` (`providers.router`) causes Hermes to match it against its built-in `ramp_router` (`AuthError: No usable credentials found for provider 'router'. Set RAMP_ROUTER_API_KEY`). Use a unique slug like `9router` (`providers.9router`).
3. **Collision with Built-in Aliases on Direct `/model <name>`**:
   If a combo shares a name with a built-in provider (e.g. `claude`), typing `/model claude` in chat causes Hermes to look for Anthropic credentials and fail.
   Fix: Define direct mappings in `model_aliases:` in `config.yaml`:
   ```yaml
   model_aliases:
     claude:
       model: claude
       provider: 9router
       base_url: http://127.0.0.1:20128/v1
     zen:
       model: zen
       provider: 9router
       base_url: http://127.0.0.1:20128/v1
   ```
4. **Known-Good Config Block for 9router Combos**:
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

   custom_providers:
     - name: 9router
       base_url: http://127.0.0.1:20128/v1
       api_key: ${OPENAI_API_KEY}
       discover_models: false
       models:
         - Antigravity
         - claude
         - NVIDIA
         - Cloudflare
         - gem
         - Cline
         - b.ai
         - newModels
         - orcarouter
         - zen
         - atria

   model:
     default: Antigravity
     provider: 9router
     base_url: http://127.0.0.1:20128/v1
     api_key: ${OPENAI_API_KEY}
   ```
5. **Live Reloading on `/model`**:
   The gateway re-reads `config.yaml` on every `/model` invocation (`ctx.read_config()`). Adding or modifying combos in `config.yaml` is reflected immediately in active Telegram chats without restarting the gateway process.
6. **Picker reads ONLY `custom_providers:` — the #1 'combo missing in Telegram' cause (verified from source, Sep 2026)**:
   `/model` in a Telegram chat → `gateway/slash_commands_model.py` → `list_picker_providers(max_models=50)` → `list_authenticated_providers` Section 4 (`_lap_custom_provider_rows` in `hermes_cli/model_switch_providers.py`), which folds ONLY `custom_providers:` list entries into the picker row. The `providers.9router.models:` dict block is NOT read by the picker at all. Consequences:
   - A combo present in 9router SQLite + `providers.9router.models` but absent from the `custom_providers:` list NEVER appears in `/model`.
   - `discover_models: false` disables the live `/v1/models` probe, so the picker shows EXACTLY the config list — no more, no less.
   - `model_aliases:` entries only affect direct `/model <name>` typing, not the picker buttons.
   - Keep all three in sync on every combo add: `providers.9router.models` dict (`Name: {}`), `custom_providers` list (`- Name`), and a lowercase alias. The `sync_models.sh` pattern does this mechanically: read combo names from SQLite (`SELECT name FROM combos`), rewrite both sections + aliases, run as a pre-backup hook so `/model` stays fresh with no restart.
   - Deterministic pre-check without touching Telegram: run the picker's exact code path against the config — see `scripts/model_picker_probe.py`. If the combo isn't in its `ROW:` output, it won't be in `/model` either.
7. **Hung agent turn blocks the whole DM queue — kill the zombie, don't restart blindly (verified live, Sep 2026)**:
   Symptom: `inbound message` logged, then nothing — no turn start, no error, no reply; later ticks warn `N update(s) queued but not consumed (stuck probe)`. Cause: a `hermes_kernel_runner.py` child stuck (e.g. waiting on a pipe / external tool with no timeout) holds the session's turn slot, so every later message queues behind it forever.
   Diagnosis: `ps aux | grep hermes` → a `hermes_kernel_runner.py` with ELAPSED of tens of minutes and no child processes; `/proc/<pid>/stack` shows `pipe_wait`, `/proc/<pid>/wchan` = `pipe_wait`. Meanwhile `getUpdates` returns empty — the messages are stuck in the gateway, not on Telegram's servers.
   Fix: `kill -9 <runner-pid>` (it may linger as `[python] <defunct>` until the gateway parent reaps it — that's fine). The gateway then completes/fails the stuck turn and drains the queue; verify with `response ready` + `Sending response` lines in `gateway.log`. Only restart the gateway itself if polling is also broken (`Fatal telegram adapter error ... rebuilding` loops with no `polling confirmed healthy`).

## Secret round-trip check (bit us on TELEGRAM_BOT_TOKEN)

- A token written through layered exec (chat → bridge script → remote shell → `.env`)
  can lose characters in transit (we lost the `:` → 20-char stub). Telegram then
  answers `{"ok":false,"error_code":404,"description":"Not Found"}` on `getMe`,
  which looks like a bad token but is really a truncated write.
- Always: read the written value back, assert length + `:` count + full-match
  against the source BEFORE diagnosing the credential itself.
- Validate independently of the gateway: `GET https://api.telegram.org/bot<TOKEN>/getMe`
  must return `{"ok":true,...}` — do this first, then start the gateway.
