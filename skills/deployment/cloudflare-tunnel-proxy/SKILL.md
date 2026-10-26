---
name: cloudflare-tunnel-proxy
description: "Deploy VLESS/Trojan proxy tunnels on Cloudflare Workers."
version: 1.0.0
---

# Cloudflare Tunnel Proxy (VLESS & Trojan)

Deploy high-performance, resilient VLESS and Trojan WebSocket proxy tunnels on Cloudflare Workers, tailored for restrictive DPI firewalls (such as Iranian ISPs including Rightel, MCI, and Irancell) and geo-restricted AI platforms (Google Gemini, OpenAI, Claude).

## Architecture: Dual-Role Worker + KV Storage

A single Cloudflare Worker can simultaneously serve a management dashboard, provide multi-format subscriptions, and handle encrypted proxy tunnels:
1. **HTTP GET (`/` or `/<path>/panel`)**: Returns the web management dashboard with live stats, QR codes, and node presets.
2. **HTTP GET (`/sub` or `/<path>/sub`)**: Dynamic multi-format subscription generator:
   - Default: Base64 VLESS links (for v2rayNG, NikaNG, Streisand).
   - `?format=singbox`: Full Sing-box JSON with built-in TLS Fragment (`length: 10-20`, `interval: 10-20`), FakeDNS, and DoH hijack.
   - `?format=clash`: Clash Meta / Mihomo YAML with auto-latency url-test groups.
   - WARP on WARP (WoW): Outbounds chained through Cloudflare consumer WARP to unblock AI services.
3. **WebSocket Upgrade (`Upgrade: websocket`)**: Handled by `handleWebSocket(request)` using `cloudflare:sockets` to tunnel TCP traffic out through Cloudflare Edge.
4. **Cloudflare KV**: Persistent storage for clean IP lists, custom proxy IPs (for fixed country routing), WARP credentials, and tunnel configurations.

```
Client (v2rayNG / Sing-box / Clash)
   │
   ├─► GET  /                 ──► Web Dashboard (HTML/CSS/JS + QR)
   ├─► GET  /sub?format=...   ──► Base64 / Sing-box JSON / Clash YAML
   └─► WS   / (443 or 8443)   ──► VLESS/Trojan Tunnel ──► cloudflare:sockets ──► Target Internet
```

## Step 1 - Worker Source Code (`src/worker.js`)

```javascript
import { connect } from 'cloudflare:sockets';

const TARGET_UUID = 'f2fa065d1dff468aa7cb3faf1352b8ce'; // 32 hex chars without hyphens
const RAW_UUID = 'f2fa065d-1dff-468a-a7cb-3faf1352b8ce';
const NAT64_PREFIXES = ['[2602:fc59:b0:64::]', '[2602:fc59:11:64::]', '[2a02:898:146:64::]'];

export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const upgradeHeader = request.headers.get('Upgrade') || '';

    // 1. WebSocket Proxy Tunnel
    if (upgradeHeader.toLowerCase() === 'websocket') {
      return handleWebSocket(request);
    }

    // 2. Base64 Subscription Endpoint
    if (url.pathname === '/sub' || url.pathname === `/${RAW_UUID}/sub`) {
      return handleSubscription(request, url);
    }

    // 3. Embedded Web Dashboard
    return new Response(HTML_DASHBOARD, {
      headers: { 'Content-Type': 'text/html; charset=utf-8' }
    });
  }
};
```

## Step 2 - Wrangler Configuration (`wrangler.toml`)

Always include `nodejs_compat` to enable Node stream primitives and `cloudflare:sockets`, and bind the KV namespace for persistent storage:

```toml
name = "hermes-tunnel"
main = "src/worker.js"
compatibility_date = "2024-09-23"
compatibility_flags = ["nodejs_compat"]
workers_dev = true

[[kv_namespaces]]
binding = "kv"
id = "<your-kv-namespace-id>"
```

Generate the KV namespace via:
```bash
npx wrangler kv namespace create kv
```

## Step 2.1 - API Token Generation with Pre-filled Permissions

Avoid permission error 10011 by directing users to create a token with exact required scopes via pre-filled URL:
```text
https://dash.cloudflare.com/profile/api-tokens?permissionGroupKeys=[{"key":"workers_scripts","type":"edit"},{"key":"workers_kv_storage","type":"edit"},{"key":"page","type":"edit"},{"key":"workers_routes","type":"edit"},{"key":"d1","type":"edit"},{"key":"dns","type":"edit"},{"key":"zone","type":"read"},{"key":"user_details","type":"read"},{"key":"account_settings","type":"read"}]&name=tunnel-token&accountId=*&zoneId=all
```

## Step 3 - GitHub Actions Automated Deployment & Secret Inlining

Never commit raw Cloudflare API tokens (`cfut_...`) into git repos, as GitHub Push Protection immediately rejects commits with token rule violations. Use placeholder replacement in CI/CD:

Save as `.github/workflows/deploy.yml`:

```yaml
name: Deploy Tunnel to Cloudflare

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '22'
      - name: Inject Secrets and Deploy
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CLOUDFLARE_API_TOKEN }}
          CLOUDFLARE_ACCOUNT_ID: ${{ secrets.CLOUDFLARE_ACCOUNT_ID }}
        run: |
          sed -i "s|__CF_API_TOKEN__|$CLOUDFLARE_API_TOKEN|g" src/worker.js
          sed -i "s|__CF_ACCOUNT_ID__|$CLOUDFLARE_ACCOUNT_ID|g" src/worker.js
          npx wrangler deploy
```

