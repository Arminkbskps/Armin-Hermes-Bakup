---
name: python-live-dashboard
category: software-development
description: "Live dashboard for Python CLI projects using only stdlib."
---

# Python Live Dashboard

Use this skill when you need to add a **live web dashboard** to an existing Python CLI project that has log files, config, results, or output audio/video files — without adding any dependencies (no Flask, no FastAPI, no npm). The pattern is a **stdlib-only HTTP server** that reads project files and exposes them as REST API endpoints, served alongside a **single-file self-contained HTML** dashboard with auto-refresh.

## Architecture

```
┌────────────────────────────────────┐
│  Browser (dashboard.html)          │
│  Dark theme, cards, tabs, audio    │
│  Auto-refresh every 10s            │
└──────────────┬─────────────────────┘
               │ HTTP (fetch /api/*)
┌──────────────▼─────────────────────┐
│  dashboard_server.py               │
│  (stdlib: socket, json, urllib, os)│
│                                    │
│  /api/config     → config.json     │
│  /api/log/main   → automation.log  │
│  /api/voices     → voices/*.wav    │
│  /api/history    → history.txt     │
│  /api/results    → results.txt     │
│  /api/voice-file → stream audio    │
└──────────────┬─────────────────────┘
               │ reads project files
┌──────────────▼─────────────────────┐
│  Project Files                     │
│  config.json  *.log  *.txt         │
│  voices/      results.txt          │
└────────────────────────────────────┘
```

## Core Steps

### 1. Create the Python HTTP server (`dashboard_server.py`)

Build a single-file Python server using only stdlib (`socket`, `json`, `urllib.parse`, `os`, `threading`, `time`, `pathlib`). No imports from external packages.

#### Key route patterns

```python
from pathlib import Path
from urllib.parse import urlparse, unquote
import json, os, socket, threading, time

ROOT = Path(__file__).resolve().parent
HOST = "127.0.0.1"
PORT = 1865

MIME = {
    ".html": "text/html; charset=utf-8",
    ".css": "text/css; charset=utf-8",
    ".js": "application/javascript; charset=utf-8",
    ".json": "application/json; charset=utf-8",
    ".txt": "text/plain; charset=utf-8",
    ".wav": "audio/wav",
    ".mp3": "audio/mpeg",
    ".png": "image/png",
}


def handle_request(method: str, url: str, body: bytes) -> tuple:
    parsed = urlparse(url)
    path = unquote(parsed.path)
    qs = parsed.query
    params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
    params = {k: unquote(v) for k, v in params.items()}  # ← CRITICAL

    # Config
    if path == "/api/config":
        return 200, "application/json", (ROOT / "config.json").read_bytes()

    # Logs (tail mode)
    if path == "/api/log/main":
        data = (ROOT / "automation.log").read_bytes()
        lines = data.decode("utf-8", errors="replace").splitlines()[-500:]
        return 200, "text/plain; charset=utf-8", "\n".join(lines).encode("utf-8")

    # List voice files
    if path == "/api/voices":
        vdir = ROOT / "voices"
        files = sorted(
            (f.name for f in vdir.iterdir()
             if f.is_file() and f.suffix.lower() in (".wav", ".mp3", ".txt")),
            key=lambda n: (ROOT / "voices" / n).stat().st_mtime, reverse=True
        )
        return 200, "application/json", json.dumps(files, ensure_ascii=False).encode("utf-8")

    # Serve audio files
    if path == "/api/voice-file":
        fname = params.get("f", "")
        if not fname or ".." in fname or "/" in fname or "\\" in fname:
            return 403, "text/plain", b"forbidden"
        fpath = ROOT / "voices" / fname
        ct = MIME.get(fpath.suffix.lower(), "application/octet-stream")
        return 200, ct, fpath.read_bytes()

    # Static files
    if path == "/" or path == "":
        path = "/dashboard.html"
    static_path = ROOT / path.lstrip("/")
    try:
        static_path.resolve().relative_to(ROOT.resolve())
    except ValueError:
        return 403, "text/plain", b"forbidden"
    if static_path.is_file():
        return 200, MIME.get(static_path.suffix, "application/octet-stream"), static_path.read_bytes()

    return 404, "text/plain", b"not found"
```

#### Server loop

```python
def run_server():
    global PORT  # ← MUST be first, before any use of PORT
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        server.bind((HOST, PORT))
    except OSError:
        PORT += 1
        server.bind((HOST, PORT))
    server.listen(16)
    server.settimeout(1.0)

    # Open browser
    threading.Thread(target=lambda: (
        time.sleep(0.8), __import__("webbrowser").open(f"http://{HOST}:{PORT}/")
    ), daemon=True).start()

    while True:
        try:
            conn, addr = server.accept()
        except socket.timeout:
            continue
        try:
            data = conn.recv(65536)
            if not data: continue
            request_line = data.split(b"\r\n")[0].decode()
            parts = request_line.split()
            method = parts[0]
            url = parts[1]
            # Minimal header/body split
            head, _, body = data.partition(b"\r\n\r\n")
            status, ct, resp = handle_request(method, url, body)
            conn.sendall(
                f"HTTP/1.1 {status} OK\r\n"
                f"Content-Type: {ct}\r\n"
                f"Content-Length: {len(resp)}\r\n"
                f"Access-Control-Allow-Origin: *\r\n"
                f"Cache-Control: no-cache\r\n"
                f"Connection: close\r\n\r\n".encode() + resp
            )
        finally:
            conn.close()
```

