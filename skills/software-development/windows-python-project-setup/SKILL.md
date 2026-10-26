---
name: windows-python-project-setup
description: "Set up Python projects on Windows with venv and bat files."
tags: [windows, python, venv, batch, setup]
---

# Windows Python Project Setup

## Workflow

1. Clone or download the project to the target directory
2. Create venv in the project directory
3. Install requirements into the venv
4. Create start.bat with absolute paths (not relative)
5. **Verify imports in bash BEFORE telling the user to run the .bat file** — run the exact same command the .bat uses (`"D:\...\venv\Scripts\python.exe" -c "import yaml; from X import Y"`) and only proceed when it returns OK
6. Test by running the .bat file from Windows Explorer (not from bash)

## Creating a Working start.bat

Always use absolute paths to the venv Python executable. Never use
`call venv\Scripts\activate.bat` plus bare `python` - activation
is unreliable in batch files and can fall back to system Python.

## Pitfall: Venv-in-Venv on Windows

When you create a venv from inside an already-activated venv, the new
venv inherits the parent site-packages path. This works in bash but
fails in Windows CMD/bat files with ModuleNotFoundError.

Fix: install packages directly into venv site-packages:

```bash
venv/Scripts/pip install --target venv/Lib/site-packages -r requirements.txt
```

Prevention: deactivate first or use uv to create the venv.

## Pitfall: Editable Install in WebUI / Server Projects

When a WebUI or server project depends on the Hermes Agent package
(`hermes-agent`), it must be installed in editable mode in the
project's venv. The `sys.path` includes the agent dir automatically,
but the `from run_agent import AIAgent` import may fail with
"AIAgent not available" at runtime unless:

```bash
cd /path/to/hermes-agent
/path/to/project/venv/Scripts/pip install -e .
```

**CRITICAL:** `pip install -e .` makes the agent's Python files importable by path but does *not* install the agent's `pyproject.toml` dependencies into the project venv — pip sees them as "already satisfied" in the parent hermes-agent venv. You must also install dependencies explicitly:

```bash
/path/to/project/venv/Scripts/pip install --target venv/Lib/site-packages -r /path/to/project/requirements.txt
```

After install, restart the server. Verify with:

```bash
/path/to/project/venv/Scripts/python -c "import yaml, requests, httpx, openai; from run_agent import AIAgent; print('OK')"
```

If the import succeeds in bash but fails when the .bat file runs, the packages are only in the parent hermes-agent venv, not the project venv. Verify from Windows CMD explicitly, not just bash.

## Pitfall: Sequential Dependency Failures

A WebUI / server project that depends on `hermes-agent` has **two layers of dependencies** that fail independently and sequentially:

1. **Layer 1 — AIAgent import:** `run_agent → agent/process_bootstrap → utils → yaml`. Fix: install `pyyaml` and the agent's `pyproject.toml` deps.
2. **Layer 2 — OpenAI client:** After fixing Layer 1, the server starts but chat fails with `Failed to initialize OpenAI client: No module named 'openai'`. Fix: `pip install openai`.

Always verify ALL layers at once:
```bash
venv/Scripts/python -c "import yaml, requests, httpx, openai, fastapi; from run_agent import AIAgent; print('OK')"
```

## Pitfall: Passlib and Bcrypt >= 4.0.0 Compatibility (ValueError)

When using `passlib.context` with the `bcrypt` backend on Windows (common in FastAPI/Django templates), a `ValueError: password cannot be longer than 72 bytes` error can be thrown during context initialization or hashing (due to internal passlib testing of old wrap bugs).

Fix: Avoid using `passlib` for bcrypt hashing, and use the standard python `bcrypt` library directly:
```python
import bcrypt

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

def verify_password(plain_password: str, hashed_password: str) -> bool:
    try:
        return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))
    except Exception:
        return False
```

## Pitfall: Port Conflict on Restart

After killing a server process, the port may still be in use by a
lingering child. Always confirm the port is free before restarting:

```bash
netstat -ano | grep 8787
# or
taskkill /F /PID <pid>
```

## Verification Before Telling User

Before handing off to the user, always run the **exact same Python command**
the bat file will execute from a terminal:

```bash
"D:\...\venv\Scripts\python.exe" -c "import yaml; from api.profiles import set_request_profile; print('OK')"
```

