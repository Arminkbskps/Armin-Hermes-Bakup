---
name: external-api-integration
description: >
  Use when calling external APIs in automation.
version: 1.0.0
author: hermes-curator
license: MIT
metadata:
  hermes:
    tags: [api, automation, ci, cloudflare, secrets]
    related_skills: [cloudflare-deploy, github-pr-workflow]
---

# External API Integration

## When to Use

Trigger when a task involves calling a third-party API from a script, worker,
or CI job — AI providers, Cloudflare, GitHub, or similar. Especially when
auth fails mysteriously, a provider "changed something", a sync step is green
but data never arrives, or server-to-server HTTP 403s appear.

Two assumptions cause most breakage: **the provider's format is stable** (it is
not — key prefixes, SDKs, and model IDs rotate) and **a bare HTTP client is
enough** (WAFs disagree). This skill encodes the defensive pattern.

## Steps

1. **Verify the provider live before coding.** Check the vendor's current docs /
   SDK for the auth format, endpoint shape, and valid model IDs. Never trust a
   remembered format (see references/provider-drift-case.md for a session where
   `AIza`-prefix validation and `generateContent` REST were both already
   outdated).
2. **SDK-first with REST fallback.** Prefer the vendor's current SDK; wrap it so
   a missing/renamed SDK falls back to plain REST. Pin the SDK in
   `requirements.txt` (or equivalent) so CI actually installs it.
3. **Never validate secrets by shape.** Key prefixes rotate (`AIza…` →
   `AQ.…`). Treat any non-empty secret as opaque; validity is decided by one
   live test call, not by regex.
4. **Keep model IDs in config, not code.** Read provider/model from a settings
   file or env with a sane default. Rotating a model must be a config edit, not
   a code deploy.
5. **Always send an explicit `User-Agent` on server-to-server requests.**
   Cloudflare WAF/bot-fight blocks headerless clients (notably Python
   `urllib`'s default) with 403. Set something identifiable, e.g.
   `site-summarizer-ci` or `Mozilla/5.0 (compatible; <project>/1.0)`.
6. **Single source of truth for secrets.** If users enter keys in an admin UI,
   sync them into automation (CI env) from that store — masked — instead of
   requiring a second manual entry in CI secrets. Document which store wins.
7. **Fail loudly in automation.** A sync/push step that swallows per-item
   errors and exits 0 produces phantom green runs. Log per-item `ok/FAIL`,
   count failures, and `exit 1` (e.g. `::error::`) when any item fails.
8. **Verify end-to-end, not just status codes.** After a write, read the value
   back (PUT → GET round-trip with a distinctive marker during diagnosis) and
   distrust edge caches: send `Cache-Control: no-store` and cache-bust reads
   (`?t=<ts>`) while debugging staleness.

## Pitfalls

- Hardcoding a key-prefix check rejects valid rotated keys and sends you
  debugging the wrong layer (auth) when the real breakage is elsewhere.
- When the user reports a live test contradicting your diagnosis (e.g. "I
  tested the token, it works"), believe their test first and re-examine your
  own assumptions — in the source session the remembered `AIza` rule was
  wrong, the user's key was valid, and the bug was the outdated endpoint.
- `urllib` without headers works from a laptop but 403s from CI/datacenter IPs
  behind Cloudflare — always set `User-Agent`, and test from the CI network,
  not just locally.
- Silent-failure push loops: `except: print('fail')` + exit 0 hides systemic
  breakage for weeks. Count and raise.
- Concurrent automation writers racing on one branch: use run concurrency
  (e.g. `concurrency: group: …`, `cancel-in-progress: false`) plus pull/rebase
  + push-retry in the commit step.

## Verification

- [ ] One live test call per provider with the real secret, from the CI
       network (or a runner-equivalent), before declaring integration done.
- [ ] Requirements/lockfile includes the SDK; CI log shows it installed.
- [ ] Push/sync step log shows per-item results and non-zero exit on failure.
- [ ] Round-trip read-back returns the written value (no stale cache).

## Files

```text
external-api-integration/
├── SKILL.md                        ← you are here
└── references/
    └── provider-drift-case.md      ← real session: AI Studio format rotation
                                      + Cloudflare UA 403 + secret-sync fix
```
