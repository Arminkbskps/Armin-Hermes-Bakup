# Shared cPanel Probe (FastAPI vs PHP decision)

Session recipe for deciding whether a Python backend can run on a shared cPanel plan.
Full runbook pointer: `cloud-dev-environments` SKILL.md section "Shared cPanel Hosting".

## Probe via cPanel UAPI (no SSH needed)

Base: `https://<cpanel-host>:2083/execute/<Module>/<func>` with header
`Authorization: cpanel <user>:<API-TOKEN>`. Use `terminal` + `curl -sk`.
Never store the real token in skills, memory, or guides — revoke after use.

```bash
CP='https://<cpanel-host>:2083'; AUTH='<user>:<API-TOKEN>'
curl -sk -m 20 -H "Authorization: cpanel $AUTH" "$CP/execute/DomainInfo/domains_data?format=json"
curl -sk -m 20 -H "Authorization: cpanel $AUTH" "$CP/execute/Features/list_features"
curl -sk -m 20 -H "Authorization: cpanel $AUTH" "$CP/execute/Mysql/list_databases"
curl -sk -m 20 -H "Authorization: cpanel $AUTH" "$CP/execute/Mysql/list_users"
curl -sk -m 20 -H "Authorization: cpanel $AUTH" "$CP/execute/Fileman/list_files?dir=public_html"
curl -sk -m 20 -H "Authorization: cpanel $AUTH" "$CP/execute/SSL/installed_hosts"
```

## Feature flags that decide everything

From `Features/list_features` (seen on a HostIran shared plan):
- `passengerapps: 0` + `lvepythonsel: 0` + `ssh: 0` + `api_shell: 0` = NO
  persistent Python (no Passenger/Python App, no uvicorn/gunicorn, no Docker).
- `ea-php82` / `ea-php83: 1` = PHP path is available.
- `mysql: 1`, `postgres: 0` = MySQL-only; map to the existing `voidclub_*` DB.
- `cron: 1` exists but is not a substitute for a long-running API process.

## Fileman API quirks (stable across calls)

- List param is `dir`, NOT `path`: `Fileman/list_files?dir=public_html` or
  `?dir=%2Fhome%2F<user>%2Fbackend`. Passing only `path=` silently returns the
  home-dir listing — misleading when the docroot looks "empty".
- Read file: `Fileman/get_file_content?dir=<dir>&file=<name>` (needs both keys;
  `path=` alone errors with "parameter file is required").
- Many modules fail to load on restricted plans (`Terminal`, `Cron`, `MultiPHP`,
  `ZoneEdit`, `CloudLinux`, `LangManagers`, `DiskUsage` → "Can't locate
  Cpanel/API/....pm"). Treat as missing capability, not as a retryable error.
- On Windows hosts parse UAPI JSON with `python` (not `python3` — the Store shim
  breaks pipes); keep `head -c` budgets small (800–3000 chars).

## DNS vs server-side truth

- Public `nslookup <domain>` may return NXDOMAIN while the server is fine.
- Verify server-side with forced resolve (Windows: write to a local file, no /tmp):
  `curl -sk --resolve <domain>:443:<cpanel-IP> https://<domain>/ -o out.html`
- HTTP 200 via `--resolve` + NXDOMAIN via public DNS = server OK, client DNS /
  registrar delegation still pending. Say so explicitly; don't chase app bugs.

## Verifying registrar delegation (user sets nameservers, e.g. at IRNIC/airlink)

Setting nameservers at the registrar is only half the job — confirm the host's
zone actually answers. Query Google DNS-over-HTTPS (works even when local
`nslookup` is proxied/broken):

```bash
curl -s -m 15 'https://dns.google/resolve?name=<domain>&type=NS'
curl -s -m 15 'https://dns.google/resolve?name=<domain>&type=A'
```

- `"Status":3` + `Authority` showing the TLD SOA (e.g. `a.nic.ir.`) = NOT
  delegated yet — tell the user to wait / double-check the registrar NS entries.
- `"Status":0` + `Answer` listing the host's nameservers (seen:
  `ns1.hostiran.net.` / `ns2.hostiran.net.`) and `A → <cpanel-IP>` = delegated;
  also check `www` (often a CNAME to the apex). TTLs run ~14400–21600s, so warn
  that resolvers may serve stale NXDOMAIN for hours after delegation flips.

## Decision rule (VOID CLUB class)

- If `passengerapps`/`lvepythonsel`/`ssh` are all 0: NEVER promise to run
  FastAPI/uvicorn/Docker on the plan. Options, in order: (a) pure-PHP port of
  the API preserving every `/api/*` route so the vanilla-JS frontend is
  untouched; (b) frontend-only on cPanel + backend on a VPS; (c) ask the host
  to enable Python App / move plan.
- A `public_html` containing only `index.php` (coming-soon) + `php.ini` + `cgi-bin`
  means an empty docroot ready for upload — not a broken deploy.
