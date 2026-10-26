---
name: cloudflare-deploy
description: End-to-end Cloudflare Workers + D1 + R2 + Pages deployment.
version: 1.1.0
---

# Cloudflare Deployment

Once credentials are provided, deploy everything without asking.

## Setup

### Option A: GitHub Actions (RECOMMENDED if proxy blocks Cloudflare)
If local machine proxy blocks `api.cloudflare.com`:
- Use GitHub Actions runner (no proxy issue)
- Add secrets to GitHub repo: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`
- Push → auto-deploy

### Option B: Direct API (if no proxy issues)
```bash
# Test auth first
curl -s "https://api.cloudflare.com/client/Trace" --noproxy '*'

# Verify credentials
curl -s "https://api.cloudflare.com/client/cdn-4/user" \
  -H "X-Auth-Email: YOUR_EMAIL" \
  -H "X-Auth-Key: YOUR_GLOBAL_API_KEY"
```

### Option C: Wrangler CLI (requires OAuth browser login)
```bash
npm install -g wrangler
wrangler login  # Opens browser, NOT API key login
# Note: --email flag does NOT exist for wrangler login
```

## Create Resources via API

```bash
# D1 Database
curl -s -X POST "https://api.cloudflare.com/client/cdn-4/accounts/ACCOUNT_ID/d1/databases" \
  -H "X-Auth-Email: EMAIL" -H "X-Auth-Key: API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "db-name"}'

# R2 Bucket
curl -s -X POST "https://api.cloudflare.com/client/cdn-4/accounts/ACCOUNT_ID/r2/buckets" \
  -H "X-Auth-Email: EMAIL" -H "X-Auth-Key: API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"name": "bucket-name"}'
```

### Wrangler with API Token

```bash
# Set credentials in environment (NOT in login flow)
export CLOUDFLARE_API_TOKEN="cfk_..."
export CLOUDFLARE_ACCOUNT_ID="your-account-id"

