#!/usr/bin/env python3
"""Hermes backup -> GitHub (Repository Sync + Full Release Archive)."""
import os
import sys
import json
import glob
import time
import subprocess
import urllib.request
import urllib.error

CONFIG_FILE = os.path.expanduser("~/.config/backup/github_token.json")
if not os.path.exists(CONFIG_FILE):
    print(f"FAILED: Config file not found at {CONFIG_FILE}")
    sys.exit(1)

with open(CONFIG_FILE) as f:
    cfg = json.load(f)

TOKEN = cfg["token"]
REPO = cfg["full_name"]
TMP = "/tmp/hermes_github_bak"
os.makedirs(TMP, exist_ok=True)
TS = time.strftime("%Y%m%d-%H%M")
TAG_NAME = f"v{time.strftime('%Y.%m.%d-%H%M')}"
RELEASE_TITLE = f"Hermes Backup - {time.strftime('%Y-%m-%d %H:%M UTC')}"
REPO_DIR = os.path.expanduser("~/.local/share/hermes_github_repo")

# 1. Sync human-readable repo tree on main branch
print("==> Syncing git repository tree...")
os.makedirs(REPO_DIR, exist_ok=True)
if not os.path.exists(os.path.join(REPO_DIR, ".git")):
    subprocess.run(["git", "init", "-b", "main"], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "config", "user.name", cfg["username"]], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "config", "user.email", "armin-hermes@agentmail.to"], cwd=REPO_DIR, check=True)
    subprocess.run(["git", "remote", "add", "origin", f"https://{cfg['username']}:{TOKEN}@github.com/{REPO}.git"], cwd=REPO_DIR, check=True)

# Rsync files
def sync_tree():
    # skills
    subprocess.run(["rsync", "-a", "--delete", "--exclude=.hub/*cache*", "--exclude=.locks",
                    os.path.expanduser("~/.hermes/skills/"), os.path.join(REPO_DIR, "skills/")], check=True)
    # scripts
    subprocess.run(["rsync", "-a", "--delete",
                    os.path.expanduser("~/scripts/"), os.path.join(REPO_DIR, "scripts/")], check=True)
    # memories
    subprocess.run(["rsync", "-a", "--delete",
                    os.path.expanduser("~/.hermes/memories/"), os.path.join(REPO_DIR, "memories/")], check=True)
    # cron
    cron_dir = os.path.join(REPO_DIR, "cron")
    os.makedirs(cron_dir, exist_ok=True)
    if os.path.exists(os.path.expanduser("~/.hermes/cron/jobs.json")):
        subprocess.run(["cp", os.path.expanduser("~/.hermes/cron/jobs.json"), cron_dir], check=True)
    # config
    cfg_dir = os.path.join(REPO_DIR, "config")
    os.makedirs(cfg_dir, exist_ok=True)
    for cf in ["config.yaml", "SOUL.md"]:
        src = os.path.expanduser(f"~/.hermes/{cf}")
        if os.path.exists(src):
            subprocess.run(["cp", src, cfg_dir], check=True)
    # exam_work
    if os.path.exists(os.path.expanduser("~/exam_work")):
        subprocess.run(["rsync", "-a", "--delete",
                        os.path.expanduser("~/exam_work/"), os.path.join(REPO_DIR, "exam_work/")], check=True)

sync_tree()

# Update README.md
readme_path = os.path.join(REPO_DIR, "README.md")
with open(readme_path, "w", encoding="utf-8") as f:
    f.write(f"""# Armin Hermes Backup 🛡️

Automated backup repository for **Hermes Agent**.

- **Owner:** [{cfg['username']}](https://github.com/{cfg['username']})
- **Target Repo:** `{REPO}`
- **Last Sync:** {time.strftime('%Y-%m-%d %H:%M:%S UTC')}
- **Sync Interval:** Every 6 hours

---

### 📂 Repository Structure (Main Branch)
- `skills/` — All customized Hermes agent skills & instructions
- `scripts/` — Maintenance, automation & backup scripts
- `memories/` — Core agent persistent memory (`MEMORY.md`, `USER.md`)
- `cron/` — Scheduled jobs configuration (`jobs.json`)
- `config/` — Hermes config and persona definition
- `exam_work/` — Educational materials, solutions & scripts

### 📦 Full System Archives (Releases)
Each 6-hour backup additionally creates a full, standalone compressed `.tar.gz` archive containing all SQLite databases (`state.db`, `kanban.db`, `shared-state.db`), sessions, and runtime states under [Releases](https://github.com/{REPO}/releases).

#### Quick Restore:
```bash
# Download and unpack full archive (replace URL with release asset):
curl -sL -H "Authorization: token $GITHUB_TOKEN" <RELEASE_ASSET_URL> | tar -xzf - -C /home/daytona
```
""")

