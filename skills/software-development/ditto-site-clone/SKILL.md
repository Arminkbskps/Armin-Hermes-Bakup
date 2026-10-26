---
name: ditto-site-clone
description: Clone live sites into Next.js/Vite apps via ditto.site API.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags:
      - web
      - cloning
      - nextjs
      - vite
      - api
    related_skills:
      - github-project-discovery
---

# ditto.site Clone Skill

[ditto.site](https://github.com/ion-design/ditto.site) (MIT) turns a public URL into a runnable Next.js or Vite React app by capturing what the browser actually renders — deterministic capture-to-code, not LLM authoring. This skill drives the **hosted REST API** (`https://api.ditto.site`) and unpacks results locally.

"Clone" here means *generate a codebase from a live URL* — not `git clone`.

## When to Use

- "این سایت رو کلون کن / کدش رو برام بساز" + a public URL
- Rebuilding a landing page or design as editable Next.js/Vite code
- Don't use for: sites the user has no rights to copy, login-walled or personalized pages, phishing/impersonation

## Prerequisites

- **API key** (`dtto_live_...`), stored as a single line in `%USERPROFILE%\.ditto\api_key`. Never paste the raw key into commands, logs, or chat back-quotes. Get one at https://www.ditto.site/api-key (or `POST /v1/signup/request` with an email → verification link).
- **Node >= 20** (JSON parsing + unpacker). No `npm install` needed — the unpacker is zero-dependency.
- Local copies: repo clone at `C:\Users\Radon System\workspace\ditto.site`; skill scripts `scripts/ditto-fetch.sh` and `scripts/ditto-unpack.mjs` (unpacker copied from `packages/cli/bin/ditto.mjs`, MIT).

## Network reality on this machine (tested 2026-09)

| Path | Result |
|---|---|
| curl through the local proxy (`http_proxy=127.0.0.1:10808`) while the VPN app is running | ✅ the working path (healthz 200, POST/list OK) |
| curl direct (`--noproxy '*'`) | ❌ connection reset — api.ditto.site blocked on the direct path |
| Node fetch direct | ❌ `UND_ERR_CONNECT_TIMEOUT` |
| github.com (git clone/ls-remote) direct | ✅ works; npm works only with proxy env stripped (`env -u http_proxy -u https_proxy npm ...`) |

`scripts/ditto-fetch.sh` tries the proxy path first, then direct. If **both** fail the proxy app itself is down — curl errors say `via 127.0.0.1:10808`. Ask the user to start their VPN/proxy app and retry once; do not retry-loop. If the network is fine but the response is empty/odd, print the truncated body — it may be an API error, not transport.

## Fallback A — direct static mirror (no API, no queue)

For blocked, queue-stalled, or auth-free sites: `mirror_site.py` (D:\Hermes file\tools\mirror_site.py) fetches pages + assets directly and rewrites links into a browsable local static mirror. No LLM, no code-gen — pixel-accurate look, static (no JS logic). Works on Python 3.14 (`C:/Users/Radon System/AppData/Local/Programs/Python/Python314/python.exe`, needs `requests`+`beautifulsoup4`); the PATH python (3.11, Hermes venv) lacks them.

```
terminal(command='"C:/Users/Radon System/AppData/Local/Programs/Python/Python314/python.exe" "D:/Hermes file/tools/mirror_site.py" "https://SITE.ir/" "C:/Users/Radon System/workspace/mirrors/SITE" --max-pages 30 --timeout 15 --max-seconds 480', background=true, notify=true)
```

- Direct connection first (works for .ir sites without proxy), proxy fallback for blocked assets; global deadline via `--max-seconds`; asset-heavy homepages can eat the budget — re-run for deeper crawl (dedup via `_seen`).
- Output: `<out>/<host>/index.html` + relative-rewritten assets (CSS url(), srcset, fonts). Open via `open_preview` on the index.html file path.
- Deliverable framing: "look/edit-copy" vs ditto's "runnable Next/Vite app".

## Fallback B — alternatives

- **screenshot-to-code** (github.com/abi/screenshot-to-code, MIT, active): screenshot/URL → HTML+Tailwind/React/Vue via LLM. Self-host needs model keys (Gemini/OpenAI/Anthropic). Good when you want clean re-authored code, not a mirror.
- **Open Lovable** (github.com/firecrawl/open-lovable, MIT): URL → React app via Firecrawl+LLM+sandbox (Vercel/E2B). Needs several cloud keys.
- **HTTrack** (httrack.com): classic site copier, Windows binaries exist. Not vetted on this machine yet.

## How to Run

```
terminal(command='bash "C:/Users/Radon System/AppData/Local/hermes/skills/software-development/ditto-site-clone/scripts/ditto-fetch.sh" "https://example.com" "C:/Users/Radon System/workspace/clones/example" single tailwind next', background=true, notify=true)
```

Args: `<url> <out-dir> [mode=single] [styling=tailwind] [framework=next]`. For multi-page: `multi` (slower; re-POSTing the same URL as `multi` after a `single` clone reuses the first capture). `DITTO_POLL_MAX` caps the in-script poll loop (default 60 ticks ≈ 10 min).

**Always run the fetch in the background** — `terminal(background=true, notify=true)`. Foreground calls hard-cap around 7 min regardless of the `timeout` value and die mid-poll; background runs have no such cap and notify on exit.

### Long jobs: the watchdog pattern (cron monitor)

The hosted service runs a **shared public queue**: on 2026-09-02 all 50 jobs (ours included) sat `queued` for >30 min with zero worker events — a service-side stall, not an auth or script problem. Don't burn a session polling. Deploy `scripts/ditto-watch.sh`:

1. `cp <skill-dir>/scripts/ditto-watch.sh "$HOME/AppData/Local/hermes/scripts/"` and edit its JOB/OUT constants for the job being watched. The script stays silent while queued/running, downloads + unpacks the bundle itself on success, and only prints on failure, completion, or ~8h stall.
2. `cronjob(action='create', schedule='*/20 * * * *', monitor='ditto-watch.sh', deliver='origin,all', skills=['ditto-site-clone'], prompt=…)` — the monitor hashes the script output each tick; unchanged (silent) output = no agent run at all.
3. Cron gotchas: `monitor` must be a **filename relative to `~/.hermes/scripts/`** (absolute paths are rejected); `context_from` cannot reference the job being created in the same call (drop it); the create response may report the job as local-only (output saved, no live delivery into the session) — don't rely on the cron pushing into this chat; check `cronjob(action='list')` for the last run output.

## Quick Reference (hosted REST)

| Endpoint | Purpose |
|---|---|
| `POST /v1/clones` `{url, options{mode,styling,framework,verify}}` | start clone → `202 {jobId,status}` or inline result |
| `GET /v1/clones/:id` | poll status (`queued`/`running`/`succeeded`/`failed`) |
| `GET /v1/clones/:id/result` | file map JSON (text inline; binaries by URL) |
| `GET /v1/clones/:id/files/preview.html` | static frozen preview (inline CSS, **no JS**) |
| `GET /v1/clones/:id/bundle?format=tgz` | whole app as one archive |
| `DELETE /v1/clones/:id` | purge artifacts |

Options: `mode` single|multi, `styling` tailwind|css, `framework` next|vite.

## Procedure

1. **Key check:** `[ -f "$HOME/.ditto/api_key" ] && echo present`. If missing, ask the user for the key, then `mkdir -p ~/.ditto && printf '%s' '<KEY>' > ~/.ditto/api_key`. Never echo it back or commit it.
2. **Clone:** run `ditto-fetch.sh` (How to Run). Completion criterion: script prints `>> OK:` and the out-dir lists `package.json`, `src/`, `public/`.
3. **Preview:** open `<out>/preview.html` in `open_preview` for an instant static look; the real app is a standard npm project — `cd <out> && env -u http_proxy -u https_proxy npm install && npm run dev` (proxy env vars break npm on this machine).
4. **Hand off edits:** every generated app ships `AGENTS.md` + `ARCHITECTURE.md`; safe-to-edit surfaces are `src/app/content.ts` and `src/app/components/`.

## Pitfalls

- The script reads the key from `~/.ditto/api_key` or `$DITTO_API_KEY` — never inline it in a command.
- `preview.html` is a frozen picture of the page (no JS, no interactivity) — the working app is the unpacked project.
- Binaries in the result JSON are by-reference URLs; the unpacker fetches them with `--base-url`/`--api-key`. The bundle path avoids this entirely; `--no-fetch` = text tree only.
- Multi-page clones of large sites can exceed 10 minutes — always `background=true, notify=true`; for `queued` jobs see the watchdog pattern above.
- A `queued` status with `events: []` on `GET /v1/clones/:id/events` means the worker hasn't picked the job up yet — list `GET /v1/clones` and count other queued jobs before assuming the problem is local.
- If `POST` returns no `jobId`, print the (truncated) response — it may be a rate limit or auth error, not a network failure. A large **inline** result can also make POST slow; the script allows 240 s for it.

## Verification

- Script exits 0 with the `>> OK:` line and `package.json` exists in the out-dir.
- Then actually run the app (`npm run dev`) and confirm the page renders — a clone that doesn't build isn't done.

## Responsible Use

Only clone sites the user has the right to inspect, copy, transform, and operate. No phishing, impersonation, credential capture, or bulk third-party capture. Source: `docs/RESPONSIBLE_USE.md` in the repo.
