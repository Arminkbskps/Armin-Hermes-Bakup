---
name: exam-pdf-typesetter
description: "Use when typesetting Persian STEM exams and test booklets."
version: 1.4.0
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
- **Math & Formulas**:
  - **Strict Prohibition of Slash Fractions (`1/3`, `2/3`, `a/b`)**: NEVER write fractions with an inline forward slash (e.g., `1/3`, `2/3`, `1/a3`, `4/3`) anywhere in question stems, options, pedagogical roadmaps, derivations, or trap boxes. In Persian typography, `1/3` resembles a decimal number (`۱٫۳` - یک و سه دهم) or causes severe misinterpretation. Every single fraction MUST be a vertical stacked fraction (کسر طبقاتی) with an explicit horizontal fraction bar.
  - **Compound & Multi-Level Fractions (کسر طبقاتی مرکب)**: When fractions are nested within fractions (e.g. `\frac{\frac{1}{3}}{\frac{2}{3}}` or `\frac{34}{\frac{11}{12}}`), the primary fraction bar MUST be distinctly longer, thicker, and centered relative to the sub-fraction bars so the hierarchy of operations is unmistakable at a glance.
  - **Preferred Offline KaTeX Engine**: Pre-render all LaTeX math directly into static HTML via local KaTeX (`bun -e "const katex = require('...'); ..."` or node) and inline `katex.min.css`. This completely eliminates font flattening, baseline shifts, and CDN network dependencies while producing publication-grade vertical fractions and superscripts.
  - **Unicode Superscripts Over HTML `<sup>`**: In flexbox math containers (`display: inline-flex`), Chromium's PDF renderer flattens `<sup>` tags to the baseline, rendering expressions like `(3 tan α + 2)²` as `(3 tan α + 2)2=`. Always use true Unicode superscript glyphs (`²`, `³`, `⁴`, `⁶`, `⁰`, `¹`) for numerical exponents when using raw HTML, or use KaTeX.
- **Strict Prohibition of HTML Entities in Math Templates**: Never use HTML named entities (such as `&implies;`, `&lpar;`, `&rpar;`, `&alpha;`, `&theta;`, `&minus;`, etc.) in HTML math generation. Many entity names are non-standard, unhandled by rendering engines, or fail silently in headless Chromium, leaking literal text like `&implies;` directly into the student booklet.
  ALWAYS use direct UTF-8 Unicode characters:
  - Arrows & Relations: `⇒`, `→`, `⇔` (never `&implies;` or `&rArr;`)
  - Parentheses: `(`, `)` (never `&lpar;` or `&rpar;`)
  - Greek letters: `α`, `β`, `θ`, `π` (never `&alpha;` or `&theta;`)
  - Operators & Math signs: `−` (true minus U+2212), `×`, `÷`, `·`, `±`, `√`, `∠`, `°`
- **Headless Chromium Offline Math Rendering (No Remote CDN)**:
  When generating PDFs via headless Chromium (`--print-to-pdf`), NEVER load external MathJax CDNs (e.g. `cdn.jsdelivr.net/.../tex-svg.js`). In environments with proxy or egress restrictions, remote asset requests fail silently (`handshake failed; net_error -101`), dumping raw unresolved TeX expressions (`\sin^2 x`, `\frac{...}{...}`) into the final PDF.
  Always pre-render math via local KaTeX with bundled CSS, or use pure offline CSS fractions:
  ```css
  .fraction { display: inline-flex; flex-direction: column; vertical-align: middle; text-align: center; padding: 0 3px; font-size: 0.95em; line-height: 1.05; }
  .fraction .num { border-bottom: 1.5px solid currentColor; padding-bottom: 1px; }
  .fraction .den { padding-top: 1px; }
  ```
- **Chromium PDF Flags (Suppressing Browser Header/Footer)**:
  When rendering via headless Chromium, ALWAYS pass `--no-pdf-header-footer` along with standard flags:
  ```bash
  chromium --headless --no-sandbox --disable-gpu \
    --allow-file-access-from-files \
    --run-all-compositor-stages-before-draw \
    --no-pdf-header-footer \
    --print-to-pdf=output.pdf input.html
  ```
- **Page Balancing & Orphan Elimination**:
  When using `page-break-inside: avoid;` on question cards (`.q-card`):
  - Avoid cards exceeding ~950px of printable height on A4. If an SVG diagram is included, keep its height compact (100px to 130px max) so the complete question (Stem, Options, SVG, Steps, Trap box) fits on one page.
  - Never place a page break immediately between a section header and its first question card; group the section bar with the first question card (or place the `page-break-before: always;` on the section bar itself with `margin-top: 0;`) so section titles never sit alone on an orphaned page.
  - Post-build assertion: Check page text lengths with `pypdf` to ensure no page has <150 characters (orphaned headings or 1-line spillovers).
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
  assert not re.search(r'[0-9]+/[0-9]+', pdf_text), 'Slash fraction found instead of stacked fraction'
  for i, p in enumerate(reader.pages):
      txt = p.extract_text() or ''
      assert len(txt.strip()) > 150, f'Page {i+1} is orphaned/too short ({len(txt)} chars)'
  print('Pre-delivery verification passed: 100% clean PDF text!')
  "
  ```
- **Embedded Figures**: Centered, sharp vector SVG or 300+ DPI images adjacent to the relevant question.

## Scanned Exam Document Ingestion (CamScanner Workflow)
When a user provides a CamScanner or image-only PDF (`pypdf` page text length is 0):
1. **Extract Images**: Extract page images directly using `pypdf.PdfReader(path).pages[i].images`.
2. **Page Orientation & Sideways Detection**:
   CamScanner and phone scans frequently contain sideways pages (width > height). Multimodal vision models fail or hallucinate formulas when reading vertical/sideways text. Check dimensions in PIL; if rotated, apply `image.rotate(90, expand=True)` (or 270°) before transcribing.
3. **Payload Downscaling & Question Slicing**:
   Uploading raw 4000x3000 scans (>2MB) to vision endpoints causes read timeouts and 429 quota exhaustion. Downscale full pages with `thumbnail((1200, 1200))` or slice individual question bounding boxes (<100KB) to ensure rapid, error-free transcription.
4. **Formal SymPy Verification**:
   Formally verify every mathematical step, formula, and option in Python using SymPy before drafting solutions.
5. **Compile & Pre-Flight Gate**:
   Compile cleanly with headless Chromium (`--no-pdf-header-footer`) and run the pre-flight verification script to confirm zero raw LaTeX leakage and zero name leakage.

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
