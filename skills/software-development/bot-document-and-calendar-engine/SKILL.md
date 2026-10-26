---
name: bot-document-and-calendar-engine
description: "Use for bot files and Tehran time grounding."
version: 1.0.0
---

# Bot Document Generation & Grounding Engine

Lessons, architectural patterns, and debugging recipes for implementing zero-leak document generation (PDF, Word, Code) and accurate calendar grounding in conversational bots.

## 1. The Bidi Paragraph Line-Wrapping Inversion Trap in PDF Generation
- **Symptom**: Generated Persian PDFs have sentences rendered in reverse order (the last sentence of a paragraph appears on the first line at the top, and the introductory sentence appears at the bottom).
- **Mechanism**: Applying `bidi.algorithm.get_display(arabic_reshaper.reshape(paragraph_text))` to an entire multi-line paragraph converts the whole paragraph into a single visually-reversed string. When ReportLab's layout engine splits that long string into lines based on column width, it takes chunks from the beginning of the visual string — which are actually the end of the logical paragraph!
- **Fix (Pre-Wrapping at Word Boundaries)**:
  1. Pre-wrap the logical Persian text into lines using font metrics: measure candidate lines with `pdfmetrics.stringWidth(test_line, font_name, font_size) <= printable_width_pt`.
  2. Reshape and apply Bidi **line by line** individually: `get_display(arabic_reshaper.reshape(single_line))`.
  3. Join the reshaped lines with `<br/>` and pass into ReportLab `Paragraph`. This preserves 100% correct top-to-bottom reading order.

## 2. DOCX Text Run RTL Run Properties
- In `python-docx`, setting `<w:bidi w:val="1"/>` on paragraph properties (`pPr`) is insufficient for mixed Persian/Latin text, parentheses, and numbers.
- Every text run (`r = p.add_run(...)`) MUST have `<w:rtl w:val="1"/>`, `<w:cs/>`, and complex script fonts (`<w:rFonts w:ascii="Ray" w:hAnsi="Ray" w:cs="Ray"/>`) added to `rPr`, otherwise parentheses, punctuation, and English terms flip to the beginning of the line.

## 3. Python f-String Escaping Crash with JSON Action Tags
- When embedding JSON structures like `[FILE:{"filename":"..."}]` inside system prompts generated via Python f-strings (`f"""..."""`), literal braces MUST be doubled (`{{...}}`).
- Unescaped single braces trigger fatal `ValueError: Invalid format specifier` at runtime, causing background tasks to fail silently and freeze the bot on typing placeholders (`...`). Using block format `[FILE:name.ext]...[/FILE]` eliminates JSON escaping pitfalls entirely.

## 4. LLM Max Token Truncation & Fault-Tolerant File Extraction
- LLMs writing long documents frequently hit token budgets and truncate before closing tags (`[/FILE]` or `}]`).
- The extraction regex must be resilient to unclosed blocks: extract `filename`, `title`, and unclosed `content` up to EOF, strip raw blocks from the chat bubble, and auto-enforce the requested extension (`.pdf` or `.docx`) based on the user's prompt keywords (e.g. "برام پی دی اف کن") even if the LLM hallucinated `.md` or `.txt`.

## 5. PostScript / `%PDF-1.4` Raw Bytecode Hallucination
- When asked to "make a PDF", LLMs often hallucinate raw PDF bytecode (`%PDF-1.4 1 0 obj ... << /Length ... >> stream BT ... Tj`).
- System prompts must explicitly state: "برای PDF به هیچ عنوان کدهای باینری مانند %PDF- ننویس؛ فقط متن تمیز با تیترهای # درج کن؛ ربات خودکار آن را به فایل تبدیل می‌کند".
- Include a runtime safety catcher: if `%PDF-` appears in response text, parse strings inside `(...) Tj`, assemble a clean markdown document, and compile it into a real PDF automatically.

