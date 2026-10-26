# SQLite Additive Migration Pattern

Bots ship with a live DB full of user data. Migrations must be additive and
idempotent — the bot restarts with the new file and upgrades itself.

## Pattern

```python
# New tables: always IF NOT EXISTS
self.execute("""CREATE TABLE IF NOT EXISTS post_versions (...)""")

# New columns: suppress the "already exists" error on re-run
for col_sql in (
    "ALTER TABLE rewritten_posts ADD COLUMN hot_alerted INTEGER DEFAULT 0",
    "ALTER TABLE api_keys ADD COLUMN error_count INTEGER DEFAULT 0",
):
    with contextlib.suppress(sqlite3.OperationalError):
        self.execute(col_sql)

# New settings: set_default (INSERT OR IGNORE semantics)
self.set_default("digest", "1")
self.set_default("last_digest_day", "")
```

## Rules

- Never DROP, never recreate, never `DELETE FROM` user tables on upgrade.
- New code must tolerate old rows: use `_row_get(row, key, default)` /
  `COALESCE(col,0)` wherever a new column is read (SQLite Rows raise on
  missing keys only if the SELECT names them — but `SELECT *` on an old DB
  file opened by new code is fine; the reverse is not).
- Deploy = copy file + restart. No manual SQL step.

## Provider switch (retire-by-rename, not DROP)

When the backend provider changes and old session rows become useless
(temp-mail Mail.tm → Catchmail: old `account_id`/`token`/`password` columns
mean nothing), do NOT ALTER the old shape into the new one. Detect via
`PRAGMA table_info`, rename the stale table aside, then create fresh —
users/channels tables stay untouched:

```python
cols = {r[1] for r in con.execute("PRAGMA table_info(sessions)").fetchall()}
if cols and "username" not in cols:  # old provider-era schema
    con.execute("DROP TABLE IF EXISTS sessions_legacy")
    con.execute("ALTER TABLE sessions RENAME TO sessions_legacy")
# same for seen_msgs when the key changes (account_id → address)
con.executescript("CREATE TABLE IF NOT EXISTS sessions ...")
```

Rename instead of DROP keeps a recoverable copy if the rollout is reverted.
Real incident: temp-mail bot crashed on EVERY callback with
`sqlite3.OperationalError: table sessions has no column named username`
after a provider switch shipped without this — fixed by rename-on-startup.

## Smoke test (temp DB, no user data touched)

```python
import sqlite3, tempfile, os
fd, p = tempfile.mkstemp(suffix=".sqlite3"); os.close(fd)
con = sqlite3.connect(p)
# 1. create the OLD schema (copy the CREATE TABLEs from the previous file)
# 2. run the new migration block
# 3. exercise UPSERT/SELECT paths (retry enqueue, daily stats, versions)
con.close(); os.unlink(p)
```

Real incident: Bot4's DB had 916 incoming / 745 rewritten / 3312 post_checks
rows plus 681 cached web rows. A `cleanup_loop` (TTL: web cache 7d,
post_checks 14d, decisions 30d, media 14d, tmp always, then VACUUM) keeps it
small — but cleanup is a loop, never part of migration.
