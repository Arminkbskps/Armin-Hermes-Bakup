# Adding a product-level attribute — full-stack recipe (proven by `product_type`, session 2026-09-11)

Use when the user asks for a new per-product attribute (type, material, gender, season, …)
that must be set in admin, filterable in the shop, and/or change the product page.
Values `tshirt | hoodie | sweatshirt | cap` below are the example — substitute your own.

## Backend (`api/`)

1. **`schema.sql`**: add the column + a `KEY ix_prod_<attr> (...)` next to the other product keys.
2. **`lib_db.php`** (4 coordinated edits):
   - SQLite mirror `CREATE TABLE` in `vc_sqlite_init()` — add the column (SQLite-relaxed type).
   - `vc_ensure_<attr>($pdo)` auto-migration (static `$done` guard, same shape as
     `vc_ensure_category_parent()`): `SELECT <attr> FROM products LIMIT 1` → return if present;
     else `ALTER TABLE` — `TEXT NULL` on sqlite, `VARCHAR(..) NULL … ADD KEY` on MySQL.
     Old installs (host MySQL + local sqlite) then migrate with zero reinstall.
   - `vc_normalize_<attr>($v)` whitelist: accept the EN slug(s) AND the Persian label(s),
     return `null` for anything else (never store raw user input).
   - `vc_<attr>_label($v)` FA-label map + expose both raw and label fields in `vc_product_full()`.
3. **`api.php` — products block** (4 touch points, all need the `ensure` call):
   - `GET` list: call both ensures, parse `$_GET['<attr>'] ?? $_GET['type'] ?? null`.
     Multi-select filters: `explode(',', …)` → normalize each → `IN (?,…)` placeholders.
     The `count_only` path reuses `$sql/$args`, so the filter applies there automatically.
   - `GET` by id: call both ensures too — otherwise detail pages 500 on pre-migration DBs.
   - `POST`: add the column explicitly to the `INSERT` list + normalized value.
   - `PUT`: append to the `$fields` allowlist + a normalize branch in the loop + ensure call.
     (`enterprise-admin.js` batch PUTs like `{price}` / `{category_id}` keep working — untouched fields are skipped.)
4. **`install.php` seed**: include the column in the products `INSERT` with a sensible
   guess/default (seed guess here: hoodie-ish collections → `hoodie`, else `tshirt`).

## Frontend (`js/app.js` top-level — TDZ-safe, before `initRouter()`)

- One `const <ATTR>_TYPES = [{value, label}…]` + `get<Attr>Label()` + `get<Attr>Specs()` /
  `<attr>SpecsHtml()` helpers. Single source of truth for labels AND product-page spec lines.
- **Spec lines must each be single-line strings** (rendered as `<li>`); legacy `null`
  values get a fallback message, never a blank accordion.
- Shared-scope check first: `grep` the helper names across `js/*.js` — a duplicate
  top-level `const` kills the whole second script (see TDZ pitfall in SKILL.md).

## Admin (`account.html` + `app.js`)

- **Single-value attribute → radio inputs styled as `.size-check-chip`** (looks like the
  checkbox chips the user asked for, but prevents invalid multi-select). One default
  `checked` in the add form; edit modal pre-ticks from `p.<attr>` with a legacy-`null` default.
- Both payload builders (`handleAdminAddProduct`, `handleSaveProductEdit`) include the field.
- Show a small badge in `loadAdminProducts()` rows so the admin can see the value at a glance.

## Shop filter (`shop.html` + `app.js` + `js/products.js` + `css/responsive.css`)

- New `.filter-group` in the sidebar with its own `#<attr>-filter-list` div.
- `products.js`: map the new filter key to a query param (accept both `product_type` and `type`).
- `initShopPage`: render real checkboxes from the const list, `change` → reload;
  deep-link from URL (`?product_type=a,b`) on init. Multi-select joins with `,`.
- **Responsive 3-mode rule**: append the new list id to the `#category-filter-list`
  selectors in `responsive.css` (tablet chip-row + phone bottom-sheet column) or the new
  filter breaks on mobile while categories work.
- Bump `?v=` FORWARD on every edited JS/CSS file across all HTML pages (script-driven replace).

## Acceptance checklist

- `node --check` on edited JS; `grep -c <attr>` non-zero in schema/api/lib_db/app/products/account/shop/install.
- Logic test without a server: labels resolve, spec line counts match, no multiline lines,
  filter join produces `a,b`.
- Live (user runs `start.bat` — PHP CLI is absent on this box, portable download may fail
  behind the proxy): edit one product's value in admin → `GET /api/products/{id}` returns it →
  shop checkboxes filter → product page accordion shows the right specs.
