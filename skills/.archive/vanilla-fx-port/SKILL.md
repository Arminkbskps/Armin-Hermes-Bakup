---
name: vanilla-fx-port
description: Port animation components to vanilla static sites.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
---

# Vanilla FX Port — porting component-library animations to static sites

## When to Use

- Target is raw HTML/CSS/JS (GitHub Pages, Cloudflare Worker SPA dashboards, no build step) but the effect
  lives in a React component library (e.g. a registry `animations/` folder or VibeFarsi).
- User asks for flashy hero effects (3D tilt, starfields, beams, scrambles, spotlight)
  on a static site or serverless admin panel. Do TEACH → PORT instead of installing anything.
- For complete VibeFarsi vanilla implementation snippets (TiltCard, SpotlightCard, BorderBeam, ShineButton, RetroGrid), see `references/vibefarsi-vanilla-porting.md`.

## Steps

1. TEACH — read the component source AND the real keyframes from the
   library's global CSS (or its registry keyframe strings). Never write
   keyframes from memory; copy them verbatim (e.g. meteor uses
   `rotate(215deg) translateX(-420px)`; beam needs `@property --beam-angle`).
2. PORT — build elements with a JS string builder (`innerHTML` /
   `insertAdjacentHTML`). Positions must be deterministic via index modulo,
   not `Math.random` (stable across renders, mirrors the source):
   `left = (i*53)%100`, `delay = ((i*37)%60)/10`, `dur = 3+((i*17)%40)/10`.
3. RTL — mirror directions: `inset-inline-end` instead of `right`;
   shine sweeps with `translateX(-120%)` in RTL contexts.
4. Reduced motion — gate the builder on
   `matchMedia("(prefers-reduced-motion: reduce)")` AND neutralize every new
   animation under `@media (prefers-reduced-motion: reduce)`.
5. Verify — serve locally, screenshot after animations settle (scramble-type
   effects need a few seconds), inspect visually.

## Proven mapping (particle/registry-style effects)

- Starfield → N `span.star` with `twinkle` (vary size 1–3px by `i%3`).
- Meteors → N `span.meteor` with `meteor` keyframes + glowing `.meteor-head`.
- Sparkles → N four-point-star SVGs with `sparkle` (`scale(0)→(1) rotate(90deg)`).
- BorderBeam → `::before` with
  `conic-gradient(from var(--beam-angle), transparent 0 78%, <color> 92%, transparent 100%)`
  + `beam 5s linear infinite`.
- TextScramble → glyph pool string, settle one char every 2 frames
  (Persian pool: `"ابپتثجچحخدذرزژسشصضطظعغفقکگلمنوهی"`).
- ShineButton → `::after` gradient sweep, `shine 0.8s` on hover only (or periodic glint on primary CTAs).
- TiltCard → pointermove sets `--rx/--ry` or `perspective(800px) rotateX/rotateY`, max 10-14deg, reset on pointerleave.
- SpotlightCard → pointermove tracks `clientX - rect.left` and sets `--spotlight-x/--spotlight-y`, rendering a soft `radial-gradient` highlight that follows the cursor across cards.
- RetroGrid → `linear-gradient` grid with radial perspective mask overlay.
- VibeFarsi in Serverless / Static Dashboards: When building single-file HTML SPAs or Cloudflare Worker dashboards where React is not used, port VibeFarsi's core interaction physics and CSS keyframes directly.
- Dynamic DOM Pitfall: When cards or list items are rendered dynamically via API calls (e.g. `loadAccounts()`, `loadRules()`), always re-invoke `initVibeInteractions()` / pointer listeners on the new elements so newly appended cards get tilt and spotlight physics.
- CandyButton (vengence-ui) → glossy `::before` top-half white gradient +
  colored drop-shadow + hover lift (`translate: 0 -2px; scale: 1.02`),
  active press (`scale: 0.96; translate: 0 1px`). List transitioned
  properties explicitly — never `transition: all`.
- NeonTrace (vengence-ui animated-border) → `::before` 2px top bar,
  `linear-gradient(to left, transparent, var(--brand), transparent)`,
  resting `translateX(-100%)` → `translateX(100%)` on hover with
  `1s ease-in-out`. RTL-safe via `inset-inline` + X percents.
- BlobatarFallback → zero-dep deterministic avatar when remote favicons fail:
  integer hash (`h = h*31 + charCode`), `hue = h % 360`,
  shape from `shapes[h % 3]` (round / squircle / organic blob radius),
  expression from `(h >> 3) % 4` (open / wink / shades / sleepy). White SVG
  face on `linear-gradient(135deg, hsl(hue,…), hsl(hue+40,…))`. Hover-only
  `blob-wiggle` keyframes; neutralize under reduced-motion.

## Scope of Change: Micro-Polish vs "خفن تغییر" (user correction)

This user distinguishes sharply between *polish* and a *visible transformation*.
Session lesson: adding a favicon fallback, a subtle neon line, or a glossy
button highlight while keeping the same layout drew «از نظر ظاهری هنوز همون
قبلیه» — to them, nothing had changed. When they ask for a «تغییر خفن» with
«المان‌های 3D», they want **hero-scale structural change**: a new scene layer
behind the header (floating blobs, parallax orbs with `data-depth`,
perspective container, giant morphing centerpiece), not deeper tweaks of the
existing components.

Rules of thumb:
- Cosmetic-only diffs (borders, shadows, small fallbacks) do NOT count as the
  requested change — they can ride along, but the headline must be a new
  visible element or layout layer.
- Before declaring done, take a screenshot and check: would a person who saw
  the page for 1 second notice the difference? If not, it's not the change
  they asked for.
- Prefer one dramatic, verified hero effect over five invisible micro-edits.

## Pitfalls

- Screenshots taken mid-scramble show gibberish — wait for settle before judging.
- `@property --beam-angle` is required; without it the conic rotation is static.
- Keep one styling system: plain CSS in a CSS project, never add a framework
  just for the effect.
- After `git pull --rebase`, files you edited may have changed on disk —
  re-read (`sed`/`read_file`) before issuing further `patch` calls, or the
  old_string won't match and you'll waste rounds retrying.
