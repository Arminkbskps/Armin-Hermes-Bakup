---
name: blobatar
description: "Deterministic geometric SVG blobatars with zero deps."
version: 0.1.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Blobatar, Avatars, SVG, React, UserProfile]
    related_skills: [ui-ux-pro-max, react-bits]
---

# Blobatar Skill

Generate deterministic, lightweight (under 4.5KB), geometric blob-style avatar faces from any string seed or user identifier with zero external dependencies.

## When to Use

- Generating consistent, playful user avatars from usernames, emails, or wallet hashes without server-side image storage.
- Implementing avatar fallbacks for comment sections, user profiles, team directories, and chat messages.
- Customizing avatar appearance with deterministic seed properties (expression, shape, hue).
- Replacing heavy Gravatar/BoringAvatars libraries with a zero-dependency ~4KB bundle.

## Installation & Setup

```bash
# Core package
npm install blobatar
# React wrapper (optional)
npm install @blobatar/react
```

## Usage Patterns

### 1. React Usage with Motion CSS

```tsx
import { Blobatar } from '@blobatar/react'
import 'blobatar/motion.css'

export function UserAvatar({ username }: { username: string }) {
  return (
    <div className="flex items-center gap-3">
      <Blobatar
        name={username}
        size={48}
        animate="hover"
        shape="round" // "round" | "squircle"
      />
      <span className="font-medium text-neutral-200">{username}</span>
    </div>
  )
}
```

### 2. Pure SVG / Vanilla JavaScript (No React Required)

```javascript
import { createBlobatar } from 'blobatar'

// Generates an inline SVG string deterministically from the input string
const svgString = createBlobatar('user_12345', {
  size: 64,
  expression: 'happy', // "happy" | "sleepy" | "wink" | "neutral"
  shape: 'round',
  hue: 210,
})

document.getElementById('avatar-container').innerHTML = svgString
```

## Props & Options Reference

| Property | Type | Default | Description |
|---|---|---|---|
| `name` | `string` | required | Input string seed (userId, username, email) |
| `size` | `number` | `40` | Width and height in CSS pixels |
| `shape` | `'round' \| 'squircle'` | `'round'` | Outer contour geometry |
| `expression` | `'auto' \| 'happy' \| 'sleepy' \| 'wink' \| 'chill'` | `'auto'` | Deterministic facial expression |
| `hue` | `number (0–360)` | derived from seed | Primary color hue angle |
| `animate` | `'none' \| 'hover' \| 'always'` | `'none'` | Micro-motion wiggle animation |

## Best Practices

- **Predictable Caching:** The output is completely deterministic; passing the exact same `name` string always renders identical geometry and colors.
- **Accessibility:** Always provide an accessible `aria-label` or `alt` text on the parent wrapper (e.g. `aria-label="آواتار کاربر آرمین"`).
- **Dark Mode Compatibility:** Blobatar uses vibrant hues with balanced saturation that render cleanly on both pure black (#000000) and light backgrounds.
