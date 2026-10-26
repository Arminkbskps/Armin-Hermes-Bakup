---
name: github-sync-from-local
description: "Clone a GitHub repo and sync all files from a local folder. Includes AmnGram version upgrade workflow, CI secret management, and verify.mjs fix patterns."
---
# Sync Local Folder → GitHub Repo
Replace all files in a cloned GitHub repo with contents of a local source folder, then commit and push. Use when user says "sync X folder to repo Y" or "upgrade repo from folder Z".

## Key patterns learned from this user's workflows
- Source folders often have **nested structure** (e.g., `D:\Downloads\AmnGram-v5-required-files\AmnGram-v5-required-files\`). Always `ls` the folder first — if you see only one subfolder with the same name, descend one level.
- CI workflow file names must **exactly match** what the workflow expects (e.g., `site.webmanifest`, NOT `site.manifest` or `site.manifest` → rename at copy time).
- Git push can fail with `curl 55 Send failure: Connection was reset` — retry immediately, it usually works.
- CRLF warnings from Windows Git are harmless (just line-ending conversion), push still succeeds.
- After `git commit --amend`, push needs `--force` (requires user approval).
- **Avoid token leakage**: When upgrading or syncing code (like Bale bots or Telegram bots), do not blindly copy template variables, API keys, or admin IDs. Preserve the user's specific credentials from their origin repository or `.env` files.

## Steps
### 1. Probe the source folder structure first
```bash
ls -la /path/to/source/              # check if root has files or only one subfolder
ls -la /path/to/source/SUBNAME/      # descend if nested
```
If the source folder contains only one subfolder with the same name (common with downloaded folders), use the inner path as `SRC`.

### 2. Clone to temp dir (always rm first)
`rm -rf /path/clone && git clone https://ghp_TOKEN@github.com/OWNER/REPO.git /path/clone --depth=1`
On Windows: destination must be empty — git clone into non-empty dir fails.
On Windows: repo is likely already cloned at `D:\tmp\<repo-name>\` — work from there instead of re-cloning.

### 3. Copy ALL files from source to clone
**Do NOT use a hardcoded file list.** Copy the entire tree or copy by subdirectory — check what's actually in the source first.
```python
import shutil, os
src = r"SOURCE_PATH"
dst = r"TEMP_CLONE_PATH"
# Copy the whole tree (most reliable for full-project syncs)
shutil.copytree(src, dst, dirs_exist_ok=True)
print("Done")
```
Or copy subdirectories selectively:
```bash
# Backend
cp 'SRC/backend/worker.js' 'DST/backend/worker.js'
# Assets — replace brand/gifs contents (rm first to remove old files)
rm -rf DST/assets/brand/* && cp SRC/assets/brand/* DST/assets/brand/
rm -rf DST/assets/gifs/* && cp SRC/assets/gifs/* DST/assets/gifs/
cp SRC/assets/css/* DST/assets/css/
cp SRC/assets/js/* DST/assets/js/
```
**Rename files at copy time if needed** (e.g., `cp SRC/site.manifest DST/site.webmanifest`).

### 4. Update preview.html from index.html
`cp index.html preview.html` — always keep these in sync.

### 5. Verify, commit, push
```bash
cd /path/clone && git add -A && git status --short
git commit -m "Descriptive message" && git push origin master
# If push fails with "Connection was reset" or "unexpected disconnect" — retry immediately
git push origin master
# If you amended the commit (e.g., added missing file): git push origin master --force
```
Success = `OLD_SHA..NEW_SHA branch -> branch` in push output.

## Common source→repo file mappings (AmnGram project)
When syncing AmnGram Cloudflare Workers projects, these are the standard files:
- `index.html`, `preview.html` (sync index → preview)
- `backend/worker.js`
- `assets/css/style.css`, `assets/js/script.js`, `assets/js/v6.js`
- `assets/brand/*` (logo, app icons, favicons — replace entire folder)
- `assets/gifs/*` (replace entire folder — includes `library/` subfolder with 200+ GIFs in v6.1+)
- `schema.sql`, `wrangler.toml`, `package.json`, `_headers`, `runtime-config.json`
- `site.webmanifest` (NOT site.manifest — CI expects webmanifest)
- `favicon.ico` (root + assets/brand/)
- `.github/workflows/deploy.yml`
- `preview-desktop.png`, `preview-mobile.png` (v6+)
- `README-AmnGram.md`, `UPGRADE-v6.md` (v6.2+)

## Git push retry & conflict resolution
- Push can fail mid-transfer with **`curl 55 Send failure: Connection was reset`** — retry immediately, it usually succeeds on second try.
- If `git push` is rejected because remote is ahead: `git pull --rebase origin master` then push.
- Merge conflict in docs (e.g. README.md): `git checkout --ours README.md && git add README.md && GIT_EDITOR=true git rebase --continue && git push origin master`.

## npm check failures after sync
After copying files, always run `npm run check` to verify JS syntax. If it fails because `package.json` references a file that doesn't exist in the new source (e.g. `v7.js` was removed):
- Update `package.json` scripts line to only reference files that actually exist in the new source
- Then commit `package.json` alongside the other changes

## Windows pitfalls
- `cp` fails on `D:\\\\Folder With Spaces\\\\` → use Python shutil or single-quoted POSIX paths
- Git SSL errors on `ls-remote` → trust push output
- MSYS paths `/c/Users/` fail → absolute POSIX or Python paths
- Nested source folders → always `ls` first, descend one level if only one subfolder found
- **`cd` auto-descends into subfolders**: `ls -la /d/.../AmnGram-6.2/` can silently descend into a same-named subfolder. Always use **absolute paths in `cp` commands** and verify with `find /d/... -maxdepth 3` before copying.
- **`ls -la` vs Python `os.listdir`**: Terminal `ls -la` and Python's `os.listdir` can show different filesystem views on Windows. Always verify with `ls -la` from terminal. If `ls -la` shows files but `os.listdir` shows empty, trust `ls -la`.
- **Source path naming**: Source folders often have double-nesting (e.g., `AmnGram-v6.5-.../AmnGram-v6.5-.../`). Always `ls -la` first to find the correct inner path.

## `npm run check` failures after sync
After copying files, run `npm run check`. Two common failure types:
1. **Missing file referenced in check script**: New `package.json` references a file not yet in the source. Fix by patching `package.json` scripts line to only reference existing files, then commit it alongside other changes.
2. **Exact-string CSS assertion failures**: `scripts/verify.mjs` uses exact string matching (e.g., `.composer {\n  grid-area: composer;`). If it fails, examine CSS with `cat -A` or `xxd` to see exact whitespace/LF vs CRLF. Run `npm run check` BEFORE `git commit`, not after, so you can fix issues before pushing.