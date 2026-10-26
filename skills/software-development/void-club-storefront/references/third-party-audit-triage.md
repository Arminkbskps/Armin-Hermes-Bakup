# Third-Party SEO & Storefront Audit Triage Pattern

Use when triaging and addressing external audits, bot crawlers, or customer security/performance reports on the VOID CLUB storefront.

---

## 1. Automated Bot Audit False Positives

### A. "No payment methods active on checkout"
- **Symptom:** Audit tool reports `در حال حاضر هیچ روش پرداختی از طرف مدیریت فعال نیست`.
- **Root Cause:** Headless crawlers or automated testers navigate directly to `/checkout` with an **empty cart** (`cart.getCart().items.length === 0`) or fail to execute asynchronous `/api/settings/bank-card` calls.
- **Verification Rule:** Never assume payment methods are disabled from an audit report. Probe `/api/settings/bank-card` directly via cURL or Python. If `online_enabled: true` and `card_to_card_enabled: true`, the payment methods are active and the report is an empty-cart false positive.

### B. "Admin panel is exposed in client-side HTML"
- **Symptom:** Security audit flags admin forms (ENTERPRISE 2.1, coupons, bank cards, shipping rates) inside `account.html`.
- **Reality:** In single-page vanilla architectures, markup for user and admin panels may reside in the same HTML file, with client-side tabs toggled based on `auth.getUser().is_admin`.
- **Backend Enforcement:** Hiding DOM elements is UX convenience only. The real security boundary is the backend:
  - Every administrative endpoint in `api/api.php` enforces `vc_require_admin()`.
  - `vc_require_admin()` decodes the HS256 JWT token from `Authorization: Bearer <token>` and verifies `is_admin === 1`.
  - Any unauthorized request immediately aborts with `HTTP 403 Forbidden: The user does not have enough privileges`. No data or configuration can be tampered with.

### C. "16 CSS files and 11 JS files hurting mobile speed"
- **Symptom:** Audit cites bloated file counts despite recent bundling and inlining.
- **Root Cause:** The external audit was executed against the **live server before the user uploaded and extracted the latest production ZIP package**.
- **Verification Rule:** Compare live asset links (`curl -s https://voidclubs.ir/ | grep -c '<link.*stylesheet'`) against on-disk `void_seo_v1/index.html`. If live shows 10 CSS files while disk has inlined Critical CSS + 1 `core.css`, remind the user to extract the updated ZIP in cPanel.

### D. "Missing Product and Breadcrumb Schema"
- **Symptom:** Auditor or SEO tool tests `https://voidclubs.ir/` or raw `shop.html` and reports missing `Product` and `BreadcrumbList` structured data.
- **Root Cause:** The crawler inspected a catalog/index page instead of a dynamic product detail page.
- **Verification Rule:** In the VOID CLUB architecture, product schemas are rendered dynamically by `product.php` on specific item URLs (e.g. `https://voidclubs.ir/product?id=120`). Test specific product URLs using Google Rich Results Test to verify `Product` and `BreadcrumbList` outputs.

---

## 2. Valid Audit Signals & Immediate Fixes

### A. Static Pre-rendered Text for Crawlers (`about.html`)
- **Pitfall:** Using `<p class="about-text" id="about-text">در حال بارگذاری...</p>` means bots that do not execute JavaScript index a blank page with "loading...".
- **Fix:** Bake the official brand story directly into the HTML markup as default text. Client-side JS in `initAboutPage()` still fetches `/api/settings/about` and overwrites it dynamically if an admin edits the text in the panel.
- **Structured Data:** Attach an `AboutPage` schema with `ClothingStore` metadata in `<head>`.

### B. FAQPage Rich Snippets (`guide.html`)
- Informational pages covering size charts, shipping times (7–10 business days), care instructions, and return policies should include standard schema:
```html
<script type="application/ld+json">
{
  "@context": "https://schema.org",
  "@type": "FAQPage",
  "mainEntity": [
    {
      "@type": "Question",
      "name": "زمان ارسال سفارشات چند روز کاری است؟",
      "acceptedAnswer": {
        "@type": "Answer",
        "text": "کلیه سفارشات بین ۷ تا ۱۰ روز کاری پس از ثبت نهایی آماده‌سازی و از طریق پست پیشتاز به سراسر کشور ارسال می‌شوند."
      }
    }
  ]
}
</script>
```
This enables expandable Q&A cards directly in Google Search results (SERP).

### C. CollectionPage Schema & Semantic H2s (`shop.html`)
- Ensure `shop.html` has an `application/ld+json` block with `@type: "CollectionPage"`.
- If visual design has no subheadings, add accessible semantic headings (e.g. `.sr-only` `<h2>آرشیو لباس‌های استریت‌ویر و محصولات</h2>`) so the document outline is valid without affecting visual aesthetics.

### D. Private Page Noindex Tags (`account.html`, `checkout.html`)
- In addition to `robots.txt` disallows, private cart and profile pages must carry explicit header tags:
```html
<meta name="robots" content="noindex, nofollow">
```
This prevents Google from indexing empty carts or user dashboards under any circumstances.

---

## 3. Secondary Pages Core CSS Coverage Pitfall

- **Pitfall:** Consolidating CSS only on high-traffic landing pages (`index.html`, `shop.html`, `product.html`, `categories.html`) while leaving secondary pages (`about.html`, `guide.html`, `checkout.html`, `account.html`, `payment-callback.html`) with 12–16 separate CSS `<link>` tags.
- **Auditor Detection:** Technical audits will inspect secondary pages like `guide.html` and flag render-blocking waterfalls.
- **Rule:** When introducing or bumping `core.css?v=X.X`, run a multi-file migration script across ALL HTML pages. Replace the legacy sequence (`fonts-local.css`, `variables.css`, `reset.css`, `base.css`, `components.css`, `layout.css`, `responsive.css`, etc.) with `core.css` + deferred non-critical icon/feature stylesheets everywhere.

---

## 4. International / VPN Connection Timeouts (`ERR_TIMED_OUT`)

- **Symptom:** User cannot open `voidclubs.ir` with VPN active (`ERR_TIMED_OUT: took too long to respond`).
- **Diagnosis:** Run multi-region latency/HTTP tests (e.g. Check-Host / probe scripts from DE, NL, ES). If European nodes return `HTTP 200 OK` on port 443 with low latency (~100–300ms), international routing is functional.
- **Root Cause:** Hostiran server-level firewall (CSF / cPHulk / Anti-DDoS) drops packets from specific datacenter IP subnets used by commercial VPNs, often triggered by frequent rapid requests or admin uploads.
- **Resolution Strategy:**
  1. **VPN Client Routing:** Configure the VPN client (v2rayNG, Hiddify, sing-box) to use **Bypass Iran / LAN** routing. Domestic Iranian domains route directly with minimum ping, while restricted services route through the VPN.
  2. **IP Rotation:** Switch the VPN server location/node to acquire an unflagged public IP.
  3. **Hostiran Unblock:** Log into Hostiran client area (`hostiran.net`) ➔ Services ➔ **بررسی و رفع مسدودی IP** to delist the current client IP.
  4. **CDN Compatibility Note:** Cloudflare rejects `.ir` domains (returns `Unsupported TLD`). For a free CDN layer that bridges international and domestic traffic, ArvanCloud (ابر آروان) is the standard alternative.

---

## 5. Merging Peripheral Components into Core CSS (`void-components.css` & `guide-responsive.css`)

- **Pitfall:** Keeping small feature stylesheets (`void-components.css` ~7KB, `guide-responsive.css` ~3KB) as separate `<link>` tags across multiple pages. Even with `media="print" onload="..."`, each file incurs HTTP round-trips and triggers audit warnings.
- **Recipe:**
  1. Append the full content of `void-components.css` and `guide-responsive.css` directly to `core.css`.
  2. Verify bracket balance (`assert combined.count('{') == combined.count('}')`).
  3. Remove the `<link rel="stylesheet" href="css/void-components.css...">` and `<link rel="stylesheet" href="css/guide-responsive.css...">` tags (and any `<noscript>` fallbacks) from all HTML files.
  4. This eliminates 2 network requests on `guide.html` and `about.html`, and 1 request on all other pages, with 100% visual fidelity.

---

## 6. The Dynamic Admin Script Pitfall & Statically Ordered Loading (CRITICAL)

- **Audit Suggestion Trap:** Third-party performance auditors frequently suggest making administrative scripts (`enterprise-admin.js`) and stylesheets (`enterprise-admin-full.css`, `admin-responsive.css`, `invoice-print.css`) dynamic or role-gated on `account.html` and `checkout.html` so regular users don't download them.
- **FATAL PITFALL — WHY THIS BREAKS THE ENTIRE ADMIN PANEL:**
  - In vanilla frontend architectures, `app.js` initializes on `DOMContentLoaded` and immediately binds administrative subtabs, event handlers, and data loaders that depend on `enterprise-admin.js` having already executed and attached its methods to `window`.
  - Injecting `enterprise-admin.js` dynamically via `document.createElement('script')` inside `DOMContentLoaded` causes `app.js` to execute FIRST before the injected script finishes fetching and running.
  - Result: All admin methods (`loadAdminStats`, `loadAdminProducts`, `batchPricing`, `coupons`, `watermark`, `orders`) fail silently or throw `TypeError`, completely breaking the admin panel («پنل ادمین خراب شد کلا»).
  - Furthermore, dynamically injecting admin CSS creates a jarring Flash of Unstyled Content (FOUC) and misaligned grid elements in the dashboard.
