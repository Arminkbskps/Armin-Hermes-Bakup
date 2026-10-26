---
name: flask-process-manager
category: software-development
description: Manage background Python daemons with a Flask web panel.
---

# Flask Process Manager Web Panel

Build a single-file Flask web application that controls background Python daemons (bots, workers, crawlers). The pattern is: **process manager API + beautiful live-updating dashboard**.

## Architecture

```
┌──────────────────────────────────────┐
│         Browser (UI)                 │
│  Dark glassmorphism, Vazir font,     │
│  Font Awesome, toggle switches       │
└─────────────┬────────────────────────┘
              │ HTTP (JSON API)
┌─────────────▼────────────────────────┐
│       Flask Backend                  │
│  /api/status  /api/start             │
│  /api/stop    /api/toggle            │
└─────────────┬────────────────────────┘
              │ subprocess / psutil
┌─────────────▼────────────────────────┐
│     Background Python Processes      │
│  bot1.py  bot2.py  worker.py ...     │
└──────────────────────────────────────┘
```

## Core Components

### 1. Process Manager Class
- `subprocess.Popen` to start daemons
- `psutil.Process` to monitor (RAM, CPU, PID, uptime)
- `proc.terminate()` / `proc.kill()` to stop
- Track processes in a `dict[str, psutil.Process | subprocess.Popen]`
- Auto-discover existing processes by scanning `psutil.process_iter()` for matching command lines

### 1a. Security — Login Page

**Always add authentication** before deploying. The panel controls real processes — leaving it open is dangerous.

Pattern: a `@app.before_request` hook that checks for a cookie/token:

```python
PANEL_PASSWORD = "change-me-before-deploy"

@app.before_request
def require_auth():
    if request.path == "/":
        token = request.args.get("token") or request.cookies.get("token")
        if token != PANEL_PASSWORD:
            return render_template_string(LOGIN_HTML)
    elif request.path.startswith("/api/"):
        token = request.headers.get("X-Panel-Token") or request.args.get("token")
        if token != PANEL_PASSWORD:
            return jsonify({"error": "unauthorized"}), 401

@app.route("/auth")
def auth_check():
    token = request.args.get("token", "")
    return jsonify({"ok": token == PANEL_PASSWORD})
```

The login page itself is a minimal dark-themed form (same Vazir font / Font Awesome stack) that POSTs to `/auth?token=...` and sets a cookie. The JS side sends `X-Panel-Token` header on every API call; 401 responses redirect back to `/`.

**Pitfall:** Never embed the password into the JS login page source — it's checked server-side only. The login form POSTs to `/auth`, gets a JSON `{"ok": true/false}`, and only then sets the cookie.

### 2. Flask API Routes

| Route | Method | Purpose |
|---|---|---|
| `/` | GET | SPA HTML page (or login redirect) |
| `/auth` | GET | Validate password token, return `{"ok": bool}` |
| `/api/status` | GET | All bots + system stats |
| `/api/start/<id>` | POST | Start a bot |
| `/api/stop/<id>` | POST | Stop a bot |
| `/api/toggle/<id>` | POST | Start/stop toggle |
| `/api/start_all` | POST | Start all stopped |
| `/api/stop_all` | POST | Stop all running |

### 3. UI Key Patterns (Persian RTL)
- **Font**: Vazir from CDN (`rastikerdar/vazir-font`)
- **Icons**: Font Awesome 6 (`fa-brands`, `fa-solid`)
- **Theme**: Dark background (`#0a0e17`), glassmorphism cards (`#1a2332` with border)
- **Toggle**: Pure CSS toggle switch (`<input type="checkbox">` + `<label>`)
- **Status indicators**: Green = running, dimmed = stopped, accent bar on top of cards
- **Auto-refresh**: `setInterval(fetchStatus, 5000)`
- **Loading overlay**: Full-screen backdrop blur with spinner
- **Toast notifications**: Slide-in/slide-out for success/error feedback

## Code Template

