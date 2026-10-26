---
name: frontend-design-standards
description: Use for frontend UI. High-quality, Brutalist aesthetics.
---
# Frontend Design Standards

## Trigger
Use whenever generating or designing web UIs, dashboards, or frontend prototypes.

## Guidelines
- **Quality over Basic:** Avoid generic, bare-bones UI templates. The user expects high-quality, production-ready aesthetics (e.g., Brutalist, Cyberpunk, or refined modern Minimalist).
- **Features:** Always include Dark/Light mode toggles, interactive elements (toast notifications, hover animations), and responsive layouts.
- **Data Viz:** Use interactive libraries (like ApexCharts) for data-heavy dashboards rather than static HTML progress bars.
- **Typography:** Respect requested fonts (e.g., Lalezar, Vazirmatn for Persian UIs). Use Monospace fonts for numbers, PIDs, and technical data to enhance the "monitoring" aesthetic.

## Workflow & Pitfalls
- Do not deliver a low-effort UI and expect the user to style it later. Deliver a fully styled, interactive single-file HTML (using Tailwind via CDN and FontAwesome) from the very first iteration.
- When applying specific styles (like Brutalism), fully commit to the aesthetic (e.g., hard shadows, thick borders, specific accent colors like red/black/white) rather than a half-measure.
- **Do not copy reference implementations.** When the user shows a reference game/site, extract the *concept* and build something original — different theme, different mechanics, different visual identity. The user explicitly rejects clones.
- **Use SVG icons, not emojis, for game/UI elements.** Emojis render differently across platforms and look amateurish in games. Inline SVG or pre-rendered SVG-to-canvas is preferred for ship sprites, icons, and HUD elements.

## Browser Game Development (Canvas2D)

When building browser games with Canvas2D, follow these patterns:

### Architecture
- **Single IIFE** wrapping all game code — no global pollution.
- **`requestAnimationFrame` loop** with delta-time capping (`Math.min(dt, 0.033)`) to prevent physics explosions on tab-switch.
- **State machine** for screens: `menu | playing | paused | roundLost | levelComplete | gameOver | victory`.
- **Entity arrays** (ships, asteroids, orbs, particles) — iterate and update in the game loop.

### Physics
- **Gravity:** `F = G * M / r²` toward center. Apply as acceleration each frame: `vx += (dx/dist) * grav * dt`.
- **Momentum-based movement:** Thrust adds velocity, drag multiplies by `0.985–0.99` per frame. Clamp max speed.
- **Collision detection:** Circle-circle for ships/orbs (`Math.hypot`), AABB for blocks. Always check radius sums.

### AI Opponent
- **Reaction delay:** AI re-aims every `0.05 + (1-skill) * 0.4` seconds, not every frame. This prevents robotic jitter.
- **Prediction:** Trace ball/projectile path forward to predict intercept point.
- **Aim error:** Frozen per reaction cycle (not re-rolled per frame). Error margin = `(1-skill) * range`.
- **Easing:** AI glides toward target with `Math.min(1, dt*14)` easing, never snaps.

### Particle System
- Simple array of `{x, y, vx, vy, life, t, color, size}` objects.
- Update: `t += dt; x += vx*dt; vx *= 0.94` (drag). Remove when `t > life`.
- Render with `globalAlpha = 1 - t/life` for fade-out.

### Procedural Audio (WebAudio)
- No external assets needed. Use `OscillatorNode` + `GainNode` for tones.
- Pattern: create oscillator → set frequency → connect gain → exponentialRampToValueAtTime for fade.
- Different waveforms for different events: `sine` for collect, `square` for hit, `sawtooth` for lose.

### SVG Ship Rendering
- Define ships as inline SVG strings with `VAR_A`/`VAR_B` placeholders for colors.
- Render to offscreen `<canvas>` via `Blob` → `URL.createObjectURL` → `Image.onload` → `drawImage`.
- Pre-render once per level (when colors change), then `drawImage` each frame at ship position/angle.

### 2-Player Mode
- **Critical:** Player 1 uses WASD only, Player 2 uses arrow keys only. Do NOT share key bindings.
- In `updateShip(ship, dt, isP1)`: check `isP1` → WASD; else if `mode==='ai'` → AI; else → arrow keys.
- HUD labels must update: "بازیکن ۱" / "بازیکن ۲" in 2P mode, "بازیکن ۱" / "حریف" in AI mode.

