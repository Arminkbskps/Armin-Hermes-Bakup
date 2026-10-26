# Single-File Python Polling Bots → Ubuntu VPS Runbook

For Telegram (aiogram / python-telegram-bot / requests+threading) and Bale
(`tapi.bale.ai`) long-polling bots that keep SQLite + logs beside the `.py` file.

## 1. Intake inspection (run on the server first)

```bash
whoami; pwd; echo "---"; cat /etc/os-release; echo "---"
python3 --version; pip3 --version; echo "---"
free -h; df -h; nproc; echo "---"; ls -la
ps -p 1 -o comm=   # 'systemd' or not — decides keep-alive path
```

Good baseline seen in the field: Ubuntu 22.04, Python 3.10.12, root, systemd present.
Container VPS often has huge CPU/RAM but no systemd — check before promising units.

## 2. Bot inventory (run locally before touching the server)

```bash
grep -E "^import |^from " <bot>.py | sort -u        # third-party deps
grep -oE "(BOT_TOKEN|TOKEN)[\"']? *[:=] *[^,}]*" <bot>.py | head -3
grep -oE "(DB_PATH|DATABASE_PATH|BASE_DIR|LOG_PATH)[^,]*" <bot>.py | head -5
grep -c "Bot/" <bot>.py                             # hardcoded relative paths?
```

Real patterns encountered:
- Bale supergroup bot (`bot.py`, ~800KB, requests+threading, psutil, g4f optional):
  `TOKEN`, `DB_PATH = "Bot/bot_database.db"`, reads/writes `Bot/games_state.json`,
  `Bot/db_backup_*.db`, `Bot/exports/`, `Bot/downloads/`, `Bot/backups/`.
  Only runs from a cwd that has the `Bot/` subdir beside it.
- Telegram twin (`bot2.py`): same shape, `DB_PATH = "Bot 2/bot_database.db"`,
  log file `"bot 2.log"`.
- aiogram uploaders (`bot3.py`, `uploader.py`): only need `aiogram`;
  the older copy hardcoded `DATABASE_PATH = "Bot 3/ai_pro_uploader.sqlite3"`.
- Content bot (`bot4.py`, aiogram+aiohttp+bs4+rapidfuzz): hardcoded
  `BASE_DIR = Path("/home/container/Bot 4")` — dead on any other host.
- Gold radar (`bot5.py`, aiogram+aiohttp+bs4+aiosqlite+matplotlib+g4f): already
  portable (`BASE_DIR = Path(__file__).resolve().parent`).

## 3. Path-portability fixes (apply to local copies before upload)

```python
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "bot4.sqlite3"          # was Path("/home/container/Bot 4")
DATABASE_PATH = str(BASE_DIR / "ai_pro_uploader.sqlite3")  # was "Bot 3/..."
LOG_PATH = str(BASE_DIR / "ai_pro_uploader.log")
```

Keep each bot in its own folder (`/opt/bots/<name>/`) with its DB/log beside the
script. For the `Bot/`-prefixed legacy bots, ship the subdir (`Bot/games_state.json`)
inside the zip and always start the process with cwd = the bot folder.
Cleanest bots first — deploy one, verify, then repeat.

## 4. Dependency map (per-bot venv, never shared)

- bot1 / bot2 (requests bots): `requests psutil g4f` (+ stdlib sqlite3/threading)
- bot3 / uploader: `aiogram`
- bot4: `aiogram aiohttp beautifulsoup4 rapidfuzz g4f`
- bot5: `aiogram aiohttp beautifulsoup4 aiosqlite matplotlib g4f`

```bash
apt update && apt install -y python3-venv python3-pip unzip tmux nano htop curl
mkdir -p /opt/bots/<name> && cd /opt/bots/<name>
python3 -m venv venv && source venv/bin/activate
pip install -U pip && pip install -r requirements.txt
python <bot>.py     # smoke test: bot answers in Telegram/Bale, then Ctrl+C
```

## 5. Getting files onto the box without SCP (sshx.io case)

sshx is a browser shared terminal — no file manager, link expires, anyone with the
full URL (including the `#fragment`) can join. User-side flow:

1. On Windows: right-click bot folder → Send to → Compressed folder (`<name>.zip`).
2. Upload the zip at tmpfiles.org / transfer.sh, copy the download link.
   Warn: tokens are inside these files — never post the link publicly.
3. On the server:
   ```bash
   cd /opt/bots/<name>
   wget "<link>" -O bot.zip && unzip -o bot.zip && ls -lh
   ```

Also warn the user to obtain permanent access (IP + user + password/SSH key) —
when the sshx link dies they lose the box otherwise.

## 6. Keep-alive

Quick (works everywhere, survives SSH close, not reboot):

```bash
tmux new -s <name>
source venv/bin/activate
python <bot>.py
# Ctrl+B then D to detach; tmux attach -t <name> to rejoin
```

Correct (systemd, only if `ps -p 1 -o comm=` says `systemd`):

```ini
# /etc/systemd/system/<name>.service
[Unit]
Description=<Human name> bot
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/bots/<name>
ExecStart=/opt/bots/<name>/venv/bin/python /opt/bots/<name>/<bot>.py
Restart=always
RestartSec=5
StandardOutput=append:/opt/bots/<name>/bot.log
StandardError=append:/opt/bots/<name>/bot.log

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable <name> && sudo systemctl start <name>
sudo systemctl status <name>
sudo journalctl -u <name> -f        # live log
sudo systemctl restart <name>       # after every code re-upload
```

## 7. Update flow

Re-zip locally → re-upload → `unzip -o` over the folder → `systemctl restart <name>`
(or kill + rerun inside tmux). SQLite files beside the script survive restarts;
`-shm`/`-wal` sidecars next to the `.db` are normal.
