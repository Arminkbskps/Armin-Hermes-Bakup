---
name: local-credential-extraction
description: Use when extracting API keys from local desktop apps.
version: 0.1.0
author: Hermes
license: MIT
metadata:
  hermes:
    tags: [credentials, vscode, electron, dpapi, security]
    related_skills: [omniroute-port-conflict-resolution]
---

# Extracting Credentials from Local Desktop Apps

## When to Use

- User asks to find/get/extract the API key or token an app is using (VS Code extension, Electron app, Chromium-based tool).
- User wants to move a key out of one app into another service (e.g. paste a VS Code extension key into 9router/Hermes config).
- Auth debugging where the key must exist locally but isn't in any settings file.

When a user asks "find the API key my extension/app is using" (VS Code, Electron apps, Chromium-based tools), the key is almost never in a settings file — it lives in an OS-backed secret store. This skill covers the Windows/VS Code path, which is the common case.

## Where secrets live (Windows, VS Code)

| What | Location |
|---|---|
| Extension SecretStorage (the usual home for API keys) | `%APPDATA%\Code\User\globalStorage\state.vscdb` → SQLite `ItemTable`, keys named `secret://{"extensionId":"<id>","key":"<name>"}` |
| Extension plaintext config | `%APPDATA%\Code\User\globalStorage\<extension.id>\settings\*.json|yaml` — check first, it is free |
| User/workspace settings | `%APPDATA%\Code\User\settings.json`, `workspaceStorage\*\state.vscdb` (webview state) |
| Encryption key (Electron safeStorage) | `%APPDATA%\Code\Local State` → `os_crypt.encrypted_key` (base64 = `"DPAPI" + DPAPI-blob`) |

Value format quirk: values are JSON-serialized Node Buffers — `{"type":"Buffer","data":[...]}` — decode `bytes(value['data'])` before decrypting.

Ciphertext formats, in check order:
1. Starts with `v10` → Electron safeStorage: nonce = bytes `[3:15]` (12 bytes), ciphertext = `[15:]`, AES-256-GCM, no AAD, key = 32 bytes from `Local State` after stripping the 5-byte `DPAPI` prefix and running `CryptUnprotectData`.
2. Anything else → raw DPAPI blob, `CryptUnprotectData` on the whole buffer.

## Procedure

1. **Find the extension and its key names.** `ls ~/.vscode/extensions/` → open `<pub.name-ver>/package.json` for config properties/commands, then grep `dist/*.js` for `secrets.store`, `secrets.get`, and candidate key names (`apiKey`, `<name>Key`). This tells you the exact secret identifiers AND how the app calls the API (base URL, extra headers) — needed later for verification.
2. **Read the DB read-only:** `sqlite3.connect(f'file:{path}?mode=ro', uri=True)` so a running VS Code is never disturbed.
3. **Decrypt** with `scripts/extract_electron_secrets.py --match <substring>` (prints JSON of key name → plaintext).
4. **Verify against the provider, not just the file:** call the provider's `GET <base>/v1/models` with `Authorization: Bearer <key>` (200 = key valid), then a real `POST <base>/v1/chat/completions`. Optionally probe account endpoints (`/v1/me`, provider-specific) for plan/quota.
5. **Tell the user where any copy landed** (script output file) and offer to delete it — keys written to disk should never be a silent side effect.

Worked example (extraction → verify → triage → 9router onboarding): see [references/ahefi-provider.md](references/ahefi-provider.md).

## Verification: reading the failure

| Result | Meaning |
|---|---|
| `/v1/models` 200, chat 401 | key valid, chat auth differs (wrong header/scheme) |
| `/v1/models` 200, chat 502 `upstream_error` on EVERY model | provider-side outage — key is fine; if the provider exposes a logs/usage API, confirm `error_code: upstream_error` there |
| HTML page instead of JSON | endpoint does not exist (SPA catch-all), not an auth failure — go back to the app's own JS and read which URL it actually calls |
| `http=000` from curl | network layer, not the API: unset `http_proxy https_proxy all_proxy` (a stale local socks proxy env var fails closed) |

## Pitfalls

- **DPAPI is user+machine bound.** Copying the ciphertext (or `Local State`) to another machine/user cannot be decrypted; always decrypt on the box that stored it.
- **ctypes typing:** pass the buffer as `ctypes.cast(ctypes.create_string_buffer(data, len(data)), ctypes.POINTER(ctypes.c_byte))` — handing a `c_char_Array` straight to a `POINTER(c_byte)` field raises `incompatible types`.
- **Big inline heredocs get blocked/truncated.** Write the script with `write_file` and run `python path\to\script.py`; oversized `python - <<'EOF'` payloads hit the command blocklist and giant tool calls hit stream timeouts.
- **Don't persist secrets silently.** If you save a decoded key to disk, name the file in your reply and offer removal (the user must approve deletions).
- **Platform:** this script is Windows-only (DPAPI). On macOS the keychain holds it (`security find-generic-password -s <service> -w`); on Linux Electron uses libsecret/kwallet or falls back to plaintext prefs — check `Local State`/prefs before assuming encryption.
- **Keep tool payloads small** (small script files + short curl probes); oversized single tool calls get dropped before delivery and waste the turn.
