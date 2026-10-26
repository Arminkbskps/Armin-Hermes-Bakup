---
name: rtl-web-development
trigger: "When making frontend code RTL."
description: "Use for RTL support. Pitfalls with global dir attribute."
---

# RTL Web Development Guidelines

When modifying web applications to support Right-to-Left (RTL) languages (like Persian, Arabic, Hebrew), keep these core principles and pitfalls in mind.

## 1. Setting the `dir` attribute

To properly enable RTL rendering at the browser level, you **must** set the `dir` attribute on the `<html>` or `<body>` tag, alongside any CSS classes you add, *unless* the application explicitly isolates RTL to specific containers.

**Do:**
```javascript
document.documentElement.classList.add('rtl-mode');
document.documentElement.dir = 'rtl'; 
```

**Don't:**
```javascript
// Missing the `dir` attribute. CSS `direction: rtl` alone is insufficient
// for correct browser-level bidirectional text rendering, scrolling, and flexbox behavior.
document.documentElement.classList.add('rtl-mode');
```

## 2. Granular UI Targeting vs Global Targeting

When a user asks to "make the site RTL", determine if they mean:
- **Global RTL:** The entire application interface changes direction.
- **Content-specific RTL:** Only the user-generated content or chat messages should flip (e.g., in a chat application where the UI stays LTR but the messages are RTL).

### Pitfall: Accidentally breaking LTR-designed shells
In applications where only specific content areas have RTL CSS rules defined (like Hermes WebUI, which targets `.chat-content-rtl .msg-body`), setting `document.documentElement.dir = 'rtl'` globally will flip the entire application shell (sidebars, nav bars) which may not have corresponding RTL CSS, leading to a broken layout.

**Rule:** If the CSS specifies RTL for a specific container, apply `direction: rtl` only to that container or rely *only* on the CSS classes designed for it. Do not set `document.documentElement.dir = 'rtl'` unless you are sure the entire application is designed to handle it.

### Pitfall: Inline Direction vs Global Direction
When building a global RTL layout, avoid scattering inline `style="direction: rtl"` across elements. Instead, set `<html dir="rtl">` or `<body dir="rtl">`.
If a specific component (like a data grid or game board) must explicitly render left-to-right (LTR) while the rest of the page is RTL, set `dir="ltr"` on that specific container.
**Example:** A periodic table puzzle built for RTL users still needs its chemical symbol grid to render LTR. Set `dir="ltr"` on the grid container, not inline styles on every cell, and ensure child cell contents explicitly specify `text-align: left; direction: ltr;` if their text layout breaks.

## 3. Font Integration

When adding RTL fonts, ensure the font is correctly added to the CSS variable stack, usually at the front, so it takes precedence over Latin fonts for RTL characters, but falls back gracefully.

**Recommended Persian fonts (Google Fonts):**
- **Vazirmatn** — Clean, modern, excellent for UI text and body copy.
- **Lalezar** — Bold, decorative, excellent for headings, logos, and game titles. Pairs well with Orbitron for a space/arcade aesthetic.

**Pitfall — Orbitron does NOT support Persian:** Orbitron is a Latin-only geometric display font. Using it for Persian/Arabic text renders empty boxes or fallback sans-serif. Always verify Google Fonts language support before choosing a display font for RTL UIs. Lalezar is the recommended alternative for Persian display text.

**Do:**
```css
--font-ui: "Vazirmatn", -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif;
/* For headings/titles: */
--font-display: "Lalezar", "Orbitron", sans-serif;
```

**Don't:**
```css
/* Replacing the entire stack, breaking fallbacks */
--font-ui: "Vazirmatn";
```

## 4. CSS Variable Theming (Dark/Light) for RTL Apps

When building RTL apps with dark/light theme support, use the `data-theme` attribute pattern on `<body>` or `<html>`.

**Structure:**
```css
:root {
  --bg: #08090f;
  --text: #e8eaf0;
  --accent-a: #00c8e0;
  /* ... all dark theme vars ... */
}
[data-theme="light"] {
  --bg: #f0f2f8;
  --text: #1a1d2e;
  --accent-a: #0090a8;
  /* ... all light theme vars — MUST mirror every dark var ... */
}
```