wrangler whoami  # Should work
```

## Common Pitfalls

### Proxy Blocks Cloudflare
If `curl` and `wrangler` both fail to reach `api.cloudflare.com`:
- Clear proxy env vars: `unset https_proxy http_proxy all_proxy no_proxy`
- Or use GitHub Actions (runs from GitHub's servers, no local proxy)
- Or configure proxy to allowlist `*.cloudflare.com`

### Cloudflare Pages Project Pre-Creation in CI/CD (Code 8000007)
When deploying a static folder via GitHub Actions using `npx wrangler pages deploy <dir> --project-name=<name>`, Wrangler fails with:
`Project not found. The specified project name does not match any of your existing projects. [code: 8000007]` if the project was never initialized in the dashboard or via CLI.
**Rule:** Always precede the deploy command with an idempotent project creation step:
```bash
npx wrangler pages project create <project-name> --production-branch=main || true
npx wrangler pages deploy <dir> --project-name=<project-name> --branch=main --commit-dirty=true
```

### GitHub Secrets Injection via Python PyNaCl
When `gh` CLI is absent and npm is blocked by local proxy, use Python `pynacl` (`pip install pynacl`) to encrypt and set GitHub Actions secrets via REST API.

### GitHub Actions Log Download 403 on S3 Pre-signed URL Redirect
When fetching job logs via `/actions/jobs/{id}/logs`, GitHub redirects to an AWS S3 pre-signed URL. Standard HTTP clients forward the `Authorization: token ...` header to S3, causing HTTP 403.
**Rule:** Strip the `Authorization` header whenever the redirect URL target is not `github.com`.

### Wrangler Auth Issues
- `wrangler login` uses **OAuth** (opens browser) — NOT `--email` or `--apikey`
- To use API token directly: set `CLOUDFLARE_API_TOKEN` env var, don't run `login`
- Error "Invalid access token" = API token rejected (proxy or wrong key)

### GitHub PAT `workflow` Scope Requirement
If `.github/workflows/*.yml` push fails with `"refusing to allow a Personal Access Token to create or update workflow"`:
- Token is missing the **`workflow` scope**
- Fix: Regenerate token at github.com → Settings → Developer settings → Personal access tokens → check `workflow`
- Alternative: Create workflow file manually via GitHub web UI (github.com/{owner}/{repo}/new/main → create file at `.github/workflows/deploy.yml`)

### Proxy Blocks Cloudflare (Iran IP)
If direct API calls and `wrangler` both fail:
- Symptom: Empty response / timeout / `code: 9109` or `code: 7003` errors
- Root cause: Local proxy (e.g. 127.0.0.1:1080) blocks `*.cloudflare.com`
- Clearing env vars doesn't help if proxy is system-level
- **Solution**: Use **GitHub Actions CI/CD** — runner runs from GitHub servers, NOT from Iran IP
- Create `.github/workflows/deploy.yml` manually (see above) and push other files
- Add secrets: `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `JWT_SECRET`
- On first run, D1 ID will be created → add `CLOUDFLARE_D1_ID` secret manually

### wrangler.toml Must Be in .gitignore
When using CI-generated `wrangler.toml` (the template pattern), the repo's root `wrangler.toml` should be gitignored:
- It either has placeholder values (`{{ secrets.X }}`) that won't work locally
- Or it's generated dynamically during the workflow with real secret values
- Add to `.gitignore`: `wrangler.toml`, `.wrangler/`, `.dev.vars`, `.env`
- Wrangler parses the config file for EVERY command, including `kv namespace list` and `r2 bucket create`. A root `wrangler.toml` containing placeholder bucket names fails those unrelated steps with `r2_buckets[0].bucket_name="__R2_BUCKET__" is invalid`. Keep the repo root inert: either gitignore `wrangler.toml` and generate it in CI, or commit a stub (name + main + compatibility_date only, no bindings) and keep the real config in `wrangler.template.toml`, with CI doing `cp wrangler.template.toml wrangler.ci.toml` — never copy the stub.

### Wrangler KV Create Output Is Not JSON
`wrangler kv namespace create <title>` prints `id = "<32hex>"` (TOML style), not `"id": "..."`. A grep for `"id":` matches nothing, leaving the variable empty and silently poisoning the generated config. Parse the TOML form first, then fall back to re-listing:
```bash
KV_ID=$(echo "$OUT" | grep -oE 'id = "[a-f0-9]{32}"' | head -1 | grep -oE '[a-f0-9]{32}')
[ -z "$KV_ID" ] && KV_ID=$(node -e "try{const l=JSON.parse(require('fs').readFileSync('kv_list.json','utf8'));const f=l.find(n=>n.title==='<title>');console.log(f?f.id:'')}catch(e){console.log('')}")
```

### Authentication Error (code 10000)
- Wrong email spelling in API call vs token
- Use exact email from Cloudflare dashboard
- Account ID must match the account that owns the token
- Missing permission scope: Workers KV needs `Account -> Workers KV Storage -> Edit`; R2 bucket create/list/bind needs `Account -> Workers R2 Storage -> Edit`; Pages project create/deploy needs `Account -> Cloudflare Pages -> Edit`. Without the right scope Cloudflare returns generic code 10000 authentication failure — KV succeeding does NOT prove R2 or Pages will work, so verify each service separately.
- `GET /user/tokens/verify` returning `active` proves only that the token exists; it says nothing about scopes. Diagnose per-service in CI before creating resources:
```bash
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/user/tokens/verify" | head -c 500; echo
curl -s -H "Authorization: Bearer $CLOUDFLARE_API_TOKEN" "https://api.cloudflare.com/client/v4/accounts/$CLOUDFLARE_ACCOUNT_ID/r2/buckets" | head -c 500; echo
# {"success":false,"errors":[{"code":10000,...}]} on the second call = token lacks R2 scope; ask the user to mint a new token with Workers Scripts + Workers KV Storage + Workers R2 Storage Edit.
```
- Deploy-time consequence: `wrangler deploy` fails with `R2 bucket '<name>' not found [code: 10085]` when the bucket was never created because the create step was scope-blocked. Treat 10085 as 'bucket missing OR token cannot see R2', not as a typo in `bucket_name`.

### TCP Sockets (`cloudflare:sockets`) on Workers vs Pages
When deploying VLESS, Trojan, or raw TCP proxies using `cloudflare:sockets`:
- Deploy as a native Cloudflare Worker (`wrangler deploy` with `main = "src/worker.js"`, `compatibility_flags = ["nodejs_compat"]`).
- Avoid bundling raw socket proxies into Pages functions (`public/_worker.js`), which frequently triggers opaque deployment failures (`Failed to publish your Function. Got error: Unknown internal error occurred`).

### Iran Censorship Bypass & Domain Safety
- **Never use `.ir` domains for tunnels or proxies**: `.ir` domains are legally tied to national identity records (IRNIC) and present severe safety hazards for Iranian users. Use Cloudflare Workers/Pages subdomains, foreign custom domains, or WireGuard/WARP.
- **SNI Blocking on `*.workers.dev` (TCI / Mokhaberat)**: State firewalls often block `*.workers.dev` at the TLS ClientHello SNI stage. Bypass via client-side TLS packet fragmentation (`packets: tlshello` or `1-3`, `length: 10-20`, `interval: 10-20ms`) or route through alternate TLS ports (8443, 2053, 2083, 2087, 2096) with clean Cloudflare Anycast IPs.

## Flow

```bash
# 1. Create (via API or dashboard)
wrangler d1 create DB_NAqE
wrangler r2 bucket create BUCKET_NAqE

# 2. Configure wrangler.toml with account_od + database_id + bucket_name

# 3. Migrate + Deploy
wrangler d1 migrations apply DB_NAqE --remote
wrangler deploy
wrangler pages project create PROJECT_NAqE
```

### Python/FastAPI Backend (Railway/Render) + Cloudflare Pages Frontend Pattern
When hosting a Python/FastAPI app:
- Host Backend (FastAPI + SQLite/Postgres) on **Railway** via `Procfile` (`uvicorn backend.app.main:app --host 0.0.0.0 --port ${PORT:-8000} --workers 4`) + `nixpacks.toml`.
- Host Frontend on **Cloudflare Pages** (`wrangler pages deploy frontend` or dashboard upload).
- In `frontend/js/api.js`, implement dynamic origin detection: fallback to Railway API URL when on `*.pages.dev` or custom domain, else use `window.location.origin/api`.
- Place `_headers` (with CORS `Access-Control-Allow-Origin: *`) and `_redirects` in `frontend/` directory.

### FastAPI Deploy Pitfalls (hard-won, real build failures)

**WASM/WASIX builders cannot run this stack.** If the build log shows `--platform wasix_wasm32`, `cross-requirements.txt`, or `No matching distribution found for pydantic-core==...`: the platform cross-compiles Python to WebAssembly. Binary packages (pydantic-core, Pillow, gunicorn, psycopg2) have no WASM wheels and will never resolve — pinning versions does NOT help, the next binary dep fails instead. Fix: deploy on a standard Linux runtime: Railway (GitHub repo → auto-detects `railway.json`/`nixpacks.toml`/`Procfile`), Koyeb/Render (Buildpack or Dockerfile), Hugging Face Spaces (SDK = Docker).

**Multiple requirements files drift.** When the repo has `backend/requirements.txt` (used by the Dockerfile) AND a root `requirements.txt` (used by nixpacks/Procfile), adding a package to one fixes local runs while the cloud build using the other still crashes at worker boot (classic: `ModuleNotFoundError: No module named 'email_validator'` from Pydantic `EmailStr`). Fix: add to BOTH files, or consolidate to one canonical file. Grep for all `requirements*.txt` before declaring deps "fixed".

**First deploy = empty database.** SQLite ships empty in a fresh container; local seed data never transfers. Expect an empty catalog on the first public URL and either seed on boot or write a SQLite→target migration script. The public URL comes from Service → Settings → Networking → **Generate Domain** (reuse the existing one if already generated).

**MySQL via docker-compose (Unicode/Persian-safe).** Use `mysql:8.0` with `command: --character-set-server=utf8mb4 --collation-server=utf8mb4_unicode_ci`, URL `mysql+pymysql://user:pass@db:3306/dbname?charset=utf8mb4`, and gate the web service with `depends_on: db: condition: service_healthy` plus a `mysqladmin ping` healthcheck — without the gate the app boots before MySQL accepts connections and crashes with Connection Refused. SQLAlchemy models written with plain `String(n)`/`Text` columns are portable; no code change needed, only `DATABASE_URL`.

## Migration from Firebase/Supabase to Cloudflare

When migrating a full-stack app (e.g. Firebase Auth + Realtime DB + Supabase Storage) to Cloudflare:

1. **Backend**: Rewrite server-side logic as a Cloudflare Worker (Hono framework). Auth via JWT (PBKDF2 password hashing + HMAC-SHA256 JWT). Database via D1 (SQLite). Storage via R2.
2. **Frontend**: Remove ALL external script tags (`firebase-app.js`, `firebase-database.js`, `supabase-js`). Replace `firebase.database().ref(...)` calls with `fetch(API_BASE + '/api/...')` calls. Replace Supabase storage uploads with `FormData` POST to Worker `/api/upload`.
3. **Real-time**: Without Firebase Realtime, use simple polling (`setInterval(pollMessages, 3000)`) or upgrade to WebSockets later.
4. **Auth flow**: Store JWT token in `localStorage`. Send as `Authorization: Bearer <token>` header on all API calls.
5. **Verify zero external dependencies**: `grep -rn "firebase\|supabase" --include="*.js" --include="*.html"` should return nothing (except comments).

### R2 Not Available → Use Supabase Storage Instead

If the user can't provide Cloudflare R2 (requires payment method/billing), migrate to **Supabase Storage**:

See `references/supabase-storage-migration.md` for:
- Code changes in `worker.js` (R2 bindings → REST API fetch)
- `wrangler.toml` changes (remove `[[r2_buckets]]`, add `SUPABASE_URL`/`SUPABASE_ANON_KEY` vars)
- Workflow changes (new `SUPABASE_ANON_KEY` secret)
- How media URLs go from signed R2 proxy to direct Supabase public URLs

### Deploy Workflow Template
See `templates/github-actions-cloudflare-deploy.yml` for a ready-to-use GitHub Actions workflow that creates D1, R2, deploys Worker, and deploys Pages.

### GitHub Actions: `working-directory` for Wrangler

**Critical**: When using `wrangler deploy --config <path>`, the config file's `main = "backend/worker.js"` is resolved **relative to the config file's directory**, not the working directory. 

**Fix**: Write `wrangler.ci.toml` and secrets file to `${{ github.workspace }}` (not `$RUNNER_TEMP`) so paths resolve correctly:

```yaml
- name: Prepare CI configuration
  id: config
  shell: bash
  run: |
    CONFIG="${GITHUB_WORKSPACE}/wrangler.ci.toml"
    SECRETS="${GITHUB_WORKSPACE}/amngram-secrets.json"
    # ... python writes both files to GITHUB_WORKSPACE
```

**Pitfall**: If you write config to `$RUNNER_TEMP` but run with `working-directory: ${{ github.workspace }}`, wrangler looks for `backend/worker.js` relative to `$RUNNER_TEMP` and fails with "entry-point file not found".

## GitHub Actions: Reliable Placeholder Substitution

**Problem**: Python heredoc approach for substituting placeholders in `wrangler.toml` fails silently (no error, placeholders stay as `__D1_ID__`, `__SITE_URL__`, etc.) - often due to Python interpreter issues, heredoc escaping, or path resolution.

**Solution**: Use `sed` commands with explicit environment variables and debug output:

```yaml
- name: Replace placeholders in wrangler.toml
  run: |
    set -euo pipefail
    cp wrangler.toml wrangler.ci.toml
    sed -i "s/__D1_ID__/$CLOUDFLARE_D1_ID/g" wrangler.ci.toml
    sed -i "s|__SITE_URL__|$SITE_URL|g" wrangler.ci.toml
    sed -i "s|__SUPABASE_ANON_KEY__|$SUPABASE_ANON_KEY|g" wrangler.ci.toml
    echo "wrangler.ci.toml created successfully"
    cat wrangler.ci.toml  # DEBUG: verify substitutions
  env:
    CLOUDFLARE_D1_ID: ${{ secrets.CLOUDFLARE_D1_ID }}
    SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
    SITE_URL: ${{ vars.AMNGRAM_SITE_URL || 'https://amngram.armin13891219.pages.dev' }}

- name: Create secrets file
  run: |
    set -euo pipefail
    echo "{\"JWT_SECRET\":\"$JWT_SECRET\",\"SUPABASE_ANON_KEY\":\"$SUPABASE_ANON_KEY\"}" > amngram-secrets.json
    echo "Secrets file created"
  env:
    JWT_SECRET: ${{ secrets.JWT_SECRET }}
    SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}
```

**Why sed works better**: No Python interpreter dependency, no heredoc escaping issues, explicit debug output shows actual values.

### Secrets vs `[vars]`: Silent Override

A `[vars]` entry and a `wrangler secret` with the **same name** — the **secret does not win**. The binding resolves as `type: "plain_text"` holding the `[vars]` value, and `wrangler secret put` reports **success** while the worker keeps reading the placeholder. This silently ships a public default as an auth token, an API key, or a JWT secret. There is no error and no warning anywhere.

**Rule:** any value that is a secret must NEVER appear in `[vars]`, even as a placeholder. Use a harmless unrelated var instead:

```toml
# WRONG — placeholder shadows the real secret forever
[vars]
ADMIN_TOKEN = "placeholder-set-via-secret"

# RIGHT
[vars]
SITE_NAME = "My Site"
```

**Verify the binding actually resolved as a secret** after deploy — do not trust `wrangler secret put` exit code:
```js
const r = await fetch(
  `https://api.cloudflare.com/client/v4/accounts/${ACCOUNT}/workers/scripts/${SCRIPT}/settings`,
  { headers: { Authorization: `Bearer ${OAUTH_TOKEN}` } }
);
const bindings = (await r.json()).result.bindings;
// secret  → { type: "secret_text" }
// leaked  → { type: "plain_text", text: "placeholder..." }  ← the bug
```
The `wrangler whoami` OAuth token is stored in `~/.wrangler/config/*.toml` as `oauth_token`; read it from there rather than asking the user for a second credential.

**Recovery once shadowed** — `wrangler secret delete` + `wrangler secret put` is not enough while the `[vars]` entry exists. Remove the `[vars]` key from `wrangler.toml` first, then `wrangler deploy`, then `wrangler secret put`.

**Password-style secret input** — `wrangler secret put NAME` consumes stdin, and MSYS/bash mangles piped values (`<<<`/here-strings strip content, pipes arrive empty, the CLI then creates a secret bound to nothing). Reliable forms:
```bash
echo -n "$TOKEN" | wrangler secret put ADMIN_TOKEN          # -n: no trailing newline
```
Verify the deployed value end-to-end by actually calling an authenticated endpoint with `curl --noproxy '*'` afterward.

## Worker CORS: Cross-Origin Requests With Authorization

A GitHub Pages site calling a Cloudflare Worker is cross-origin. Without preflight handling, authenticated `fetch()` calls from the browser **hang with no error, no network tab entry, and no response** — `Runtime.evaluate` times out and there is nothing to debug from the page.

```js
const CORS = {
  "Access-Control-Allow-Origin": "*",     // or the specific origin
  "Access-Control-Allow-Methods": "GET, POST, PUT, DELETE, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, Authorization",
  "Access-Control-Max-Age": "86400",
};

// MUST be the first route in fetch():
if (request.method === "OPTIONS") {
  return new Response(null, { status: 204, headers: CORS });
}
```
Any request with an `Authorization` header is a "non-simple" request → triggers an `OPTIONS` preflight. If the preflight 404s (falls through to a catch-all 404), the real request is never sent.

**Ordering pitfall** — route registration must distinguish by method *before* the auth check, or a public route silently becomes 401:
```js
// WRONG — /api/data with auth header and no method guard hits the auth check first
if (path === "/api/data" || path === "/api/sites") { ... }
// and /api/data returns {"error":"admin token required"} to anonymous readers
```
```js
// RIGHT — per-method
if (path === "/api/data" && method === "GET")  return handlePublic(env);
if (path === "/api/sites" && method === "GET") return handlePublic(env);
if (path === "/api/sites" && method === "POST") { /* auth */ }
```

**Local CORS verification** — test both the preflight and the real call:
```bash
curl -s -X OPTIONS -H "Origin: https://owner.github.io" \
  -H "Access-Control-Request-Method: GET" \
  -H "Access-Control-Request-Headers: authorization" \
  -o /dev/null -w "%{http_code}\n" "$API/api/settings"   # expect 204
