---
name: web-development-pitfalls
description: "Use when fixing web dev, CDN caches, and GitHub API limits."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Web, HTML, JS, GitHub Pages, Debugging]
---

# Web Development Pitfalls

This skill contains durable lessons and workarounds for web development tasks, specifically targeting browser/CDN caching, API-driven architectures, and large file handling.

## Static Site Font Audit (Missing Files, Path Mismatches, Unicode Gaps)

**Pitfall:** A site declares `@font-face` rules and HTML `<link rel="preload">` for fonts, but the actual `.woff2`/`.woff`/`.ttf` files are missing from disk, exist in a different directory than the CSS references, or the CSS `unicode-range` is too narrow for the target language. The browser silently falls back to system fonts — no console error, no network failure, just wrong-looking text.

**Root causes found together (2026-09-18):**
1. **Font files never downloaded** — `@font-face` declarations exist in CSS but the `.woff2` files were never placed in the project. Zero files in the fonts directory.
2. **Path mismatch between CSS and HTML** — CSS `@font-face` `src: url('../fonts/...')` resolved to `project-root/fonts/` while HTML preloads pointed at `project-root/assets/fonts/`. Neither directory had files, and even after downloading, only one path would have worked.
3. **Hardcoded `font-family`** instead of CSS variables — dozens of CSS rules and HTML inline styles used `'Vazirmatn', sans-serif` directly instead of `var(--font-fa)`, meaning any font change requires grep-and-replace across every file.
4. **Narrow `unicode-range`** — the original range for a Persian font covered only `U+0600-06FF` (basic Arabic) but missed `U+200C` (ZWNJ/نیم‌فاصله), `U+200D` (ZWJ), `U+0660-0669` (Arabic-Indic digits), and `U+2018-201F` (quotation marks). Characters outside the range silently fell back to system font.

**Audit checklist (run for any site using custom fonts):**
1. **Do font files exist?** `find . -name '*.woff2' -o -name '*.woff' -o -name '*.ttf'` — if zero results, fonts never load.
2. **Do CSS `@font-face` paths resolve?** Compare `src: url(...)` in CSS against `href="..."` in HTML preloads — they must resolve to the same files. CSS paths are relative to the CSS file location, not the HTML file.
3. **Is `font-family` consistent?** Grep for hardcoded font names outside `@font-face` blocks: `grep -rn "font-family:" --include='*.css' --include='*.html' | grep -v '@font-face' | grep -v 'var(--font'` — any match is a candidate for variable replacement.
4. **Is `unicode-range` broad enough?** For Arabic/Persian fonts, ensure at minimum: `U+0600-06FF, U+0750-077F, U+08A0-08FF, U+FB50-FDFF, U+FE70-FEFF, U+200C-200F, U+0660-0669`. Missing ZWNJ (`U+200C`) is the #1 cause of "half the Persian text looks wrong".
5. **Are `font-display: swap` and `crossorigin` on preloads?** Missing `crossorigin` on preload `<link>` tags causes the browser to download the font twice (once for preload, once for CSS) or silently skip the preload.

**Quick download sources:**
- Vazirmatn: `cdn.jsdelivr.net/gh/rastikerdar/vazirmatn@v33.003/fonts/webfonts/Vazirmatn-{Regular,Medium,Bold,Black}.woff2`
- Outfit (variable font): fetch `fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800&display=swap` with a Chrome User-Agent header to get woff2 URLs.

## Icon Libraries: Self-Host Them, Never Lazy-Load From CDNs

**Pitfall:** Icon fonts (RemixIcon, Font Awesome) loaded from `cdn.jsdelivr.net` / `cdnjs.cloudflare.com` — especially via the "performance" pattern `<link rel="preload" as="style">` + `<link rel="stylesheet" media="print" onload="this.media='all'">` — silently vanish for users behind restrictive national filtering (e.g. Iran) or corporate proxies. The CDN request hangs or is reset, the stylesheet never applies, and because it was loaded with `media="print"`, the browser considers it "done" — no console error, no fallback. Result: every `ri-*`/`fa-*` glyph renders as blank/invisible forever. A second variant: a page uses icon classes but the library `<link>` is simply missing from `<head>` (seen: a page with 80 icon classes and zero links).

**Why the lazy pattern makes it worse:** normal `<link>` failures are visible in DevTools; the `media="print"` swap depends on the stylesheet's own `onload` firing, which never happens if the connection stalls instead of erroring fast. There is no timeout and no retry.

**Fix (validated 2026-09-18):**
1. Download the CSS + font binaries locally: `assets/icons/remixicon.css` + `remixicon.woff2/.ttf` (strip `.eot`/`.woff` lines from the CSS), and Font Awesome `all.min.css` verbatim + `fa-brands-400`, `fa-regular-400`, `fa-solid-900`, `fa-v4compatibility` (`.woff2` + `.ttf`) into `assets/webfonts/`. FA's `url(../webfonts/...)` paths resolve correctly when the CSS sits one directory above.
2. Link both stylesheets plainly in `<head>` on EVERY page that uses icon classes — no preload/print tricks.
3. Audit: grep each HTML for `class="...ri-|fa-...` usage, then require both local links present; zero CDN references (`grep -c 'jsdelivr\|cdnjs' *.html` = 0) is the acceptance check.
4. Verify live in a browser: `document.fonts.check('16px remixicon')` and `('16px "Font Awesome 6 Free"')` → `true`; a rendered icon element's computed `fontFamily` must be the icon font. Note icon fonts are lazy-loaded on demand — `fonts.check` returning `false` while no icon element is on screen is normal.
5. If the site relies on aggressive asset caching (30–90 day `Expires` headers), bump the CSS `?v=` query in all pages when icon/font files change, or hosts keep serving stale bytes even after a correct upload.

**Trade-off note:** self-hosting costs ~450KB of static assets but removes all external dependency and CSP/allowlist concerns. For this user's hosting region the trade is mandatory, not optional.


## Cloudflare Worker API: UA-less PUT 403s and Stale GETs
See `references/cloudflare-worker-put-and-cache.md` — always send an explicit `User-Agent` on every Worker API call (WAF 403s headerless PUTs even when GETs pass with the same token), and ship `Cache-Control: no-store` + client cache-bust from day one.

## GitHub Pages Caching
GitHub Pages aggressively caches static assets (`.js`, `.css`). When you push a fix to a script but the user reports the site is still broken (even after hard refreshing), the browser or an intermediate CDN has cached the old version.
**Workaround:** Edit the HTML file to append a cache-buster query string (like a Unix timestamp) to the asset URL, then push the HTML update.
```html
<!-- Change this: -->
<script src="script.js"></script>

<!-- To this: -->
<script src="script.js?v=1785304336"></script>
```
This forces all downstream caches and the user's browser to fetch the fresh file.

## Large File Updates via GitHub API
When using the GitHub REST API (`PUT /repos/:owner/:repo/contents/:path`) as a fallback because the local `git` client is failing (e.g., networking timeouts), large base64-encoded strings will break bash argument length limits and quoting.

