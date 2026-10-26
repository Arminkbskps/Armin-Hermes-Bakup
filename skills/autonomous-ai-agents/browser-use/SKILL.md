---
name: browser-use
description: Drive a real browser via CDP for scraping and automation.
version: 0.1.0
author: Armin (Armin13891219A), Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [browser, automation, scraping, cdp]
    related_skills: [computer-use]
---

# Browser Use Skill

Direct control of a real Chrome/Chromium browser over CDP through the `browser-use` CLI/harness (installed via uv). Handles interaction (click/type/upload/download), JS-rendered and bot-protected pages, logged-in sessions, and screenshots. The verbatim official skill text lives in `references/official-skill.md` — read it for cloud browsers, recordings/videos, and per-mechanic guides (dropdowns, iframes, shadow-dom, uploads, …).

## When to Use

- Task needs real interaction: click, type, navigate, upload, download, log into the user's session.
- Page is JS-heavy, behind a bot wall, or a plain fetch already failed or returned a shell page — escalate to the browser, don't start there.
- **Don't use for:** reading public static info (`web_extract`/`curl` first); desktop-app automation (`computer-use`).

## Prerequisites

- `browser-use` installed via uv. On this Windows machine it is NOT on the MSYS PATH. Resolve the exe once per session:
  ```bash
  export BU=$(ls /c/Users/*/AppData/Local/uv/cache/archive-v0/*/Scripts/browser-use.exe 2>/dev/null | head -1); "$BU" --version
  ```
  If empty, the uv cache hash dir changed after an upgrade — the glob re-finds it. Installed here as of 2026-09: `browser-use 0.13.8` + `browser-harness 0.1.9` (its `--version` prints the harness version).
- Chrome/Chromium reachable. If the daemon can't connect it opens `chrome://inspect/#remote-debugging`; on macOS permission prompts use `browser-use mac-approve`.

## How to Run (Hermes)

- **Preferred: the `browser_exec` tool.** Hermes runs this exact same harness — helpers are pre-imported, the daemon auto-starts, and each call's first line should be a one-line comment (the UI shows it as a step label). Python vars do NOT persist between calls; files in the returned `workspace` dir do.
- **Terminal fallback** (diagnostics, auth, recordings, or standalone scripts) via heredoc:
  ```bash
  "$BU" <<'PY'
  new_tab("https://example.com")
  print(page_info())
  PY
  ```
- Diagnostics: `terminal(command="$BU --doctor")`. Cloud auth: `"$BU" auth login`. Update: `"$BU" --update -y`.

## Quick Reference (pre-imported helpers)

`new_tab(url)` (first navigation), `goto_url(url)`, `wait_for_load()`, `page_info()`, `js(expr)` (wrap IIFEs: `js('(() => {...})()')`), `fill_input(sel, text)`, `click_at_xy(x, y)`, `capture_screenshot()`, `cdp('Domain.method', **kw)`, `ensure_real_tab()`. Task-specific helpers go in `$BH_AGENT_WORKSPACE/agent_helpers.py`.

## Procedure

1. **Text-first.** `page_info()` for state; `cdp("Accessibility.getFullAXTree")["nodes"]` for every element's role/name/`backendDOMNodeId` — filter in Python before printing (thousands of nodes). Coordinates: `q = cdp("DOM.getBoxModel", backendNodeId=n)["model"]["content"]; x, y = sum(q[0::2])/4, sum(q[1::2])/4`.
2. **Click loop:** AX node → box center → `click_at_xy(x, y)` → verify with a targeted `js(...)`/`page_info()` check. Fall back to raw HTML via `js(...)` only when the AX tree lacks the element; screenshot when layout/imagery matters.
3. **Multi-item tasks:** append batches to a JSON/CSV file in the workspace, then aggregate in Python and verify the collected count against what was asked.
4. **Login walls: stop and ask the user.** Never guess credentials. Exception: SSO already signed into Chrome; still stop for passwords/MFA/consent.
5. Completion criterion: the final `page_info()`/extraction output shows the expected URL/title/data — not intent.

## Pitfalls (this machine)

- `$LOCALAPPDATA` backslash paths break bash globs — use the `/c/Users/...` form above.
- Direct GitHub/PyPI/CDN fetches frequently fail with SSL/timeout on this network; driving real Chrome (which uses the user's working browser stack) is the standard workaround — that is often exactly why this skill is loaded.
- Heredocs must be quoted (`<<'PY'`) so bash doesn't expand `$` inside Python code.
- `new_tab()`/`switch_tab()` attach without changing Chrome's visible tab; background CDP input works — call `activate_tab` only if the user asks or rendering pauses.
- Daemon stale after a version update: `"$BU" --reload`.
- Optional domain skills off by default; set `BH_DOMAIN_SKILLS=1` and read `$BH_AGENT_WORKSPACE/domain-skills/<site>/` for site-specific tasks.

## Verification

- `print(page_info())` returns the expected URL/title after the flow.
- If a screenshot was captured, the printed file path exists on disk.
- For extracted data, the workspace JSON/CSV row count matches the requested item count.
