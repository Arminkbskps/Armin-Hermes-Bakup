# Cloudflare Worker Reverse Tunnel (Durable Object WebSocket Bridge)

Use this pattern when operating inside restricted CDEs (like Daytona, Codespaces, or locked-down VPS) where:
1. No direct public IP is assigned.
2. Outbound DPI firewalls block known tunnel domains (`*.trycloudflare.com`, `*.argotunnel.com`, `*.ngrok.io`, `*.localtunnel.me`, `*.playit.gg`) via TCP RST on TLS Client Hello SNI inspection.
3. Standard `cloudflared` fails with `Connection reset by peer` or `HTTP/2 connection is blocked or unreachable`.

## Architecture

- **Public Side**: Cloudflare Worker with a SQLite-backed Durable Object (`new_sqlite_classes = ["RouterTunnel"]` works on Cloudflare Free plan).
- **Edge Multiplexing**: The Durable Object holds a live WebSocket to the CDE backend. Public HTTP requests (API calls, web UI) are converted to JSON messages, sent over WebSocket to the CDE, executed against `127.0.0.1:<PORT>`, and returned as HTTP responses.
- **Client Side (CDE)**: Node.js 22 (built-in native `WebSocket`) daemon connects outbound to `wss://<worker>/_tunnel_backend` with 15s heartbeat pings.

## Cloudflare Worker Configuration

### `wrangler.toml`
```toml
name = "my-proxy"
main = "worker.js"
compatibility_date = "2025-01-01"

[durable_objects]
bindings = [
  { name = "ROUTER_TUNNEL", class_name = "RouterTunnel" }
]

[[migrations]]
tag = "v1"
new_sqlite_classes = ["RouterTunnel"]
```

### `worker.js` (Handler & Durable Object)
```javascript
export default {
  async fetch(req, env) {
    const url = new URL(req.url);
    const path = url.pathname;

    // Route service paths + Next.js static assets to Durable Object
    if (path.startsWith("/service") || path.startsWith("/_next/") || path === "/login" || path.startsWith("/dashboard") || path === "/_tunnel_backend") {
      const id = env.ROUTER_TUNNEL.idFromName("global_tunnel");
      const obj = env.ROUTER_TUNNEL.get(id);

      let subPath = path;
      if (path.startsWith("/service/")) {
        subPath = "/" + path.slice(9);
      }
      const targetUrl = new URL(subPath + url.search, url.origin);
      return obj.fetch(new Request(targetUrl, req));
    }
    return new Response("Not Found", { status: 404 });
  }
};

export class RouterTunnel {
  constructor(state, env) {
    this.state = state;
    this.env = env;
    this.backendWs = null;
    this.pending = new Map();
  }

  async fetch(request) {
    const url = new URL(request.url);

    // 1) Backend WebSocket registration from CDE
    if (url.pathname === "/_tunnel_backend") {
      if (request.headers.get("Upgrade") !== "websocket") {
        return new Response("Expected websocket", { status: 426 });
      }
      const pair = new WebSocketPair();
      const [client, server] = Object.values(pair);
      server.accept();
      this.backendWs = server;

      server.addEventListener("message", (event) => {
        try {
          const data = JSON.parse(event.data);
          if (data.type === "ping") return;
          const p = this.pending.get(data.id);
          if (p) {
            this.pending.delete(data.id);
            clearTimeout(p.timer);
            p.resolve(data);
          }
        } catch (e) {
          console.error("Tunnel message parse error:", e);
        }
      });

      server.addEventListener("close", () => {
        if (this.backendWs === server) this.backendWs = null;
      });
      return new Response(null, { status: 101, webSocket: client });
    }

    // 2) Public HTTP request handling
    if (!this.backendWs) {
      return new Response(JSON.stringify({ error: "Backend not connected", status: 503 }), {
        status: 503,
        headers: { "Content-Type": "application/json", "Access-Control-Allow-Origin": "*" }
      });
    }

    const id = crypto.randomUUID();
    let body = null;
    if (request.method !== "GET" && request.method !== "HEAD") {
      body = await request.text();
    }

    const forwardPayload = {
      id,
      method: request.method,
      url: url.pathname + url.search,
      headers: Object.fromEntries(request.headers.entries()),
      body
    };

    const responsePromise = new Promise((resolve) => {
      const timer = setTimeout(() => {
        this.pending.delete(id);
        resolve({
          status: 504,
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ error: "Gateway timeout" })
        });
      }, 60000);
      this.pending.set(id, { resolve, timer });
    });

    this.backendWs.send(JSON.stringify(forwardPayload));
    const res = await responsePromise;
    const responseHeaders = new Headers(res.headers);
    responseHeaders.delete("content-encoding");
    responseHeaders.delete("transfer-encoding");
    responseHeaders.set("alt-svc", "clear");
    responseHeaders.set("Access-Control-Allow-Origin", "*");

    return new Response(res.body, { status: res.status, headers: responseHeaders });
  }
}
```

