---
name: gdrive-webapp-bridge
description: "Use when uploading files to Google Drive without GCP OAuth."
category: productivity
version: 1.0.0
author: hermes-agent
license: MIT
metadata:
  hermes:
    tags: [gdrive, google-drive, cloud-storage, apps-script, upload, storage-bridge]
---

# Google Drive Web App Bridge

A lightweight, zero-OAuth-credential bridge to upload files from headless agents or disk-constrained environments (Daytona, Codespaces, Docker, minimal VPS) directly into a user's Google Drive via a Google Apps Script Web App.

## When to Use
- User wants the agent to offload files or generated artifacts (PDFs, media, archives, datasets) to their personal Google Drive.
- Standard Google Cloud Console OAuth setup (`google-workspace` skill) is rejected by the user as too complex, requires admin permissions they lack, or fails due to port/redirect issues in headless environments.
- The agent needs a permanent, simple HTTP endpoint to push files without managing expiring OAuth refresh tokens.

## Architecture & How It Works
1. **Google Apps Script (Web App)**: Runs in the user's Google account with Drive permissions. Exposes a public endpoint (`/exec`) that handles HTTP POST.
2. **Payload**: JSON with `filename`, `mimeType`, and `base64` encoded file content.
3. **Storage**: The script automatically finds or creates a dedicated target folder (default: `Hermes_Files`) and writes the file via `DriveApp.getFoldersByName` and `folder.createFile`.
4. **Client Helper**: A tiny Python stdlib script encodes the local file, sends HTTP POST, and receives back `{status: "success", name, url}`.

## Deployment Procedure (Guided User Setup)

Guide the user through these 4 simple steps:

### Step 1: Open Google Apps Script
Direct the user to `https://script.google.com/` and ask them to click **New project**.

### Step 2: Paste the Server Code
Instruct the user to press `Ctrl + A` (or `Cmd + A`) to select all existing template text (`myFunction`), delete it completely, and paste this script:

```javascript
function doPost(e) {
  try {
    var data = JSON.parse(e.postData.contents);
    var rootFolderName = "Hermes_Files";
    var rootFolders = DriveApp.getFoldersByName(rootFolderName);
    var rootFolder = rootFolders.hasNext() ? rootFolders.next() : DriveApp.createFolder(rootFolderName);

    var targetFolder = rootFolder;
    if (data.subfolder) {
      var subFolders = rootFolder.getFoldersByName(data.subfolder);
      targetFolder = subFolders.hasNext() ? subFolders.next() : rootFolder.createFolder(data.subfolder);
    }

    if (data.replace) {
      var existingFiles = targetFolder.getFiles();
      while (existingFiles.hasNext()) {
        var oldFile = existingFiles.next();
        if (!data.filename || oldFile.getName() === data.filename) {
          oldFile.setTrashed(true);
        }
      }
    }

    var decoded = Utilities.base64Decode(data.base64);
    var blob = Utilities.newBlob(decoded, data.mimeType || 'application/octet-stream', data.filename || 'file');
    var file = targetFolder.createFile(blob);
    file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW);

    return ContentService.createTextOutput(JSON.stringify({
      status: "success",
      name: file.getName(),
      url: file.getUrl()
    })).setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({
      status: "error",
      message: err.toString()
    })).setMimeType(ContentService.MimeType.JSON);
  }
}

function doGet(e) {
  return ContentService.createTextOutput("OK");
}
```

