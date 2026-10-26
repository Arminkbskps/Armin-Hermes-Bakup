---
name: github-cloudflare-deploy
description: "Deploy from GitHub to Cloudflare Pages."
version: 1.0.0
---
# GitHub to Cloudflare Pages Deploy Pipeline
## Step 1 - Create GitHub Repo via Node.js
Use Node.js instead of curl on Windows to avoid shell quoting issues that cause 400/403:
```javascript
const https = require("https");
const TOKEN = process.env.GITHUB_TOKEN;
function ghApi(method, path, body) {
  const data = JSON.stringify(body || {});
  return new Promise((res, rej) => {
    const req = https.request({
      hostname: "api.github.com", path, method,
      headers: { "Authorization": `token ${TOKEN}`, "User-Agent": "Hermes-Deployer", "Accept": "application/vnd.github.v3+json", "Content-Type": "application/json", "Content-Length": Buffer.byteLength(data) }
    }, resp => { let b = ""; resp.on("data", c => b += c); resp.on("end", () => { try { res({ status: resp.statusCode, body: JSON.parse(b) }); } catch { res({ status: resp.statusCode, body: b }); } }); });
    req.on("error", rej); if (data) req.write(data); req.end();
  });
}
async function createRepo(name, desc) {
  const { status, body } = await ghApi("POST", "/user/repos", { name, description: desc || "", private: false });
  if (status === 201) console.log("Created:", body.html_url);
  else console.error("Error:", status, JSON.stringify(body));
}
createRepo("my-project", "Description");
```
Must have: `User-Agent` (prevents 403) + `Content-Length` via `Buffer.byteLength(data)` (prevents 400).
## Step 2 - Git Push
```bash
cd "/e/Armin/develop/Full/Path/To/Project"   # full path on Windows, quoted
git init
git remote add origin "https://$GITHUB_TOKEN@github.com/OWNER/REPO.git"
git add -A; git commit -m "Initial commit"; git branch -M main; git push -u origin main
```
Windows MSYS paths (/e/ARMIN~1/...) are unreliable. Use quoted full paths. If push fails with schannel handshake error, the remote URL is corrupted. Fix: `git remote set-url origin https://TOKEN@github.com/OWNER/REPO.git`
## Step 3 - Cloudflare Pages
1. Go to dash.cloudflare.com > Workers & Pages > Create application > Pages > Connect to Git
2. Authorize GitHub, select repo, build command empty for pure HTML
3. Deploy -> URL: https://project-name.pages.dev
Alternative via Wrangler: `npx wrangler pages project create my-project --production-branch main`
## Free tier: 500 build mins/mo, unlimited sites, auto SSL, branch previews.
## Pitfalls
1) No User-Agent=403, 2) No Content-Length=400, 3) Windows curl use Node.js, 4) git remote corruption fix the URL, 5) push ≠ live — fetch a live asset URL and expect HTTP 200 before announcing a deploy, red Actions mean nothing shipped, 6) Cloudflare API `Authentication error [code: 10000]` on every call means the CLOUDFLARE_API_TOKEN in GitHub secrets is invalid — resync it, don't redeploy blindly, 7) npm ECONNRESET behind proxy env vars — curl the registry direct vs via proxy, and when direct works unset the proxy vars for that command, 8) Pages create `Subdomain is blocked [code: 8000030]` means the account is flagged for Pages creation, not a bad name — stop Cloudflare attempts and migrate the same static folder to GitHub Pages, 9) Never ship proxy/VPN Workers (VLESS/Trojan) on a fresh clean account — that class gets accounts flagged; keep risky workloads off accounts that must stay healthy for Pages, 10) GitHub Pages serving stale Jekyll content means `build_type` is `legacy` — PUT `/repos/{owner}/{repo}/pages` `{"build_type":"workflow"}` then re-run the Actions deploy, 11) Cloudflare Pages rate limits `[code: 10429]` or edge SNI/SSL connection resets: when `npx wrangler pages deploy` fails with code 10429 or the `.pages.dev` domain encounters TLS handshake resets, activate GitHub Pages immediately on the repo via `POST /repos/{owner}/{repo}/pages` (with payload `{"source": {"branch": "main", "path": "/"}}`). GitHub Pages builds in ~30s and serves live at `https://{owner}.github.io/{repo}/{path}/` without Cloudflare Pages rate limits.

## Cloudflare Workers (Workers+assets, not Pages)
For projects that serve static frontend via `backend/worker.js` + `dist/` directory:
- See `references/cloudflare-workers-deploy.md` — covers Workers-specific workflow, D1 schema, Supabase upload, PWA manifest, secrets, and pitfalls
- **Critical**: use `site.webmanifest` (NOT `site.manifest`) — workflow copies it to `dist/`
- **Upload fix**: Supabase media upload must go through Worker (server-side) with `SUPABASE_SECRET_KEY` — browser-side upload with `SUPABASE_ANON_KEY` causes RLS errors
- **GIPHY**: `GIPHY_API_KEY` secret is optional; falls back to `assets/gifs/library/` offline catalog
- **D1 schema**: tables use `CREATE TABLE IF NOT EXISTS` — safe to re-run on every deploy

## Private Repo as a Database (Frontend-only Serverless)
For serverless sites needing a simple persistent datastore without backend infrastructure (like a high-score leaderboard):
1. **GitHub Rest API + Private Repo:** Create a private repo with a JSON file (e.g., `leaderboard.json`).
2. **Access:** Use a Personal Access Token (PAT) with repo scope. *(Warning: Storing PATs in frontend JS is a severe security risk for public sites; use this only for constrained, low-risk, or single-user environments where the token exposure is acceptable or obfuscated).*
3. **Read/Write Flow:** Fetch the file via the REST API (`/repos/OWNER/REPO/contents/FILE`) to get the current content and `sha`. Decode the Base64 content (`decodeURIComponent(escape(atob(data.content)))`), update it locally, encode it back to Base64 (`btoa(unescape(encodeURIComponent(JSON.stringify(data))))`), and PUT it back to the API using the required `sha`.