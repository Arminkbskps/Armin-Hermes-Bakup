# SEO Indexability + Hidden-Modal Leak (VOID CLUB, 2026-09-30)

Class-level lessons from one session covering a Search Console Coverage
export (`Chart.csv / Critical issues.csv / Non-critical issues.csv /
Metadata.csv`) and a leaked invoice modal in `account.html`.

## 1. Coverage triage (read the export before touching code)

| Reason | Meaning | Action |
|---|---|---|
| Discovered - currently not indexed (58) | Fresh site, crawl-budget queue — normal | No fix; Request Indexing on 5–10 key URLs |
| Duplicate without user-selected canonical (46) | WE told Google the pages are duplicates | Fix canonical self-harm (see §2) |
| Crawled - currently not indexed (10) | Crawled but judged too thin | Thicken SSR view-source (see §3) |
| Blocked by robots.txt (3) / Page with redirect (1) / Alternate with proper canonical (6) | Intentional (api/, payping/, account/checkout/login, 301s) | Leave alone |

Chart.csv showed first data 2026-09-18 → site ~2 weeks old; most
"not indexed" is age + queue, not a blocker. Verify live
`robots.txt` health first (Allow: /, Disallow: api/payping/account/
checkout/login/callback, Sitemap: sitemap.php + sitemap.xml).

## 2. Canonical self-harm pattern (the 46 duplicates)

Root cause: NO `shop.php` pre-renderer existed, so `/shop?category=X`
served static `shop.html` whose hardcoded canonical pointed at plain
`/shop` — while `sitemap.php` submitted `/shop?category=anime` as its
own URL. Mixed signal = "Duplicate without user-selected canonical".

Fix (mirrors existing `product.php` / `categories.php` pattern):
- Create `shop.php`: category self-canonical
  (`/shop?category=X` → itself), facet params (sort/type) collapse to
  the base category URL, `?q=` search pages get `noindex,follow`
  (robots.txt already Disallows `?q=`), paginated pages keep `&page=N`.
- `.htaccess`: `RewriteRule ^shop$ shop.php [QSA,L]`, remove `shop`
  from the `*.html` clean-URL rule, add `shop.php → /shop` 301 next to
  the product/categories ones.
- Keep client-side `vcSetSeoMeta` in `js/app.js` consistent with the
  server canonical.
- Unify sitemaps: static `sitemap.xml` had drifted from dynamic
  `sitemap.php` (missing `/shop?category=anime`, 120 vs live DB).
  Add the missing URL; submit ONLY `sitemap.php` in Search Console.

## 3. Thin-SSR pattern (the 10 crawled-not-indexed)

`product.html` view-source (what Google indexes pre-JS) was a bare H1
+ skeleton divs; all real content rendered by `drawProductDetails()`.
Fix without ANY visual change: inject an invisible `.sr-only`
snapshot (existing class in `css/core.css`) inside
`#product-detail-layout` server-side — h2 title, category, price,
stock, ~600 chars of description, featured img. JS wipes it on load,
so users never see it. Guard vars (`$ssFull/$ssToman`) so an empty-DB
branch can't emit undefined-variable output.

## 4. Conditionally-loaded CSS leaking raw modals (account.html)

Root cause: `invoice-print.css` (which carries
`.invoice-modal{display:none}` / `.open{display:flex}`) was injected
ONLY for admins via the localStorage `is_admin` script, but the
`#order-invoice-modal` markup ships for EVERY user. As a plain user
the unstyled modal rendered its raw template (`-`, `۰ تومان`, empty
table) inline at the bottom of the panel — looked like "something new
and broken was added".

Fix (zero visual change):
1. Load `invoice-print.css` globally via `<link>` for all users.
2. Remove it from the admin-only JS injection list (avoid double load).
3. Belt-and-braces: inline `style="display:none"` on the modal shell
   (no-CSS fallback) + `modal.style.display='flex'/'none'` in
   `openOrderInvoiceModal` / `closeInvoiceModal` alongside the class
   toggle.

Rule: NEVER gate a stylesheet on role when its `display:none`
hides markup that ships to other roles.

## 5. No fake-fallback data in invoice paths

`vc_order_full` (lib_db.php) and `openOrderInvoiceModal` (app.js)
contained demo fallbacks (sample buyer name/phone, sample product
titles). A leaked/empty order then shows PLAUSIBLE-LOOKING fake data.
Prefer honest empties (`—`, "محصول حذف‌شده") over invented values.
