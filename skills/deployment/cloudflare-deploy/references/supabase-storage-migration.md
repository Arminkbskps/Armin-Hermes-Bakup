# Supabase Storage as R2 Alternative

## When to Use
- Cloudflare R2 requires payment method on file (credit card) even for free tier
- User cannot provide payment method (e.g., Iran sanctions, no international card)
- Need S3-compatible storage with public/private buckets
- Free tier: 1 GB storage, 50 GB egress/month on Supabase

## Architecture Changes

### Worker Code (`backend/worker.js`)

**Before (R2):**
```javascript
// Binding in wrangler.toml: [[r2_buckets]] binding = "MEDIA"
await env.MEDIA.put(key, file.stream(), { httpMetadata: {...} });
return { mediaRef: `r2:${key}` };
```

**After (Supabase Storage):**
```javascript
// Env vars: SUPABASE_URL, SUPABASE_ANON_KEY
const arrayBuffer = await file.arrayBuffer();
const uploadRes = await fetch(`${env.SUPABASE_URL}/storage/v1/object/amngram-media/${encodeURIComponent(key)}`, {
  method: "POST",
  headers: {
    "Authorization": `Bearer ${env.SUPABASE_ANON_KEY}`,
    "Content-Type": contentType,
    "x-upsert": "true",
  },
  body: arrayBuffer,
});
return { mediaRef: `supabase:${key}` };
```

### Media URL Resolution

**Before (R2 - signed URLs required):**
```javascript
// Private bucket → signed URLs with HMAC
async function signedMediaUrl(request, env, storedValue) {
  if (storedValue.startsWith("r2:")) {
    const key = storedValue.slice(3);
    const expiresAt = Math.floor(Date.now() / 1000) + 15 * 60;
    const signature = await mediaSignature(key, expiresAt, env.JWT_SECRET);
    return `${origin}/api/media/${key}?exp=${expiresAt}&sig=${signature}`;
  }
}
```

**After (Supabase public bucket - direct URLs):**
```javascript
async function signedMediaUrl(request, env, storedValue) {
  if (storedValue.startsWith("supabase:")) {
    const path = storedValue.slice(9);
    return `${env.SUPABASE_URL}/storage/v1/object/public/amngram-media/${encodeURIComponent(path)}`;
  }
  // Legacy R2 support kept for backward compatibility
}
```

### Wrangler Config (`wrangler.toml`)

```toml
# Remove: [[r2_buckets]] binding = "MEDIA" bucket_name = "amngram-media"
# Add:
[vars]
SUPABASE_URL = "https://<project-ref>.supabase.co"
SUPABASE_ANON_KEY = "__SUPABASE_ANON_KEY__"  # placeholder, real value via secrets
```

### GitHub Actions Workflow (`.github/workflows/deploy.yml`)

```yaml
env:
  # ...existing vars...
  SUPABASE_ANON_KEY: ${{ secrets.SUPABASE_ANON_KEY }}

# In Prepare CI configuration step:
json.dumps({
  'JWT_SECRET': os.environ['JWT_SECRET'],
  'SUPABASE_ANON_KEY': os.environ['SUPABASE_ANON_KEY']
})
```

### Required GitHub Secrets
| Secret | Source |
|--------|--------|
| `SUPABASE_ANON_KEY` | Supabase Dashboard → Settings → API → anon/public key |

## Supabase Setup Steps

1. Create project at https://supabase.com/dashboard
2. Go to Storage → Create bucket: `amngram-media` (public)
3. Copy Project URL and anon key
4. Add secrets to GitHub repo
5. Deploy

## Comparison

| Aspect | R2 | Supabase Storage |
|--------|-----|------------------|
| Payment method | Required | Not required (free tier) |
| Free tier | 10 GB/month | 1 GB storage + 50 GB egress |
| Signed URLs | Required for private | Optional (public bucket = direct URLs) |
| Range requests | Native | Via Supabase CDN |
| Worker integration | Native binding | REST API (`fetch`) |
| Latency (Iran) | Blocked | Works (CDN) |

## Gotchas

1. **Public bucket = anyone with URL can download** — acceptable for chat media
2. **No signed URL expiry** — URL works forever unless object deleted
3. **POST upload endpoint** = `/storage/v1/object/<bucket>/<path>` (not `/object/public/...`)
4. **x-upsert: true** header replaces existing object at same path
5. **Max file size** = 50 MB (Supabase default), configure in bucket settings if needed
6. **CORS** — configure in Supabase Dashboard → Storage → Settings → CORS if needed
7. **`package.json` "type": "module" issue**: If your Node.js build script uses `require()`, save it as `.cjs` extension. The `.js` extension is forced into ESM mode by `"type": "module"` and `require` will throw `ReferenceError`.
8. **D1 schema save issue**: The `database_name` field in `wrangler.toml` is easy to typo (e.g. `Satabase_name`). This causes wrangler parse failure. Double-check the exact field name. 
9. **secret password as `SUPABASE_ANON_KEY` should be set as GitHub Actions Repository Secret** and validated early with `: "${SUPABASE_ANON_KEY:?Missing SUPABASE_ANON_KEY secret}"`