**Pitfall:** `curl -d '{"content": "'$B64'"}'` will fail with "Invalid request" or silently truncate the file for payloads over ~32KB.

**Solution:** Write the JSON payload to disk using Python, then pass it to curl via `@payload.json`.
```python
import json, base64, urllib.request

b64 = base64.b64encode(open('large-file.html', 'rb').read()).decode()

# Must fetch the current SHA to update an existing file
req = urllib.request.Request('https://api.github.com/repos/owner/repo/contents/large-file.html', headers={'Authorization': 'token MY_TOKEN'})
sha = json.loads(urllib.request.urlopen(req).read())['sha']

with open('payload.json', 'w') as f:
    json.dump({"message": "update file", "content": b64, "sha": sha, "branch": "main"}, f)
```
```bash
curl -X PUT -H "Authorization: token MY_TOKEN" -d @"payload.json" https://api.github.com/repos/owner/repo/contents/large-file.html
```

## GitHub Pages Deployment Workflow

When deploying a static site (HTML/CSS/JS) to GitHub Pages, follow this complete sequence:

```bash
# 1. Create repo
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  https://api.github.com/user/repos \
  -d '{"name":"my-site","description":"Description","public":true}'

# 2. Push code
cd /path/to/site && git init && git add -A && git commit -m "Initial commit"
git remote add origin https://github.com/$GH_USER/my-site.git
git branch -M main && git push -u origin main

# 3. Enable Pages (deploy from root of main branch)
curl -s -X POST \
  -H "Authorization: token $GITHUB_TOKEN" \
  -H "Content-Type: application/json" \
  "https://api.github.com/repos/$GH_USER/my-site/pages" \
  -d '{"source":{"branch":"main","path":"/"}}'

# 4. Wait for deploy and verify (takes 10-60 seconds)
sleep 15
curl -s -o /dev/null -w "%{http_code}" "https://$GH_USER.github.io/my-site/"
# Returns 200 when live
```

**Pitfalls:**
- Pages deploy takes 10–60 seconds. Don't immediately test — poll or wait.
- The `path` in the POST body determines which directory to serve. Use `"/"` for root.
- After deploy, check `curl -s .../repos/{owner}/{repo}/pages` for `"status": "built"`.
- Pages URL format: `https://{user}.github.io/{repo}/`
- To change the deploy source later, use PUT instead of POST on the same endpoint.

## Git Clone SSL Fallback (Windows schannel)

On Windows, `git clone` can fail with `SSL/TLS connection failed` due to schannel issues. The GitHub REST API uses a different TLS stack via curl, so you can read repo contents directly:

```bash
# List files in repo root
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/contents/" \
  | python3 -c "import json,sys; [print(f'{i[\"name\"]:40} {i[\"type\"]}') for i in json.load(sys.stdin)]"

# Read a file (base64-decode the content field)
curl -s -H "Authorization: token $GITHUB_TOKEN" \
  "https://api.github.com/repos/owner/repo/contents/file.js" \
  | python3 -c "import json,sys,base64; d=json.load(sys.stdin); print(base64.b64decode(d['content']).decode())"
```

**Pitfalls:**
- Files > 1 MB need the Git Blob API (`/repos/{owner}/{repo}/git/blobs/{sha}`).
- Directory listings give metadata only; read content via the individual file endpoint.
- The `download_url` field gives raw access, but authenticated API is more reliable for private repos.
- This pattern avoids schannel entirely since curl uses WinHTTP/OpenSSL for API calls.

## Daytona Workspace Deployments
Daytona is a cloud development environment. By default, it restricts outbound access to unknown domains (`Internet is restricted on Tier 1 and Tier 2`).

**Pitfalls:**
- Running `install.sh` scripts that fetch from non-GitHub domains will fail with `Connection reset by peer` or `404`.
- Downloading raw files from GitHub using `curl -fsSL` or `curl -fsSLO` can sometimes return `404` or fail due to network restrictions.
- The `hermes gateway run` command cannot connect to AI providers (OpenAI, Anthropic) if they are not explicitly whitelisted, resulting in `APIConnectionError`.

**Workarounds:**
- Clone the repository directly using `git clone` instead of downloading raw installer scripts via `curl`.
- Use a local proxy or port forwarding to route traffic.
- When deploying web apps/dashboards from Daytona for external access, you cannot rely on a public IP. Instead, push the `docker-compose.yml` (and a dummy `Dockerfile` if required by the target platform like Render) to GitHub, and deploy it via a free tier host (Koyeb, Render). Render requires a `Dockerfile` even if it just wraps an existing image: `FROM decolua/9router:latest\nEXPOSE 20128`.
When attempting to repair broken syntax in single-line minified JS using `patch` or `sed`, finding the exact unbalanced brace `{` or `}` is error-prone. The agent's fuzzy patch matcher often fails on dense one-liners or strips subsequent lines.

**Solution:** 
**Solution:** Do not attempt surgical string replacements on mangled minified JS. Instead:
1. Extract the broken JS.
2. Rewrite or restructure it cleanly.
3. Replace the entire `<script>` block, or better yet, move the JS to an external file (`script.js`) and link it. This eliminates HTML/JS escaping issues entirely.

## JavaScript Variable Scoping in Render/Draw Loops

**Pitfall:** A variable defined inside a parent function (like `render()`) is referenced by a child draw helper called from that parent, but the helper doesn't receive it as a parameter → `ReferenceError: X is not defined` at runtime.

This commonly happens with theme-detection variables (`isL`, `isDark`) that are computed once in `render()` but needed by multiple draw functions.

```js
// ❌ Broken — isL is local to render()
function render() {
  const isL = document.body.getAttribute('data-theme') === 'light';
  drawPowerups(); // ReferenceError: isL is not defined
}
function drawPowerups() {
  ctx.fillStyle = isL ? 'rgba(0,0,0,.04)' : 'rgba(255,255,255,.05)'; // 💥
}

// ✅ Fixed — pass as parameter
function render() {
  const isL = document.body.getAttribute('data-theme') === 'light';
  drawPowerups(isL);
}
function drawPowerups(isL) {
  ctx.fillStyle = isL ? 'rgba(0,0,0,.04)' : 'rgba(255,255,255,.05)'; // ✅
}
```

**Rule:** Every draw/render helper that depends on shared state should receive it as an explicit parameter. Do not rely on closure over parent-scope locals in render loops — the function is called frequently and stale closures cause subtle visual bugs.

## Missing Event Listeners After Code Rewrites

**Pitfall:** When rewriting large sections of JavaScript (e.g., replacing a full game loop or UI module), `addEventListener` calls for buttons/interactions can be accidentally dropped. The HTML still has the buttons, but the JS never wires them up — clicking does nothing, no error appears.

