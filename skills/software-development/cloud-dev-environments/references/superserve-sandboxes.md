# Superserve Sandbox Architecture & Cloudflare Worker Bridging

## Architecture
- **Control Plane (`https://api.superserve.ai`)**: Handles sandbox lifecycle (create, get, list, pause, resume, activate, preview-ports, secrets). Authenticated via `X-API-Key: ss_live_...`.
  - **Path Invariant**: Endpoints do NOT use a `/v1/` prefix. They are routed directly as `/sandboxes`, `/sandboxes/<id>`, and `/sandboxes/<id>/activate`.
- **Data Plane (`https://sandbox.superserve.ai`)**: Shared multi-tenant host for sync execution (`POST /exec`), streaming execution (`POST /exec/stream`), and filesystem operations (`GET/POST/DELETE /files`). Requires:
  - Header `X-Superserve-Sandbox-Id: <sandbox_id>`
  - Header `X-Access-Token: <token>` (64-character token from `/activate` or `/resume`)
- **Per-Sandbox Direct Host (`https://boxd-<sandbox_id>.sandbox.superserve.ai`)**: WebSocket endpoint (`/exec/connect`) for interactive terminal sessions (`commands.spawn`).

## Geo-Blocking Bypass via Cloudflare Worker
Superserve's edge infrastructure blocks direct requests from restricted regions (e.g. Iran) with `HTTP 403 Forbidden`.
Deploy a minimal Cloudflare Worker proxy (`superserve-proxy`) to bridge requests:
- Route `/api/*` -> `https://api.superserve.ai/*` (strip `/api` prefix so `/api/sandboxes` -> `/sandboxes`)
- Route `/dp/*` -> `https://sandbox.superserve.ai/*` (map `X-Superserve-Sandbox-Id` to `Host: <id>.sandbox.superserve.ai`)
- Route `/bot*` -> `https://api.telegram.org/bot*`

### Cloudflare Worker Header & Body Pitfalls
1. **Never Forward Incoming `Host` Header**: When proxying to an upstream on Cloudflare (`sandbox.superserve.ai`) or external APIs (such as `api.telegram.org`), forwarding the client's `Host: <worker-domain>` causes Cloudflare edge routing or upstream WAFs to fail with `502 Bad Gateway` or `404 Not Found: {"ok":false,"error_code":404}`. Always delete `host` or explicitly override it to the target domain (`headers.set("Host", "api.telegram.org")`).
2. **Body Buffering**: Avoid piping raw `request.body` streams directly without `{ duplex: "half" }`. Buffer the request body with `await request.arrayBuffer()` to prevent runtime fetch stream errors.

## Zero-Downtime Preemptive Failover & Edge Health Watcher
Trial cloud environments (e.g. Superserve $5 credit containers) run for a bounded duration (approx. 5–5.5 days on 2 vCPU / 2GB RAM). Because billing/snapshot endpoints may not be directly exposed via API, failover must be handled via edge monitoring:

### 1. Continuous State Synchronization
Run a lightweight background loop inside the primary sandbox to snapshot live state to Cloudflare KV every 30 minutes.
**CRUCIAL**: Explicitly include `.env` in the archive (`.hermes/.env` or `.hermes/profiles/<profile>/.env`). Without `.env`, `TELEGRAM_BOT_TOKEN` and `TELEGRAM_ALLOWED_USERS` will be absent upon failover:
```bash
cat << 'EOF' > /home/user/sync_backup.sh
#!/bin/bash
while true; do
  tar -czf /tmp/backup.tar.gz -C /home/user .9router/db/data.sqlite .hermes/config.yaml .hermes/.env .hermes/pairing .hermes/state.db 2>/dev/null
  curl -s -X PUT --data-binary @/tmp/backup.tar.gz https://<worker-domain>/files/backup.tar.gz >/dev/null 2>&1
  sleep 1800
done
EOF
chmod +x /home/user/sync_backup.sh
nohup /home/user/sync_backup.sh >/dev/null 2>&1 &
```

