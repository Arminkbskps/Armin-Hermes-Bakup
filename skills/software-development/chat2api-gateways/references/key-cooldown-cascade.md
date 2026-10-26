# API-Key Cooldown Cascade (recurring-outage pattern)

Seen in a production Telegram content bot rotating Google AI Studio keys.

Symptom: bot works for days, then every rewrite fails for ~20 min with
`No active Google AI Studio API key`, then recovers, then dies again.
Log pattern: `Google HTTP 503` once → `No active key` repeatedly → `AI rewrite failed`.

Root cause: uniform cooldown-on-error. One transient 503 put EVERY key to
sleep for 20 minutes, so subsequent requests saw zero active keys and failed
— a deterministic cascade, not bad luck. Two compounding bugs:
- `mark_key_used` cleared `last_error` but NOT `cooldown_until`, so sleep/wake logic drifted.
- Dead fallback (`g4f` default provider needing auth) meant no second chance.

Fix (status-code-differentiated cooldowns):
- 429/500/502/503/504 (transient overload/quota) → 2 min cooldown, try next key.
- 404 (retired model name) → do NOT punish the key; try next model in a
  `GOOGLE_MODELS` list (`gemini-3.5-flash-lite`, `gemini-2.5-flash-lite`,
  `gemini-2.0-flash`, `gemini-1.5-flash`).
- 400/401/403 (bad/blocked key) → 120 min cooldown, try next key.
- Success path MUST clear `cooldown_until` (`UPDATE ... SET cooldown_until=NULL`).
- Failed work goes to a `retry_queue` table with exponential backoff
  (5m → 10m → 20m …) + a manual Retry button, instead of an instant
  user-facing "rewrite failed" message.
- Track per-key `success_count` / `error_count` / daily stats so the next
  debugging session can see which key is actually sick.

Diagnostic shortcut: `grep -c "No active.*key" bot.log` vs `grep -o "Google HTTP [0-9]*"
bot.log | sort | uniq -c` — one transient error followed by a burst of
"no active key" confirms the cascade.
