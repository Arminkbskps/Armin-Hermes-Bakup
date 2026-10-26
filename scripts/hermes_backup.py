#!/usr/bin/env python3
"""Hermes backup -> Google Drive with automatic multi-part chunking (chunks <=20MB)."""
import os, sys, json, base64, subprocess, urllib.request, glob, time

ENDPOINT_FILE = os.path.expanduser("~/.config/gdrive/endpoint.txt")
with open(ENDPOINT_FILE) as f:
    ENDPOINT = f.read().strip()

TMP = "/tmp/hermes_bak"
os.makedirs(TMP, exist_ok=True)
TS = time.strftime("%Y%m%d-%H%M")
CHUNK_SIZE = 20 * 1024 * 1024  # 20MB per chunk max for Google Apps Script

BASE_EXCLUDES = [
    "--exclude=.hermes/tools", "--exclude=.hermes/cache", "--exclude=.hermes/logs",
    "--exclude=.hermes/models_dev_cache*", "--exclude=*request_dump_*.json",
    "--exclude=.hermes/skills/.hub/*cache*",
    "--exclude=.hermes/state.db-wal", "--exclude=.hermes/state.db-shm",
    "--exclude=*.sock",
    "--exclude=*.mp3", "--exclude=*.mp4", "--exclude=*.gif", "--exclude=*.wav",
]

PATHS = ([".hermes/cron"] + sorted(
    p.replace("/home/daytona/", "") for p in glob.glob("/home/daytona/.hermes/*.db"))
    + [".hermes/skills", ".hermes/sessions",
       ".config/gdrive", ".config/mail", ".config/cloudflare",
       "scripts", "exam_work"])

FNAME = f"Hermes_Backup_{TS}.tar.gz"
archive = f"{TMP}/{FNAME}"
cmd = ["tar", "--use-compress-program=gzip -9", "-cf", archive] + BASE_EXCLUDES + ["-C", "/home/daytona"] + PATHS
r = subprocess.run(cmd, capture_output=True, text=True)
if r.returncode not in (0, 1):
    print(f"Tar failed: {r.stderr[:300]}")
    sys.exit(1)

total_sz = os.path.getsize(archive)
total_mb = total_sz / 1048576
print(f"Total Archive Size: {total_mb:.1f} MB ({total_sz} bytes)")

def upload_chunk(chunk_bytes, filename, mime_type="application/octet-stream"):
    payload = {
        "filename": filename,
        "subfolder": "Hermes_Backups",
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
    print(f"Uploading single file {FNAME}...")
    with open(archive, "rb") as f:
        raw = f.read()
    url = upload_chunk(raw, FNAME, mime_type="application/gzip")
    if not url:
        print("FAILED: Single upload failed")
        sys.exit(1)
    part_urls.append((FNAME, url))
    print(f"SUCCESS: {url}")
    print(f"BACKUP_URL={url}")
else:
    num_parts = (total_sz + CHUNK_SIZE - 1) // CHUNK_SIZE
    print(f"Archive exceeds {CHUNK_SIZE/1048576:.0f}MB limit. Splitting into {num_parts} parts of <= {CHUNK_SIZE/1048576:.0f}MB...")
    with open(archive, "rb") as f:
        for idx in range(1, num_parts + 1):
            chunk = f.read(CHUNK_SIZE)
            part_name = f"{FNAME}.part{idx}"
            chunk_mb = len(chunk) / 1048576
            print(f"Uploading Part {idx}/{num_parts}: {part_name} ({chunk_mb:.1f} MB)...")
            url = upload_chunk(chunk, part_name, mime_type="application/octet-stream")
            if not url:
                print(f"FAILED: Part {idx} upload failed")
                sys.exit(1)
            print(f"Part {idx} uploaded: {url}")
            part_urls.append((part_name, url))

    print(f"ALL {num_parts} PARTS UPLOADED SUCCESSFULLY!")
    for idx, (pname, url) in enumerate(part_urls, 1):
        print(f"PART_{idx}_URL={url}")
    
    links_str = " | ".join(f"[{pname}]({url})" for pname, url in part_urls)
    print(f"BACKUP_URL={links_str}")
    print(f"Restore command: cat {FNAME}.part* > {FNAME} && tar -xzf {FNAME}")

# Cleanup local temporary files
if os.path.exists(archive):
    os.remove(archive)
for p in glob.glob(f"{TMP}/Hermes_Backup_*.tar.gz*"):
    try:
        os.remove(p)
    except Exception:
        pass

sys.exit(0)