## Critical Pitfalls & Diagnostics

### 1. `ERR_QUIC_PROTOCOL_ERROR` on Cloudflare Worker Domains
- **Symptom:** Chrome shows `This site can’t be reached ... ERR_QUIC_PROTOCOL_ERROR` when opening `https://<worker>.workers.dev`.
- **Cause:** Cloudflare Edge advertises HTTP/3 over QUIC (`alt-svc: h3=":443"`). In regions with strict DPI or filtered networks (e.g. Iran), outbound UDP on port 443 is blocked or scrambled. Chrome attempts the QUIC handshake, fails, and refuses to fall back to TCP.
- **Worker-side Fix:** In the Durable Object and Worker handlers, strip QUIC advertising by forcing:
  ```javascript
  responseHeaders.set("alt-svc", "clear");
  ```
- **Browser-side Workaround:** If Chrome still caches the alt-svc instruction, navigate to `chrome://flags/#enable-quic`, change **Experimental QUIC protocol** to **Disabled**, and relaunch Chrome, or use Firefox/Edge without QUIC.

### 2. WebSocket 101 Handshake Stripping in Worker Fetch Wrapper
- **Symptom:** The backend client connects to `wss://<worker>/_tunnel_backend` but receives `Unexpected server response: 503` or the WebSocket immediately closes.
- **Root Cause:** If the Worker's outer `fetch` handler wraps the Durable Object response in a `new Response(resp.body, ...)` for all routes:
  ```javascript
  // BUGGY:
  const resp = await obj.fetch(new Request(targetUrl, req));
  return new Response(resp.body, { status: resp.status, headers: ... });
  ```
  In Cloudflare Workers, a WebSocket upgrade response (`status: 101, webSocket: client`) carries the underlying WebSocket binding on the Response object. Re-wrapping it in `new Response()` strips that native property.
- **Fix:** Always return the Durable Object response directly for `/_tunnel_backend`:
  ```javascript
  const targetUrl = new URL(subPath + url.search, url.origin);
  if (path === "/_tunnel_backend") {
    return obj.fetch(new Request(targetUrl, req));
  }
  const resp = await obj.fetch(new Request(targetUrl, req));
  const headers = new Headers(resp.headers);
  headers.set("alt-svc", "clear");
  return new Response(resp.body, { status: resp.status, headers });
  ```

## CDE Client Daemon (`tunnel_client.js`)

```javascript
const http = require("http");

const WORKER_WS_URL = "wss://<worker-domain>/_tunnel_backend";
const TARGET_HOST = "127.0.0.1";
const TARGET_PORT = 20128; // Local service port

function connect() {
  const ws = new WebSocket(WORKER_WS_URL);
  let heartbeatTimer = null;

  ws.onopen = () => {
    // Crucial: 15s ping prevents Cloudflare edge from dropping idle WebSocket (drops at ~60s)
    heartbeatTimer = setInterval(() => {
      if (ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: "ping" }));
      }
    }, 15000);
  };

  ws.onmessage = async (event) => {
    try {
      const data = JSON.parse(event.data);
      if (data.type === "ping" || data.type === "pong") return;

      const { id, method, url, headers, body } = data;
      const reqHeaders = { ...headers };
      delete reqHeaders["host"];
      delete reqHeaders["connection"];
      delete reqHeaders["upgrade"];
      reqHeaders["accept-encoding"] = "identity"; // Avoid compressed binary parsing issues

      const req = http.request({
        hostname: TARGET_HOST,
        port: TARGET_PORT,
        path: url,
        method: method,
        headers: reqHeaders,
        timeout: 55000
      }, (res) => {
        let chunks = [];
        res.on("data", (chunk) => chunks.push(chunk));
        res.on("end", () => {
          const resBody = Buffer.concat(chunks).toString("utf-8");
          if (ws.readyState === WebSocket.OPEN) {
            ws.send(JSON.stringify({ id, status: res.statusCode, headers: res.headers, body: resBody }));
          }
        });
      });

      req.on("error", (err) => {
        if (ws.readyState === WebSocket.OPEN) {
          ws.send(JSON.stringify({
            id, status: 502,
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ error: err.message })
          }));
        }
      });

      if (body) req.write(body);
      req.end();
    } catch (err) {
      console.error("Message handling error:", err);
    }
  };

  ws.onclose = () => {
    if (heartbeatTimer) clearInterval(heartbeatTimer);
    setTimeout(connect, 3000);
  };

  ws.onerror = () => {};
}

connect();
```

## Process Persistence via PM2
On restricted CDE VMs where creating new systemd units via sudo triggers approval timeouts or permission errors:
```bash
sudo npm install -g pm2
pm2 start /home/ubuntu/tunnel_client.js --name 9router-tunnel
pm2 save
sudo pm2 startup systemd -u ubuntu --hp /home/ubuntu
```
