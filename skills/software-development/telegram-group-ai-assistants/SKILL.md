---
name: telegram-group-ai-assistants
description: "Use for conversational AI assistants in Telegram and Bale."
version: 1.4.0
author: Armin & Hermes
license: MIT
metadata:
  hermes:
    tags: [telegram, bale, group-bots, ai-assistant, reply-chain, tgju, zero-slash, custom-providers, 9router, file-generator, docx-pdf, sqlite-salvage, tehran-time]
---

# Telegram & Bale AI Assistants

Architecture, state machines, and operational patterns for LLM-powered assistant bots in Telegram and Bale groups and private chats. Covers conversational context isolation, multi-layer reply-chain thread tracking, real-time market data grounding, zero-slash glass-button UX, prompt anti-caricaturing, universal file generation, database recovery, and solar Hijri / Tehran calendar grounding.

## Core Architectural Pillars

### 1. Full Reply-Chain Thread Traversal (رشته پیام‌های ریپلای‌شده)
- **Problem**: When users engage in a multi-turn group debate (User A asks -> Bot answers -> User B disputes -> User A counters with a bot mention/reply), checking only the immediate `reply_to_message` loses the entire antecedent dialogue, making the bot reply out of context.
- **Solution**:
  - Maintain a bounded in-memory message cache (`self.recent_msg_map: OrderedDict[str, dict]` storing `msg_id`, `sender_name`, `is_bot`, `text`, `reply_to_id`, capped at ~2000 items).
  - Cache every incoming group message AND every bot-generated response with its target `reply_to_id`.
  - When an incoming message has a `reply_to_message`, recursively traverse backwards: check the nested `reply_to_message` object or look up parent IDs in `recent_msg_map` up to 8 levels deep.
  - Reverse the collected chain to chronological order (`chain.reverse()`) and inject into `messages`:
    - Bot turns: `{"role": "assistant", "content": item["text"]}`
    - User turns: `{"role": "user", "content": f"{item['sender_name']}: {item['text']}"}`
    - Target prompt: `{"role": "user", "content": f"{sender_name}: {clean_text}"}`.
  - Ground in System Prompt:
    `🧵 رشته گفتگو و زنجیره ریپلای‌ها: پیام‌های بالا یک زنجیره مرتبط هستند. مخاطب نهایی و مستقیم پاسخ تو فقط و فقط «{sender_name}» است که پیام آخر را فرستاده است. سیر مکالمه را بفهم و به پیام آخر پاسخ بده.`

### 2. The Intervening-User Multi-Addressee Trap (Group Dialogue Pollution)
- **Symptom**: User A chats with the bot in a group. An intervening third party (User B) posts an unrelated message. User A asks the next question. The bot replies addressing BOTH User A and User B ("Salam Armin... Reza in response to your question...").
- **Root Cause**: Naively passing raw group chat history into `messages` as `role: "user"` turns gives the LLM multiple pending user prompts from different authors in a single turn.
- **Fix**:
  1. Conversational turns (`messages`) MUST strictly isolate the dialogue between the **current user (`sender_name`) and the bot** (or the specific reply chain). Unrelated bystander chatter must NEVER enter `messages` as `role: "user"`.
  2. Bystander chatter belongs exclusively in the system prompt under `[پیام‌های پس‌زمینه اخیر گروه (صرفاً برای اطلاع از جو گروه، مخاطب این پیام‌ها نیستی)]`.
  3. Enforce single-addressee exclusivity in the system prompt:
     `🎯 مخاطب مستقیم و انحصاری تو: طرف صحبت تو در این نوبت فقط و فقط «{sender_name}» است. تحت هیچ شرایطی به افراد دیگر گروه پاسخ نده، نام آن‌ها را نیاور، و تمام پاسخ منحصراً خطاب به «{sender_name}» باشد.`

### 3. Real-Time Market Data Grounding (TGJU vs Search Snippets)
- **Symptom**: Bot has web search enabled, but when asked real-time market queries like "قیمت طلا الان چنده؟", the model refuses with boilerplate: "من هوش مصنوعی هستم و به اینترنت یا قیمت لحظه‌ای بازار دسترسی ندارم".
- **Root Causes**:
  - Search engine snippets (Bing/Google) for gold/currency in Iran return macroeconomic analysis ("فشردگی قیمت زیر میانگین متحرک...") rather than exact numeric spot rates.
  - Seeing no numbers, LLMs default to safety refusal boilerplate.
  - Prepending author names (`"Armin: قیمت طلا الان چنده؟"`) causes search engines to search for the author's name, returning zero/irrelevant market results.