## Step 4 - Initializing Admin Password in KV

On initial deployment of panel systems (like BPB), secure the admin panel immediately by setting the password key in KV to prevent unauthenticated lockouts:
```bash
npx wrangler kv key put --binding=kv "pwd" "<your-secure-password>"
```

## AI Platforms & Zero IP/DNS Leak Architecture

1. **Why Direct Worker Sockets Fail on Google Gemini & AI**:
   Direct `cloudflare:sockets` outbound connections exit from Cloudflare Datacenter Anycast IPs (AS13335). Google Gemini, ChatGPT, and Claude maintain blocklists for datacenter ranges and throw regional errors ("Gemini is not supported in your country") or 403 blocks.
2. **WARP on WARP (WoW) Routing**:
   To bypass AI region blocks, chain outbound traffic through Cloudflare's consumer WARP WireGuard endpoints (`engage.cloudflareclient.com` / `162.159.192.1`). Consumer WARP exit nodes are treated as residential/eyeball traffic by Google and resolve regional restrictions.
3. **Preventing DNS and IP Leaks**:
   - Force **FakeDNS** (`enhanced-mode: fake-ip`) in Sing-box and Clash configs so the client OS never resolves DNS queries on the local ISP.
   - Enforce **Remote DoH** via `https://1.1.1.1/dns-query` through the tunnel detour with DNS hijacking to prevent local ISP eavesdropping.

## Operator Tuning (Mokhaberat, Rightel, MCI, Irancell)

See detailed decision table and port matrix in `references/iran-isp-matrix.md`.

1. **Mokhaberat (TCI) Port 443 DPI Bypass**:
   Mokhaberat aggressively blocks `*.workers.dev` SNI on port 443 via TCP resets.
   - **Alternative Port 8443**: Cloudflare Workers support TLS on ports `443, 8443, 2053, 2083, 2087, 2096`. Routing through `speed.cloudflare.com:8443` or clean IP `104.17.34.10:8443` completely bypasses the port 443 SNI blocker.
   - **Mandatory Fragment**: Set `packets: tlshello` (or `1-3`), `length: 10-20`, `interval: 10-20`.

2. **Rightel (Mobile Data)**:
   Rightel allows standard port 443 with low latency. Use `cloudflare.com:443` or `104.16.148.243:443` with `sni` and `host` set to the worker.

3. **Sing-box Built-In TLS Fragment**:
   Embed fragment parameters directly in outbound JSON config so clients bypass DPI automatically without manual setup:
   ```json
   "tls": {
     "enabled": true,
     "server_name": "worker-domain.workers.dev",
     "utls": { "enabled": true, "fingerprint": "chrome" },
     "fragment": {
       "enabled": true,
       "length": "10-20",
       "interval": "10-20"
     }
   }
   ```

4. **Clean IP Injection**:
   Configure node host as clean Cloudflare Anycast CDN IPs (`cloudflare.com`, `speed.cloudflare.com`, `104.16.148.243`, `104.17.34.10`), while keeping the `sni` and `host` headers pointing to the Worker domain.

5. **Fallback NAT64**:
   Cloudflare Workers free tier routes outbound IPv4 through NAT64. The worker must include fallback IPv6 NAT64 prefix resolvers for domains lacking native IPv6 records.

## Pitfalls & Operational Security

- No-clone mandate is a hard constraint: when the user says not to reuse a named reference project, never deploy that project's code or panel under a custom name, even when its internals would solve the problem faster.
- Dashboard quality bar: the web panel is a first-class deliverable, not a styled stub. Build it against a real design system (dark-mode-native surfaces, one restrained accent, consistent type scale, SVG icons instead of emoji) with working copy, QR, and subscription interactions.

- **Direct Worker Sockets Blocked by Google/Gemini**: Never rely on a bare Cloudflare Worker VLESS proxy for AI tools; it exits via AS13335 datacenter IPs which Google blocks by default. Always chain outbound traffic through WARP on WARP (WoW) or a clean residential proxy IP.
- **GitHub Push Protection Blocks API Tokens**: Never commit `cfut_...` tokens directly to git repositories; GitHub Push Protection immediately rejects the push (`GH013`). Always inject tokens dynamically via GitHub Secrets during CI/CD using runner placeholders (`sed -i "s|__CF_API_TOKEN__|$SECRET|g"`).
- **Zero Tolerance for Personal `.ir` Domains**: Never bind `.ir` domains to proxy workers in Iran. `.ir` domains require national ID / IRNIC verification and expose the operator to immediate attribution and legal hazard. Always use `workers.dev` paired with Clean IPs, port 8443, and TLS fragmentation.
- **Pages Function Publishing Error**: Do not deploy TCP proxy scripts with `cloudflare:sockets` via Cloudflare Pages Advanced Mode (`_worker.js`); it frequently fails with `Unknown internal error occurred`. Always deploy as a standalone Cloudflare Worker (`wrangler deploy`).
- **Cloudflare Loop Detection**: Automated deployments must run via GitHub Actions runners, not from an environment whose outbound traffic is proxied through Cloudflare Workers.