**Pitfall — variable mismatch:** Every CSS variable defined in `:root` MUST have a corresponding definition in `[data-theme="light"]`. A missing light-theme var causes the dark value to bleed through in light mode, producing invisible text or broken backgrounds. Count vars in both sections to verify parity.

**JS toggle pattern:**
```javascript
let isDark = true;
function applyTheme() {
  document.body.setAttribute('data-theme', isDark ? 'dark' : 'light');
  localStorage.setItem('theme', isDark ? 'dark' : 'light');
}
```

**Pitfall — canvas rendering in themed apps:** When drawing on `<canvas>`, theme-dependent colors (e.g. `isL ? 'light-color' : 'dark-color'`) must be passed to every render sub-function. A common bug is defining `const isL = ...` inside `render()` but calling sub-functions like `drawPowerups()` without passing it — the sub-function then throws `ReferenceError: isL is not defined`. Always pass theme state as a parameter to render helpers.

**Pitfall — aurora/glow opacity:** Light themes need lower opacity on decorative gradients (aurora, glows) because light backgrounds amplify them. Typical ratio: dark `.30–.45`, light `.15–.25`.

## 5. Bidirectional (BiDi) Text & Native `<select>` / Dropdown Issues

When rendering mixed Latin/English text or badges inside RTL sentences (such as `دراپ‌های تولید محدود (Limited)`), browsers can reverse punctuation or displace the Latin segment if directionality is not isolated.

### Pitfall: Native OS `<select>` / Dropdown Popovers in RTL Dark Themes
Native `<select>` elements and their `<option>` popups are rendered by the OS/browser engine, not the DOM styling layer.
- **Visual Glitches:** Sharp 90-degree corners, native OS blue focus highlights, and unstyled light-gray borders clash with custom dark glass/Liquid Glass design systems.
- **BiDi Displacement:** Native select options often mess up parenthetical English phrases inside RTL text (e.g. rendering `(Limited) دراپ‌های تولید محدود`).
- **Solution:** Always replace critical UI dropdowns (sorting, filters) with custom accessible JavaScript dropdown components (`.custom-select-wrapper`, `.custom-select-trigger`, `.custom-select-options`) with explicit `direction: rtl` and custom animations.

## 6. Mobile vs Desktop Bar Collision
In mobile-first responsive RTL web applications with a floating bottom app bar (`.mobile-bottom-bar`):
- Explicitly guard desktop viewports with `@media (min-width: 769px) { .mobile-bottom-bar { display: none !important; } }`.
- Ensure multi-column footers stack into 2-column or 1-column layouts with `overflow-wrap: break-word` and explicit spacing to prevent touch collisions.

## 7. RTL Segmented Control & Slider Positioning (translateX direction)

When converting CSS segmented control pill sliders (e.g. `.fx-misc-segmented-slider`) to RTL:
- In LTR layouts, moving right is `translateX(100%)`, `translateX(200%)`.
- In RTL layouts, the starting position is anchored to the right (`right: 4px;` instead of `left: 4px;`), so subsequent options move **to the left**:
  ```css
  .fx-misc-segmented input:nth-of-type(1):checked ~ .fx-misc-segmented-slider { transform: translateX(0); }
  .fx-misc-segmented input:nth-of-type(2):checked ~ .fx-misc-segmented-slider { transform: translateX(-100%); }
  .fx-misc-segmented input:nth-of-type(3):checked ~ .fx-misc-segmented-slider { transform: translateX(-200%); }
  ```
- **Z-Index in RTL Floating Dropdowns:** Searchable province/city dropdowns and popovers inside form grids must have `z-index: 9999` and explicit positioning to avoid clipping underneath subsequent form sections or payment method cards.

## 8. Centering Fixed Overlays in RTL (toasts, modals, banners)

The classic LTR centering recipe **silently breaks** in RTL and pushes the element off-screen with no console error, no overflow, no visible clue — the user just reports "the message doesn't show on mobile."

**The bug** — combining a logical inset with a physical translate:
```css
/* WRONG — double-negates in RTL, element lands off-canvas */
.overlay {
  inset-inline-start: 50%;   /* in RTL this is right: 50%, anchoring to the RIGHT of center */
  translate: -50% 0;         /* then shifts LEFT by half its own width → off the left edge */
}
```
Measured on a 390px viewport: `left: -25.7px`. Completely invisible.