**Symptoms:**
- User clicks a button (e.g., "Continue", "Next Level") and nothing happens.
- Console shows no errors — the button simply has no listener.
- The code *looks* complete but a grep for the element ID in the JS reveals no `addEventListener`.

**Prevention:** After any large rewrite, grep for every `id="..."` in the HTML and verify each has a matching `getElementById('...').addEventListener` in the JS. A quick automated check:

```bash
# Extract HTML IDs, then check each has a JS listener
grep -oP 'id="([^"]+)"' index.html | sed 's/id="//;s/"//' | while read id; do
  grep -q "$id" game.js || echo "⚠️  No JS reference for #$id"
done
```

**Rule:** Event listeners are the most commonly dropped element during code rewrites. Always verify them as the LAST step before committing.

## Dependency Migration: Exhaustive Cleanup

**Pitfall:** When removing a dependency (e.g. Firebase, Supabase, jQuery), agents grep only `.js` and `.html` files. The dependency lingers in README, docs, config files, CSS comments, deploy scripts — causing confusion and broken documentation.

**Rule:** After removing a dependency, run a project-wide grep across ALL file types:
```bash
find . -type f \( -name "*.js" -o -name "*.html" -o -name "*.css" -o -name "*.md" \
  -o -name "*.yml" -o -name "*.yaml" -o -name "*.toml" -o -name "*.json" \
  -o -name "*.sql" -o -name "*.sh" -o -name "*.bat" \) \
  -exec grep -li "firebase\|supabase\|jquery\|<DEPENDENCY>" {} \;
```
Check every hit. Comments mentioning the old dependency in code are acceptable; references in README, documentation, and config must be removed or updated.

**User correction pattern:** "I told you to remove X but you didn't" — means the agent checked code but not docs/config. Always do the exhaustive grep as the FINAL verification step before claiming the migration is complete.

## Z-Index Stacking Contexts and Floating Dropdowns

**Pitfall:** Dropdown menus (e.g., custom selects, searchable location pickers, datepickers, toast notifications) frequently clip or hide underneath subsequent form cards, modal overlays, or layout containers when opened, despite having `z-index: 1000`. This happens because a parent element has `overflow: hidden`, a separate `isolation: isolate`, or a lower `z-index` in its own stacking context than sibling cards or modal backdrops with `position: fixed` / `position: relative`.

**Rules:**
1. Give floating dropdown popovers and global toast notification containers an explicit top-tier elevated z-index (e.g., `z-index: 9999999 !important`).
2. Ensure parent containers (like `.checkout-box` or `.form-group`) do not enforce `overflow: hidden` or lower stacking orders on mobile cards.
3. When dropdowns are used inside fixed modals (`.modal-overlay` with `z-index: 2000+`), ensure the dropdown wrapper uses `position: relative` and dropdown list items don't inherit overflow clipping from inner glass panels.
4. For select inputs that have complex search requirements, avoid nesting non-standard dropdowns where a standard text input or clean modal popover with `position: fixed` provides superior accessibility and zero clipping.

## Dynamic Homepage Collections & Admin Sync

**Pattern:** Rather than hardcoding category/collection cards in static homepage HTML:
1. Provide an async renderer on the home page (`initHomePage`) that queries `GET /api/categories`.
2. Map over returned categories and dynamically generate responsive collection cards with fallback thumbnails.
3. This guarantees that whenever an administrator adds, edits, or deletes a category in the admin management panel, the changes instantly reflect on the public landing page without requiring frontend code edits.

## Lightweight Zero-Dependency Persian & Jalali Datepickers

**Pattern:** When collecting localized birthdates or booking dates without bloated external calendar libraries:
1. Provide a `readonly` input styled with a calendar icon that triggers a small absolute glass popover.
2. Render three lightweight select dropdowns (Year, Month name, Day) with predefined reasonable ranges (e.g., 1320–1403).
3. Provide "Apply" and "Clear" buttons that format the date string (e.g., `YYYY/MM/DD`) directly into the input value and update the profile via API.

## Pure CSS UI Components & Micro-Interactions

When building pure CSS controls (segmented controls, 3D keys, accordions) without framework overhead:
- **Pure CSS Accordions (`<details>`):** Style `<summary>` with `list-style: none`, hide `-webkit-details-marker`, and use pseudo-elements (`summary::after`) with `transition: transform 0.3s ease` to rotate `+` to `45deg`. Target `.accordion-body` using `max-height` transitions on `[open]`.
- **Pure CSS Segmented Controls (Radio Tabs):** Use hidden radio inputs (`input { display: none; }`) paired with sibling `<label>` tags and an absolute `.slider` span. In RTL layouts, calculate `transform: translateX(-100%)`, `-200%`, etc., from the right boundary.
- **3D Press Buttons:** Combine linear background gradients with bottom borders / solid box-shadows (`box-shadow: 0 5px 0 #color_dark, 0 8px 15px rgba(0,0,0,0.3)`). On `:active`, use `transform: translateY(5px)` and collapse the shadow to `0 0 0`.

## Printable Order Invoices (`@media print`)

**Pattern:** When an e-commerce or management dashboard requires order invoices with print capabilities:
1. Provide a dedicated modal with full customer details (name, phone, address, tracking code, item breakdown with units/sizes/prices, discounts, and totals).
2. **Comprehensive Variant & Color Specification:** In invoice item tables and receipt cards, always display both the size and color specifications (e.g., `سایز L | رنگ مشکی زغالی (Deep Black)`), rather than size alone. This eliminates shipping errors and fulfills customer transparency on physical order receipts.
3. **Paper Margins vs Container Padding (Avoiding A4 Bleed & Clipping):**
   - Do NOT set `@page { margin: 0; }` combined with huge CSS padding (e.g. `75px` or `100px`) on `.invoice-card`. When `@page` margin is zero, browsers assume edge-to-edge printing, causing large paddings and wide tables to bleed outside the physical printable area of A4 paper.
   - Set standard print margins on `@page`: `@page { size: A4 portrait; margin: 14mm 12mm; }` and zero out body/container margins in print: `.invoice-card { padding: 0 !important; width: 100% !important; max-width: 100% !important; }`.
   - **Static Layering & Overflow Unlocking:** Fixed overlays with `position: fixed; max-height: 90vh; overflow-y: auto;` cause the print renderer to print only the visible viewport window, clipping bottom totals and signatures. Wrap the card in a print layer that resets to `position: static !important; overflow: visible !important; height: auto !important;` under `@media print`.
   - Add `page-break-inside: avoid;` to `.invoice-table tr`, `.invoice-header`, and `.invoice-summary-box` to prevent rows from splitting across page breaks.
4. Invert dark-mode backgrounds to clean black-on-white (`background: #ffffff !important; color: #000000 !important; border: none;`) and hide action buttons (`.no-print { display: none !important; }`) for clean PDF and A4 printer rendering.
5. **Logo and Emblem Print Inversion:** On dark-mode sites where logos use `filter: invert(1)` or white SVGs, generate or force a dedicated solid black asset in print styles (`content: url("../assets/images/logo_black.png") !important; filter: none !important;`) so emblems render crisp and dark without fuzzy browser inversion artifacts.
6. **Coupon & Discount Presentation:** Include explicit rows for applied coupon codes, discount percentages, and deducted amounts alongside final payable totals to maintain financial clarity on paper.