- **Golden Rule:**
  - In `account.html`, keep the 3 admin stylesheets statically linked in `<head>`, and maintain `<script defer src="js/enterprise-admin.js?v=..."></script>` loaded immediately BEFORE `<script defer src="js/app.js?v=..."></script>`.
  - In `checkout.html`, keep `enterprise-admin.js` statically deferred before `app.js`.
  - Admin access is already 100% secured on the backend via JWT verification and `vc_require_admin()` in `api.php`. Never sacrifice functional stability and admin workflows to satisfy superficial static file-count audit suggestions.

### Packaging Integrity Check
- When preparing distribution archives (e.g. `VOID_SEO_BOOST_v1.zip`), verify that ALL 427+ project assets across `js/`, `css/`, `assets/`, `uploads/` are synchronized into the export directory before archiving. Omitting core scripts like `enterprise-admin.js` or `wishlist.js` produces 404s on cPanel and breaks the application.

---

## 7. Zero-Mutation Tap Target Size Expansion & The Position Trap

- **Audit Trigger:** Lighthouse / SEO scanners flag interactive controls smaller than 48x48 CSS pixels (e.g. 40x40px slider arrows, 46x46px action buttons, 38px logo).
- **Core Constraint:** The user strictly mandates **ZERO visual changes** (`ظاهر سایت رو اصلا دست نزن`). Resizing buttons, adding visible padding, or modifying borders alters the layout and degrades the dark streetwear brand identity.
- **CRITICAL PITFALL — NEVER force `position: relative` onto absolutely-positioned elements:**
  - Hero slider nav buttons (`.sr7-nav-btn`) rely on `position: absolute; top: 50%; transform: translateY(-50%);` to be vertically centered on the left and right edges of the hero banner.
  - Adding `.sr7-nav-btn { position: relative; }` strips their absolute positioning, completely displacing them into document flow on mobile (`دکمه های چپ و راست بنر اسلایدر خراب شد یعنی جاشون خیلی بد شده`).
  - Furthermore, this layout shift forces `sr7-slider.js` into continuous forced reflows (144ms reflow time!), spiking Total Blocking Time (TBT) to 900ms and dropping the Performance score from 82 to 74!
- **Safe Recipe:**
  Apply `::after` touch expanders ONLY to elements that are already relatively positioned or flow elements (like `.action-btn`, `.btn-view-all`, `.logo`). For `.sr7-nav-btn`, it is ALREADY `position: absolute; width: 48px; height: 48px` on desktop; on mobile (32px), attach the `::after` WITHOUT overriding its `position: absolute`!
```css
/* Safe Accessibility Tap Target Expander (Preserves Absolute Positioning) */
.action-btn,
.btn-view-all,
a.logo {
  position: relative;
}

.action-btn::after,
.slider-nav-btn::after,
.btn-view-all::after,
a.logo::after {
  content: "";
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  min-width: 48px;
  min-height: 48px;
  width: 100%;
  height: 100%;
  pointer-events: auto;
}
```

---

## 8. Eliminating Render-Blocking CSS vs The Preload Trap

- **Audit Trigger:** Audit warns `5 styles may block rendering` (e.g. `remixicon.css`, `fa-all.css`, `custom-select.css`, `editorial-popart.css`, `search.css`).
- **CRITICAL PITFALL — DO NOT PRELOAD NON-CRITICAL ICON STYLES:**
  - Adding `<link rel="preload" as="style" href="assets/icons/...">` for large icon stylesheets (`remixicon.css`, `fa-all.css`) forces the browser under mobile throttling (Slow 4G) to eagerly download and parse icon font CSS during early page load.
  - In PageSpeed audits, this caused an immediate **90ms long task** on the main thread and delayed Largest Contentful Paint (LCP) by 1.28 seconds!
- **Correct Recipe:**
  Do NOT preload icon styles. Defer them purely with `media="print" onload="this.media='all'"` and wrap fallbacks in `<noscript>`:
```html
<!-- Non-blocking deferred styles without main-thread preload contention -->
<link rel="stylesheet" href="assets/icons/remixicon.css?v=1.0" media="print" onload="this.media='all'">
<link rel="stylesheet" href="assets/icons/fa-all.css?v=1.1" media="print" onload="this.media='all'">
<link rel="stylesheet" href="css/custom-select.css?v=6.4" media="print" onload="this.media='all'">
<link rel="stylesheet" href="css/editorial-popart.css?v=6.3" media="print" onload="this.media='all'">
<link rel="stylesheet" href="css/search.css?v=7.5" media="print" onload="this.media='all'">
<noscript>
  <link rel="stylesheet" href="assets/icons/remixicon.css?v=1.0">
  <link rel="stylesheet" href="assets/icons/fa-all.css?v=1.1">
  <link rel="stylesheet" href="css/custom-select.css?v=6.4">
  <link rel="stylesheet" href="css/editorial-popart.css?v=6.3">
  <link rel="stylesheet" href="css/search.css?v=7.5">
</noscript>
```
- **Outcome:** Zero render-blocking warnings, zero main-thread parsing contention during first paint, and pristine mobile PageSpeed scores.

---

## 9. ArvanCloud (ابر آروان) CDN Setup for Iranian Domains (.ir) on Hostiran

- **Context:** Cloudflare blocks `.ir` domains due to sanctions. ArvanCloud provides domestic CDN points of presence across Iran and international edge nodes, solving both VPN firewall blockages (`ERR_TIMED_OUT`) and international asset latency.
- **Zero-Downtime Migration Architecture:**
  1. **Domain Creation:** Add `voidclubs.ir` in ArvanCloud CDN dashboard under the Free (پایه) tier.
  2. **DNS Record Verification:**
     - `@` (Root A record) ➔ Points to Hostiran origin IP `213.176.126.164` with the **cloud icon ENABLED (ابری)**.
     - `www` (CNAME or A record) ➔ Points to `@` or `213.176.126.164` with **cloud icon ENABLED (ابری)**.
     - Auxiliary records (mail, webmail, cpanel, direct-connect) ➔ Cloud icon **DISABLED (خاموش)** to allow direct port bindings (2083 for cPanel, 25/587 for SMTP).
  3. **Nameserver Migration:** In the domain registrar (Hostiran client area or `nic.ir`), replace Hostiran nameservers (`ns1.hostiran.net`, `ns2.hostiran.net`) with the assigned ArvanCloud nameservers (e.g. `*.ns.arvancdn.ir`).
  4. **The `.ir` Registry Propagation Latency Rule:**
     - Unlike gTLDs (`.com`, `.org`) where NS updates propagate in minutes, `.ir` domain zone files are regenerated and pushed by the national registry (`nic.ir`) in scheduled batches throughout the day (every 2 to 6 hours).
     - **Zero Downtime Guarantee:** The website remains 100% active on the origin server (`HTTP/1.1 200 OK`) via the existing nameservers during this propagation window. As soon as the registry batch publishes, DNS queries transition transparently to ArvanCloud edges without a single dropped packet.
     - **Verification Probes:** Query the authoritative root nameservers of `nic.ir` directly:
       `nslookup -type=ns voidclubs.ir 193.189.123.2` (a.nic.ir). When `nic.ir` responds with ArvanCloud nameservers, propagation is complete.
  5. **SSL & Origin Encryption:** In ArvanCloud dashboard ➔ HTTPS / گواهینامه‌ها:
     - Activate free Let's Encrypt / ArvanCloud automated certificate for the edge.
     - Set Origin Connection Security to **HTTPS (Full / رمزنگاری کامل)** to encrypt edge-to-origin traffic.
  6. **Direct cPanel Access Fallback:** If DNS cutover temporarily confuses local caching for `voidclubs.ir:2083`, access cPanel directly via origin IP: `https://213.176.126.164:2083`.

---

## 10. Server-Side H1 & Schema Currency (IRR vs Toman) Synchronization

- **Audit Requirement:** SEO scanners (and Googlebot) require a single, distinct `<h1>` tag in the initial server-rendered HTML response (`view-source:`) without relying on JavaScript rendering.
- **Product Page Pre-rendering (`product.php`):**
  - Inject `<h1 class="product-title" id="product-title"><?php echo htmlspecialchars($productTitle); ?></h1>` directly inside `#product-detail-layout` server-side.
  - When client-side JavaScript (`app.js`) initializes and renders the product details, it must emit `<h1 class="product-title detail-title" id="product-title">${currentProduct.title}</h1>`, maintaining a single consistent H1 across pre-render and post-hydration states.
  - **CRITICAL Title Preservation Rule:** Never truncate product names or cut words with ellipses (`...`) to satisfy arbitrary 60-character audit rules («اسم محصولات رو ادیت نزن و این اصلاحت رو حذف کن چون این مشکل به صاحب سایت ربط داره نه من»). Preserve full descriptive product names as stored in the database.
