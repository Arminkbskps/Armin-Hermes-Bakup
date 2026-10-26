# Home New-Arrivals Slider + Shop Sort Modes (session 2026-09-11)

The «جدیدترین تیشرت‌ها و هودی‌ها» home section is a SINGLE-ROW slider of 10
products (not a grid), built by cloning the featured-categories slider pattern
in `references/home-categories-slider.md`. Shop sort gained گران‌ترین/ارزان‌ترین
and `popular` became most-ordered-first.

## Arrivals slider recipe (per frontend copy: root + PROJECT + CLOUD + CPANEL)

1. `index.html`: replace `<div class="product-grid" id="new-arrivals-grid">` with
   viewport + track + progress bar + prev/next arrows in `.home-section-actions`,
   and point the archive link at `shop.html?sort=newest`:
   `home-arrivals-viewport` > `#new-arrivals-grid.home-arrivals-track` +
   `#home-arrivals-progress-bar` + `#home-arrivals-prev-btn/next-btn`
   (`onclick="slideHomeArrivals(∓1)"`).
2. `app.js`: fetch `products.getAll({ sort_by: 'newest', limit: 10 })`,
   `slice(0, 10)`, stash in `window.homeArrivalsList`, render cards as
   `<div class="product-card home-arrival-card">`, then call
   `updateHomeArrivalsSliderPosition()` + `setupHomeArrivalsSwipe()` after
   `grid.innerHTML = html`. Slider helpers mirror the categories ones verbatim
   (metrics / position / `window.slideHomeArrivals` / swipe / resize debounce ~120ms)
   except `homeArrivalsPerView()`: 1 (≤768px) / 2 (769–1024px) / 4 (>1024px).
3. `responsive.css`: the track MUST be flex — grid classes on `#new-arrivals-grid`
   would stack rows instead of sliding:
   `.home-arrivals-track { display:flex; gap:20px; transition: transform ... }`,
   cards `flex: 0 0 calc(25% - 15px); min-width: 0`, tablet
   `calc(50% - 10px) !important`, phone `flex: 0 0 82% !important` (+ gap 14px).
4. `products.js`: `getAll` must forward `limit`/`offset` (`filters.limit`),
   otherwise the `limit: 10` param is silently dropped and the API default
   (200) decides the count.

## Shop sort modes

- Options: `popular` (🔥 محبوب‌ترین) / `newest` (✨ جدیدترین) /
  `expensive` (💎 گران‌ترین‌ها) / `cheapest` (💰 ارزان‌ترین‌ها).
  `limited` (دراپ تولید محدود) was REMOVED per user request — do not re-add
  without asking.
- Backend `popular` = most-ordered-first: subquery
  `COALESCE(SUM(quantity),0) FROM order_items WHERE product_id = products.id`
  DESC, id DESC (FastAPI: outerjoin + group_by with try/except fallback to
  `is_featured` ordering; PHP port: correlated subquery, 0 for never-ordered).
  `expensive` = `price DESC`, `cheapest` = `price ASC`.
- `initShopPage` reads `?sort=` / `?sort_by=` from the URL (whitelist
  `['popular','newest','expensive','cheapest']`, default `popular`),
  pre-selects the matching `.custom-option` + label, and `syncShopSortUrl()`
  keeps `?sort=` in the address bar via `history.replaceState` on change.

## Verify

- `node --check js/app.js`; forward `?v=` bumps (JS + CSS) on all pages.
- Anchor grep in ALL FOUR frontends with matching counts:
  `home-arrivals-track`, `slideHomeArrivals`, `shop.html?sort=newest`,
  `data-value="expensive"`, `data-value="cheapest"`, zero `data-value="limited"`.
- Live: 10 cards, single row, arrows + phone swipe move it, bar fills,
  archive link opens shop pre-sorted newest.
