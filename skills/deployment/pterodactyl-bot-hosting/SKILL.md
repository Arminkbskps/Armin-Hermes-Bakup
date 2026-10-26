---
name: pterodactyl-bot-hosting
description: "Use when managing bots on Pterodactyl or HidenCloud."
version: 1.3.0
author: Armin & Hermes
license: MIT
metadata:
  hermes:
    tags: [pterodactyl, hidencloud, sftp, python-bots, deployment, hosting]
---

# Pterodactyl Bot Hosting & Automation

Procedure for managing, automating, and editing Python/Node bots hosted on Pterodactyl-based cloud panels (such as HidenCloud, Shockbyte, PebbleHost, and custom Wings nodes).

## 1. Subuser Onboarding & Credentials Setup
- **Subuser Invitation**: When user invites an agent email (e.g. `armin-hermes@agentmail.to`), Pterodactyl sends an "Account Created" email with a password setup link.
- **Password & Security Rules**:
  - Never type or accept passwords in plaintext chat or browser automation forms.
  - User sets the initial password via the reset URL in their own browser.
  - The panel assigns a subuser username (e.g. `armin-hermesgqz`).

## 2. SFTP Connection Architecture
Pterodactyl isolates server storage behind an internal Wings SFTP daemon (typically port 2022, not port 22 or 443).
- **Target Host & Port**: Available in **Server Settings -> SFTP Details** (e.g., `jacob.hidencloud.com:2022`).
- **Composite Username**: The SFTP username is ALWAYS formatted as `<panel_username>.<server_identifier>` (e.g. `h82uygjo3q-155393.8bf3ab98` or `armin-hermesgqz.8bf3ab98`). Using the bare account username alone will fail authentication.

## 3. Connecting From Restricted CDEs (HTTP CONNECT Tunneling)
In cloud development environments (Daytona, Codespaces, LXC containers), outbound TCP traffic to non-standard ports (like 2022) is often blocked by host firewall rules, resulting in connection timeouts.
- **Bridge Solution via Local Proxy**:
  Route OpenSSH and SFTP through the local HTTP proxy bridge (e.g., `127.0.0.1:8888`) using OpenSSH's `ProxyCommand`:
  ```bash
  sftp -o "ProxyCommand=/home/daytona/.ssh/http_proxy.py %h %p" -P 2022 <username>@<host>
  ```
  Where `http_proxy.py` issues a raw `CONNECT <host>:<port> HTTP/1.1` to the local proxy and bridges stdin/stdout to the socket.

## 4. Non-Interactive Script Automation (No sshpass)
When `sshpass` is not installed, automate SFTP commands, downloads, and uploads in scripts using OpenSSH's native askpass mechanism:
```bash
# 1. Prepare password file with strict permissions
echo -n "PASSWORD" > ~/.ssh/sftp_pass.txt
chmod 600 ~/.ssh/sftp_pass.txt

# 2. Command wrapper (e.g., hiden-sftp)
echo "ls -la" | SSH_ASKPASS_REQUIRE=force SSH_ASKPASS=/home/daytona/.ssh/askpass.sh \
  setsid sftp -o "ProxyCommand=/home/daytona/.ssh/http_proxy.py %h %p" \
  -o "StrictHostKeyChecking=no" -P <port> <user>@<host>
```
- **Downloading (`get`)**: `echo "get \"$REMOTE_FILE\" \"$LOCAL_PATH\"" | ...`
- **Uploading (`put`)**: `echo "put \"$LOCAL_FILE\" \"$REMOTE_PATH\"" | ...`

## 5. Multi-Bot Scoping & Directory Isolation
When a single Pterodactyl container runs multiple bot instances simultaneously (e.g., via `main.py` using `multiprocessing.Process` or background runners):
- **Relative Path Collision Pitfall**: Process runners typically execute with working directory set to root `/home/container`. Any hardcoded or relative paths (`bot_database.db`, `games_state.json`, `exports/`, `backups/`) will collide across bots, causing SQLite database locks or overwriting state.
- **Strict Prefix Scoping**: Every cloned or parallel bot must explicitly scope its files and SQLite paths to its own directory:
  - `DB_PATH = "Bot 2/bot_database.db"` (instead of `"Bot/..."` or bare `"bot_database.db"`)
  - `"Bot 2/games_state.json"`, `"Bot 2/downloads"`, `"Bot 2/exports"`, `"Bot 2/backups"`
