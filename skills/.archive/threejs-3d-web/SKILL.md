---
name: threejs-3d-web
description: "Three.js 3D web: GLTF portfolios, scenes, interactions."
version: 1.0.0
author: curator
license: MIT
metadata:
  hermes:
    tags: [threejs, 3d, gltf, webgl, portfolio, interactive, three.js]
    related_skills: [claude-design, browser-game-development, popular-web-designs]
---

# Three.js Interactive 3D Web Experiences

Use when building interactive 3D web experiences — portfolios, showcases, product demos, immersive landing pages — with Three.js and GLTF/GLB models. Covers module setup, model sourcing, scene composition, and cyberpunk/dark-theme 3D portfolio patterns.

## When to Use

- User asks for "a 3D site like jesse-zhou.com" or similar reference
- Building an interactive 3D portfolio, showcase, or product demo
- Loading and displaying GLTF/GLB models in a web page
- Creating a full-screen 3D environment with clickable objects

## Critical: What "3D Website" Means to Users

When users say "3D interactive website like [reference]", they mean:
- **Real modeled 3D environments** loaded from GLTF/GLB files
- Full-screen canvas with orbit controls (drag to rotate, scroll to zoom)
- Clickable objects that trigger UI (modals, panels)

They do NOT mean (all repeatedly rejected as "basic" / "not real 3D"):
- Abstract particle systems or floating spheres
- Procedural geometry (cubes/cylinders pretending to be furniture)
- 2D cards with 3D parallax or tilt effects
- CSS 3D transforms on flat elements

## Three.js r160+ Module Setup

Use importmap — required for addon imports (GLTFLoader, OrbitControls):

```html
<script type="importmap">
{
    "imports": {
        "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
        "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/"
    }
}
</script>
<script type="module">
    import * as THREE from 'three';
    import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
    import { GLTFLoader } from 'three/addons/loaders/GLTFLoader.js';
    import { DRACOLoader } from 'three/addons/loaders/DRACOLoader.js';
</script>
```

**Do NOT** use old `<script src="three.min.js">` — breaks addon imports.

## GLTF Model Loading

```js
const dracoLoader = new DRACOLoader();
dracoLoader.setDecoderPath('https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/libs/draco/');
const gltfLoader = new GLTFLoader();
gltfLoader.setDRACOLoader(dracoLoader);

gltfLoader.load(url, (gltf) => {
    const model = gltf.scene;
    model.traverse((child) => {
        if (child.isMesh) {
            child.castShadow = true;
            child.receiveShadow = true;
        }
    });
    scene.add(model);
    // Auto-frame camera on model
    const box = new THREE.Box3().setFromObject(model);
    const center = box.getCenter(new THREE.Vector3());
    controls.target.copy(center);
}, (xhr) => {
    if (xhr.total) {
        const pct = Math.round((xhr.loaded / xhr.total) * 100);
        // Update progress bar
    }
}, (err) => console.error(err));
```

## Finding Free GLTF Models

See `references/gltf-model-sources.md` for Sketchfab API search patterns, known good models, and licensing.

## Dark / Cyberpunk 3D Scene Recipe

Essential ingredients for a premium 3D portfolio:

1. **Full-screen canvas** — scene fills viewport, UI as fixed overlays
2. **Renderer**: `ACESFilmicToneMapping`, `toneMappingExposure: 1.2`, `PCFSoftShadowMap`, `SRGBColorSpace`
3. **Fog**: `FogExp2(bgColor, 0.04)` for atmospheric depth
4. **Multi-light**: ambient (dim) + directional (moonlight) + 2–3 colored PointLights (neon red/blue)
5. **Reflective floor**: `MeshStandardMaterial({ roughness: 0.3, metalness: 0.8 })`
6. **Floating particles**: 100–150 Points, `AdditiveBlending`, slow drift
7. **OrbitControls**: damping on, `maxPolarAngle < PI/2` (no under-floor view)
8. **Raycasting hotspots**: ring + dot meshes with pulsing opacity, click opens modal
9. **GSAP camera tween**: smooth zoom to hotspot on click
10. **Custom cursor**: neon dot + ring, slight lag on ring
11. **Loading screen**: progress bar from GLTF loader's onProgress

## Pitfalls

- **Light theme on neon 3D scenes**: nearly impossible to look good. Stick to dark.
- **Procedural rooms from primitives**: cubes/cylinders never pass as "real 3D". Always use actual GLTF models.
- **Feature overload**: adding terminal, playable game, synthesizer, day/night toggle simultaneously = cluttered. Get core 3D experience solid first, add features incrementally.
- **Text over 3D**: use fixed-position overlays, not CSS transforms fighting 3D perspective.
- **Old Three.js global + ES module addons**: breaks. Must use importmap for r128+.
- **Sketchfab downloads need API token**: search is free, download requires auth. Programmatic signup fails silently ("Registration unexpectedly failed") even without visible CAPTCHA — manual account creation is required.
- **Always import and wire DRACOLoader**: Many models (including three.js official examples like LittlestTokyo.glb) are Draco-compressed. Without DRACOLoader you get `No DRACOLoader instance provided` — a silent failure that shows no visible error except a black canvas and error callback.
- **`clock.getElapsedTime()` + `clock.getDelta()` conflict**: calling both in the same animation loop produces wrong delta values. `getElapsedTime()` internally calls `getDelta()` and resets the timer, so a subsequent `getDelta()` returns ~0. Fix: use only `getDelta()` and accumulate elapsed manually: `const dt = clock.getDelta(); elapsed += dt;`
- **GLB files need a local server**: models loaded from `file://` fail due to CORS. Always serve via `python -m http.server` or similar. Remind the user they can't double-click index.html.
- **Browser cache after code fix**: if a user reports the same error after you patched the JS, it's likely cached old code. Use cache-busting query string (`?t=Date.now()`) or instruct Ctrl+Shift+R.
- **RawShaderMaterial keeps GLSL1 syntax**: `attribute`/`varying`/`texture2D`/`gl_FragColor` shaders only work as-is in `RawShaderMaterial`. Three auto-prefixes `#version 300 es` + `#define attribute in` conversions for non-raw materials only — moving a raw shader to `ShaderMaterial` without converting syntax breaks compilation.
- **ResizeObserver + `renderer.setSize()` feedback loop**: observing a container while calling `setSize()` inside the callback re-triggers the observer → "ResizeObserver loop completed with undelivered notifications" spam. Guard on actual size change and rAF-debounce; cancel the pending frame in cleanup. See `references/shader-particles-harness.md`.
- **`document.hidden` gating hides output in headless harnesses**: pausing the render loop when hidden is correct for prod, but automated-browser screenshots run with `visibilityState: hidden`, so the canvas stays black. Manual `renderer.render(scene, camera)` still draws — use it plus `renderer.info.render.calls` to isolate loop-vs-shader failures.
- **Missing Tailwind in a test harness explodes canvas sizing**: shadcn components assume `relative/h-full/w-full/block/overflow-hidden` exist. Without Tailwind (e.g. plain Vite scaffold), the canvas↔container feedback loop can produce absurd canvas heights (observed 1066×16356). Add the minimal utility equivalents to index.css.
- **three r186 deprecates `THREE.Clock`**: console warns "Please use THREE.Timer instead." Harmless, but prefer `Timer` in new code.
- **Diagnosing black-canvas particle scenes**: expose `window.__dbg` hooks (load state, particle counts, `{renderer, scene, camera, object3D, uniforms}`), check `renderer.info.render` after a forced render, and force uniform values to separate data/loop/shader causes. Full recipe in `references/shader-particles-harness.md`.