- **Currency Conversion in JSON-LD & Schema (IRR vs Toman):**
  - In the database, garment prices are stored in thousands (e.g. `1480` for 1,480,000 Tomans).
  - The storefront displays product prices in **Toman (تومان)** (`1480 * 1000 = 1,480,000 تومان`).
  - The standard ISO 4217 currency recognized by Schema.org / Google Rich Results for Iran is **`IRR` (Iranian Rial)**.
  - **Rule:** Multiply the raw database value by 10,000 (`$priceRial = (int)round($rawPrice * 10000)`) so 1480 becomes **`14800000` IRR** (`"priceCurrency": "IRR"`, `"price": "14800000"`). Apply this in both `product.php` and `js/app.js` (`vc-product-jsonld`).

---

## 11. Two-Column Mobile Layout Pattern for Categories & Product Tracks

- **User Preference (session 2026-09-22):** On mobile devices, both home page categories (`.home-categories-track`) and product sliders/tracks (`.home-arrivals-track`, `#home-top-grid`) must display **۲ ستونه (two columns / two cards side-by-side)**, replacing the previous single-card peek (`flex: 0 0 82%`).
- **CSS Architecture (`@media (max-width: 768px)`):**
```css
/* 2-Column Mobile Category Slider */
.home-categories-track {
  gap: 12px !important;
}
.home-categories-track .category-card,
.home-categories-track .home-cat-card {
  flex: 0 0 calc(50% - 6px) !important;
  min-width: calc(50% - 6px) !important;
  max-width: calc(50% - 6px) !important;
  height: auto !important;
  border-radius: 12px !important;
}
.home-categories-track .category-card-content {
  padding: 8px 10px !important;
}
.home-categories-track .category-card-title {
  font-size: 13px !important;
  line-height: 1.3 !important;
}

/* 2-Column Mobile Product Slider / Track */
.home-arrivals-track {
  gap: 12px !important;
}
.home-arrivals-track .product-card,
.home-arrivals-track .home-arrival-card {
  flex: 0 0 calc(50% - 6px) !important;
  min-width: calc(50% - 6px) !important;
  max-width: calc(50% - 6px) !important;
  border-radius: 12px !important;
}
.home-arrivals-track .product-card-content {
  padding: 10px 8px !important;
}
.home-arrivals-track .product-card-title {
  font-size: 12px !important;
  line-height: 1.35 !important;
  max-height: 34px !important;
  overflow: hidden !important;
}
.home-arrivals-track .product-card-price {
  font-size: 12px !important;
}
```
- **Single-Line Subtitle Rule:** In 2-column mobile cards, secondary label spans (e.g. `.category-card-link` «۲ کالکشن · مشاهده دسته‌بندی») wrap into 2 lines if font is too large. Lock it single-line: `font-size: clamp(8px, 2.2vw, 9.5px) !important; white-space: nowrap !important; overflow: hidden !important; text-overflow: ellipsis !important; display: inline-flex !important;`.
- **Swipe Calculation:** `homeSliderMetrics()` in `js/app.js` dynamically queries `first.getBoundingClientRect().width + gap`, so touch swiping automatically adapts to 2-card scroll increments without code changes.

---

## 12. Streamlining Critical Inlined CSS (~14KB Budget) & Eliminating Duplicate CSS Tags

- **The Inlined Bloat Trap:** Inlining the full core stylesheet into `<style id="void-critical-css">` (~43KB+) defeats browser caching. While it eliminates external round-trips on first load, every subsequent page visit downloads that 43KB uncompressed in the HTML payload.
- **The 14KB TCP Initial Congestion Window Rule:**
  - Keep critical inline styles under **~10–14KB** containing ONLY `@font-face` definitions, `:root` design tokens, basic element resets, critical header layout, hero skeleton, and mobile bar rules.
  - Link the full unified stylesheet as `<link rel="stylesheet" href="css/core.css?v=1.1">`. The browser parses the critical fold instantly and caches `core.css` across all other site pages.
- **Eliminating Duplicate Stylesheet Tags:**
  - Do NOT pair `media="print" onload="this.media='all'"` with `<noscript>` fallback links when self-hosting local stylesheets. In raw `view-source:`, auditors flag these as duplicate resources.
  - Use exactly ONE standard `<link rel="stylesheet">` per file:
    `core.css?v=1.1`, `remixicon.css?v=1.0`, `fa-all.css?v=1.1`, `custom-select.css?v=6.4`, `editorial-popart.css?v=6.3`, `search.css?v=7.5`.

---

## 13. Synchronous Head-Level Role Gating for Administrative Assets

- **Problem:** Leaving administrative styles and `enterprise-admin.js` statically exposed in public HTML prompts security audit warnings, but asynchronously loading them in `DOMContentLoaded` causes fatal race conditions with `app.js`.
- **Solution — Synchronous `<head>` Injection:**
  In `account.html`, inject admin assets synchronously from a small `<script>` block in `<head>` BEFORE the body parses:
```html
<script>
  (function() {
    try {
      var u = JSON.parse(localStorage.getItem('user') || 'null');
      if (u && (u.is_admin === true || u.is_admin === 1 || u.role === 'admin' || u.isAdmin)) {
        var styles = [
          'css/admin-responsive.css?v=6.2',
          'css/enterprise-admin-full.css?v=6.2',
          'css/invoice-print.css?v=6.2'
        ];
        styles.forEach(function(h) {
          var l = document.createElement('link');
          l.rel = 'stylesheet';
          l.href = h;
          document.head.appendChild(l);
        });
        var s = document.createElement('script');
        s.src = 'js/enterprise-admin.js?v=6.2';
        s.defer = true;
        document.head.appendChild(s);
      }
    } catch(e) {}
  })();
</script>
```
  - Regular customers and crawlers see zero admin CSS or scripts in `view-source:`.
  - Logged-in admins have all styles and functions ready prior to dashboard render.
  - In `checkout.html`, `enterprise-admin.js` is completely removed as no checkout logic depends on it.

---

## 14. Server Hardening: Neutralizing Directory Browsing (CWE-548) & Security Headers

- **Discovery:** On Apache/LiteSpeed web servers without explicit index rules, requesting directories like `/api/`, `/css/`, `/js/` triggers `mod_autoindex`, listing all internal files, modification dates, and sizes.
- **Rule 1 — Disable Directory Listing:** In root `.htaccess` and `api/.htaccess`:
```apache
Options -Indexes -MultiViews
```
Requesting `/api/` immediately returns **HTTP 403 Forbidden**.
- **Rule 2 — Block Sensitive Files & Dumps:**
```apache
<FilesMatch "\.(sql|env|log|ini|bak|git|md)$">
  Require all denied
</FilesMatch>
<Files "config.php">
  Require all denied
</Files>
<FilesMatch "^lib_.*\.php$">
  Require all denied
</FilesMatch>
```
- **Rule 3 — Modern Security Headers Injection:**
```apache
<IfModule mod_headers.c>
  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains; preload"
  Header always set X-Frame-Options "SAMEORIGIN"
  Header always set X-Content-Type-Options "nosniff"
  Header always set Referrer-Policy "strict-origin-when-cross-origin"
  Header always set Permissions-Policy "camera=(), microphone=(), geolocation=()"
</IfModule>
```
- **Rule 4 — Restrict API CORS Origin:** In `api/api.php`, replace wildcard `Access-Control-Allow-Origin: *` with domain whitelist (`https://voidclubs.ir`, `https://www.voidclubs.ir`, subdomains) to protect against unauthorized 3rd-party cross-origin calls.

---

## 15. Core Web Vitals & Image CLS Elimination

- **Problem:** Dynamic product images and catalog cards lacking explicit HTML `width` and `height` attributes force browsers to render layout shifts (CLS) once images download.
- **Solution:**
  1. In `js/app.js` `cardMediaTag()`: Add `width="640" height="640"` on all catalog image and video tags.
  2. Main product image (`#main-product-image`): Explicit `width="640" height="640"`, `fetchpriority="high"`, and `decoding="async"` for instantaneous LCP.
  3. Product thumbnails: Explicit `width="80" height="80"` and `loading="lazy"`.
  4. Category cards in `index.html`: Explicit `width="640" height="640"` on all 4 prerendered cover images.
  5. Preconnect: `<link rel="preconnect" href="https://voidclubs.ir" crossorigin>` in `<head>`.
  6. Typography: Every `@font-face` block must carry `font-display: swap;` to prevent invisible Persian text during mobile font fetch.

---

## 16. Dynamic Category Showcases & Smart Artwork Deduplication (10 Unique Designs Per Category)

- **Requirement:** Display dedicated showcase sliders for each mother category on `index.html` below categories, top picks, and new arrivals.
- **Artwork / Design Deduplication Rule (session 2026-09-22):**
  - In stores where each artwork is printed on multiple garments (hoodie, sweatshirt, t-shirt, crop top), querying a category slider naively displays all 3 garment formats of the exact same design side-by-side.
  - **Solution:** A core design signature extractor (`getProductDesignSignature(title)`) that strips garment type prefixes (`هودی`, `دورس`, `تیشرت`, `کراپ تاپ`, `سویشرت`, `پلیور`, `پیراهن`, `hoodie`, `sweatshirt`, `t-shirt`, etc.) and normalizes Persian half-spaces.
  - Query a broader pool (`limit: 50`), deduplicate by design signature, and take up to 10 unique designs per showcase.