- **Log Isolation**: Point logger file handlers to distinct files (e.g., `bot.log` for Bot 1, `bot 2.log` for Bot 2) and give each logger a unique name (`TelegramSuperBot` vs `BaleSuperBot`).
- **Debugging Non-Running Parallel Bots**: When one bot runs but another (e.g. `Bot 4`) silently fails, inspect its dedicated log directory (e.g. `Bot 4/logs/bot4.log`) or root supervisor logs. Common causes:
  - Model deprecation (e.g. Google returning 404 for deprecated models like `gemini-3.5-flash-lite`, requiring update to `gemini-flash-lite-latest` or `gemini-3.8-flash`).
  - Stale/suspended API keys in SQLite tables: check `cooldown_until` and error columns — failed calls can leave keys on a persistent cooldown or disabled state even after code fixes, unless `cooldown_until = NULL` and `enabled = 1` are reset.
- **Selective Bot Shutdown in Multi-Process Containers**:
  When shutting down specific bots (e.g. Bot 3 or Bot 4) while keeping others active:
  1. Never rely on killing PIDs alone; Pterodactyl server restarts or supervisor loops will respawn them.
  2. In the launcher (`main.py`), remove or comment out their `Process(target=run_bot, ...)` instantiation and `process.join()` calls.
  3. In each disabled bot's script (e.g. `Bot 3/bot3.py`), place an immediate exit guard at `if __name__ == "__main__": sys.exit(0)`. This guarantees no alternative launcher (`main_35.py` or console command) can execute them.

## 6. SQLite WAL & SHM Clean Replacement Pitfall
When replacing or uploading an updated SQLite `.db` file over SFTP into an active bot directory:
- **Header Mismatch Crash**: If the previous run operated in WAL mode (`PRAGMA journal_mode=WAL`), the old `.db-wal` and `.db-shm` files remain on disk. Starting a newly uploaded `.db` while old WAL files exist causes SQLite page header mismatches, crash loops, or silent rollbacks.
- **Rule**: Whenever uploading an updated database, rename or remove the existing `-wal` and `-shm` siblings:
  ```bash
  hiden-sftp "rename \"Bot 2/bot_database.db-wal\" \"Bot 2/bot_database.db-wal.bak\""
  hiden-sftp "rename \"Bot 2/bot_database.db-shm\" \"Bot 2/bot_database.db-shm.bak\""
  ```
- **Prefer Code-Level Migrations Over Binary DB Replacement**: Downloading active SQLite WAL files while bots write produces torn copies (`database disk image is malformed`). When updating database schemas, tables, or seeds, add migration code directly to the Python bot's `__init__` rather than overwriting live `.db` files over SFTP.

## 7. Automatic Backup Directory Bloat & Container Hygiene
- Bots with startup auto-backup create timestamped files (`backup_YYYYMMDD_HHMMSS.db`) inside `Bot/backups/` and `Bot 2/backups/` on every container reboot.
- Over dozens of restart cycles, this fills the disk (especially on 10GB/5GB free VPS containers).
- **Cleanup Procedure & Junk Inventory**: Regularly purge the following accumulated files using non-interactive SFTP commands:
  - Corrupted/old SQLite fallback WAL and SHM files: `*.corrupt_bak`, `*.db-wal.corrupt_bak`, `*.db-shm.corrupt_bak` (can easily reach 4-10MB+ each).
  - Outdated source code backups: `*.py.bak`, `*.bak`.
  - Obsolete launcher/manager scripts: `index.js`, `bot_mn.py`, `main_35.py`, `start_bot_manager.sh`, `startup.js`.
  - Ad-hoc verification scripts from past debugging runs: `check_*.py`, `test_*.py`.
  - Sub-bot demo databases/logs: `*_demo.sqlite3`, `*_demo.log`.
  - Accidental typo directories (e.g. `fonts;` created by mistyped shell commands).
  - Routine purge: `*/backups/backup_*.db`, `archive-*.tar.gz`, `*.db-shm.bak`, and `*.db-wal.bak`.

## 8. Long-Polling Timeout vs HTTP Socket Timeout
- In Telegram/Bale long-polling, `getUpdates` passes a `timeout` parameter (e.g. `{"timeout": 25}`) instructing the Telegram server to hold the connection open for up to 25s if no updates exist.
- If the HTTP request client's socket timeout is equal to or less than the polling timeout (`requests.post(..., timeout=25)`), `requests` will throw `HTTPSConnectionPool: Read timed out` on every quiet poll interval, flooding `bot.log` with thousands of false timeouts.
- **Rule**: Always enforce `request_timeout = max(request_timeout, poll_timeout + 15)` in the low-level API client for `getUpdates`.

