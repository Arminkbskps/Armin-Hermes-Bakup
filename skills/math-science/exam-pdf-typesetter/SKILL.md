---
name: exam-pdf-typesetter
description: "Use when typesetting Persian STEM exams and test booklets."
version: 1.2.0
author: Armin & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [exam, test, pdf, typst, persian, latex, weasyprint]
---

# Exam PDF Typesetter

Typeset publication-quality Persian multiple-choice and descriptive STEM exams (A4 multi-column, standard exam headers, question numbers, four choices, and embedded geometric figures).

## Layout & Strict Anonymity Standards
- **Header**: Standard Iranian educational header (Ministry of Education / Sampad / School Name, Subject, Grade, Date, Time, Teacher/Author, Total Score).
- **Strict Anonymity Rule**: NEVER put student or user name anywhere on the document (header, footer, meta, or body) unless explicitly asked. Run `grep -i '<name>'` on HTML/PDF text to verify 0 occurrences.
- **Two-Column Grid**: 2 balanced columns with vertical divider line.
- **Question Format**: Bold Persian question number, clear stem, aligned four choices (۱) (۲) (۳) (۴).
- **Math & Formulas**: Typst math mode ($...$) or clean rendered HTML/CSS fractions (see `references/html_math_css_template.md`).
- **Unicode Superscripts Over HTML `<sup>`**: In flexbox math containers (`display: inline-flex`), Chromium's PDF renderer flattens `<sup>` tags to the baseline, rendering expressions like `(3 tan α + 2)²` as `(3 tan α + 2)2=`. Always use true Unicode superscript glyphs (`²`, `³`, `⁴`, `⁶`, `⁰`, `¹`) for numerical exponents.
- **Strict Prohibition of HTML Entities in Math Templates**: Never use HTML named entities (such as `&implies;`, `&lpar;`, `&rpar;`, `&alpha;`, `&theta;`, `&minus;`, etc.) in HTML math generation. Many entity names are non-standard, unhandled by rendering engines, or fail silently in headless Chromium, leaking literal text like `&implies;` directly into the student booklet.
  ALWAYS use direct UTF-8 Unicode characters:
  - Arrows & Relations: `⇒`, `→`, `⇔` (never `&implies;` or `&rArr;`)
  - Parentheses: `(`, `)` (never `&lpar;` or `&rpar;`)
  - Greek letters: `α`, `β`, `θ`, `π` (never `&alpha;` or `&theta;`)
  - Operators & Math signs: `−` (true minus U+2212), `×`, `÷`, `·`, `±`, `√`, `∠`, `°`
- **Enforced Anti-Raw-LaTeX & Entity Pre-Flight Gate**: When using HTML-based math rendering, NEVER allow raw LaTeX control sequences (`\text{...}`, `\text{LHS}`, `\text{RHS}`, `\quad`, `\checkmark`, `\left`, `\right`, `\implies`, `\times`) to leak into the HTML body. Use natural Persian text (`طرف اول:`, `طرف دوم`, `✓ (حکم ثابت شد)`).
  Before delivering any PDF to the user, MUST execute pre-flight and post-build assertions:
  ```bash
  python3 -c "
  import re, html, pypdf
  # 1. HTML validation
  t = open('doc.html').read()
  raw_macros = re.findall(r'\\\\[a-zA-Z]+', t)
  assert not raw_macros, f'Forbidden raw LaTeX macros: {set(raw_macros)}'
  raw_ents = re.findall(r'&[a-zA-Z0-9#]+;', t)
  assert not raw_ents, f'Forbidden HTML entities found (use direct Unicode): {set(raw_ents)}'
  
  # 2. PDF text verification (after chromium compile)
  reader = pypdf.PdfReader('doc.pdf')
  pdf_text = ''.join(p.extract_text() or '' for p in reader.pages)
  assert '&' not in pdf_text, 'Unescaped & entity found in PDF'
  assert not re.search(r'\\)\\d+=', pdf_text), 'Flattened exponent like )2= found in PDF'
  print('Pre-delivery verification passed: 100% clean PDF text!')
  "
  ```
  Fail the build immediately if any unrendered macro, ampersand entity, or broken symbol is found.
- **Embedded Figures**: Centered, sharp vector SVG or 300+ DPI images adjacent to the relevant question.
  - **BiDi Flip Guard in SVG Vector Diagrams**: In RTL HTML documents (`dir="rtl"`), Chromium's text shaping engine reverses mixed alphanumeric strings, coordinates, dimensions, and radicals inside SVG `<text>` elements (e.g. `5√2` renders flipped as `2√5`, `32√5` as `5√32`, `150cm` as `cm150`, `P(1-3a, 4a)` as `(4a, 1-3a)P`). ALWAYS add `direction="ltr"` to `<text>` elements containing formulas, dimensions, coordinates, or units inside SVG figures.
  - **KaTeX Error Fallback & Red Error Text Gate**: When rendering KaTeX server-side with `throwOnError: false`, syntax errors (unclosed braces like `\frac{1}{\sqrt{3}`, unsupported macros, or Persian characters inside `\text{...}` that lack font metrics) silently emit `<span class="katex-error" style="color:#cc0000">...</span>`, leaking raw red LaTeX code directly into the compiled exam PDF. ALWAYS assert `assert '<span class="katex-error"' not in html` before Chromium compilation.
  - **Complete Question Preservation**: When solving or restructuring an exam booklet, never silently drop numbered questions (such as cross-topic questions between chapters). Preserve the full numbered sequence or explicitly account for every question.

## Scanned Exam Document Ingestion (CamScanner Workflow)
When a user provides a CamScanner or image-only PDF (`pypdf` page text length is 0):
1. Extract page images directly using `pypdf.PdfReader(path).pages[i].images`.
2. Transcribe and parse question texts using the active multimodal model with base64 `image_url` data payload via local inference bridge (e.g., 9router `127.0.0.1:20128`), bypassing external cloud vision endpoints that time out under host egress restrictions.
3. Formally verify every mathematical step, formula, and option in Python using SymPy before writing solutions.
4. Compile cleanly with headless Chromium and verify the PDF text before delivery.

## Web App Alternative & Fallback (Web Link Delivery)
When user asks for a web view, web link, or when headless PDF layout has issues (such as flexbox superscript flattening or mobile responsive viewing needed):
- Build an interactive single-page web app with client-side MathJax (`tex-svg.min.js`), Vazirmatn font, dark/light theme switcher, quick-navigation anchor buttons (`#q1`, `#q2`), and responsive cards.
- Client-side MathJax completely eliminates baseline flattening and LaTeX conversion issues because the client browser renders full TeX equations dynamically with vector SVG precision.
- **Publishing & Delivery**:
  1. **GitHub Pages**: Push HTML to the showcase repo (`armin-hermes/hermes-showcase`), which serves on `https://armin-hermes.github.io/hermes-showcase/<path>/`.
  2. **Google Drive Link**: Use `gdrive-upload <path> [name.html]` to provide a direct web view / download link (`https://drive.google.com/file/d/.../view?usp=drivesdk`).

## Answer Booklet Pedagogical Architecture
- **Strategic Insight (نقشه راه)**: 2 lines on conceptual approach before calculations.
- **Detailed Steps**: Fully spelled-out algebraic derivations without skipping steps.
- **Teacher Trap (دام تستی / تله مصحح)**: Explicit callout on sign errors, quadrant mistakes, or domain traps.
- **Verification (راستی‌آزمایی)**: Fast numerical check with reference angles.
