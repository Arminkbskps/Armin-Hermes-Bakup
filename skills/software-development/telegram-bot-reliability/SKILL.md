---
name: telegram-bot-reliability
description: 'Use when hardening long-running Telegram polling bots.'
---

# Telegram Bot Reliability

Class-level skill for single-file, long-polling content bots (aiogram,
python-telegram-bot/PTB, SQLite, t.me/s scrapers, AI rewrite pipelines). Use it
whenever a bot "dies after a few days", spams "rewrite failed", or needs ops
features (retry, digest, backup).

## When to use

- AI rewrite failures that cascade (one 503/429 kills all keys for hours).
- Fallback provider (g4f, second model) never actually works when primary fails.
- SQLite schema must evolve without wiping user data.
- User asks for ops add-ons: retry queue, per-key stats, digest, heartbeat,
  watchdog, backup, bulk approve, preview, feedback votes.

## Core workflow

1. **Diagnose from logs + DB, not guesses.**
   - Tail the log for the repeating triple: `Google HTTP <code>` →
     `No active key` → `AI rewrite failed`.
   - Count distinct HTTP codes and check `api_keys(cooldown_until, last_error)`.
   - Count AI calls per post (ad judge + duplicate judge + fact-check + rewrite
     easily 3-4x quota).
2. **Fix key rotation before adding features.**
   - Tiered cooldowns: transient (429/500/502/503/504, network) = 1-2 min;
     auth/config (400/401/403/404) = ~120 min. Never 20 min for everything.
   - Success MUST clear `cooldown_until` (the classic stuck-key bug).
   - Record per-call stats (success/error counters + daily table) and add a
     "reset all cooldowns" action. See `references/ai-key-rotation.md`.
3. **Queue failures instead of dropping them.**
   - Failed rewrite → `incoming_posts.status='rewrite_failed'` + row in
     `retry_queue` with exponential backoff (5m, 10m, 20m...), max ~5 tries.
   - A `retry_loop` picks up due rows; a manual Retry button calls the same
     path with `retry_of=<failed_id>`. See `references/retry-queue.md`.
4. **Migrate SQLite additively.**
   - `CREATE TABLE IF NOT EXISTS` for new tables, `ALTER TABLE ... ADD COLUMN`
     wrapped in `suppress(OperationalError)`, `set_default()` for new settings.
   - Never drop/recreate on upgrade. Smoke-test the migration SQL on a temp DB.
   - See `references/sqlite-migration.md`.
5. **Wire the fallback honestly.**
   - For g4f: enumerate providers, skip `needs_auth=True`, cap tries (5) and
     timeout (~300s), reject empty/`.har` responses, log which provider won.
   - If the fallback lib is missing, raise a clear error — never silent death.
   - Cross-provider fallback: In-provider model rotation fails when the account
     is suspended (e.g. Google returning 403 `Consumer api_key:... has been suspended`).
     Always chain across independent providers (`primary_provider -> openrouter free`),
     not just across models on the same account.
   - See `references/g4f-fallback.md`.
6. **Add ops loops as independent tasks.**
   - `scan_loop` stamps `last_scan_ok`; `digest_loop` (daily), `heartbeat_loop`
     (every 6h), `watchdog_loop` (alert when `now - last_scan_ok` exceeds
     3 intervals), `backup_loop` (weekly, WAL checkpoint before copy),
     `cleanup_loop` (TTL + VACUUM). See `references/ops-loops.md`.

## Scope discipline (learned the hard way)

- When the user cancels a sub-task ("don't fix #4", "remove multi-model"),
  revert it COMPLETELY: code + config constants + helper functions + call
  sites. Then verify zero remaining references (search_files for the symbol) and
  re-compile. A half-removed feature is worse than no feature.
- Keep single-model when asked: one `GOOGLE_MODEL` string, no model list, no
  "try next model" branch — but keep the tiered cooldowns.

## Verification (every change)

