#!/usr/bin/env python3
"""Backup all HidenCloud bot codes, scripts, and databases to Google Drive."""
import os, sys, json, base64, subprocess, urllib.request, glob, time, shutil
from pathlib import Path

ENDPOINT_FILE = os.path.expanduser("~/.config/gdrive/endpoint.txt")
with open(ENDPOINT_FILE) as f:
    ENDPOINT = f.read().strip()

STAGING_DIR = Path("/tmp/hidencloud_staging")
if STAGING_DIR.exists():
    shutil.rmtree(STAGING_DIR)
STAGING_DIR.mkdir(parents=True, exist_ok=True)

TS = time.strftime("%Y%m%d-%H%M")
ARCHIVE_NAME = f"HidenCloud_Bots_Backup_{TS}.tar.gz"
ARCHIVE_PATH = Path("/tmp") / ARCHIVE_NAME
CHUNK_SIZE = 20 * 1024 * 1024  # 20MB per chunk

print("Connecting to HidenCloud via SFTP to download all bot codes...")

# List of items to download
sftp_commands = [
    f"lcd {STAGING_DIR}",
    # Root scripts
    "get bot_mn.py",
    "get check_files.py",
    "get index.js",
    "get main.py",
    "get main_35.py",
    "get requirements.txt",
    "get start.sh",
    "get start_bot_manager.sh",
    "get startup.js",
    "get test_import.py",
    # Directories
    'get -r "Bot"',
    'get -r "Bot 2"',
    'get -r "Bot 3"',
    'get -r "Bot 4"',
    'get -r "Bot 5"',
    'get -r "bots"',
]

sftp_script = "\n".join(sftp_commands) + "\nbye\n"

p = subprocess.Popen(
    ["sftp", "-o", "ProxyCommand=/home/daytona/.ssh/http_proxy.py %h %p",
     "-o", "StrictHostKeyChecking=no", "-P", "2022",
     "h82uygjo3q-155393.8bf3ab98@jacob.hidencloud.com"],
    stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True,
    env={"SSH_ASKPASS_REQUIRE": "force", "SSH_ASKPASS": "/home/daytona/.ssh/askpass.sh", "PATH": "/usr/bin:/bin"}
)

stdout, stderr = p.communicate(input=sftp_script)
print("SFTP finished.")

# Verify downloaded files
downloaded = list(STAGING_DIR.glob("**/*"))
print(f"Total downloaded files/folders: {len(downloaded)}")
for item in sorted(STAGING_DIR.iterdir()):
    if item.is_dir():
        cnt = len(list(item.glob("**/*")))
        print(f" - {item.name}/ ({cnt} items)")
    else:
        print(f" - {item.name} ({item.stat().st_size} bytes)")

# Create tar.gz archive
print("Compressing into tar.gz...")
cmd = [
    "tar", "--use-compress-program=gzip -9", "-cf", str(ARCHIVE_PATH),
    "-C", str(STAGING_DIR), "."
]
subprocess.run(cmd, check=True)

total_sz = ARCHIVE_PATH.stat().st_size
total_mb = total_sz / 1048576
print(f"Archive created: {ARCHIVE_NAME} ({total_mb:.2f} MB)")

def upload_chunk(chunk_bytes, filename, mime_type="application/octet-stream"):
    payload = {
        "filename": filename,
        "subfolder": "HidenCloud_Backups",
        "replace": True,
        "mimeType": mime_type,
        "base64": base64.b64encode(chunk_bytes).decode("ascii")
    }
    data = json.dumps(payload).encode("utf-8")
    for attempt in range(1, 4):
        try:
            req = urllib.request.Request(
                ENDPOINT, data=data,
                headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
                method="POST"
            )
            with urllib.request.urlopen(req, timeout=300) as resp:
                res = json.loads(resp.read().decode())
            if res.get("status") != "success":
                raise RuntimeError(res.get("message", "Unknown error from Apps Script"))
            return res.get("url")
        except Exception as e:
            print(f"Attempt {attempt}/3 for {filename} failed: {e}")
            if attempt < 3:
                time.sleep(4 * attempt)
    return None

part_urls = []
if total_sz <= CHUNK_SIZE:
    print(f"Uploading single archive {ARCHIVE_NAME} to Google Drive...")
    with open(ARCHIVE_PATH, "rb") as f:
        raw = f.read()
    url = upload_chunk(raw, ARCHIVE_NAME, mime_type="application/gzip")
    if not url:
        print("FAILED: Upload failed")
        sys.exit(1)
    part_urls.append((ARCHIVE_NAME, url))
    print(f"SUCCESS: {url}")
else:
    num_parts = (total_sz + CHUNK_SIZE - 1) // CHUNK_SIZE
    print(f"Archive exceeds {CHUNK_SIZE/1048576:.0f}MB limit. Splitting into {num_parts} parts...")
    with open(ARCHIVE_PATH, "rb") as f:
        for idx in range(1, num_parts + 1):
            chunk = f.read(CHUNK_SIZE)
            part_name = f"{ARCHIVE_NAME}.part{idx}"
            chunk_mb = len(chunk) / 1048576
            print(f"Uploading Part {idx}/{num_parts}: {part_name} ({chunk_mb:.1f} MB)...")
            url = upload_chunk(chunk, part_name, mime_type="application/octet-stream")
            if not url:
                print(f"FAILED: Part {idx} upload failed")
                sys.exit(1)
            print(f"Part {idx} uploaded: {url}")
            part_urls.append((part_name, url))

# Cleanup
if ARCHIVE_PATH.exists():
    ARCHIVE_PATH.unlink()
if STAGING_DIR.exists():
    shutil.rmtree(STAGING_DIR)

print("\n" + "="*50)
print(f"HIDENCLOUD BACKUP COMPLETED! ({total_mb:.2f} MB)")
for pname, url in part_urls:
    print(f"LINK: {pname} -> {url}")
print("="*50)

with open("/home/daytona/.config/gdrive/last_hiden_backup.json", "w") as f:
    json.dump({
        "timestamp": TS,
        "archive_name": ARCHIVE_NAME,
        "size_mb": total_mb,
        "parts": part_urls
    }, f, indent=2)

