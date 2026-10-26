# 9router Dashboard Password — Auth Internals & Recovery

Reverse-engineered from 9router v0.5.81 (minified Next.js server chunks).
Verified end-to-end: default login → bcrypt set → new-pass login OK → old-pass rejected → tunnel login OK.

## Where the password lives

- SQLite DB, `settings` table, row `id=1`, JSON blob in `data` column → key `password`.
- Value is a **bcrypt hash** (`$2b$12$...`), compared at login with bcrypt compare
  (hasher module uses `$2b$` salt generation — standard bcrypt).
- Find the LIVE db first: 9router resolves its data dir from the *process* HOME/cwd
  (`~/.9router` under the daemon's env), which may differ from your shell's `$HOME`.
  Don't guess — read `/proc/<9router-pid>/cwd` + `/proc/<pid>/environ` (HOME, DATA_DIR),
  then inspect that `<dir>/db/data.sqlite`.

## Default when unset

- If `password` is absent/empty AND `INITIAL_PASSWORD` env is unset → dashboard password is `123456`.
- Check state without guessing: `GET /api/auth/status` returns `hasPassword` + `requireLogin`.

## The trap: reset-password CLEARS, it doesn't set

- `POST /api/auth/reset-password` with `{"password": null}` **clears** the password
  (sets it to null → back to `123456` default). It is not a set-password endpoint.
- There is no CLI command to set the dashboard password either (`9router --help`
  shows only port/host/no-browser/tray/skip-update flags).

## Setting a password directly (verified recipe)

```bash
pip install --break-system-packages bcrypt   # if externally-managed python
python3 - <<'EOF'
import bcrypt, sqlite3, json
h = bcrypt.hashpw(b'<NEW-PASSWORD>', bcrypt.gensalt()).decode()
con = sqlite3.connect('<LIVE-DIR>/db/data.sqlite')
s = json.loads(con.execute('select data from settings where id=1').fetchone()[0])
s['password'] = h
con.execute('update settings set data=? where id=1', (json.dumps(s),))
con.commit()
EOF
```

## Verification (all three, in order)

1. `POST /api/auth/login {"password":"<NEW>"}` → `{"success":true}` (local).
2. Same with the OLD password → `{"error":"Invalid password. N attempt(s) left..."}`.
3. Same login through the remote URL/tunnel → `{"success":true}`.

## Pitfalls

- **Lockout counter is real.** Every failed login decrements `remainingBeforeLock`
  ("4 attempt(s) left before lockout", then 429). Batch-verify with the right password;
  don't probe blindly.
- **Secret round-trip check.** When writing any token/password through layered exec
  (local script → bridge → remote shell → file), a truncated write looks exactly like
  an invalid credential at the far end (e.g. Telegram `404 Not Found` on a token that
  lost its `:` in transit). After every secret write, read it back and assert
  length + delimiter count + full-match BEFORE concluding the credential is bad.
