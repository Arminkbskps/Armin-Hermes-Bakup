# Windows Cleanup Targets — Measured Sizes (Aug 2026)

Reference data from a real cleanup on a 238GB Windows 10 system.

## Cleanup Results Summary

| Target | Freed |
|--------|-------|
| Chrome Cache (Default + Profile 7) | 3,879 MB |
| Firefox cache2 | 1,013 MB |
| User Temp | 614 MB |
| npm cache | 905 MB |
| uv cache | 670 MB |
| pip cache | 193 MB |
| Claude Cache (not vm_bundles) | 333 MB |
| CapCut Cache + Logs | 712 MB |
| WinGet Packages | 711 MB |
| upscayl-updater | 249 MB |
| **Total** | **~9 GB** |

## Large Protected Items (NOT cleaned)

| Item | Size | Reason |
|------|------|--------|
| Claude-3p vm_bundles | 10.9 GB | Claude Desktop VM, required |
| Chrome User Data (profiles) | 8.98 GB | User data, history, passwords |
| hermes/hermes-agent | 4.5 GB | Hermes agent itself |
| CapCut User Data (non-cache) | ~300 MB | Projects, resources |
| Microsoft Edge Data | 953 MB | Browser profile |
| OneDrive | 799 MB | Sync cache (risky to clear) |

## Chrome Cache Path Mapping

```
C:\Users\<user>\AppData\Local\Google\Chrome\User Data\
├── Default\
│   ├── Cache\              — ~350 MB
│   ├── Code Cache\         — ~530 MB
│   ├── Service Worker\     — ~730 MB (biggest single item)
│   ├── GPUCache\           — ~6 MB
│   └── DawnWebGPUCache\    — ~6 MB
├── Profile 7\
│   ├── Cache\              — ~370 MB
│   ├── Code Cache\         — ~730 MB
│   └── Service Worker\     — ~1120 MB (1.1 GB!)
```

## Notes
- Chrome caches rebuild within days — cleanup is safe but temporary
- WinGet cache regenerates on next `winget install`
- npm/uv/pip caches are pure download caches — 100% safe
- Claude vm_bundles contains rootfs.vhdx (8.3 GB) — never delete
- Firefox cache2 is the only cache dir — clean the whole thing
