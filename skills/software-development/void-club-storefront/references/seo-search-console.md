# SEO — robots.txt + sitemap + server-side pre-rendering for VOID_CLUB_CPANEL (Search Console, Social Previews & IndexNow)

Use when the user asks about Google Search Console, IndexNow, indexing, robots, sitemap, search-result title/description, or social link cards (Telegram/WhatsApp/Twitter).

## Architecture: Hybrid Static + PHP Pre-Render (Zero Frontend Visual Change)

Because Googlebot, search crawlers, and social link unfurlers (Telegram, WhatsApp, Twitter) fetch raw server HTML without executing asynchronous client-side JavaScript, relying solely on `app.js` causes:
- 100% duplicate title tags (`مشخصات محصول | VOID CLUB`) across all products.
- No OpenGraph preview image or price when sharing links.
- Static canonical tag on `categories.html` cannibalizing category collection rankings.

### Solution: Transparent Apache Rewrite to PHP Pre-renderers
In `.htaccess`:
```apache
# 301 Redirect /index.html to / (Consolidate canonical signal)
RewriteCond %{THE_REQUEST} ^[A-Z]{3,9}\ /index\.html\ HTTP/
RewriteRule ^index\.html$ / [R=301,L]

# SEO Dynamic Pre-renderers for Products and Categories
RewriteRule ^product\.html$ product.php [QSA,L]
RewriteRule ^categories\.html$ categories.php [QSA,L]
```

### Pre-Renderer Files (docroot `public_html`)

1. **`product.php`**:
   - Reads `$_GET['id']` and queries `products` + `product_images` via `api/lib_db.php` (`vc_pdo()`).
   - Replaces `<title>` with `خرید {title} | VOID CLUB`.
   - Injects dynamic `<meta name="description">` (trimmed to 160 chars).
   - Injects absolute canonical `<link rel="canonical" href="https://voidclubs.ir/product.html?id={id}">`.
   - Injects complete OpenGraph (`og:title`, `og:description`, `og:image`, `og:url`, `product:price:amount`, `product:price:currency`).
   - Injects Twitter Cards (`summary_large_image`).
   - Injects Schema.org `Product` JSON-LD (with price in IRR, inLanguage `fa-IR`, `InStock`) and `BreadcrumbList`.
   - Flushes the original `product.html` template. If DB is unavailable, falls back cleanly to static template with zero 500 errors.
   - Preserves 100% byte-identical visual layout and DOM for the browser.

2. **`categories.php`**:
   - Reads `$_GET['category']` (or `category_id`).
   - Injects specific title: `خرید تیشرت و هودی‌های {category} | VOID CLUB`.
   - Injects specific canonical: `https://voidclubs.ir/categories.html?category={slug}` (fixes the canonical self-harm bug where all collections canonicalized to generic `categories.html`).
   - Injects category-specific meta description and OG metadata.

3. **`sitemap.php`** — DYNAMIC source of truth, always in sync with live DB:
   - Requires `api/lib_db.php` (`vc_pdo()`), outputs `Content-Type: application/xml`.
   - Excludes `/index.html` (only keeps root `/` with priority 1.0).
   - Deduplicates all category and collection URLs (normalizes lowercase slugs).
   - Dynamically loops through all active products (`product.html?id={id}`) with priority 0.8.
   - Deduplicates via `$seenUrls` hash set to prevent crawl budget waste.
   - Wrapped in try/catch — on failure still serves static routes.

4. **`robots.txt`**:
   - Allow `/`, block sensitive folders (`/api/`, `/tools/`, `/checkout.html`, `/uploads/receipts/`).
   - Block query parameter junk (`/*?*sort*`, `/*?*q=*`).
   - Declare both dynamic `https://voidclubs.ir/sitemap.php` and static `https://voidclubs.ir/sitemap.xml`.

5. **IndexNow Instant Protocol (Bing, Yandex, Seznam, Naver)**:
   - Key verification file placed on docroot: `https://voidclubs.ir/<key>.txt` containing `<key>`.
   - Example key: `c032646d2f344bb19bc41235183dbf9b`.
   - Batch submit URLs via POST to `https://api.indexnow.org/indexnow`:
     ```json
     {
       "host": "voidclubs.ir",
       "key": "c032646d2f344bb19bc41235183dbf9b",
       "keyLocation": "https://voidclubs.ir/c032646d2f344bb19bc41235183dbf9b.txt",
       "urlList": ["https://voidclubs.ir/", "https://voidclubs.ir/shop.html", ...]
     }
     ```
   - HTTP 202 confirms receipt and instant crawler queuing across Bing, Yandex, and partners.

## Verification Pattern

Verify with Python urllib + Mozilla UA (bypasses WAF blocks):
```python
import urllib.request, xml.etree.ElementTree as ET

opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
for u in ['https://voidclubs.ir/robots.txt', 'https://voidclubs.ir/sitemap.php']:
    req = urllib.request.Request(u, headers={'User-Agent': 'Mozilla/5.0'})
    body = opener.open(req, timeout=20).read()
    print(u, len(body))

# Test product pre-render headers & OpenGraph
req_prod = urllib.request.Request('https://voidclubs.ir/product.html?id=120', headers={'User-Agent': 'Mozilla/5.0'})
html = opener.open(req_prod, timeout=20).read().decode('utf-8')
assert 'og:image' in html
assert 'schema.org' in html
```