- **Fix**:
  1. Wire a direct spot-rates API (`https://call.tgju.org/ajax.json`) alongside web search.
  2. When market triggers (`طلا`, `سکه`, `دلار`, `ارز`, `بیت کوین`, `قیمت`, `نرخ`) fire, fetch the structured JSON containing `geram18`, `sekeb`, `nim`, `rob`, `ons`, `price_dollar_rl`, calculate exact Toman rates, and format into a structured table.
  3. Append an imperative anti-refusal grounding directive:
     `تو به ارقام دقیق و لحظه‌ای بالا دسترسی کامل داری. حتماً بر اساس همین نتایج پاسخ کاربر را بده و نرخ/قیمت را اعلام کن. هرگز نگو 'من دسترسی به اینترنت یا نرخ لحظه‌ای ندارم'.`

### 4. Zero-Slash-Command & Glass-Button UI (Strict Standing Rule)
- **Zero Slash Commands**: NEVER force, suggest, or require users or admins to type slash commands (`/start`, `/add_provider`, `/set_provider`, `/test_provider`, `/providers`). Every single administrative action, navigation, CRUD operation, key management task, and engine toggle MUST be accessible through the primary inline glass keyboard (`پنل شیشه‌ای اول`) and in-place edited messages (`edit_message_text`).
- Accept natural Persian keyword triggers in DM (`پنل`, `منو`, `مدیر`, `تنظیمات`, `هوش مصنوعی`) to summon the admin hub without slashes.
- **Step-by-Step Wizards (مرحله‌به‌مرحله) Over Brittle Multi-Field Strings**:
  - When capturing multi-field configurations (such as adding custom AI providers, endpoints, or keys), NEVER ask the user to type a complex single-line string with separators (`name*url*key*model`). Separator syntax is brittle, unnatural on mobile, and prone to whitespace, character-escaping, and delimiter errors.
  - Always implement a step-by-step interactive wizard that prompts for one attribute per step:
    - Step 1: Provider Name (e.g. `xkiro` or `deepseek`)
    - Step 2: Base URL (e.g. `https://api.xkiro.com/v1`) — auto-strip trailing slashes, spaces, and `/chat/completions` suffix.
    - Step 3: API Key(s) — accept single or multiple keys (comma/line-separated) to populate the key pool.
    - Step 4: Model Name (e.g. `qwen/qwen3.8-max:free`)
  - **The `target_msg_id` State-Carry Rule (Avoiding `NameError` / `MES-...` Crashes)**:
    - In multi-step wizards, always extract `target_msg_id = u_state.get("msg_id")` at the top of the state router. If undefined in a step handler, Python throws fatal `NameError: name 'target_msg_id' is not defined` (surfaced as error code `MES-...`).
    - Attempt `self.api.edit_message_text(sender_id, target_msg_id, ...)` to smoothly mutate the panel card in place. If editing fails or `target_msg_id` is missing, send a new message and save its `message_id` into `u_state["msg_id"]` for subsequent steps.
    - Delete the user's secret/input message (`self.api.delete_message(chat_id, msg.get("message_id"))`) after each step to keep the private chat clean.

### 5. Custom 9Router-Style AI Providers & Multi-Key Pool Architecture
- **Dedicated Glass Management Cards**:
  - In the main AI panel, clicking any custom provider must open a dedicated glass card showing its Base URL, Model, active status, and key pool breakdown.
  - Provide direct inline buttons on the card: `[🟢 فعال‌سازی]`, `[🧪 تست اتصال و پینگ]`, `[➕ افزودن کلید به استخر]`, `[🧠 تغییر مدل]`, `[🗑 حذف کلید]`, `[🗑 حذف پرووایدر]`, `[« بازگشت]`.
- **Multi-Key Pool & Round-Robin Load Balancing**:
  - Store keys in a dedicated table (`custom_ai_keys(provider_name, api_key, enabled, cooldown_until, usage_count, last_error)`).
  - Implement round-robin key rotation across active keys.
  - **Automatic Failover on 429/401**: When a key hits `429` (Rate Limit) or quota exhaustion, set a temporary cooldown (60s) and immediately fail over to the next key in the pool without dropping or failing the user's message.
  - Automatically fall back to non-streaming (`stream: False`) if SSE streaming fails or is buffered by upstream gateways.
- **Premature Variable Scope in Streaming Generators (`active_messages`)**:
  - In streaming generators (e.g. `_ask_ai_stream_multi_key`), placing custom provider handlers at the top of the function before `active_messages` is constructed raises fatal `UnboundLocalError`.
  - Always place the custom provider runner after system prompt injection, message sanitization, and web search enrichment so the payload is fully assembled.
- **Reboot Persistence**:
  - Never execute unconditional `UPDATE global_settings SET active_provider = 'google'` in `__init__`, as it wipes the user's selected custom provider on every container restart. Only set default to Google if `active_provider` is unset or empty.

