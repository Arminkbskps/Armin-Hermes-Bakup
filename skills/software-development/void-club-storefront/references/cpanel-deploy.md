# VOID_CLUB cPanel deploy — UAPI + PHP port runbook (session 2026-09-10)

Project: `D:/Hermes file/VOID_CLUB_CPANEL/` (isolated from `VOID_CLUB_PROJECT/`).
Stack on host: PHP 8.3 + PDO_MYSQL + GD + mod_rewrite, MySQL `voidclub_void`, no Passenger/SSH.

## Layout
- `/api/config.php` — DB creds (`VC_DB_*`) + `VC_SECRET_KEY` (hex random). Env overrides supported.
- `/api/lib_jwt.php` — dependency-free HS256 encode/decode (base64url + hash_equals + exp check).
- `/api/lib_db.php` — PDO singleton, `vc_input/vc_send/vc_error`, `vc_current_user/vc_require_admin`, serializers mirroring FastAPI shapes exactly (`vc_product_full`, `vc_cart_full`, `vc_order_full`, `vc_wishlist_public`, `vc_coupon_public`, `vc_banner_public`), settings helpers + `vc_validate_coupon` (percent/fixed/freeship math identical to coupons.py).
- `/api/lib_upload.php` — GD adaptive watermark port of upload.py (brightness sampling → black/white logo, bottom-left 18% width, JPEG q92) + `vc_upload_guard()` (mkdir + drops uploads/.htaccess + index.html).
- `/api/api.php` — single front controller for ALL `/api/*` routes (auth/products/categories/cart/wishlist/coupons/orders/users/settings/banners/upload). Reads `?path=` from .htaccess; falls back to parsing REQUEST_URI. CORS `*` + OPTIONS short-circuit.
- `/api/schema.sql` — utf8mb4 InnoDB schema 1:1 with models.py (FKs, indexes, unique slugs/codes).
- `/install.php` — one-shot web installer (schema + 4 categories + 6 products + admin + shipping_rate). Refuses if users non-empty. MUST be deleted after use.
- `/.htaccess` — rewrites `^api/(.*)$ → api/api.php?path=$1`, forwards Authorization header, blocks schema.sql. Upload execution blocked ONLY by `uploads/.htaccess`, never globally.
- Frontend = byte-copy of `VOID_CLUB_PROJECT/frontend/` minus wrangler.toml; `js/api.js` untouched (`origin + /api`).

## cPanel UAPI patterns (token auth: `Authorization: cpanel user:TOKEN`)
- Base: `https://<host>:2083/execute/<Module>/<fn>`. Auth check: `DomainInfo/domains_data`.
- Capability probe: `Features/list_features` → `passengerapps/lvepythonsel/ssh` all 0 = no Python; `ea-php82/83` = PHP path. Many modules (Terminal, Cron, MultiPHP, ZoneEdit, DiskUsage) fail to load on this plan — treat as unavailable, not fatal.
- `Fileman/list_files` needs `?dir=<path>` (NOT `path=`); returns home listing when wrong. `get_file_content` needs `dir=` + `file=`. `save_file_content` needs `dir/file/content` (works for .htaccess overwrite). There is NO create/mkdir/delete/rename/copy in Fileman on this plan — only `upload_files` (`-F dir= -F file=@local`) + `save_file_content`.
- `upload_files` is CREATE-ONLY: any existing file (html/php/css/.htaccess)
  fails with "already exists" (seen: `.htaccess`, `shop.html`, `config.php`).
  Overwrite text files via `save_file_content` (`dir` + `file` + `content`).
- `.htaccess` needs a merge, not a replace: keep the cPanel-generated php-ini
  `error_log` block, append VC rewrite rules locally, then `save_file_content`.
  Never drop the cPanel error_log block.
- MySQL: `Mysql/list_databases`, `Mysql/list_users`, `Mysql/set_password?user=&password=`, link via `Mysql/set_privileges_on_database` (NOT `add_user_to_database` — missing on this plan). Verify link in list_databases `users:[...]`.
- Capability probes that 404/500 are normal: `get_privileges`, `get_database_info`, `compress_files`, `get_available_compression_types` don't exist here.

## DB sync: local SQLite → host MySQL via the PHP API (session 2026-09-10)

Local source of truth is `VOID_CLUB_PROJECT/fashion_shop.db` (SQLite); host runs
MySQL `voidclub_void`. Sync goes through the live `/api/*` endpoints with the admin
JWT — never direct SQL — so validation/serialization stays identical.

1. Dump local tables to JSON first (`sqlite3` row→dict for
   `categories/products/product_images/product_variants/banners/settings`), then drive
   the sync from that file. Sync script pattern lives at `D:/Hermes file/sync_db2.py`.
2. **Categories are upsert-by-slug, not blind POST.** Re-POSTing an existing slug
   returns 400 `دسته‌بندی با این نام/شناسه وجود دارد`. Flow: `GET /api/categories`
   → build `slug→id` map → `POST` only missing slugs → `PUT /api/categories/{id}`
   to fix drifted `image_url` (seen: server cats carried stale upload hashes while
   local had the real covers). Keep the local-id→slug table to remap
   `product.category_id` to the server id. Runnable template:
   `scripts/cpanel-db-sync.py` (`python scripts/cpanel-db-sync.py vc_local.json
   --base <host> --email <admin> --password <pw>`).
3. **Product POST 500s are almost always a bad `category_id`.** The PHP creator
   defaults missing ids to `1`, which may not exist → FK 500. Always send the
   remapped server category id. Payload shape: `images: [{url, is_featured}]`,
   `variants: [{size, color, stock}]` (note: `stock`, not `stock_quantity`).