### 2. Create the single-file HTML dashboard (`dashboard.html`)

A self-contained HTML file with inline `<style>` and `<script>`. No build step, no external CSS frameworks.

**UI sections to include:**

| Section | Content |
|---|---|
| **Header bar** | Logo, title, status badge, auto-refresh indicator, manual refresh button |
| **Stats grid** | Card per stat: audio file count, narration count, result lines, log entries, last run time, build version. Colored: accent, green, orange, purple, blue |
| **Config panel** | Tabbed (core / TTS / flow), compact key-value grid from config.json |
| **Log viewer** | Tabbed (automation / flow / watermark), color-coded log lines, tailed to last 80 lines |
| **Audio players** | WAV file list with native `<audio controls>`, file size, download links |
| **History/Results** | Tabbed — history list and results.txt preview (last 100 lines in monospace) |
| **Quick actions** | Run Automation, Open Voices, Open Log, Edit Config |

**Key CSS tokens:**
```css
:root {
  --bg: #0a0c10;
  --surface: #14181f;
  --surface2: #1c2330;
  --surface3: #263040;
  --border: #2a3446;
  --text: #dce1ed;
  --text2: #8896aa;
  --accent: #6c8cff;
  --accent2: #a78bfa;
  --green: #34d399;
  --orange: #fb923c;
  --red: #f87171;
  --blue: #60a5fa;
  --radius: 12px;
  --shadow: 0 8px 32px rgba(0,0,0,.45);
}
```

**Auto-refresh pattern:**
```javascript
async function refreshAll() {
  renderStats();
  const activeTab = qs('#configTabs .tab.active')?.dataset?.tab || 'configCore';
  renderConfig(activeTab);
  const logTab = qs('#logTabs .tab.active')?.dataset?.tab || 'logMain';
  renderLogs(logTab);
  renderVoices();
  renderHistory();
}
// Initial load + auto-refresh every 10 seconds
refreshAll();
setInterval(refreshAll, 10000);
```

### 3. Create a start script

```bat
@echo off
title Dashboard - %~dp0
cd /d "%~dp0"
py dashboard_server.py
pause
```

## Critical Pitfalls

### 1. URL-encode query parameter values
The browser's `fetch()` URL-encodes special characters (spaces → `%20`, commas → `%2C`). The Python server must `unquote` BOTH the request path AND every query parameter value:

```python
# ✓ CORRECT
params = {k: unquote(v) for k, v in params.items()}

# ✗ WRONG — params still have %20, %2C etc.
params = dict(p.split("=", 1) for p in qs.split("&") if "=" in p)
```

### 2. `global` declaration order in Python
When modifying a module-level variable inside a function, `global <name>` must be the **first statement** in the function body — before imports, before any read or write:

```python
def run_server():
    global PORT       # ← FIRST
    import socket     # ← OK after global
    server.bind((HOST, PORT))  # reads PORT
    PORT += 1                   # writes PORT
```

Putting `global PORT` after the `bind` call causes `SyntaxError: name 'PORT' is used prior to global declaration`.

### 3. Directory traversal protection
Always resolve both sides and require the static path to be under the project root:

```python
try:
    static_path.resolve().relative_to(ROOT.resolve())
except ValueError:
    return 403, "text/plain", b"forbidden"
```

### 4. MIME type for audio files
Browsers need the correct `Content-Type` for inline audio playback. `.wav` → `audio/wav`, not `audio/wave` or `application/octet-stream`. Maintain a MIME dictionary keyed by extension.

### 5. Connection lifecycle
The stdlib socket server is single-threaded and vulnerable to slow clients. Always:
- Set `server.settimeout(1.0)` so `KeyboardInterrupt` is responsive
- Wrap `sendall` in `try/finally` → `conn.close()`
- Set `Cache-Control: no-cache` to prevent stale data in the browser

### 6. CORS for dev tools
Add `Access-Control-Allow-Origin: *` headers so `curl`, Postman, and browser dev tools can test the API from any origin.

### 7. Filesystem path gotchas
- Windows `startfile()` paths need `.resolve()` to convert forward slashes
- File names with spaces, commas, colons need proper encoding on both sides
- Always open file paths from `Path.resolve()` to avoid relative path confusion

### 8. Credential Safety
When modifying or generating code based on this template, **never** copy sample API keys, bot tokens, or admin IDs. Always extract and strictly use the user's explicit credentials from their provided configuration files (e.g., `.env`).

## When NOT to use this skill

- The project already has Flask/FastAPI — just serve the dashboard from the existing app
- The user needs authentication, websockets, or database-backed live updates — use Flask + psutil + websockets instead
- The user wants a design mockup before building — use the `sketch` skill
- The project doesn't have file-based data that changes over time