```

## Static Site on Pages: Never Use `[site]` or `wrangler deploy`

A pure static frontend (HTML/CSS/JS, no Worker code) must be deployed as **Cloudflare Pages**, not Workers Sites. Wrapping it in the deprecated Workers Sites config fails the Pages build with:

```
[WARNING] Because you've defined a [site] configuration, we're defaulting to "workers-site" for the deprecated `site.entry-point` field.
✘ [ERROR] The entry-point file at "workers-site/index.js" was not found.
```

**Cause**: a `wrangler.toml` containing a `[site]` block (e.g. `bucket = "./frontend"`) deployed via `wrangler deploy`. Wrangler then hunts for a `workers-site/index.js` entry-point that a static project doesn't have.

**Fix** — top-level `pages_build_output_dir`, no `[site]` section:

```toml
name = "my-frontend"
pages_build_output_dir = "./frontend"
compatibility_date = "2026-08-30"
```

Deploy with the Pages command (never `wrangler deploy` for static sites):

```bash
npx wrangler pages deploy frontend --project-name my-frontend
```

Dashboard (Git-connected) equivalent: Framework preset `None`, **Build command completely empty**, Build output directory `frontend` (or `./` when the upload root is the frontend folder itself).

### CI Smoke-Check Strings Must Track the Current Build
Validate steps that grep the built file for feature strings break on the first redesign that removes them — the check then asserts a stale snapshot, not deployability. Assert only stable invariants (`test -f`, `dir="rtl"`, the app's storage/API key) and re-point the feature grep at whatever the current build ships; update the check in the same commit as the redesign.

### Worker + Static Assets: Full-Stack Single Deploy (No Pages Project)

When the app is a Worker API plus a static frontend (even a single `public/index.html`), ship both with ONE `wrangler deploy` via Workers Static Assets — no Pages project, no second pipeline:

```toml
name = "my-app"
main = "src/worker.js"
compatibility_date = "2025-10-01"
account_id = "__ACCOUNT_ID__"

