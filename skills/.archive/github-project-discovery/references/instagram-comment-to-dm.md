# Instagram comment-to-DM: deep-vet notes (OpenReply + Meta policy)

Vetted 2026-09-25 for "read this repo fully — can it run on my Python host, is there a ban risk, stable or should we build our own?"

## OpenReply (github.com/diwenne/openreply)

One-line: self-hosted ManyChat alternative — a keyword in a comment triggers an official-API private reply (DM), plus optional public reply. MIT; forked from `im-anishraj/instagram-comment-to-dm`, maintained by Diwen Huang; optional paid connection provider Zernio (sponsor).

**Verification run on this machine (2026-09-25):** `npm ci` ✅ · `npm test` after `npx prisma generate` → 26/27 files, **284 passed / 12 skipped** (DB test needs `TEST_DATABASE_URL`) · `typecheck` ✅ · `lint` ✅ · `next build` ✅.
Health: 176 commits, born ~2026-04, last commit 4 days prior, 22 contributors, 8 open/9 closed issues, **no versioned releases**, one main maintainer → active but young; good code, not battle-tested enterprise.

**Hard hosting requirements (why shared Python hosting fails outright):**
- Node 20+, Next.js 16 / React 19 / TS, **two always-on processes**: web (`next start`) + worker (`tsx worker/dm-worker.ts`) — no worker ⇒ webhooks arrive but nothing sends
- **PostgreSQL only** (`prisma/schema.prisma` → `provider = "postgresql"`), **Redis over native TCP** (BullMQ blocking commands; HTTP-only Redis rejected)
- public HTTPS webhook (`/api/webhook`); login is **email magic link only** → `RESEND_API_KEY` or `EMAIL_SERVER` SMTP is mandatory
- free stack per `docs/stack.md`: Vercel (web) + Neon (PG) + Redis Cloud 30MB + always-free VM worker under pm2 + Resend

## Official Meta private-reply policy

Source: developers.facebook.com → `documentation/business-messaging/instagram-messaging/features/private-replies` (updated 2026-07-02; the old `/docs/messenger-platform/instagram/features/private-replies` redirects there).

- Private reply = **one single message** keyed off the comment ID, within **7 days** of the comment (post/ads/reel); Instagram Live only during the broadcast
- Conversation continues only if the user replies → then the **24-hour messaging window** applies
- Delivery: followers get it in **Inbox**, non-followers in **Request** folder (low deliverability ≠ ban)
- Requirements: Page linked to the IG professional account, `instagram_manage_comments` + `pages_messaging`, Page access token from a user with the MESSAGING task
- **Standard Access** = only accounts holding a role on the app (admin/dev/tester — the normal self-host path, one tester-invite dance per account). **Advanced Access** = App Review; automated-DM apps get strict scrutiny and first submissions often fail; business verification needed to serve accounts you don't control

## Ban-risk decomposition (the verdict shape)

- **Low by construction:** official Graph API, no scraping, no browser automation, never asks for the password; self-capped at Meta's documented 750 private replies/hour with requeue-instead-of-push; honors the 7-day / one-reply-per-comment windows
- **Residual risk is behavioral:** recipient Reports, messages not relevant to the comment (Meta policy), replies firing instantly look automated (upstream feature request literally: "optional delay so replies don't look automated"), sheer volume
- App-level restriction ⇒ exceeding rate limits (the library guards it); account-level restriction ⇒ content/Reports (the library cannot guard it)
- Account must be **Business or Creator**; personal accounts cannot connect

**Build-vs-buy takeaway:** the code is the easy part — idempotent one-reply-per-comment, window-error classification, slot reserve/release around failed sends, webhook-miss reconciler are weeks of re-derivation; the Meta app / App Review work is identical under any language. A minimal self-built version (webhook receiver + queue + sender) is only worth it if the full dashboard can't be hosted anywhere else.
