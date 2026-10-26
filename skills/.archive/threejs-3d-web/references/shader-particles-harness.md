# Shader-particle test harness (Three.js + GSAP)

Session recipe from testing VengeanceUI `interactive-particles` (Three.js `RawShaderMaterial` + GSAP intro) in a plain Vite React scaffold. Use when a particle/shader scene renders a black canvas with no console errors.

## Scaffold recipe

1. Registry item deps were `three` + `gsap` → `npm i three gsap` (+ `@types/three`).
2. Plain Vite has no Tailwind/shadcn: component used `@/lib/utils` (`cn`) and classes `relative/h-full/w-full/block/overflow-hidden`. Fixed by a local `src/lib/utils.ts` (`cn` join) + minimal utility CSS in `index.css`, and rewrote the import to a relative path.
3. Removed the unused `import * as React` (fails `tsc -b` with `noUnusedLocals`).
4. Demo page: `<InteractiveParticles src="/demo.svg" …/>` plus live sliders for `color/size/randomness/depth/touchRadius/threshold` — fastest way to prove all props work.

## Black-canvas diagnosis ladder (in order — each step isolates one layer)

1. **Data**: rasterize the source image in-page, count bright pixels over `threshold`. (Ours: 320×160 grid, 4324 visible of 51200 — data fine.)
2. **Load**: `TextureLoader.load(src, onLoad, undefined, onError)`; record load/error state on `window`. (Ours: `loaded:640x320` — load fine.)
3. **GLSL version**: confirm the shader targets GLSL1 (`attribute`/`varying`/`texture2D`/`gl_FragColor`) and stays in `RawShaderMaterial`. Three only auto-converts to `#version 300 es` for non-raw materials.
4. **Render loop vs scene**: expose `{renderer, scene, camera, object3D, uniforms}` on `window`; force uniform values (`uSize/uRandom/uDepth/uTime`); call `renderer.render(scene, camera)` manually and read `renderer.info.render.calls/points`. (Ours: manual render drew 1 call — scene fine, loop was the culprit.)
5. **Loop gating**: component paused its loop when `document.hidden`. Automated browsers report `visibilityState: hidden` + rAF never fires — canvas stays black *by design*. Verified via `document.visibilityState` probe + rAF timeout test. Not a bug; verify in a real foreground tab or via manual render.
6. **GSAP intro freeze under StrictMode**: `gsap.fromTo(uSize …)` started at `0.0` while the loop was paused → tweens never ticked, `uSize` stuck at 0. Confirm `uSize` stays 0 across polls. Fix options: render one frame after build regardless of visibility, or start tweens on first visible frame.

## ResizeObserver loop fix

Symptom: `ResizeObserver loop completed with undelivered notifications` spam (hundreds of matches). Cause: `applySize` called `renderer.setSize()` synchronously inside the observer → re-trigger. Fix applied to the test copy:

```ts
let sizeRaf = 0;
const applySize = () => {
  sizeRaf = 0;
  const next = getSize();
  if (next.width === view.width && next.height === view.height) return;
  view = next;
  /* ... camera + renderer.setSize + applyScale ... */
};
const scheduleSize = () => {
  if (sizeRaf) return;
  sizeRaf = requestAnimationFrame(applySize);
};
const resizeObserver = new ResizeObserver(scheduleSize);
window.addEventListener("resize", scheduleSize);
// cleanup: removeEventListener("resize", scheduleSize) + cancelAnimationFrame(sizeRaf)
```

## Env quirks hit this session (do NOT generalize)

- `raw.githubusercontent.com` needed direct connection (`no_proxy='*'` unset proxy vars); npm registry mirror `npmmirror.com` reset on big tarballs → switched to `registry.npmjs.org` for `three`/`gsap`.
- These were machine-state issues, not durable rules.
