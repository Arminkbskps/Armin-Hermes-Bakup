---
name: site-mirror
description: Mirror a live site into a browsable offline static copy.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - web
      - mirror
      - scraping
      - offline
    related_skills:
      - ditto-site-clone
---

# Site Mirror Skill

Download a website into a **browsable offline static copy** — pages + assets with all links rewritten to relative paths. No queue, no LLM, no API key. Tool: `D:\Hermes file\tools\mirror_site.py` (requests + BeautifulSoup).

## When to Use

- User wants a working local copy of a public site (look, images, fonts, navigation)
- ditto.site clone is blocked/stalled (hosted queue) and a runnable app isn't needed — a faithful static copy is enough
- Don't use for: login-walled sites, generating editable framework code (that's ditto/screenshot-to-code territory)

## Prerequisites

- Python 3.14 (`C:/Users/Radon System/AppData/Local/Programs/Python/Python314/python.exe`) with `requests` + `beautifulsoup4` — the PATH python (3.11 Hermes venv) lacks them.

## How to Run

```
terminal(command='"C:/Users/Radon System/AppData/Local/Programs/Python/Python314/python.exe" "D:/Hermes file/tools/mirror_site.py" "https://SITE.ir/" "C:/Users/Radon System/workspace/mirrors/SITE" --max-pages 30 --timeout 25 --max-seconds 900', background=true, notify=true)
```

## Procedure

1. **Run in background** (command above). Completion criterion: `== MIRROR DONE` with `pending_unfetched=0`.
2. **If `pending_unfetched > 0`**: just re-run the same command with a bigger `--max-seconds` (asset downloads **skip files already on disk**, so a re-run continues where it stopped).
3. **Verify**: open `<out>/<host>/index.html` via `open_preview`; check images/fonts render and header/nav works.

## Pitfalls

- **Two-phase design**: phase 1 crawls pages first, phase 2 downloads assets. Asset-heavy homepages (e.g. 7wears.ir: 200+ assets) can eat the whole budget → `pending_unfetched > 0` is expected; re-run to continue.
- **Non-ASCII paths** (Persian filenames) get an md5 suffix to avoid collisions after sanitizing.
- **WordPress/Elementor themes with entry animations** (theme "Essentials"/pix-*): animations stay hidden because the theme triggers them via its page-transition handler which never fires offline. The script injects a `data-mirror-fix` fallback `<script>` before `</body>` that calls `pix_animation_display()` after load — do not remove it.
- 6 download threads; per-host direct/proxy memory — .ir sites usually work **direct** (no proxy needed).

## Verification

- `open_preview` the index.html: images render, menu works, entry animations play once on load.
- Sample-check: `grep -c "data-mirror-fix" <page>.html` → ≥1 on animated pages.

## Related

- For a **runnable Next.js/Vite app** instead of a static mirror, use the `ditto-site-clone` skill.