[assets]
directory = "./public"
not_found_handling = "single-page-application"

[[kv_namespaces]]
binding = "META"
id = "__KV_ID__"
```

- The Worker owns `/api/*` and `/f/*`; every other GET falls through to `index.html` at the edge (`single-page-application`), so share-links like `/p/:id` resolve without Worker code. Do not add a `[site]` block — that forces the deprecated workers-site path and breaks the deploy.
- `[assets] directory` resolves relative to the config file: generate `wrangler.ci.toml` from a committed `wrangler.template.toml` with `sed` in CI, and keep the repo-root `wrangler.toml` a binding-free stub so unrelated `kv`/`r2` CLI steps never parse placeholders.
- Verify live after every deploy: `GET /` returns 200 HTML and `GET /api/stats` returns JSON; treat any `error code: NNNN` plaintext body as a binding/config failure, not an app bug.

### A Matching Remote SHA Is Not a Live Deploy (Pages)
After pushing, confirm the Pages deployment itself went green and the live URL serves the new bytes (fetch the page and grep for a string the commit added, e.g. a footer marker) — a synced `origin/main` with a failing action still serves the old site. When the action fails with `Authentication error [code: 10000]`, re-syncing secrets only helps if the local token value is good; if CI still returns 10000 after a fresh sync, the stored token itself is invalid or scope-short — mint a new token with `Cloudflare Pages` Edit scope and sync that instead of re-pushing the same value.

## Cloudflare Pages URL Format

**Wrong**: `https://amngram.pages.dev` (doesn't exist)

**Correct**: `https://amngram.armin13891219.pages.dev` — Pages projects are hosted at `<project>.<account>.pages.dev`

Always use the account-specific subdomain. Set default in workflow:
```yaml
SITE_URL: ${{ vars.AMNGRAM_SITE_URL || 'https://amngram.armin13891219.pages.dev' }}
```

## Cloudflare Dashboard Navigation for Pages

**Critical**: Users often confuse Worker detail pages with the Pages dashboard.

- Worker detail page (tabs: Overview, Metrics, Deployments, Bindings, Observability, Domains, Settings) → **This is NOT where you create Pages projects**
- To create Pages: Go to main **Workers & Pages** → Click **Pages** tab (top of page) → **Create a project**
- Direct link: `https://dash.cloudflare.com/<account-id>/pages`

Always verify the exact URL format before showing it to the user.

## Node.js Module Type Pitfall

When `package.json` has `"type": "module"` (ESM), Node.js treats `.js` files as ESM modules where `require()` is unavailable.

**Error**: `ReferenceError: require is not defined in ES module scope`

**Fix**: Rename CommonJS scripts to `.cjs` extension:
```bash
mv scripts/build-config.js scripts/build-config.cjs
# In workflow: node scripts/build-config.cjs
```

This forces Node.js to treat the file as CommonJS regardless of `package.json` type.

## wrangler.toml Field Name Typos

**Common typo**: `Satabase_name` instead of `database_name` in `[[d1_databases]]` section.

**Symptom**: wrangler parse failure or `database_id must have valid database_id specified [code: 10021]`

**Prevention**: Always double-check exact field names in `wrangler.toml`:
```toml
[[d1_databases]]
binding = "DB"
database_name = "amngram-db"   # NOT Satabase_name
database_id = "uuid-here"
```

## Secret Validation in Workflow

Always validate secrets early with bash parameter expansion:
```yaml
- name: Validate deployment settings
  run: |
    set -euo pipefail
    : "${CLOUDFLARE_API_TOKEN:?Missing CLOUDFLARE_API_TOKEN secret}"
    : "${CLOUDFLARE_ACCOUNT_ID:?Missing CLOUDFLARE_ACCOUNT_ID secret}"
    : "${CLOUDFLARE_D1_ID:?Missing CLOUDFLARE_D1_ID secret}"
    : "${JWT_SECRET:?Missing JWT_SECRET secret}"
    : "${SUPABASE_ANON_KEY:?Missing SUPABASE_ANON_KEY secret}"
```
This fails fast with clear message instead of cryptic wrangler errors later.

## GitHub Secrets via Node.js (when gh CLI unavailable)

See `references/github-secrets-nodejs.md` for a complete Node.js script using `sodium-native` to encrypt and add GitHub Actions secrets via the REST API. Install: `npm install sodium-native` in a temp dir.

## GitHub Actions Node.js Version

**CRITICAL (2025+)**: GitHub Actions runners use Node.js 24 by default. Using `node-version: '20'` triggers deprecation warnings and may fail.

```yaml
# WRONG (deprecated)
- uses: actions/checkout@v4
- uses: actions/setup-node@v4
  with:
    node-version: '20'

# CORRECT
- uses: actions/checkout@v5
- uses: actions/setup-node@v5
  with:
    node-version: '24'
```

## GitHub Token Scopes

| Scope | What it does |
|-------|-------------|
| `repo` | Push code, manage PRs/issues |
| `workflow` | Create/update `.github/workflows/*.yml` files |

If push fails with `refusing to allow a Personal Access Token to create or update workflow`:
- The token lacks `workflow` scope
- **Fix**: Regenerate token with `workflow` scope, OR
- **Workaround**: Edit workflow file manually in GitHub web UI
- **OR** push workflow via API with `sodium-native` encryption (see `references/github-secrets-nodejs.md`)

## computer_use Failures

When `computer_use` fails 3+ times with the same error:
- Stop retrying immediately
- Switch to terminal/API approach
- Don't loop — the user gets frustrated watching you repeat the same failing action

**Rule**: Maximum 2 retries on computer_use before switching to `terminal` or direct API calls. The dashboard navigation issues in this session (404 on Pages link, confusion between Worker detail page and Pages dashboard) are classic examples where direct URLs + user instructions beat browser automation.
### GIPHY_API_KEY Is Optional

When a new v6/v7 feature adds a new API (e.g. GIPHY), make the workflow validate it gracefully:
```yaml
# WRONG — hard fail if GIPHY_API_KEY is missing
: "${GIPHY_API_KEY:?Missing GIPHY_API_KEY secret}"

# CORRECT — GIPHY falls back to offline GIFs, no crash
# GIPHY_API_KEY is optional (falls back to offline GIFs)
```
Always validate required secrets, but mark optional ones with a comment. Update the skill's required_secrets list when the project evolves.

### R2 Unavailable (Code 10042) → KV-Only Fallback (No Billing)

When the account cannot enable R2 (no international card, sanctions, `code: 10042` on bucket list/create), ship a KV-only Worker instead of blocking on R2 — KV needs no billing and the existing token scopes already cover it. Error-code triage: `10000` on R2 calls = token lacks R2 scope (mint a new token); `10042` = account-level R2 not enabled (no token fixes it, pivot to KV-only); `10085` at deploy = binding refers to a bucket that was never created (create it or drop the binding).

KV-only rules (mechanism: KV values cap at 25MB, so base64 payloads must stay well under it): per-file cap 9MB (413 above it), store bytes as chunked-base64 under `data/:id` plus JSON meta under `meta/:id`, keep a soft global quota guard (e.g. 800MB via meta scan) returning 507, strip `[[r2_buckets]]` from `wrangler.template.toml`, and make the R2 CI step a no-op echo. Keep the same API contract so the frontend never changes.

Omit `limit` from KV `list()` — call `list({ prefix, ...(cursor ? { cursor } : {}) })` and page on `list_complete/cursor`; an explicit `limit` breaks on some runtimes and silently returns zero keys, which surfaces as a false-empty stats endpoint.

### R2 Bucket Is Optional (Graceful Workflow)

Not all users have R2 enabled in their Cloudflare account. Make the workflow degrade gracefully:

```yaml
- name: Ensure R2 media storage
  shell: bash
  run: |
    set -euo pipefail
    # R2 is optional; if not enabled in dashboard, skip gracefully
    if npx wrangler r2 bucket list 2>/dev/null | jq -e --arg name "$R2_BUCKET_NAME" '.[] | select(.name == $name)' >/dev/null; then
      echo "R2 bucket already exists: $R2_BUCKET_NAME"
    else
      echo "Attempting to create R2 bucket (requires R2 enabled in Cloudflare Dashboard)..."
      if npx wrangler r2 bucket create "$R2_BUCKET_NAME" 2>/dev/null; then
        echo "R2 bucket created: $R2_BUCKET_NAME"
      else
        echo "::warning::R2 bucket could not be created. Continuing deployment without R2..."
      fi
    fi
```

Also **comment out the R2 binding in wrangler.toml** if R2 is unavailable, otherwise `wrangler deploy` fails:

```yaml
- name: Prepare Wrangler config
  shell: bash
  run: |
    set -euo pipefail
    cp wrangler.toml wrangler.ci.toml
    sed -i "s/__D1_ID__/$CLOUDFLARE_D1_ID/g" wrangler.ci.toml
    # Comment out R2 binding if R2 is not enabled
    if ! npx wrangler r2 bucket list 2>/dev/null | grep -q '"name"'; then
      echo "R2 not available, commenting out R2 binding in wrangler.ci.toml"
      sed -i '/^\[\[r2_buckets\]\]/,/^$/ s/^/#/' wrangler.ci.toml
    fi
```

This prevents `[ERROR] A request to the Cloudflare API (/accounts/***/r2/buckets) failed. Please enable R2 through the Cloudflare Dashboard. [code: 10042]` from blocking the whole deployment.

### `site.webmanifest` Not `site.manifest`

When copying PWA manifest files from a source folder, check the workflow's `cp` line. The workflow expects `site.webmanifest` exactly. If the source has `site.manifest`, rename on copy:
```bash
cp source/site.manifest dest/site.webmanifest
```
Otherwise: `cp: cannot stat 'site.webmanifest': No such file or directory`

### `preview.html` Must Mirror `index.html`

After replacing `index.html`, always also:
```bash
cp index.html preview.html
```
They are separate tracked files in the repo.

### Core Dumps Break Pages Deploys (25 MiB File Limit)

A crashed `node` (or any native process) can drop a multi-dozen-MB `core` file in the repo root; if it gets committed — especially under the deployed folder — `wrangler pages deploy` fails with `Pages only supports files up to 25 MiB in size` naming the `core` file. Prevent it on every Pages/Workers repo: add `core` and `core.*` to `.gitignore`, `git rm` any tracked one, delete local copies, and run `ulimit -c 0` in shells running crash-prone tooling. Before pushing a deploy, scan for oversized blobs: `git rev-list --objects --all | git cat-file --batch-check='%(objecttype) %(objectname) %(objectsize) %(rest)' | awk '$1=="blob" && $3>1000000'`.

### Copying Files with Spaces in Path (Windows/MSYS)

When copying files whose path contains spaces (e.g. `D:\System File\Downloads\AmnGram-v6-Full-Project`):
```bash
# WRONG — quoting doesn't protect & operator from being parsed as background
cp "$SRC/backend/worker.js" "$DST/backend/worker.js" &

