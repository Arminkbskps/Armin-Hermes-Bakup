---
name: lenis-scroll
description: "Smooth scroll integration with GSAP, React, and native web."
version: 0.1.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Smooth Scroll, Lenis, GSAP, Animation, React]
    related_skills: [gsap-core, gsap-scrolltrigger, gsap-react]
---

# Lenis Smooth Scroll Skill

Implement high-performance, accessible smooth scrolling using Lenis, with seamless integration into GSAP ScrollTrigger, React, Vue, and vanilla web applications.

## When to Use

- Building creative landing pages, portfolios, and agency websites requiring silky smooth scrolling.
- Coordinating GSAP ScrollTrigger animations with momentum/inertia scroll without jank.
- Building parallax effects, WebGL camera sync, or horizontal scroll containers.
- Replacing legacy scroll jackers (like Locomotive Scroll) with a modern native-scroll wrapper.
- Don't use for: Dense data dashboards, admin tables, or forms where inertia scrolling hampers productivity.

## Prerequisites

- Node.js >= 18.
- Package installation via project's package manager:
  ```bash
  npm install lenis
  # Or for React projects:
  npm install lenis @types/react
  ```

## Integration Patterns

### 1. Vanilla JavaScript (Modern Loop)

```javascript
import Lenis from 'lenis'
import 'lenis/dist/lenis.css'

const lenis = new Lenis({
  duration: 1.2,
  easing: (t) => Math.min(1, 1.001 - Math.pow(2, -10 * t)),
  smoothWheel: true,
  touchMultiplier: 2,
})

function raf(time) {
  lenis.raf(time)
  requestAnimationFrame(raf)
}

requestAnimationFrame(raf)
```

### 2. GSAP ScrollTrigger Sync (Crucial)

Lenis and GSAP ScrollTrigger must share the same ticker to avoid desync and stutter:

```javascript
import Lenis from 'lenis'
import gsap from 'gsap'
import { ScrollTrigger } from 'gsap/ScrollTrigger'
import 'lenis/dist/lenis.css'

gsap.registerPlugin(ScrollTrigger)

const lenis = new Lenis()

// Sync ScrollTrigger updates with Lenis scroll events
lenis.on('scroll', ScrollTrigger.update)

// Hook Lenis into GSAP ticker instead of a standalone requestAnimationFrame
gsap.ticker.add((time) => {
  lenis.raf(time * 1000)
})

// Disable lag smoothing to prevent visual skips
gsap.ticker.lagSmoothing(0)
```

### 3. React / Next.js Setup

```tsx
'use client'
import { ReactLenis, useLenis } from 'lenis/react'
import 'lenis/dist/lenis.css'

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <ReactLenis root options={{ lerp: 0.1, duration: 1.2, smoothWheel: true }}>
      {children}
    </ReactLenis>
  )
}
```

## Pitfalls & Best Practices

- **Never combine with CSS `scroll-behavior: smooth`:** Having both causes competing scroll calculations, leading to intense shaking or stutter. Always remove `html { scroll-behavior: smooth; }`.
- **CSS Import is Required:** Always include `import 'lenis/dist/lenis.css'`. Without it, Lenis cannot properly manage overflow and layout bounds.
- **Anchor Link Scrolling:** Native hash navigation works, but for animated transitions use `lenis.scrollTo('#target', { offset: -50 })`.
- **Accessibility:** Respect user preference for reduced motion:
  ```javascript
  const prefersReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
  if (prefersReducedMotion) lenis.destroy()
  ```
- **Cleanup in Single-Page Apps:** Call `lenis.destroy()` on component unmount to prevent duplicate scroll listeners.

## Verification

- Inspect that `html.lenis` classes are applied on document root.
- Verify smooth scrolling with mouse wheel and trackpad with zero layout shift.
- In devtools console: `window.lenis?.isScrolling` reports true during motion and false when idle.
