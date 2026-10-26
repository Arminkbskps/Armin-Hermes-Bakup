# AmnGram Session Fixes

## Initial Setup (v3.1-v5) — 2026-08-01/02

### Context
Deploying AmnGram (Persian/Arabic RTL messenger) to Cloudflare Workers + D1 + Supabase Storage via GitHub Actions. User in Iran with proxy blocking direct Cloudflare API access.

### Initial State
- Repo: `Armin13891219A/AmnGram` 
- Branch: `master`
- Fixed files provided via zip/folder attachment
- GitHub PAT with `repo` + `workflow` scopes available

### Issues Encountered & Fixes

#### 1. Missing `CLOUDFLARE_D1_ID` secret
**Error**: `Missing CLOUDFLARE_D1_ID secret`
**Fix**: Created D1 database via wrangler, extracted UUID, added as GitHub secret

#### 2. Invalid API Token (Global API Key instead of Custom Token)
**Error**: `Invalid access token [code: 9109]`
**Fix**: Created Custom API Token with permissions: D1/R2/Pages/Workers Edit + User Details Read

#### 3. Wrangler config file path resolution
**Error**: `The entry-point file at "backend/worker.js" was not found`
**Root cause**: `wrangler.ci.toml` written to `$RUNNER_TEMP` but `working-directory: ${{ github.workspace }}` — wrangler resolves `main = "backend/worker.js"` relative to config file location
**Fix**: Write config and secrets to `${GITHUB_WORKSPACE}`

#### 4. R2 requires payment method
**Error**: `Please enable R2 through the Cloudflare Dashboard [code: 10042]`
**Fix**: Migrated to Supabase Storage (free, no payment method)
- Removed `[[r2_buckets]]` from wrangler.toml
- Added `SUPABASE_URL` + `SUPABASE_ANON_KEY` vars
- Updated worker.js to use Supabase REST API (`fetch` to `/storage/v1/object/...`)
- Media URLs now direct public Supabase URLs (no signed proxy needed)

#### 5. YAML heredoc syntax error
**Error**: `Invalid workflow file: .github/workflows/deploy.yml#L109` — Node.js heredoc inside YAML
**Fix**: Moved inline Node script to `scripts/build-config.cjs` (`.cjs` extension for CommonJS)

#### 6. Node.js ESM vs CommonJS
**Error**: `ReferenceError: require is not defined in ES module scope`
**Root cause**: `package.json` has `"type": "module"` but build script used `require()`
**Fix**: Rename script to `.cjs` extension

#### 7. Python placeholder substitution silently failed
**Problem**: Python heredoc approach didn't replace `__D1_ID__`, `__SITE_URL__`, `__SUPABASE_ANON_KEY__` — no error, just passed through
**Fix**: Replaced with `sed` commands + `cat wrangler.ci.toml` for verification

#### 8. Wrong Pages URL format
**Error**: `ERR_CONNECTION_CLOSED` for `https://amngram.pages.dev`
**Fix**: Pages projects are at `<project>.<account>.pages.dev` → `https://amngram.armin13891219.pages.dev`

#### 9. wrangler.toml typo: `Satabase_name` vs `database_name`
**Error**: `binding DB of type d1 must have a valid database_id specified [code: 10021]`
**Fix**: Corrected field name in wrangler.toml

#### 10. Secret validation missing
**Added**: Early validation step with bash parameter expansion for all required secrets

## Version Upgrade Chain (v5 → v6 → v6.1 → v6.2 → v6.3)

Each cycle: user provides a folder with changed files, copy them into repo, fix CI failures, push.

### Step-by-Step File Replacement Pattern

```bash
SRC='/d/System File/Downloads/AmnGram-v6.x-Folder/AmnGram-v6.x-Subfolder'
DST='D:/tmp/amngram-raw'

# Root files
cp "$SRC/index.html" "$DST/index.html"
cp "$SRC/favicon.ico" "$DST/favicon.ico"
cp "$SRC/site.webmanifest" "$DST/site.webmanifest"
cp "$SRC/runtime-config.json" "$DST/runtime-config.json"
cp "$SRC/_headers" "$DST/_headers"
cp "$SRC/package.json" "$DST/package.json"
cp "$SRC/wrangler.toml" "$DST/wrangler.toml"
cp "$SRC/schema.sql" "$DST/schema.sql"
cp "$SRC/README.md" "$DST/README.md"

# Backend + JS/CSS
cp "$SRC/backend/worker.js" "$DST/backend/worker.js"
cp "$SRC/assets/css/style.css" "$DST/assets/css/style.css"
cp "$SRC/assets/js/script.js" "$DST/assets/js/script.js"
cp "$SRC/assets/js/v6.js" "$DST/assets/js/v6.js"  # if present

# Brand + GIFs (replace entirely)
rm -rf "$DST/assets/brand/"* && cp "$SRC/assets/brand/"* "$DST/assets/brand/"
rm -rf "$DST/assets/gifs/"*  && cp -r "$SRC/assets/gifs/"* "$DST/assets/gifs/"

# Workflow
cp "$SRC/.github/workflows/deploy.yml" "$DST/.github/workflows/deploy.yml"

# Mirror preview.html
cp index.html preview.html

# Verify + push
npm run check
git add -A
git commit -m "Sync with AmnGram v6.x: ..."
git push origin master
```

