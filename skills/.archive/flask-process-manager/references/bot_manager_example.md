# Flask Bot Manager — Full Working Implementation

This file was built during a real session to manage 5 Telegram/Bale bots.
It demonstrates the complete pattern: Flask API + subprocess management + modern Persian dark-themed UI.

## File Location
```
D:\Hermes file\bot_manager\bot_manager.py
```

## Quick Start
```bash
pip install flask psutil
python bot_manager.py
# Open http://localhost:5000
```

## Key Design Decisions
- **Single-file**: Everything in `bot_manager.py` for easy deployment
- **Process discovery**: Scans running PIDs on startup to detect already-running bots
- **Startup crash detection**: Sleeps 1s after Popen, checks `proc.poll()` before reporting success
- **Windows compat**: Uses `creationflags=subprocess.CREATE_NO_WINDOW` to hide console windows
- **HTML inlined**: Full UI template inside `render_template_string()` — no external files needed

## Bot Definitions Structure
```python
BOT_DEFINITIONS = {
    "bot1": {
        "name": "Bot Display Name",
        "file": "bot.py",           # relative to BOTS_DIR
        "description": "What it does",
        "icon": "fa-brands fa-telegram",   # Font Awesome class
        "color": "#2AABEE",                # Accent color for card
        "category": "Group Management",     # For category tag
    },
}
```

## API Endpoints
See SKILL.md for the full route table. Key nuance: `/api/toggle/<id>` reads current status and calls start or stop accordingly — avoids race conditions from stale frontend state.

## UI Theme Stack
- **Background**: `#0a0e17` with radial gradient overlays (3 ellipses at 20%/50%/80%)
- **Cards**: `#1a2332` with `3px` top accent bar colored per bot
- **Toggle**: 50×28px pill, green when checked, smooth slide transition
- **System bar**: 5 mini-cards showing RAM (with progress bar), CPU, Python version, OS, active bot count
- **Toast**: Bottom-right stack with slide-in animation, auto-dismiss after 3s
- **Loading**: Full-screen `backdrop-filter: blur(8px)` overlay with spinning border

## Bot Path Configuration
The real bot paths point to:
```python
BOTS_DIR = Path(r"D:\System File\Downloads\Bots")
```
Each bot file is `{BOTS_DIR}/{def["file"]}`. The subprocess `cwd` is set to `BOTS_DIR` so relative SQLite paths in the bots resolve correctly.
