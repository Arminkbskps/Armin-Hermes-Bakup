# Home Featured-Categories Slider — robust pattern (session 2026-09-11)

RTL slider on `index.html`: `#home-categories-viewport` > `#home-featured-categories-slider.home-categories-track` + `#home-categories-progress-bar` + `#home-cat-prev-btn` / `#home-cat-next-btn`.

## Bugs found (all in `js/app.js` + `index.html` + `css/responsive.css`)
1. `homeCategoriesPerView` referenced WITHOUT `()` in 3 places (`updateHomeCategorySliderPosition`, `slideFeaturedCategories` guard + `maxIdx`) → number-vs-function comparison is always false/NaN, arrows dead. Fix: always call `homeCategoriesPerView()`.
2. No progress-bar element existed in `index.html` although CSS (`.home-slider-progress`) and JS (`updateHomeCategoryProgress`) expected `#home-categories-progress-bar`. Fix: add exactly ONE `<div class="home-slider-progress"><div class="home-slider-progress-bar" id="home-categories-progress-bar"></div></div>` below the viewport; dedupe if a parallel edit inserts a second copy (duplicate IDs).
3. Cards rendered with inline `style="flex: 0 0 calc(33.333% - 14px)"` — correct on desktop, broken on phones (`perView=1`). Fix: render `<div class="category-card home-cat-card">` with NO inline flex; size via CSS: `.home-categories-track .home-cat-card { flex: 0 0 calc(33.333% - 14px); min-width: 260px; height: 380px }` + phone override `flex: 0 0 82% !important; height: 210px !important`.
4. Swipe was touch-only (`touchstart`/`touchend`, `passive:true`) with no mouse drag and no `touchmove` lock. Fix: `setupHomeCategorySwipe()` handles touch (with `touchmove` `{passive:false}` + horizontal-lock so vertical page scroll still works) AND desktop `mousedown`/`mousemove`/`mouseup` drag; `touch-action: pan-y; cursor: grab` on the viewport, `.dragging` class kills track transition mid-drag.
5. Position used percentage `translateX(idx * 35%)` — drifts on mobile. Fix: pixel-accurate `homeSliderMetrics()` = first-card width + track gap (`columnGap || gap`), `px = min(idx * step, scrollWidth - clientWidth - 1)`, `translateX(+px)` for RTL. `updateHomeCategorySliderPosition()` clamps idx, sets transform, updates bar width (`(idx+perView)/total`, 100% when all fit), and dims dead-end arrows (`disabled` + `opacity .35` + `cursor not-allowed`). Resize listener debounced (~120ms).

## Verify
- `node --check js/app.js`; bump `?v=` FORWARD on all HTML pages after any slider/CSS change.
- Live: click both arrows to both ends, swipe on a phone (horizontal moves slider, vertical scrolls page), bar fills left→right, single `getElementById('home-categories-progress-bar')` match.
