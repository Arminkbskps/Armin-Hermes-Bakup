# Shop category/collection tree — sidebar + breadcrumb + pills + URL sync (session 2026-09-12)

Pattern for a `shop.html` where backend categories form `Category (parent_id NULL) → Collection (child) → Product (category_id → collection)`, and the sidebar must show parents WITH their child collections, active state derived from the URL.

## Backend contract (already existed — no change needed)

- `GET /api/categories` returns parents each with embedded `children[]`.
- `GET /api/products?category_slug=<slug>` resolves a PARENT slug to parent + all children ids via `vc_resolve_category_ids()` — so a parent page shows ALL sub-collection products with zero frontend fan-out. A child slug matches only itself.
- `product_type` (comma-joined `IN` filter) combines with `AND` — collection + product-type works server-side.

## Frontend single-state architecture (`initShopPage` in `js/app.js`)

- `shopSlugMap`: `slug → { node, parent }` built once from `/api/categories` (parents map to `{node: c, parent: null}`, children to `{node: k, parent: c}`). Unknown URL slug falls back to `''` (all products).
- `renderShopMeta()` — ONE function renders title + breadcrumb + pills + sidebar checked/highlight state, all from `currentCategory`. Never derive active state from CSS alone.
- `setShopCategory(slug, push=true)` — the ONLY category transition: updates `currentCategory`, `pushState`s `?category=`, calls `renderShopMeta()` + `loadShopProducts()`, closes the mobile sheet. Sidebar radios and pills both call it (client-side filtering, no full reload).
- `syncShopFilterUrl(replace=true)` — keeps `category` + `product_type` + `sort` in the URL on type/sort changes via `replaceState`.
- ONE `popstate` listener guarded by `getElementById('shop-products-grid')` re-parses `category/product_type/sort` from the URL and re-renders — Back/Forward and Refresh stay correct.
- Sidebar HTML is fully dynamic (no hardcoded collections): `همه محصولات` radio + per-parent `.filter-parent-group` (parent radio + child radios). New collections appear automatically.

## Breadcrumb + pills markup/CSS (`shop.html` inline `<style>`)

- `<nav id="shop-breadcrumb">`: `خانه / parent / collection` (2 levels on parent pages, hidden on search/all). Home + parent are links; current is `.shop-bc-current` with `max-width:45vw` + ellipsis so phones never overflow. Hidden (`display:none`) until JS fills it.
- `<div id="shop-pills">`: `[همه] [child…]` for the ACTIVE parent only; `overflow-x:auto` + `scrollbar-width:none` for phone horizontal scroll; `.active` = accent bg + glow. Clicks go through `setShopCategory` (pushState, sidebar stays in sync).

## Touch blank-card CSS rule (`components.css`)

See SKILL.md pitfall — hover-swap rules live inside `@media (hover: hover) and (pointer: fine)`, `@media (hover: none)` keeps hiding the stuck 2nd image. Never `opacity: 1 !important`.

## Testing without PHP/browser (no PHP CLI on this box, no network for portable-PHP download)

Node harness recipe that verified 23/23: extract the real block between markers (`let shopCats = [];` … `renderShopMeta();` + `} catch (e) {`) plus the sidebar-template slice, `eval` it in Node with minimal stubs (`document.getElementById`, `window.history.pushState/replaceState` recorders, `window.addEventListener` capturing `popstate`, `loadShopProducts`/`setCategorySheet` counters), fixture categories in API shape, then assert title/breadcrumb/pills/radios/URL/push/popstate. Static asserts cover the CSS guards and mount ids. `node --check` on `app.js` + HTML parse on `shop.html` first.
