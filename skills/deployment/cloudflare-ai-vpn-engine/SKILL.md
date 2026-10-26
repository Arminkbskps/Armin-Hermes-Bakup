---
name: cloudflare-ai-vpn-engine
description: "Use when building Cloudflare proxy tunnels and Gemini WARP."
version: 1.0.0
---

# Cloudflare AI & Anti-Censorship Proxy Engine

Deploy custom, zero-leak VLESS/Trojan and WireGuard WARP proxy engines on Cloudflare Workers, specifically engineered for bypassing aggressive ISP DPI (Mokhaberat, Rightel) and unblocking geo-restricted AI platforms (Google Gemini, OpenAI, Claude).

## 1. The Core Architecture: Dual-Layer Egress

A standard Cloudflare Worker VLESS proxy routes outbound connections directly from Cloudflare's Datacenter Anycast IPs (AS13335). Google Gemini, ChatGPT, and Claude block AS13335 by default with region/datacenter errors.

To guarantee 100% access without IP leaks or blocks:
1. **General Web Traffic**: Tunnels through VLESS-WebSocket over TLS on port 443 (Rightel/MCI) or port 8443 (Mokhaberat TCI).
2. **AI & Gemini Traffic**: Chained through Cloudflare consumer WARP (WireGuard `162.159.192.1:2408`) via Sing-box / Clash Meta routing rules. Consumer WARP exit nodes are treated as residential/eyeball traffic by Google.

```
Client (v2rayNG / Sing-box / Clash)
   │
   ├── AI Traffic (Gemini, Claude, OpenAI) ──► WireGuard WARP Outbound (162.159.192.1:2408) ──► Clean Residential Exit
   ├── General Web (Mokhaberat fixed)       ──► Port 8443 + TLS Fragment (tlshello, 10-20, 10-20) ──► Cloudflare Edge
   └── General Web (Rightel mobile)         ──► Port 443 + Clean Anycast IP (104.16.148.243)     ──► Cloudflare Edge
```

## 2. Multi-Format Subscription Implementation

The worker must dynamically handle format query parameters on `/sub`:

### A. Sing-box JSON (`/sub?format=singbox`)
Combines WireGuard WARP for AI domains with VLESS for general traffic, FakeDNS, and Remote DoH:
```json
{
  "dns": {
    "servers": [
      { "tag": "remote-dns", "address": "https://1.1.1.1/dns-query", "detour": "HERMES-SELECT" },
      { "tag": "local-dns", "address": "local", "detour": "direct" }
    ],
    "rules": [
      { "outbound": "any", "server": "remote-dns" },
      { "clash_mode": "Direct", "server": "local-dns" }
    ],
    "final": "remote-dns",
    "strategy": "prefer_ipv4"
  },
  "route": {
    "auto_detect_interface": true,
    "final": "HERMES-SELECT",
    "rules": [
      { "protocol": "dns", "action": "hijack-dns" },
      {
        "domain_suffix": [
          "gemini.google.com",
          "aistudio.google.com",
          "generativelanguage.googleapis.com",
          "openai.com",
          "chatgpt.com",
          "claude.ai",
          "anthropic.com"
        ],
        "outbound": "WARP-GEMINI-UNBLOCK"
      }
    ]
  },
  "outbounds": [
    {
      "type": "wireguard",
      "tag": "WARP-GEMINI-UNBLOCK",
      "server": "162.159.192.1",
      "server_port": 2408,
      "local_address": ["172.16.0.2/32", "2606:4700:110:8fd2:11f3:8e67:11d4:3704/128"],
      "private_key": "<base64-private-key>",
      "peer_public_key": "bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=",
      "reserved": [55, 94, 131],
      "mtu": 1280
    },
    {
      "type": "vless",
      "tag": "Hermes-Mokhaberat-8443",
      "server": "speed.cloudflare.com",
      "server_port": 8443,
      "uuid": "<uuid>",
      "tls": {
        "enabled": true,
        "server_name": "<worker-domain>",
        "fragment": { "enabled": true, "length": "10-20", "interval": "10-20" }
      },
      "transport": { "type": "ws", "path": "/", "headers": { "Host": "<worker-domain>" } }
    }
  ]
}
```

