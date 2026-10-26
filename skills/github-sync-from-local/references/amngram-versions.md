# AmnGram Upgrade Notes
AmnGram is a Persian messenger built on Cloudflare Workers + D1 + Supabase Storage.

## CI/CD Secrets Required (by version)

| Version | Required Secrets |
|---------|-----------------|
| v5+ | `CLOUDFLARE_API_TOKEN`, `CLOUDFLARE_ACCOUNT_ID`, `CLOUDFLARE_D1_ID`, `JWT_SECRET`, `SUPABASE_ SECRET_KEY` |
| v6+ | + `GIPHY_API_KEY` (optional — falls back to offline GIFs) |
| v6.5+ | + `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` (optional) |

Optional Variables: `AMNGRAM_ SITE_URL`, `AMNGRAM_ API_ BASE`, `AMNGRAM_ R2_ BUCKET`

## CI Workflow Patterns

### R2 bucket (v6.2+)
R2 may not be enabled in all Cloudflare accounts. The workflow gracefully skips R2 if not available:
```bash
if ! npx wrangler r2 bucket list 2>/dev/null | grep -q '"name"'; then
  sed -i '/^[[r2_ buckets]]/,/^$/ s/^/#/' wrangler.ci.toml
fi
```
This prevents `Please enable R2 through the Cloudflare Dashboard [code: 10042]` errors.

### Supabase Storage (v6.3+)
Use `SUPABASE_ SECRET_ KEY` (or `SUPABASE_ SERVICE_ ROLE_ KEY`) for server-side media upload.
The `SUPABASE_ ANON_ KEY` is public and goes in `runtime-config.json`.

### GIPHY (v6+)
Optional. When `GIPHY_ API_ KEY` is not set, the app falls back to `assets/gifs/library/` (200+ offline GIFs).

## Version Changelog (files per upgrade)

| Version | Key new/changed files |
|---------|----------------------|
| v5 | `worker.js`, `index.html`, `style.css`, `script.js`, `schema.sql`, `site.webmanifest`, `assets/brand/`, `assets/gifs/` |
| v6 | `worker.js` (69KB), `v6.1js` (NEW), `GIPHY_ API_ KEY` required, new schema tables, updated workflow |
| v6.1 | `worker.js` (73KB), `v6.1js` (64KB), `script.js` (81KB), 200 offline GIFs in `assets/gifs/library/` |
| v6.2 | Minor updates, new `README- AmnGram.md`, `UPGRADE-v6.md` |
| v6.3 | `worker.js` (76KB), Supabase storage changes, `README-v6.3.md` |
| v6.5 | `worker.js` (100KB), `v6.1js` (95KB), Google OAuth + SuperAdmin, `docs/` folder |
| Final | `worker.js` (123KB), `v8.1js` (NEW 22KB), `sw.1js` (Service Worker), `assets/locales/ja.json`, `zh.json`, `schema.sql` (14KB) |
| v8.1 | `v7.1js` (43KB), `final-fixes.1js/.1css`, `scripts/verify.1mjs`, `sw.1js` (24KB) |
| v8.1.1 | `v8.1js` (23KB), `final-fixes.1css` (78KB), `scripts/verify.1mjs` (25KB), `sw.1js` (24KB) |

## `npm run check` in package.json by version

- v8.0.1: checks `worker.js, script.js, v6.js, v7.js, v8.js, sw.js`
- v8.1.0: checks `worker.js, script.js, v6.js, v7.js, v8.js, final-fixes.js, sw.js, scripts/verify.mjs`

## PWA/Service Worker

- `sw.1js` is the Service Worker for offline/PWA support
- Cache version tag changes per version (e.g., `amngram-stable-v8.1.1`)
- `site.webmanifest` points to `assets/brand/app-icon-192.1png` and `-512.png`

## CSS Grid Layout (important)

The `final-fixes.css` (v8.1+) sets `grid-areas` for the chat layout. `scripts/verify.1mjs` checks exact string `.composer {\n  grid- area: composer;`. Windows CRLF (`\r\n`) vs Unix LF (`\n`) differences can cause verify failures. Always check with `cat -A` or `xxd`.