subprocess.run(["git", "add", "."], cwd=REPO_DIR, check=True)
status_res = subprocess.run(["git", "status", "--porcelain"], cwd=REPO_DIR, capture_output=True, text=True)
commit_sha = "unchanged"
if status_res.stdout.strip():
    subprocess.run(["git", "commit", "-m", f"Hermes Backup - {TS}"], cwd=REPO_DIR, check=True)
    push_res = subprocess.run(["git", "push", "origin", "main"], cwd=REPO_DIR, capture_output=True, text=True)
    rev_res = subprocess.run(["git", "rev-parse", "--short", "HEAD"], cwd=REPO_DIR, capture_output=True, text=True)
    commit_sha = rev_res.stdout.strip()
    print(f"Git commit pushed: {commit_sha}")
else:
    print("Git repository files unchanged.")

# 2. Build full compressed archive for Release
print("==> Building complete system archive (.tar.gz)...")
BASE_EXCLUDES = [
    "--exclude=.hermes/tools",
    "--exclude=.hermes/cache",
    "--exclude=.hermes/logs",
    "--exclude=.hermes/installs",
    "--exclude=.hermes/models_dev_cache*",
    "--exclude=*request_dump_*.json",
    "--exclude=.hermes/skills/.hub/*cache*",
    "--exclude=.hermes/skills/.locks",
    "--exclude=.hermes/state.db-wal",
    "--exclude=.hermes/state.db-shm",
    "--exclude=*.sock",
    "--exclude=*.mp3",
    "--exclude=*.mp4",
    "--exclude=*.gif",
    "--exclude=*.wav",
    "--exclude=.local/share/hermes_github_repo",
    "--exclude=.git",
    "--exclude=node_modules",
]

PATHS = [
    ".hermes/config.yaml",
    ".hermes/SOUL.md",
    ".hermes/memories",
    ".hermes/cron",
    ".hermes/skills",
    ".hermes/sessions",
    ".config/gdrive",
    ".config/mail",
    ".config/cloudflare",
    ".config/backup",
    "scripts",
    "exam_work",
    "bot_edit",
    "bot4_workspace",
    "hermes-showcase"
]

db_paths = [p.replace("/home/daytona/", "") for p in glob.glob("/home/daytona/.hermes/*.db")]
all_paths = [p for p in PATHS + db_paths if os.path.exists(os.path.join("/home/daytona", p))]

ARCHIVE_NAME = f"Hermes_Backup_{TS}.tar.gz"
archive_path = os.path.join(TMP, ARCHIVE_NAME)

tar_cmd = ["tar", "--use-compress-program=gzip -9", "-cf", archive_path] + BASE_EXCLUDES + ["-C", "/home/daytona"] + all_paths
tar_r = subprocess.run(tar_cmd, capture_output=True, text=True)
if tar_r.returncode not in (0, 1):
    print(f"FAILED: Tar failed: {tar_r.stderr[:300]}")
    sys.exit(1)

total_sz = os.path.getsize(archive_path)
total_mb = total_sz / (1024 * 1024)
print(f"Archive Size: {total_mb:.2f} MB ({total_sz} bytes)")

# 3. Create GitHub Release and Upload Asset
print("==> Creating GitHub Release...")
headers = {
    "Authorization": f"token {TOKEN}",
    "Accept": "application/vnd.github.v3+json",
    "User-Agent": "Hermes-Agent"
}

