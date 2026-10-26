---
name: atomicmail
description: "Send and read agent email via Atomic Mail JMAP."
version: 0.1.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [email, jmap, atomicmail, agents]
    related_skills: [himalaya]
---

# Atomic Mail Skill

Atomic Mail is an ESP for AI agents. You manage mail over JMAP (RFC 8620 + RFC 8621)
through a single shell CLI with three commands: `register`, `jmap_request`, `help`.

This skill is separate from `himalaya` (IMAP/SMTP for human mailboxes) and from the
Hermes Email gateway adapter (lets people email the agent). Use it when the task
needs the agent's own `@atomicmail` inbox.

## When to Use

- Register a new agent inbox, or log in with an existing API key.
- Send mail, list/read inbox, reply, upload attachments via JMAP.
- Look up exact JMAP shapes, presets, placeholders before guessing.

Don't use for: human Gmail/IMAP mailboxes (use `himalaya` instead).

## Prerequisites

- Node.js >= 20 (`node --version` to verify) + `npx` available.
- Credentials live in a credentials dir (default `~/.atomicmail/`:
  `credentials.json` + JWTs). Pass `--credentials-dir DIR` to isolate accounts.
- No API key / env var needed before register — `register` creates them.

Canonical runner (always through the `terminal` tool):

```bash
npx --package=@atomicmail/agent-skill atomicmail <command> [options]
```

> Do NOT use `npx --package=@file:...` — that form fails with `file not found`.
> Package name is `@atomicmail/agent-skill` (note the `/`, no `:` prefix tricks).

## Quick Reference

```bash
# Register (username 5-21 chars, permanent public address — ask operator for the name)
npx --package=@atomicmail/agent-skill atomicmail register --username "myagent"

# Log in with existing key
npx --package=@atomicmail/agent-skill atomicmail register --api-key UUID

# Inline JMAP batch
npx --package=@atomicmail/agent-skill atomicmail jmap_request \
  --ops '[["Mailbox/get", {"accountId": "$ACCOUNT_ID"}, "m0"]]'

# From a preset file + vars
npx --package=@atomicmail/agent-skill atomicmail jmap_request --ops-file send_mail.json
npx --package=@atomicmail/agent-skill atomicmail jmap_request --credentials-dir ./.atomic-mail \
  --ops-file send.json --vars '{"TO":"a@b.com","SUBJECT":"Hi","BODY":"Hello"}'

# With attachment (injects $ATTACHMENT_N_* vars)
npx --package=@atomicmail/agent-skill atomicmail jmap_request \
  --ops-file send_mail_blob_attachment.json --attachment ./notes.txt \
  --vars '{"TO":"self@example.com","SUBJECT":"File","BODY":"See attach."}'

# Dry run (prints resolved request, no send; incompatible with --attachment)
npx --package=@atomicmail/agent-skill atomicmail jmap_request --ops-file send_mail.json --dry-run

# Help first — topics match the installed version
npx --package=@atomicmail/agent-skill atomicmail help --topic overview
npx --package=@atomicmail/agent-skill atomicmail help --topic presets
npx --package=@atomicmail/agent-skill atomicmail help --topic jmap_cheatsheet
```

Help topics: `overview, installation, auth, jmap_cheatsheet, tools, presets,
troubleshooting, readme, cron, multi-account`. Call `help` before guessing protocol details.

## Procedure

1. **Register or log in.** Completion: credentials dir contains `credentials.json`.
   - New inbox: `terminal(command="npx --package=@atomicmail/agent-skill atomicmail register --username \"NAME\"")`.
   - Username is permanent and appears on every sent message — if the operator
     hasn't named it, ask them instead of inventing one.
   - `register` requires a `--watch` decision (who reads the inbox). Run `register`
     with no `--watch` to see the choices, then ask the operator; don't pick silently.
2. **Inbox polling (Hermes).** Completion: operator confirmed scheduled vs on-demand.
   - Registration alone reads nothing. On `watch="scheduled"`, schedule a daily
     **agent turn** on Hermes' own scheduler — never `crontab`/systemd/wrapper scripts,
     never `atomicmail jmap_request` alone, never cross-runtime (register on host A,
     cron on host B is forbidden).
   - `register --watch scheduled` prints the exact host-specific setup step — run it.
   - Hermes shape: `hermes cron create "0 9 * * *" "<prompt with list_inbox.json inside>" --name "atomicmail-inbox" --deliver origin`.
   - No durable scheduler (session-only runtimes): ask the operator to poll on a
     durable host or fetch manually.
3. **Send / read mail via `jmap_request`.** Completion: JMAP response shows created/sent IDs.
   - Bundled presets (relative `ops-file` resolves from credentials dir first, then
     bundled): `send_mail.json`, `list_inbox.json`, `reply.json`,
     `send_mail_attachment.json`, `send_mail_blob_attachment.json`.
   - Placeholders `$ACCOUNT_ID`, `$INBOX`, `$INBOX_MAILBOX_ID`, `$UPLOAD_URL`,
     `$DOWNLOAD_URL` auto-resolve; any other `$NAME` (e.g. `$TO`, `$SUBJECT`,
     `$BODY`, `$MAIL_ID`) must come from `--vars '{"TO":"..."}'`.
   - `send_mail.json` needs `TO/SUBJECT/BODY`; `reply.json` needs `MAIL_ID/BODY`;
     `list_inbox.json` needs nothing extra.
   - Capabilities (`using`): bare methodCalls default to core+mail only; for
     submission/blob methods use a full envelope with `core+mail+submission` (+`blob`).
4. **Verify.** Completion: mail appears in inbox / send response has no `error` key.
   - `--dry-run` first when testing new ops. Re-check sends via `list_inbox.json`.

## Pitfalls

- `inMailbox` expects the mailbox **id** (`$INBOX_MAILBOX_ID`), not the email address.
- Missing `$TO` etc. = you forgot `--vars`. Blob/upload shape errors = `data` must be
  an array of datasource objects — check `help --topic troubleshooting` first.
- `register` PoW uses scrypt (`N=16384,r=8,p=1,dklen=64`); JWTs refresh automatically
  and persist to disk. Missing-credentials error = run `register` or fix `--credentials-dir`.
- `atomicmail help <topic>` (positional) is wrong — use `atomicmail help --topic <topic>`.
- On Windows/MSYS the `terminal` tool runs bash: quote `--vars` JSON in single quotes
  so `$TO`-style values aren't expanded by the shell.

## Verification

- `terminal(command="npx --package=@atomicmail/agent-skill atomicmail help --topic presets")` lists bundled presets.
- `terminal(command="npx --package=@atomicmail/agent-skill atomicmail jmap_request --ops-file list_inbox.json --dry-run")` prints a resolved request without sending.
- A real `jmap_request` returns JMAP `methodResponses` with created IDs and no `error` type.
