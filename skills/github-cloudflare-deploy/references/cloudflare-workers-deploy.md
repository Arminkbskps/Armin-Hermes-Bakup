# Cloudflare Workers (not Pages) — Deploy Reference

## vs Cloudflare Pages

Cloudflare Workers با `wrangler deploy` کار می‌کنه، نه Pages build. Worker فایل‌های static (index.html, assets/) رو از دایرکتوری `dist/` سرو می‌کنه.

## Workflow Structure (`.github/workflows/deploy.yml`)

```yaml
jobs:
  deploy:
    runs-on: ubuntu-latest
    env:
      CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
      CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
      CLOUDFLARE_D1_ID: ${{ secrets.CLOUDFLARE_D1_ID }}
      JWT_SECRET: ${{ secrets.JWT_SECRET }}
      SUPABASE_SECRET_KEY: ${{ secrets.SUPABASE_SECRET_KEY }}
      # Optional:
      GIPHY_API_KEY: ${{ secrets.GIPHY_API_KEY }}

    steps:
      # Step 1: Validate secrets
      - name: Validate deployment settings
        run: |
          : "${CLOUDFLARE_API_TOKEN:?Missing}"
          : "${CLOUDFLARE_ACCOUNT_ACT_ID:?Missing}"
          : "${CLOUDFLARE_D1_ID:?Missing}"
          : "${JWT_SECRET:?Missing}"
          # Storage key: SUPABASE_SECRET_KEY OR SUPABASE_SERVICE_ROLE_KEY
          STORAGE_KEY="${SUPABASE_SECRET_KEY:-${SUPABASE_SERVICE_ROLE_KEY:-}}"
          : "${STORAGE_KEY:?Set SUPABASE_SECRET_KEY or SUPABASE_SERVICE_ROLE_KEY}"
          # GIPHY_ACT_KEY is OPTIONAL (falls back to offline GIFs)

      # Step 2: Replace wrangler.ci.toml placeholders
      - name: Prepare Wrangler config
        run: |
          cp wrangler.ci.toml wrangler.toml
          sed -i "s/__D1_ID__/$CLOUDFLARE_D1_ID/g" wrangler.toml

      # Step 3: Apply D1 schema
      - name: Apply D1 schema
        run: npx wrangler d1 execute amngram-db --remote --yes --file=./schema.sql

      # Step 4: Build dist/ with ALL static assets
      - name: Build static site and secret file
        run: |
          rm -rf dist
          mkdir -p dist/assets
          cp index.html _headers site.webmanifest favicon.ico dist/
          cp -R assets dist/
          # runtime-config.json is built with Node to inject secrets

      # Step 5: Deploy
      - name: Deploy Worker with assets
        run: npx wrangler deploy --config ./wrangler.toml --secrets-file ./secrets.json
```

## Required Secrets

| Secret | Required | Purpose |
|---|---|---|
| `CLOUDFLARE_API_TOKEN` | ✅ | Wrangler auth |
| `CLOUDFLARE_ACCOUNT_ID` | ✅ | Workers/Pages identify |
| `CLOUDFLARE_D1_ID` | ✅ | Database ID |
| `JWT_SECRET` | ✅ | Token signing |
| `SUPABASE_SECRET_KEY` | ✅ | Media upload (Server-side only) |
| `SUPABASE_SERVICE_ROLE_KEY` | ⚡ | Alternative to SUPABASE_SECRET_KEY |
| `GIPHY_API_KEY` | ❌ | GIF search (falls back to offline) |

## File Naming Convention

- **Always**: `site.webmanifest` (NOT `site.manifest`)
- The workflow copies `site.webmanifest` to `dist/`. Using `site.manifest` causes:
  ```
  cp: cannot stat 'site.webmanifest': No such file or directory
  ```

## Supabase Storage for Media Upload

1. Worker uploads media server-side using `SUPABASE_SECRET_KEY`
2. Browser NEVER sees the secret key (upload goes through Worker API)
3. This fixes RLS errors: `new row violates row-level security policy`
4. Bucket `amngram-media` must be Public for direct image/video display

## Wrangler Config (`wrangler.toml`)

```toml
name = "amngram-api"
main = "backend/worker.js"
compatibility_date = "2024-01-01"

[[assets]]
bucket = "./dist"           # static files served from here
include = ["assets/*", "index.worker.js"]
```

## Common Pitfalls

1. **Missing `SUPABASE_SECRET_KEY`**: Upload silently fails, RLS errors in browser
2. **`GIPHY_API_KEY` missing**: GIF search fails → falls back to offline library → user sees no GIFs but no error (optional secret)
3. **Wrong file name `site.manifest`**: Build step fails with file not found
4. **Missing `assets/brand/` in dist**: PWA icons won't load (manifest references them)
5. **D1 schema not applied**: New tables missing → 500 errors on new features