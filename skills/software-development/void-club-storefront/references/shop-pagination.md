# Shop Pagination — 20/page, VibeFarsi range logic (session 2026-09-20)

Ships in `VOID_mobile_perf_v6.zip` (only `shop.html` + `js/app.js` differ from v5).

## Why vanilla, not `npx vibefarsi add pagination`

- Registry `https://vibefarsi.ir/r` timed out from this environment (direct + proxy `127.0.0.1:10808` both failed; CLI reported `Cannot reach registry`).
- The pagination algorithm has zero React dependency, so the logic was ported 1:1 from `vibafarsiui/registry/ui/pagination.tsx`:
  `range = [1, total] + current ± siblings + '…' between gaps`, RTL chevrons (prev=right, next=left), Persian digits.

## State (all inside `initShopPage` closure)

- `SHOP_PAGE_SIZE = 20`, `currentPage` (parsed from `?page=`, default 1), `shopAllItems` (full filtered+sorted array).
- Helpers: `shopPageRange(page,total,siblings=1)`, `shopFa(n)` (`toLocaleString('fa-IR')`), `syncShopPageUrl(push)`, `shopGotoPage(p,push)`, `renderShopPage()`, `renderShopPagination()`.

## Flow

1. `loadShopProducts()` fetches everything (unchanged filters/sort, incl. `top` mode), sets `shopAllItems`, clamps `currentPage` to total pages, calls `renderShopPage()`.
2. `renderShopPage()` slices `[(page-1)*20, +20)`, renders the existing card template per item, sets count text:
   multi-page `نمایش X تا Y از Z محصول`, single-page `نمایش Z محصول`, empty → not-found + count ۰ + nav hidden.
3. `renderShopPagination()` fills `nav#shop-pagination` (hidden when ≤1 page) with prev button + range buttons + next button, `.vf-page-btn` classes, `aria-current="page"` on current, click → `shopGotoPage(p, true)` → `pushState ?page=` + smooth-scroll to grid.
4. Resets to page 1 (and drops `?page=`): `setShopCategory`, `syncShopFilterUrl` (type checkboxes), `syncShopSortUrl` (sort dropdown). `popstate` restores `currentPage` from URL.

## Markup/CSS (in `shop.html`)

- Container after `#shop-products-grid`: `<nav class="vf-pagination" id="shop-pagination" aria-label="صفحه‌بندی" style="display:none;"></nav>`.
- `.vf-pagination` / `.vf-page-btn` (+`.active`, `:disabled`, `.nav`, `.vf-page-ellipsis`) styled on VOID glass tokens (`#990000` active, `var(--glass-border)`), phone compaction at ≤768px.
- Grid columns untouched (`#shop-products-grid` 4-col desktop, 2-col tablet/phone) → 20 items = 5 rows desktop / 10 rows mobile.

## Verification

- `node --check js/app.js` clean; range unit checks: `range(1,5)=[1,2,…,5]`, `range(3,5)=[1..5]`, `range(1,1)=[1]`; 100 items → 5 × 20 slices.
- After any touch: bump `js/app.js?v=` forward in `shop.html`.