### 6. Prompt Bleed & Character Caricaturing (The "Don't Preach" Rule)
- When giving a bot an ideological or philosophical persona (e.g. classical liberal, free-market, republican), never write raw negative meta-imperatives like "attack socialism, despise bureaucracy, skip greetings".
- Mechanism: LLMs suffer from prompt bleed and take meta-instructions literally, quoting prompt fragments to users ("بدون سلام و احوال‌پرسی ملال‌آور، بگو از کدام رانت یا ایده سوسیالیستی کلافه‌ای؟") and caricaturing greetings into political speeches.
- Fix:
  - Frame the worldview as implicit reasoning rather than an explicit sermon ("عمل‌گرا، حامی آزادی فردی و شایسته‌سالاری؛ اما سیاست‌زده نیستی و در چت‌های عادی لفاظی‌های سنگین سیاسی نمی‌کنی").
  - Explicitly forbid repeating prompt instructions: "هرگز جملاتی مانند 'بدون مقدمه‌چینی'، 'طبق قوانین من' یا توضیحات درباره ساختار پرامپت را در خروجی نیاور".
  - When user greets, greet back warmly and naturally; never launch into unprompted political rhetoric.
  - Sanitize user names directly from raw updates; never affix arbitrary suffixes or declensions (e.g. turning `آرمین` into `آرمینای عزیز`).

### 7. Universal File & Document Generation (Word, PDF, Code, Any Extension)
- **Natural AI Tag Protocol & Format Enforcement**:
  - Prefer the plain block format `[FILE:filename.ext]...[/FILE]` over JSON tags. If using JSON action tags like `[FILE:{{"filename":"..."}}]` inside Python f-strings (`f"""..."""`), literal braces MUST be doubled (`{{...}}`) — unescaped single braces cause fatal `ValueError: Invalid format specifier` at runtime, freezing the bot on typing placeholders (`...`).
  - Instruct the model to place the tag at the end of its response after a single-line chat confirmation.
  - **Auto-Enforce Extension by User Intent**: When users say "برام پی دی اف کن" or "فایل ورد بساز", the extraction logic must parse user prompt keywords and enforce the requested extension (`.pdf` or `.docx`), even if the model hallucinates `.md` or `.txt`.
- **Fault-Tolerant Truncated Stream Extraction**:
  - Long documents frequently hit the model's `max_tokens` budget, truncating the stream before closing tags (`[/FILE]` or `}]`).
  - The extractor regex must be resilient to unclosed blocks: extract `filename`, `title`, and unclosed content up to EOF, strip the raw block from the chat message, and compile the partial document rather than dumping raw tag syntax into the chat.
- **The Bidi Paragraph Line-Wrapping Inversion Trap in ReportLab PDF**:
  - **Symptom**: Generated Persian PDFs have sentences rendered in reverse order (the last sentence of a paragraph appears on line 1 at the top of the page, and the introductory sentence appears at the bottom).
  - **Mechanism**: Applying `bidi.algorithm.get_display(arabic_reshaper.reshape(paragraph_text))` to an entire multi-line paragraph converts the whole paragraph into a single visually-reversed string. ReportLab's layout engine splits that long string into lines based on column width, taking chunks from the start of the visual string — which are actually the end of the logical paragraph!
  - **Fix (Pre-Wrapping at Word Boundaries)**:
    1. Pre-wrap the logical Persian text into lines using font metrics: test candidate words with `pdfmetrics.stringWidth(test_line, font_name, font_size) <= printable_width_pt`.
    2. Reshape and apply Bidi **line by line** individually: `get_display(arabic_reshaper.reshape(single_line))`.
    3. Join the reshaped lines with `<br/>` and pass into ReportLab `Paragraph`. This preserves 100% correct top-to-bottom reading order.
- **DOCX Run-Level RTL Properties**:
  - Setting `<w:bidi w:val="1"/>` on paragraph properties (`pPr`) is insufficient for mixed Persian/Latin text, parentheses, and numbers.
  - Every text run (`r = p.add_run(...)`) MUST have `<w:rtl w:val="1"/>`, `<w:cs/>`, and complex script fonts (`<w:rFonts w:ascii="Ray" w:hAnsi="Ray" w:cs="Ray"/>`) added to `rPr`, otherwise punctuation and Latin terms flip to the line start.
- **PostScript / `%PDF-1.4` Raw Bytecode Hallucination**:
  - LLMs asked to "make a PDF" often hallucinate raw PDF bytecode (`%PDF-1.4 1 0 obj ... << /Length ... >> stream BT ... Tj`).
  - System prompt must explicitly state: "برای PDF به هیچ عنوان کدهای باینری مانند %PDF- ننویس؛ فقط متن تمیز با تیترهای # درج کن؛ ربات خودکار آن را به فایل تبدیل می‌کند".
  - Include a runtime safety catcher: if `%PDF-` appears in response text, parse strings inside `(...) Tj`, assemble a clean markdown document, and compile it into a real PDF automatically.
