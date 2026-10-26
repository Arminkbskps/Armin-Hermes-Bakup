# Disposable-Email Providers (Catchmail + Mail.tm quirks)

Session-specific provider notes from building a temp-mail bot. Providers
change response shapes without versioning — parse defensively.

## Catchmail (recommended, verified 2026-09)

- No accounts, no tokens, no passwords: ANY `slug@catchmail.io` is instantly
  receivable. The bot just invents a slug and polls.
- `GET https://api.catchmail.io/api/v1/mailbox?address=FULL` → 200 with
  `{address, page, page_size, messages[], count, total}`; each item
  `{id, mailbox, from, subject, date, size}`.
- `GET /api/v1/message/{id}?mailbox=FULL` → full
  `{from, to, subject, date, body: {text, html}, attachments[]}`.
  Unknown id → 404 `{"detail":"Message not found"}`.
- `DELETE /api/v1/message/{id}?mailbox=FULL` → 200/204.
- Limits: 1 req/sec/IP anonymous (higher with API key); messages auto-delete
  ≤ 7 days. Per-address web view (auto-refresh 5s):
  `https://catchmail.io/mailbox/catchmail.io/{slug}` — give users a URL
  button to it.
- Watcher implication: no auth expiry, so a poll loop + `seen` table keyed
  by `(address, msg_id)` is enough; extract OTP codes with a `\d{4,8}`
  regex over text/HTML-stripped body.

## Mail.tm (brittle — lessons, not a recommendation)

- Docs show Hydra (`hydra:member`) but the live API v2 returns BARE JSON
  lists for `/domains` and `/messages`. Always normalize:
  `payload if isinstance(payload, list) else payload.get("hydra:member", [])`.
  Shipping only the dict path broke domain fetch AND account creation at
  runtime (empty domain → garbage address → 422).
- `POST /accounts` enforces password policy: a 14-char lowercase+digits
  password got `422 Unprocessable Entity`; mixed-case+digit worked. Never
  assume the failure is the address — log the response body.
- Token auth (`/token` + `Authorization: Bearer`) per account; tokens expire,
  so the watcher must handle 401 with re-login, and the sessions table must
  store passwords — i.e. the DB schema couples to the provider.
- Takeaway: provider-owned auth state means switching providers later MEANS
  a schema migration (see `sqlite-migration.md` → Provider switch).
