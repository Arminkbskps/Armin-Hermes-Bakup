# Windows VPN & Proxy Diagnostics

Detailed reference for diagnosing and fixing broken VPN / proxy connections on Windows (V2RayN, Clash, Sing-box, Hiddify) under hostile network / censorship conditions.

## 1. Stale PAC URL in Registry (Port 10811 Hang)

### Symptom
Browsers (Chrome, Edge) spin indefinitely on page load or return `ERR_PROXY_CONNECTION_FAILED`, even when V2RayN / Xray is listening on port 10808.

### Cause
When V2RayN or another proxy tool is run in PAC mode, it starts a local PAC server (typically on `127.0.0.1:10811`). If PAC mode is switched off or the proxy restarts, the binary blob in:
`HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections\DefaultConnectionSettings`
and `SavedLegacySettings` can retain the stale PAC URL `http://127.0.0.1:10811/pac...`.
Windows WinINet applications stall on every new connection trying to fetch the non-existent PAC file before timing out.

### Diagnosis
```bash
# Check if 10811 is listening
netstat -ano | grep 10811

# Check registry connections blob
reg query "HKCU\Software\Microsoft\Windows\CurrentVersion\Internet Settings\Connections"
```

### Fix
Remove `AutoConfigURL` and clean WinINet settings:
```powershell
$regPath = 'HKCU:\Software\Microsoft\Windows\CurrentVersion\Internet Settings'
Set-ItemProperty -Path $regPath -Name ProxyEnable -Value 1
Set-ItemProperty -Path $regPath -Name ProxyServer -Value '127.0.0.1:10808'
Remove-ItemProperty -Path $regPath -Name AutoConfigURL -ErrorAction SilentlyContinue
```

---

## 2. QUIC / HTTP/3 UDP 443 Drop (Chrome Hang in System Proxy Mode)

### Symptom
Chrome or Edge spins on "Connecting..." or "Establishing secure connection..." for 10–20 seconds when loading Google, YouTube, or Cloudflare sites, and sometimes errors out with `ERR_QUIC_PROTOCOL_ERROR` or `ERR_CONNECTION_TIMED_OUT`.

### Cause
- Windows System Proxy (HTTP/SOCKS via WinINet) **only handles TCP traffic**. It does not intercept UDP.
- Chrome uses QUIC (HTTP/3 over UDP port 443) by default.
- Censored ISPs (e.g. Iranian operators like Rightel, MCI, Irancell) frequently blackhole or drop foreign UDP 443 packets.
- Chrome attempts UDP first, hangs waiting for timeout, and only then falls back to TCP.

### Fix
1. **Disable QUIC in Chrome:**
   Navigate to `chrome://flags/#enable-quic` -> Set to **Disabled** -> Relaunch Chrome.
2. **OR switch VPN client to TUN Mode:**
   TUN mode creates a virtual network adapter (Wintun) that intercepts all UDP + TCP at the network layer and routes it through the proxy tunnel.

---

## 3. Local DNS Poisoning & IPv6 Leak

### Symptom
Browser shows censorship landing pages (e.g. `10.10.34.35` / Peyvandha) or `ERR_NAME_NOT_RESOLVED` despite VPN being active.

### Cause
In System Proxy mode, apps or the OS may perform local DNS lookups against the physical adapter's DNS server (e.g. mobile hotspot `10.x.x.x`). The ISP resolver poisons domain queries. Additionally, if IPv6 is enabled on the physical adapter, poisoned IPv6 records (e.g. `2001:4188:...`) take precedence in Windows 11 Happy Eyeballs algorithm.

### Diagnosis
```powershell
# Test local DNS resolution
Resolve-DnsName -Name 'youtube.com' -ErrorAction SilentlyContinue

# Check IPv6 binding on adapters
Get-NetAdapterBinding -ComponentID ms_tcpip6 | Select-Object Name, Enabled
```

### Fix
- Enable TUN mode in V2RayN / Sing-box / Hiddify so DNS is handled via remote DoH or FakeDNS.
- Disable IPv6 on the active physical adapter if the ISP returns poisoned AAAA records:
```powershell
Disable-NetAdapterBinding -Name "Wi-Fi" -ComponentID ms_tcpip6
```

---

## 4. V2RayN SQLite DB Inspection (`guiNDB.db`)

When mass filtering blocks a protocol class (e.g. VLESS Reality port 443 blocked by SNI/TLS fingerprinting), inspect V2RayN's internal database to find surviving configs.

### DB Location
`%LOCALAPPDATA%\v2rayN\guiConfigs\guiNDB.db` or `<v2rayN-install-dir>\guiConfigs\guiNDB.db`