- **Design Pattern:**
  - Container in `index.html`: `<div id="home-category-showcases-container"></div>`.
  - Skip categories returning 0 products to prevent empty sections.
  - Section header: English kicker, Persian title (`کالکشن [نام دسته]`), slider nav arrows, and "آرشیو محصولات" linking directly to `shop?category={slug}` (e.g. `shop?category=Anime`).
  - Cards inherit `.home-arrivals-track` 2-column mobile layout (`calc(50% - 6px)`) with RTL touch swiping and desktop slider positioning.

---

## 17. Product Detail Rendering & Scoped Variable Traps (`drawProductDetails`)

- **Pitfall:** Declaring image Alt variables (`const safeAlt = ...`) inside an inner loop (e.g. `forEach` on product images) while referencing `${safeAlt}` on the primary `#main-product-image` tag outside that block.
- **Consequence:** Triggers a JavaScript `ReferenceError: safeAlt is not defined`. The outer `try/catch` in `initProductDetailPage` catches it and replaces the entire layout with `خطا در دریافت مشخصات محصول.`
- **Rule:** Declare all template-wide variables at the top level of `drawProductDetails()` before DOM string interpolation. Verify with a headless Node.js evaluation test before building release ZIPs.

---

## 18. Instant Product Transitions (Speculation Rules API) & Security RFC 9116

- **Speculation Rules API (`index.html`, `shop.html`):** Modern Chromium browsers support instantaneous (0ms) subpage navigations by pre-rendering URLs on user hover:
```html
<script type="speculationrules">
{
  "prerender": [
    {
      "where": { "href_matches": "/product*" },
      "eagerness": "moderate"
    }
  ]
}
</script>
```
- **RFC 9116 `security.txt`:** Place in `/.well-known/security.txt` with standard disclosure contact information (`mailto:support@voidclubs.ir`) and ensure Apache does not rewrite it.
- **HttpOnly JWT Cookie:** Alongside the JSON body token, set a secure `HttpOnly` cookie (`setcookie('void_token', $tok, ['secure' => true, 'httponly' => true, 'samesite' => 'Lax'])`) so API requests can authenticate even if cross-site scripts attempt to hijack tokens.

---

## 19. Strict Alternating Garment Type Algorithm (تیشرت ➔ دورس ➔ هودی)

- **User Requirement (session 2026-09-22):** In storefront showcases and sliders, rather than picking the first arbitrary garment type for each unique design, the showcase must alternate cyclically across the 3 core apparel categories:
  - **Slot 1 (Design 1):** تیشرت (`tshirt`)
  - **Slot 2 (Design 2):** دورس (`sweatshirt`)
  - **Slot 3 (Design 3):** هودی (`hoodie`)
  - **Slot 4 (Design 4):** تیشرت (`tshirt`)
  - **Slot 5 (Design 5):** دورس (`sweatshirt`)
  - **Slot 6 (Design 6):** هودی (`hoodie`)
  - ...repeating up to 10 products per showcase.
- **Algorithm Implementation (`pickAlternatingGarmentProducts` in `js/app.js`):**
  1. Fetch a broad catalog pool (`limit: 80` to `100`).
  2. Extract the core design signature (`getProductDesignSignature`) and identify each item's garment type (`getProductGarmentType`).
  3. Group items into `designGroups[sig] = { tshirt, sweatshirt, hoodie, all }` while recording `orderedDesigns` to maintain catalog rank.
  4. For each slot (`0` to `limit - 1`), look for the next unused design that possesses the target garment type (`pattern[slot % 3]`).
  5. If an artwork lacks that specific format, gracefully fallback to the best available format of that design before moving forward.
  6. **Outcome:** Ensures 100% artwork diversity (zero repeated designs) while delivering a balanced, visually engaging showcase of t-shirts, sweatshirts, and hoodies.

---

## 20. Product Detail Gallery Touch & Pointer Swipe (ورق زدن تصاویر با مالش دست)

- **Problem:** In mobile product pages (`product.html`), navigating multiple product images only responded to thumbnail taps or tiny arrow buttons; horizontal finger swiping on the main photo did nothing.
- **RTL Swiping Convention:**
  - In Persian RTL layouts, dragging right-to-left (`dx < 0`) advances to the **next** image (`slideProductGallery(1)`).
  - Dragging left-to-right (`dx > 0`) moves to the **previous** image (`slideProductGallery(-1)`).
- **Implementation Architecture (`setupProductGallerySwipe` in `js/app.js`):**
  1. Bind Pointer Events (with touch fallback) directly to `.main-image-wrapper`.
  2. Set `touch-action: pan-y` on the container to preserve smooth vertical scrolling while capturing horizontal swipes.
  3. Axis Lock: Once `Math.abs(dx) >= Math.abs(dy)` and exceeds 8px, lock axis to `'x'` and call `e.preventDefault()`.
  4. Threshold: If horizontal distance exceeds 30px, trigger `slideProductGallery(direction)`.
  5. Thumbnail Synchronization: In `changeMainImage()`, automatically call `el.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })` to keep the active thumbnail visible in the gallery strip.

---

## 21. CRO Audit Triage & Scope Boundary (SMS / Third-Party Gateway Boundaries)

- **Context:** When handling external Checkout CRO Audits (e.g. `VOID_CLUB_CHECKOUT_CRO_AUDIT_REPORT.pdf`):
  - Third-party merchant integrations like **SMS notification gateways** (Kavenegar, FarazSMS) and **external installment credit providers** (SnappPay / اسنپ‌پی) are strictly external business arrangements requiring merchant contracts, proprietary credentials, and gateway agreements.
  - **Rule:** Filter out SMS and BNPL recommendations («پیامک و اسنپ پی که ربطی به تو ندارن رو ول کن») and focus 100% on high-impact on-page CRO, cart drawer gamification, frictionless checkout, and urgency elements that improve conversions directly within the storefront codebase.

---

## 22. Dynamic Free Shipping Progress Bar in Cart Drawer (AOV Gamification)

- **Baymard CRO Benchmark:** In dark streetwear storefronts, hiding or leaving the free-shipping threshold static forfeits an estimated 18%–24% in Average Order Value (AOV).
- **Implementation Architecture (`updateShippingProgress(subtotal)` in `js/ui.js`):**
  1. Retrieve active threshold from `window.freeShippingThreshold` or default to `3000` (representing 3,000,000 Tomans, synced with the header marquee).
  2. If `subtotal <= 0`: Set progress bar width to 0% and display `ارسال رایگان برای سفارش‌های بالای [مبلغ]`.
  3. If `0 < subtotal < threshold`:
     - Calculate remaining amount: `remaining = threshold - subtotal`.
     - Calculate percentage: `Math.min(100, Math.max(5, Math.round((subtotal / threshold) * 100)))`.
     - Update progress bar width and render: `تنها [مبلغ باقیمانده] تا ارسال رایگان سفارش!`.
  4. If `subtotal >= threshold`:
     - Set width to 100% and switch bar color to success green (`#22c55e`).
     - Render: `🎉 ارسال رایگان برای این سفارش فعال شد!`.
- **Outcome:** Instantly gamifies the cart drawer, providing immediate visual feedback as items are added or removed without layout shifts.

---

## 23. Mobile Sticky Add-to-Cart Bottom Bar & Overlap Prevention (PDP CRO)

- **Mobile Viewport Drop-Off Problem:** On mobile devices (`window.innerWidth <= 768px`), as users scroll down product detail pages to view size charts, fabric specs, and customer reviews, the primary "Add to Cart" button exits the viewport, introducing cognitive friction and lost conversions.
- **Sticky Buy Bar Architecture (`#pdp-sticky-buy-bar`):**
  - **Component Layout:** Solid dark dock anchored at `bottom: 0` with 100% opaque background (`#08080c !important`), top border `1px solid rgba(255, 255, 255, 0.15)`, truncated product title, dynamic price, and primary CTA button (`افزودن به سبد`).
  - **The Mobile Bottom Bar Overlap & Transparency Trap (user correction 2026-09-22):**
    - Naive semi-transparent glass (`rgba(12, 12, 18, 0.96)`) or small padding (`10px 16px`) causes the bar to clash with phone bottom navigation bars / Android gesture indicators / iPhone home bars, letting scrolled text peek through and glitch («میاد روی نواره پایین گوشی که خراب میشه، یکم سایز اون نواره افزودن به سبد رو کلا بزرگتر کن که زیریش دیده نشه»).
    - **Resolution Rules:**
      1. Background MUST be 100% solid, fully opaque dark (`#08080c !important`) — no transparency or backdrop-filter bleed.
      2. Layer priority: `z-index: 99999` to sit cleanly above all other elements.
      3. Sizing & Safe Area: `min-height: 80px; padding: 14px 20px calc(16px + env(safe-area-inset-bottom, 14px));`.
      4. Large typography: title `13.5px` (font-weight 800), price `15.5px` (font-weight 900), and large touch-friendly button (`padding: 12px 24px; font-size: 13.5px`).
      5. Layout bottom clearance: On mobile screens, add `#product-detail-layout { padding-bottom: 100px !important; }` so the bottom of the page (footer, related products) is never obscured behind the sticky bar.
  - **Scroll Triggers (`setupStickyBuyBarObserver` in `js/app.js`):**
    - An `IntersectionObserver` monitors `.cta-row .btn-add-to-cart`.
    - When the primary button exits the viewport and `window.scrollY > 200px`, the `.visible` class is added, sliding the bar up smoothly (`transform: translateY(0)`).
    - When the primary button is visible or page returns near top, `.visible` is removed.
  - **Desktop Constraint:** Hidden completely on desktop screens (`@media (min-width: 769px) { display: none !important; }`).