- `python -m py_compile bot.py` must pass.
- AST/grep check: every new `callback_data` prefix has a router handler;
  every new helper is actually called.
- Migration smoke test on a temp SQLite file (create old schema → run new
  ALTERs/CREATEs → exercise UPSERT paths).
- Confirm no leftover references to reverted features.

## Media-batch bots (transparent-PNG background changer pattern)

- In-code config when the user asks for it: `BOT_TOKEN` / `SUPER_ADMIN` constants
  at the top of the single file, no `.env`/env lookups. Refuse to add env
  plumbing unprompted once the user says "everything in code".
- Batch intake: collect `Document` files (never `Photo` — Telegram recompresses
  photos) into a `PENDING[user_id]` list, cap at ~100, show
  "intake" keyboard with Run/Cancel, delete the user's upload messages quietly.
- Lossless recolor: `Image.alpha_composite(bg, rgba)` → save `PNG`
  (`optimize=False` to keep it fast), preserve `dpi` from `im.info`. Never
  resize. Verify with a 100x100 RGBA round-trip in the smoke test.
- Opaque inputs need a smart pipeline (the Printify lesson): external `src`
  images are usually OPAQUE, so plain `alpha_composite` is a silent no-op —
  the new color hides under the old background and the user reports "it did
  nothing". FIRST check whether the platform already serves a transparent
  original (Printify: `print_areas[].placeholders[].images[]` upload_id →
  `GET /v1/uploads/{id}.json` → `preview_url` — its own no-background
  download; recolor that directly, no AI). Only when no transparent source
  exists, gate with `has_transparency()` (alpha-channel minimum < 250):
  transparent → direct recolor; opaque → `remove_background()` first, then
  recolor. Removal chain (cloud-first — see weak-host rule below): free public
  HF Space (no token needed — see `references/hf-rmbg-free.md`), else a
  border-sampled flood fallback (median of edge pixels as bg guess, refuse
  when the transparent ratio is <2% or >98% so a bad guess never ships).
  NEVER run local rembg/onnxruntime on a weak deploy host (2-core shared
  Pterodactyl/VPS): first run downloads a ~176MB model, CPU inference pins
  one core at 100% for minutes (shows as "50% of 2 cores, low RAM" — a hang,
  not slowness), and rembg has no internal timeout so even `wait_for` ceilings
  can be outlasted. Tell: an `onnxruntime ... device_discovery` warning in the
  host log means rembg is installed there — delete the rembg branch (or
  `pip uninstall -y rembg onnxruntime`) and let AI run on the cloud Space.
  Refine EVERY cut (AI or flood) with `_refine_cut()` before recoloring —
  see `references/cut-refinement.md` — or dark recolors show a white halo and
  jagged edges. Report the path in the caption
  (`direct | removed_hf | removed_flood | opaque`) so the
  user sees what happened. Accept JPG/WebP uploads too, not just PNG.
- Progress: send one status message, `edit_message_text` at most every ~1.5s
  (Telegram flood limit), with a text bar (`progress_bar(done,total)`).
  Delete the status message when done; deliver a ZIP bundle + individual
  documents (ZIP via `zipfile.ZIP_DEFLATED` from disk paths).
- Windows venvs here often lack `pip`: install with
  `uv pip install --python "<venv>/Scripts/python.exe" ...`, then smoke-test
  with that exact interpreter (`-m py_compile` + `migrate()` + one
  `apply_background` call).
- Always state the final project path explicitly
  (e.g. `D:/Hermes file/<bot-dir>/bot.py` + `run.bat`) — the user wants the
  location named, not "some folder".

## Heavy per-callback work (anti-lock pattern — the frozen-bot lesson)

- Symptom: bot sticks on "⏳ processing..." and ALL handlers freeze — every
  user, every button, even sibling bots sharing the host/loop. Root causes
  found together in one session: (a) CPU-bound work (numpy/Pillow on 1200px
  images) running inline on the event loop; (b) absurd network budgets (180s
  timeout × 3 retries + sleep backoff ≈ 10 min stuck with zero feedback);
  (c) double-clicks spawning parallel heavy jobs on a weak host.