### Python Query Script
```python
import sqlite3

db_path = "D:/System File/Apps File/Apps File/v2rayN-windows-64/guiConfigs/guiNDB.db"
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Check subscriptions
subs = cursor.execute("SELECT id, remarks, url, autoUpdateInterval, updateTime FROM SubItem").fetchall()
for s in subs:
    print("Sub:", s)

# Find configs with working latency (delay > 0)
rows = cursor.execute("""
    SELECT p.Remarks, p.Address, p.Port, p.ConfigType, e.Delay
    FROM ProfileItem p
    LEFT JOIN ProfileExItem e ON p.IndexId = e.IndexId
    WHERE e.Delay > 0
    ORDER BY e.Delay ASC
    LIMIT 20
""").fetchall()

for r in rows:
    print(r)
```
- `e.Delay == -1`: Node is dead or filtered (connection timeout).
- If all Reality nodes on port 443 show `-1`, look for `HTTP` / `XHTTP` / `CDN` nodes on alternate ports (e.g. 2096, 80) which often bypass TLS/SNI inspection.

---

## 5. Commercial Browser VPN Extensions Failure Mode (VeePN, ZenMate, SetupVPN)

### Symptom
Browser VPN extensions (e.g. VeePN) stop connecting entirely during censorship crackdowns, failing to load server lists or throwing continuous connection errors.

### Cause
- Commercial browser VPNs rely on plain HTTPS/WSS proxies or standard OpenVPN/WireGuard tunnels routed to central API endpoints (e.g. `api.veepn.com`) and static public datacenter IP pools.
- They have **zero anti-censorship obfuscation** (no uTLS fingerprint spoofing, no Reality, no XHTTP, no packet fragmentation).
- When national firewalls tighten filtering, central API hostnames and entire ASN IP blocks of these VPN services are blacklisted at the perimeter. The extension cannot reach its backend even to fetch server lists.

---

## 6. Standalone In-Browser V2Ray Client Architecture (Chrome Extension + Local Daemon)

When the user wants to paste/import configs (`vless://`, `vmess://`, `trojan://`, `ss://`, or subscription URLs) directly into the browser extension rather than managing a heavy desktop GUI like V2RayN:

### The Architectural Constraint
Chrome Manifest V3 extensions **cannot create raw TCP/UDP sockets** and cannot forge TLS ClientHello handshakes in pure JavaScript. Chrome's `chrome.proxy.settings` API only speaks to standard proxy protocols (`http`, `https`, `socks5`).

### Solution: Hybrid Extension + Silent Background Core Controller
1. **Chrome Extension (Frontend & Routing):**
   - Built with Manifest V3.
   - Embeds **offline Persian font (Vazirmatn)** in `fonts/` so fonts never depend on blocked CDNs before connection.
   - Manages UI: power switch, live ping, mode switcher (Smart Bypass IR vs Global), and config list.
   - Sets Chrome proxy via `chrome.proxy.settings.set`:
     ```javascript
     chrome.proxy.settings.set({
       value: {
         mode: "fixed_servers",
         rules: {
           singleProxy: { scheme: "socks5", host: "127.0.0.1", port: 20808 },
           bypassList: ["<local>", "*.ir", "*aparat.com*", "*digikala.com*", "*bank*", "10.*", "192.168.*"]
         }
       },
       scope: "regular"
     });
     ```
2. **Local Daemon (`daemon.py` via `pythonw.exe` on Windows):**
   - Runs silently without a console window on `127.0.0.1:28888` (REST API).
   - Endpoints:
     - `POST /api/parse`: Decodes `vless://`, `vmess://`, `trojan://`, `ss://` or fetches subscription URLs.
     - `POST /api/activate`: Writes outbound JSON and spawns `xray.exe run -c <active.json>` listening on `127.0.0.1:20808` (mixed protocol).
     - `GET /api/ping`: Tests real latency to `https://www.google.com` through `20808`.
   - Dynamic Outbound Builder:
     - Handles `raw`/`tcp` transports with HTTP fake headers (`rawSettings` with Host header).
     - Handles `xhttp`/`splithttp`, `ws`, `grpc`.
     - Handles TLS (`alpn`, `fingerprint`) and Reality (`publicKey`, `shortId`, `spiderX`).
3. **Silent Persistence:**
   - Place a `.vbs` script in `%APPDATA%\Microsoft\Windows\Start Menu\Programs\Startup\` invoking `pythonw.exe daemon.py` with window style `0`.
   - The user never sees a terminal window, never opens V2RayN, and controls their censorship bypass entirely from the Chrome toolbar with Persian Vazirmatn typography.
