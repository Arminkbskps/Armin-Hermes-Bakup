---
name: persian-social-posters
description: "Use when designing Persian social media news posters."
version: 1.1.0
author: Armin & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [poster, telegram, social-media, persian, typography, design, 16x9]
---

# Persian Social Media Posters & News Graphics

Design publication-grade 16:9 news posters and thumbnails for Persian Telegram channels (such as `@ai_pro_center` reference style: post 1473).

## Visual Structure & Workflow

### 1. Photographic Background & Dramatic Lighting
- **Cinematic Atmosphere**: Use real, dramatic photographic environments (night skylines, dusk horizons, rocket launches, or industrial complexes) with warm amber/golden horizon glows and deep dark upper-right skies (brightness < 30 RGB).
- **Avoid Washed-Out Fog**: Never use flat white/slate milky overlays (e.g., 80% opacity `#f4f7fb` fog); they wash out contrast and look unpolished. The upper-right quadrant must be deep midnight dark to ensure >15:1 contrast for white headlines.

### 2. Left Visual Focal Points
- **Thematic 3D & Tech Elements**: Feature authentic visual subjects (flags, official profile badges, glowing quantum/AI processor chips with cyan PCB circuitry traces extending into the dark ground).
- **No Generic Browser Windows**: Avoid desktop-tutorial wireframes (e.g. browser windows with macOS red/yellow/green dots). Instead, present social profile assets as sleek, dark glassmorphism cards with glowing neon rims and authentic verified badges.

### 3. Typographic Rules (صرفاً تیتر)
- **3-Line High-Impact Stack (Right-Aligned RTL)**:
  - Line 1 (Size ~115pt): Setup (e.g. `ایلان ماسک رسماً از` or `کره جنوبی وارد رقابت`) in pure white `IRANSansX-Black` or `Tahamtan`.
  - Line 2 (Size ~125pt): Core Hook inside a vibrant royal electric-blue rounded rectangle (`#0f7cff` or `#1d9bf0`).
  - Line 3 (Size ~115pt): Punchline (e.g. `رونمایی کرد!` or `هوش مصنوعی شد!`) in pure white.
- **Pure Headline Only**: Do NOT clutter with long paragraphs, explanatory subtitles, or fine print unless requested.
- **Emoji Rendering in PIL**: TTF fonts like IRANSansX lack Apple color emojis and render as blank/tofu boxes in PIL. Avoid passing raw Unicode emojis into PIL `draw.text`; use clean punctuation (`!`) or composited vector icons.

### 4. Layout & Branding
- **Canvas**: Standard 16:9 (`1920x1080`).
- **Margins & Spacing**: Maintain at least **200px of clear breathing space** between the right edge of the visual card on the left and the left edge of the headline banner on the right.
- **Watermark**: Telegram circular blue paper-plane icon + `@ai_pro_center` in white bold font in the bottom-right corner.