### Pitfall: `site.manifest` vs `site.webmanifest`

The workflow copies `site.webmanifest` (PWA manifest). If the upgrade folder has `site.manifest`, copy and rename:
```bash
cp source/site.manifest dest/site.webmanifest
```
Otherwise CI fails: `cp: cannot stat 'site.webmanifest': No such file or directory`

### Pitfall: `preview.html` Must Be Synced

`preview.html` is a separate tracked file that must mirror `index.html`. After every `index.html` replacement:
```bash
cp index.html preview.html
```

### Pitfall: `&` vs `&&` in Windows/MSYS Shell

Using `&&` chains `cp` commands correctly. Using `&` at line end causes MSYS to interpret it as shell background operator → Hermes foreground terminal rejects the command with `Foreground command uses '&' backgrounding`.

**WRONG**: `cp "$SRC/file" "$DST/file" &`
**RIGHT**: `cp "$SRC/file" "$DST/file" && cp "$SRC/file2" "$DST/file2" && echo "done"`

Or put each copys in its own terminal() call.

### GitHub Rebase After CI Modifies README.md

When `git push` is rejected because the remote has new commits (e.g. workflow auto-updated README):

```bash
# In repo
git pull --rebase origin master

# If README.md conflicts:
git checkout --ours README.md
git add README.md
GIT_EDITOR=true git rebase --continue

git push origin master
```

The `--ours` side is the local (just-committed) version.

### CI Failure: `GIPHY_API_KEY` Missing

**Error**: `GIPHY_API_KEY: Missing GIPHY_API_KEY secret`
**Root cause**: v6+ added GIPHY integration. The validate step does `: "${GIPHY_API_KEY:?...}"` which fails if secret isn't set.
**Fix**: Remove that check line and add a comment:
```yaml
# WRONG
: "${GIPHY_API_KEY:?Missing GIPHY_API_KEY secret}"

# RIGHT
# GIPHY_API_KEY is optional (falls back to offline GIFs)
```

### CI Failure: R2 Bucket Not Enabled

**Error**: `Please enable R2 through the Cloudflare Dashboard. [code: 10042]`
Blocks both `wrangler r2 bucket create` AND `wrangler deploy` (because `wrangler.toml` has `[[r2_buckets]]`).

**Fix**: Two changes needed:

1. **Make R2 bucket creation non-fatal** (warning only):
```yaml
- name: Ensure R2 media storage
  run: |
    if npx wrangler r2 bucket list 2>/dev/null | jq -e ...; then
      echo "already exists"
    else
      if npx wrangler r2 bucket create "bucket" 2>/dev/null; then
        echo "created"
      else
        echo "::warning::R2 not available, skipping..."
      fi
    fi
```

2. **Comment out R2 binding in CI config** if R2 not available:
```yaml
- name: Prepare Wrangler config
  run: |
    cp wrangler.toml wrangler.ci.toml
    sed -i "s/__D1_ID__/$CLOUDFLARE_D1_ID/g" wrangler.ci.toml
    if ! npx wrangler r2 bucket list 2>/dev/null | grep -q '"name"'; then
      echo "R2 not available, commenting out R2 binding"
      sed -i '/^\[\[r2_buckets\]\]/,/^$/ s/^/#/' wrangler.ci.toml
    fi
```

## Final Working Configuration

### Required GitHub Secrets

| Secret | Description |
|--------|-------------|
| `CLOUDFLARE_API_TOKEN` | Custom token with D1/R2/Pages/Workers Edit + User Details Read |
| `CLOUDFLARE_ACCOUNT_ID` | From Workers & Pages dashboard |
| `CLOUDFLARE_D1_ID` | UUID from `wrangler d1 list` |
| `JWT_SECRET` | 32+ char random string (`openssl rand -base64 48`) |
| `GIPHY_API_KEY` | Optional — without it, app uses offline GIFs |

### Optional Variables

| Variable | Default |
|----------|---------|
| `AMNGRAM_SITE_URL` | `https://amngram-api.armin13891219.workers.dev` |
| `AMNGRAM_API_BASE` | (empty, auto-detected) |

### `npm run check` Command

Project defines: `"check": "node --check backend/worker.js && node --check assets/js/script.js && node --check assets/js/v6.js"`

Always run before commit to catch syntax errors early.

## Lessons for Future

- Always verify exact filename casing (`site.webmanifest` not `site.manifest`, `_headers` with underscore)
- Mirror `preview.html` after any `index.html` change
- Validate secrets early with `: "${SECRET:?msg}"` but mark optional ones with comments
- Make new API integrations (GIPHY, R2) gracefully degrade
- When the workflow checks for a resource (e.g. R2) and it fails, **also** disable its binding in wrangler config before deploy
- Use `&&` chains (not `&`) for cp on MSYS/Windows
- Run `npm run check` before every commit
- Do `git pull --rebase` before push when remote has new commits
- Execute full flow autonomously — user expects no manual steps