# GitHub Actions Secrets via Node.js API

When `gh` CLI is unavailable and Python PyNaCl is not installed, use Node.js + `sodium-native` to encrypt and add GitHub Actions secrets via the REST API.

## Setup

```bash
mkdir -p /tmp/gh-secrets && cd /tmp/gh-secrets
npm init -y && npm install sodium-native
```

## Complete Script

```js
const sodium = require("./node_modules/sodium-native");
const https = require("https");

const TOKEN = "ghp_...";
const REPO = "owner/repo";

const secrets = {
  "SECRET_NAME": "secret-value",
};

function apiRequest(path, method, data) {
  return new Promise((resolve, reject) => {
    const postData = data ? JSON.stringify(data) : null;
    const opts = {
      hostname: "api.github.com",
      path, method,
      headers: {
        "Authorization": `token ${TOKEN}`,
        "User-Agent": "Agent-Deployer",
        "Accept": "application/vnd.github.v3+json",
        "Content-Type": "application/json",
      }
    };
    if (postData) opts.headers["Content-Length"] = Buffer.byteLength(postData);
    const req = https.request(opts, res => {
      let body = "";
      res.on("data", c => body += c);
      res.on("end", () => {
        try { resolve({ status: res.statusCode, data: JSON.parse(body) }); }
        catch(e) { resolve({ status: res.statusCode, data: body }); }
      });
    });
    req.on("error", reject);
    if (postData) req.write(postData);
    req.end();
  });
}

function encryptSecret(value, publicKeyB64) {
  const publicKey = Buffer.from(publicKeyB64, "base64");
  const nonce = Buffer.alloc(sodium.crypto_box_SEEDBYTES);
  sodium.randombytes_buf(nonce);
  const encrypted = Buffer.alloc(value.length + sodium.crypto_box_SEALBYTES);
  sodium.crypto_box_seal(encrypted, Buffer.from(value), publicKey);
  return encrypted.toString("base64");
}

async function main() {
  const keyRes = await apiRequest(`/repos/${REPO}/actions/secrets/public-key`, "GET");
  const { key_id, key: publicKeyB64 } = keyRes.data;
  
  for (const [name, value] of Object.entries(secrets)) {
    const encrypted = encryptSecret(value, publicKeyB64);
    const res = await apiRequest(`/repos/${REPO}/actions/secrets/${name}`, "PUT", {
      encrypted_value: encrypted, key_id
    });
    console.log(`${name}: ${res.status === 201 || res.status === 204 ? "OK" : "FAIL"} (${res.status})`);
  }
}

main();
```

## Key Notes
- `sodium-native` is a native C addon — installs fast (no Python needed)
- GitHub requires libsodium `crypto_box_seal` encryption for secrets
- Plain base64 or AES will NOT work — GitHub validates the encryption format
- Token needs `repo` scope (NOT `workflow` scope — that's only for pushing workflow files)