## Unified Multipart Uploads in API Client Wrappers

**Pitfall:** Writing ad-hoc `fetch(uploadUrl, { method: 'POST', body: formData })` directly in individual form handlers across multiple admin pages leads to token desynchronization, hardcoded host errors, and `Content-Type` header bugs (manually setting `headers['Content-Type'] = 'multipart/form-data'` strips the browser's necessary `boundary` string).

**Solution:** Centralize file uploads directly in the shared API wrapper (`api.js`):
```javascript
const api = {
    async upload(file, applyWatermark = false) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('apply_watermark', applyWatermark ? 'true' : 'false');

        const token = this.getToken();
        const headers = {};
        if (token) headers['Authorization'] = `Bearer ${token}`;

        // Do NOT set Content-Type header manually; let fetch calculate boundary
        const response = await fetch(`${API_URL}/upload`, {
            method: 'POST',
            headers,
            body: formData
        });

        const data = await response.json();
        if (!response.ok) throw new Error(data.detail || 'Upload failed');
        return data;
    }
};
```

## Admin Entity Quick-Pickers for Dynamic Parameterized Deep Links

**Pattern:** When non-technical admin users configure hero banners, promotional carousels, or announcements, requiring them to manually know and type exact deep links (e.g. `shop.html?category=anime-hoodies` or `product.html?id=12`) results in broken links or user confusion.
- Provide auto-populated quick dropdowns (`<select>`) beside the URL input that fetch `/api/categories` and `/api/products` during admin panel initialization.
- On `<select>` change, automatically populate the text input with the formatted URI.
- Allow manual editing if the user wants custom query parameters or anchor hashes (`guide.html#sizes`).
- **Add a live filter box** above the dropdowns (`oninput` handler filtering cached name/slug/title arrays client-side) once the entity list grows — dropdown-only pickers become unusable past ~10 items. Style the multi-option `<select size="N">` lists with a thin custom scrollbar (5px brand-colored thumb) instead of the chunky default.

## E-Commerce Variant Matrix Generation & Slider Card Clipping

**Patterns for Product Editing & Dynamic UI Cards:**
1. **Multi-Color Variant Matrix Generation:** When admin users define or edit a product's color palette (via color picker or badge presets), the frontend submit handler must automatically generate the Cartesian product of available sizes and selected colors (`sizes x colors`) into valid `ProductVariant` records. If colors are omitted, fall back to a single `Default` or `Free` variant to prevent empty variant arrays from breaking the cart/checkout flow.
2. **Color Field Normalization & Modal Hydration:** When opening a product edit modal, fetch fresh data and sanitize the color inputs: filter out placeholder values (`'Default'`, `'پیش‌فرض'`), display only active color names in the comma-separated input, and reset temporary color picker inputs to prevent stale color values from bleeding into subsequent edits.
3. **Cross-Variant Size/Color Selection Logic:** On product detail pages with separate size and color selectors, state management should track both `selectedProductSize` and `selectedProductColor` independently. When a customer picks a color, automatically find the variant matching that color and the currently active size (or update the active size to match available stock), avoiding desynchronization where selecting a color accidentally resets or ignores size choices.
4. **Card Corner Clipping & Hover Elevation in Sliders / Carousels:** When creating carousel or slider cards (e.g. category cards or product cards) with rounded corners (`border-radius: 16px`), applying `border-radius` only to the outer card is insufficient:
   - Ensure `overflow: hidden; border-radius: inherit;` on inner child elements (`<a>`, `<img>`, and gradient content overlays) to prevent square image corners and backdrop gradients from bleeding outside rounded boundaries.
   - When slider cards have hover elevations (`translateY(-4px)` or `box-shadow` glows), an `overflow: hidden` parent track will clip the upper border and shadow on hover. Provide compensating vertical padding and negative margins (`padding: 10px 0; margin: -10px 0;`) on the outer wrapper so cards elevate smoothly without getting clipped at container boundaries.
5. **Synchronized Dropdowns Across Multi-Entity Admin Panels:** When creating, updating, or deleting auxiliary entities (such as collections/categories), always invoke the dropdown population helper (`loadAdminCategories()`) across all active forms (both "Create Product" and "Edit Product" modals). Additionally, call `loadAdminCategories()` whenever any entity edit modal opens to guarantee newly added categories appear in select dropdowns immediately without requiring a full page refresh.

## Full-Stack Uploads & Pydantic Nested Model Polymorphism

**Pitfalls:**
1. **Frontend API URL construction for Multipart Uploads:** Avoid ad-hoc path replacements like `API_URL.replace('/api', '')`. Use standard template literals `${API_URL}/upload` so port/host changes remain unified across both regular JSON requests and `FormData` uploads.
2. **Polymorphic Nested Lists in FastAPI Endpoints:** When an endpoint accepts structured payloads containing nested models (e.g. `images: List[Union[ProductImageCreate, dict, str]]`), incoming data may arrive as either Pydantic models, raw dicts, or strings depending on whether it came from a web form or another internal service. Always extract URLs defensively:
   ```python
   for idx, img_item in enumerate(product_in.images):
       if isinstance(img_item, dict):
           raw_url = img_item.get('url', '')
       elif hasattr(img_item, 'url'):
           raw_url = img_item.url
       else:
           raw_url = str(img_item)
       if hasattr(raw_url, 'url'):
           raw_url = raw_url.url
       # Persist ORM instance cleanly
   ```

## Browser-Driven End-to-End Verification

**Rule:** When complex interactions span JWT cookies/localStorage, multi-step modals, print stylesheets, and dynamic DOM rendering, always run a headless browser probe (`browser_exec` / `drive_preview`) to physically exercise the UI (log in, submit forms, read computed styles, and inspect rendered counts) before declaring the task verified. Unit tests and `curl` only prove the HTTP layer, not DOM reactivity.

## JWT Authentication & Frontend Role Sync

**Pitfall:** Login endpoints in FastAPI/Node often return only `{ access_token, token_type }` while frontend logic expects `user` or role flags (e.g. `is_admin`) in the same payload. If Pydantic schemas lack `from_attributes = True` or the frontend expects `data.user`, the role is lost and admin dashboards fail to render or redirect prematurely.

**Solution & Pattern:**
1. In Pydantic response models, ensure ORM models can serialize nested user objects:
   ```python
   class Token(BaseModel):
       access_token: str
       token_type: str
       user: Optional[UserResponse] = None
       class Config:
           from_attributes = True
   ```
2. In the frontend authentication client (`auth.js`), immediately fetch the authenticated user profile via `/auth/me` upon receiving a valid token, and persist it to `localStorage` before routing to protected pages (`account.html`).
3. Always verify script loading order in HTML dashboards (`api.js` -> `auth.js` -> `ui.js` -> `app.js` -> feature modules) to avoid `undefined` reference errors during session initialization.

## E-Commerce Admin Batch Operations & Order State Management

**Patterns for high-converting store backends:**
- **Batch Product Actions:** Provide multi-select checkboxes on inventory tables. When items are checked, reveal a sticky toolbar allowing batch price overrides (`PUT /api/products/{id}`) and batch category/collection reassignments in a single round.
- **Pending Order User Controls:** If an order status is `pending` (under review), allow customers to update their shipping address or cancel the order directly from their account dashboard before fulfillment begins.
- **Dynamic Search Hot Tags:** Allow administrators to curate real-time search suggestions/tags from the admin panel without redeploying code, storing them either in local storage cache or via an API endpoint.
- **Custom Branded Order Identifiers vs Sequential IDs:** Sequential database IDs (`#1`, `#2`) expose store order volume and look unprofessional. Generate structured branded random order codes (e.g. `VOID-84729`) in the backend or schema to maintain enterprise prestige and privacy across customer accounts, admin panels, and printable invoices.
- **Accurate Sales & Order Analytics:** When querying dashboard metrics (total revenue, completed order count), always filter out cancelled or failed orders across all language variants (`~Order.status.in_(["cancelled", "لغو شده", "canceled"])`) so metrics reflect actual net sales rather than gross unfulfilled attempts.
- **Universal Product Deep Links Across UI:** Ensure product cards, search results, flyout cart/wishlist items, and historical order details/receipt modal item rows wrap both the thumbnail image and the product title in active links (`<a href="product.html?id=...">`) for seamless navigation back to the product page from anywhere.
- **Unified Address & Validation Experience:** Keep postal address modals (e.g., in user account panels) strictly synchronized with checkout address forms in terms of interactive province pickers and strict validations (e.g., 11-digit mobile, 10-digit postal code).
- **Consistent Branded Order Numbers in Dialogs & Toasts:** When adopting branded order codes (`VOID-XXXXX`), ensure all customer notifications, toast alerts, cancellation prompts (`آیا از لغو سفارش VOID-XXXXX اطمینان دارید؟`), and archive feedback use the formatted code consistently instead of leaking raw database IDs (`#9`).
- **Mobile Admin Navigation:** Convert vertical admin sidebar menus to horizontal scrollable segmented pill bars (`white-space: nowrap; overflow-x: auto`) on mobile to preserve vertical screen space and keep all management panels instantly accessible.
- **Checkout Saved Addresses Selector:** On the checkout page, query the user's saved addresses (`/api/users/addresses`) and present them as interactive radio cards with title and default badges. This allows one-click address selection without retyping, while offering an optional "Add new address" button.
- **Drawer Product Deep Links:** In interactive cart and wishlist flyout drawers, always wrap product images and titles in active links (`<a href="product.html?id=...">`) so customers can easily navigate back to the product details page.

## E-Commerce Checkout Resilience & Order Payload Synchronization

**Pitfall 1 — Server-Side Cart Race Conditions:** Relying solely on server-side cart database state during order creation (`POST /orders`) causes silent failures or "Cart is empty" (HTTP 400) errors if asynchronous client-to-server cart sync calls lag or fail due to network hiccups. The customer sees a success animation or redirection, but the order is never written to the database or reflected in their account history.

**Pitfall 2 — Local Cart Item ID vs Product ID Mismatch:** In local cart architectures (e.g. `localStorage`), cart items often generate a unique client-side timestamp/UUID identifier (`item.id = Date.now()`). Sending `item.id` as `product_id` to the order API causes foreign key / product lookup failures in the backend, leading to empty or unlinked order items.

**Pitfall 3 — Discount Unit Mismatch & Zero Total Invoices:** If store currency is stored in unit scales (e.g. `990` for 990,000 Tomans) while discounts are typed or calculated in full nominal currency (`50000` or `50,000,000`), the discount drastically exceeds the order total, zeroing out invoice totals and corrupting financial records.

**Solution & Pattern:**
1. **Direct Payload Acceptance in Order Creation:** Allow the order creation schema (`OrderCreate`) to optionally receive the full item list directly (`items: Optional[List[OrderItemCreate]] = []`).
2. **Defensive Processing on Backend:**
   ```python
   # 1. Process direct items if supplied by the checkout request
   if order_in.items and len(order_in.items) > 0:
       for it in order_in.items:
           prod = db.query(Product).filter(Product.id == it.product_id).first()
           if prod:
               items_to_process.append({
                   "product_id": prod.id,
                   "variant_id": it.variant_id,
                   "quantity": it.quantity,
                   "price": prod.price
               })
   # 2. Otherwise fall back to server-side session/cart database items
   elif cart and cart.items:
       ...
   ```
3. **Explicit ID Mapping on Frontend:**
   ```javascript
   const formattedItems = cartData.items.map(item => ({
       product_id: parseInt(item.product_id || item.product?.id || item.id),
       variant_id: item.variant_id ? parseInt(item.variant_id) : null,
       quantity: parseInt(item.quantity || 1),
       price: parseFloat(item.price || item.product?.price || 0)
   }));
   ```
4. **Guaranteed Persistence & Feedback:** On the client side, send the formatted items snapshot directly with the checkout request. If the backend returns an error, catch it immediately, keep the submit button active, and display the exact server error message instead of clearing the local cart prematurely.

## Lightweight Security Scanning Without Docker

**When to use:** Docker is unavailable, Strix/nuclei can't install, or you need a quick audit with minimal bandwidth.

**Approach:** A single-file Python script using only `requests` (no extra deps) that checks:
1. **Security headers** — HSTS, CSP, X-Frame-Options, X-Content-Type-Options, Referrer-Policy, Permissions-Policy, COOP, CORP
2. **Info leaks** — Server/X-Powered-By headers, exposed .env/.git/config/package.json paths
3. **Cookie security** — Missing Secure/HttpOnly/SameSite flags
4. **TLS** — Version, cipher, cert expiry, SANs
5. **HTTP methods** — Dangerous TRACE/DELETE/PUT allowed
6. **CORS** — Wildcard or reflected arbitrary origin
7. **Open redirect** — Common param names (next, url, redirect, return)
8. **Rate limiting** — Rapid-fire requests to check 429 response

**Bandwidth:** ~50 small HTTP requests total. No large downloads, no Docker pull.

**Key pitfall:** On Windows behind a proxy, `curl` to GitHub/strix.ai may fail with SSL errors or corrupt downloads. Use the local proxy explicitly (`https_proxy=http://127.0.0.1:10808`) or skip to the Python-based approach. Docker Desktop may not be installed — check `docker info` before assuming it's available.

**Output:** JSON report + human-readable summary with severity ratings (critical/high/medium/low/info). Save to project directory for reference.

**Limitations vs Strix/nuclei:** This only does passive/semi-active checks (no actual exploitation, no PoC generation, no SAST/DAST). For real pentesting, Docker + Strix is the proper tool — this is a triage-level first pass.

## Autonomous Execution — Do Not Delegate Manual Steps

**Rule:** When the user provides credentials (API tokens, keys), execute everything autonomously via API/CLI. Do NOT explain steps for the user to do manually ("go to settings, click X, paste Y"). The user expects the agent to handle it end-to-end.

**Pattern:** If one path is blocked (proxy blocks API, token lacks scope), immediately try the next:
1. Direct API → 2. CLI tool → 3. Browser automation → 4. GitHub Actions as deployment proxy.

**Networking/SSL Fallback:** When calling the GitHub API locally (e.g. enabling GitHub Pages via `curl` or Python `urllib`), Windows SSL/Proxy setups might cause timeout errors (`WinError 10060`, `SSL handshake failed`). If this happens, DO NOT loop retries with different proxy strings. Instead, cleanly catch the error, acknowledge the network block, and provide the exact manual GUI URL (e.g. `https://github.com/user/repo/settings/pages`) so the user can click it to finish the task. Do not endlessly debug the proxy.

Never stop at "here's what you should do" when you have the tools to do it yourself.

## Pydantic Response Serialization for Relational Entities

**Pitfall:** In FastAPI endpoints returning collections of models with nested relationships (e.g., `Order` -> `OrderItem` -> `Product`), if the Pydantic schema declares `product: ProductResponse` strictly without `Optional`, any deleted product or null foreign relationship in the database triggers an unhandled `fastapi.exceptions.ResponseValidationError: model_attributes_type Input should be a valid dictionary or object to extract fields from, input: None`.

**Rule:** Always declare nested relationship models as optional with default `None`:
```python
class OrderItemResponse(BaseModel):
    id: int
    product_id: int
    variant_id: Optional[int] = None
    quantity: int
    price_at_purchase: float
    product: Optional[ProductResponse] = None
    variant: Optional[ProductVariantResponse] = None

    class Config:
        from_attributes = True
```

## FastAPI Interactive API Documentation Theming (/docs)

**Pitfall:** Attempting to force a custom dark theme onto standard Swagger UI (`/docs`) by injecting ad-hoc CSS overrides often leads to broken contrast ratios, unreadable white-on-white text, and light/dark theme clashes across nested schema accordions.

**Solution:**
1. **Native Light Theme:** Standard Swagger UI is natively optimized for high-contrast light backgrounds. When custom theming Swagger UI, keep the main container light/white with crisp borders, and apply brand colors (`--primary: #E26F6F`) cleanly to method badges, execute buttons, and headers without overriding inner table/input text colors.
2. **Alternative for Dark-First Apps:** If strict dark mode is necessary for `/docs`, serve Redoc (`redoc.standalone.js`) with a structured JSON theme configuration (`colors.primary`, `sidebar.backgroundColor`, `rightPanel.backgroundColor`, `typography.fontFamily`) which natively handles dark-mode tokenization with zero CSS leakage.

## FastAPI Router Prefixes & Frontend 'Failed to fetch' Debugging

**Pitfall 1 — Nested Router Prefix Duplication:** When submodules declare router prefixes (e.g., `router = APIRouter(prefix="/products")` in `products.py`) and `main.py` registers them with `app.include_router(products.router, prefix="/api/products")`, the resulting endpoint becomes `/api/products/products`.
- Frontend calls to `/api/products/{id}` fail with `405 Method Not Allowed` or `404 Not Found`.
- Browsers report this as `Failed to fetch` in client JS try/catch blocks.

**Pitfall 2 — SQLAlchemy Constructor Kwarg Mismatch:** If an update endpoint constructs ORM model instances (e.g. `ProductVariant(color_code=...)`) with fields that exist only in Pydantic schemas but not on the SQLAlchemy model, Python raises `TypeError: 'color_code' is an invalid keyword argument`, crashing the endpoint with HTTP 500.

**Rules & Diagnostics:**
1. In `main.py`, mount sub-routers with a unified base prefix `app.include_router(products.router, prefix="/api")` if sub-routers already define their resource prefix.
2. Verify effective routes deterministically:
   ```python
   for r in app.routes:
       print(getattr(r, 'path', r), getattr(r, 'methods', ''))
   ```
3. Dynamically anchor frontend `API_URL` to the current host origin:
   ```javascript
   const API_URL = (typeof window !== 'undefined' && window.location.origin)
       ? `${window.location.origin}/api`
       : 'http://127.0.0.1:8000/api';
   ```
4. In multi-image product editors, allow explicit manual selection of `is_featured` rather than auto-promoting the first uploaded image index.

## Full-Stack Global Color Rebranding (SVGs, CSS Variables & URL-Encoded Gradients)

**Pitfall:** When re-theming or softening an accent color across an entire frontend, replacing only CSS root variables (like `--color-accent`) leaves stale colors in:
1. Static SVG files (`fill="#ff0055"`, `stroke="#ff0055"`, `<stop-color="#ff0055">`).
2. CSS `background-image` data URLs (`fill='%23ff0055'`).
3. JavaScript animation/slider offsets (e.g. `.fx-misc-segmented-slider`).
4. Inline SVG vectors inside icons or buttons.

**Rule:** Perform an exhaustive multi-format search and replacement across all `.css`, `.html`, `.js`, and `.svg` files, checking both raw hex (`#E26F6F`), URL-encoded hex (`%23E26F6F`), and RGB/RGBA channel values.

## Adaptive Luminance-Based Watermarking on Media Uploads (PIL/Pillow)

**Pitfall:** Applying a static white or static black watermark/emblem to user-uploaded images leads to invisible or muddy watermarks when the background matches the watermark color (e.g., white watermark on white canvas, or black watermark on dark streetwear photos).

**Pattern & Solution:**
1. Crop the target bounding box where the watermark will be placed (e.g., bottom-left corner with margin).
2. Compute the local average luminance ($0-255$) of that specific bounding region using grayscale conversion and histogram averaging:
   ```python
   def calculate_region_brightness(img, box):
       region = img.crop(box).convert("L")
       hist = region.histogram()
       total_pixels = sum(hist)
       if total_pixels == 0:
           return 128
       return sum(i * count for i, count in enumerate(hist)) / total_pixels
   ```
3. If `avg_brightness > 128` (bright/light background), composite the **solid black emblem asset** (`logo_black.png`).
4. If `avg_brightness <= 128` (dark background), composite the **pure radiant white emblem asset** (`logo_white.png`).
5. This guarantees maximum contrast, legibility, and brand prestige across all photo aesthetics.

## Localized Hex-to-Name Color Parsing & Accessible Swatch Circles

**Pitfall:** When product variants store raw hex strings (e.g. `#000000, #ffffff`) or combination strings (e.g. `مشکی (#000000)`), naive renderers often fail in two ways:
1. They display raw unformatted hex codes `#000000` to the customer in order summaries, receipts, and invoices instead of human-friendly names (e.g. "مشکی").
2. On dark-mode UI, black color swatch circles (`#000000`) vanish into dark card backgrounds without a subtle contrasting border and inner glow.

**Rules:**
1. **Dual-Channel Color Resolvers:** Implement two distinct helper functions in client JS:
   - `getColorHex(val)`: Extract or map to a valid CSS `#hex` string for visual swatch backgrounds (`style="background-color: ${getColorHex(color)}"`).
   - `getColorDisplayName(val)`: Translate direct hex codes (`#000000` -> "مشکی", `#ffffff` -> "سفید") or strip parenthetical codes for textual display across cart drawers, checkout sidebars, order receipts, and invoice tables.
2. **Swatch Circle Styling in Dark Mode:** Always provide swatches with a `1px` to `2px` semi-transparent border (`border: 2px solid rgba(255, 255, 255, 0.2); box-shadow: inset 0 0 4px rgba(0,0,0,0.5);`) and an active ring outline in the brand accent color (`--color-accent`). This ensures both pure white and pitch black fabrics remain distinct.
3. **Reactive Selection Labels:** Update the text label next to the option title (`رنگ‌بندی پارچه: [نام رنگ]`) reactively whenever a user clicks any swatch dot.

## Stale Server Process Serving Old Routes (405/404 That "Should" Work)

**Pitfall:** After adding new backend routes (e.g. a new `banners.py` router), the client keeps getting `405 Method Not Allowed` even though the code on disk clearly registers the route. Re-reading the code finds nothing wrong — because nothing IS wrong with the code. The running uvicorn/gunicorn process was started BEFORE the routes were added and is serving stale code (`reload=False` never picks up changes).

**Diagnosis — check the LIVE server, not the disk:**
```bash
# What routes does the RUNNING server actually have?
curl -s http://127.0.0.1:8000/openapi.json | python -c "import json,sys; print([f'{m.upper()} {p}' for p,ops in json.load(sys.stdin)['paths'].items() for m in ops])"
```
If the expected route is missing from this output, the code is fine — the process is stale.

**Fix:** find the listening PID (`netstat -ano | grep :8000 | grep LISTENING`), `taskkill /PID <pid> /F` (Windows; note MSYS bash needs `taskkill /PID x /F` — the `//PID` form fails), restart the server, re-verify via `/openapi.json` before testing the endpoint again.

**Rule:** When an HTTP error contradicts the code on disk, verify the running process's actual route table first. Editing code that is already correct wastes cycles.

## Don't Over-Apply Style Changes to Nested Components

**Pitfall (user correction):** When asked to remove "the glass boxes around the header", the agent stripped background/border/radius from the outer header shell AND the nested nav pill (`.fx-misc-segmented`) AND the icon buttons. The user then complained the navbar "lost its border radius and looks bad" — they wanted only the outermost container decluttered, with the inner controls keeping their glass/radius identity.

**Rule:** Scope de-chroming requests to the specific surface named. When a request targets a container ("around the header"), change that container only; leave nested interactive components (nav pills, icon buttons, segmented controls) untouched. If uncertain which elements are in scope, list the affected selectors in the reply so the user can veto before the next turn — or revert immediately and completely (as they expect) when told it regressed.

## Decoupled Payment Gateway Callbacks & Result Pages

**Pattern:** When integrating online payment gateways (e.g. Shaparak / ZarinPal / Stripe / PayPal):
1. **Dedicated Callback Handler (`payment-callback.html`):** Provide a standalone, beautifully styled result page that parses query parameters (`status=success|failed`, `order_number`, `ref_id`, `amount`, `track_id`).
2. **State Differentiation:**
   - **Success State:** Display a vibrant success badge/icon, the branded order reference (`VOID-XXXXX`), transaction tracking code (`TRX-XXXXXX`), formatted payable amount, and direct CTA to view the order in the user account panel.
   - **Failure/Cancel State:** Display an unmistakable warning badge/icon, clear reassurance that no funds were deducted, and a one-click "Retry Payment" CTA redirecting back to `checkout.html`.
3. **Cart & Discount Clearance:** Clear transient discount keys and local cart data only after an order is successfully registered or confirmed by the backend to prevent cart abandonment loss during momentary payment failures.

## Theme Implementation and Decoupled Layouts

**Pitfall:** Designing dark/light themes via custom CSS overrides (e.g. `[data-theme="light"]`) often results in inconsistent, broken layout variables, bad readability, and broken contrast ratios.

**Rule:** Unless explicitly requested to support dark/light toggles, design websites **strictly with a dark-first aesthetic**. If a light theme is developed and later requested to be removed:
1. Revert to a single-theme structure utilizing clean variable tokens.
2. Remove any theme-toggling buttons and state management logic (`localStorage` listeners, script event listeners) to keep the codebase lightweight and maintainable.
3. Keep layout structure decoupled from coloring rules to prevent layouts from breaking when themes or colors are modified.
4. **Clean reversion workflow:** When rolling back theme modifications, restore the CSS completely from a clean git commit reference (`git show <commit-hash>:style.css > style.css`) instead of manual patch-by-patch deletion to prevent residue styling conflicts. Keep native styling and original category colors intact.

## Core Web Vitals (CWV): Asynchronous CSS Loading vs Desktop Layout Shift (CLS)

**Pitfall:** Deferring CSS using the async pattern (`media="print" onload="this.media='all'"`) to eliminate mobile render-blocking requests will catastrophically break desktop Performance (dropping scores from 95+ to the 60s) if the deferred stylesheet contains above-the-fold layout containers (such as hero sliders, banners, or video modules).
- At paint time (millisecond 0), an unstyled container (e.g. `.sr7-module`) computes to `height: 0`.
- When the stylesheet loads 150–300ms later, the container abruptly expands to its full aspect-ratio height (e.g. 600px).
- This shifts all content below it downward, triggering massive Cumulative Layout Shift (`CLS > 0.45` on desktop) while mobile may pass unnoticed.

**Rules for Zero-CLS Performance Optimization:**
1. **Never Defer Above-the-Fold Geometry:** Include structural dimensions for hero modules (`aspect-ratio: 16 / 9; min-height: 200px; max-height: 820px; width: 100%; overflow: hidden; background: #08080c;`) in the synchronous core CSS bundle, or lock them directly via inline styles on the HTML element.
2. **Combine Core Stylesheets & Inline Critical CSS for Mobile 90+:** Rather than serving 7–9 separate CSS files (`reset.css`, `base.css`, `variables.css`, `layout.css`, `responsive.css`), concatenate and minify them into a single `core.css` (~10KB gzipped). For maximum mobile Lighthouse scores, inline this core bundle directly into `<head>` inside `<style id="critical-css">` and pair with `<link rel="prefetch" href="css/core.css" as="style">`. Gzip compression makes the HTML payload increase by only ~10 KB, fitting inside the initial TCP window and eliminating 100% of render-blocking stylesheet latency.
3. **CRITICAL Relative Path Pitfall When Inlining CSS:** When moving CSS rules from `css/core.css` to an inline `<style>` tag in the site root's `index.html`, any relative paths like `url('../assets/fonts/...')` or `url('../images/...')` must be rewritten to `url('assets/...')`. Inlined styles resolve relative to the HTML document location, so `../` escapes above the web root and causes 404 font errors.
4. **Font Preload Bandwidth Contention on Mobile:** Preloading 4+ web fonts simultaneously consumes ~180 KB of bandwidth, competing with the Largest Contentful Paint (LCP) image on throttled mobile connections. Preload ONLY the 1–2 critical bold weights used in above-the-fold headers and titles; allow regular body fonts to load on demand.
5. **Reserve Dynamic API Containers (Skeletons & Static Pre-renders):** When carousels/sliders (e.g. `#home-featured-categories-slider`) start empty in HTML and populate via JS `fetch()`, their expansion pushes sibling sections down (`CLS ~ 0.15`). Pre-render initial cards or skeletons directly in raw HTML with explicit aspect-ratio and heights so layout geometry is 100% stable before JavaScript executes.
6. **GPU-Composited Shimmer Animations:** Avoid animating `background-position` or `background-position-x` on `.skeleton` placeholders (which causes main-thread repaint and triggers Lighthouse's "Avoid non-composited animations" penalty). Use GPU-composited `opacity` pulsing (`@keyframes { 0%, 100% { opacity: 0.8; } 50% { opacity: 0.3; } } will-change: opacity;`).
7. **Preload LCP Image Candidates:** For client-rendered carousels where the primary LCP candidate is injected by JS, add `<link rel="preload" as="image" href="..." fetchpriority="high" type="image/webp">` in `<head>` to eliminate the 3-second discovery delay on mobile 4G.

## Chrome Extension Development & Unpacked Deployment Pitfalls

**Pitfall 1 — Reserved Underscore Names (`__pycache__`):**
Chrome strictly prohibits loading unpacked extensions that contain any file or folder starting with an underscore (except `_locales`):
`Cannot load extension with file or directory name __pycache__. Filenames starting with "_" are reserved for use by the system.`
- If an extension uses or is paired with a local Python companion/daemon/test script, **never place or run Python scripts inside the unpacked extension directory**. Running Python generates `__pycache__`, instantly breaking Chrome's `Load unpacked`.
- If Python must run nearby, set `PYTHONDONTWRITEBYTECODE=1` / `sys.dont_write_bytecode = True`, or cleanly separate into distinct sibling directories:
  ```
  project/
    browser-extension/   <-- pure web files only (manifest.json at root, html, js, css, icons)
    backend-core/        <-- python, daemons, binaries, helpers
  ```

**Pitfall 2 — Manifest Location vs User Folder Selection:**
When instructing users to load an unpacked extension via `chrome://extensions`, users always select the exact root folder path provided to them. If `manifest.json` is nested in a subfolder (e.g. `project/extension/manifest.json`), Chrome immediately throws:
`Manifest file is missing or unreadable. Could not load manifest.`
- Always ensure `manifest.json` sits at the exact top-level root of the directory intended for `Load unpacked`.

**Pitfall 3 — Browser Extension Sandbox vs Raw Network Protocols (V2Ray / Reality):**
- In Manifest V3, JavaScript inside browser extensions has zero raw TCP/UDP socket access and cannot forge raw TLS handshakes (uTLS / Reality) or customize low-level packet headers to bypass deep packet inspection (DPI).
- `chrome.proxy.settings` only supports standard proxy schemes (`http`, `https`, `socks4`, `socks5`).
- **Working Architecture:** Pair the extension with a lightweight local core (e.g. `xray.exe` on mixed port `127.0.0.1:20808`), controlled via a local REST daemon (`127.0.0.1:28888`). The extension manages `chrome.proxy.settings`, parses client links (`vless://`, `vmess://`, `trojan://`, `ss://`), and commands the local daemon to reload the core on the fly.
- **Smart Routing (Bypass Domestic Traffic):** Always supply an explicit `bypassList` in `chrome.proxy.settings` (`["<local>", "*.ir", ...]` and local CIDRs) to keep domestic sites and payment portals direct, fast, and unblocked while routing foreign traffic through the tunnel.

**Pitfall 4 — Localized Typography in Offline / Extension Contexts:**
Never link Google Fonts or external CDNs in browser extensions intended for circumvention or offline use. If the proxy is disconnected or DNS is poisoned, CDN font requests fail silently, breaking Persian/Arabic typography. Always bundle local `.ttf` / `.woff2` font files (e.g., `Vazirmatn-Regular.ttf`, `Vazirmatn-Bold.ttf`) directly inside an extension's `fonts/` directory and declare `@font-face` with local relative paths and explicit font weights.

**Pitfall 5 — WebRTC IP Leaks Bypassing Chrome Extension Proxies:**
By default, browsers execute WebRTC STUN/TURN queries over all network adapters (including local Wi-Fi/cellular adapters), bypassing `chrome.proxy.settings` and leaking the user's real public and local IP to websites even when the proxy is active.
- **Fix:** Add `"privacy"` to `permissions` in `manifest.json`.
- In the background service worker:
  ```javascript
  // When proxy turns ON:
  chrome.privacy.network.webRTCIPHandlingPolicy.set({
    value: "disable_non_proxied_udp"
  });

  // When proxy turns OFF:
  chrome.privacy.network.webRTCIPHandlingPolicy.clear({});
  ```
  This forces all WebRTC traffic through the configured proxy or blocks direct UDP packets, ensuring complete IP anonymity.

**Pattern — High-Performance Multi-Server Ping & Auto-Fastest Selection:**
Testing full HTTP egress through a tunnel sequentially is too slow (taking 1–2 seconds per server). To test 20–50 configs simultaneously in a browser UI:
1. Provide a parallel TCP handshake endpoint on the local companion daemon (`/api/ping_all`) using Python `concurrent.futures.ThreadPoolExecutor(max_workers=12)`:
   ```python
   def tcp_ping(host, port, timeout=2.5):
       t0 = time.time()
       try:
           s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
           s.settimeout(timeout)
           s.connect((host, int(port)))
           latency = int((time.time() - t0) * 1000)
           s.close()
           return latency
       except Exception:
           return -1
   ```
2. The browser popup sends all candidate `{ id, address, port }` objects in a single batch POST.
3. All servers are evaluated concurrently in ~200ms total.
4. The client updates UI badges instantly (`< 350ms` fast green, `350–800ms` medium yellow, `> 800ms` slow red) and can automatically activate the lowest-latency node with one click.
5. Combine with `tabular-nums` on latency badges to prevent text jitter during live refreshes, and track mouse coordinates (`--x`, `--y`) on hero cards to render dynamic VibeFarsi / Aceternity `BorderBeam` and `Spotlight` effects.