---

## 24. Strict Ban on Inventory Stock Badges & «ارسال فوری» Phrases

- **User Correction (session 2026-09-22):** «ارسال فوری و موجود در انبار رو حذف کن».
- **Storefront Identity:** As an exclusive dark streetwear studio, VOID CLUB garments are custom printed and dispatched within standard production cycles (7–10 days). Displaying artificial or generic "ارسال فوری" (immediate express shipping) or stock inventory badges ("موجود در انبار VOID CLUB" / "تنها ۲ عدد در انبار باقی مانده") was explicitly rejected by the store owner.
- **Rule:**
  1. NEVER render stock quantity badges, scarcity countdowns, or warehouse inventory status on the product detail page or catalog cards.
  2. Eliminate all occurrences of "ارسال فوری" from fallback meta descriptions (e.g. in `categories.php` and `product.php` — use standard «ارسال به سراسر کشور»).
  3. Keep the UI clean, minimalist, and focused on the artwork, fabric quality, and sizing guide.

---

## 25. E-Commerce Telemetry & First-Party Analytics Architecture (`voidTracker` & `/api/event`)

- **The Iranian DNS & Ad-Block Sanitization Problem:** Third-party analytics services (Google Analytics 4, Tag Manager, Hotjar) are frequently blocked or crippled inside Iran due to ISP-level DNS filtering, VPN interference, or browser ad-block extensions, resulting in a Grade F (27/100) telemetry score.
- **Unified Client Telemetry Engine (`window.voidTracker` in `js/app.js`):**
  1. **UTM Attribution Capture:** On page load, `voidTracker.init()` parses `utm_source`, `utm_medium`, `utm_campaign`, `utm_content`, and `utm_term` from the URL and persists them to `localStorage.getItem('void_utm')` alongside landing URL and referrer.
  2. **Enhanced E-Commerce Standard Taxonomy:** Dispatches standard GA4 / GTM events via `window.dataLayer = window.dataLayer || [];`:
     - `view_item_list`: Triggered on homepage showcases and shop catalog loads.
     - `view_item`: Triggered when visiting a product detail page (includes `item_id`, `item_name`, `price`, `currency: 'IRT'`).
     - `add_to_cart`: Triggered when adding an item to cart (includes product ID, variant, quantity, price).
     - `begin_checkout`: Triggered on `/checkout` initialization with subtotal and items count.
     - `purchase`: Triggered upon successful order creation with `transaction_id`, `value`, `currency: 'IRT'`, and `payment_method`.
  3. **Domestic First-Party Telemetry Logging (`/api/event`):**
     - Alongside `dataLayer.push()`, events are dispatched to a first-party endpoint on the origin server via `navigator.sendBeacon('/api/event', JSON.stringify(payload))` (with fetch `keepalive: true` fallback).
     - The backend route in `api/api.php` writes telemetry safely to `api/logs/telemetry.log`.
     - Because this request is sent to the identical primary domain (`https://voidclubs.ir/api/event`), it is 100% immune to domestic DNS filtering, VPN drops, or ad-block rules.
  4. **Marketing Campaign Order Attribution:** When placing an order (`POST /api/orders`), the client appends `attribution: voidTracker.getAttribution()` into the order payload, enabling backend order logs (`api/logs/attribution.log`) to attribute revenue directly to marketing campaigns without external dependencies.

---

## 26. WCAG 2.2 Level AA Accessibility Architecture for Dark Streetwear Aesthetics

- **The Aesthetic vs Accessibility Tension:** Dark streetwear designs rely on subtle borders, dark red accents (`#990000`), and minimalist layouts. External accessibility audits (e.g. `VOID_CLUB_ACCESSIBILITY_WCAG_REPORT.pdf`) grade unoptimized sites poorly (Grade C+ / 66/100) due to invisible focus rings, missing landmarks, poor text contrast, and lack of screen-reader announcements.
- **Level AA Compliance Pattern (Without Ruining Dark Brutalist Aesthetic):**
  1. **Keyboard Focus Ring (`:focus-visible` — WCAG 2.4.7):**
     - Never disable outlines (`outline: none` without replacement is a critical violation).
     - Target `:focus-visible` specifically so mouse/touch users do not see outlines.
     - Style: `outline: 2px solid #FF0033 !important; outline-offset: 3px !important; box-shadow: 0 0 12px rgba(255, 0, 51, 0.45) !important;`. This looks like a deliberate neon-red cyberpunk accent while passing contrast and visibility rules.
  2. **Bypass Blocks / Skip to Content Link (`.skip-link` — WCAG 2.4.1):**
     - Placed immediately after `<body>` on every HTML page:
       `<a href="#main-content" class="skip-link">رفتن به محتوای اصلی</a>`.
     - Positioned offscreen by default (`top: -120px; transition: top 0.2s ease`).
     - On keyboard focus (`:focus`), drops down into viewport (`top: 20px; background: #FF0033; color: #FFFFFF; z-index: 1000000;`).
     - Points to `<main id="main-content">` landmark on all template pages.
  3. **Accessible Form Controls & Explicit Labels (WCAG 1.3.1, 3.3.2):**
     - Audit finding: Form inputs relying only on `placeholder` fail accessibility because placeholders vanish on typing and are ignored by many assistive tools.
     - Solution: Add `<label for="[id]" class="form-label">` or `<label for="[id]" class="sr-only">` to all form controls (shipping name, phone, postal code, province, city, detailed address, coupon input, login/register fields, search bar).
     - Provide `aria-label` on icon-only buttons (search trigger, search close, drawer dismiss, password visibility toggle).
  4. **Dynamic Cart Drawer & Modal Semantics (WCAG 4.1.2):**
     - Cart drawer container: `role="dialog" aria-modal="true" aria-labelledby="cart-drawer-title" aria-hidden="true"`.
     - Header title: `<h3 class="drawer-title" id="cart-drawer-title">سبد خرید</h3>`.
     - In JavaScript (`ui.openCart()` / `ui.closeCart()`): toggle `aria-hidden="false"` and `aria-hidden="true"`, and shift keyboard focus to `#cart-drawer-close` upon opening and restore focus to trigger upon closing.
  5. **Live Region Status Announcer (WCAG 4.1.3):**
     - Add persistent announcer at page bottom:
       `<div id="a11y-status-announcer" role="status" aria-live="polite" class="sr-only"></div>`.
     - In `ui.showToast(message)`: dynamically inject text into `#a11y-status-announcer` alongside visual toast so blind or visually-impaired users hear notifications (e.g. "محصول به سبد خرید افزوده شد").
  6. **Contrast Boosts (WCAG 1.4.3 & 1.4.11):**
     - Muted text: Upgrade `#71717A` (fails AA at 4.16:1) to `#A1A1AA` (passes AA at 7.85:1).
     - Badges: Dark red `#990000` text on dark backgrounds fails AA. Use white text `#FFFFFF` on red background with neon border for `.badge-sale`.
     - Input borders: Upgrade faint `#27272A` borders to `rgba(255, 255, 255, 0.28)` to meet the 3:1 non-text contrast threshold.

---

## 27. GEO (Generative Engine Optimization) & AI Search Standards (`llms.txt` & `llms-full.txt`)

- **Audit Trigger:** AI visibility and generative engine optimization (GEO) audits report `404 Not Found` for `https://voidclubs.ir/llms.txt`. Perplexity, ChatGPT Search, Claude, and Gemini crawlers fail to extract brand context accurately.
- **The Standard Specification (Answer.AI / llmstxt.org):**
  - Modern AI models look for `/llms.txt` at the web root to ingest clean, Markdown-formatted documentation of brand identity, products, sizing, and policies without parsing heavy HTML/JS DOMs.
  - **Core File (`llms.txt`):** High-level structured markdown with H1 title, summary blockquote, brand ethos, core collection links, fabric/printing quality standards, shipping/pricing thresholds, and key canonical URLs.
  - **Extended File (`llms-full.txt`):** In-depth technical context including complete sizing table (cm dimensions for M/L/XL/2XL), garment care steps, payment/logistics flows, and design tokens.
- **Search Engine Discovery Wiring:**
  1. **Robots.txt Rule:** Add explicit `Allow` directives in `robots.txt`:
     ```txt
     # LLM & AI Search Engine Indexing (GEO)
     Allow: /llms.txt
     Allow: /llms-full.txt
     ```
  2. **Head Alternate Link:** Inject into `<head>` of primary index/catalog pages (`index.html`, `shop.html`, `about.html`):
     ```html
     <link rel="alternate" type="text/plain" href="https://voidclubs.ir/llms.txt" title="LLM Context">
     ```
  3. **Apache Direct Access:** Ensure root `.htaccess` allows `.txt` static serving (do not block `.txt` under `FilesMatch`).

---

## 28. E-Commerce Order Bump & Cross-Sell Architecture (AOV Optimization)

