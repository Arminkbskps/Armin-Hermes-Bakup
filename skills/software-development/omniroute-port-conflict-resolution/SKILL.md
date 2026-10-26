---
name: omniroute-port-conflict-resolution
description: Resolve port conflicts between omniroute and 9router; debug 9router OAuth refresh, relay routing, and provider keepalive.
tags: [omniroute, 9router, port-conflict, debugging]
---

# Resolving OmniRoute/9Router Port Conflicts

When running both `omniroute` and `9router` concurrently, they may try to bind to the same default port (e.g., `20128`). This causes one of the services to fail silently or fallback improperly.

## Symptoms
- Both commands (`omniroute` and `9router`) open the dashboard on the exact same `localhost:<port>`.
- One service fails to start or gets stuck in a loop.
- `EADDRINUSE` errors in the logs.

## Resolution Workflow

### 1. Identify the Source of the Port Definitions
Both packages usually define `DEFAULT_PORT` in their runtime or CLI files. (If installed globally on Windows via npm, check `%APPDATA%\\npm\\node_modules\\`).
- `9router`: check `node_modules/9router/cli.js` or `node_modules/9router/src/cli/commands/*`. On Windows, if globally installed, check `%APPDATA%\\npm\\node_modules\\9router\\cli.js` and `%APPDATA%\\npm\\node_modules\\9router\\src\\cli\\commands\\xaiVideo.js`.
- `omniroute`: check `node_modules/omniroute/src/lib/runtime/ports.ts`, `.env` overrides, or `node_modules/omniroute/bin/cli/*`.

### 2. Modify the Port in One Package
To prevent conflicts, change the `DEFAULT_PORT` in one of the packages (e.g., change `omniroute` from `20128` to `20129`).
- Use the `patch` tool to carefully replace the `DEFAULT_PORT` constant.

```javascript
// Example modification in omniroute/src/lib/runtime/ports.ts
- const DEFAULT_PORT = 20128;
+ const DEFAULT_PORT = 20129;
```

### 3. Rebuild (If Applicable)
If the project requires a build step (e.g., TypeScript or Next.js), you MUST rebuild the project after patching the source files.
- For `omniroute`, run `npm run build` or the specific build script used by the project.
- **Note:** If `cross-env` or other global tools are missing, use `npx` to run them locally (e.g., `npx cross-env ...`).

### 4. Restart the Services
After patching (and rebuilding), restart both services in the background and verify they are listening on different ports.

```bash
# Example verification
curl -I http://localhost:20128
curl -I http://localhost:20129
```

### 5. Update Client/Consumer Configurations
If you change the port of a local AI router (like 9router), you **must** update the configuration of any clients (like Hermes Agent) consuming that API.
- Update `base_url` to point to the new port (e.g., `http://localhost:20129/v1`).
- **Crucial:** If the client uses environment variables derived from the URL for API keys (e.g., `HERMES_CUSTOM_LOCALHOST_20128_API_KEY`), you must ALSO update the `key_env` setting in the client config to match the new port (`HERMES_CUSTOM_LOCALHOST_20129_API_KEY`) **AND** ensure that new environment variable is actually set in the environment. Mismatched `key_env` names after a port change lead to 401 Unauthorized or Connection errors. Alternatively, consolidate multiple client configs to use a single, port-agnostic variable (like `HERMES_CUSTOM_9ROUTER_API_KEY`).

## Provider Routing & Proxy Relays
For detailed notes on 9router internal SQLite database schema (`data.sqlite`), native vs custom provider collisions, bypassing OpenCode 403 FreeTier gates, resolving Cline 401/429 multi-account traps, multi-user credential sanitization and provider-shell retention, sandbox migration patterns, and configuring Vercel/Cloudflare relays, see [references/9router-provider-routing.md](references/9router-provider-routing.md).
For "Token expired and refresh failed" on OAuth providers (Cline, Claude, Gemini-CLI...): dead local proxy env is the #1 cause — see [references/9router-oauth-refresh.md](references/9router-oauth-refresh.md).
To onboard a key extracted from a desktop app (VS Code extension secret stores, Electron safeStorage/DPAPI) as a custom OpenAI-compatible connection, see the companion skill `local-credential-extraction` (has the decrypt script + a `references/ahefi-provider.md` case study of a working `https://ahefi.com/v1` provider: valid key + `/v1/models` 200 while chat returned 502 `upstream_error` = provider-side outage, not a config fault).