### 2. Standby Container Pre-Warming
Before failover is needed, provision the standby sandbox with the spare API key:
1. Symlink system binaries (`node`, `npm`, `python3`, `hermes`).
2. Install dependencies globally (`npm install -g 9router@0.5.81`, `cloudflared`).
3. Apply runtime patches (e.g. 9router FreeTier chunk 318 patch).
4. Pre-extract complete skill sets (using ephemeral in-tunnel transfer for >25MB sets).
5. Stage a one-command activation script (`/home/user/start_failover.sh`) that pulls the latest KV backup, unpacks it into `/home/user`, and spawns 9router, cloudflared, and `hermes gateway run`.

### 3. Edge Health Watcher (Cloudflare Cron Triggers)
Configure a 5-minute cron trigger in `wrangler.toml`:
```toml
[triggers]
crons = ["*/5 * * * *"]
```
In `worker.js`, implement `scheduled(event, env, ctx)`:
- Query Superserve API `/sandboxes/<primary_id>` and ping the Cloudflare Tunnel URL.
- Track consecutive failures in KV (`fails_<user>`).
- Upon 3 consecutive failures (timeout or credit shutdown), execute automatic zero-touch failover:
  1. Call `POST /sandboxes/<standby_id>/activate` with the standby API key to wake the standby sandbox and obtain `access_token`.
  2. Directly invoke `POST /exec` on the data plane with `Host: <standby_id>.sandbox.superserve.ai` and `X-Access-Token` to trigger `/home/user/start_failover.sh`.
  3. Send an alert to the Telegram admin via `api.telegram.org/bot<token>/sendMessage`.
  4. Mark failover status in KV to prevent duplicate migrations.
