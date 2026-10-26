---
name: cloud-dev-environments
description: "Workflows for Daytona, Codespaces, and LXC VPS."
category: software-development
---

# Cloud Dev Environments & Minimal VPS

Use this skill when the user is operating inside a Cloud Development Environment (CDE) like Daytona, GitHub Codespaces, or a minimal container-based VPS (LXC/OpenVZ).

## Daytona Storage & Cron Maintenance (10GB Host SSD)
- **Strict 10GB Disk Ceiling**: Daytona workspaces operate under a hard 10GB overlay filesystem. Bulky global installs or unpruned media will exhaust disk space rapidly and halt runtime services.
- **Backup Archive Compression Rules**: Automated Google Drive backup archives (`hermes_backup.py`) MUST exclude bulky media files (`--exclude=*.mp3`, `--exclude=*.mp4`, `--exclude=*.gif`, `--exclude=*.wav`). Google Apps Script upload endpoints enforce a strict 30MB payload ceiling; uncompressed media in skill assets causes uploads to abort with `TOO BIG for single upload`.
- **Automated GitHub Backup Architecture (Git Tree vs Release Assets)**: When backing up to GitHub on a schedule (e.g., every 6h), do NOT commit raw `.tar.gz` archives or uncompressed SQLite database dumps (`state.db`) into git commits — git objects accumulate in `.git/objects` by 30-80MB per run, permanently ballooning local disk and remote clone size. Instead, use a split architecture:
  1. *Main branch*: Rsync and commit only human-readable text trees (`skills/`, `scripts/`, `memories/`, `cron/jobs.json`, `config/`, workspace files) so commits remain tiny diffs readable directly in GitHub.
  2. *Releases for Standalone System Archives*: Create full system tarballs (`.tar.gz` containing SQLite databases, sessions, and configs) and upload directly as GitHub Release assets via API (`POST /repos/{owner}/{repo}/releases/{id}/assets`). Release assets live in external object storage and never touch git packfiles.
  3. *Release Pruning*: Retain the newest N releases (e.g., 28 releases = 7 days of 6h intervals) and delete older releases and tags via API (`DELETE /repos/{owner}/{repo}/releases/{id}`).
  4. *Auth Isolation*: When a machine-wide git credential helper is bound to another user, embed the target token in the clone remote URL (`https://<user>:<token>@github.com/<owner>/<repo>.git`) and store API credentials in a restricted config (`chmod 600 ~/.config/backup/github_token.json`) rather than modifying global git settings.
- **Disk Watchdog Cron Placement**: Cron jobs running non-agent scripts (`no_agent: true`) look for executable scripts strictly in the active profile directory (`~/.hermes/scripts/<script_name>`). Ensure `~/.hermes/scripts/disk_watchdog.py` is present, marked executable (`chmod +x`), and outputs `[SILENT]` when healthy so scheduled runs succeed without error logs.

## Networking & Port Forwarding (Daytona / CDEs)
- **No Direct Public IP & Restricted Outbound**: CDEs often lack an exposed public IP. Running `curl ifconfig.me` might return an error like `Internet is restricted on Tier 1 and Tier 2`. Furthermore, outbound API calls (e.g., to LLM providers or `pkg.cloudflareclient.com`) may be silently dropped or return `Connection reset by peer`.
  - **Outbound Port 22 SSH Dropped**: Direct SSH (`ssh user@host -p 22`) times out because cloud containers block outbound port 22. To reach remote SSH targets or other Daytona workspaces (`ssh.app.daytona.io`), route through the local proxy bridge:
    `ssh -o ProxyCommand="python3 /home/daytona/ssh_proxy.py %h %p" <user>@<host>`
  - **Tunnel & Tunneling Domain DPI Blocks**: Daytona actively inspects TLS Client Hello SNI and immediately resets connections (TCP RST / `Connection reset by peer`) to known tunnel and terminal-sharing domains, including `*.trycloudflare.com`, `*.argotunnel.com`, `*.sshx.io`, `*.ngrok.io`, `*.localtunnel.github.io`, and `*.tunnelmole.com`. Both quick tunnels (`cloudflared tunnel --url ...`) and named token tunnels fail outbound on port 7844 and 443.
    - *Bypass via Cloudflare Worker Reverse Tunnel (Durable Objects)*: When a permanent public link is required despite DPI blocking, deploy a Cloudflare Worker with a SQLite Durable Object (`new_sqlite_classes = ["RouterTunnel"]` on free plan) paired with an outbound WebSocket client inside the CDE. Note: on restricted ISPs (Iran), Chrome may throw `ERR_QUIC_PROTOCOL_ERROR` on `*.workers.dev`; set `alt-svc: clear` on responses or disable `chrome://flags/#enable-quic`. See `references/cloudflare-worker-reverse-tunnel.md`.
    - *Bypass via Local SSH Port-Forwarding*: The lowest-latency, zero-tunnel alternative is forwarding the CDE service directly to the user's localhost: `ssh -N -L 20128:127.0.0.1:20128 <user>@ssh.app.daytona.io`.
  - If Hermes is installed *inside* the CDE, it may fail to reach external APIs. You cannot easily install Cloudflare WARP or V2Ray to bypass this if the host OS blocks it or lacks `systemd` to run the daemon.
  - The reliable fix for LLM API connection errors inside Daytona is to switch to an explicitly supported provider (like Nous Portal via `hermes model`) or run the agent locally rather than inside the restricted CDE.
