# Cloudflare API Token Permissions — Critical Discovery

## Problem
Standard API token permission groups do NOT contain:
- `Cloudflare Workers → Edit` (does not exist)
- `Cloudflare Pages → Edit` (does not exist)

The exact labels that were tried and failed:
```
☑ Cloudflare Workers — Edit  (NOT FOUND)
☑ Cloudflare Pages — Edit   (NOT FOUND)
```

## Solutions

### Solution 1: Global API Key (RECOMMENDED)
- Go to: https://dash.cloudflare.ae/profile/api-keys
- Use the **Global API Key**, not API Token
- Auth command: `wrangler login --email EMAIL --apikey KEY`
- **Has full access to everything** without any permission group hunting

### Solution 2: Direct Wrangler Auth
```bash
wrangler login  # Opens browser, authenticates, no token needed
```
This bypasses the API token permission problem entirely.

### Solution 3: Try Permission Groups by Exact Name
If using API Token, look for these exact labels (not the ones in docs):
- Account Settings (Read/Edit)
- Workers (may be bundled under something else)
- Pages (may be bundled under something else)

### Solution 4: Separate Tokens Per Service
- Create one token with Workers permissions only
- Create one token with Pages permissions only
- Combine via environment variables

## Finding Available Permission Groups
Without a token, the API endpoint to list available groups is:
```
GET https://api.cloudflare.com/client/v4/user/tokens/permission_groups
Authorization: Bearer {any_token}
```
But this requires at least a valid auth header format. The Global API Key is the most reliable option.

## D1 Database Commands (Wrangler CLI)
```bash
# Create
wrangler d1 create DB_NAME

# Migrations
wrangler d1 migrations create DB_NAME migration_name
wrangler d1 migrations apply DB_NAME --remote

# Query
wrangler d1 execute DB_NAME --remote --command "SELECT * FROM users"
```

## R2 Commands
```bash
# Create bucket
wrangler r2 bucket create BUCKET_NAME

# Upload (via Worker, not CLI)
# Configure in wrangler.toml:
# [[r2_buckets]]
# binding = "MEDIA"
# bucket_name = "BUCKET_NAME"
```

## Wrangler.toml Template
```toml
name = "PROJECT-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"

[[d1_databases]]
binding = "DB"
database_name = "PROJECT_DB"
database_id = "GET_FROM_WRANGLER_CREATE_OUTPUT"

[[r2_buckets]]
binding = "MEDIA"
bucket_name = "BUCKET_NAME"
```

## Critical Values to Save
When `wrangler d1 create` or `wrangler r2 bucket create` runs, save:
- `database_id` from D1 create output
- `bucket_name` you chose
- `account_id` from Cloudflare dashboard footer