- **Second-level queue fallback (multi-key chains, verified live Sep 2026)**: when holding 2+ spare keys per user, pre-warm a second standby ("queue" sandbox) with the same stack (node links, 9router + chunk-318 patch, cloudflared, backup restore, skills, `start_failover.sh`). Store `queueId`/`queueKey` per user in the Worker config. In `triggerFailover`, try standby first; if `activate` is not `ok` or returns no `access_token`, automatically retry against the queue sandbox, run the same `failoverScript` via `/dp/exec` with `Host: <queue_id>.sandbox.superserve.ai`, and record the used level in KV (`failover_<user>_target` = `{level: "standby"|"queue", id, at}`). Surface `queueId`, live `queue: {status, ageDays, estRemainingDays}` and `failoverTarget` in `/health` so the operator sees chain depth at a glance. Notify the admin which level served the failover.
- Telegram's built-in polling message queue preserves all incoming messages during the brief handover window, guaranteeing zero lost user messages. Expect one transient `telegram.error.Conflict: ... terminated by other getUpdates request` in the new gateway log right after failover — the retired instance's long-poll overlaps briefly; it clears on its own once the old process exits (`polling confirmed healthy` follows). Not a token problem, don't chase it.
- **Paused ≠ dead: probe `paused` sandboxes that lack your own pause marker (verified live Sep 2026).** A credit-dead box reports the same `"paused"` status as platform sleep, so a watcher whose paused branch only peek-wakes will wait forever on a dead box — this exact gap missed a real billing death. Each tick, when `GET /sandboxes/<id>` → `paused` AND KV `paused_<user>` is empty, send a probe `POST /sandboxes/<id>/activate`: `402` containing `billing_ineligible` → dead (increment `fails_<user>`, fail over at 3 consecutive); `2xx` → alive platform sleep (immediately `POST /pause` again so the probe doesn't burn credit, and write the `paused_<user>` marker so later ticks skip the probe and go straight to peek-wake); anything else → unknown, don't count. Verify the detector with a temporary canary route (e.g. `/canary-billing-dead` running the probe against a known-dead sandbox ID and returning `{expected:{dead:true}, got, pass}`), confirm `pass:true` live, then delete the route and redeploy — don't leave dead-box credentials in the Worker source.

### 4. Idle Auto-Pause + Telegram Peek-Wake (Credit Saver, Verified Live Sep 2026)

When billing is wall-clock or uptime-based, pause idle sandboxes instead of burning credit:

1. **Heartbeat reporter on each primary** (every 5 min → KV `hb_<user>`): last Telegram `inbound message` timestamp from `gateway.log` + `max(timestamp)` from 9router `usageHistory`. Small JSON, one PUT.
2. **Watcher cron (5 min)** computes idle minutes from the heartbeat. If idle ≥ threshold (e.g. 180 min) and status is `active` → `POST /pause`, store `{at, reason}` in KV `paused_<user>`, then **seed the Telegram offset**: `getUpdates?timeout=0`, save `max(update_id)+1` to KV `tg_offset_<user>`. Notify the admin.
3. **Paused branch never counts as failure.** Each tick, peek `getUpdates` with the stored offset as lower bound — **read-only: never advance the offset server-side** (Telegram only confirms on a HIGHER offset, so the gateway's own long-poll still receives everything after resume). First new message → `POST /activate` (wakes with processes intact — 9router, gateway, tunnels all survive), clear `paused_<user>`, re-seed offset, notify.
4. **Bot tokens in KV, not in the Worker source**: upload each profile's `TELEGRAM_BOT_TOKEN` once via `grep TELEGRAM_BOT_TOKEN <profile>/.env | cut -d= -f2 | tr -d ' \r\n' | curl -s -X PUT --data-binary @- <worker>/files/tg_token_<user>` (note: direct `urllib` PUT from the sandbox got `403` — piping through `curl --data-binary @-` worked; KV probe from an unrestricted host succeeded, so prefer sandbox-side `curl` for binary PUTs).
5. **Manual overrides**: `/pause/<user>` and `/resume/<user>` endpoints on the Worker for instant credit-saving or wake without waiting for the cron tick.
6. **`/health` usage report**: per server include `status`, `ageDays` (from `created_at`), `estRemainingDays` (`MAX_LIFETIME_DAYS − ageDays`, e.g. 5.5-day assumption on 2 vCPU/2GB), `lastActivity` (heartbeat JSON), `idleMinutes`, `pausedByWatcher`, `consecutiveFails`, `failoverCompleted`.
8. **Triage recipe when `/health` shows `paused` (marker check before panic):** `GET /diag/<user>` returns `{apiStatus, ownPause, probe}`. If `ownPause: true` → credit-saver sleep, just `POST /resume/<user>` (200 = awake, processes intact from snapshot). If `ownPause: false` → the billing probe runs inline: `dead:true` (activate → 402) = billing death → fail over immediately; `alive` = platform sleep (watcher re-pauses + marks it, later ticks skip the probe). After ANY resume, Quick Tunnel hostnames rotate — re-read the URL from the tunnel log, verify `GET <new-url>/api/health → 200` directly, then update `tunnelUrl` in `worker.js` and redeploy before trusting the `tunnelHealthy` flag.
7. **Test before trusting**: verify `POST /pause → 204`, `GET /sandboxes → "paused"`, `POST /resume (or /activate) → 200 + active`, and `ps aux` shows 9router/gateway/heartbeat still running post-resume. Tested end-to-end on a live sandbox: resume restored all processes from the memory snapshot.

### 5. Multi-User Sandbox Isolation Verification
When hosting multiple users or separating admin from guest accounts:
1. **SQLite Database Audit**: Check `providerConnections` and `combos` tables in `.9router/db/data.sqlite`. Ensure guest instances contain only permitted combos and no personal OAuth accounts.
2. **Environment & Pairing Scan**: Run `grep -rn "<admin_telegram_id>" /home/user/.hermes /home/user/.9router` on the guest container to confirm zero credential leakage.
3. **Dedicated Profile Paths**: Guest sessions run under isolated profiles (`hermes -p <profile> gateway run`) with isolated `.env`, `pairing/`, and `skills/` directories.

## Lifecycle & Pausing Gotchas
- **Idle Sleep**: Superserve automatically pauses inactive sandboxes (`status: "paused"`). Attempting data plane operations on a paused sandbox fails with connection drops or 502.
- **Checking Status Before Pause/Resume**: `GET /api/sandboxes/<id>` returns `status` (`"paused"` or `"active"`). `POST /pause` returns `204 No Content` (empty body — do not `json.loads()`). If already paused, `POST /pause` returns `409 Conflict: Sandbox is not in a valid state for this operation`.
- **Waking Up**: Before sending commands, check status. If paused or on authorization failure, call:
  `POST /api/sandboxes/<id>/activate` or `POST /api/sandboxes/<id>/resume`.
  Extract `data.access_token` and save it to `.token`.
- **Tokens Survive Explicit Pause/Resume (verified live, Sep 2026)**:
  After explicit `POST /pause` → `POST /resume` (or `/activate`), Superserve returns the SAME 64-char `access_token` and the pre-pause token keeps working on `/dp/exec` — do NOT assume invalidation or discard cached tokens on resume. Keep the `401/403 → re-activate` loop in bridge scripts (`exec.js`) as defense (auto-sleep pauses may still rotate tokens), but treat it as fallback, not the expected path. Match on status code, not body strings like `body.includes("expired")`.
- **Paused Sandbox Exec Returns 503, Not 502**:
  `POST /dp/exec` against a paused sandbox returns `HTTP 503` with body `sandbox is paused`. That means "wake it with `POST /activate`", NOT an upstream outage — don't route it into the 502-outage diagnosis or the failover counter.
- **402 `billing_ineligible` = True Credit Death (verified live, Sep 2026)**:
  Exhausted $5 credit makes BOTH `POST /activate` and `POST /resume` return `HTTP 402 {"error":{"code":"billing_ineligible","message":"Sandbox usage is unavailable until billing is active"}}`. Terminal — the box never wakes and `/dp/exec` stays `503`. Trap: `GET /sandboxes/<id>` still returns `200` with a fresh-looking 64-char `access_token` on a dead box, so never trust GET alone; the verdict comes from activate/resume status codes. On 402 → fail over immediately, no retry loop.
- **Quick Tunnel URLs Rotate — Re-read After Every Relaunch**:
  `cloudflared tunnel --url http://127.0.0.1:<port>` mints a NEW `*.trycloudflare.com` hostname on every (re)start, including after sandbox pause/resume. A stale hostname stops resolving (tunnel check errors) while the local service is fine (`/api/health` → `{"ok":true}`). After any relaunch: `grep -o 'https://[-a-z0-9]*\.trycloudflare\.com' <tunnel.log> | head -1`, update `SERVERS[<user>].tunnelUrl` in `worker.js`, redeploy, and re-check `/health`.
- **Backup Tars Carry Data, Not the Loop Scripts**:
  `sync_backup.sh` archives only data paths (sqlite, config, `.env`, pairing, state.db) — NOT itself, `heartbeat.sh`, or `sync_models.sh`. A freshly restored standby therefore has data but no maintenance loops. After every failover, reinstall the loops (copy from the surviving sibling server or KV `/files/`) and `nohup` them, then confirm KV `hb_<user>` updates within ~5 min. Nor compiled-code patches: the 9router chunk-318 FreeTier patch lives under `node_modules/.../app/.next-cli-build/server/chunks/` on disk, so a data restore never carries it — a freshly provisioned box must be (re-)patched and 9router restarted even with a perfect backup. Audit after every restore: `grep -c 'w(b,!0),b.tool_choice="auto"' <318.js>` must be ≥1 and `grep -c 'Array.isArray(b.tools)&&0!==b.tools.length||w(b,!0)'` must be 0, then confirm with a live chat that carries agent `tools` (the exact shape that used to 403).
- **`pkill -f` Self-Match Over Remote Exec**:
  When the command runs as `sh -c '<cmd>'` (Superserve `/exec`, ssh, wrappers), `pkill -f <name>` matches your OWN shell because `<name>` appears in its command line — it kills itself (exit 143) before the rest runs. Use the bracket trick (`pkill -f '[h]eartbeat'`) or start daemons in a separate call without a preceding `pkill`.
- **Process Preservation**: Resuming a paused sandbox restores running processes from memory snapshot (e.g. background 9router and cloudflared tunnels keep running).
- **Pre-seed Telegram Allowlists Before Starting Gateway**: Hermes Gateway requires pairing codes for unknown senders. If remote exec is down or intermittent, approving pairing codes dynamically is blocked. Always inject `TELEGRAM_ALLOWED_USERS=<user_id>` directly into `~/.hermes/.env` before launching `hermes gateway run` so senders are pre-authorized without pairing codes.

### WebSocket Proxying in Cloudflare Workers
`fetch()` in Cloudflare Workers rejects `ws://` and `wss://` schemes (`TypeError: Fetch API cannot load`). To proxy WebSockets through Cloudflare Workers (e.g. `/exec/connect`), keep the URL as `https://` and pass incoming headers (excluding `host`):
```javascript
if (request.headers.get("Upgrade") === "websocket") {
  const wsTarget = target.replace(/^ws/, "http");
  const reqHeaders = new Headers(request.headers);
  reqHeaders.delete("host");
  return fetch(new Request(wsTarget, request), { headers: reqHeaders });
}
```

## Diagnosing 502 Bad Gateway: Upstream Outage vs Proxy Error vs Expired API Key
When `sandbox.superserve.ai/exec` returns `502 Bad Gateway` (with a Cloudflare HTML error page citing `Host (sandbox.superserve.ai): Error` or `<worker-domain> | 502: Bad gateway`), operators often suspect the API key (`ss_live_...`) is invalid or expired. Use this diagnosis sequence:
1. **Worker Liveness & Exceptions via `wrangler tail`**: Run `npx wrangler tail`. If `outcome: "ok"` and `exceptions: []` while `response.status: 502`, the Worker did not crash — the 502 is returned by the upstream origin server.
2. **Control Plane Isolation Probe**: Call `POST /api/sandboxes/<id>/activate` with `X-API-Key`.
   - If it returns `HTTP 200` with `status: "active"` and a 64-char `access_token`, the API key and account are 100% valid.
3. **Network Log Timestamp Probe**: Query `GET /api/sandboxes/<id>/network`.
   - Check the `ts` timestamps of the latest connections. If the last recorded connection was hours ago despite active tunnel or gateway traffic, the container's execution network namespace is stalled on the host hypervisor.
4. **Ephemeral Sandbox Test**: Create a temporary test sandbox (`POST /api/sandboxes` with `{"name": "probe"}`).
   - Immediately attempt `POST /dp/exec` on the new sandbox ID. If a brand-new sandbox also returns `502`, Superserve's shared execution plane (`sandbox.superserve.ai`) has an upstream infrastructure outage. Delete the probe sandbox immediately after testing.
5. **Local Fallback Strategy**:
   - If 9router and TryCloudflare tunnel inside the sandbox remain responsive (`/api/health` returns `{"ok":true}`) but remote shell exec is down, client agents (such as Hermes Telegram Gateway) can be run locally or on a fallback host pointed at the remote tunneled 9router endpoint (`https://<random>.trycloudflare.com/v1`) with zero model downtime.

## Fast Asset & Skill Transfer Across Geo-Blocked Sandboxes

When moving skills, packages, or large archives (e.g. 30MB+ tarballs) between the local Windows machine and remote sandboxes behind strict geo-blocking:

### 1. Cloudflare Worker KV File Transfer (<25 MB)
- Bind a KV namespace (`FILES`) in `wrangler.toml`:
  ```toml
  [[kv_namespaces]]
  binding = "FILES"
  id = "<kv-id>"
  ```
- In `worker.js`, route `GET /files/*`:
  ```javascript
  if (path.startsWith("/files/")) {
    const filename = path.slice(7);
    const data = await env.FILES.get(filename, "arrayBuffer");
    if (!data) return new Response("Not found", { status: 404 });
    return new Response(data, { headers: { "Content-Type": "application/gzip" } });
  }
  ```
- Upload directly from Windows via `npx wrangler kv key put --namespace-id=<id> "<name>" --path="<path>" --remote`.
- Download instantly on remote sandboxes: `curl -s -L https://<worker-domain>/files/<name> -o /tmp/<name>`.

### 2. Ephemeral In-Tunnel HTTP Server (>25 MB)
When transferring archives larger than Cloudflare KV limits (e.g. 30MB+ complete skill directories):
1. On the source sandbox:
   ```bash
   nohup python3 -m http.server 20199 --directory /tmp > /tmp/srv.log 2>&1 &
   nohup cloudflared tunnel --url http://127.0.0.1:20199 > /tmp/cf_srv.log 2>&1 &
   sleep 4; grep -o 'https://[a-z0-9-]*\.trycloudflare\.com' /tmp/cf_srv.log | head -1
   ```
2. On the destination sandbox:
   ```bash
   curl -s -L https://<quick-tunnel-url>/archive.tar.gz -o /tmp/archive.tar.gz
   tar -xzf /tmp/archive.tar.gz -C <target-dir>
   ```
3. Immediately kill the temporary server and tunnel on the source sandbox:
   ```bash
   pkill -f 'http.server 20199'; pkill -f 'tunnel --url http://127.0.0.1:20199'
   ```

### 3. Multi-Profile Hermes Skill Directory Sync
- Default profile skills reside at `/home/user/.hermes/skills/`.
- Isolated user profiles store their skills in `/home/user/.hermes/profiles/<profile>/skills/`.
- When syncing skills to a secondary profile, extract into both directories so that `hermes -p <profile> skills list` accurately reflects all available procedural skills.

### 4. Dynamic Tunnel URL Tracking + Per-User Auto-Notify (verified live Sep 2026)

Quick Tunnel hostnames rotate on every relaunch, so a static `tunnelUrl` in `worker.js` rots within hours. Track it dynamically:

1. **Reporter loop on each primary** (`/home/user/tunnel_report.sh`, every 120s → KV `tunnel_<user>`): greps the CURRENT tunnel log and PUTs the URL. Prefer `/home/user/tunnel.log` over legacy `/var/log/tunnel.log` — after cleanup relaunches only the former is fresh; reading the stale one pushes a dead URL into KV. Always `grep -a` (not plain `grep`): cloudflared's log contains binary/control characters, so plain grep prints `binary file matches` and extracts NO URL — the reporter then pushes nothing and KV keeps rotting on the old hostname.
2. **Worker prefers KV over static**: `getEffectiveTunnelUrl(userKey, srv, env)` returns KV `tunnel_<user>` when it starts with `https://`, else the static fallback. Both `checkTunnel` and `/health` use it; `/health` surfaces both `tunnelUrl` (effective) and `tunnelUrlStatic`.
3. **Rotation auto-notify**: `detectTunnelChange` runs on every ACTIVE-branch tick, diffs the effective URL against KV `tunnel_last_<user>`, and on change sends the fresh link via the USER'S OWN bot (`notifyUser`: KV `tg_token_<user>` + per-server `chatId`), not the admin bot — message: `🔗 <b>لینک جدید 9router</b>` + URL in `<code>`. First-ever write seeds the baseline silently (no notify when no prior value).
4. **N-level chains**: `triggerFailover` builds `levels` from `{standby, queue, level3, level4}` and `.filter(lv => lv.id && lv.key)`, so users can have different depths (user1: 4 levels, user2: 3). Surface `level4Id` in `/health` the same way as `level3`.