## 9. Porting Bots Between Platforms (Bale <-> Telegram)
Bale's Bot API is modeled closely on Telegram's Bot API, making code sharing straightforward, but requires precise conversions:
- **API Endpoints**:
  - Base URL: `https://tapi.bale.ai/bot{TOKEN}` <-> `https://api.telegram.org/bot{TOKEN}`
  - File Download URL: `https://tapi.bale.ai/file/bot{TOKEN}/{path}` <-> `https://api.telegram.org/file/bot{TOKEN}/{path}`
- **Deep Links & Web Addresses**:
  - Channels: `https://ble.ir/join/{uname}` -> `https://t.me/joinchat/{uname}` (or `https://t.me/{uname}`)
  - Channel posts: `https://ble.ir/c/{clean_id}` -> `https://t.me/c/{clean_id}`
  - Bot start / panel: `https://ble.ir/{bot}?start=...` -> `https://t.me/{bot}?start=...`
  - Group addition: `https://ble.ir/{bot}?startgroup=true` -> `https://t.me/{bot}?startgroup=true`
  - AI referer headers: `https://bale.ai` -> `https://t.me`
- **Persian Text Replacement Pitfall (The "بله" False-Positive Trap)**:
  - NEVER run a blind regex or global search-and-replace for the Persian word `بله`!
  - In Persian, `بله` means **"Yes"** (e.g. `{'✅ بله' if sanc else '❌ خیر'}` or `is_muted = f"بله (تا {time})"`). Blind replacement corrupts Boolean status messages and prompt outputs into nonsense like `{'✅ تلگرام' if sanc else '❌ خیر'}`.
  - Target ONLY platform-specific collocations:
    - `"پیام‌رسان بله"` / `"پیام رسان بله"` -> `"پیام‌رسان تلگرام"`
    - `"ربات هوشمند بله"` -> `"ربات هوشمند تلگرام"`
    - `"در بله"` -> `"در تلگرام"`
    - `"API بله"` -> `"API تلگرام"`
    - `"کانال تلگرامی/بله"` -> `"کانال تلگرام"`

## 10. Monkey-Patching Overrides Later in File Pitfall
- In monolithic legacy bot files (8,000 - 15,000 lines), early class definitions (e.g. `class WebSearcher: ...`) are often silently overridden thousands of lines later by monkey-patches like `WebSearcher.search = staticmethod(_web_search_final)`.
- Always search the entire codebase for reassignments to class methods (`<ClassName>.<method> = `) before assuming an early definition is the active execution path.

## 11. Pterodactyl Client API
For operations outside the filesystem (viewing live console, starting/stopping, power actions, or triggering server re-installation):
- Instruct user to generate an **Account API Key** (`Account Settings -> API Credentials`).
- Client API keys begin with `ptlc_`.
- Base endpoint: `https://<panel-domain>/api/client`.
- Header: `Authorization: Bearer ptlc_...`, `Accept: Application/vnd.pterodactyl.v1+json`.

## 12. Full Bot Server Backup via Non-Interactive SFTP Batch
To take a complete backup of all bots, scripts, databases, and configuration on a Pterodactyl/HidenCloud server:
- **Skip Bloated Runtime Directories**: Never mirror `.local/`, `.cache/`, or `.g4f/` (Python site-packages and package caches consume hundreds of megabytes).
- **Batch Command Piping**: Feed batch commands to OpenSSH SFTP via stdin using `subprocess.Popen`:
  ```python
  commands = [
      f"lcd {STAGING_DIR}",
      "get bot_mn.py", "get main.py", "get index.js", "get startup.js", "get requirements.txt",
      'get -r "Bot"', 'get -r "Bot 2"', 'get -r "Bot 3"', 'get -r "Bot 4"', 'get -r "Bot 5"', 'get -r "bots"'
  ]
  # Pipe into sftp with ProxyCommand and askpass
  ```
- **Compress & Offload**: Compress with `tar --use-compress-program="gzip -9" -cf archive.tar.gz -C staging .` and push to Google Drive using the Web App Bridge. If archive exceeds 20 MB, chunk into sequential parts (`.part1`, `.part2`) to guarantee successful delivery without hitting Web App payload ceilings.

## 13. Custom AI Provider 9Router Architecture (Multi-Key Pool & Failover)
When adding custom or reverse-engineered OpenAI-compatible API providers (e.g. external gateways, vLLM, Ollama, 9router) to multi-bot architectures:

### 1. User Preference: 100% Inline Glass Panel Workflow (No Slash Commands)
- For this user's bots, **NEVER force slash commands** (`/providers`, `/add_provider`, `/set_provider`, etc.) or delimiter strings. Every configuration and management flow must be driven via the **Inline Glass Panel** (`پنل شیشه‌ای`).
- Terminal CLI commands (`/test_provider`, `/providers`, etc.) may exist purely as a secondary shortcut for developers, but the primary user flow must be 100% clickable glass buttons.

### 2. Step-by-Step Inline Wizard (مرحله‌به‌مرحله) over Asterisk Delimiter Strings
- Do not force users to format complex single-line strings with asterisks (`name*url*key*model`) which are error-prone due to spaces or punctuation.
- Implement a conversational 4-step wizard that morphs the panel message in place (`edit_message_text`) and deletes the user's input messages (`delete_message(chat_id, msg_id)`):
  - **Step 1**: Provider Name (`p_name`)
  - **Step 2**: Base URL (auto-trim trailing slashes/spaces and ensure `https://`)
  - **Step 3**: API Key(s) (supports single key or comma-separated keys for pool)
  - **Step 4**: Model Name
  - **Completion**: Registers the provider and all keys, and displays a dedicated glass management card with instant buttons for `[🟢 فعال‌سازی]`, `[🧪 تست اتصال و پینگ]`, `[➕ افزودن کلید به استخر]`, `[🧠 تغییر مدل]`, and `[« بازگشت]`.
- **`target_msg_id` Scope Pitfall in State Machines**: At the root of `if u_state:`, always assign `target_msg_id = u_state.get("msg_id")` before checking specific step types. Omitting this causes `NameError: name 'target_msg_id' is not defined` when updating panel messages, generating fatal `MES-` error cards.

### 3. Strict Provider Isolation: NO "لایه دوم" (Zero Silent Fallbacks)
- When a user selects a provider or model (whether custom or built-in), **DO NOT silently fall back to secondary providers** (e.g. OpenRouter or Google) or secondary backup models (`default_fallbacks` like `dolphin-3.0-r1-mistral-24b:free` or `gemini-2.5-flash-free`).
- **The `else: provider = "openrouter"` Trap**: In legacy dispatchers, any provider not in a hardcoded tuple (`"google"`, `"openai"`, etc.) often falls into `else:` where `provider` is forcibly reassigned to `"openrouter"`, completely bypassing the custom provider runner. Always check `custom_ai_providers` FIRST and return immediately.
- If the selected provider or model fails, return the error of THAT EXACT provider and model directly. Never call other providers behind the user's back ("لایه دوم ارسال نمی‌خواد").

### 4. Duplicate Legacy Implementations in Monolithic Files
- Monolithic bot files (8,000-15,000 lines) often contain duplicate implementations of AI callers (e.g. `DynamicAIClient.ask_ai_stream` at line 1150 and `_ask_ai_stream_multi_key` at line 13200). If the early definition is not stripped or routed to the unified implementation, early callers will bypass newer patches and hit legacy fallbacks. Replace early duplicate bodies with direct forwarders to the unified multi-key runner.

### 5. Multi-Key Pool & Round-Robin Load Balancing
- Store keys in a dedicated table (`custom_ai_keys(provider_name, api_key, enabled, cooldown_until, usage_count, last_error)`).
- Support multiple comma-separated keys (`sk-1,sk-2`) and auto-clean trailing spaces on URLs (`.strip().rstrip('/')`).
- Implement round-robin rotation across active keys and **automatic failover**: when a key hits `429` (rate limit) or `401/403` (auth error), mark a short cooldown (60s for 429) and immediately rotate to the next key in the pool without failing the user request.
- Automatically fall back to non-streaming (`stream: False`) if SSE streaming fails or is buffered by gateways.

### 6. Python `sqlite3.Row` Has No `.get()` Method
- Calling `row.get("field")` on a `sqlite3.Row` object returned by `cursor.fetchone()` raises `AttributeError: 'sqlite3.Row' object has no attribute 'get'`.
- Always convert to `dict(row).get(...)` or access directly by key `row["field"]`.

### 7. Top-Level Standard Library Imports in Monolithic Codebases
- Standard library imports (such as `import contextlib`) placed deep in the file (e.g. line 13500) will throw `NameError` if invoked by functions or monkey patches earlier in execution order. Ensure all required imports exist at lines 1-30.