# CORRECT — separate commands, single-quoted paths
cp '/d/System File/Downloads/Folder/file.js' 'dest/file.js' && echo "done"
cp '/d/System File/Downloads/Folder/file2.js' 'dest/file2.js' && echo "done"
```

## Self-Hosting / Reverse Migration (Cloudflare → VPS)

When the user asks "can I self-host this?" for a Cloudflare-based project, analyze the stack and map each component:

### Component Mapping

| Cloudflare Service | VPS Replacement |
|---|---|
| **Cloudflare Workers** (compute) | Node.js/Express/Fastify server behind Nginx |
| **Cloudflare D1** (SQLite) | SQLite on VPS (same schema, often drop-in) or PostgreSQL |
| **Supabase Storage** (media) | Local filesystem + Nginx static serving, or MinIO (S3-compatible) |
| **R2** (object storage) | Local disk or MinIO |
| **Cloudflare Pages** (static) | Nginx/Caddy serving static files |
| **Google OAuth** | Same service — just update callback URLs in Google Console |

### Architecture Analysis Steps (for any repo)

1. Read `package.json` — identifies dependencies, scripts, runtime
2. Read `wrangler.toml` / `docker-compose.yml` — identifies cloud services and bindings
3. Read `schema.sql` — D1 schemas are SQLite; port directly to SQLite on VPS
4. Read main backend file — identify external API calls (Supabase, Google JWKS, etc.)
5. Read frontend HTML — identify Google Sign-In scripts, CDN dependencies

### Domain Strategy (Keep Cloudflare for DNS Only)

Option A: **Cloudflare DNS-only** (orange cloud OFF) — A record points to VPS IP, no Cloudflare proxy
Option B: **Cloudflare Tunnel** — zero-trust access without opening ports on VPS (more secure)

### VPS Requirements for Chat Apps

| Component | RAM | Disk | Notes |
|---|---|---|---|
| Node.js backend | ~200MB | negligible | SQLite is memory-efficient |
| SQLite database | ~50MB | scales with data | WAL mode for concurrent reads |
| Static files | negligible | 10-20MB | HTML/CSS/JS |
| Media uploads | varies | **SSD fills fast** | See pitfall below |
| Nginx | ~10MB | negligible | Reverse proxy + static serving |

### Pitfall: 40GB SSD Fills Fast with Media

Chat apps with image/video uploads consume SSD rapidly. Mitigations:
- Set file size limits in backend (e.g., 20MB per upload)
- Use object storage (MinIO, Backblaze B2) for media instead of local disk
- Configure automatic cleanup for old media
- Or keep Supabase Storage for media only while self-hosting everything else

### Reverse Migration Checklist

1. Rewrite `worker.js` (Workers API) → Node.js server (Express/Fastify)
   - `env.DB.prepare()` → SQLite/PG driver calls
   - `env.SUPABASE_URL` → local file storage or MinIO
2. Run `schema.sql` against local SQLite
3. Serve static files via Nginx
4. Update Google OAuth redirect URLs
5. Set up SSL with Certbot/Let's Encrypt
6. Configure UFW firewall

## Worker + D1 as App Backend: Hard-Won Patterns

When a Worker + D1 serves as the live backend for a static frontend (e.g. GitHub
Pages dashboard + admin panel), these patterns prevent whole classes of bugs:

### No-Store JSON + Client Cache-Bust (stale GETs after PUT)

Symptom: `PUT /api/sites/:id` returns `{"ok":true}` but the next `GET` returns
the old row — looks like the write failed, but it succeeded. Cause: edge or
browser caching of GET JSON. Fix on both ends:

```js
// Worker: every JSON response carries no-store
const JSON_HEADERS = {
  "Content-Type": "application/json; charset=utf-8",
  "Cache-Control": "no-store, no-cache, must-revalidate",
  "Access-Control-Allow-Origin": "*",
  // ...
};
```

```js
// Client: cache-buster on every fetch
fetch(API + path + (path.includes("?") ? "&" : "?") + "_=" + Date.now(), opts)
```

Verify with a marker round-trip: PUT a distinctive value, GET it back, confirm.

### urllib Gets 403 Behind Cloudflare — Set a Browser User-Agent

Python's `urllib` default `User-Agent: Python-urllib/x.y` is rejected with 403
by Cloudflare-fronted endpoints. Every `urllib.request.Request` must carry:

```python
headers = {"Authorization": "Bearer " + tok, "User-Agent": "my-ci/1.0"}
opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))  # proxy-safe
```

Same for `requests`: `session.trust_env = False` so dead local proxies
(`127.0.0.1:1080`) don't hijack CI calls.

### Normalize the API Base URL in CI

See `references/gemini-interactions-api.md` for the `google-genai` Interactions-API call path, fast-moving Gemini model IDs, and why AI Studio keys must never be validated by prefix shape.
Secrets get stored with or without a trailing `/api` (`...workers.dev` vs
`...workers.dev/api`), and string concatenation produces 404s
(`/api//admin/list`). Normalize once at the top of every CI step:

```bash
BASE="${WORKER_API%/}"; [[ "$BASE" != */api ]] && BASE="$BASE/api"
curl -s -H "Authorization: Bearer $ADMIN_TOKEN" "$BASE/admin/list"
```

Guard the sync: fail fast on empty body or `"error"` in the response instead of
letting the pipeline run on zero sites and report false success.

### CI Regeneration Must Not Clobber Good Data with Fallback Junk

Free AI providers often block datacenter IPs, so a CI summarizer falls back to
template text. Never overwrite a real stored summary with a fallback one —
keep the previous row and flag it:

```python
if ai.get("provider") == "fallback" and prev and prev.get("provider") not in (None, "fallback", "pending"):
    prev["stale"] = True
    return prev  # keep the real summary
```

And the commit step must `git add` the **generated data file**, not just
config — otherwise the pipeline succeeds every run while the site never updates.

### Public Endpoints Must Never Return the Settings Table

A `handlePublicData` that runs `SELECT key, value FROM settings` and spreads
it into the response leaks every stored secret (`google_api_key`,
`openrouter_api_key`, …) to anyone with curl — and the leak is invisible
because the endpoint keeps returning 200 with correct data. Rule: public
handlers return only `meta` + `sites` (explicit columns, never `SELECT *`
over a secrets-bearing table); settings are readable solely through an
authenticated `/api/settings` route. Verify live after fixing:

```bash
curl -s "$API/api/data" | python -c "import json,sys; assert 'settings' not in json.load(sys.stdin)"
```

If a key already leaked, rotate it — closing the hole doesn't un-leak it.
Same class of bug: never commit token files (`worker/.admin_token`):
`git rm --cached <file>` + a `.gitignore` entry; the file stays locally,
stops being tracked. Tokens already pushed must be regenerated regardless.

### Frontend Fallback to Committed Data When the Worker Is Down

If the static frontend reads only from the Worker, one outage = a blank page
with a load error. Chain a fallback to the committed data file:

```js
fetch(WORKER_API + "/data?cache=no", { cache: "no-store" })
  .then((r) => { if (!r.ok) throw new Error("HTTP " + r.status); return r.json(); })
  .catch((e) => fetch("data/sites.json", { cache: "no-store" }).then((r2) => {
    if (!r2.ok) throw e;
    return r2.json();
  }));
```

The fallback is only as fresh as the last commit, so this depends on the
previous subsection: CI must keep committing the generated `data/sites.json`.

### GitHub Actions Log API Hits Abuse Detection

Downloading run logs via the REST API (`/actions/jobs/{id}/logs`) from
automation frequently returns `Whoa there!` / `400 Bad request` (abuse
detection), plus `exit 23` on redirect chains. Don't loop on it — instead:
read `annotations` / `check-runs` for the failing step name, then reproduce
the step locally (same curl/python with proxy env stripped) to get the real
error.