## Pitfalls
- **Compiled vs. Source:** Patching `.ts` files inside `src/` does nothing if the runtime executes `.js` files from a `dist/` or `.build/` folder. Always check if a build step is required or if you should patch the compiled files directly for a quick fix.
- **Rebuild Failures:** Complex build scripts (like `build-next-isolated.mjs`) may fail if dependencies or scripts are missing/moved. In such cases, prefer patching the compiled output (`dist/`) directly to verify the fix before wrestling with the build system.
- **Minified Next.js chunks need a location recipe, not a rebuild:** 9router ships only compiled `.next-cli-build/server/chunks/*.js` (no source for the test path). Don't reach for source/build — `grep -rl <term>` to find the chunk, then `node --input-type=module` + `JSON.stringify(slice)` for unicode-safe Windows output.
- **Cap minified-chunk output:** full-chunk dumps flood context and can surface as empty replies. Always slice (`head -n`, small windows, short `JSON.stringify` snippets) and keep each tool result compact.
- **Keep every tool result compact.** Very long outputs (full-chunk dumps, whole
  tables, multi-KB slices) can surface as EMPTY assistant replies — the user
  experiences this as the agent "disconnecting mid-task". Always slice
  (`head -n`, small windows, `print(x[:N])`), prefer counts/summaries over full
  rows, and split big investigations across several small calls.
- **9router tray-mode auto-respawns:** killing the PID listening on 20128 is NOT enough — the parent `cli.js` (tray mode) immediately respawns `custom-server.js` with a new PID. Find the parent via `wmic process where "ProcessId=<pid>" get ParentProcessId,CommandLine` and stop that (or quit the tray app) before a patched restart; otherwise the old code keeps serving. A respawned child DOES pick up disk patches to `.next-cli-build` chunks (plain require, no rebuild step).
- **Dashboard Test APIs need browser-session auth:** `POST /api/providers/validate` and `test-batch` return `401 Unauthorized` with or without the 9router API key — the Test button can't be driven headlessly that way. Verify with a real chat call instead, or click Test in the dashboard.
- **Windows Registry Proxy Leak (`WinError 10061` in Python `urllib`):** On Windows, `urllib.request` loads proxy settings directly from the Windows Registry (`Software\Microsoft\Windows\CurrentVersion\Internet Settings\ProxyServer`, e.g. `127.0.0.1:10808`). Simply unsetting `os.environ` proxy variables is NOT sufficient — if 10808 is closed, local connections to `127.0.0.1:20128` or `127.0.0.1:8091` fail with `ConnectionRefusedError: [WinError 10061]`. You MUST install an empty ProxyHandler:
  ```python
  urllib.request.install_opener(urllib.request.build_opener(urllib.request.ProxyHandler({})))
  ```
- **9router Upgrades (e.g. v0.5.91) Resetting Provider Relays:** Updating 9router can reset `providerConnections` for OpenCode back to Cloudflare workers (`2231fa54-b792-4102-a1e7-41b72efdb265`, blocked in Iran) or reset combo definitions. Always ensure `opencode` is locked to Vercel Relay (`cbb8ae02-c43e-4087-a095-f1fa9f096282`) and `combos.zen` / `combos.newModels` remain strictly locked to `["oc/muse-spark-1.3-contributor-free"]`.
- **"Key invalid" can be the upstream, not the key:** before tearing down a custom OpenAI-compatible connection, prove the key independently — `GET <base>/v1/models` with `Bearer <key>` returning 200 means auth is fine. If chat then fails 502 `upstream_error` across EVERY model (stream/non-stream, extra headers included), that's a provider-side outage; confirm via the provider's own logs/usage API if it has one, and re-test later instead of reconfiguring. A SPA returning HTML with HTTP 200 on an unmatched path means the endpoint doesn't exist — read the client app's JS for the URL it really calls.

## Watchdog: opencode/zen keepalive (`D:\Hermes file\opencode-proxy\watch_router.py`)

- Scheduled task `9router-watchdog` runs it every 5 min. Use the FULL python path
  in `schtasks /tr` (bare `python` fails with Last Result `-2147024894` — not on
  PATH in task context), and use `pythonw.exe` instead of `python.exe` so no
  console window flashes every run / at logon.
- Each run: 9router `/api/health` (restart via `9router.cmd --no-browser` if down)
  → relay `/zen/v1/models` probe → real `zen` chat ping → quota usage report
  (read-only) → cline OAuth refresh via relay (10-min lead, `workos:`
  prefix enforced, 400-revoked → `isActive=0`).