- Fix — apply all four together, never just one:
  1. `await asyncio.to_thread(cpu_fn, ...)` for every CPU-bound step (image
     processing, numpy, flood-fill). The event loop must never do pixel work.
  2. `await asyncio.wait_for(_do(), timeout=150.0)` ceiling over the whole
     download+process unit. On `asyncio.TimeoutError` show a timeout message
     with a Retry button — never silence, never hang.
  3. Per-user busy set: `PF_BUSY: set[int]`; if `uid in PF_BUSY` →
     `q.answer("a job is already running", show_alert=True)` and return.
     `add` before starting, `discard` in `finally` (success AND error paths)
     so the lock itself can never stick.
  4. Sane network budgets: ~45s file download / ~30s JSON API, max 2 retries,
     NO sleep-backoff inside user-facing handlers. Fail fast with a clear
     message + retry button instead of hanging on a spinner.
- Rule: every handler MUST resolve (success, error, or timeout message).
  "Stuck on spinner" is the worst outcome — it cascades to all users, so a
  regression test should assert the guard trio exists: `to_thread` +
  `wait_for` + busy-set add/discard.
- Two extra lock sources found in the same session (check both when a stuck
  spinner survives the trio): (a) the busy-guard referencing a stale variable
  name (`query` param vs `q.answer()` → NameError raised BEFORE try/finally,
  so the busy entry is never added/discarded and the NEXT attempt takes the
  lock path and also throws — a permanent lock; grep that every
  `PF_BUSY`-style guard uses the handler's actual param name); (b) expensive
  morphology (MinFilter/Blur) run on the FULL-size image instead of the
  downscaled mask — on a 2-core host one Pillow filter pass pins a core at
  100% (shows as "50% of 2 cores, low RAM" — a hang, not slowness). Do
  erode+threshold on the small mask, upscale after, then one light blur.

## Long-Polling Timeout vs HTTP Socket Timeout

- In Telegram/Bale long-polling, `getUpdates` passes a `timeout` parameter (e.g. `{"timeout": 25}`) instructing the Telegram server to hold the connection open for up to 25s if no updates exist.
- If the HTTP request client's socket timeout is equal to or less than the polling timeout (`requests.post(..., timeout=25)`), `requests` will throw `HTTPSConnectionPool: Read timed out` on every quiet poll interval, flooding `bot.log` with tens of thousands of false timeouts.
- **Rule**: Always enforce `request_timeout = max(request_timeout, poll_timeout + 15)` in the low-level API client for `getUpdates`.

## Single-menu UX & Zero-Slash-Command Architecture (Strict User Preference)

- **Strict Zero-Slash Rule**: Never force or prompt the user to use slash commands (`/start`, `/add_provider`, `/set_provider`). All navigation, configuration, and CRUD must happen through interactive inline glass buttons (`inline_keyboard`) and in-place edited messages.
- Almost every bot message EDITS the one living menu message (`menu_msg` table or `edit_message_text`), never spamming new messages. Delete user uploads or text prompts quietly.
- Natural Persian keyword triggers: accept plain natural words without slash (`پنل`, `منو`, `مدیر`, `تنظیمات`, `هوش مصنوعی`) in DM to summon the admin hub.
- Two-step text inputs via state tracking: when inputting credentials or new custom provider endpoints (`name*url*key*model`), edit the current menu message to show instructions + a `« بازگشت` cancel button, set `admin_states[user_id]`, capture the text, delete the secret user message silently, and re-render the parent menu in place.
- Colored "glass" inline buttons everywhere (PTB v22 `style=` kwarg: `primary`/`success`/`danger`); copy-buttons (`CopyTextButton`) for HEX codes, tokens, IDs. See `references/ptb-buttons-effects.md`.
- Slash-command-free: `set_my_commands([])` in `post_init`; all navigation via inline keyboards. Plain text is only honored when `user_data["awaiting"]` expects it.

## Telegram platform gotchas (Printify product-page lesson)

- `callback_data` is capped at 64 BYTES — a 24-char external ID inside a
  multi-segment callback (`pf:art:{shop}:{pid}:{upload_id}` = 65 bytes) is
  silently rejected and the menu never updates. Keep callbacks short: store
  the fetched object in a server-side cache (`PF_CACHE[(uid, shop, pid)]`)
  and put only a small index (`pf:art:{shop}:{pid}:{n}`) in the button.
  Smoke-test: byte-length of a real callback with production-length IDs must
  be ≤ 64.
- Button text is NOT HTML — never `html.escape()` it, or users see raw
  entities (`Men&#x27;s`). Escape only message text/captions parsed as HTML.
- Attach keyboards to the NEWEST message. If you `edit_message_text` an old
  menu and then `send_photo` a preview after it, the user only looks at the
  photo and never sees the buttons. Fix: pass `reply_markup=` on the
  `send_photo` itself (the photo carries the buttons); treat the edited menu
  as backup.
- A photo message can't be edited with `edit_message_text` (it owns a caption,
  not text) — when the keyboard lives ON the photo (previous bullet), every
  later edit of that message must fall back to
  `edit_message_caption(caption=..., parse_mode=..., reply_markup=...)`.
  Build the two-step fallback INTO `safe_edit_query` (try text → on
  "there is no text" class of BadRequest try caption → return bool) so no
  caller ever branches on message type. A missing caption fallback shows up
  later as dead buttons under the preview photo.
