---
name: persian-social-posters
description: "Use when designing Persian social media news posters."
version: 1.0.0
author: Armin & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [poster, telegram, social-media, persian, typography, design, 16x9]
---

# Persian Social Media Posters & News Graphics

Design publication-grade 16:9 and square news posters and infographics for Persian Telegram channels (such as `@ai_pro_center`) and Instagram feeds.

## Workflow

### 1. Asset Handling & Theme Selection
- **Feature Real Screenshots**: When the user provides a screenshot (social media post, benchmark, tweet, paper, or dashboard), integrate the **authentic screenshot**. Crop cleanly and present it inside a sleek floating window/device frame with subtle drop shadows. Never replace real user screenshots with generic fake mockups.
- **Theme Selection (Light vs. Dark)**: Do NOT default to pitch-black, starry, or cyberpunk themes unless explicitly requested. If the source material is light-mode or the news is corporate/editorial, use clean, modern light styling (soft slate `#f8fafc` wash, frosted glass, or authentic photographic backdrops with an 80–90% light overlay).

### 2. Typographic Rules (صرفاً تیتر)
- **3-Line Punchy Headline**:
  - Line 1: Context/Setup (e.g., `خداحافظ AI، سلام به`) in high-contrast bold display font (**Tahamtan** or **IRANSansX-Black**).
  - Line 2 (Focal Hook): Keyword placed inside a vibrant rounded rectangular banner (e.g., Electric Blue `#1d9bf0` or Brand Accent).
  - Line 3: Strong takeaway/punchline (e.g., `تولد ابرهوش ایلان ماسک`).
- **No Clutter**: Keep the poster purely focused on the headline. Avoid long explanatory subtitles, paragraph blocks, or fine print unless explicitly requested.
- **Bidi Punctuation Trap**: Avoid placing trailing ASCII exclamation marks (`!`) directly at the end of pure Persian strings without bidi markers, as RTL renderers may flip them to the visual right (beginning of the line). Place Latin/English text with its own punctuation inside distinct text calls or clean banner badges.

### 3. Spatial Layout & Proportions
- **Canvas Ratio**: Standard 16:9 (`1920x1080` or `1280x720`).
- **Two-Column Split**:
  - Left Side: Visual asset / floating screenshot window (`~700–740px` wide).
  - Right Side: Right-aligned Persian headline anchor (`W - 100px`).
- **Breathing Room Gate**: Maintain at least **150px of clear space** between the right edge of the visual card and the left edge of the headline/banner. Avoid narrow gaps (<50px) that cause visual tension.
- **Branding**: Position channel watermark (e.g., `@ai_pro_center`) discreetly in the bottom-right corner with a clean accent dot.