rel_payload = {
    "tag_name": TAG_NAME,
    "target_commitish": "main",
    "name": RELEASE_TITLE,
    "body": f"""### Hermes Agent Full Backup 🛡️

- **Timestamp:** {time.strftime('%Y-%m-%d %H:%M:%S UTC')}
- **Archive File:** `{ARCHIVE_NAME}`
- **Archive Size:** {total_mb:.2f} MB ({total_sz:,} bytes)
- **Git Commit:** `{commit_sha}`

#### Contents:
- SQLite Databases: `state.db`, `kanban.db`, `shared-state.db`
- Full Memory & User Profile (`MEMORY.md`, `USER.md`)
- Complete Skills Directory
- Scheduled Cron Jobs & History
- Custom Scripts & Workspaces

#### Restore Command:
```bash
curl -sL -H "Authorization: token $GITHUB_TOKEN" "https://github.com/{REPO}/releases/download/{TAG_NAME}/{ARCHIVE_NAME}" | tar -xzf - -C /home/daytona
```
""",
    "draft": False,
    "prerelease": False
}

req = urllib.request.Request(
    f"https://api.github.com/repos/{REPO}/releases",
    data=json.dumps(rel_payload).encode("utf-8"),
    headers=headers,
    method="POST"
)

try:
    with urllib.request.urlopen(req) as resp:
        rel_data = json.loads(resp.read().decode())
        release_id = rel_data["id"]
        release_html_url = rel_data["html_url"]
        upload_url_base = rel_data["upload_url"].split("{")[0]
        print(f"Created Release: {release_html_url} (ID: {release_id})")
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"FAILED: Could not create release: {e} - {err_body}")
    if os.path.exists(archive_path):
        os.remove(archive_path)
    sys.exit(1)

# Upload Asset
print(f"==> Uploading {ARCHIVE_NAME} to release...")
with open(archive_path, "rb") as f:
    archive_bytes = f.read()

asset_req = urllib.request.Request(
    f"{upload_url_base}?name={ARCHIVE_NAME}",
    data=archive_bytes,
    headers={
        "Authorization": f"token {TOKEN}",
        "Content-Type": "application/gzip",
        "User-Agent": "Hermes-Agent"
    },
    method="POST"
)

try:
    with urllib.request.urlopen(asset_req, timeout=300) as resp:
        asset_data = json.loads(resp.read().decode())
        asset_url = asset_data["browser_download_url"]
        print(f"Asset uploaded successfully: {asset_url}")
except urllib.error.HTTPError as e:
    err_body = e.read().decode()
    print(f"FAILED: Asset upload failed: {e} - {err_body}")
    if os.path.exists(archive_path):
        os.remove(archive_path)
    sys.exit(1)

# Cleanup local archive
if os.path.exists(archive_path):
    os.remove(archive_path)

# 4. Prune old releases (keep last 28 releases = 7 days of 6h backups)
try:
    list_req = urllib.request.Request(
        f"https://api.github.com/repos/{REPO}/releases?per_page=100",
        headers=headers
    )
    with urllib.request.urlopen(list_req) as resp:
        releases = json.loads(resp.read().decode())
    if len(releases) > 28:
        to_delete = releases[28:]
        print(f"Pruning {len(to_delete)} old releases (keeping newest 28)...")
        for old_rel in to_delete:
            del_id = old_rel["id"]
            del_tag = old_rel.get("tag_name")
            del_req = urllib.request.Request(
                f"https://api.github.com/repos/{REPO}/releases/{del_id}",
                headers=headers,
                method="DELETE"
            )
            urllib.request.urlopen(del_req)
            if del_tag:
                tag_del_req = urllib.request.Request(
                    f"https://api.github.com/repos/{REPO}/git/refs/tags/{del_tag}",
                    headers=headers,
                    method="DELETE"
                )
                try:
                    urllib.request.urlopen(tag_del_req)
                except Exception:
                    pass
except Exception as e:
    print(f"Note: Pruning old releases encountered: {e}")

print("---")
print("SUCCESS: GitHub backup completed.")
print(f"REPO_URL=https://github.com/{REPO}")
print(f"RELEASE_URL={release_html_url}")
print(f"DOWNLOAD_URL={asset_url}")
print(f"ARCHIVE_SIZE_MB={total_mb:.2f}")
print(f"COMMIT_SHA={commit_sha}")
sys.exit(0)