### Spintax Parser Variable Collision Pitfall

When building message automation templates that support both Spintax (`{سلام|درود}`) and template variables (`{username}`, `{first_name}`):
- **Pitfall**: A naive regex `/{([^{}]+)}/g` matches `{username}` as a 1-element list (`['username']`), strips the curly braces, and converts it to literal `username` before variable substitution can run.
- **Fix**: Spintax parser MUST verify that `choices` contains a pipe (`|`) before replacing; otherwise return the original matched text. Substitute template variables first:

```javascript
export function parseSpintax(text) {
  if (!text || typeof text !== 'string') return '';
  const spintaxRegex = /\{([^{}]+)\}/g;
  let prev = '', current = text, iterations = 0;
  while (prev !== current && iterations < 10) {
    prev = current;
    current = current.replace(spintaxRegex, (match, choices) => {
      if (!choices.includes('|')) return match; // protect template variables like {username}
      const options = choices.split('|');
      return options[Math.floor(Math.random() * options.length)] || '';
    });
    iterations++;
  }
  return current;
}
```

### Meta / Instagram Graph API Webhook & Comment-to-DM on Cloudflare Workers

For zero-server Instagram comment-to-DM automation:
See `references/cloudflare-multi-account-and-ig-automation.md` for complete D1 multi-account schemas, Meta Graph API private replies, Persian ZWNJ text normalizers, native Jalali date formatters, and multi-worker Failover / Round-Robin routing patterns.
1. **Webhook Handshake**: `GET /webhook` must respond with status 200 and return `hub.challenge` as plain text when `hub.mode === 'subscribe'` and `hub.verify_token` matches your secret token.
2. **Official Private Reply Endpoint**: Use `POST https://graph.facebook.com/v20.0/{page_id}/messages` with payload `{"recipient": {"comment_id": commentId}, "message": {"text": messageText}}`. This sends a Direct Message in response to a comment without needing an existing 24-hour messaging window.
3. **D1 Deduplication**: Store `comment_id TEXT UNIQUE` in Cloudflare D1. Check existence before processing any comment to ensure no duplicate DM is ever sent.
4. **Self-Reply Guard**: Filter out comments where `commenter_id === account.ig_user_id` or `commenter_username === account.username` to avoid infinite self-trigger loops.
5. **Testing via Python vs curl**: On Windows MSYS/Git-Bash, curl with non-ASCII / Persian strings in `-d` gets character-mangled. When switching to Python `urllib`, Cloudflare blocks the default `Python-urllib` User-Agent with 403 Forbidden — always specify `'User-Agent': 'Mozilla/5.0'`.

## User Rule

Execute full flow once credentials arrive. No intermediate prompts. Do NOT explain steps for the user to do manually — do it all via API/CLI. If one path is blocked (proxy, missing scope), immediately try the next path.

## Frustration Prevention
- **Never ask the user to do manual steps** when you have API/CLI access
- **Never show wrong URLs** — always verify the exact URL format before showing it
- **Never loop on failing tools** — if computer_use fails 3x, switch to terminal
- **Never explain what you can't do** — explain what you DID do and what the result is
- **User expects autonomous execution** — "do it yourself" means "don't ask me to click buttons"
- **Batch progress into ONE message per phase** — during long autonomous jobs, never drip-feed one line per micro-step. Collect the whole phase (what ran, what the result was, what is next) and send it as a single consolidated update; narrating each tool call the user can already see is noise, not progress.