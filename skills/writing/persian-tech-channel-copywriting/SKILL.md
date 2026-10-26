---
name: persian-tech-channel-copywriting
description: Use when writing Persian tech news and AI posts.
version: 1.1.0
author: Armin & Hermes
license: MIT
metadata:
  hermes:
    tags: [persian, telegram, copywriting, tech-news, ai, social-media]
    related_skills: [persian-writing, persian-colloquial-prompts]
---

# Persian Tech Channel Copywriting

Write punchy, high-signal Persian tech news, benchmark breakdowns, and viral AI media captions for Telegram channels (such as `@ai_pro_center`) and social media feeds.

## Core Formats

### 1. Viral Media & Video Reaction (Ultra-Short, 2 Lines)
Use when sharing AI videos, 3D animations, generative clips, or audio demos. Do not drown the media in paragraphs. Always offer two variants (Option 1: ultra-short viral punchy hook; Option 2: technical breakdown highlighting camera tracking, physics, and rendering fidelity).
- **Line 1 (The Hook):** A punchy, authentic reaction to the technical feat (fidelity, lighting, physics, facial expressions, camera movement).
- **Line 2 (Attribution / Breakdown):** The exact model, generator name, or technical bullet points.
- **Artistic & Masterpiece Names:** When referencing world-famous paintings, artworks, or pop-culture classics (e.g. *Liberty Leading the People*, *The Last Supper*), always use the authentic English title or standard transliteration rather than obscure literal Persian calques that sound awkward (e.g. use «Liberty Leading the People» or «لیبرتی لیدینگ د پیپل» instead of «آزادی هدایت‌گر مردم»).
- **Media Delivery:** Always deliver the video or image directly with the post (`MEDIA:/path/to/media.mp4`) so the user can immediately publish it to Telegram.
- **Example:**
  ```text
  فیزیک مو، میمیک چهره و انتقال حس... رسماً با خروجی پیکسار مو نمی‌زنه! 🤯🎬
  ساخته‌شده با مدل ویدیوساز جدید Seedance 2.5 ⚡️

  @ai_pro_center
  ```

### 2. Model Release & Benchmark Breakdown
Use for major model drops (Gemini, Claude, GPT, Grok) or benchmark updates (Artificial Analysis, LMSYS, SWE-bench).
- **Header:** `❗️` + Bold headline with 1–2 emojis.
- **Sub-hook:** 1 concise sentence summarizing the real-world milestone.
- **Bullets (2–4 Points Max):** Concrete figures only—intelligence index scores, cost per task (Pareto frontier), context window, specific test names (HLE, DeepSWE).
- **Closer:** 1 engaging discussion question followed by `🏴` and channel handle.

## Media Extraction & Inspection Workflows

### 1. Telegram Post Media Extraction
When given a raw Telegram post link (`https://t.me/<channel>/<id>`):
- Never rely on plain web extract of `t.me/<channel>/<id>` (it hides CDN media behind a web redirect).
- Fetch the embed widget endpoint via `https://t.me/<channel>/<id>?embed=1`. It exposes the unauthenticated `telesco.pe` CDN video/photo URLs and raw message text directly.

### 2. Vision Analysis of Video Frames
- When inspecting video frames with `vision_analyze` to understand scenes or verify absence of watermarks:
- Never send full-resolution raw frames or large montages (they frequently time out on vision APIs).
- Downscale frames to ~400–480px width (e.g. `424x232`) before calling `vision_analyze`. This eliminates timeouts while retaining complete detail for character costumes, physics, motion blur, and text detection.

### 3. Video Clean-up & Outro Trimming
When rewriting or packaging a post based on a video clip that contains third-party competitor branding, promotional end-cards, or creator watermarks (e.g. outro cards displaying handles like `@channel_id` or `@mgh_mobin`):
- **Exact Boundary Detection:** Sample frames backwards every 200–250ms from the end to detect the exact moment the speaker's last sentence/subtitle ends and the outro splash screen appears (inspect mean frame brightness and center pixel changes).
- **Smooth Cut & Audio Fade:** Cut with `ffmpeg -ss 0 -to <cutoff_sec> -i input.mp4 -af "afade=t=out:st=<cutoff_sec - 0.3>:d=0.3" ...` so the voiceover ends cleanly without cutting off the last word abruptly or letting any outro logo appear.
- **Delivery:** The delivered post must be accompanied by the clean trimmed video (`MEDIA:/path/to/trimmed.mp4`).

## Vocabulary & Register Rules

