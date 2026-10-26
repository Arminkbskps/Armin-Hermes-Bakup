# Ops Loops (digest, heartbeat, watchdog, backup, cleanup)

Independent `asyncio.create_task(...)` loops started in `on_startup`, each
gated by its own `db.get_setting(...)` toggle so the panel can switch it off.

## scan_loop (existing) + stamp

Stamp `db.set_setting("last_scan_ok", now_iso())` after every successful pass
(and in `sync_self_channel_archive`). Every other loop reads this stamp.

## digest_loop — daily summary + hot alerts

- `DIGEST_TIME_UTC = "17:30"` (= 21:00 Tehran, UTC+3:30). Loop sleeps 60s,
  fires once when `HH:MM` matches and `last_digest_day != today`.
- Summary counts: incoming today, rewritten today, hot (score ≥ threshold),
  used/rejected, failed, currently pending, feedback good/bad, plus top-5 by
  `importance_score`.
- `maybe_hot_alert(bot, rewritten_id)`: if `importance_score >=
  HOT_SCORE_THRESHOLD` (9) and `hot_alerted == 0`, send `🔥 خبر داغ!` card
  immediately and set `hot_alerted=1`. Called right after a successful rewrite.

## heartbeat_loop + watchdog_loop — liveness

- `heartbeat_loop` every 6h (`HEARTBEAT_INTERVAL_SECONDS = 21600`): `💓 زنده‌ام`
  with pending count, retry-queue depth, and last successful scan time.
- `watchdog_loop` every 5 min: if `now - last_scan_ok > max(3×scan_interval,
  30 min)` → `🚨 اسکن گیر کرده` alert with the stale duration. This catches
  the "bot silently dead for days" case the user originally reported.

## backup_loop — weekly DB copy to admins

- Every 7 days (`BACKUP_INTERVAL_SECONDS = 604800`): WAL checkpoint
  (`PRAGMA wal_checkpoint(TRUNCATE)`), copy DB to tmp, `send_document` to all
  admins, delete tmp copy. Plus on-demand `💾 بکاپ` panel button.

## cleanup_loop — daily TTL + VACUUM

- `auto_cleanup_once()`: delete `web_search_cache` > 7d, `post_checks` > 14d,
  `decisions` > 30d, finished retry rows, `media/` > 14d, all of `tmp/`,
  then `VACUUM`. Report counts to the panel `🧹 پاکسازی` button.

## Review ops (bonus, same session)

- **Pending pagination + search**: 8 per page (`PENDING_PAGE_SIZE`), prev/next
  buttons, `🔍 جستجو` stored per-admin (`pending_search_<id>`), `-` clears.
- **Bulk approve/reject**: act on the whole filtered set (cap 200), then
  re-render the page.
- **Post versions**: `post_versions` table; save old text on every manual edit
  / format / unformat; `↩️ نسخه‌ها` lists with one-tap restore.
- **Feedback**: `post_feedback(rewritten_post_id PK, vote)` + counters
  `feedback_good/feedback_bad`; toggle semantics (repeat vote removes it).
- **Error panel**: `📋 خطاها` tails the log for `[ERROR]/[WARNING]/Traceback`
  (last 15 lines) + `🔁 تلاش مجدد همه failها`.
- **Channel preview**: `👀 پیش‌نمایش کانال` sends header + media-with-caption +
  overflow continuation exactly like the target channel would show it.
