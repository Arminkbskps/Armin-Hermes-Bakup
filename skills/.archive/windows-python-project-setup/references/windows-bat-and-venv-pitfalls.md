# Windows Batch (.bat) Authoring Pitfalls

Hard-won from the VOID CLUB start.bat failures (Aug 2026 session).

## CMD metacharacters in echo/banner text

In a .bat file, `&`, `|`, `<`, `>` are command separators EVEN inside plain `echo` text:

```bat
echo   VOID CLUB // Dark Cyber Streetwear Web & API Server
```

CMD splits this and tries to execute `API Server` as a command:
- `'Web' is not recognized as an internal or external command`
- `'API' is not recognized as an internal or external command`

The banner prints partially and the script continues, so the noise masks real errors further down.

**Fix:** write "and" in banner text, or escape as `^&`. Audit any generated banner/echo lines for `&`, `|`, `<`, `>` before handing a .bat to the user.

## Hollow .venv (folder exists, nothing inside)

A copied/moved project can carry a `.venv` that has `python.exe` but no pip and no packages:
- `python -m pip` reports "No module named pip"
- every import fails with ModuleNotFoundError (e.g. `import uvicorn` in run_server.py)
- a start.bat that prefers the local venv keeps failing even when a healthy parent venv exists

**Don't debug a hollow venv — rebuild it:**

```bash
proj/.venv/Scripts/python.exe -m pip --version   # "No module named pip" = hollow
rm -rf proj/.venv
/path/to/healthy/venv/Scripts/python.exe -m venv proj/.venv
proj/.venv/Scripts/python.exe -m pip install -r proj/requirements.txt
```

Then verify imports with the exact interpreter path the bat file uses:
```bash
proj/.venv/Scripts/python.exe -c "import uvicorn, fastapi, sqlalchemy, PIL; print('OK')"
```

## Pydantic EmailStr requires email-validator (also bites cloud builds)

FastAPI apps crash at startup with `ImportError: email-validator is not installed, run pip install 'pydantic[email]'` when any schema uses `EmailStr`.

**Fix:** add `email-validator` to requirements.txt. Cloud builds (Railway/Nixpacks/Docker) hit the SAME crash at deploy time with a confusing "Application failed to respond" — gunicorn boots, workers spawn, then die on the first import of the schemas module. It must be in the requirements manifest, not just installed locally.

Related Dockerfile pitfall: `COPY backend/requirements.txt .` copies INTO a `backend/` dir inside the image while `pip install -r requirements.txt` reads from the workdir root — use an explicit destination: `COPY backend/requirements.txt ./requirements.txt`.