### 1. Banned Literal Corporate Idioms
Never translate technical corporate idioms literally.
- **Forbidden:** «بازوی هوش مصنوعی فلان شرکت» (sounds bizarrely anatomical in Persian).
- **Correct:** «شرکت هوش مصنوعی فلان» or «بخش هوش مصنوعی».

### 2. No Infantilizing or Nursery Vocabulary
Colloquial Persian for tech audiences must remain tech-savvy, sharp, and mature (رفیقانه، گنگ، فنی).
- **Forbidden:** Childish diminutives like «گربه تپلی»، «کوچولو»، «عروسکی».
- **Correct:** Technical observation in natural voice: «فیزیک مو»، «اکت و میمیک چهره»، «ثبات تصویر در زوم بی‌نهایت».

### 3. Combat Verbosity
- Never use academic padding: «در دنیای پرشتاب امروز»، «شایان ذکر است»، «از اهمیت بسزایی برخوردار است».
- If a post exceeds 6–8 short lines, cut it in half. State the insight directly without throat-clearing.
- Maintain Persian digits (۰-۹), proper ZWNJ (نیم‌فاصله), and clean punctuation.

### 4. Recency & Date Verification Before Pitching News
Never present historical AI milestones (such as capabilities, models, or benchmarks released months or years prior, e.g. Claude 3.5 Computer Use or old benchmark battles) as fresh or breaking news. Always verify the exact release date via search before pitching or tagging as breaking.

### 5. Direct Source Rewriting (No Topic Swapping)
When the user provides an existing text, excerpt, quote, or draft to rewrite («این رو بازنویسی کن / نمی خواد خودت پست جدید بزنی»), rewrite that *exact* subject into the channel's signature style. Do not discard their source text to invent or pitch an unrelated story.

### 6. Distinguish Channel Post Writing from Local Tool Execution
When the user shares a post or link about an open-source AI tool/framework (e.g. OpenDesign Motion, HyperFrames, Remotion) and asks «نظرت در مورد این چیه؟» or «از این برام یه پست بزن», pay close attention to follow-up steering:
- If the user clarifies they want the tool run or tested on the system («منظورم پست زدن نبود... منظورم این بود که رو سیستم خودت ران کنی»), do not continue drafting Telegram posts. Switch immediately to inspecting the repository, installing lightweight dependencies, and executing the requested generation or render.

### 7. Brand Marketing & Reel Production: Ground in Real Storefront Data
When producing promotional video scripts, reels, or marketing copy for real brands (e.g. `voidclubs.ir`):
- NEVER invent fantasy concepts, fake scarcity limits («فقط ۵۰ عدد»), or imaginary membership items («کارت تیتانیومی باشگاه») from thin air.
- Always inspect the live website or API (`/api/products`) first to extract actual catalog products, real titles (e.g. Better Call Saul / Lalo Salamanca double-exposure hoodie, anime/music collections), and actual product imagery.
- Never pair cinematic dark reels with robotic or flat TTS voiceovers. If human voiceover or ElevenLabs is unavailable, warn the user rather than delivering a mechanical robotic voice that ruins the production.

### 8. Social Media Carousel Video & Live Wallpaper Extraction
When user shares an Instagram/social post and asks for an embedded video or wallpaper:
- **Download Method:** Use `yt-dlp --playlist-items <N>` to target the video directly (avoids Instagram login walls that block scrapers like `gallery-dl`).
- **Desktop Live Wallpaper Adaptation:**
  - If the extracted video is in portrait aspect ratio (e.g. 1080x1440 or 9:16) and intended for desktop background (Lively Wallpaper / Wallpaper Engine):
  - **Edge Bleed Pitfall:** Never blindly apply an in-place edge feathering mask if the source artwork extends to the canvas border (non-zero edge luminance). Feathering full-bleed graphics eats into the visual elements and makes the artwork look cropped or cut off at the sides.
  - Inspect edge pixels first. If edges are already pure black (`#000000`), a smooth feather to 16:9 canvas works cleanly. If artwork touches the borders, either:
    1. Deliver the pristine original untouched video so wallpaper managers (Lively Wallpaper / Wallpaper Engine) can scale it natively (e.g. using Uniform Fill / Zoom mode).
    2. Or provide a blurred background fill (`[0:v]scale=2560:1440:force_original_aspect_ratio=increase,boxblur=25:5[bg];[bg][0:v]overlay=(W-w)/2:(H-h)/2`) instead of clipping edge pixels.
  - Always upload to Google Drive (`gdrive-upload`) and provide the official open-source GitHub download URL for Lively Wallpaper (`https://github.com/rocksdanister/lively/releases/latest`).