- Make edit helpers report failure: `safe_edit_query` returning `bool`
  (False on non-"not modified" BadRequest, logged) lets the caller fall back
  to `render_menu` (fresh message) so buttons are always visible somewhere.
  Swallowing the error silently produces "no buttons" bug reports.

## Deploy portability (local proxy vs server direct)

- The local dev shell may inject proxy env vars
  (`http_proxy=http://127.0.0.1:10808`, `all_proxy=socks5://...`) while deploy
  hosts (Pterodactyl panels, VPS) have direct net. NEVER hardcode a proxy URL
  in `bot.py` — one hardcoded proxy breaks every other environment with
  `ConnectError: All connection attempts failed` on startup.
- Pattern: `_detect_proxy()` reads
  `PROXY_URL/HTTPS_PROXY/HTTP_PROXY/https_proxy/http_proxy/ALL_PROXY/all_proxy`
  from ENV (plus a `DISABLE_PROXY=1` kill-switch); apply it to the PTB builder
  AND every `httpx.AsyncClient` helper (API calls, file downloads) — proxying
  only polling leaves the rest broken behind filters.
- `requirements.txt` must carry `python-telegram-bot[socks]` + `httpx-socks`,
  otherwise any socks5 proxy raises
  `RuntimeError: ... must be installed via pip install "python-telegram-bot[socks]"`.
- Ship a `requirements.txt` with every single-file bot deployed to a panel host
  (PTB, Pillow, httpx, requests, psutil).

## External API integrations (end-to-end or nothing)

- Never ship a token-storage dead end (the Printify lesson: saving the token
  with no usable flow reads as "broken"). Validate the token at entry
  (e.g. `GET /shops.json`), then wire the full loop: picker → paginated list →
  detail → act → upload-back. See `references/printify-integration.md`.

## Group Chat AI Assistant Architecture & Traps

