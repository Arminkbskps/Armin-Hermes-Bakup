---
name: agent-email-inbox
description: "Manage agent email inboxes for signups, OTP, and mail."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [email, agentmail, inbox, otp, verification, accounts]
---

# Agent Email Inbox

Manage dedicated, programmatic email inboxes for AI agents. Enables autonomous service signups, email verification (OTP codes and magic links), and outbound notifications without relying on human personal email accounts.

## Provider Selection

1. **AgentMail (`agentmail.to`) [Recommended for Instant Setup]**:
   - Modern API-first email infrastructure for AI agents backed by Amazon SES.
   - High deliverability; not blocked by GitHub, Cloudflare, or major developer platforms.
   - Provides full send (`POST /v0/inboxes/{id}/messages/send`) and receive (`GET /v0/inboxes/{id}/messages`).
   - Requires API key (`am_us_inbox_...` or dashboard API key). Free tier includes 3 inboxes and 3,000 emails/month.

2. **Cloudflare Email Routing + Worker [Recommended for Custom Domains]**:
   - Zero-cost catch-all forwarding on custom domains (`*@yourdomain.com`).
   - Completely immune to disposable email blocklists because custom domains represent verified business identities.
   - Can forward to a primary inbox or trigger a Cloudflare Worker webhook.

3. **Legacy / Disposable Services (Atomic Mail, Mail.tm, etc.) [Caution]**:
   - Shared public domains (e.g. `@atomicmail.ai`, `@maxxspace.com`) are frequently detected and blacklisted by enterprise anti-abuse systems (GitHub, Cloudflare, OpenAI).
   - Only use for low-security test environments, or when custom domain MX records are attached.

## Standard AgentMail Workflow

### 1. Configuration
Store credentials locally in a secure file (`chmod 600`):
```json
// ~/.config/mail/agentmail.json
{
  "api_key": "YOUR_AGENTMAIL_API_KEY",
  "inbox_id": "agent-name@agentmail.to",
  "email": "agent-name@agentmail.to"
}
```

### 2. Inbox Operations (REST API)

- **List Inboxes**:
  `GET https://api.agentmail.to/v0/inboxes` with header `Authorization: Bearer <API_KEY>`
- **List Messages**:
  `GET https://api.agentmail.to/v0/inboxes/<INBOX_ID>/messages`
- **Read Single Message**:
  `GET https://api.agentmail.to/v0/inboxes/<INBOX_ID>/messages/<ENCODED_MESSAGE_ID>`
- **Send Message**:
  ```bash
  POST https://api.agentmail.to/v0/inboxes/<INBOX_ID>/messages/send
  Headers: Authorization: Bearer <API_KEY>, Content-Type: application/json
  Body: {"to": ["target@example.com"], "subject": "Subject", "text": "Body"}
  ```

### 3. Verification & OTP Polling Loop
When waiting for a verification email or OTP during service onboarding:
1. Record existing message IDs before triggering the action on the external site.
2. Poll `GET /v0/inboxes/<INBOX_ID>/messages` every 3-5 seconds with a defined timeout (typically 60-90s).
3. Identify the newest unread message from the service provider (e.g. `GitHub <noreply@github.com>`).
4. Retrieve the full message payload (`text` or `html`).
5. Extract verification credentials:
   - **Numeric OTP**: `re.findall(r'\b[0-9]{6,8}\b', body)`
   - **Magic Verification Link**: `re.search(r'https://[^\s"\'>]+(?:verify|confirm|token=)[^\s"\'>]+', body)`

## Pitfalls & Operational Rules

- **Disposable Blocklist Rejection**: If a provider rejects the email address during signup with a message like *"This email domain is not permitted"*, switch immediately from public domains to AgentMail or a custom domain. Do not retry with another disposable provider.
- **Two-Stage Verification**: Services like GitHub often issue two separate emails during registration:
  1. Initial signup launch code / email verification.
  2. Device verification code (`[GitHub] Please verify your device`) when logging in from an unrecognized browser session.
  Always inspect message subjects and poll again if a second verification step is triggered.
- **URL-Encoded Message IDs in REST Calls**: Message IDs often contain angle brackets and special characters (e.g. `<010001a...@email.amazonses.com>`). Always URL-encode the message ID before appending it to API endpoint URLs (`urllib.parse.quote(msg_id)`).
- **Cloudflare Worker Egress Conflict**: When running within local proxies that route through Cloudflare Workers (e.g. `*.workers.dev`), outbound HTTPS connections to `dash.cloudflare.com` or `api.cloudflare.com` fail due to Cloudflare-to-Cloudflare loop protection. Run Cloudflare signup flows via human operator relay or direct egress.
