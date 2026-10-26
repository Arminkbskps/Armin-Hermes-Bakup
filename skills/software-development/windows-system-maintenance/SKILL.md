---
name: windows-system-maintenance
description: "Disk cleanup and PowerShell-from-MSYS patterns on Windows."
tags: [windows, cleanup, disk, powershell, maintenance, cache]
---

# Windows System Maintenance

## Critical: PowerShell from MSYS/Bash

Hermes terminal runs through MSYS bash on Windows, NOT cmd or PowerShell.
`$_` and `$()` variables get consumed by bash before PowerShell sees them.

**NEVER** use inline `powershell -Command "..."` with PowerShell variables.
**ALWAYS** write a `.ps1` file and execute with `-File`:

```bash
# WRONG — $_ and $() break
powershell -Command "Get-ChildItem | ForEach-Object { $_.Name }"

# RIGHT — write to file first
write_file("cleanup.ps1", "Get-ChildItem | ForEach-Object { ... }")
terminal("powershell -ExecutionPolicy Bypass -File cleanup.ps1")
```

Clean up the .ps1 file after execution.

## Disk Cleanup Methodology

### Step 1: Scan (never delete without scanning first)
- `df -h /c` for disk overview
- PowerShell script (FSO-based) to scan all known cache/temp locations — ready script: `scripts/scan-profile-sizes.ps1`
- Sort by size descending, report top consumers
- Ask user before deleting anything >1GB (unless explicitly told to "just clean it")

Scanning pitfalls (measured in a real 2026-09 session):
- `Scripting.FileSystemObject` (the fast COM route) runs WITHOUT admin: it silently returns **0.00 GB** for protected roots (`C:\Windows`, `C:\Program Files*`, most of `C:\ProgramData`) and throws Access Denied on `C:\Windows\Temp`. A 0.00 on a protected path means "unknown", NEVER "empty" — do not report system dirs as small based on FSO.
- `du -m --max-depth=1 <dir>` in MSYS bash is a reliable fallback for USER dirs (full `AppData\Local` scan ≈ 2-4 min). NEVER run plain `du` on `C:\Windows` or the whole drive — it hangs past any timeout.
- `du -sm dir/*` glob SKIPS dot-directories — it hid a 3 GB `.git` inside `hermes-agent`. Always use `--max-depth=1` on the directory itself, not a `/*` glob.

### Step 2: Categorize
- **Safe to delete**: browser caches, package manager caches, temp files, updater caches
- **NEVER delete**: vm_bundles (Claude Desktop VM), user profiles/data, hermes-agent, system files

### Step 3: Clean (use PowerShell script, not inline commands)
- Write a `.ps1` cleanup script
- **High Performance Deletion**: Do NOT use `Remove-Item -Recurse -Force` or pipe `Get-ChildItem | Remove-Item` for large directory trees (like `uv\cache` or `npm-cache` with 10k+ files) — it is extremely slow in PowerShell and causes timeout aborts (180s+). Instead, use fast .NET directory deletion:
  ```powershell
  try {
      [System.IO.Directory]::Delete($path, $true)
  } catch {
      Remove-Item -LiteralPath $path -Recurse -Force -ErrorAction SilentlyContinue
  }
  ```
- Track freed space per target
- Report total freed at end
- Verify final disk state with `df -h /c` or `Get-PSDrive C`

## Safe Cleanup Targets (Windows)

### OneDrive Cleanup & Disabling (~400-900 MB)
If OneDrive is consuming resources and the user wants it disabled:
1. **Kill running process**: `taskkill /f /im OneDrive.exe` (or via PowerShell `Get-Process`)
2. **Remove from Startup Registry**:
   ```powershell
   Remove-ItemProperty -Path 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Run' -Name 'OneDrive'
   ```
3. **Disable Scheduled Tasks**:
   ```powershell
   Get-ScheduledTask -TaskName *OneDrive* | Disable-ScheduledTask
   ```
4. **Clean up Installers/Updaters**: Delete setup cache files in `AppData\Local\Microsoft\OneDrive\StandaloneUpdater\*` and any `*setup*.exe` recursively. Avoid deleting user data sync folders.