### Dark/Light Theme for Games and Interactive Apps
- Use CSS custom properties (34+ vars) on `:root` (dark) and `[data-theme="light"]` (light).
- **Legibility & Contrast:** Do not merely make elements bright or dim randomly. When building a light theme as an inverse of a dark theme, ensure:
  - Text inside colored blocks (e.g. elements in a periodic table, grid cards, badges) must use a high-contrast text color (such as absolute white `#ffffff` or dark charcoal `#0f172a` depending on the block color's luminance).
  - Empty targets, slots, or placeholder cards (e.g. puzzle empty slots) should look physically distinct from filled ones, using muted, neutral light backgrounds (like `#f1f5f9`) and clear light borders (like `#cbd5e1`) in the light theme.
  - Quick-selectors, toggles, or navigation buttons must explicitly reflect their active/inactive states with distinguishable contrast relative to the card/background.
- Canvas rendering must check theme: `const isL = document.body.getAttribute('data-theme') === 'light'`.
- Adjust canvas colors: planet fill, asteroid fill/stroke, grid lines, text shadows.
- Theme toggle button with `localStorage` persistence.
- CSS `transition: background .4s, color .4s` for smooth switching.

### Portfolio and High-Fidelity Showcases
When a user requests a high-fidelity visual portfolio/showcase inspired by creative websites (e.g., jesse-zhou.com):
- **Avoid Amateur 3D Stubs:** Never build basic, blocky 3D rooms with raw Three.js meshes (like plain BoxGeometry cubes) as they look unpolished and basic. Instead, design a clean, high-end HTML layout matching a premium design system (like Linear or Vercel) and enhance it with a sophisticated, abstract interactive 3D background (e.g., particle/wave canvases that react to mouse movements).
- **Interactive Component Effects:** Use CSS 3D Tilt (perspective-based rotation on mouse move) on standard UI cards to provide tactile, spatial interactions without compromising layout structure or text rendering.
- **Prevent Text Overlaps:** Never embed crucial reading text inside raw 3D scenes or absolute-positioned 3D labels that can overlap in different viewports. Keep metadata and descriptions in responsive HTML/CSS wrappers, and apply visual 3D transforms only to the outer container. Ensure clean padding and flex-wrap layouts at all media breakpoints.
- **Dependency Loading & UI Freezes:** When using Three.js, GSAP, or other interactive libraries in single-file templates, verify that all external script tags are loaded in the `<head>` *before* their usage. A missing dependency triggers a silent `ReferenceError` that permanently freezes the initial loading screens.

### Level Select Pagination (10+ Levels)
When a game has 10+ levels, do NOT display them all in a single flex-wrap row — it becomes visually overwhelming and breaks on mobile.

**Pattern:** Show 5 levels per page with left/right arrow navigation.

```html
<div class="level-select-wrap">
  <button class="page-arrow" id="pagePrev" disabled>◀</button>
  <div class="level-select" id="levelSelect"></div>
  <button class="page-arrow" id="pageNext">▶</button>
</div>
<div class="page-counter" id="pageCounter">1 / 4</div>
```

```js
const PER_PAGE = 5;
let page = 0;

function buildLevelSelect() {
  const w = document.getElementById('levelSelect');
  w.innerHTML = '';
  const totalPages = Math.ceil(LEVELS.length / PER_PAGE);
  const start = page * PER_PAGE;
  const end = Math.min(start + PER_PAGE, LEVELS.length);
  for (let i = start; i < end; i++) { /* render card */ }
  document.getElementById('pagePrev').disabled = page === 0;
  document.getElementById('pageNext').disabled = page >= totalPages - 1;
  document.getElementById('pageCounter').textContent = (page + 1) + ' / ' + totalPages;
}
```

**CSS:** `.level-select` uses `flex-wrap: nowrap; overflow: hidden` with the wrapper as a flex container. Cards use `flex: 1` with `min-width/max-width` constraints. Arrow buttons are circular with `backdrop-filter: blur`.

**Mobile:** Reduce card size at 768px, 520px, 380px breakpoints. Arrow buttons shrink proportionally.

### Event Listener Audit After Rewrites
After any large JavaScript rewrite, verify every HTML `id` has a matching `addEventListener` in the JS. Missing listeners produce silent failures (button clicks do nothing, no console error). This is the #1 most-dropped element during code rewrites.

### E-Commerce & Fullstack WebUI Rules
- **Non-Blocking UI Notifications:** Never use native browser `alert()` or `confirm()` in production web apps. They freeze JavaScript execution threads, pause animations, and block headless/automated testing tools. Use non-blocking floating glass toast notifications with automatic dismiss and dedicated modal components for confirmations.
- **Admin Panel Completeness:** Admin product management must always include full CRUD (Create, Read, Update/Edit with modal prefill, Delete) directly from the UI without requiring database resets.
- **Auth Session & Logout Guard:** Ensure logout completely wipes all tokens and user JSON from `localStorage` and `sessionStorage`, and wrap protected pages (`account.html`) with an immediate redirect guard if unauthenticated.
- **Z-Index & Mobile Drawer Stacking:** Explicitly define layers (Ambient Blobs: 0, Cards/Content: 1-10, Mobile Bar: 900, Announcements: 990, Header: 995, Drawers & Modals: 1010+, Toasts: 1050). Never let backdrop glows bleed over interactive buttons.
- **Dark Mode Contrast & Reset Auditing:**
  - Audit all interactive buttons (`button`, `.btn`, stepper `+`/`-`, trash icons, dropdown triggers) to prevent browser default unstyled white backgrounds (`background: #ffffff`) from rendering washed-out white-on-white text/icons.
  - Subtitles, metadata, and footer links on dark mode backgrounds (`#0d1117`, `#0f0f16`) must use high-contrast text (`#d1d5db` or `#9ca3af`, never `#333344` or dark purple) to ensure WCAG AA compliance.
- **Mobile Bottom Navigation Desktop Guard:**
  - When designing mobile bottom action bars (`.mobile-bottom-bar`), strictly hide them on desktop with `@media (min-width: 769px) { display: none !important; visibility: hidden !important; }` and a default `display: none;` in base styles to prevent horizontal clutter on wide viewports.
- **Footer Mobile Grid Balancing:**
  - On mobile viewports (`<= 768px`), avoid collapsing 4-column footers into a single vertical tower. Use a 2-column balanced grid (`grid-template-columns: repeat(2, 1fr)`) for link lists (e.g. Collections & Help), while giving the brand bio and newsletter full-width spans (`grid-column: 1 / -1`).
- **Global Search Drawer Injection:**
  - Ensure the search trigger (`#search-btn`) dynamically instantiates and mounts the top search drawer on any page if not statically present in HTML, and binds `Enter` key events with URI encoding (`shop.html?q=...`) paired with case-insensitive `ILIKE` / substring filtering across titles, subtitles, and descriptions on the backend.
- **Custom Floating Dropdowns & Select Stacking:**
  - Always replace native OS `<select>` dropdowns in high-end dark themes with custom Liquid Glass components to prevent unstyled OS popups and bidirectional (BiDi) RTL text order glitches.
  - The parent toolbar must have `position: relative; z-index: 50;` and the floating options dropdown must have `position: absolute; z-index: 1000;` with an elevated backdrop blur and high opacity so product cards below do not clip or paint over the open menu.
- **Brand Logos & Graphic Scaling in Dark Mode:**
  - When rendering monochrome vector/raster logos on dark backgrounds, use `filter: brightness(0) invert(1)` with a subtle drop-shadow to achieve pure radiant white without muddy gray tones.
  - Give brand logos substantial visual weight (e.g. 38–48px height in header/footer, scaling gracefully on mobile) rather than diminutive icons. Keep the gap between the logo icon and the brand title text tight (e.g. 4px–8px) to maintain a cohesive single visual unit.
- **Cyber & Dark Aesthetic Accent Balance:**
  - Avoid overly harsh, 100% saturated neon primaries (e.g. intense `#ff0055` or glaring eye-straining red) across large UI surfaces or frequent text badges. Opt for sophisticated, mellowed crimson/rose tones (such as `#E26F6F`) with translucent glass glow (`rgba(226, 111, 111, 0.35)`), maintaining the edgy dark aesthetic while keeping long-form reading and shopping comfortable.
- **FastAPI / Swagger UI Docs Branding & RTL Theming:**
  - When serving API documentation via FastAPI (`/docs`), do not leave Swagger UI as the generic unstyled white page. Override the docs route with a custom `HTMLResponse` styled to match the main project's dark aesthetic, brand title, Persian/Vazirmatn typography, RTL direction, custom top navbar with return-to-store action, and brand accent colors (`#E26F6F`).
- **Interactive Form Components (Persian Datepicker & Profile Forms):**
  - For user birth date fields, avoid clumsy free-text inputs. Provide a smooth glass dropdown datepicker component (with Persian Solar Hijri year, month, and day selectors) that updates the input upon confirmation.
  - Keep customer account forms clean and friction-free by collecting only essential fulfillment data (name, phone, birth date) and omitting intrusive identity fields like national codes unless strictly legally required.
- **Manga & Pop-Art Editorial Sections:**
  - For streetwear/anime editorial manifestos, incorporate oversized background stroke typography (`-webkit-text-stroke`), high-contrast duotone gradients, and cel-shaded SVG artwork that collapses from a 2-column flex to a comfortable single column on mobile without squeezing text or causing overflow.
- **Strict E-Commerce Form Validations (Iran / Regional Localization):**
  - **Mobile Numbers:** Validate strictly with `/^09[0-9]{9}$/` (11 numeric digits starting with 09) and reject non-digit or incorrect lengths.
  - **Postal Codes:** Enforce exact 10-digit numeric codes `/^[0-9]{10}$/` with `maxlength="10"` and input sanitization to prevent dashes or letters.
  - **Two-Tier Searchable Dropdowns (Province & City):** Avoid raw unstructured text inputs for geographical locations. Implement two-tier searchable custom glass dropdowns where selecting a province filters and dynamically populates only the valid cities for that province.
- **Pure CSS Micro-Interactions & Controls:**
  - **Liquid Glass Segmented Controls:** Use CSS sibling selectors (`input[type="radio"]:checked ~ .fx-segmented-slider`) for ultra-smooth tab switching and filters without JS overhead.
  - **Pure CSS Accordions:** Structure FAQ and guide sections using semantic `<details>` and `<summary>` tags with animated pseudo-elements (`::after { transform: rotate(45deg); }`) and max-height transitions.
  - **3D Press Buttons:** Enhance primary checkout/action CTA buttons with tactile 3D box-shadow depths (`box-shadow: 0 6px 0 #b31b2c`) and active translation (`translateY(6px)`).
- **Responsive Admin Subtabs & Data Tables:**
  - On viewports `<= 900px`, convert admin tab bars into horizontal scrollable flex strips (`overflow-x: auto; flex-wrap: nowrap;`) with `-webkit-overflow-scrolling: touch`.
  - Wrap administrative and transaction tables in `.admin-table-container` with explicit minimum widths (`min-width: 650px`) so tables remain legible via horizontal swipe instead of squishing columns.
- **Safe DOM Lifecycle Initialization:**
  - When initializing page router functions or binding form handlers across multi-page sites, check `document.readyState === 'loading'` and bind to `DOMContentLoaded`, or run immediately if already loaded, ensuring dynamically injected components always attach listeners reliably.
- **Payment Result & Gateway Callback Pages:**
  - Design dedicated transaction callback views (`payment-callback.html`) supporting both success (`status=success`) and failure/cancellation states.
  - Apply dual-state styling: animated glowing status badge (`pulse-glow`) with emerald green for success and crimson red for failed/cancelled states.
  - Clearly display organizational order codes (e.g. `VOID-XXXXX`), bank tracking IDs, formatted currency with `font-variant-numeric: tabular-nums`, and explicit recovery action buttons ("تلاش مجدد جهت پرداخت") on failure so customers can retry without abandoning their carts.
- **Localized Variant Color Name Resolvers:**
  - Never display raw hexadecimal strings (`#000000`, `#ffffff`, `#990000`) directly to shoppers in cart drawers, order summaries, or invoices.
  - Implement a centralized bidirectional color resolver (`getColorDisplayName`) that maps direct hex codes and parenthetical hex names to natural localized Persian color terms (e.g. مشکی، سفید، قرمز دارک).
- **Luminance-Aware Adaptive Watermarking:**
  - When stamping brand watermarks/emblems onto product images, calculate the average luminance of the target placement bounding box.
  - Dynamically choose a high-contrast asset: pure white vector/PNG for dark backgrounds (luminance <= 128) and solid deep black for light or white backgrounds (luminance > 128).
- **16:9 Hero Sliders & Interactive Character Animation:**
  - Standardize hero banners to modern 16:9 aspect ratios (`aspect-ratio: 16 / 9`) with full-width responsive scaling across mobile and desktop.
  - Keep the header overlay clean and flat: avoid heavy glass boxes, borders, or backdrop blurs around the top navigation header so the cinematic banner artwork fills the viewport uninterrupted.
  - For character and artwork cutouts (e.g. Vagabond/Guts street art), apply multi-layered deep drop shadows (`drop-shadow(0 25px 45px rgba(0,0,0,0.95)) drop-shadow(0 0 35px rgba(0,0,0,0.85))`) to create separation from the background without harsh borders.
  - Add continuous multi-directional organic drift (`@keyframes` with subtle scale, translation and minor rotation) to make static hero figures feel dynamic and alive.
  - Equip the slider with both automatic progression and manual navigation (bullets with linear progress bars, arrow buttons, and touch gestures), with full CRUD in the admin panel to upload images, reorder slides, and assign custom hyperlinked destinations.
- **A4 Printable Invoices & Margin Isolation:**
  - When designing printable invoice modals, never use fixed zero margins (`@page { margin: 0; }`) with large internal container paddings, as it causes desktop browser print engines to clip contents outside the paper bounds.
  - Set safe print boundaries directly on `@page { size: A4; margin: 12mm 10mm; }` and reset the printable layer to `position: static` with `padding: 0` in `@media print` to guarantee the entire invoice fits neatly on standard A4 paper without pagination cuts.
- **Instant Search on Orders & Archives:**
  - Equip customer account order histories and admin management panels with real-time substring filtering across order numbers, customer names, phone numbers, and postal tracking codes across both active and archived order buckets.