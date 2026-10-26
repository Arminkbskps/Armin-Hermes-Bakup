---
name: vengence-ui
description: "Next-gen animated buttons, borders, and marketing UI blocks."
version: 0.1.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [VengeanceUI, Animated Buttons, Tailwind, Framer Motion, Hero UI]
    related_skills: [ui-ux-pro-max, react-bits, lenis-scroll]
---

# Vengeance UI Skill

Build next-generation interactive marketing UI components (Candy buttons, Pop buttons, Animated borders, dynamic tooltips, and interactive hero blocks) using Tailwind CSS and Framer Motion.

## When to Use

- Designing high-converting SaaS landing pages, marketing sites, and product showcases.
- Adding playful yet polished animated call-to-action buttons (Candy Button, Gradient Border Button, Shimmer Button).
- Creating interactive bento grids, hover cards, and animated status badges.
- Upgrading standard shadcn buttons with magnetic hover, gradient sweeps, and click pops.

## Installation & Setup

```bash
npm install framer-motion clsx tailwind-merge
```

### Supporting Helper (`cn` utility)

```typescript
// lib/utils.ts
import { clsx, type ClassValue } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}
```

## Signature Component Patterns

### 1. Candy Button (Juicy 3D Pop Effect)

```tsx
'use client'
import React from 'react'
import { motion } from 'framer-motion'
import { cn } from '@/lib/utils'

interface CandyButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode
  variant?: 'primary' | 'crimson' | 'emerald'
}

export function CandyButton({ children, className, variant = 'primary', ...props }: CandyButtonProps) {
  const colorMap = {
    primary: 'from-violet-500 to-indigo-600 shadow-indigo-500/30',
    crimson: 'from-rose-500 to-red-600 shadow-red-500/30',
    emerald: 'from-emerald-400 to-teal-600 shadow-teal-500/30',
  }

  return (
    <motion.button
      whileHover={{ scale: 1.04, y: -2 }}
      whileTap={{ scale: 0.96, y: 1 }}
      transition={{ type: 'spring', stiffness: 400, damping: 17 }}
      className={cn(
        'relative inline-flex items-center justify-center px-6 py-3 font-semibold text-white rounded-2xl',
        'bg-gradient-to-b shadow-lg active:shadow-md transition-shadow select-none overflow-hidden cursor-pointer',
        colorMap[variant],
        className
      )}
      {...props}
    >
      {/* Top glossy shine highlight */}
      <span className="absolute top-0 inset-x-0 h-1/2 bg-gradient-to-b from-white/25 to-transparent pointer-events-none rounded-t-2xl" />
      <span className="relative z-10">{children}</span>
    </motion.button>
  )
}
```

### 2. Animated Border Card (Neon Trace)

```tsx
'use client'
import React from 'react'
import { cn } from '@/lib/utils'

export function AnimatedBorderCard({ children, className }: { children: React.ReactNode, className?: string }) {
  return (
    <div className={cn('relative p-[1px] rounded-2xl overflow-hidden group', className)}>
      <div className="absolute inset-0 bg-gradient-to-r from-transparent via-cyan-500 to-transparent translate-x-[-100%] group-hover:translate-x-[100%] transition-transform duration-1000 ease-in-out" />
      <div className="relative bg-neutral-950 p-6 rounded-2xl border border-neutral-800">
        {children}
      </div>
    </div>
  )
}
```

## Pitfalls & Best Practices

- **Avoid 3D skewing on text:** Keep button text completely flat and legible while animating borders or container scales.
- **Mobile Touch State:** On mobile devices without hover, ensure `active:` styles provide instant tactile feedback without sticky hover states.
- **Button Sizing:** Maintain minimum touch targets (at least 44×44px on mobile devices).
