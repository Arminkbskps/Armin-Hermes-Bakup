---
name: persian-singlefile-sites
description: Use when building Persian RTL single-file sites.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Persian, RTL, static-sites, Cloudflare-Pages]
    related_skills: [cloudflare-deploy]
---

# Persian Single-File Sites

## When to Use

- User asks for a Persian RTL static site (countdown, landing, tool) shipped as one HTML file to Cloudflare Pages.
- Don't use for: React apps, backends, or anything needing npm dependencies.

Build Persian RTL single-file static sites (one `public/index.html`, inline CSS+JS, Vazirmatn, `dir=rtl lang=fa`) deployable to Cloudflare Pages. Borrow the *style* of VibeFarsi/Linear, never copy-paste component trees.

## Procedure

1. Read the current `index.html` first to preserve its JS data model (localStorage keys, object shapes) — same keys, same shapes, new skin. When the app's purpose changes (e.g. countdown studio becomes a study clock), keep legacy keys and accept legacy record shapes so old user data stays readable.
2. Set Linear-grade tokens as CSS vars: near-black bg (`#08090a/#0f1011/#191a1b`), text `#f7f8f8/#d0d6e0/#8a8f98`, one accent (`#5e6ad2` default), borders `rgba(255,255,255,.05/.08)`, radius 6/8/12/22, tabular numbers for timers.
3. Theme engine: `data-theme` switcher (graphite/turquoise/saffron/pomegranate/lapis/paper) + dark/light mode + accent swatches overriding `--brand/--primary`; persist all in localStorage; theme change must repaint the whole site in one click.
4. Mobile-first responsive: bottom tab bar on mobile, sidebar only >=1024px, grids collapse 4->2->1, tables become cards <768px, modals become bottom-sheets, 44px touch targets, safe-area insets, `overflow-x:hidden`, zero horizontal scroll.
5. Ship features, then verify: extract inline JS and syntax-check it, curl for key strings (`dir="rtl"`, `data-theme`, feature keywords, `localStorage`), grep that no emoji range remains, screenshot at 390px and confirm no overflow.
6. Report progress as ONE consolidated message per phase (what ran, result, next) — never drip-feed one line per micro-step.

## Rules

- Zero emoji anywhere in site UI (buttons, badges, toasts, empty states) — use an inline-SVG stroke icon set (lucide-style: clock, calendar, plus, chart, settings, trash, share, play, pause, book, timer, palette, moon/sun, search); emoji in chat replies to the user is fine, emoji in the shipped site is not.
- Take VibeFarsi's look (clean Persian type, spacing, radius, shadows, color) without cloning its component inventory — ship only the blocks the page needs; a sparse Linear-grade page beats a crowded component showcase.
- Keep single-file budgets: core studio under ~100KB, absolute cap ~200KB; no external JS deps, Google Fonts link only.
- Color per project, never a house monochrome: use the palette that fits the project (black/white minimal applies only when the user explicitly asks it for that project). Reserve strong fills for meaning (priority/status); priority mapping is p1 = solid fill, p2 = outline, p3 = muted; sort lists pinned-first, then priority, then newest. Keep body text monochrome and put the signal in fills, borders, and badges.
- Flex overflow guard: every flex-row child gets min-width:0 plus ellipsis (or line-clamp) on its text — long Persian names force horizontal scroll on 360px viewports even with overflow-x:hidden on body.
- Pair every fill with its inverse token: `background:var(--tx0)` always goes with `color:var(--bg0)` — never hardcode `#fff` text, which turns invisible on white fills and in light mode.
- Namespace localStorage per feature (`app.todo.v1`, `app.notes.v1`) and cap arrays with `slice(-N)` on every save so quota never blows; accept legacy record shapes on load so old user data stays readable.
- Ship real PWA files: `manifest.webmanifest` (name, icons 192/512, standalone, rtl/fa) + `icons/icon-192.png` + `icons/icon-512.png` (maskable) + `sw.js` registered with `updateViaCache:'none'`; service worker caches fonts/icons for offline but uses network-first for navigations and bumps the CACHE version on every ship, otherwise users stay stuck on stale HTML behind the old worker.
- Client-side share image: render text reports to `<canvas>` with theme-aware fills and trigger download via `toDataURL` — no server round-trip needed for PNG export.
- Every theme ships dark AND light variants (`[data-theme="x"][data-mode="light"]` overrides) — a theme without a light variant stays dark when the user flips to light mode.
- Widget mode (`?widget=1`) must target the tab wrappers (`main>#tab-timer` with `!important`), hide the tabbar, and force the timer tab on via JS — a generic `main>*:not(.hero)` selector hides every tabpage including the timer.
- Focus/zen mode dims only (`opacity`, no `filter:blur`, never `pointer-events:none`) so buttons stay tappable while dimmed.
- Tabbar fits mobile without cutoff: grid (e.g. `repeat(3,1fr)`) on small screens, never a scrolling row that clips tabs off-screen.
- App icons must be square / rounded-square (squircle), not circular, to avoid double-masking in mobile launchers and match modern app design standards.
- Push is not live: after push, fetch a live asset URL over HTTP and expect 200 with the new marker string before announcing; on GitHub Pages ensure `build_type` is `workflow` (PUT `/repos/{owner}/{repo}/pages` `{"build_type":"workflow"}`), otherwise legacy Jekyll serves stale content.