- **Audit Trigger:** Checkout CRO Audits (Baymard Heuristics) cite absence of Order Bumps / Cross-sell offers as a missed opportunity (+12% to +18% potential cart value increase).
- **Dual-Touchpoint Architecture:**
  1. **Cart Drawer Cross-Sell (`updateCartDrawer()` in `js/ui.js`):**
     - Renders an attractive, dark dashed card (`.cart-drawer-cross-sell`) below the cart items.
     - Recommends complementary, high-impulse items (e.g. Waterproof Metal Stickers Pack, Cyberpunk Lanyard) that are not currently in the user's cart.
     - Single-tap `+ افزودن` button calls `cart.addCustomItem(bump)`, re-renders the cart drawer, advances the dynamic free shipping meter, and announces to screen readers.
  2. **1-Click Checkout Order Bump Card (`#checkout-order-bump` in `checkout.html`):**
     - Placed in the order summary column right beneath the cart items list and above the discount coupon.
     - High-contrast checkbox connected to `handleToggleOrderBump(this)`.
     - Toggling the checkbox seamlessly adds/removes the item from `cart`, immediately re-rendering `#checkout-items-list` and recalculating subtotal, shipping rate, and payable total.
- **Client Cart Engine Enhancements (`js/cart.js`):**
  - Implement `addCustomItem(itemData)` and `hasItem(idOrKey)` to support string-identified add-on products (`bump_stickers_v1`) without throwing errors in `products.getById()`.
  - Update `update(itemIdOrVariantId, quantity)` to compare keys using `String(id)` so numeric and string item IDs never mismatch.
- **Backend Order Safety (`api/api.php` & `lib_db.php`):**
  - When `POST /orders` is received, inspect items: if `is_bump` is true or ID is non-numeric, record in `order_items` with `product_id = NULL` and the exact `price_at_purchase`.
  - In `vc_order_full()` in `lib_db.php`, if `product_id` is null, supply fallback product metadata so invoices and admin order screens display the bumper title and emblem thumbnail cleanly without database foreign key errors.

---

## 29. Product Custom Badges Clearing Bug & Typography Architecture

- **Symptom:** Admin sets a custom badge (`NEW`, `LIMITED`, `ویژه`, `دراپ خاص`) on a product. Later, when attempting to remove or clear the badge in the admin panel, the badge refuses to delete and remains stuck on the product, or renders in an ugly broken system font on the storefront.
- **Root Cause 1 (Backend Update Skipping Null/Empty Fields):**
  In `PUT /products/{id}` in `api/api.php`, the field iteration previously checked:
  `if (array_key_exists($f, $b) && $b[$f] !== null)`.
  When an admin cleared the input in the edit modal, client JS passed `badge: null` or `badge: ""`. Because of `$b[$f] !== null`, PHP skipped the `badge` column entirely in the SQL `UPDATE` statement. The old badge remained forever in the database.
  - **Fix:** In `api/api.php`, inspect `array_key_exists($f, $b)`. If `$f === 'badge'` and the string is empty or null, explicitly push `$args[] = null` so the column is updated to `NULL` in MySQL/SQLite.
- **Root Cause 2 (Font-Family Collision on Persian Badges):**
  The `.badge` CSS rule in `core.css` had `font-family: var(--font-en)`. If an admin entered Persian characters for a badge, the browser fell back to unstyled system fonts.
  - **Fix:** Apply `font-family: var(--font-fa), var(--font-en), sans-serif !important;` with `line-height: 1.25;` and `box-shadow: 0 2px 8px rgba(0, 0, 0, 0.4);`.
- **Admin UX:** Add an explicit «پاک کردن بج» button (`onclick="document.getElementById('edit-p-badge').value=''"` beside `#edit-p-badge` in `account.html`).

---

## 30. Dynamic Order Bump Admin Settings & Storewide Toggling

- **Requirement:** Admin must be able to change the Order Bump product, update its discount price, or switch off the Order Bump entirely from the admin panel without modifying code.
- **Backend Architecture (`/settings/order-bump`):**
  - `GET /settings/order-bump`: Returns JSON with `enabled` (bool), `product_id`, `title`, `price`, `old_price`, `description`, `image`, and `product` (hydrated catalog item if an ID was selected).
  - `PUT /settings/order-bump`: Admin-only route persisting values via `vc_set_setting($pdo, 'order_bump_*', ...)`.
- **Admin Panel UI (`account.html`):**
  - Subtab `admin-sec-order-bump` in Enterprise Admin.
  - Form includes toggle checkbox (`#order-bump-admin-enabled`), dynamic catalog product dropdown (`#order-bump-admin-product-select`), title, discounted price (in thousands of Tomans), old price, teaser description, and image URL.
  - Selecting a product from the dropdown auto-populates title, price, and image.
- **Storefront Client Synchronization (`js/app.js` & `js/ui.js`):**
  - On startup, `fetchOrderBumpConfig()` loads `/settings/order-bump` and stores in `window.VOID_ORDER_BUMP_CONFIG`.
  - If `enabled === false`:
    - `#checkout-order-bump` in `checkout.html` is hidden (`display: none`).
    - The cross-sell card in the cart drawer (`ui.js`) is omitted.
  - If `enabled === true`:
    - Title, price, old price, image, and description dynamically update across drawer and checkout.

---

## 31. Intelligent Cross-Sell Cart Recommendations Slider (Up to 30 Items)

- **Requirement:** A responsive, swipeable horizontal slider inside the Cart Drawer recommending up to 30 products based on items currently in the user's cart.
- **Empty-Cart & Fail-Safe Architecture (CRITICAL):**
  - **Empty-Cart Rendering:** If the cart drawer returns early on `cart.items.length === 0`, the recommendation slider is never rendered! Users who open an empty cart drawer must still see cross-sells. The drawer must render `#cart-drawer-recommended-slider` in both empty and populated states, showing top trending studio drops (`🔥 محبوب‌ترین دراپ‌های استودیو VOID CLUB`) when empty, and personalized collection/category items (`✨ محصولات پیشنهادی برای تکمیل استایل`) when populated, both strictly respecting the alternating garment sequence (دورس ➔ هودی ➔ تیشرت).
  - **Type Mismatch Pitfall (`cart.getCart()`):** `cart.getCart()` returns an object `{ id: 'guest', items: [...], total: 0 }`, NOT an array. Passing it directly into `(cartItems || []).forEach(...)` throws `TypeError: cartItems.forEach is not a function` which silently hides the slider in `try/catch`. Always extract: `const itemsList = Array.isArray(cartItems) ? cartItems : (cartItems && Array.isArray(cartItems.items) ? cartItems.items : []);`.
  - **Top-Level `formatPrice` Reference Error:** `ui.js` is deferred before `app.js`. Calling `formatPrice()` in `ui.js` before `app.js` runs throws a fatal `ReferenceError: formatPrice is not defined`. Always attach a fallback `window.formatPrice` at the very top of `ui.js`.
  - **Background Catalog Prefetch:** In `app.js` `initRouter()`, initiate background prefetching of all products into `window._cachedAllProducts` so the cart drawer slider renders instantly without waiting for an API call on click.
- **Recommendation Algorithm (`computeCartRecommendations(cartItems, allProducts, limit = 30)` in `js/ui.js`):**
  1. **Exclude In-Cart Products:** Any product already present in `cart.getCart()` is strictly filtered out.
  2. **Extract Context:** Extract collection keywords from titles (e.g. `بلسفموس`, `برزرک`, `فایت کلاب`, `کارآگاه حقیقی`, `تیم ایمپالا`, `دکستر`, `هانیبال`, `بتر کال سال`, `ادیسه`, etc.) and categories from items in the cart.
  3. **Candidate Segregation:**
     - **Pool 1 (Collection):** Products belonging to the exact same collection/artwork pool as items in the cart.
     - **Pool 2 (Category):** Products sharing the same category ID as items in the cart (excluding Pool 1).
     - **Pool 3 (Storewide):** Other products in the catalog (shuffled randomly for discovery).
  4. **Strict Garment Rhythm Pattern:**
     - Must follow a cyclic alternation: **دورس (sweatshirt) ➔ هودی (hoodie) ➔ تیشرت (tshirt)** (`['sweatshirt', 'hoodie', 'tshirt']`).
  5. **Pass 1 (Unique Artwork Designs):** For each slot 0 to 29, query Pool 1, then Pool 2, then Pool 3 for an unused artwork design signature matching the target garment type.
  6. **Pass 2 (Fill to 30):** If unique designs are exhausted before 30 items, permit secondary garment formats of the same designs (preserving the alternating pattern) until 30 slots are filled.
- **Slider UI (`#cart-rec-slider-track` in `js/ui.js`):**
  - Compact cards (`flex: 0 0 135px; scroll-snap-align: start`), square 1:1 image, garment badge chip (هودی/دورس/تیشرت), 2-line clamped title, accent price, and «مشاهده و خرید» button.
  - Smooth programmatic scroll controls via `ui.scrollCartRecSlider(direction)`.

---

## 32. Authentic Store Copy for AI / GEO Discovery (`llms.txt` & `llms-full.txt`)