```python
from flask import Flask, jsonify, render_template_string
import psutil, subprocess, time, os, signal, platform

app = Flask(__name__)

BOTS = {
    "bot1": {
        "name": "My Bot",
        "file": "bot.py",
        "icon": "fa-brands fa-telegram",
        "color": "#2AABEE",
        "category": "Messaging",
    },
}

class ProcessManager:
    def __init__(self):
        self.processes = {}
        self._discover_existing()

    def _discover_existing(self):
        for proc in psutil.process_iter(["pid", "cmdline"]):
            try:
                cl = " ".join(proc.info["cmdline"] or [])
                for bid, bd in BOTS.items():
                    if bd["file"] in cl and bid not in self.processes:
                        self.processes[bid] = proc
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

    def _get(self, bot_id):
        proc = self.processes.get(bot_id)
        if proc is None:
            return None
        try:
            p = proc if isinstance(proc, psutil.Process) else psutil.Process(proc.pid)
            return p if p.is_running() else None
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            self.processes.pop(bot_id, None)
            return None

    def start(self, bot_id):
        pass

    def stop(self, bot_id):
        pass

    def status(self, bot_id):
        proc = self._get(bot_id)
        if not proc:
            return {"running": False, "ram_mb": 0}
        mem = proc.memory_info()
        return {
            "running": True,
            "pid": proc.pid,
            "ram_mb": round(mem.rss / 1024 / 1024, 1),
            "cpu_percent": round(proc.cpu_percent(interval=0.1), 1),
            "uptime_seconds": int(time.time() - proc.create_time()),
        }
```

## Pitfalls
- **Working directory**: Always `cwd=str(bot_file.parent)` so relative paths resolve correctly
- **Windows vs Linux**: `creationflags=subprocess.CREATE_NO_WINDOW` on Windows to hide console windows
- **Startup crash detection**: After `Popen()`, sleep 1s then `proc.poll()` — if exit code is not None, read stderr and report immediately
- **Zombie processes**: Always call `.wait()` after terminate/kill; use `try/except psutil.TimeoutExpired` for the 5-second grace
- **Resource leaks**: `subprocess.PIPE` for stdout/stderr can deadlock if not consumed; for silent bots, use `subprocess.DEVNULL` instead
- **Thread safety**: Flask dev server uses threads; use `threading.Lock` around process dict mutations if needed
- **Don't assume localhost**: The panel is useless if the user can't reach it. Always include deployment instructions — don't just create the file and stop.

## Deployment

### PORT Environment Variable
Many cloud hosts (Heroku, Railway, HidenCloud) assign a dynamic port. Support it:

```python
port = int(os.environ.get("PORT", os.environ.get("SERVER_PORT", "5000")))
```

### Production Server — Waitress
Flask dev server is single-threaded and leaks on long-running subprocess managers. Auto-detect Waitress:

```python
try:
    from waitress import serve
    serve(app, host="0.0.0.0", port=port, threads=8)
except ImportError:
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
```

### Network Detection
Print the host's detected LAN IP alongside localhost so the user knows where to connect:

```python
import socket
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.connect(("8.8.8.8", 80))
real_ip = s.getsockname()[0]
s.close()
print(f"📍 Local:  http://localhost:{port}")
print(f"🌐 LAN:    http://{real_ip}:{port}")
print(f"☁️ Cloud:  http://<server-ip>:{port}")
```

### Restricted Hosts (Game Servers, Firewalled VPS)
Some hosts like **HidenCloud** (game server hosting, 2 vCores / 3GB RAM / 15GB free) don't expose arbitrary ports. Options:

| Problem | Solution |
|---|---|
| No port forwarding in panel | Use **Cloudflare Tunnel**: `cloudflared tunnel --url http://localhost:PORT` → gives a `trycloudflare.com` URL |
| Only game ports open | Bind to an allocated port (check panel → Allocations → add port) |
| No public IP | Use **ngrok** for HTTP forwarding: `ngrok http PORT` |
| SSH-only access | Forward via SSH tunnel: `ssh -L 5000:localhost:PORT user@host` |

Cloudflare Tunnel is preferred (free, no auth, auto-HTTPS, no client software on the browser side):

```bash
# Install
curl -L https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-linux-amd64 -o cloudflared
chmod +x cloudflared
# Run alongside the panel
./cloudflared tunnel --url http://localhost:5000
```

## Related Reference Files

- `references/bot_manager_example.md` — Full working bot_manager.py with 5-bot dashboard
- `references/python_ram_footprint.md` — RAM diagnostics: why matplotlib + aiogram bloat
- `references/hidencloud_deployment.md` — Deploying on restricted hosts (game server hosting, firewalled VPS)
