# Dead-Handler Sweep — Bare Method References Without `()` (VOID CLUB)

**Bug class (seen 2026-09-10, ~25 instances across 4 files):** a method
referenced WITHOUT call parens. Syntactically valid JS — `node --check`
passes, no console error, no lint warning — but the call never happens and
the button/handler is silently dead.

## Instances fixed this session

| Pattern | File(s) | Effect |
|---|---|---|
| `openSearch;` instead of `openSearch();` | `js/ui.js:383`, `js/search-helper-snippet.js:46` | Search button opened nothing on ALL pages |
| `() => searchInput.focus` (no `()`) | `js/ui.js:371`, `js/search-helper-snippet.js:34` | Search input never focused |
| `() => this.closeCart` / `() => this.closeWishlist` | `js/ui.js:292-293,308-309` | Cart/wishlist ✕ + backdrop click never closed |
| `() => toast.remove` | `js/ui.js:60` | Toasts never removed from DOM |
| `str.toLowerCase` / `lower.includes` (no `()`) | `js/app.js` ×~15, `js/sr7-slider.js:52` | `getColorHex` threw `lower.includes is not a function` → `drawProductDetails` fell into `catch` → product page showed «خطا در دریافت مشخصات محصول» **while the API returned 200** |
| `onclick="addCurrentProductToCart"` (no `()`) | `js/app.js:585` (template string) | Product-page add-to-cart button dead |
| `hideError;` | `login.html:403` | Auth tab switch never cleared errors |
| `await loadCheckoutShippingRate;` / `await loadCheckoutBankCard;` (await on a bare reference) | `js/app.js` checkout init | `await` resolves the function OBJECT — loader never runs, checkout totals/cards stale |
| `await fetchAdminCoupons;`, `await loadAdminCategories;` / `await loadAdminProducts;` | `js/enterprise-admin.js`, `js/app.js` | Coupon/category/product admin lists silently never refresh |
| `if (e) e.preventDefault;` / `if (event) event.preventDefault;` | `js/app.js` (banner create, product edit…) | Form submits fall through to native reload instead of AJAX |
| `onclick="toggleArchivedOrdersView"` / `onclick="loadAdminOrders"` / `onclick="handleRejectReceiptSubmit"` (no `()`, inside template strings) | `js/app.js` admin-orders render | Archive toggle, retry, and reject-receipt buttons dead |
| `onclick="...getElementById('...').click"` (no `()`) | `account.html` ×5, `checkout.html` ×1 | All admin file-picker buttons + c2c receipt dropzone dead |
| `?.reset;` / `.reset;` | `js/app.js:3147`, `js/enterprise-admin.js:158` | Banner/coupon forms never clear after submit |
| `value.toUpperCase.trim()` (missing `()` on `toUpperCase`) | `js/enterprise-admin.js:147,359` | Coupon create + checkout coupon apply threw `trim is not a function` |
| `(e) => e.stopPropagation` (no `()`) | `js/app.js` province search | Clicks leaked through the dropdown overlay |
| `box.onclick = (e) => { if (e.target === box) closeReceiptLightbox; }` | `js/app.js` receipt modals | Backdrop click never closed the lightbox/reject modals |

## Sweep commands (run from `D:/Hermes file`)

```bash
# Broad sweep — bare identifiers where a call was intended
grep -rn --include='*.js' -E '\.focus[^(]|\.trim[^(]|\.remove[^(]|hideError[^(]|openSearch[^(]|closeSearch[^(]|closeCart[^(]|closeWishlist[^(]|toLowerCase[^(]|\.includes[^(]' frontend/js/ | grep -vE '\.(focus|trim|remove|includes|toLowerCase)\(|hideError\(\)|openSearch\(\)|closeSearch\(\)|closeCart\(\)|closeWishlist\(\)|removeItem|removeChild|removeEditProductImage|removeProductGalleryImage'
# onclick attributes missing parens ( tríckier — eyeball the hits )
grep -rhoE 'onclick="[a-zA-Z_]+(?=")' frontend/*.html frontend/js/*.js
# Admin-panel round 2 (2026-09-10): awaited bare refs, dead pickers, dead resets
grep -rn --include='*.js' -E 'await [A-Za-z_$][A-Za-z0-9_$.]*\s*;' frontend/js/   # await on a reference, not a call
grep -rn --include='*.js' -E 'onclick="[A-Za-z_]+"' frontend/js/                  # onclick without () inside template strings
grep -rn '\.click"' frontend/*.html                                               # file-picker buttons missing ()
grep -rn --include='*.js' -E '\.reset;|toUpperCase[^()]|preventDefault;|stopPropagation\s*[^()]' frontend/js/
```

False positives to ignore: `removeItem`, `removeChild`,
`removeEditProductImage`, `removeProductGalleryImage` (different method),
`const openSearch = ...` declarations, `addEventListener('click', closeSearch)`
(passing the reference IS correct there).

## Diagnosis rule

When a button "does nothing" but the API is healthy (verified via
`curl` + `products.getById()` succeeding in `browser_exec` while the page
still shows the error state): the failure is INSIDE the render/handler
path, not the fetch path. Re-run the page function manually in
`browser_exec` (`drawProductDetails()`, `initProductDetailPage()`) and read
the thrown error — this session's product-page 404-lookalike was a
`TypeError` in a color helper, never a real 404.