### B. Clash Meta / Mihomo YAML (`/sub?format=clash`)
```yaml
dns:
  enable: true
  enhanced-mode: fake-ip
  nameserver:
    - https://1.1.1.1/dns-query

proxies:
  - name: "🤖 WARP-GEMINI-UNBLOCK"
    type: wireguard
    server: 162.159.192.1
    port: 2408
    ip: 172.16.0.2
    ipv6: 2606:4700:110:8fd2:11f3:8e67:11d4:3704
    public-key: bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
    private-key: <base64-private-key>
    reserved: [55, 94, 131]
    udp: true
    mtu: 1280

rules:
  - DOMAIN-SUFFIX,gemini.google.com,🤖 WARP-GEMINI-UNBLOCK
  - DOMAIN-SUFFIX,aistudio.google.com,🤖 WARP-GEMINI-UNBLOCK
  - DOMAIN-SUFFIX,generativelanguage.googleapis.com,🤖 WARP-GEMINI-UNBLOCK
  - DOMAIN-SUFFIX,openai.com,🤖 WARP-GEMINI-UNBLOCK
  - DOMAIN-SUFFIX,claude.ai,🤖 WARP-GEMINI-UNBLOCK
  - MATCH,⚡ HERMES-SELECT
```

### C. WireGuard Standalone (`/sub?format=wireguard`)
Outputs pure `.conf` text for import into WireGuard, Oblivion, or Hiddify:
```ini
[Interface]
PrivateKey = <base64-private-key>
Address = 172.16.0.2/32, 2606:4700:110:8fd2:11f3:8e67:11d4:3704/128
DNS = 1.1.1.1, 2606:4700:4700::1111
MTU = 1280

[Peer]
PublicKey = bmXOC+F1FxEMF9dyiK2H5/1SUtzH0JuVo51h2wPfgyo=
AllowedIPs = 0.0.0.0/0, ::/0
Endpoint = 162.159.192.1:2408
PersistentKeepalive = 25
```

## 3. UI/UX Standards for Web Panels

When delivering a management dashboard hosted on `/`:
- **Linear-Inspired Minimalist Palette**: Base `#08090a`, cards `rgba(255,255,255,0.025)`, border `rgba(255,255,255,0.08)`, brand accent `#5e6ad2` / `#7170ff`.
- **RTL Typography**: `Vazirmatn` font for Persian prose, `Space Grotesk` or `JetBrains Mono` for latency, ports, IPs, and UUIDs.
- **No Raw Emoji Icons**: Use clean inline SVG icons for shields, speeds, servers, and copy buttons.
- **Client Side QR & Toast**: Non-blocking toast notifications on copy; sharp canvas-rendered QR code modals.
- **Zero-Dependency Resilience**: Embed styles and logic directly in HTML to ensure the panel renders even when international CDNs are degraded in Iran.

## 4. Key Pitfalls & Hard Constraints

1. **No-Clone Mandate**: When the user requests a custom tool and explicitly says not to use an existing project (e.g. BPB), never deploy that third-party project under the hood. Build a clean, native, self-contained worker.
2. **Direct Worker Sockets Fail on Gemini**: Never assume a bare VLESS WebSocket worker can open Google Gemini. Always provide a WireGuard WARP outbound or chained WoW configuration for AI domains.
3. **GitHub Push Protection (Secret Detection)**: Never commit raw Cloudflare API tokens (`cfut_...`) into git repos. Keep `src/worker.js` clean of secrets and let `wrangler deploy` read `CLOUDFLARE_API_TOKEN` from GitHub Actions runner environment secrets.
4. **Mokhaberat Port 443 Block**: Mokhaberat injects TCP resets on `*.workers.dev` SNI on port 443. Use alternative Cloudflare TLS ports (8443, 2053, 2087) paired with `tlshello` fragment.