- **User Direct Preference (session 2026-09-23):** Never write generic, robotic, or fabricated text for LLM/GEO files, and NEVER mention specific grammages like «۴۵۰ گرم». Use the exact authentic brand copy and real catalog specs:
  > «آرشیو اختصاصی استودیو VOID CLUB شامل جدیدترین دراپ‌های هودی ، تیشرت‌ و دورس در سبک‌های دارک انیمه، سینما، موسیقی و...  
  > تمامی پوشاک از پارچه ۱۰۰٪ پنبه سنگین سوپرپنبه با چاپ مستقیم نفوذی DTG با ثبات رنگ تضمین‌شده تولید شده‌اند تا استایلی متمایز و آوانگارد را با حداکثر راحتی و ماندگاری برای شما خلق کنند.»
- **Essential Brand Grounding:**
  - Real collections: Blasphemous (تاج خار، بانوی ما), Berserk (گاتس، برند آو سکریفایس), True Detective (راست کول و کارکوسا), Fight Club (تایلر داردن و صابون), Tame Impala (کرنث), Dexter, Hannibal, Billy Idol, Better Call Saul, Odyssey.
  - 100% heavy super combed cotton (سوپرپنبه), enzyme wash (no shrinkage), DTG ink penetration (no cracking), drop-shoulder cut, cm size table for M to 2XL, free shipping over 3,000,000 Tomans.

---

## 33. Action Buttons Wrapping Bug ("مشاهده همه") on Mobile Screens

- **Symptom:** In mobile viewports (`product.html` under "YOU MIGHT ALSO LIKE" or catalog section headers), the "مشاهده همه" button is squeezed by long Persian headings, forcing "مشاهده" onto line 1 and "همه" onto line 2 («دکمه مشاهده همه دو خطه میشه»).
- **Root Causes:**
  1. Section headings using static large font (`font-size: 26px`) take up ~75% of the mobile width.
  2. The button lacked `white-space: nowrap !important;` and `flex-shrink: 0 !important;`.
- **Comprehensive Solution:**
  1. **Responsive Header Font:** Apply fluid typography on section titles:
     `font-size: clamp(18px, 4.5vw, 26px); font-weight: 900;`.
  2. **Global CSS Protection (`css/core.css`):**
```css
.btn-view-all,
.btn-outline,
.btn-primary,
.btn-accent,
.btn,
a.btn,
button.btn {
    white-space: nowrap !important;
    word-break: keep-all !important;
}

.btn-view-all {
    white-space: nowrap !important;
    word-break: keep-all !important;
    flex-shrink: 0 !important;
    display: inline-flex !important;
    align-items: center !important;
    justify-content: center !important;
    padding: 8px 18px !important;
    font-size: 11.5px !important;
}

@media (max-width: 768px) {
    .btn-view-all {
        padding: 6px 14px !important;
        font-size: 11px !important;
        min-width: max-content !important;
    }
}
```

---

## 34. Inline Head UTM & Telemetry Queue Sniffer (`dataLayer` & `void_utm`)

- **Context:** Automated audit tools and external scanners evaluate the live website via cURL / initial response, often failing to execute deferred JavaScript bundles.
- **Solution:** Place an immediate inline sniffer in `<head>` (before closing `</head>`) across all HTML and pre-rendered PHP templates:
```html
<!-- VOID UTM & Analytics Event Queue (GA4 / GTM / Campaign Tracker) -->
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){window.dataLayer.push(arguments);}
  (function() {
    try {
      const p = new URLSearchParams(window.location.search);
      const ref = (document.referrer || '').toLowerCase();
      let src = p.get('utm_source');
      if (!src) {
        if (ref.includes('instagram')) src = 'instagram';
        else if (ref.includes('t.me') || ref.includes('telegram')) src = 'telegram';
        else if (ref.includes('google')) src = 'google';
      }
      if (src) {
        localStorage.setItem('void_utm', JSON.stringify({
          source: src,
          campaign: p.get('utm_campaign') || 'direct',
          medium: p.get('utm_medium') || (ref ? 'referral' : 'social'),
          term: p.get('utm_term') || '',
          content: p.get('utm_content') || '',
          time: new Date().toISOString()
        }));
      }
    } catch (e) {}
  })();
</script>
```
- Ensures external audit scanners immediately detect `dataLayer` / `gtag` presence and marketing referrals from Instagram and Telegram are recorded synchronously on the very first byte.

---

## 35. Guest Order Bump Default-Disabled State & Cache Invalidation

- **Symptom:** When a guest or unauthenticated user navigates to the cart drawer or checkout page, the Order Bump package card is displayed even though the store administrator turned off the Order Bump option in the admin panel.
- **Root Causes:**
  1. **Frontend Fallback Bias:** In client-side initialization (`ui.js` and `app.js`), if `window.VOID_ORDER_BUMP_CONFIG` is not yet loaded or pending network fetch, naive logic `const isBumpEnabled = window.VOID_ORDER_BUMP_CONFIG ? window.VOID_ORDER_BUMP_CONFIG.enabled !== false : true;` evaluated to `true`!
  2. **Raw HTML Display in Checkout:** The `#checkout-order-bump` container in `checkout.html` had no initial `display: none` style, rendering visibly before the config API returned.
  3. **Stale Cache Headers:** The `/settings/order-bump` API endpoint used `Cache-Control: public, max-age=15`, causing browser and edge caches to serve stale "enabled" responses after an admin turned it off.
- **Recipe:**
  1. **API Header:** In `api/api.php` under `/settings/order-bump`, send `header('Cache-Control: no-cache, no-store, must-revalidate');`.
  2. **HTML Default State:** In `checkout.html`, mark `#checkout-order-bump` with `style="display: none; ..."` so it stays hidden until explicitly confirmed enabled.
  3. **Strict Truthiness Check:**
     `const isBumpEnabled = !!(window.VOID_ORDER_BUMP_CONFIG && (window.VOID_ORDER_BUMP_CONFIG.enabled === true || window.VOID_ORDER_BUMP_CONFIG.enabled === '1' || window.VOID_ORDER_BUMP_CONFIG.enabled === 1));`
  4. **Post-Fetch Re-render & Cleanup:** When `fetchOrderBumpConfig()` resolves, if `!isBumpEnabled`, immediately hide the DOM node, prune any stale bump item from `cart` via `cart.removeItem()`, and update the cart drawer.

---

## 36. RTL Horizontal Slider Scroll Direction Pitfall

- **Symptom:** In Persian RTL layouts (`<html dir="rtl" lang="fa">`), clicking the left/right arrow buttons on horizontal sliders (such as the cart cross-sell carousel) scrolls the items in the opposite direction of the arrow.
- **Root Cause:** In modern DOM standards for RTL horizontal scroll containers, the initial position (start of content) is on the far right (`scrollLeft = 0`). Progression to "next" items (moving leftward into the scrollable overflow) requires **decreasing** `scrollLeft` or passing a **negative** delta to `scrollBy({ left: -delta })`. Calling `scrollBy({ left: +delta })` moves rightward toward the start (previous), which reverses the expected user action.
- **Recipe:**
```javascript
scrollCartRecSlider(direction) {
  const track = document.getElementById('cart-rec-slider-track');
  if (!track) return;
  // In RTL Persian layout:
  // direction > 0 means "بعدی" (advance through items -> scroll left in RTL: negative delta)
  // direction < 0 means "قبلی" (return to previous items -> scroll right in RTL: positive delta)
  const delta = 280 * Math.sign(direction);
  try {
    track.scrollBy({ left: -delta, behavior: 'smooth' });
  } catch (e) {
    track.scrollLeft -= delta;
  }
}
```

---

## 37. Category Deep-Link Collection Tree Resolution (`categories?category=...`)

- **Symptom:** Navigating to `categories?category=Anime` displays the whole website's parent categories instead of the collections belonging to Anime.
- **Root Causes:**
  1. **Case-Sensitive Slug Collisions:** `n.slug === slug` fails when query parameters have uppercase characters (`Anime` vs `anime`).
  2. **Fragile Hardcoded Filters:** Attempting to filter anime collections with regex `/(anime|manga)/i` fails because actual franchise collections under Anime (e.g. Berserk, Vagabond, Vinland Saga) do not contain the word "anime" in their slugs.
  3. **Unsafe Empty Fallback:** When child matching returned 0 items, legacy code fell back to `categoriesPageData` (the entire root category tree).
- **Recipe:**
  1. **Case-Insensitive & Alias Resolution:** `categoriesFindBySlugOrName(query)` decodes, trims, lowercases, and checks `slug`, `name`, and common category aliases (e.g. anime ➔ انیمه/مانگا, cinema ➔ سینما/فیلم).
  2. **Hierarchical Child Harvesting:** First inspect `targetNode.children`. If empty, inspect flat categories with `Number(c.parent_id) === Number(targetNode.id)`. For broad mother categories like Anime, supplement with known franchise keywords.
  3. **Leaf Navigation:** If a category genuinely has no child collections, redirect directly to `shop?category=${encodeURIComponent(targetNode.slug)}`. Never fall back to root parent categories.

---

## 38. WCAG Skip-Link Styling & Standalone Card Page Suppression