If this works in bash but the bat file fails, check:
1. The bat file uses an absolute path to python.exe, not a bare `python`
2. Packages are installed in the venv's own site-packages, not inherited
3. Any editable installs (hermes-agent, etc.) are correctly registered

## Pitfall: `signal.SIGALRM` Does Not Exist on Windows

`signal.signal(signal.SIGALRM, …)` / `signal.alarm(…)` are POSIX-only — on
Windows the attribute doesn't exist and the script crashes with
`AttributeError` (and even on POSIX, SIGALRM only fires on the main thread).
If the same script must run on Windows AND Linux CI, use a thread-based
hard timeout instead:

```python
import concurrent.futures

with concurrent.futures.ThreadPoolExecutor(max_workers=1) as ex:
    fut = ex.submit(blocking_call, *args)
    try:
        result = fut.result(timeout=90)  # hard timeout, cross-platform
    except concurrent.futures.TimeoutError:
        raise RuntimeError("hard timeout (90s)")
```

Note: Python can't kill threads, so the worker keeps running after timeout —
safe for fire-and-forget network calls that have their own `timeout=`, not
for code needing guaranteed cancellation.

## Pitfall: Windows `CREATE_NO_WINDOW` in background Git subprocesses

When Python calls `subprocess.run(["git", ...])` on Windows, it briefly flashes an empty CMD window on the screen for every call. If the app polls Git in the background (e.g., checking workspace status or updates), this makes the app unusable as windows constantly steal focus.

Fix: Always pass `creationflags=0x08000000` (`CREATE_NO_WINDOW`) on Windows:

```python
def _windows_hide_flags() -> int:
    import sys, subprocess
    if sys.platform == "win32":
        return getattr(subprocess, "CREATE_NO_WINDOW", 0x08000000)
    return 0

subprocess.run(
    ["git", ...],
    creationflags=_windows_hide_flags(),
    # ...
)
```

## Pitfall: `&` (and other CMD metacharacters) in echo Text

In a .bat file, `&` separates commands even in plain echo text:

```bat
echo   VOID CLUB // Dark Cyber Streetwear Web & API Server
```

CMD splits the line and tries to run `API Server` as a command → `'API' is not recognized as an internal or external command` (same for `Web`). The banner prints partially and the script continues, so the noise masks the real error further down.

Fix: write "and" in banner text, or escape as `^&`. Audit any generated banner/echo lines for `&`, `|`, `<`, `>` before handing a .bat to the user.

## Pitfall: Hollow .venv (folder exists, nothing inside)

A copied/moved project can carry a `.venv` that has `python.exe` but no pip and no packages: `python -m pip` reports "No module named pip" and every import fails with ModuleNotFoundError. A start.bat that prefers the local venv keeps failing even when a healthy parent venv exists.

Don't debug a hollow venv — rebuild it:

```bash
proj/.venv/Scripts/python.exe -m pip --version   # "No module named pip" = hollow
rm -rf proj/.venv
/path/to/healthy/venv/Scripts/python.exe -m venv proj/.venv
proj/.venv/Scripts/python.exe -m pip install -r proj/requirements.txt
```

Then verify imports with the exact interpreter path the bat file uses.

## Pitfall: Pydantic EmailStr Requires email-validator

FastAPI apps crash at startup with `ImportError: email-validator is not installed, run pip install 'pydantic[email]'` when any schema uses `EmailStr`. Fix: add `email-validator` to requirements.txt — cloud builds (Railway/Nixpacks) hit the same crash at deploy time, so it must be in the manifest, not just installed locally.

## Path Patterns on Windows (Git Bash)
For bash commands use forward slash: /d/path/to/thing

## Batch & Venv Field Notes
See `references/windows-bat-and-venv-pitfalls.md` for the full transcripts: CMD metacharacters in echo banners (`&` splitting), hollow `.venv` rebuild procedure, email-validator missing in cloud builds, and the Dockerfile `COPY requirements.txt .` destination trap.

## Related References

- `references/hermes-webui-windows-setup.md` — Complete step-by-step guide for
  installing and troubleshooting Hermes WebUI on Windows, including venv setup,
  editable install for hermes-agent, start.bat creation, and common errors.
