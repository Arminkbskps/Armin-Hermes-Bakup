# AmnGram Upgrade History — All Versions v5→Final

## v6.2→v6.3 (Supabase-Changed-Files)
- **Files changed**: `backend/worker.js` (76KB), `package.json`, `README.md`, `README-v6.3.md`, `UPGRADE-v6.md`, `wrangler.toml`, `.github/workflows/deploy.yml`
- **Key change**: Supabase storage migration (no R2 needed)
- **New file**: `README-v6.3.md` — detailed install/upload troubleshooting guide

## v6.3→v6.5 (Google-SuperAdmin-Changed-Files)
- **Files changed**: `backend/worker.js` (100KB), `index.html` (51KB), `assets/css/style.css` (70KB), `assets/js/v6.js` (95KB), `schema.sql` (10KB), `package.json`, `README.md`, `README-v6.5.md`, `runtime-config.json`, `.github/workflows/deploy.yml`
- **New files**: `README-v6.5.md`, `TEST-REPORT-v6.5.md`, `UPGRADE-v6.5.md`, `docs/AUTH-OPTIONS.md`, `docs/STORAGE-STRATEGY.md`
- **Key features**: Google OAuth, SuperAdmin role
- **schema.sql**: 10KB (new permission/ban tables)
- **workflow size**: 4979 bytes (expanded validation)

## v6.5→Final (AmnGram-Final-Changed-Files)
- **Files changed**: `backend/worker.js` (123KB), `index.html` (60KB), `assets/css/style.css` (87KB), `schema.sql` (14KB), `README.md`, `package.json` (8.0.1), `runtime-config.json` (87 bytes), `site.webmanifest`, `_headers` (1206 bytes), `wrangler.toml`, `.github/workflows/deploy.yml`
- **New files**: `assets/js/v8.js` (22KB), `sw.js` (Service Worker), `assets/locales/ja.json`, `assets/locales/zh.json`
- **Key features**: Service Worker for PWA, Japanese/Chinese locales, v8.js module
- **check fix**: `package.json` referenced `v7.js` which didn't exist → removed from check script

## CI Failures Encountered

| Version | Error | Root Cause | Fix |
|---------|-------|------------|-----|
| v5 | `cp: cannot stat 'site.webmanifest'` | Copied as `site.manifest` | Added `site.webmanifest` file |
| v6 | `GIPHY_API_KEY: Missing GIPHY_API_KEY secret` | New required secret | Made optional — falls back to offline GIFs |
| v6.2 | `[ERROR] R2 bucket ... failed. Enable R2 through Dashboard [code: 10042]` | R2 not enabled in account | Comment out R2 binding in wrangler.toml if unavailable |
| v6.3 | `git push rejected (fetch first)` | CI auto-pushed to master while I was working | `git pull --rebase origin master` + resolve README conflict |

## Secret Audit (GitHub Actions)

| Secret | v5 | v6 | v6.1 | v6.2 | v6.3 | v6.5 | Final |
|--------|----|----|------|------|------|------|-------|
| `CLOUDFLARE_API_TOKEN` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `CLOUDFLARE_ACCOUNT_ID` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `CLOUDFLARE_D1_ID` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `JWT_SECRET` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `SUPABASE_ANON_KEY` | ✅ | ✅ | — | — | — | — | — |
| `SUPABASE_SECRET_KEY` | — | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| `GIPHY_API_KEY` | — | ❌(opt) | ❌(opt) | ❌(opt) | ❌(opt) | ❌(opt) | ❌(opt) |

## Git Workflow Issues
- `git commit --amend` + `--force push` can be necessary when adding a missed file to the previous commit
- Merge conflicts in `README.md` after rebase are common — `git checkout --ours README.md` resolves them
- `push origin master --force` needs user approval but is safe when only you pushed last