### Step 3: Deploy as Web App
1. Click **Deploy** (top right) -> **New deployment**.
2. Click the gear icon -> select **Web app**.
3. Set **Execute as**: `Me` (user's account).
4. Set **Who has access**: `Anyone`.
5. Click **Deploy** and complete authorization:
   - Click *Authorize access* -> Choose Google Account -> Click *Advanced* -> Click *Go to ... (unsafe)* -> Click *Allow*.
6. Copy the resulting **Web app URL** (ending in `/exec`).

### Step 4: Configure Local Agent Helper
Store the endpoint URL in `~/.config/gdrive/endpoint.txt` and install the CLI script `gdrive-upload`:

```bash
mkdir -p ~/.config/gdrive ~/.local/bin
echo "<WEB_APP_URL>" > ~/.config/gdrive/endpoint.txt
```

Python client implementation (`~/.local/bin/gdrive-upload`):
```python
#!/usr/bin/env python3
import sys, os, mimetypes, base64, json, urllib.request

ENDPOINT_FILE = os.path.expanduser("~/.config/gdrive/endpoint.txt")
if not os.path.exists(ENDPOINT_FILE):
    print("Error: endpoint not configured in ~/.config/gdrive/endpoint.txt")
    sys.exit(1)

with open(ENDPOINT_FILE) as f:
    ENDPOINT = f.read().strip()

if len(sys.argv) < 2:
    print("Usage: gdrive-upload <filepath> [custom_filename]")
    sys.exit(1)

filepath = sys.argv[1]
if not os.path.exists(filepath):
    print(f"File not found: {filepath}")
    sys.exit(1)

custom_name = sys.argv[2] if len(sys.argv) > 2 else os.path.basename(filepath)
mime_type, _ = mimetypes.guess_type(filepath)
if not mime_type:
    mime_type = "application/octet-stream"

with open(filepath, "rb") as f:
    content = f.read()

payload = {
    "filename": custom_name,
    "mimeType": mime_type,
    "base64": base64.b64encode(content).decode("ascii")
}

req = urllib.request.Request(
    ENDPOINT,
    data=json.dumps(payload).encode("utf-8"),
    headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0"},
    method="POST"
)

try:
    with urllib.request.urlopen(req, timeout=120) as resp:
        result = json.loads(resp.read().decode("utf-8"))
        print(json.dumps(result, ensure_ascii=False, indent=2))
except Exception as e:
    print(f"Upload failed: {e}")
    sys.exit(1)
```

## Pitfalls & Lessons

- **Leftover boilerplate syntax error**: Google Apps Script starts new projects with `function myFunction() {}`. Users who paste code without clearing the editor end up with an unclosed trailing brace (`SyntaxError: Unexpected token '}'`). Always explicitly instruct the user to select-all (`Ctrl+A`) and delete before pasting.
- **Apps Script Redirects**: Google Apps Script redirects (HTTP 302) POST requests to a script output domain. In Python, `urllib.request.urlopen` automatically follows redirects, but some lower-level HTTP clients lose the POST body on redirect; standard `urllib` or `requests` (with `allow_redirects=True`) handles this seamlessly.
- **Payload Size Limits**: Google Apps Script rejects POST bodies near/above ~50 MB with a generic HTTP 400. Base64 inflates files by ~37%, so a ~38 MB archive becomes a ~51 MB payload and fails — keep the JSON payload under ~45 MB (archive ≤ ~30 MB). Check payload size client-side before sending and abort with a clear error instead of POSTing a doomed request. Keep automated backup archives lean: exclude volatile/heavy paths (session DBs, `*.db-wal`/`*.db-shm`, preview PNGs, caches) from the tar.
- **Cronjob Prompt Safety Filter**: When scheduling automated cron backups with `cronjob_manage`, avoid invisible Unicode characters like ZWNJ (\u200c / نیم‌فاصله) in the prompt argument; the safety scanner blocks them as potential injections. Write clean English/ASCII cron prompts that instruct the agent to deliver in Persian.
- **Never invent the upload URL**: cron prompts for uploads must instruct the agent to copy the URL from the script output verbatim, and to report FAILURE with no link when the upload fails — a guessed Drive URL looks plausible but opens to nothing.
- **New uploads are private by default — links open to "no item"**: after `targetFolder.createFile(blob)` always call `file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW)` before returning `file.getUrl()`, otherwise anyone opening the link (even the owner in another browser) gets a dead page despite `status: "success"`.
- **Updating Existing Web App Code**: When modifying an already deployed Apps Script (e.g. adding subfolder or replace features), saving the file is NOT enough. To update without breaking the client URL: Click **Deploy** -> **Manage deployments** -> click the pencil icon (**Edit**) -> select Version: **`New version`** -> click **Deploy**. The Web App URL remains 100% identical.
- **Local Cleanup**: Immediately remove large local artifacts from disk after a confirmed `status: "success"` response to keep minimal SSD environments unburdened.
- **Private-by-default links look broken ("no item"/sign-in page)**: `file.getUrl()` returns a private URL — call `file.setSharing(DriveApp.Access.ANYONE_WITH_LINK, DriveApp.Permission.VIEW)` right after `createFile` so every upload is link-readable despite `status: "success"`; existing deployments need a New-version redeploy for the fix to take effect.
- **Diagnose a dead Drive link before re-uploading**: fetch the URL anonymously with curl — an HTTP 401 page containing sign-in text means the file exists but is private (fix sharing), not missing. Only re-upload when the file is actually gone or trashed.
- **Automatic Multi-Part Chunking for Archives > 20MB**: Google Apps Script rejects POST bodies near/above ~50 MB with a generic HTTP 400 or silent timeout. Because Base64 inflates binary data by ~37%, raw archives larger than ~22 MB will exceed this execution limit. When an archive exceeds 20 MB (e.g. including extensive PDFs, exam diagrams, or multiple bot databases), do not abort or strip essential files; split the archive into sequential chunks (`CHUNK_SIZE = 20 * 1024 * 1024`), upload each chunk with filename `<filename>.part<N>` and mimeType `application/octet-stream`, and output the standard Unix reassembly command: `cat <filename>.part* > <filename> && tar -xzf <filename>`. Single archives <= 20 MB upload directly as a single file. Keep non-essential bulky files (ephemeral caches, `.mp3`, `.mp4`, `.gif`, `.wav`, socket files) excluded from the tar.
- **Tar never expands globs from a list**: passing `.hermes/*.db` as a subprocess arg without a shell fails with `Cannot stat`. Expand with Python `glob.glob()` first and pass concrete paths to tar.