- `retry_shim.py` (OpenAI-compatible, `127.0.0.1:8091` → 9router `20128`):
  absorbs transient 503 `service_overloaded`/429/502/504 and empty replies on the
  SAME single model (`zen` = only `oc/muse-spark-1.3-contributor-free`, user vetoed
  any fallback models/combos). Bounded retries: max 3 attempts with 2s linear backoff
  (prevents 200+ second hangs like `waiting on newModels`), auto-injects master 9router
  API key from `data.sqlite` to prevent 401s, installs empty `ProxyHandler({})`,
  and supports live SSE stream passthrough. Auto-started hidden via `Startup\retry_shim.vbs`
  (pythonw). The `zen-stable` multi-model fallback combo was built then REMOVED per user
  veto — never recreate.
- zen ping uses `max_tokens=64` (upstream rejects `<16` with 400) and treats a
  valid `chat.completion` structure as healthy — free models sometimes return
  empty/verbose content (a `200` with `''` content was observed), connectivity
  is what the watchdog guards, not model obedience.
- usage reporting (`quota_rotate`, read-only): the `zen` combo is pinned to ONE
  model (`oc/muse-spark-1.3-contributor-free` — do NOT expand it; user vetoed
  expansion). Each run sums lifetime `usageHistory` opencode tokens and logs the
  currently-selected relay, e.g.
  `quota: total=539953717 pool=vercel (locked, no auto-switch)` — it NEVER
  writes `proxyPoolId`.
- HISTORY — relay auto-flip REMOVED by user veto: an earlier version flipped the
  opencode relay `vercel ↔ cloudflare` every 250k tokens (same model, new egress
  identity). The user saw opencode jump to cloudflare on its own and ordered the
  relay to stay EXACTLY as selected in the dashboard. Do NOT reintroduce
  auto-switching; if quota-bypass is ever revisited, ask first. Leftovers:
  `QUOTA_TOKENS`/`VERCEL_POOL`/`CF_POOL`/`QUOTA_STATE` constants and
  `quota_state.json` in `watch_router.py` are dormant.
- Log: `watch_router.log` (last 200 lines). RESULT line is `ALL-GREEN` or
  `NEEDS-ATTENTION`.
- usageHistory note: opencode has no OAuth/session to expire (`accessToken`
  EMPTY, `noauth`) — its disconnects are network-side (relay/WAF/geo), never
  `Token expired`. Zero non-ok rows in `usageHistory` = upstream healthy.
  Mid-chat drops while running SEVERAL PARALLEL TASKS on one account are 429
  rate-limits, not disconnects — all tasks hit the combo's FIRST model at once.
  The quota rotation above is the mitigation (over-quota model sinks to the end
  of the order); do NOT "expand" the combo as a first resort.

## Global Installation & Path Troubleshooting (Windows)

On Windows, upgrading or running `9router` or `omniroute` can fail or run outdated versions due to:
1. **Multiple Node/npm Paths:** Windows `PATH` might contain both a global NVM symlink (`C:\nvm4w\nodejs`), user profile npm folder (`%APPDATA%\Roaming\npm`), and application-specific Node directories (like Hermes' built-in `AppData\Local\hermes\node`).
2. **File Locking (EACCES / Busy errors):** If `9router` or `omniroute` is currently running as a background service or CLI node process, attempting to update or delete the files will fail with `The process cannot access the file ... because it is being used by another process`.

### Step-by-Step Resolution:
1. **Identify Executable Paths:**
   Run `where.exe node`, `where.exe npm`, and `where.exe 9router` (or `omniroute`) to see the resolution priority.
2. **Check for Running Instances (File Lockers):**
   Search for Node processes running the target CLI:
   ```powershell
   Get-CimInstance Win32_Process -Filter "name='node.exe'" | Select-Object CommandLine, ProcessId
   ```
3. **Terminate Conflicting Processes:**
   If a background process is running the CLI (e.g. `.../node_modules/9router/cli.js`), terminate it:
   ```powershell
   Stop-Process -Id <ProcessId> -Force
   ```
4. **Remove Conflicting/Stray Shims:**
   If there are stray global shims in AppData Roaming that override NVM or Hermes Node:
   ```powershell
   Remove-Item 'C:\Users\Radon System\AppData\Roaming\npm\9router*' -Force
   ```
5. **Re-install / Upgrade:**
   Run `npm install -g 9router@latest --prefer-online` or target the specific Node environment prefix needed.