- **Streaming Guard (`_strip_ai_thinking`)**:
  While streaming live response tokens to the Telegram/Bale chat bubble, strip any trailing or incomplete `[FILE:.*$` and `%PDF-.*$` from the display text so raw syntax never flickers on the user's screen.
- **Zero Memory & Zero Disk Leaks**:
  - Import heavy formatting libraries (`docx`, `reportlab`, `arabic_reshaper`, `python-bidi`) lazily inside generation routines; never load them into persistent global memory on startup.
  - Write files to `/tmp/ai_generated_files/` and immediately call `os.remove(built_path)` after `send_document()` finishes to prevent disk space exhaustion on low-storage containers.
- **Raw Code/Data Files**: Strip any accidental Markdown code-block wrappers (````python ... ````) before saving to disk to ensure immediate executable validity.
- **Platform-Specific `send_document` Field Names**:
  - **Telegram Bot API (`/sendDocument`)**: The multipart file field MUST be named `'document'` (`files={'document': (filename, f)}`). Sending `'file'` causes Telegram to reject the payload with `Bad Request: document empty`.
  - **Bale Bot API (`/sendDocument`)**: Expects the multipart key `'file'` (`files={'file': (filename, f)}`).

### 8. Dynamic Volume Matching, Brevity Decoupling & Greeting Suppression (ایجاز و تعادل)
- **Decouple Chat Brevity from Document Richness**:
  An aggressive meta-rule like "Answer in 1-2 lines only" causes the LLM to write telegraphic, grammatically broken, and incomplete content inside generated files (`content`). Explicitly separate the two scopes: the chat message is 1 short line without greeting ("فایل درخواستی شما آماده شد:"), while the file content must be comprehensive, fluent, rich, and well-structured.
- **Avoid Extreme Truncation in Explanations**:
  For conceptual, historical, scientific, or tutorial questions, provide an informative, well-rounded, and engaging answer. Strip conversational filler and throat-clearing, but never truncate explanations so severely that they become telegraphic or incomplete.
- **Strict Ban on Salutations/Greetings**:
  Eliminate boilerplate greetings ("سلام", "درود", "وقت‌بخیر", "ارادت") from the start of assistant turns. The model must immediately address the subject matter without conversational throat-clearing.

### 9. SQLite Database Malformation Salvage Protocol (`database disk image is malformed`)
- **Root Cause**: Hard container kills, power interruptions, or rapid concurrent writes with out-of-sync WAL files (`.db-wal`) corrupt SQLite page headers, causing fatal `sqlite3.DatabaseError: database disk image is malformed` on specific table queries (surfaced as `MES-...` error codes). Standard `SELECT *` or `.dump` commands abort on the first bad page.
- **Recovery Procedure**:
  1. Extract the full DDL table schema from `sqlite_master`.
  2. Create a clean replacement database file and execute all DDL statements (including creating indexes and modern migration columns like `key_index`).
  3. Attempt table-by-table bulk copy for healthy tables.
  4. For corrupted tables, fall back to row-by-row scanning using `WHERE rowid = ?` in a loop from 1 to the max row ID, wrapping individual row fetches in `try ... except`. This salvages 100% of the uncorrupted rows instead of abandoning the entire table.
  5. Checkpoint the clean database (`PRAGMA wal_checkpoint(TRUNCATE);`) and verify `PRAGMA integrity_check;` returns `[('ok',)]`.
  6. Rename corrupt files (`.db`, `.db-wal`, `.db-shm`) to `.corrupt_bak`, move the clean database into place, and trigger a host process restart to release stale file locks held by the previous process.

### 10. Accurate Solar Hijri (Shamsi) Calendar & Tehran Time Grounding
- **Problem**: When users ask "امروز چندمه؟", "چه روزیه؟", or "ساعت چنده؟", LLMs hallucinate dates or report confusion if only given raw UTC server time or Gregorian dates.
- **Solution**:
  - Implement a zero-dependency Gregorian-to-Jalali conversion function and calculate official Iran time (`UTC+3:30`).
  - In every prompt build, inject the exact specifications:
    - Shamsi date (e.g. `شنبه، ۲ آبان ۱۴۰۵`)
    - Weekday name in Persian (`شنبه`)
    - Official Tehran time (`۱۹:۴۸`)
    - Gregorian date for cross-reference (`2026/10/24`)
  - Ground with: `تو دقیقاً می‌دانی امروز چه روزی، چه تاریخی و چه ساعتی است. به سوالات زمانی و تقویمی سریع و با اطمینان پاسخ بده.`