- **The Third-Person Perspective Hallucination Trap**:
  - NEVER cram conversation history, replied context, and meta-instructions into a single `role: "user"` message as raw formatted strings (e.g., `[پیام قبلی خودت]: ...\n[پیام کاربر]: ...\nتو همان ربات هستی، پاسخ بده`).
  - Mechanism: The LLM reads the meta-prompts as user text describing a third-party scenario rather than an active dialogue. It loses first-person identity and speaks in the second/third person ("ربات می‌گوید...", "در پاسخ به کاربر باید گفت...") or writes advice about what someone should say.
  - Fix: Structure OpenAI-compatible chat messages with genuine roles:
    - Put the bot's own prior responses in `role: "assistant"`.
    - Put user prompts in `role: "user"`, identifying the speaker with either the `name` attribute or a clean prefix: `[<SenderName>]: <Text>`.
    - System prompt must explicitly enforce: "You are the assistant. Always speak directly in first-person ('من'). Never refer to yourself in the third person or narrate what the bot or user said."
- **The Intervening-User Multi-Addressee Trap (Group Dialogue Pollution)**:
  - Symptom: User A chats with the bot in a group. An intervening third party (User B) posts a message. User A asks the next question. The bot replies addressing BOTH User A and User B ("Salam Armin... Reza in response to your question...").
  - Root Cause: Naively looping over the raw group `chat_history` (e.g. `for h in hist_list: msg_turns.append({"role": "user", "content": h})`) injects User B's unrelated message as an active `role: "user"` turn in the prompt! The LLM sees multiple pending user questions in the dialogue and dutifully responds to all authors.
  - Fix:
    1. Conversational turns (`msg_turns`) MUST strictly isolate the dialogue between the **current user (`sender_name`) and the bot** (or the specific message replied to). Unrelated third-party group chatter must NEVER enter `messages` as `role: "user"`.
    2. Other group chatter only belongs in the system prompt under `[پیام‌های پس‌زمینه گروه (صرفاً برای اطلاع از جو گروه، مخاطب این پیام‌ها نیستی)]`.
    3. The system prompt must enforce single-addressee exclusivity:
       `🎯 مخاطب مستقیم و انحصاری تو: طرف صحبت تو در این نوبت فقط و فقط «[Sender]» است. تحت هیچ شرایطی به افراد دیگر گروه پاسخ نده، نام آن‌ها را نیاور، و تمام پاسخ منحصراً خطاب به «[Sender]» باشد.`
- **Web Search Grounding vs RLHF Safety Refusals ("I don't have access to live markets")**:
  - Symptom: Bot has web search enabled, but when asked real-time market queries like "قیمت طلا الان چنده؟", the model refuses with boilerplate: "من هوش مصنوعی هستم و به اینترنت یا قیمت لحظه‌ای بازار دسترسی ندارم".
  - Root Causes (Trio):
    1. **Query pollution**: Prepending the sender's name (`"Armin: قیمت طلا الان چنده؟"`) causes search engines to search for the user's name instead of the topic, returning empty/irrelevant results. Query must be stripped of author prefixes, punctuation, and conversational filler words before sending to the search engine.
    2. **Monkey-patch overrides**: A secondary/fallback search function later in the file (e.g. `WebSearcher.search = staticmethod(_web_search_final)`) quietly replacing the search engine with an ungrounded API (e.g. DuckDuckGo Instant Answer API which returns empty results for 99% of Persian market queries). Always verify `inspect.getsource(WebSearcher.search)` to ensure late monkey-patches don't revert the engine.
    3. **Missing grounding mandate**: Modern LLMs (Gemini, Llama) are heavily RLHF-tuned to decline live market questions. If `search_context` is injected without an imperative grounding prompt, the model defaults to its safety refusal. Fix: Always append an explicit directive:
       `تو به اطلاعات زنده و نتایج وب بالا دسترسی کامل داری. حتماً بر اساس همین نتایج پاسخ کاربر را بده و نرخ/قیمت/اطلاعات را بگو. هرگز نگو 'من دسترسی به اینترنت یا نرخ لحظه‌ای ندارم'.`
    4. **Dependency-free pure regex parser**: Do not depend on `from bs4 import BeautifulSoup` inside runtime scrapers on panel hosts where external libraries might be missing or fail imports; use pure regex `re.findall(r'<li class="b_algo"[^>]*>(.*?)</li>', ...)` with `<h2>\s*<a[^>]*>(.*?)</a>` and `<div class="b_caption"[^>]*>\s*<p[^>]*>(.*?)</p>` to guarantee zero-dependency execution.
