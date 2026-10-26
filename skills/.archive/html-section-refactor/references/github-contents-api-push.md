# GitHub Contents API — File Push Fallback

When `git push` fails (proxy, firewall, network), upload files via the GitHub Contents API.
Especially relevant for single-file HTML projects deployed to GitHub Pages.

## Pattern (Python via execute_code)

```python
import base64, json, os
from hermes_tools import terminal

# 1. Get current file SHA (required for updates)
result = terminal(
    'curl -s -H "Authorization: token $TOKEN" '
    '"https://api.github.com/repos/OWNER/REPO/contents/index.html"'
)
sha = json.loads(result["output"]).get("sha", "")

# 2. Build payload as JSON FILE (not shell variable — large b64 gets truncated)
with open("local_file.html", "rb") as f:
    b64 = base64.b64encode(f.read()).decode()

payload = {"message": "update", "content": b64, "sha": sha, "branch": "main"}
with open("_payload.json", "w") as f:
    json.dump(payload, f)

# 3. Upload via curl -d @file
result = terminal(
    'curl -s -X PUT '
    '-H "Authorization: token $TOKEN" '
    '-H "Content-Type: application/json" '
    '-d @_payload.json '
    '"https://api.github.com/repos/OWNER/REPO/contents/index.html"'
)

# 4. Verify size matches
result = terminal(
    'curl -s -H "Authorization: token $TOKEN" '
    '"https://api.github.com/repos/OWNER/REPO/contents/index.html"'
)
remote_size = json.loads(result["output"]).get("size", 0)
local_size = os.path.getsize("local_file.html")
assert remote_size == local_size, f"Size mismatch: {remote_size} vs {local_size}"
```

## Critical Pitfalls

1. **SHA required for updates** — omitting it returns `"sha" wasn't supplied`
2. **Never inline base64 in shell variables** — shell expansion truncates large strings silently (52KB file → 3KB upload). Always write the JSON payload to a file and use `-d @file`. This is especially important for `.html` files which frequently exceed variable length limits on Windows bash/MSYS when base64 encoded.
3. **Always verify upload size** — compare API `size` field to local `os.path.getsize()`.
4. **Omit SHA for new files** — only existing files need the current SHA.
