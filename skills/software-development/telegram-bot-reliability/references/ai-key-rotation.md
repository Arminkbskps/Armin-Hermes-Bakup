# AI Key Rotation (Gemini / Google AI Studio)

The #1 killer of long-running bots: one transient 503 puts ALL keys to sleep
for 20 minutes, the bot logs `No active Google AI Studio API key` 100x, and
every post fails with "خطا در بازنویسی".

## Tiered cooldowns

| HTTP / error              | Cooldown | Reason                              |
|---------------------------|----------|-------------------------------------|
| 429, 500, 502, 503, 504   | 2 min    | Transient / overload, retry soon    |
| network exception         | 2 min    | Same bucket as transient            |
| 400, 401, 403, 404        | 120 min  | Key is invalid/quota-dead, park it  |

Never use one flat cooldown for all codes. A 503 spike must not park a key
for 20 minutes.

## The stuck-key fix

`mark_key_used()` MUST clear the cooldown:

```python
db.execute(
    "UPDATE api_keys SET usage_count=usage_count+1, last_error=NULL,"
    " cooldown_until=NULL, success_count=COALESCE(success_count,0)+1,"
    " last_used_at=? WHERE id=?", (now_iso(), key_id))
```

Without `cooldown_until=NULL`, a key that recovers never wakes up — it stays
asleep until a manual reset. This single line was the actual root cause in
the Bot4 incident (usage 1561 vs 64 across two keys).

## Stats + reset

- Columns on `api_keys`: `success_count`, `error_count`, `last_used_at`,
  `usage_count`, `cooldown_until`, `last_error`.
- Daily table `key_daily_stats(api_key_id, day, success_count, error_count)`
  with UPSERT per call — shows ✅/❌ per key per day, 7-day rollup, success rate.
- Panel action `reset_all_key_cooldowns()`:
  `UPDATE api_keys SET cooldown_until=NULL, last_error=NULL WHERE enabled=1`.

## Single-model discipline

When the user says "remove multi-model": keep ONE `GOOGLE_MODEL` string,
delete the model list + the "try next model" branch entirely, verify with
`search_files` that zero refs to the list remain, and re-compile. A half-removed
fallback is worse than none.
