# Cloudflare Multi-Account Hub & Social Automation on Workers + D1

## 1. Cloudflare Multi-Account Hub Architecture

When managing multiple Cloudflare accounts (e.g. personal, client projects, or distributing free tier quota of 100k req/day across accounts):

### D1 Schema Pattern
```sql
CREATE TABLE IF NOT EXISTS cloudflare_accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    account_id TEXT NOT NULL,
    api_token TEXT NOT NULL,
    email TEXT DEFAULT '',
    worker_url TEXT DEFAULT '',
    is_primary INTEGER DEFAULT 0,
    status TEXT DEFAULT 'active',
    last_verified INTEGER DEFAULT 0,
    created_at INTEGER NOT NULL,
    updated_at INTEGER NOT NULL
);
```

### Live Token & Account Verification
Cloudflare Workers can call Cloudflare's own REST API directly:
```javascript
// 1. Verify token status
const verifyRes = await fetch('https://api.cloudflare.com/client/v4/user/tokens/verify', {
    headers: { 'Authorization': `Bearer ${apiToken}` }
});
const verifyData = await verifyRes.json();
if (!verifyData.success) {
    throw new Error(verifyData.errors?.[0]?.message || 'Invalid Cloudflare API Token');
}

// 2. Fetch Account Name & Email
const accRes = await fetch(`https://api.cloudflare.com/client/v4/accounts/${accountId}`, {
    headers: { 'Authorization': `Bearer ${apiToken}` }
});
const accData = await accRes.json();
const accountName = accData.result?.name || '';
```

---

## 2. Multi-Worker Traffic Routing: Failover & Load-Balancing Strategies

Cloudflare Workers Free plan has a limit of **100,000 requests/day per account**. When operating multiple accounts, incoming webhooks (e.g. Meta Graph API Webhooks) can be routed intelligently:

### Strategy 1: Smart Failover (سوییچ خودکار در صورت اتمام سهمیه)
- Primary worker receives and processes webhooks while tracking a daily counter (`cf_requests_today`) in D1.
- When `cf_requests_today >= cf_daily_request_cap` (e.g. 95,000 requests) or on processing errors:
  The worker forwards the incoming webhook to backup worker URLs registered in `cloudflare_accounts`.
- Guard against infinite loops with custom header: `x-instaflow-forwarded: 1`.

```javascript
async function forwardWebhook(targetWorkerUrl, body) {
    try {
        const endpoint = targetWorkerUrl.replace(/\/+$/, '') + '/webhook';
        await fetch(endpoint, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'x-instaflow-forwarded': '1'
            },
            body: JSON.stringify(body)
        });
        return true;
    } catch (e) {
        console.error('Failed to forward webhook:', e);
        return false;
    }
}
```

### Strategy 2: Round-Robin / Load Balancing (توزیع بار همزمان)
- Distribute inbound webhooks probabilistically or sequentially across all active workers.
- Effectively multiplies total throughput: `N accounts * 100k = N * 100k requests/day`.
- If an outbound forward fails or times out, immediately fall back to local execution.

### Strategy 3: Midnight Quota Reset
- Cloudflare cron triggers (`scheduled(event, env, ctx)`) reset `cf_requests_today = 0` every midnight when date changes, ensuring continuous uninterrupted operation.

---

## 3. Instagram & Meta Graph API Automation on Workers

### Webhook Handshake & Verification
```javascript
if (path === '/webhook' && request.method === 'GET') {
    const mode = url.searchParams.get('hub.mode');
    const token = url.searchParams.get('hub.verify_token');
    const challenge = url.searchParams.get('hub.challenge');

    if (mode === 'subscribe' && token === expectedToken) {
        return new Response(challenge, { status: 200 });
    }
    return new Response('Forbidden', { status: 403 });
}
```

### Official Private Reply (Comment-to-DM)
Send a direct message in response to a public comment without requiring an existing 24h conversation:
```javascript
const res = await fetch(`https://graph.facebook.com/v20.0/${pageId}/messages?access_token=${accessToken}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        recipient: { comment_id: commentId },
        message: { text: messageText }
    })
});
```

### Spintax Engine (Variable Collision Safe)
Always ensure choices contain a pipe (`|`) before parsing; otherwise template tags like `{username}` will be stripped:
```javascript
export function parseSpintax(text) {
    if (!text || typeof text !== 'string') return '';
    const spintaxRegex = /\{([^{}]+)\}/g;
    let prev = '', current = text, iterations = 0;
    while (prev !== current && iterations < 10) {
        prev = current;
        current = current.replace(spintaxRegex, (match, choices) => {
            if (!choices.includes('|')) return match;
            const options = choices.split('|');
            return options[Math.floor(Math.random() * options.length)] || '';
        });
        iterations++;
    }
    return current;
}
```

### Persian/Arabic Text Normalization (ZWNJ & Letter Variations)
In comment and keyword matching, Persian users write interchangeably with or without half-space (نیم‌فاصله) and Arabic 'ي' / 'ك':
```javascript
export function normalizePersianText(text) {
    if (!text || typeof text !== 'string') return '';
    return text
        .replace(/ي/g, 'ی')
        .replace(/ك/g, 'ک')
        .replace(/[\u200B-\u200D\uFEFF]/g, '')
        .replace(/\u200c/g, ' ') // ZWNJ to space ensures 'می‌خوام' matches 'میخوام'
        .replace(/\s+/g, ' ')
        .trim()
        .toLowerCase();
}
```

---

## 4. Native Jalali Date Formatting in Workers / Vanilla Browser
Format Persian dates without importing any external libraries:
```javascript
function formatJalaliTime(timestampSec) {
    return new Intl.DateTimeFormat('fa-IR', {
        year: 'numeric', month: 'short', day: 'numeric',
        hour: '2-digit', minute: '2-digit'
    }).format(new Date(timestampSec * 1000));
}
```
