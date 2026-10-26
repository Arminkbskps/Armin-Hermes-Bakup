# Iran ISP Optimization Matrix for Cloudflare Workers Proxy

This reference provides tested network parameters for bypassing DPI and TLS inspection across major Iranian Internet Service Providers (ISPs) when using Cloudflare Workers tunnels.

## 1. ISP Decision & Parameter Matrix

| ISP | Filtering Mechanism | Primary TLS Port | Fallback Port | Recommended Clean IP / Address | Fragment Rule |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Mokhaberat (TCI Fixed)** | Port 443 SNI RST Injection | **8443** | 2053 / 2087 | `104.17.34.10` or `speed.cloudflare.com` | `tlshello` / `10-20` / `10-20` |
| **Rightel (Mobile)** | Light SNI check, occasional throttle | **443** | 8443 | `cloudflare.com` or `104.16.148.243` | `1-3` / `10-20` / `10-20` |
| **Hamrah Aval (MCI Mobile)** | Deep packet inspection on port 443 | **443** | 2053 | `speed.cloudflare.com` or `104.18.25.10` | `tlshello` / `20-40` / `10-20` |
| **Irancell (MTN Mobile)** | Strict SNI filter on non-TLS & standard ports | **443** | 8443 | `worker-domain.workers.dev` (Direct Edge) | `tlshello` / `10-30` / `10-20` |

---

## 2. Cloudflare Alternative TLS Ports

Cloudflare Workers terminate TLS on six standard HTTPS ports:
- `443` (Default HTTPS)
- `8443` (Alternative HTTPS — **Most effective against TCI / Mokhaberat port 443 filters**)
- `2053`
- `2083`
- `2087`
- `2096`

When an ISP implements a blanket RST injection on `*.workers.dev` on port 443, shifting the connection to `8443` while retaining `sni: <worker-domain>` frequently bypasses the hardware DPI box.

---

## 3. Client Fragment Configuration

Fragmenting the initial TLS `ClientHello` packet splits the cleartext SNI extension across multiple TCP frames, preventing stateful DPI boxes from reconstructing the domain name.

### v2rayNG / NikaNG Settings
- **Packets**: `tlshello` (splits only the TLS handshake) or `1-3`
- **Length**: `10-20` bytes per fragment
- **Interval**: `10-20` ms delay between fragmented packets

### Sing-box 1.9+ Native Outbound Config
```json
"tls": {
  "enabled": true,
  "server_name": "hermes-tunnel.armin-hermes.workers.dev",
  "insecure": false,
  "utls": {
    "enabled": true,
    "fingerprint": "chrome"
  },
  "fragment": {
    "enabled": true,
    "length": "10-20",
    "interval": "10-20"
  }
}
```

---

## 4. Multi-Format Subscription Endpoint Implementation

Workers should expose format query selectors on `/sub`:

- `/sub?format=v2ray` (Default): Base64 encoded list of `vless://` URLs.
- `/sub?format=singbox`: Full Sing-box JSON outbound structure with auto-failover `urltest` group and pre-configured fragment parameters.
- `/sub?format=clash`: Clash Meta / Mihomo YAML structure with proxy providers and latency test groups.
