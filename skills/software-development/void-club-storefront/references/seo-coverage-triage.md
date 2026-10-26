# Search Console Coverage Triage (session 2026-09-30, VOID_SEO_BOOST_v2)

Read the exported Coverage CSVs FIRST (`Chart.csv` + `Critical issues.csv`) — the
reason strings tell you exactly which class of fix to apply:

| Coverage reason | Seen | Meaning → action |
|---|---|---|
| `Duplicate without user-selected canonical` | 46 | URL is sitemap-submitted but canonicalizes elsewhere → find the mismatch, fix the canonical (below) |
| `Crawled - currently not indexed` | 10 | Google fetched it but judged it thin → thicken server-rendered view-source (below) |
| `Discovered - currently not indexed` | 58 on a fresh site (first data 2026-09-18) | Crawl-budget queue on a new site → NO action, resolves with time + manual URL Inspection on top pages |
| `Blocked by robots.txt` / `Page with redirect` / `Alternate page with proper canonical` | 3 / 1 / 6 | Intentional → do NOT "fix" |

## Fix 1 — shop canonical self-harm (the 46 duplicates)

Root cause: NO `shop.php` pre-renderer existed (only `product.php`/`categories.php`),
so `shop?category=X` served static `shop.html` whose hardcoded canonical pointed at
plain `/shop` — while `sitemap.php` submitted `shop?category=anime` as its own URL.
Google saw "submitted URL canonicalizes elsewhere" → duplicate.

New `shop.php` mirrors the `product.php`/`categories.php` pattern:
- Self-canonical per category (`/shop?category=<slug>` canonicalizes to itself).
- Facet params (`sort`/`type`) collapse to the base category URL; `?page=N` kept
  on the canonical (paginated series self-canonicalize).
- `?q=` search pages → `noindex,follow` (robots.txt already `Disallow`s `?q=`).
- BreadcrumbList JSON-LD + invisible `.sr-only` helper only (existing `core.css`
  class, JS wipes it on render) — zero visual change.
- `.htaccess`: `^shop$ → shop.php [QSA,L]`, plus `shop.php → /shop` 301 guarded by
  `%{THE_REQUEST}` (same infinite-loop prevention as product/categories), and
  remove `shop` from the `(.html)` clean-URL group.

## Fix 2 — thin product view-source (the 10 crawled-not-indexed)

Root cause: product view-source before JS runs is a bare H1 + two skeleton divs —
Google judges it content-free. Fix = `product.php` section 4b: invisible
`.sr-only#vc-ssr-snapshot` (title / price-fa / stock / desc-600 / img, existing
`core.css` class, wiped by `drawProductDetails()` on load). Zero visual change.

## Fix 3 — static/dynamic sitemap split

`sitemap.php` listed `shop?category=anime` but static `sitemap.xml` didn't. Keep
both files' URL sets identical (121 `<loc>` after fix). Search Console submission:
`sitemap.php` only (dynamic, always DB-synced).

## Verify

- `node --check js/app.js` → clean.
- `grep -n "shop" .htaccess` → rule order: 301-guard (sec 6) before internal
  rewrite (sec 8) before clean-URL group (sec 9, shop NOT in it).
- `grep -c "<loc>" sitemap.xml` matches `sitemap.php` URL count.
- Ship zip with Python `shutil.make_archive` — NEVER `Compress-Archive`
  (backslash entry names break cPanel extraction).

## After upload (tell the user)

- Submit only `sitemap.php` in Search Console.
- URL Inspection → Request Indexing for 5–10 top URLs (shop, products,
  categories) to pull Discovered URLs forward.
- Duplicates + Crawled-not-indexed clear themselves over 1–2 crawl cycles.