- **Nested QEMU & Web Services Access**: In virtualized setups like Daytona QEMU instances (e.g. `DAYTONA-VPS1`), QEMU only forwards port 2222 to guest SSH (`-netdev user,id=net0,hostfwd=tcp::2222-:22`).
  - To expose services running inside the guest VM (like 9router on port 20128 or web panels):
    1. Bind on Daytona host: `ssh -N -f -L 0.0.0.0:20128:127.0.0.1:20128 -p 2222 ubuntu@127.0.0.1`.
    2. Forward to user machine: Instruct user to run SSH port-forwarding on their **local host machine** (e.g., Windows terminal):
       `ssh -N -L 20128:127.0.0.1:20128 <user>@ssh.app.daytona.io`
    3. User accesses the dashboard at `http://localhost:20128` in their local browser.
- **Systemd in Full Guest VMs**: When running a real nested QEMU Ubuntu VM inside Daytona, systemd is PID 1 (unlike bare CDE containers). Persist services (e.g. `9router.service` and `hermes-gateway.service`) under `/etc/systemd/system/` with `Restart=always` and `systemctl enable --now`.
  - Ensure `python-telegram-bot` is installed in Hermes's venv (`uv pip install python-telegram-bot`) before starting `hermes-gateway.service`.

## Minimal Container VPS (LXC / OpenVZ)
- **No systemd (PID 1)**: Commands like `systemctl enable --now docker` will fail with `System has not been booted with systemd as init system (PID 1)`.
  - *Fix*: The OS is a container, not a full VM. Use legacy init commands like `service docker start` or `/etc/init.d/docker start`. 
  - *Note*: Even if `systemctl` fails, if the host supports nested containers, the Docker daemon might still start successfully. Check with `docker ps`.
- **Missing Core Utilities**: `sudo` and `curl` are frequently absent because the default login is `root`. 
  - *Fix*: Omit `sudo` from commands. Run `apt update && apt install curl -y` to bootstrap.

## Shared cPanel Hosting (capability probe before promising deploys)

Probe shared cPanel via UAPI (no SSH needed) before promising a Python/FastAPI/Docker deploy:
`curl -sk -m 20 -H "Authorization: cpanel <user>:<API-TOKEN>" "https://<host>:2083/execute/<Module>/<func>"`.
Checklist: `DomainInfo/domains_data` (docroot, IP), `Features/list_features` (look for
`passengerapps`, `lvepythonsel`, `ssh`, `api_shell`, `mysql`, `ea-php8x`), `Mysql/list_databases`
+ `Mysql/list_users`, `Fileman/list_files?dir=public_html` (param is `dir=`, NOT `path=` —
`path=` alone silently returns the home dir), `Fileman/get_file_content?dir=<dir>&file=<name>`
(needs BOTH keys), `SSL/installed_hosts`. Expect `Terminal`, `Cron`, `MultiPHP`, `ZoneEdit`,
`CloudLinux`, `LangManagers`, `DiskUsage` modules to fail loading on restricted plans — treat as
missing capability, not retryable. Parse JSON with `python` on Windows (`python3` hits the Store shim).
DNS: public `nslookup <domain>` may NXDOMAIN while the server is fine — verify server-side with
`curl -sk --resolve <domain>:443:<cpanel-IP> https://<domain>/`. Decision rule: if
`passengerapps`/`lvepythonsel`/`ssh` are all 0, no persistent Python process (uvicorn/gunicorn/Docker)
can run — offer a PHP port preserving `/api/*` routes or a frontend-cPanel + backend-VPS split.
A `public_html` with only `index.php` (coming-soon) + `php.ini` + `cgi-bin` means empty docroot,
not a broken deploy. Never store the real API token in skills, memory, or guides — revoke after use.
Extended probe transcript and per-module notes: `references/cpanel-shared-hosting.md`.

