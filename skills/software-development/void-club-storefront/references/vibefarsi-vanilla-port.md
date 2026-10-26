# VibeFarsi registry → vanilla static frontend (no React)

VOID CLUB's cPanel frontend is raw HTML/CSS/JS — `npx vibefarsi add` is FORBIDDEN
there (it scaffolds React files, `@/` aliases, and CSS imports that don't exist).
Instead TEACH (read the registry source in `vibafarsiui/registry/`) then hand-port
the formula. Proven on tilt-card + skeleton shimmer (session 2026-09-21, v11)
and meteors + success-check + number-field + accordion (same session, v12).

## tilt-card (registry/animations/tilt-card.tsx)

Formula: `perspective(600px) rotateX(-py*max) rotateY(px*max)`, px/py = relative
pointer position in `-0.5..0.5`, reset to `0deg` on leave, `transition: transform 150ms ease`.
- Bind `pointermove` per `.vc-tilt` element; skip `pointerType === 'touch'`.
- Throttle with `requestAnimationFrame`; cancel on `pointerleave`/`pointercancel`.
- `max` from `data-tilt-max` (default `10`).
- Shine: absolutely-positioned overlay, `background-size: 250% 100%`, drive
  `background-position` from px (`--tilt-shine-x: (px+0.5)*100%`).
  RTL targets sweep right→left (`linear-gradient(to left, ...)`).
- Guards (CSS + JS): `@media (hover: none), (prefers-reduced-motion: reduce)` →
  `transform: none`, hide shine; JS early-return on the same matchMedia.
- Never break the page: try/catch the whole binder, scope to `.vc-tilt`.

## skeleton shimmer (registry/ui/skeleton.tsx)

Highlight sweep, not a spinner: overlay `::after` with
`linear-gradient(to left, transparent 20%, rgba(255,255,255,0.35) 50%, transparent 80%)`,
`background-size: 220% 100%`, keyframes move `background-position: 120% → -120%`
with an opacity envelope (`0 → 1 → 0`), ~320ms. RTL keeps `to left`.

## meteors (registry/animations/meteors.tsx, v12)

Deterministic streaks falling top-right → bottom-left. Mirror the exact formula
in a JS builder loop (count = 12) rather than hand-writing spans:
- `left = ((i * 53) % 100) + '%'`
- `delay = (((i * 37) % 60) / 10).toFixed(1)` seconds
- `duration = (3 + ((i * 17) % 40) / 10).toFixed(1)` seconds
- Streak element: `position: absolute; top: -10%; height: 1px; width: 96px`
  (`w-24`), `background: linear-gradient(to left, transparent, rgba(255,255,255,0.55), #fff)`;
  head dot via `::after` (5px circle, `box-shadow: 0 0 8px 2px rgba(255,255,255,0.4)`).
- Keyframes `meteor`: `0% { transform: rotate(215deg) translateX(0); opacity: 1 }`
  `70% { opacity: 1 }` `100% { transform: rotate(215deg) translateX(-420px); opacity: 0 }`,
  `linear infinite`.
- Host must be `position: relative/absolute` + `overflow: hidden` + `pointer-events: none`;
  keep content above with `z-index` (meteors layer at `z-index: 0`).
- Reduced motion: `display: none` the streaks; skip building them in JS via matchMedia.

## success-check (registry/animations/success-check.tsx, v12)

Circle pops in, tick draws itself. Static SVG markup, no JS animation needed:
- `viewBox="0 0 72 72"`: halo circle (`r=34`, `fill: var(--success)`, `opacity: 0.15`),
  ring circle (`r=34`, stroke `--success`, width 2),
  tick `path d="M22 37 L32 47 L51 27"` (stroke `--success`, width 5,
  `round` caps/joins, `stroke-dasharray: 48`, `stroke-dashoffset: 48`).
- Keyframes `pop` on the svg (`scale 0.6 → 1.08 → 1`, 0.5s `cubic-bezier(0.16,1,0.3,1)`,
  `both` fill) + `draw` on the path (`to { stroke-dashoffset: 0 }`,
  `0.5s ease-out 0.35s forwards`).
- Define `--success` (e.g. `#10b981`) on the wrapper class.
- On multi-state result pages: render the tick for success-family states, fall back
  to the legacy icon box otherwise (a `showTick(on)` toggler flipping `display`).
- Reduced motion: `animation: none`, force `stroke-dashoffset: 0` so the tick is visible.

## number-field (registry/ui/number-field.tsx, v12)

Plus at inline-start (right in RTL), Persian-digit display, minus at inline-end.
Vanilla shape: `<div role="group">` > plus-button + bordered display span + minus-button.
- Display is an `<input inputmode="numeric">` showing `n.toLocaleString('fa-IR')`;
  parse back with fa→en digit conversion
  (`raw.replace(/[۰-۹]/g, d => '۰۱۲۳۴۵۶۷۸۹'.indexOf(d)).replace(/[^\d]/g, '')`).
- `set()` clamps: floor at 1 (this project's no-max variant drops the `max` prop
  entirely — never invent a cap the user didn't ask for); minus button `disabled`
  at the floor.
- Reuses the v11 stepper micro-pattern for feedback: direction-aware digit slide
  (`vc-qty-up/down`), skeleton shine sweep, floor shake (`vc-qty-min`) — but the
  animation classes now target the display WRAPPER span, not the input itself
  (inputs can't host `::after` shine overlays).
- Buttons: flat, borderless, muted icon color, accent hover — not the v11 glass keys.
- Restart animations via class remove + forced reflow (`void el.offsetWidth`).

## accordion (registry/ui/accordion.tsx, v12)

Chevron at inline-end; height animates with CSS grid, no measuring.
- Structure per item: `<button class="acc-header" aria-expanded>` + `.acc-body` >
  `.acc-body-inner` (overflow hidden) > `.acc-body-text` (padding lives here,
  never on the grid container).
- Closed: `grid-template-rows: 0fr`; open class (e.g. `.acc-open`/`.vc-open`):
  `grid-template-rows: 1fr`; `transition: grid-template-rows 200ms ease-out`.
- Chevron: `transition: transform 200ms ease`; open class rotates it `180deg`
  (no icon swap needed).
- Single-open default (mirrors the component without `multiple`): toggler removes
  the open class from siblings, flips their `aria-expanded` to false; clicking the
  open item closes it. Use real `<button type="button">` headers, not divs.
- Replace-don't-patch signal: if the legacy accordion class has ZERO definitions
  in any CSS file, the old component is unstyled dead markup — replace the whole
  block with the new pattern instead of trying to fix its CSS.
- Same pattern serves product spec/wash panels and guide FAQ — only the class
  prefix and container differ.

## real credit-card face (ReactBits credit-card-tw pattern, v12)

For bank-card displays (checkout card-to-card): `aspect-ratio: 1.586`,
`max-width: 420px`, dark gradient + red radial glow, flex column space-between.
- Top row: gold chip (gradient + etched lines via `::before`/`::after`) +
  contactless glyph + brand mark.
- Number: `dir="ltr"`, centered monospace, grouped 4-4-4-4 in JS
  (`digits.match(/.{1,4}/g).join(' ')`), `letter-spacing: 0.14em`.
- Bottom row: holder label + name (inline-start) / bank name + conic-gradient
  hologram chip (inline-end).
- Amount + copy buttons live OUTSIDE the card in stacked meta rows below it —
  never inside the card face.
- **Column alignment (v14 fix):** card + meta rows + receipt-upload box must share
  ONE width rule (`.vc-cc, .vc-cc-meta { width: 100%; max-width: 420px }` and the
  SAME `width/max-width` on the upload section). The upload box originally had no
  max-width so it rendered full-width while the card above was capped — edges
  misaligned. When a user reports "card and rows below aren't the same width",
  check every sibling in the column for the missing cap, not just the card.
- **Meta/receipt spacing (v14 fix):** the meta container needs an explicit
  bottom margin (`margin: 12px 0 18px`) — without it the last meta row (rial)
  sticks to the upload box below (`margin: 0` on rows + `gap` inside meta is not
  enough; the gap between the two SECTIONS must be owned by one of them).
- Tilt (`bindVcTiltCards`, `.vc-tilt`) keeps working: shine element stays first child.

## stepper micro-pattern (proven pairing for qty controls)

- Direction-aware digit slide: `+` slides up (`translateY(55%) → 0`), `−` slides
  down (`translateY(-55%) → 0`), 220ms `cubic-bezier(0.16,1,0.3,1)`; restart by
  removing classes + forcing reflow (`void el.offsetWidth`) before re-adding.
- Floor feedback: at minimum with no change, play a small X shake (~200ms).
- Buttons (v11 style): rounded-square glass keys (`border-radius: 14px`, translucent
  bg + border), `:hover` accent glow, `:active { transform: scale(0.88) }` — no plain
  circles. (v12 number-field uses flat borderless keys instead — pick per context.)
- `prefers-reduced-motion: reduce` disables all of it.

## Verification (static-site discipline)

- `node --check` every touched JS file.
- Keyframe/class presence check on touched HTML + JS.
- Regression grep for the removed feature family must read zero.
- Bump `?v=` query strings on touched bundles so static hosts pick up the change.
