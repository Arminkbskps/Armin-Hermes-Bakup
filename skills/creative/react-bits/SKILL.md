---
name: react-bits
description: "Animated React components, text loops, and backgrounds."
version: 0.1.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [ReactBits, Text Animations, Backgrounds, MicroInteractions, React]
    related_skills: [ui-ux-pro-max, lenis-scroll, vanta-js]
---

# React Bits Skill

Integrate high-quality, animated, interactive React components and micro-interactions from React Bits (200+ components: text effects, 3D cards, particle backgrounds, and dock menus).

## When to Use

- Building animated hero headings (Text Loop, Split Flap, Particle Text, Warp Text, Masked Heading).
- Adding interactive backgrounds (particle waves, grid distorts, animated gradients, light beams).
- Adding modern micro-interactions (magnetic buttons, card tilt, dock menus, animated tabs).
- When looking for shadcn-compatible animated React patterns without heavy custom physics engines.

## Installation & Setup

React Bits components are typically copy-pasted or installed via Tailwind CSS + Framer Motion:

```bash
npm install framer-motion clsx tailwind-merge lucide-react
```

### Common Tailwind Setup (`tailwind.config.js`)

Ensure keyframe animations and extended utilities are enabled in your Tailwind configuration:

```javascript
/** @type {import('tailwindcss').Config} */
module.exports = {
  theme: {
    extend: {
      animation: {
        'text-reveal': 'text-reveal 1.5s cubic-bezier(0.77, 0, 0.175, 1) forwards',
      },
      keyframes: {
        'text-reveal': {
          '0%': { transform: 'translate(0, 100%)', opacity: '0' },
          '100%': { transform: 'translate(0, 0)', opacity: '1' },
        },
      },
    },
  },
}
```

## Core Animation Patterns

### 1. Text Loop (Animated Cycling Headline)

```tsx
'use client'
import { useState, useEffect } from 'react'
import { motion, AnimatePresence } from 'framer-motion'

interface TextLoopProps {
  texts: string[]
  interval?: number
  className?: string
}

export function TextLoop({ texts, interval = 3000, className = '' }: TextLoopProps) {
  const [index, setIndex] = useState(0)

  useEffect(() => {
    const timer = setInterval(() => {
      setIndex((prev) => (prev + 1) % texts.length)
    }, interval)
    return () => clearInterval(timer)
  }, [texts.length, interval])

  return (
    <span className={`inline-block relative overflow-hidden align-bottom ${className}`}>
      <AnimatePresence mode="wait">
        <motion.span
          key={index}
          initial={{ y: 20, opacity: 0 }}
          animate={{ y: 0, opacity: 1 }}
          exit={{ y: -20, opacity: 0 }}
          transition={{ duration: 0.35, ease: 'easeInOut' }}
          className="inline-block"
        >
          {texts[index]}
        </motion.span>
      </AnimatePresence>
    </span>
  )
}
```

### 2. Interactive Spotlight Card

```tsx
'use client'
import { useRef, useState } from 'react'

export function SpotlightCard({ children, className = '' }: { children: React.ReactNode, className?: string }) {
  const divRef = useRef<HTMLDivElement>(null)
  const [position, setPosition] = useState({ x: 0, y: 0 })
  const [opacity, setOpacity] = useState(0)

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!divRef.current) return
    const rect = divRef.current.getBoundingClientRect()
    setPosition({ x: e.clientX - rect.left, y: e.clientY - rect.top })
  }

  return (
    <div
      ref={divRef}
      onMouseMove={handleMouseMove}
      onMouseEnter={() => setOpacity(1)}
      onMouseLeave={() => setOpacity(0)}
      className={`relative overflow-hidden rounded-xl border border-neutral-800 bg-neutral-900/50 p-8 ${className}`}
    >
      <div
        className="pointer-events-none absolute -inset-px transition duration-300"
        style={{
          opacity,
          background: `radial-gradient(600px circle at ${position.x}px ${position.y}px, rgba(255,255,255,0.06), transparent 40%)`,
        }}
      />
      <div className="relative z-10">{children}</div>
    </div>
  )
}
```

## Pitfalls & Best Practices

- **Avoid excessive layout shifts (CLS):** Fixed heights for cycling text containers prevent jumping.
- **RTL Considerations:** For Persian/Arabic layouts, flip translate directions (`x: -20` vs `x: 20`) or use directional tokens.
- **Reduced Motion:** Wrap Framer Motion transforms with `useReducedMotion()`:
  ```tsx
  import { useReducedMotion } from 'framer-motion'
  const shouldReduceMotion = useReducedMotion()
  ```
- **SSR Hydration:** When using randomized particle effects or client mouse coordinates, defer initialization until after component mount (`useEffect`).
