# Hermes WebUI Setup on Windows

## Prerequisites
- Python 3.11+
- Git
- Hermes Agent installed (runs locally)

## Installation Steps

```bash
# Clone to D:\hermes-webui
cd /d
git clone --depth 1 https://github.com/nesquena/hermes-webui.git hermes-webui

# Create venv inside the project dir (from hermes-agent venv or a clean Python)
cd hermes-webui
python -m venv venv

# Install ALL requirements into the venv's own site-packages
# Using --target to override pip's "already satisfied" from parent-venv
venv/Scripts/pip install --target venv/Lib/site-packages -r requirements.txt

# Install hermes-agent in editable mode for AIAgent import
# This does NOT install dependencies — they come from the step above
cd /c/Users/<user>/AppData/Local/hermes/hermes-agent  # (or wherever the agent is)
/d/hermes-webui/venv/Scripts/pip install -e .

# CRITICAL: verify the full import chain works
cd /d/hermes-webui
venv/Scripts/python -c "import yaml, requests, httpx, openai; from run_agent import AIAgent; print('OK')"
```

## start.bat Template

Save as `D:\hermes-webui\start.bat`:

```batch
@echo off
title Hermes WebUI
cd /d "D:\hermes-webui"
echo Starting Hermes WebUI server on port 8787...
echo Server URL: http://localhost:8787
"D:\hermes-webui\venv\Scripts\python.exe" server.py
pause
```

> **Critical:** Use the absolute path to `venv\Scripts\python.exe` — do NOT rely on `call venv\Scripts\activate.bat` followed by bare `python`. Activation is unreliable in .bat files: it can fall back to the system Python (which lacks all project dependencies).

## First Startup

1. Double-click `D:\hermes-webui\start.bat`
2. Open http://localhost:8787 in your browser
3. You should see the Hermes WebUI interface

## Troubleshooting

### "AIAgent not available" Error

**Symptom:** Chat requests fail with "AIAgent not available" even though the HTML loads. The error shows sys.path entries for the agent directory.

**Root Cause (not obvious):** The error message is a *generic wrapper* around a caught `ImportError`. The real error is hidden behind a silent import chain:

```
_get_ai_agent()          → returns None
  get_ai_agent_class()   → catches ImportError, returns None
    require_ai_agent_class()
      from run_agent import AIAgent  → ImportError
        run_agent.py line 111:
          from agent.process_bootstrap import ...
            process_bootstrap.py line 31:
              from utils import base_url_hostname, normalize_proxy_url
                utils.py line 14:
                  import yaml  → ModuleNotFoundError ← REAL ROOT CAUSE
```

The failure is almost always a **missing transitive dependency** — `yaml`, `requests`, `httpx`, `cryptography`, or `fastapi`. The `pip install -e .` for hermes-agent only makes the agent's Python files *importable by path* — it does **not** install the agent's `pyproject.toml` dependencies into the WebUI venv because pip sees them as "already satisfied" in the parent hermes-agent venv.

**Fix:**
```bash
# 1. Re-install ALL deps from the WebUI requirements (forces local copy)
cd /d/hermes-webui
venv/Scripts/pip install --target venv/Lib/site-packages -r requirements.txt

# 2. Also install hermes-agent's own deps into the WebUI venv
cd /c/Users/<user>/AppData/Local/hermes/hermes-agent
/d/hermes-webui/venv/Scripts/pip install --ignore-installed -e .

# 3. Verify the full chain
/d/hermes-webui/venv/Scripts/python -c "import yaml, requests, httpx, openai, fastapi; from run_agent import AIAgent; print('OK')"

# 4. Kill any lingering server, then restart
```

**Note:** The server startup config shows a `python` line (the discovered agent python), but this is read-only diagnostics — `sys.executable` in the running process is what matters. If `sys.executable` is the WebUI venv's python but `from run_agent import AIAgent` still fails, it's a dependency issue, not a Python path issue.

### When "It Works in Bash but Fails in the .bat File"

Bash (git-bash) inherits the parent shell's environment including the hermes-agent venv's site-packages. Windows CMD does not. This means:
- `venv/Scripts/pip list` in bash shows all packages (from parent venv)
- `venv\Scripts\pip list` in cmd shows only packages installed *into the WebUI venv*

**Verify from CMD explicitly:**
```cmd
D:\hermes-webui\venv\Scripts\python.exe -c "import yaml; print('yaml found:', yaml.__file__)"
```

If this fails, packages are only in the parent venv, not the WebUI venv.

### Port 8787 Already in Use

**Symptom:** Server fails with "Another server is already responding on 127.0.0.1:8787"

**Fix:**
```cmd
netstat -ano | findstr 8787
taskkill /F /PID <pid>
```

Then confirm the port is free before restarting.

To change the port:
```cmd
set HERMES_WEBUI_PORT=9000
"D:\hermes-webui\venv\Scripts\python.exe" server.py
```

### ModuleNotFoundError in start.bat

**Symptom:** `ModuleNotFoundError: No module named 'yaml'` when running start.bat, but works in bash.

**Cause:** The venv inherits its parent site-packages in bash but not in Windows CMD. Packages are installed in the parent venv, not the project venv.

**Fix:** Re-install packages into the project venv's own site-packages:
```bash
venv/Scripts/pip install --target venv/Lib/site-packages -r requirements.txt
```

Always verify with the **exact same command** the .bat will run — from CMD, not bash:
```cmd
"D:\\hermes-webui\\venv\\Scripts\\python.exe" -c "import yaml"
```

### No module named 'openai'

**Symptom:** After fixing "AIAgent not available", the server starts but chat fails with: `Failed to initialize OpenAI client: No module named 'openai'`

**Cause:** `openai` is a separate dependency of the WebUI's streaming/API layer, not of `hermes-agent` itself. Fixing the `AIAgent` import chain (yaml, requests, httpx) does not automatically include `openai`.

**Fix:**
```bash
cd /d/hermes-webui
venv/Scripts/pip install openai
```

Then restart the server. Verify all dependencies together:
```bash
venv/Scripts/python -c "import yaml, requests, httpx, openai, fastapi; from run_agent import AIAgent; print('OK')"
```

**Tip:** When debugging "AIAgent not available", run the full import check that includes `openai` and `fastapi` — these are separate failure points that show up one at a time.

## Session & Workspace Paths

- Hermes sessions live in: `C:\Users\<user>\AppData\Local\hermes\webui`
- Config file: `C:\Users\<user>\AppData\Local\hermes\config.yaml`
- Default workspace: `C:\Users\<user>\workspace`
- Agent checkout: `C:\Users\<user>\AppData\Local\hermes\hermes-agent`

These are auto-detected by the WebUI on startup.
