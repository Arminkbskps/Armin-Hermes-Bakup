---
name: telegram-channel-content-bots
description: "Use when building Telegram channel content bots."
version: 1.1.0
author: Armin & Hermes
license: MIT
metadata:
  hermes:
    tags: [telegram, content-bots, aiogram, scraper, multi-provider, token-optimization, channel-publishing]
---

# Telegram Channel Content Automation Bots

Class-level engineering guide for single-file, long-running Telegram channel content automation bots (scraping sources via `t.me/s`, ad and duplicate filtering, multi-provider AI rewrites, admin review panels, and editorial workflows).

## 1. Environment & Path Portability
- **The Container Path Crash**: When hosting bots on Pterodactyl/HidenCloud (`/home/container`), hardcoding paths like `BASE_DIR = Path("/home/container/Bot 4")` at the module level causes `PermissionError: [Errno 13] Permission denied: '/home/container'` during local testing, linting, or offline execution on other environments.
- **Rule**: Always make container paths environment-adaptive:
  ```python
  BASE_DIR = Path("/home/container/Bot 4") if Path("/home/container").exists() else Path(__file__).resolve().parent
  ```

## 2. Preventing AI Token Amplification in Scraper Pipelines
When monitoring multiple public channels, naively chaining LLM calls for every scanned post (ad check + duplicate check + fact check + rewrite) causes catastrophic token consumption (3–4 LLM calls per post).
- **Heuristic Ad Exemption for Tech Pricing**: In tech/AI news, pricing terms (`$`, `سنت`, `قیمت`, `تومان`, `اشتراک`) frequently appear in legitimate model announcements. Standard ad filters penalize these words and trigger expensive LLM ad judges.
  - Exclude commercial keywords from ad penalties when technical terms (`مدل`, `توکن`, `api`, `chatgpt`, `openai`) are present.
  - Enforce strict heuristic thresholds: if `score < 35`, immediately mark as non-ad without calling AI. If `score >= 75` with blatant commercial markers (`پکیج`, `سیگنال`, `ثبت نام با کد تخفیف`), mark as ad directly without AI.
- **Indexed Hash Check Before Fuzzy Matching**:
  - Check exact content hashes via indexed SQL queries (`SELECT id FROM incoming_posts WHERE content_hash = ? LIMIT 1`) for $O(1)$ instant duplicate rejection.
  - When running fuzzy string similarity (`token_set_ratio`), never scan the entire historical database without limits. Restrict comparison to a rolling window (e.g. `LIMIT 150` or last 15 days). If similarity is `< 50%`, bypass the AI duplicate check completely.

## 3. Resilient Multi-Provider AI Fallback Chaining
Relying on a single AI provider (e.g. Google AI Studio) with a broken or disabled secondary fallback (e.g. unconfigured `g4f`) causes the bot to freeze or throw unhandled `RuntimeError` exceptions when rate limits hit.
- **Cross-Provider Priority Chain**:
  1. Primary: Google AI Studio (`gemini-flash-lite-latest` or `gemini-2.0-flash`).
  2. Secondary: OpenRouter free models (`deepseek/deepseek-r1:free`, `meta-llama/llama-3.3-70b-instruct:free`).
  3. Tertiary: GitHub Models (`https://models.inference.ai.azure.com` with free GitHub tokens).
  4. Quaternary: Safe fallback generator (clean text extraction with channel signature) so the pipeline NEVER crashes or stops processing updates.
- **Status-Code-Differentiated Key Cooldowns**:
  - `401 / 403` (Deleted service account or invalid key): Permanently disable the key (`enabled = 0`). Never leave it in rotation.
  - `429` (Rate limit): Brief cooldown (90–120 seconds). Never set a 20-minute uniform cooldown for rate limits.
  - `500 / 503` (Server error): Short cooldown (30–60 seconds).
- **Token Output Ceilings**: Cap `maxOutputTokens` to 1,000–1,200 for Telegram channel rewrites. Setting 2,200+ tokens wastes quota and doubles latency for 100–150 word posts.

## 4. Anti-Freeze Protection in Inline Keyboard Handlers
- When an inline button (such as `🔁 بازنویسی` or `✨ فرمت‌دهی`) triggers an external API call, any unhandled exception crashes the Telegram dispatcher event handler and leaves the user's message permanently stuck on a loading state (e.g. `در حال بازنویسی...`).
- **Rule**: Always wrap callback action bodies in `try...except Exception as e:`. On error, revert the message back to its functional review state with inline buttons and display an actionable pop-up alert using `await callback.answer(f"خطا: {e}", show_alert=True)`.

## 5. Publishing Boundaries: Draft Review vs. Direct Channel Publishing
- **Default Policy (Draft Assistant Only)**: Content automation bots must NOT publish directly or automatically to public channels by default. Keep the bot strictly in drafting / review assistant mode within the admin's private chat.
- **No Unsolicited Publish Buttons**: Unless the user explicitly asks for direct publishing into the public channel, omit channel publish buttons from the review keyboard. The standard workflow is for the admin to review, edit, and copy the post manually.
- **When Direct Publishing is Explicitly Requested**:
  - Enforce Telegram's 1,024-character caption limit on media (`send_photo`, `send_video`, `send_animation`).
  - If `len(post_text) <= 1020`, send media with `caption=post_text`.
  - If longer, send the complete text message first, then send media as a reply (`reply_parameters=ReplyParameters(...)`).

## 6. Mobile UX Enhancements for Channel Admins
- **One-Tap Clean Copy**: Provide a `📋 کپی تمیز` callback button that renders the complete text inside `<code>...</code>` HTML tags. Tapping a monospace code block in Telegram mobile copies the entire text to the clipboard in one tap without selecting UI metadata or headers.
- **Ultra-Short Breaking News Variant**: Include a `⚡ تیتر و خلاصه فوری` preset for breaking news, generating a 2-line punchy hook suitable for fast viral dissemination.
- **Database Hygiene**: Run `PRAGMA wal_checkpoint(PASSIVE)` at bot startup and periodically in maintenance loops to prevent SQLite `.sqlite3-wal` files from accumulating multi-megabyte disk bloat on low-storage VPS hosts.