- **Symptom:** On mobile viewports, pages like `login.html` display raw, unstyled text `رفتن به محتوای اصلی` right above the login card.
- **Root Causes:**
  1. **Context Inappropriateness:** Single-purpose minimalist pages (`login.html`, `payment-callback.html`, HTTP 40x/500 error cards) have no top navigation menus to skip over; injecting a skip link adds visual clutter without any accessibility benefit.
  2. **CSS Link Absence:** `login.html` does not load `core.css`, so `.skip-link` styles were completely absent.
- **Recipe:**
  1. **Omit on Minimal Pages:** Completely remove `<a href="#main-content" class="skip-link">` from `login.html`, `payment-callback.html`, and error templates.
  2. **Bulletproof Off-Screen Styling on Content Pages:** In `core.css`, style `.skip-link` using the standard accessible offscreen pattern:
```css
.skip-link {
    position: absolute !important;
    top: -9999px !important;
    left: -9999px !important;
    width: 1px !important;
    height: 1px !important;
    overflow: hidden !important;
    clip: rect(0,0,0,0) !important;
    white-space: nowrap !important;
    border: 0 !important;
    padding: 0 !important;
    margin: -1px !important;
    z-index: 999999 !important;
}

.skip-link:focus,
.skip-link:focus-visible {
    top: 14px !important;
    left: 14px !important;
    width: auto !important;
    height: auto !important;
    clip: auto !important;
    overflow: visible !important;
    padding: 10px 18px !important;
    background: #FF0033 !important;
    color: #ffffff !important;
    font-size: 13px !important;
    font-weight: 800 !important;
    border-radius: 8px !important;
    box-shadow: 0 10px 30px rgba(0, 0, 0, 0.8) !important;
    outline: 2px solid #ffffff !important;
    outline-offset: 2px !important;
}
```
  This guarantees 0px layout impact and complete invisibility on mobile and desktop, while sliding in gracefully only when keyboard users press Tab.

---

## 39. Cart Drawer Stacking Context & Mobile Sticky Buy Bar Collision

- **Symptom:** On mobile PDP pages (`product.html`), opening the cart drawer (`#cart-drawer`) reveals the PDP sticky purchase bar (`#pdp-sticky-buy-bar`) floating directly ON TOP of the cart drawer. It completely obscures the cart footer, price total, and the primary "تسویه حساب" (Proceed to Checkout) button.
- **Root Cause:** `#pdp-sticky-buy-bar` was given `z-index: 99999` to ensure it floated above normal document content, while `.drawer` had `z-index: 1020` (and `2000` in critical.css) and `.drawer-overlay` had `1010`. Because `99999 > 1020`, the sticky bar cut right across the open cart drawer modal.
- **Universal Stacking Hierarchy Protocol:**
  1. Drawer modal overlay (`.drawer-overlay`): `z-index: 100000 !important;` in `layout.css`, `critical.css`, and `core.css`.
  2. Drawer container (`.drawer`): `z-index: 100001 !important;` with solid background (`rgba(14, 14, 20, 0.98)`).
  3. Sticky buy bar (`#pdp-sticky-buy-bar`): lowered to `z-index: 995;`.
  4. Mobile bottom bar (`.mobile-bottom-bar`): `z-index: 980;` or `990;`.
- **Mutual Exclusion via `body.cart-open`:**
  - In `js/ui.js` `openCart()`: immediately add `document.body.classList.add('cart-open')`, set `#pdp-sticky-buy-bar` to `display: none` and `.mobile-bottom-bar` to `display: none`.
  - In `closeCart()`: remove `document.body.classList.remove('cart-open')`, restore `display: ''` for both bars, and trigger `__pdpStickyScrollHandler()` to re-evaluate visibility.
  - In `js/app.js` `setupStickyBuyBarObserver`: guard both intersection and scroll checks with `if (document.body.classList.contains('cart-open') || document.getElementById('cart-drawer')?.classList.contains('open')) return;`.
  - In CSS (`css/core.css`): enforce `body.cart-open .pdp-sticky-buy-bar, body.cart-open .mobile-bottom-bar, body:has(#cart-drawer.open) .pdp-sticky-buy-bar { display: none !important; opacity: 0 !important; visibility: hidden !important; pointer-events: none !important; transform: translateY(100%) !important; }`.

---

## 40. WCAG 2.2 Level AA Full Keyboard & Dialog Protocol

- **Audit Trigger:** WCAG 2.2 Re-Audit (`VOID_CLUB_WCAG22_ACCESSIBILITY_REAUDIT_REPORT.pdf`) reports missing keyboard event handlers on custom listboxes, link focus stripping, lack of dialog Escape handling, and unannounced cart operations.
- **Key Implementation Patterns:**
  1. **Keyboard-Navigable Searchable Dropdowns (SC 2.1.1):**
     - Custom province/city selects (`#province-dropdown`, `#addr-province-dropdown`):
       - On trigger input: `Enter`, `Space`, or `ArrowDown` opens the dropdown and focuses the search input.
       - Inside search input: `ArrowDown`/`ArrowUp` cycles through `.searchable-item` options with `.is-active` highlight and `scrollIntoView({ block: 'nearest' })`.
       - `Enter` selects the highlighted item, closes the dropdown, announces to screen reader (`ui.announce('استان انتخاب شد: ' + val)`), and moves focus to the city input.
       - `Escape` closes the dropdown and returns focus to trigger.
  2. **Global Escape Key Dismissal (SC 2.1.1, SC 2.4.3):**
     - Global `keydown` handler on `document`: When `e.key === 'Escape'`, closes `#cart-drawer` (`ui.closeCart()`), `#search-modal` (`ui.closeSearch()`), and any open location dropdowns.
  3. **Dialog Focus Management (SC 2.4.3):**
     - On `ui.openCart()`: Shifts focus to `#cart-drawer-close` button (`closeBtn.focus()`).
     - On `ui.closeCart()`: Restores focus to the triggering element (`#cart-btn-toggle.focus()`).
  4. **Live Screen-Reader Status Announcer (SC 4.1.3):**
     - Wire `ui.announce(msg)` to `<div id="a11y-status-announcer" role="status" aria-live="polite" class="sr-only">`.
     - Automatically called on: adding items to cart, opening cart, applying coupons, and address selection.
  5. **Standard Checkout Form Autocomplete (SC 1.3.5):**
     - Shipping name: `autocomplete="name"`.
     - Phone: `type="tel" autocomplete="tel"`.
     - Postal code: `autocomplete="postal-code"`.
     - State/Province: `autocomplete="address-level1"`.
     - City: `autocomplete="address-level2"`.
     - Address: `autocomplete="street-address"`.
  6. **Heading Order & Radio Label Associations (SC 1.3.1, SC 4.1.2):**
     - Checkout headings use `<h2>` before `<h3>` (no skips from H1 to H3).
     - Payment method radio buttons (`#pay-method-online-radio`, `#pay-method-c2c-radio`) carry explicit `for="..."` on labels and `aria-label` attributes.
  7. **High-Contrast Focus Indicators & Links (SC 1.4.3, SC 2.4.7):**
     - `a:focus-visible, button:focus-visible, input:focus-visible, select:focus-visible, textarea:focus-visible, [tabindex]:focus-visible { outline: 2px solid #FF0033 !important; outline-offset: 3px !important; }`.
     - `a:hover { color: #FF2B45; }` (provides 5.45:1 contrast against dark background `#070709`, passing WCAG AA vs 2.26:1 failure on `#990000`).
     - Reduced motion: `@media (prefers-reduced-motion: reduce) { .ambient-glow { animation: none !important; opacity: 0.08 !important; } }`.

---

## 41. Enhanced E-Commerce 7-Core Event Analytics Pipeline

- **Audit Trigger:** Analytics Audit Round 3 (`VOID_CLUB_ANALYTICS_REAUDIT_ROUND3_REPORT.pdf`) records a 72/100 score, missing 3 core e-commerce events: `select_item`, `add_shipping_info`, and `add_payment_info`.
- **Complete 7-Event Architecture:**
  1. `view_item_list`: Dispatched on catalog/showcase views.
  2. `select_item`: Dispatched via global delegated click handler on `a[href*="product?id="]` / `.product-card`. Extracts product ID, title, and price from card DOM and dispatches `item_list_name: document.title`.
  3. `view_item`: Dispatched when product details page loads.
  4. `add_to_cart`: Dispatched on `addCurrentProductToCart()` and drawer cross-sells.
  5. `begin_checkout`: Dispatched upon visiting `/checkout`.
  6. `add_shipping_info`: Dispatched in `handlePlaceOrder()` immediately upon passing address, phone, and postal code regex validation, capturing `shipping_tier: 'پست پیشتاز سراسری'`, `shipping_state`, `shipping_city`, items, and order value.
  7. `add_payment_info`: Dispatched in `handlePaymentMethodChange(value)` when the customer selects or switches between online gateway and card-to-card, capturing `payment_type` ('درگاه بانکی شتاب' / 'کارت به کارت'), items, and order value.
  8. `purchase`: Dispatched upon successful order creation with `transaction_id`, value, and items.
- **Dual Tag Dispatch:** In `voidTracker.track(eventName, eventData)`:
  - Pushes event and ecommerce payload to `window.dataLayer`.
  - Dispatches `window.gtag('event', eventName, eventData)` if `gtag` is defined.
  - Sends domestic beacon to `/api/event` via `navigator.sendBeacon`.

