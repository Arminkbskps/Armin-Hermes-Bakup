---
name: windows-cli-proxy
description: Make CMD/PowerShell route through a local proxy.
---

# Windows CLI Proxy Setup

Configure CMD and PowerShell sessions to use a local proxy (V2RayN, Clash, mitmproxy, etc.) on Windows.

## Trigger

- User asks "make CMD/PowerShell use the VPN"
- User needs `curl`, `git`, `pip`, `npm`, `Invoke-WebRequest` to go through a local proxy
- User has V2RayN / Clash / any local proxy running

## Step 1: Identify the proxy endpoint

Check what ports the proxy has open:

```bash
# Find listening proxy ports (V2RayN typical: 10808)
netstat -ano | grep -E "1080[0-9]" | grep -i listening

# Search proxy config files
ls -la "$LOCALAPPDATA"/v2rayN/guiConfigs/
cat "$LOCALAPPDATA"/v2rayN/guiConfigs/guiNConfig.json  # Look for "Inbound" -> "LocalPort"
cat "$LOCALAPPDATA"/v2rayN/binConfigs/config.json       # Look for "inbounds" -> "port"
```

V2RayN often uses **mixed** protocol (accepts both HTTP and SOCKS5 on the same port).

Common defaults:
| Proxy | HTTP | SOCKS5 |
|-------|------|--------|
| V2RayN | 10808 (mixed) | 10808 (mixed) |
| Clash Verge | 7890 | 7891 |
| mitmproxy | 8080 | — |

## Step 2: Set environment variables (per-session)

### CMD (batch)

```bat
set HTTP_PROXY=http://127.0.0.1:10808
set HTTPS_PROXY=http://127.0.0.1:10808
set ALL_PROXY=socks5://127.0.0.1:10808
set NO_PROXY=localhost,127.0.0.1,::1,10.*,172.16.*,172.17.*,172.18.*,172.19.*,172.20.*,172.21.*,172.22.*,172.23.*,172.24.*,172.25.*,172.26.*,172.27.*,172.28.*,172.29.*,172.30.*,172.31.*,192.168.*
```

### PowerShell

```powershell
$env:HTTP_PROXY  = "http://127.0.0.1:10808"
$env:HTTPS_PROXY = "http://127.0.0.1:10808"
$env:ALL_PROXY   = "socks5://127.0.0.1:10808"
$env:NO_PROXY    = "localhost,127.0.0.1,::1,192.168.*"
# Also configure .NET WebRequest
[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy($env:HTTP_PROXY, $true)
[System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials
```

## Step 3: Create wrapper scripts (for double-click)

### proxy-shell.cmd
```bat
@echo off
set HTTP_PROXY=http://127.0.0.1:10808
set HTTPS_PROXY=http://127.0.0.1:10808
set ALL_PROXY=socks5://127.0.0.1:10808
set NO_PROXY=localhost,127.0.0.1,::1,10.*,172.16.*,172.17.*,172.18.*,172.19.*,172.20.*,172.21.*,172.22.*,172.23.*,172.24.*,172.25.*,172.26.*,172.27.*,172.28.*,172.29.*,172.30.*,172.31.*,192.168.*
cd /d "%%~dp0"
cmd /k
```

### proxy-shell.ps1
```powershell
$ProxyHTTP  = "http://127.0.0.1:10808"
$ProxySOCKS = "socks5://127.0.0.1:10808"
$env:HTTP_PROXY  = $ProxyHTTP
$env:HTTPS_PROXY = $ProxyHTTP
$env:ALL_PROXY   = $ProxySOCKS
$env:NO_PROXY    = "localhost,127.0.0.1,::1,192.168.*"
[System.Net.WebRequest]::DefaultWebProxy = New-Object System.Net.WebProxy($ProxyHTTP, $true)
[System.Net.WebRequest]::DefaultWebProxy.Credentials = [System.Net.CredentialCache]::DefaultCredentials
```

## Step 4 (optional): WinHTTP System Proxy

```bat
:: Set
netsh winhttp set proxy proxy-server="http://127.0.0.1:10808" bypass-list="localhost;127.*;10.*;192.168.*;<local>"
:: Reset
netsh winhttp reset proxy
```

## Step 5 (optional): TUN mode (full system proxy)