## 6. Brevity Decoupling & Conversational Balance
- Decouple chat brevity from document richness: an aggressive meta-rule like "Answer in 1-2 lines only" causes the LLM to write telegraphic, grammatically broken, and incomplete content inside generated files (`content`).
- Chat message should be 1 short line without greeting ("فایل درخواستی شما آماده شد:"), while document content must be comprehensive, fluent, rich, and well-structured.
- Avoid extreme truncation for explanations and concepts: provide informative, complete answers without conversational filler.

## 7. Mandatory Jalali (Shamsi) Date, Weekday, and Tehran Time Grounding
- Without explicit calendar injection, LLMs cannot answer "امروز چندمه؟" یا "ساعت چنده؟" and hallucinate dates or report confusion.
- In every turn, compute and inject the exact Persian calendar specifications into the system prompt:
  - Shamsi date (e.g. `شنبه، ۲ آبان ۱۴۰۵`)
  - Weekday name in Persian (`شنبه`)
  - Official Iran time (`به وقت تهران UTC+3:30`)
  - Gregorian date for reference (`24 October 2026`)
- Ground with: "تو دقیقاً می‌دانی امروز چه روزی و چه ساعتی است. به سوالات تقویمی و زمانی فوراً و با اطمینان بر اساس این مشخصات پاسخ بده."

## 8. Markdown Bold (`**`) & Bullet Glyph Traps in Bidi Documents
- **The Literal Asterisk Bug**: LLMs format list items and titles with `**bold**`. Printing text without parsing markdown causes literal `**` to appear in output PDFs and DOCX files.
- **The Bidi Tag Reversal Trap**: Inserting `<b>...</b>` directly into text *before* passing it to `bidi.algorithm.get_display` causes Bidi to reverse punctuation `<` and `>`, turning `<b>` into `<b/>...<b>`. ReportLab's XML parser then crashes with `Parse error: saw </para> instead of expected </b>`.
- **The Solution for PDF**:
  1. Measure candidate line widths with `pdfmetrics.stringWidth` after stripping `**` so line wrap calculations match the true visible length.
  2. Maintain bold open/close state across line wraps so multi-line bold text stays balanced on each wrapped segment.
  3. Replace `**` with neutral ASCII tokens (`XSTART...XEND`) before reshaping.
  4. Run `bidi.algorithm.get_display(arabic_reshaper.reshape(tokenized_line))`.
  5. Replace `XSTART` with `<b>` and `XEND` with `</b>` *after* Bidi.
  6. Register the font family in ReportLab: `pdfmetrics.registerFontFamily("Ray", normal="Ray", bold="Ray-Bold")` with both regular and bold TTF paths so `<b>` switches to the real bold glyphs.
- **The Solution for Word (DOCX)**:
  - Parse lines with `re.split(r'(\*\*.*?\*\*)', text)`. For matched bold tokens, create runs with `r.bold = True` and text stripped of `**`. Apply `<w:rtl/>` and complex script font attributes to every run.
- **Font Glyph Support (Missing Box `\x00\x00` Trap)**:
  - Common decorative bullet characters like `▪️` (U+25AA) are missing from standard Persian font cmaps (such as Vazirmatn) and render as blank boxes (`\x00\x00`) or question marks.
  - Always normalize bullet characters in input text to standard `•` (U+2022) or `-`, which are universally present across Persian fonts.

## 9. Scoped Import / `UnboundLocalError` in Async Background Handlers
- **Trap**: Conditional or deferred imports (e.g. `import re` inside a specialized `if "%PDF-" in text:` block) make the symbol local to the entire function scope. If that branch does not execute, any subsequent call to `re.search()` outside the branch fails with `UnboundLocalError: cannot access local variable 're' where it is not associated with a value`.
- **Impact**: In background tasks, unhandled exceptions kill the worker mid-stream, leaving the user's chat message permanently frozen on typing placeholders (`... ✍️`).
- **Rule**: Import all parser utilities (`re`, `json`, `os`) at the top of the module or helper class, and wrap document creation and dispatch in a guarded `try...except` block so that a document rendering error logs cleanly and updates the chat message with an error report instead of dropping the task.
