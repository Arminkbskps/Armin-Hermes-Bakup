# Clean URLs Migration Pattern for Static/PHP cPanel Sites

Use when migrating a static HTML or hybrid PHP/HTML website from `.html` extensions (e.g. `/shop.html`, `/product.html?id=120`) to clean extensionless URLs (e.g. `/shop`, `/product?id=120`) without breaking navigation, JavaScript routing, SEO equity, or causing Apache infinite redirect loops.

---

## 1. Apache `.htaccess` — The Core Engine

### Pitfall: Infinite Redirect Loops
A naive rewrite like:
```apache
RewriteRule ^(.*)\.html$ /$1 [R=301,L]
RewriteRule ^([^/]+)$ $1.html [L]
```
causes Apache to loop indefinitely because the internal rewrite to `$1.html` re-triggers the first rule on the next pass, resulting in `500 Internal Server Error` (`Request exceeded the limit of 10 internal redirects`).

### Solution: Inspect `%{THE_REQUEST}`
`%{THE_REQUEST}` contains the raw, untransformed HTTP line sent by the browser (e.g. `GET /shop.html HTTP/1.1`). Internal rewrites do NOT change `%{THE_REQUEST}`.

```apache
# 1. 301 Redirect direct browser requests ending in .html to clean URLs
RewriteCond %{THE_REQUEST} ^[A-Z]{3,9}\ /([^\ ?#]+)\.html(?:[?][^\ ]*)?\ HTTP/ [NC]
RewriteCond %1 !^index$ [NC]
RewriteRule ^ /%1 [R=301,L]

# 2. Strip trailing slashes on non-directories (e.g. /shop/ -> /shop)
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{THE_REQUEST} \s/+([^\s?#]+)/+[?\s]
RewriteRule ^(.+)/$ /$1 [R=301,L]

# 3. Dynamic PHP Pre-renderers (if any)
RewriteRule ^product$ product.php [QSA,L]
RewriteRule ^categories$ categories.php [QSA,L]

# 4. Clean URLs internal rewrite: explicit whitelist (safest on shared hosting)
RewriteRule ^(shop|about|guide|account|login|checkout|payment-callback)$ $1.html [L]

# 5. Fallback clean URLs internal rewrite for any other .html page
RewriteCond %{REQUEST_FILENAME} !-f
RewriteCond %{REQUEST_FILENAME} !-d
RewriteCond %{REQUEST_FILENAME}.html -f
RewriteRule ^([^/]+)$ $1.html [L]
```

---

## 2. Client-Side JavaScript Router (`app.js`)

When visiting `/shop`, `window.location.pathname` is `/shop` (does not contain `shop.html`). If your router checks `if (path.includes('shop.html'))`, the page will fail to initialize.

### Robust Path Normalization Pattern
```javascript
function initRouter() {
  const rawPath = (window.location.pathname || '').toLowerCase();
  const page = rawPath.replace(/^\/+|\/+$/g, '').replace(/\.html$/, '');

  if (page === 'product' || page.startsWith('product/')) {
    initProductDetailPage();
  } else if (page === 'shop' || page.startsWith('shop/')) {
    initShopPage();
  } else if (page === 'categories' || page.startsWith('categories/')) {
    initCategoriesPage();
  } else if (page === 'checkout' || page.startsWith('checkout/')) {
    initCheckoutPage();
  } else if (page === 'account' || page.startsWith('account/')) {
    initAccountPage();
  } else if (page === 'about' || page.startsWith('about/')) {
    initAboutPage();
  } else if (page === '' || page === 'index') {
    initHomePage();
  }
}
```
This handles `/shop`, `/shop.html`, `/shop/`, and bare root seamlessly.

### Attribute Selector Guard
Audit selectors that match on `.html`:
```javascript
// BEFORE (breaks on clean URLs):
document.querySelectorAll('.mobile-bar-item[href*="account.html"]');

// AFTER (works with both):
document.querySelectorAll('.mobile-bar-item[href*="account"]');
```

---

## 3. Dynamic Server Pre-renderers & SEO

### Dynamic Canonical Tags (`product.php`, `categories.php`)
```php
// BEFORE:
$canonicalUrl = 'https://example.com/product.html' . ($id > 0 ? ('?id=' . $id) : '');

// AFTER:
$canonicalUrl = 'https://example.com/product' . ($id > 0 ? ('?id=' . $id) : '');
```

### Structured Data (JSON-LD Breadcrumbs)
Update all breadcrumb items from `https://example.com/shop.html` to `https://example.com/shop`.

### Sitemaps (`sitemap.php` & `sitemap.xml`)
Ensure both dynamic and static sitemaps emit clean URLs:
- `/shop`
- `/categories`
- `/about`
- `/guide`
- `/product?id=X`
- `/categories?category=Y`

### `robots.txt` Disallows
Disallow both clean and legacy paths to ensure crawlers never index private pages under either format:
```robots
Disallow: /account
Disallow: /account.html
Disallow: /checkout
Disallow: /checkout.html
Disallow: /login
Disallow: /login.html
Disallow: /payment-callback
Disallow: /payment-callback.html
```

---

## 4. Verification Checklist

1. `curl -I https://example.com/shop.html` ➔ Must return `301 Moved Permanently` to `/shop`.
2. `curl -I https://example.com/shop` ➔ Must return `200 OK` (no redirect, content served).
3. `curl -I https://example.com/product.html?id=120` ➔ Must return `301 Moved Permanently` to `/product?id=120`.
4. `curl -I https://example.com/product?id=120` ➔ Must return `200 OK` with dynamic metadata in `<head>`.
5. Check browser DevTools console for 0 404s on relative CSS/JS assets (verify `<base>` or trailing slash removal rule).
6. Verify no visual layout or CSS differences.