## Permanent Hosting and CDEs
- **CDEs are Ephemeral**: They sleep when inactive and are not meant for permanent 24/7 web hosting.
- **Deploying to Free PaaS**: If the user asks to turn a CDE app into a permanent public link, explain the limitation. The best workflow is:
  1. Create a `docker-compose.yml` or Dockerfile.
  2. Push the code to a GitHub repository.
  3. Deploy the repository to a free PaaS provider like **Koyeb** or **Render** for a permanent URL.

## Deploying Single-File Python Polling Bots (Telegram / Bale) to Ubuntu VPS

Use for long-polling single-file bots (`bot.py`, `bot2.py`, … with SQLite beside the file).
Full runbook: `references/python-polling-bots-vps.md`.

- **Access warning (sshx.io)**: an `sshx.io/s/...` link is a temporary shared terminal,
  not permanent VPS access. Tell the user to get IP + user + password / SSH key from
  the provider and keep it safe; the link expires and anyone with the full URL can join.
- **Inspect first**: `whoami; cat /etc/os-release; python3 --version; free -h; nproc`.
  Ubuntu 22.04 + Python 3.10+ is the common good case. Check init before promising
  systemd: `ps -p 1 -o comm=` — container VPS often returns something other than `systemd`.
- **Path portability (most common breakage)**: single-file bots frequently hardcode
  paths (`Path("/home/container/Bot 4")`, `DB_PATH = "Bot/bot_database.db"`,
  `open("Bot/games_state.json")`). They only run from the right cwd or not at all.
  Fix to `BASE_DIR = Path(__file__).resolve().parent` and join DB/log/media dirs to it;
  run each bot from its own folder (`/opt/bots/<name>/`).
- **Transfer without SCP**: sshx has no file manager. Have the user zip one bot folder
  on Windows (right-click → Compressed folder), upload to tmpfiles.org / transfer.sh,
  then on the server `wget "<link>" -O bot.zip && unzip -o bot.zip`.
  Warn: bot tokens live inside these files — never post the link publicly.
- **One venv per bot**: `python3 -m venv venv && source venv/bin/activate &&
  pip install -U pip && pip install -r requirements.txt`. Never share one venv across bots.
- **Keep-alive**: quick path is `tmux new -s <name>` + run + `Ctrl+B, D` detach;
  correct path is one systemd unit per bot (`Restart=always`, `WantedBy=multi-user.target`,
  `ExecStart=/opt/bots/<name>/venv/bin/python /opt/bots/<name>/bot.py`) with
  `daemon-reload → enable → start → status`. After code changes: `systemctl restart <name>`.
- **One bot at a time**: deploy and verify the cleanest bot first before touching the rest.

## SSH Stability
- Interactive TUIs or wizards over CDE SSH sessions can sometimes drop unexpectedly (`Connection reset by peer`). When automating installations, prefer non-interactive flags or direct config file edits over spawning interactive prompts.
  - *Example*: Instead of running `hermes setup` over SSH which launches a TUI and crashes, manually write the API keys to `.env` and settings to `config.yaml`, then run `hermes gateway run` in the foreground or background (with `nohup`).
- **Hermes Telegram gateway runbook**: `references/hermes-telegram-gateway.md` — manual
  `.env` wiring (`TELEGRAM_BOT_TOKEN` + `TELEGRAM_ALLOWED_USERS`), `getMe` pre-check,
  default per-user DM session isolation, two-bot profile isolation, 9router combo `/model`
  picker integration (`discover_models: false` + `model_aliases:`), and the secret round-trip check.
- **Superserve Sandbox Bridging**: `references/superserve-sandboxes.md` — control/data
  plane split (`/api` vs `/dp`), Cloudflare Worker proxying around geo-blocks,
  Host header stripping, body buffering, auto-pause/activate token rotation,
  preview ports, fast KV & ephemeral in-tunnel archive transfer, multi-profile
  Hermes skills synchronization, 502 outage vs expired key diagnosis, and
  zero-downtime preemptive failover with edge health watchers (Cron Triggers + KV).