- **The "Hanging on `...`" Trap (Silent Failure in Streaming Generators)**:
  - When a bot sends an initial placeholder message (`...` or `🧠 در حال تفکر... ✍️`) before starting a streaming generator in a background thread:
  - Any unhandled exception inside the generator (`NameError`, suspended API keys, quota exhaustion, network drops) silently aborts the generator iteration.
  - The thread dies before reaching the final `edit_message_text` call, leaving the message permanently stuck on `...`.
  - Fix: Always enclose generator consumption inside `try...except Exception as err:`, log the full traceback, set `full_text = f"⚠️ خطا در پردازش: {err}"`, and ensure `edit_message_text(chat_id, p_msg_id, final_clean_text)` is executed unconditionally.
- **Never Preemptively Hijack or Override User-Selected Providers**:
  - Always honor the user's configured `active_provider` from settings/DB. Do not add static overrides (e.g. `if provider == "google": provider = "openrouter"`) based on API key prefix heuristics or assumptions (e.g. assuming `AQ.` is suspended or invalid — service accounts and Google Cloud tokens often use non-standard prefixes).
  - If fallback is needed, attempt the user-selected provider first at runtime, and only cascade across providers upon actual fatal HTTP/API errors.
- **OpenRouter & OpenAI-Compatible 400 Bad Request Traps**:
  - **Double-Prefix Model IDs**: Passing slugs like `openrouter/free` or `openrouter/<model>` directly to `https://openrouter.ai/api/v1/chat/completions` triggers `400 Bad Request: Invalid model`. Normalize model IDs: strip redundant `openrouter/` prefixes and map aliases like `free` or `auto` to verified canonical slugs (e.g. `meta-llama/llama-3.3-70b-instruct:free`).
  - **Empty Turn Content**: OpenRouter and OpenAI APIs reject any message item where `content` is an empty string `""` or whitespace with `400 Bad Request: 'content' is required`. Always strip and prune blank turns before building payload `messages`.
  - **Dynamic Base URLs for OpenAI Proxies/Gateways**: Never hardcode `https://api.openai.com/v1/chat/completions`. When supporting OpenAI-compatible proxies (Devora, LiteLLM, Ollama), check and apply `config.get("openai_base_url")` (e.g. `https://api.devora.my.id/v1`) and construct `f"{base_url.rstrip('/')}/chat/completions"`.
- **Personality & Super-Prompt Design for Group Assistants**:
  - When tasked with creating a strong ideological/character persona (e.g. Right-wing, Classical Liberal, Republican Party / GOP advocate):
    - Articulate core principles: individual freedom, private property, rule of law, free-market capitalism, limited government, deregulation, meritocracy, and grounded economic critique of socialism, welfare bureaucracy, and wokeism.
    - Combine intellectual confidence with sharp, witty, rational argumentation (wit & sarcasm without vulgarity).
    - Enforce first-person perspective (`من` / `دیدگاه من`) and eliminate boilerplate robotic openings ("من به عنوان هوش مصنوعی...", "سلام دوست عزیز").
    - Enforce proportional brevity: 1-2 punchy sentences for simple prompts to prevent token burning, reserving long analytical essays only for deep topics or code.