For V2RayN:
1. Edit `%LOCALAPPDATA%\v2rayN\guiConfigs\guiNConfig.json`
2. Set `"TunModeItem"."EnableTun": true`, `"Stack": "Mixed"`, `"AutoRoute": true`
3. Restart V2RayN (run as Administrator)

## Reverse: Unset Proxy for Blocked Domains

Sometimes the proxy blocks specific APIs (e.g. `api.cloudflare.com` from Iran). To bypass:

```bash
# Temporarily clear proxy for one command
unset https_proxy http_proxy all_proxy && curl -s "https://api.example.com/..."

# Or in a subshell
(env -u https_proxy -u http_proxy -u all_proxy wrangler whoami)

# In Node.js subprocess (Python)
import os
os.environ.pop('https_proxy', None)
os.environ.pop('http_proxy', None)
```

**Detection**: If `curl` returns empty or `wrangler` says "Invalid access token" despite correct credentials, the proxy is likely blocking the domain.

**Solution hierarchy**:
1. `unset` proxy env vars → works if proxy is env-var-based
2. Add domain to `no_proxy` → `export no_proxy="$no_proxy,api.cloudflare.com"`
3. Use GitHub Actions → runner has no proxy, runs from clean network

## Pitfalls

- **Execution policy**: Use `-ExecutionPolicy Bypass` for `.ps1` scripts, or use `.cmd` instead.
- **Unicode in PS strings**: Persian characters like `"`/`"` (smart quotes) inside double-quoted strings break PowerShell parsing. Stick to ASCII in script messages.
- **`mixed` protocol**: V2RayN's "mixed" inbound = HTTP + SOCKS5 on one port. Use `http://` or `socks5://` on the same port.
- **System Proxy != CLI proxy**: V2RayN's "System Proxy" button only affects browsers, not terminals. Env vars or TUN are needed for CLI.
- **Admin**: WinHTTP and TUN need Administrator; env vars do not.
- **Case sensitivity**: Some tools check `HTTP_PROXY`, others `http_proxy`. Uppercase covers both.
- **Cloudflare API blocked by proxy**: From Iran IPs, `api.cloudflare.com` is often blocked by V2RayN/Clash proxies. Symptom: empty response or `code: 9109`. Fix: unset proxy or use GitHub Actions.
- **Stale PAC URL in Registry**: When V2RayN is used in PAC mode and switched off, a dead PAC URL (e.g. `127.0.0.1:10811`) may linger in `DefaultConnectionSettings`, stalling browser requests. See `references/windows-vpn-diagnostics.md`.
- **Chrome QUIC (UDP 443) hang**: Windows System Proxy only proxies TCP. If the ISP drops foreign UDP, Chrome hangs for 10–20s trying QUIC before falling back. Disable QUIC in `chrome://flags/#enable-quic` or use TUN mode.
- **Filtered node protocols (Reality vs HTTP)**: When mass censorship targets VLESS Reality on port 443 (`Delay: -1` in `guiNDB.db`), switch to surviving HTTP / XHTTP / CDN nodes (e.g. port 2096). Detailed diagnostics in `references/windows-vpn-diagnostics.md`.
- **Commercial VPN Extensions Failure**: Commercial browser extensions (VeePN, ZenMate) lack anti-censorship obfuscation (no uTLS / Reality / XHTTP); their central APIs and datacenter IPs get blacklisted during DPI crackdowns.
- **In-Browser MV3 Proxy Controller**: Use a dedicated Chrome MV3 extension with `chrome.proxy.settings` and `fixed_servers` + domestic bypass list (`*.ir`, local CIDRs) to bridge the browser directly to the local core (e.g. 10808) without Windows WinINet registry interference. See `references/windows-vpn-diagnostics.md`.
- **Standalone In-Browser V2Ray Client & Offline Vazirmatn**: When the user wants to add/manage configs directly inside Chrome rather than keeping the V2RayN GUI open, pair an MV3 extension with a silent local background daemon (`pythonw.exe` on Windows) driving `xray.exe` dynamically on a dedicated port (`20808`). Always bundle Persian fonts (Vazirmatn) locally in `fonts/` so the UI renders properly offline before connection. Full architecture in `references/windows-vpn-diagnostics.md` Section 6.

## Verification

```bash
curl -x http://127.0.0.1:10808 -s --max-time 15 https://httpbin.org/ip
```
Returns the proxy's IP, not the local one.