**The fix** — logical properties *and* logical (or axis-specific) transforms must agree. Two reliable forms:
```css
/* Form A — safest, direction-agnostic */
.overlay {
  position: fixed;
  left: 50%;                  /* physical */
  transform: translateX(-50%);/* physical — matches in BOTH dirs */
}

/* Form B — fully logical */
.overlay {
  position: fixed;
  inset-inline-start: 50%;
  translate: -50% 0;          /* BUG: still wrong in RTL */
}
```
Prefer **Form A** for fixed overlays. `left: 50%` + `translateX(-50%)` is not RTL-sensitive, which is exactly what you want for a centered toast.

**Debugging an invisible overlay** — don't guess, measure:
```js
const r = el.getBoundingClientRect();
// negative left/right, or top < 0 while the page is scrolled to 0 = off-canvas
```
`document.documentElement.scrollWidth === window.innerWidth` will still report *no* horizontal overflow, because a `position: fixed` element off-canvas does not expand the document. Overflow checks cannot detect this bug — only `getBoundingClientRect()` can.

**Mobile safe-area** — fixed top overlays get clipped under the browser chrome / notch. Use:
```css
top: max(1rem, env(safe-area-inset-top, 0px));
z-index: 200; /* above sticky topbars, which typically sit at z-index 40 */
```

**Verify on mobile, not just desktop** — with CDP:
```js
cdp('Emulation.setDeviceMetricsOverride', { width: 390, height: 844, deviceScaleFactor: 2, mobile: true });
```
Then trigger the real overlay (click the button that produces it) and capture. Desktop-only checks miss this class of bug entirely.

## 9. Localization of Technical Attributes & Hex Colors in RTL E-Commerce

When building e-commerce and checkout flows in RTL applications:
- **Never display raw hex codes directly in user-facing summaries:** Raw `#000000` or `#ffffff` feels unrefined and looks like raw developer debug text. Always pass color strings through a localized mapper function (e.g. `getColorDisplayName`) to convert hex values into natural language (e.g., `#000000` → `مشکی`, `#ffffff` → `سفید`, `#990000` → `قرمز دارک`).
- **Alphanumeric Token Display:** For order codes (e.g. `VOID-84076`), tracking numbers, and currency values, combine `font-family: 'Outfit', 'Vazirmatn', sans-serif;` with `font-variant-numeric: tabular-nums;` and `-webkit-font-smoothing: antialiased;` to prevent layout shifts and ensure crisp, premium presentation.
- **Dynamic Search in Orders & Data Tables:** When filtering order tables in RTL admin/account views, query matching should normalize Persian numbers/characters and perform case-insensitive substring checks across both Latin codes (`VOID-XXXXX`) and localized customer details.

## 10. Horizontal Scroll & Slider Progression in RTL (`scrollBy` and `scrollLeft`)

In modern standards-compliant browsers with `<html dir="rtl">`:
- Horizontal content progresses from **Right to Left**.
- The start position is the rightmost edge, where `scrollLeft` is 0.
- Advancing forward through items ("Next" / "بعدی", moving towards the left) requires **decreasing** `scrollLeft` or passing a **negative delta** to `scrollBy`:
  ```javascript
  // Next (advancing through items to the left in RTL):
  track.scrollBy({ left: -delta, behavior: 'smooth' });
  // OR fallback:
  track.scrollLeft -= delta;

  // Previous (returning towards start to the right in RTL):
  track.scrollBy({ left: delta, behavior: 'smooth' });
  // OR fallback:
  track.scrollLeft += delta;
  ```
- **The Pitfall:** If an engineer writes standard LTR logic (`track.scrollBy({ left: direction * delta })` where `direction = 1` for next and `-1` for prev), the navigation arrows will behave in reverse: clicking next will attempt to scroll right (which is already at 0, doing nothing or reversing), and clicking previous will scroll left.
- Always check the physical icon orientation (`fa-chevron-left` points forward in RTL; `fa-chevron-right` points backward in RTL) and bind negative scroll to `left` progression and positive scroll to `right` return.