---
name: vanta-js
description: "Animated 3D Three.js and WebGL backgrounds for web apps."
version: 0.1.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ThreeJS, WebGL, 3D Backgrounds, Vanta, Canvas]
    related_skills: [threejs-3d-web, browser-game-development]
---

# Vanta.js 3D Backgrounds Skill

Add interactive, GPU-accelerated 3D backgrounds (Waves, Net, Birds, Fog, Halo, Rings, Clouds) to modern web applications using Three.js and Vanta.js.

## When to Use

- Adding dynamic, interactive 3D particle or wave backgrounds to hero headers and landing pages.
- Replacing heavy background videos with lightweight, interactive WebGL canvases (~120KB gzipped).
- Building visual tech demos, sci-fi/dark-mode theme aesthetics, or creative landing pages.
- Don't use for: Plain content pages, reading-heavy articles, or low-power mobile applications where battery drain is a concern.

## Available Effects & Dependencies

Most effects require **Three.js** (recommended version `r134` or compatible `0.134.x`):
- `vanta.waves`: 3D ocean/geometric wave mesh with light reflection.
- `vanta.net`: Connected particle nodes that react to cursor proximity.
- `vanta.birds`: Flocking simulation with 3D wings and depth.
- `vanta.fog`: Soft, shifting 3D volumetric fog layers.
- `vanta.halo`: Concentric energetic light rings.
- `vanta.rings`: Interlocking 3D geometric gyro rings.
- `vanta.trunk`: Procedural 3D branching structures (requires `p5.js`).

## Installation & Setup

### 1. Modern NPM / Vite / Next.js Setup

```bash
npm install vanta three
```

Note: In TypeScript or Next.js, declare ambient module types if missing:
```typescript
// types/vanta.d.ts
declare module 'vanta/dist/vanta.waves.min'
declare module 'vanta/dist/vanta.net.min'
declare module 'vanta/dist/vanta.birds.min'
```

### 2. React / Next.js Lifecycle (Mount & Mandatory Cleanup)

Always store the effect instance in a `ref` and call `.destroy()` when unmounting to prevent WebGL context leaks:

```tsx
'use client'
import { useEffect, useRef } from 'react'
import * as THREE from 'three'
import WAVES from 'vanta/dist/vanta.waves.min'

export default function HeroBackground() {
  const vantaRef = useRef<HTMLDivElement>(null)
  const effectRef = useRef<any>(null)

  useEffect(() => {
    if (!effectRef.current && vantaRef.current) {
      effectRef.current = WAVES({
        el: vantaRef.current,
        THREE,
        mouseControls: true,
        touchControls: true,
        gyroControls: false,
        minHeight: 200.00,
        minWidth: 200.00,
        scale: 1.00,
        scaleMobile: 1.00,
        color: 0x111111,
        shininess: 35.00,
        waveHeight: 15.00,
        waveSpeed: 0.75,
        zoom: 0.85,
      })
    }

    return () => {
      if (effectRef.current) {
        effectRef.current.destroy()
        effectRef.current = null
      }
    }
  }, [])

  return (
    <div ref={vantaRef} className="relative w-full h-screen overflow-hidden">
      <div className="relative z-10 flex items-center justify-center h-full">
        <h1 className="text-white text-5xl font-bold">Your Content Here</h1>
      </div>
    </div>
  )
}
```

### 3. Vanilla HTML / CDN Usage

```html
<div id="vanta-bg" style="width: 100%; height: 100vh;"></div>

<script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/vanta@latest/dist/vanta.net.min.js"></script>
<script>
  const effect = VANTA.NET({
    el: "#vanta-bg",
    mouseControls: true,
    touchControls: true,
    gyroControls: false,
    minHeight: 200.00,
    minWidth: 200.00,
    scale: 1.00,
    scaleMobile: 1.00,
    color: 0xff3f81,
    backgroundColor: 0x151515,
    points: 10.00,
    maxDistance: 22.00,
    spacing: 16.00
  })
</script>
```

## Pitfalls & Best Practices

- **WebGL Context Leaks:** Failing to call `effect.destroy()` on navigation or re-render will accumulate WebGL contexts until the browser throws `"Too many active WebGL contexts"`. Always clean up!
- **Text Readability & Contrast:** 3D canvases can overwhelm foreground text. Place a semi-transparent dark overlay (`bg-black/40` or gradient overlay) between the canvas and content.
- **Mobile Performance Optimization:**
  - Increase `spacing` or decrease `points` on mobile devices.
  - Set `scaleMobile: 0.5` or `touchControls: false` to reduce battery drain.
  - Disable entirely if `window.matchMedia('(max-width: 768px)').matches` and low battery mode is desired.
- **Container Sizing:** The container element must have explicit CSS dimensions (`height: 100vh`, `min-h-[500px]`, etc.); otherwise the canvas renders with 0 height.

## Verification

- Canvas element `<canvas class="vanta-canvas">` is injected into the container.
- Moving the mouse across the container animates or rotates the 3D perspective.
- Browser DevTools shows smooth 60fps rendering in the Performance tab with no repeated memory allocation spikes.
