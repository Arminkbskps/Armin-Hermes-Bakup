# Retry Queue (never lose a failed rewrite)

Failed posts must wait in a queue with backoff — not die with a final error card.

## Schema

```sql
CREATE TABLE IF NOT EXISTS retry_queue (
  id INTEGER PRIMARY KEY AUTOINCREMENT,
  incoming_post_id INTEGER UNIQUE,
  tone TEXT DEFAULT 'telegram',
  attempts INTEGER DEFAULT 0,
  max_attempts INTEGER DEFAULT 5,
  next_try_at TEXT,
  last_error TEXT,
  status TEXT DEFAULT 'queued',
  created_at TEXT, updated_at TEXT);
ALTER TABLE incoming_posts ADD COLUMN rewrite_error TEXT;
```

## Enqueue (exponential backoff)

- `RETRY_BASE_DELAY_SECONDS = 300` (5m); delay = base * 2^(attempts-1):
  5m → 10m → 20m → 40m → 80m, capped at `RETRY_MAX_ATTEMPTS = 5`, then `dead`.
- `ON CONFLICT(incoming_post_id) DO UPDATE` so re-fails refresh the row.
- Success path sets `status='rewritten'`, clears `rewrite_error`, and marks
  the queue row `done`.

## Failure card

On AI exception, insert a `rewritten_posts` row with `status='failed'` and
send the admin a card: `⚠️ خطا در بازنویسی`, next auto-retry time, and
buttons `post:retry:<failed_id>` + `post:details` + `post:reject`.

## Loops

- `retry_loop`: every 60s, pick up to 5 due rows
  (`status='queued' AND next_try_at <= now`), call the same
  `create_rewrite_for_incoming(bot, incoming_id, tone, retry_of, quiet=True)`.
- Manual retry (`post:retry:...`, `retry:now:...`) funnels into the same create
  function — one code path, not two.
- `mark_key_used` on success also finishes the queue row.

## Panel

- `🔁 صف تلاش مجدد` lists queued rows (incoming id, attempts, next try) with
  `retry:now:<incoming_id>` per row.
- `♻️ ریست کول‌داون همه` + `🔁 تلاش مجدد همه failها` belong next to the queue.