- **Prompt Bleed & Character Caricaturing (The "Don't Preach" Lesson)**:
  - When giving a bot an ideological or philosophical persona (e.g., right-wing, free-market, classical liberal, republican), NEVER state raw negative imperatives like "attack socialism, despise bureaucracy, skip greetings".
  - Mechanism: LLMs suffer from prompt bleed and take meta-instructions literally, quoting prompt fragments to users ("بدون سلام و احوال‌پرسی ملال‌آور، بگو از کدام رانت یا ایده سوسیالیستی کلافه‌ای؟") and caricaturing greetings into political speeches.
  - Fix:
    - Frame the worldview as implicit reasoning rather than an explicit sermon ("عمل‌گرا، حامی آزادی فردی و شایسته‌سالاری؛ اما سیاست‌زده نیستی و در چت‌های عادی لفاظی‌های سنگین سیاسی نمی‌کنی").
    - Explicitly forbid repeating prompt instructions: "هرگز جملاتی مانند 'بدون مقدمه‌چینی'، 'طبق قوانین من' یا توضیحات درباره ساختار پرامپت را در خروجی نیاور".
    - When user greets, greet back warmly and naturally; never launch into unprompted political rhetoric.
    - Sanitize user names directly from raw updates; never affix arbitrary suffixes or declensions (e.g. turning `آرمین` into `آرمینای عزیز`).
- **Custom OpenAI-Compatible Providers & Startup Defaulting**:
  - Store personal/custom providers in an additive SQLite table (`custom_ai_providers`: `name`, `base_url`, `api_key`, `model`, `enabled`).
  - Route non-built-in provider names to standard OpenAI-compatible streaming (`f"{base_url.rstrip('/')}/chat/completions"` with bearer auth).
  - When the user requires a guaranteed reboot default (e.g., "always start on Google"), unconditionally execute `UPDATE global_settings SET active_provider = 'google' WHERE id = 1` inside the bot's `__init__`, preventing residual manual test configurations from sticking across host reboots.
- **Replied-Message Text Slicing Null Pointer**:
  - In Telegram/Bale updates, `reply_to_message.text` is `None` when a user replies to media (photo, voice, sticker, file without caption).
  - Calling `reply_text[:100]` throws `TypeError: 'NoneType' object is not subscriptable` and silently kills the background AI worker, leaving users hanging. Always sanitize with `(reply_text or '')[:100]`.
- **Web Search Engine Fragility**:
  - Simple DuckDuckGo HTML scraping (`html.duckduckgo.com`) often returns HTTP 202 anti-bot challenges when called from hosting provider datacenters.
  - Use a tiered search approach:
    1. **Primary**: Bing Search parsed with `BeautifulSoup` targeting `li.b_algo h2` and `p`.
    2. **Secondary Fallback**: DuckDuckGo with browser-matching headers.
    3. **Tertiary Fallback**: Wikipedia API (`fa.wikipedia.org/w/api.php?action=query&list=search&srsearch=...`) for factual entities and bios.
  - Auto-detect temporal/factual intent (`امروز`, `الان`, `قیمت`, `اخبار`, `کیست`, `چیست`, `نرخ`) rather than forcing users to manually prefix messages with "سرچ".

## Support files

- `references/printify-integration.md` — Printify token→shop→product→image→recolor→upload-back flow.
- `references/hf-rmbg-free.md` — free bg-removal via HF RMBG-1.4 Router (chain order, status handling, Gradio dead end).
- `references/cut-refinement.md` — `_refine_cut()` white-halo removal (decontaminate + erode + soft edge) for every cut before recoloring.
- `references/ai-key-rotation.md` — tiered cooldown recipe + stuck-key fix.
- `references/retry-queue.md` — failure cards + backoff queue + loops.
- `references/sqlite-migration.md` — additive migration pattern.
- `references/g4f-fallback.md` — no-auth provider discovery.
- `references/ops-loops.md` — digest/heartbeat/watchdog/backup/cleanup.
- `references/ptb-buttons-effects.md` — PTB v22 colored buttons, copy buttons,
  message effects, premium tg-emoji IDs, async error handler, single-menu UX,
  force-join gate.
- `references/disposable-email-providers.md` — Catchmail vs Mail.tm endpoints,
  bare-list-vs-Hydra parsing, password-policy 422s.