4. **Banners map 1:1** — `image_url` may be `.mp4` (hero slider renders `<video>`
   for video extensions, `<img>` otherwise). `link_url` uses `shop.html?category=<slug>`
   so slugs must match the synced categories. `is_active: true` explicitly.
5. **Settings via dedicated PUTs:** `/api/settings/storefront` (`search_tags`,
   `marquee_text` — marquee must be non-empty), `/api/settings/bank-card`
   (`card_number` must be 16 digits, `/\D/` stripped, stored dashed).
6. **Verify with counts + media reachability, not just status codes.** After sync:
   `GET /api/products|/categories|/banners` → assert expected counts AND that every
   `images[].url` / `image_url` returns HTTP 200 (loop `curl` over the URL set with
   `--resolve` + `--noproxy '*'`). A 201 with a dead file path looks successful but
   renders broken on the storefront.
7. **Empty tables explain the "header not fixed" report.** `sr7-slider.js` falls back
   to `SR7_FALLBACK` (`assets/images/hero_banner.svg`) when `GET /api/banners` returns
   `[]`. If the user says the header/slider shows the placeholder even after uploading
   files, check table contents FIRST (`products: 0, banners: []`) before suspecting
   file uploads or CSS — files were fine (HTTP 200), the tables were empty.

## Live host verification (domain DNS may not resolve publicly — use --resolve)
- `curl --resolve voidclubs.ir:80:213.176.126.164 http://voidclubs.ir/<file>` bypasses DNS/proxy. Local shell proxy breaks direct HTTP — always `--noproxy '*'`.
- Env fingerprint via throwaway PHP file: `PHP_VERSION / PDO_MYSQL / GD / ZIP / upload_max_filesize` then `new PDO('mysql:host=localhost;dbname=...')` → expect `DB_OK`.
- PHP error log is readable: `Fileman/get_file_content?dir=/home/voidclub/logs&file=php.error.log` — 500s land here (e.g. missing tables `1146 Table ... doesn't exist` before install).
- API smoke before seed: `GET /api/api.php?path=settings/storefront` → 500 = wiring OK but tables missing; after install expect 200 JSON. Pretty URL `/api/settings/storefront` only works after .htaccess merge.

## Gotchas fixed this session
- Global `<FilesMatch \.(php...)$> Require all denied` in root .htaccess kills `api/*.php` too → scope execution-block to `uploads/.htaccess` only.
- Missing `Authorization` passthrough on CGI setups → add `RewriteCond %{HTTP:Authorization} . / RewriteRule .* - [E=HTTP_AUTHORIZATION:...]` + `apache_request_headers()` fallback in `vc_current_user`.
- `vc_open_image()` lost its `$ext = ...` line during a patch (left orphan body) → always re-read lib_upload.php fully after patches touching function boundaries.
- Banner create: `is_active` defaults true unless explicitly false — handle `array_key_exists` instead of `!empty` alone.
- Product create image loop: first image forced featured (`($idx===0 || $feat) && $idx===0` logic) to match FastAPI `idx==0` behavior.
- install.php schema split: `preg_split('/;\s*\n/', $sql)` — safe only because schema has no procedures/triggers.
- Local PHP lint unavailable (no php/docker binaries on agent box) → used node brace-balance scan as poor-man's syntax check; real proof is server-side error log + HTTP status.

## Local dev harness for the PHP port — `start.bat` + `router.php` + SQLite (session 2026-09-11)

`VOID_CLUB_CPANEL/start.bat` lets the user double-click to test everything locally:
no MySQL, no cPanel, and cPanel behavior stays byte-identical.

- `router.php` (docroot) mimics `.htaccess` under `php -S`: `/api/<path>` →
  `require api/api.php` with `$_GET['path']` set; existing static files `return false`;
  directory-index + `404.html` fallback included.
- `api/lib_db.php` `vc_pdo()` branches on `VC_DB_DRIVER=sqlite` env →
  `PDO('sqlite:' . (VC_SQLITE_PATH ?: VC_ROOT/data/voidclub.sqlite))` +
  `PRAGMA foreign_keys=ON` + `vc_sqlite_init()` (CREATE TABLE IF NOT EXISTS mirrors
  of `schema.sql` with SQLite-relaxed types, run on every connect). The MySQL path
  is otherwise untouched.
- `install.php` is portable: skips the MySQL-only `schema.sql` import when
  `VC_DB_DRIVER=sqlite` (tables already exist from `vc_sqlite_init()`), seeds via the
  same `seed_void_club()`, and uses `vc_set_setting()` for the shipping-rate default.
- `start.bat` flow: find `php` on PATH → else one-time download of portable PHP 8.3
  NTS zip into `tools/php` + generated `php.ini` enabling `pdo_sqlite, sqlite3,
  mbstring, gd, curl, openssl, fileinfo` → warn if `pdo_sqlite` still missing →
  set `VC_DB_DRIVER=sqlite` + `VC_SQLITE_PATH` → pick first free port
  (8000 → 8080 → 8001) → first run (no sqlite file yet) opens `install.php`,
  later runs open `index.html` → `php -S 127.0.0.1:%PORT% router.php`.
- Portability rule for any future shared-code change: `ON DUPLICATE KEY UPDATE` is
  MySQL-only — never use it in code paths that also run on sqlite; always go through
  `vc_set_setting()` / `vc_get_setting()`. Keep column names 1:1 with `schema.sql`
  and add the SQLite mirror table in `vc_sqlite_init()`.
