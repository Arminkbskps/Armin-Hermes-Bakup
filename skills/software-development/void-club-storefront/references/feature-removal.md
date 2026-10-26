# Full-Feature Removal from the Static cPanel Port

Use when deleting an entire feature (wishlist, quick-add, a drawer, a header button) across all HTML/JS/CSS of `VOID_CLUB_CPANEL/` or a `VOID_mobile_perf_*.zip` working copy. Proven on the v7→v10 wishlist + quick-add removal (2026-09-21, shipped `VOID_mobile_perf_v10.zip`).

## Workflow

1. **Inventory first.** `grep -c` the feature anchors per file and record expected counts (e.g. header button ×1, drawer block ×1, `<script src>` ×1 per HTML; card hearts ×4 + quick-adds ×4 in `js/app.js`; method blocks ×1 each in `js/ui.js`). The counts become the script's assertions.
2. **One Python script, count-checked.** Regex-remove per anchor; assert each substitution count equals the inventory. A `0` means the pattern is wrong — stop and inspect bytes, don't widen the regex blindly.
3. **Residual ban-scan.** After the run, grep a ban-regex over the ship set, excluding `api/` (backend) and `assets/icons/` (font CSS): `wishlist|علاقه|quickadd|quick-add|toggleWishlist|isWishlisted|btn-wish|product-card-wishlist|fa-heart|wishlist\.js|wishlist-drawer|wishlist-badge|wishlist-btn`. Zero matches is acceptance.
4. **Validity + versions.** `node --check` every touched JS (also check backtick/brace balance); bump `?v=` FORWARD on every touched JS/CSS in ALL HTML pages.
5. **Verify inside the zip.** Scan the built zip's namelist + file contents, not just the working dir. Confirm no helper scripts sneaked into the zip.

## Gotchas (all bitten in v7→v10)

- **CRLF line endings.** Files extracted from the ship zips use `\r\n`. Patterns written with `\n` silently match 0. Normalize (`text.replace('\r\n','\n')`) on load, restore each file's original ending on save.
- **Persian ZWNJ (U+200C).** `علاقه‌مندی‌ها` contains invisible non-joiners; literal Persian matching in regex fails. Anchor deletions on ASCII ids/classes (`wishlist-drawer`, `wishlist-btn-toggle`, `product-card-wishlist`, `quickAddProduct`, `toggleWishlistProduct`) and Persian-free structural markers.
- **Marker variance between pages.** `categories.html` had no `<!-- Wishlist Drawer -->` comment — anchor on the element id (`<div ... id="wishlist-drawer-overlay">`) through the next known marker (cart drawer overlay), never on comments alone.
- **Single-space indents.** These files indent JS/HTML bodies with 1 space, not 2 — copy exact bytes from `repr()` output when writing patterns.
- **Zip namelist diff noise.** Reference zips contain bare directory entries (`api/`, `css/`, …); Python-built zips don't. When diffing file lists, ignore entries ending in `/` — a count mismatch there is not a missing file.
- **Leave the backend alone.** `api/api.php` wishlist endpoints were deliberately kept — removing frontend callers is enough, and other callers/admin stay intact.

## What v10 removed (scope reference)

- Header heart button + `wishlist-badge` (8 pages), wishlist drawer block (8 pages), `js/wishlist.js` script tags (8 pages).
- `app.js`: 4 card-heart buttons, 4 quick-add divs, `quickAddProduct()` def, 4 `isWish/wishClass` pairs, detail-page wish button.
- `ui.js`: `openWishlist`/`closeWishlist`/`updateWishlistDrawer`/`toggleWishlistProduct` + header bindings + init call.
- CSS: `.product-card-wishlist` + `.product-card-quick-add` mobile rules, `.btn-wish-detail` (both breakpoints in `product.html`); buttons enlarged instead (mobile header 34→42px, desktop 40→46px, bottom bar 62→72px, detail CTA 52→58px) with `?v=` bumps (`app.js v8.0`, `ui.js v7.1`, `layout/responsive v7.0`).
