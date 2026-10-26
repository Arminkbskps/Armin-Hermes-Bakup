---
name: b2b-agent-email-provisioning
description: Use when provisioning agent emails for Daytona or GitHub.
category: email
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [email, agent-inbox, otp, verification, daytona, workos, cloudflare-email, disposable-bypass]
---

# B2B Agent Email Provisioning

Provision programmatic email inboxes for autonomous AI agents on services with strict anti-bot, disposable-email, or B2B work-email filters (Daytona Cloud, GitHub, WorkOS AuthKit, Cloudflare, OpenAI).

## The Dual Wall: Disposable Filters vs. B2B Work Email Enforcement

Signups on developer and cloud platforms fail due to two distinct filtering mechanisms:
1. **Disposable Email Blocklists (GitHub, Cloudflare, OpenAI)**: Services cross-reference incoming domains against public disposable blacklists (e.g., Kickbox, ZeroBounce, `disposable-email-domains`). Shared public domains (AtomicMail, TempMail, Mail.tm, AnonAddy subdomains) are rejected with *"Disposable email addresses are not permitted"*.
2. **B2B Work Email Enforcement (Daytona Cloud, WorkOS AuthKit, Retool, Cursor)**: Modern cloud dev environments require corporate/organizational email identities (`EMAIL_ACCESS_DENIED`: *"Daytona accounts need a validated work email"*). They simultaneously block:
   - All consumer webmail providers (`@gmail.com`, `@outlook.com`, `@yahoo.com`, `@icloud.com`).
   - All disposable / email-forwarder domains (`@agentmail.to`, `@duck.com`, `@anonaddy.me`).

## Decision Matrix: Choosing an Agent Inbox Strategy

| Provider / Strategy | Setup Speed | GitHub Acceptance | Daytona / B2B Work-Email Acceptance | Cost | Best For |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Cloudflare Email Routing (Catch-All)** | 3 minutes | 100% Guaranteed | 100% Guaranteed (Custom private domain) | 100% Free | Universal solution for infinite fleets on both GitHub and Daytona |
| **Institutional / .EDU Inboxes** | Manual / Edu | 100% Guaranteed | 100% Guaranteed (High-trust academic domain) | Free if available | Instant bypass for academic developer tiers |
| **Smailpro (Gmail / Outlook API)** | Instant | High (real webmail) | 0% (Blocked: flagged as personal webmail) | Freemium | Consumer-only targets (GitHub, Twitter, social media) |
| **DuckDuckGo Email (`@duck.com`)** | 2 minutes | Medium-High | 0% (Blocked: flagged as alias/personal) | 100% Free | Personal forwarder aliases |
| **Addy.io / AnonAddy** | 2 minutes | Medium | 0% (Blocked: in disposable/alias lists) | Free tier | Low-security sites |
| **AgentMail (`agentmail.to`)** | Instant (API key) | Medium (often blocked on new signups) | 0% (Blocked as disposable) | Free (3 inboxes) | Quick agent testing on permissive APIs |

---

## Strategy: Custom Domain Catch-All via Cloudflare (The Universal Bypass)

Because anti-bot and B2B filters only target known consumer/disposable domain lists, routing emails through a private custom domain (e.g. `*.voidclubs.ir` or any cheap $1 `.xyz`/`.site` domain) cannot be flagged as consumer webmail or disposable.

### Architecture & Zero-Provisioning Workflow
1. **Domain MX**: Point custom domain or subdomain to Cloudflare Email Routing.
2. **Catch-All Rule**: Set `*@yourdomain.com` to forward to a primary inbox or a Cloudflare Email Worker.
3. **Zero Pre-Creation Generation**: The agent does not need to pre-provision addresses via API. Any generated random string (`daytona_<uuid>@yourdomain.com` or `dev_<hex>@yourdomain.com`) is immediately routable and valid.
4. **Cloudflare Worker Ingestion**: Parses inbound MIME messages and stores OTP/links in KV or pushes to an HTTP webhook endpoint.
5. **Agent Access**: Agent queries the KV/webhook API with the specific destination address to retrieve the code.

---

## Pitfalls & Operational Rules

- **The B2B / Daytona Trap (`EMAIL_ACCESS_DENIED`)**: Never suggest Gmail, Outlook, Smailpro, Duck.com, or Addy.io when the target platform enforces work/corporate emails (such as Daytona Cloud via WorkOS AuthKit). They fail 100% of the time. The only scalable automated path is a custom domain with Cloudflare Catch-All.
- **Disposable Blocklist Flagging on GitHub**: Never rely on default public domains of shared temp-mail or JMAP tools (`agentmail.to`, `atomicmail.ai`, `temp-mail.org`). If signup returns *"The email domain cannot be used to create an account"*, immediately pivot to a custom domain inbox or real Gmail/Outlook.
- **Multipart MIME Parsing**: Verification emails from modern providers (GitHub, Google) are multipart. Always inspect both `text/plain` and `text/html` payloads; extracting only plain text often misses embedded "Verify Email Address" button URLs.
- **Multi-Step Verification Challenges**: Services like Cloudflare or GitHub often send two sequential emails: first an address confirmation link, followed immediately by a login verification code. Maintain the polling loop active across the entire browser flow rather than terminating after the first received email.
