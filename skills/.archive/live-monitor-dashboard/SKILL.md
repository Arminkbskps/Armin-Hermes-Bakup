---
name: live-monitor-dashboard
category: software-development
description: Live dashboard for Python automation - no external deps.
---

# Live Monitor Dashboard

Build a real-time web dashboard for any Python automation or batch process. Zero external dependencies — uses Python's built-in socket server, a _status.json file for live state, and a single-file SPA dashboard HTML page.

When to use: any scenario where a user needs to see what a long-running Python script is doing without SSH'ing, grepping logs, or polling the filesystem manually.

## Architecture

```
  automation.py                         dashboard_server.py
  +--------------------+                +----------------------+
  | StatusManager      | writes         | socket HTTP server   |
  | ProjectManager     | ------------>  |  /api/status         |
  | ...                |   _status.json  /api/projects         |
  |                    |                 /api/log/main          |
  +--------------------+                | /api/voice-file      |
                                        | /api/run-automation  |
                                        |                      |
                                        | +------------------+ |
                                        | | dashboard.html   | |
                                        | | SPA, dark theme  | |
                                        | | auto-refresh     | |
                                        | +------------------+ |
                                        +----------------------+
```

## Core Components

### 1. Status Manager (_status_manager.py)

A writer/reader pair around a _status.json file. The automation writes to it at each step; the dashboard reads it on every poll cycle.

```python
class StatusManager:
    def __init__(self, root: Path):
        self._path = root / "_status.json"
        self._data = {
            "status": "idle",           # idle | running | completed | error
            "current_step": "\u2014",
            "page": "\u2014",
            "topic": "\u2014",
            "project_folder": "\u2014",
            "project_dir": "\u2014",
            "progress_pct": 0,
            "last_update": "",
            "started_at": "",
        }
        self._write()

    def set_step(self, step: str, progress: int | None = None) -> None:
        self._data["current_step"] = step
        if progress is not None:
            self._data["progress_pct"] = min(100, max(0, progress))
        self._write()

    def set_page(self, page: str) -> None:
        self._data["page"] = page
        self._write()

    def mark_error(self, msg: str) -> None:
        self._data["status"] = "error"
        self._data["current_step"] = f"ERROR: {msg}"
        self._data["started_at"] = ""
        self._write()

    def mark_completed(self) -> None:
        self._data["status"] = "completed"
        self._data["progress_pct"] = 100
        self._data["started_at"] = ""
        self._write()
```

Key design: The status file is just JSON — no locks needed since writes are atomic on most filesystems for small payloads.

### 2. Project Manager (_project_manager.py)

Creates per-run project folders with Persian/Arabic-safe folder names:

```
projects/
+-- 2026-07-28_تأثير-اسكن-چهره-با-هوش-مصنوعي/
|   +-- info.json              # topic, status, steps_completed
|   +-- narration_fa.txt       # Persian narration
|   +-- youtube_post.txt       # YouTube prompt result
|   +-- telegram_post.txt      # Telegram prompt result
|   +-- results.txt            # Full results log
|   +-- audio.wav              # Copied audio
+-- 2026-07-27_نانو-ربات-در-جريان-خون/
    +-- ...
```

Folder name generation: _persian_slug() preserves Persian/Arabic Unicode (\u0600-\u06FF), collapses unsafe chars into dashes, truncates to ~50 chars, prepends date.

### 3. HTTP Server (dashboard_server.py)

Use Python's built-in http.server or raw sockets. Pattern:

```python
def handle_request(method, url, body):
    parsed = urlparse(url)
    path = unquote(parsed.path)
    qs = parsed.query
    params = {k: unquote(v) for k, v in
              (p.split("=",1) for p in qs.split("&") if "=" in p)}

    # Static file serving
    if path == "/": path = "/dashboard.html"
    static_path = ROOT / path.lstrip("/")
    try:
        static_path.resolve().relative_to(ROOT.resolve())  # security
    except (ValueError, OSError):
        return 403, b"forbidden"
    return read_file_bytes(static_path)

    # JSON APIs
    if path == "/api/status":   return json.dumps(status_data)
    if path == "/api/config":   return cfg_json
    if path == "/api/projects": return json.dumps(projects)
    if path == "/api/log/main": return automation_log[-500:]
```

Security: Guard against path traversal ("..", "/", "\" in params). Resolve paths and verify relative_to(ROOT).

### 4. Dashboard HTML (dashboard.html)

A single-file SPA with sections for live status (SVG progress ring + step/page text), stats row, tabbed config viewer, colorized live logs, inline audio players for WAV files, clickable project folder cards, and quick action buttons.

Auto-refresh at 5s via setInterval. Tab routing via event delegation on .tabs container.

## API Endpoints

| Endpoint | Method | Returns |
|---|---|---|
| / | GET | dashboard.html |
| /api/status | GET | {status, current_step, page, topic, progress_pct, ...} |
| /api/projects | GET | [{folder, topic, status, has_audio, ...}] |
| /api/project/{folder} | GET | {topic, status, files: [{name, size}]} |
| /api/config | GET | Raw config.json |
| /api/log/main | GET | Last 500 log lines |
| /api/voices | GET | ["file1.wav", ...] |
| /api/voice-file?f=.. | GET | Binary audio |
| /api/run-automation | POST | Spawns automation.py in bg |

## Pitfalls

- Non-ASCII filenames on Windows: use shutil.copy2. Path r/w handles Unicode.
- Auto-refresh at 5s for status; avoid under 2s on log-heavy pages.
- Port conflict: try PORT+1 as fallback.
- Large logs: serve only last 500-1000 lines.
- Dashboard RTL for Persian: dir=rtl on html, keep code LTR.
- Status file races: rare; completed/error writes catch stale state.
- Spaces in filenames: encodeURIComponent() in JS, unquote() server-side.
- Static file security: always resolve + relative_to(ROOT).

## Integration

1. Create _status_manager.py (StatusManager) and _project_manager.py (ProjectManager with Persian slug)
2. Patch automation to init StatusManager(ROOT) and call set_step/set_page throughout
3. Create dashboard_server.py (socket HTTP server + all endpoints)
4. Create dashboard.html (single-file SPA)
5. Create start_dashboard.bat / shell script
6. Verify: browser shows idle status, logs load, config renders