### System & Virtual Memory Files (Large Consumers)
- **Hiberfil.sys (Hibernate File)**: Can take up 10-20+ GB. If the user does not use or support Sleep/Hibernate, this file can be safely removed by turning off Hibernation.
  - *Privilege Limit*: Disabling it requires elevated privileges. Guide the user to run `powercfg.exe -h off` in an **Administrator Command Prompt**.
- **Pagefile.sys / Swapfile.sys (Virtual Memory)**: Windows paging files. These sizes dynamically scale under load. **NEVER** disable or manually delete them, as it causes system instability and crashes.

### Browser Caches (largest — ~4-5 GB total when full)
Chrome cache folder structure:
```
<Chrome User Data>/
  Default/           (Profile 1)
    Cache/
    Code Cache/
    Service Worker/    (biggest — often 1+ GB)
    GPUCache/
    DawnWebGPUCache/
  Profile N/          (additional profiles — same structure)
```
- Path: `C:\Users\<user>\AppData\Local\Google\Chrome\User Data\`
- Firefox: `C:\Users\<user>\AppData\Local\Mozilla\Firefox\Profiles\<profile>\cache2`
- Edge: `C:\Users\<user>\AppData\Local\Microsoft\Edge\User Data\Cache`
- Brave: same structure under BraveSoftware
- Firefox profiles live under `Profiles/<uuid>.<name>/` (name format varies, e.g. `gt4GZKqI.Profile 1`) — always glob `Profiles/*` for `cache2`

**Cleaning browser caches WITHOUT closing the browser works** (measured: ~2.3 GB freed with 25 chrome.exe processes running). Locked entries are expected — delete per-child with a per-file fallback:
```powershell
foreach ($child in (Get-Item -LiteralPath $path -Force).GetFileSystemInfos()) {
    if ($child -is [System.IO.FileInfo]) { try { $child.Delete() } catch {} }
    else {
        try { [System.IO.Directory]::Delete($child.FullName, $true) }
        catch {
            # partially locked dir: delete files individually, then the emptied dirs
            Get-ChildItem $child.FullName -Recurse -Force -File -EA SilentlyContinue |
                ForEach-Object { try { $_.Delete() } catch {} }
            Get-ChildItem $child.FullName -Recurse -Force -Directory -EA SilentlyContinue |
                Sort-Object FullName -Descending | ForEach-Object { try { $_.Delete() } catch {} }
        }
    }
}
```
Targets per browser profile: `Cache`, `Code Cache`, `Service Worker\CacheStorage`, `Service Worker\ScriptCache`, `GPUCache`. NEVER touch `Login Data`, `Cookies`, `IndexedDB`. Ready script: `scripts/clean-browser-caches.ps1`.

### Package Manager & Dev Caches (~5-10 GB total when full)
| Tool     | Cache Path                                    |
|----------|-----------------------------------------------|
| npm      | `AppData\Local\npm-cache`                     |
| uv       | `AppData\Local\uv\cache`                      |
| pip      | `AppData\Local\pip\cache`                     |
| node-gyp | `AppData\Local\node-gyp`                      |
| WinGet   | `AppData\Local\Microsoft\WinGet\Packages`     |

### Temp & Update Files
- User temp: `$env:TEMP` (usually `AppData\Local\Temp`) — expect locked `.tmp` / bun `.node`/`.dll` files from live processes; skip and report the count
- Windows temp: `C:\Windows\Temp` — non-admin gets Access Denied even when enumerating
- Windows Update Download: `C:\Windows\SoftwareDistribution\Download` (often 0.5-1+ GB). **Admin-only** — non-admin workarounds (robocopy over `\\localhost\C$`, self-MIR) hang past timeout; don't attempt. Hand the user this one-liner for an **Administrator** CMD:
  `net stop wuauserv && rd /s /q C:\Windows\SoftwareDistribution\Download && net start wuauserv`
- Recycle Bin: `powershell Clear-RecycleBin -Force` works from MSYS (freed 252 MB in one session) — run it standalone, not chained with slow operations

### Application Caches
- Chrome AI Models & CRX: `AppData\Local\Google\Chrome\User Data\OptGuideOnDeviceClassifierModel`, `component_crx_cache`
- Claude-3p: `AppData\Local\Claude-3p\Cache` only — **NEVER** `vm_bundles` (10+ GB, required by Claude Desktop unless explicitly asked to uninstall it)
- CapCut: `AppData\Local\CapCut\User Data\Cache` and updater stubs in `User Data\Download\*update*.exe*`
- App Updaters: `AppData\Local\upscayl-updater`, `AppData\Local\@opencode-aidesktop-updater`, `AppData\Local\antigravity-updater`, `AppData\Local\chat2api-updater`, `AppData\Local\dolphin_anty-updater` (each 80-240 MB; fully deletable — apps re-download on next update check)

### Known User-Profile Consumers (do not touch, report as "not junk")
Verified on this machine (Radon System profile, 2026-09): `AppData\Roaming\npm` global packages (2+ GB: omniroute ~2 GB, wrangler, gh), `AppData\Local\Programs\Python` (1.3 GB), Claude Code duplicates `.local\bin\claude.exe` + `.claude\downloads\claude-*.exe` (~0.7 GB), parallel Node installs `C:\nvm4w` + `C:\nvm_root` (~2 GB) and `AppData\Local\nvm` (~0.2 GB), `.vscode\extensions` (~0.9 GB), Dolphin Anty browser engine under `Roaming\dolphin_anty\browser` (~0.8 GB), Foxit update patch `.fzip` files. Deleting any of these breaks tools — flag for the user instead.

### Windows Built-in (optional, lower priority)
- Windows Installer: `C:\Windows\Installer` — partial cleanup only (orphaned patches)
- Thumbnails: `AppData\Local\Microsoft\Windows\Explorer\thumbcache_*`

## NEVER Touch
- `C:\Users\<user>\AppData\Local\Claude-3p\vm_bundles` — Claude Desktop VM (10+ GB). Only remove if explicitly asked to uninstall/remove Claude entirely. When doing so, also remove `AppData\Roaming\Claude`, `AppData\Local\AnthropicClaude`, and `AppData\Local\Programs\Claude`. Stop processes `Claude` and `claude-desktop` first.
- `C:\Users\<user>\AppData\Local\hermes` — Hermes agent itself
- `C:\Users\<user>\AppData\Local\<browser>\User Data\<Profile>` (only cache subdirs)
- `C:\Windows\` system directories
- `C:\Program Files\` / `C:\Program Files (x86)\`
- Any user documents, downloads, desktop files

## Reference Data
See `references/cleanup-targets.md` for measured sizes from a real cleanup session (what was freed, what was protected, Chrome cache path mapping).

## Pitfalls
- **Foreground `terminal` timeout cap is 600s** — a full-drive PowerShell `Get-ChildItem -Recurse` scan blows through it every time (verified twice). Scan targeted dirs or use timed `du --max-depth=1`; run known-long scans in `background=true`.
- **Quoting PowerShell from bash destroys `$_` and `$()`** even inside single-quoted `-Command '...'` strings at `$(...)` boundaries — and escaping with `\"` inside `-Command "..."` produces parser errors like `The term '=...' is not recognized`. The ONLY reliable route is the `.ps1` file + `-File` approach (see top of this file).
- `du` is extremely slow on Windows system dirs and hangs silently past timeouts on `C:\Windows\*` — restrict to user profile dirs
- `Remove-Item -Recurse -Force` on large directories (like `uv\cache` or `npm-cache`) takes minutes and times out; always use `[System.IO.Directory]::Delete($path, $true)` with per-child fallback
- In PowerShell, statement `foreach (...) { ... } | ...` throws parser error `EmptyPipeElement`. Use `$($list | ForEach-Object { ... })` or wrap in `$()`
- Some temp files are locked by running processes — skip with `-ErrorAction SilentlyContinue`
- Chrome caches rebuild quickly — cleaning them is safe but the space re-fills within days
- Plain bash `for d in /c/*/; do du -sm "$d"; done` also hangs on system dirs (verified timeout) — never enumerate C:\ root with du
