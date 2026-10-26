---
name: exam-pdf-typesetter
description: "Use when typesetting Persian STEM exams and test booklets."
version: 1.1.0
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
- **Enforced Anti-Raw-LaTeX & Entity Pre-Flight Gate**: When using HTML-based math rendering, NEVER allow raw LaTeX control sequences (`\text{...}`, `\text{LHS}`, `\text{RHS}`, `\quad`, `\checkmark`, `\left`, `\right`, `\implies`, `\times`) to leak into the HTML body. Use valid standard HTML entities (`&times;`, `&radic;`, `&#10003;`, `&rArr;` or literal `⇒`) and natural Persian text (`طرف اول:`, `طرف دوم`, `✓ (حکم ثابت شد)`). **CRITICAL TRAP**: Never use `&implies;` — it is not a valid HTML entity and renders literally as `&implies;` in the output; use `&rArr;` or Unicode `⇒`.
  Before and after compiling, MUST execute pre-flight and post-build assertions:
  ```bash
  python3 -c "
  import re, html, pypdf
  # 1. HTML validation
  t = open('doc.html').read()
  raw_macros = re.findall(r'\\\\[a-zA-Z]+', t)
  assert not raw_macros, f'Forbidden raw LaTeX macros: {set(raw_macros)}'
  for ent in set(re.findall(r'&[a-zA-Z0-9#]+;', t)):
      assert html.unescape(ent) != ent, f'Invalid HTML entity: {ent}'
  
  # 2. PDF text verification (after chromium compile)
  reader = pypdf.PdfReader('doc.pdf')
  pdf_text = ''.join(p.extract_text() or '' for p in reader.pages)
  assert '&implies;' not in pdf_text, 'Unescaped &implies; found in PDF'
  assert not re.search(r'\\)\\d+=', pdf_text), 'Flattened exponent like )2= found in PDF'
  "
  ```
  Fail the build immediately if any unrendered macro or broken entity is found.
- **Embedded Figures**: Centered, sharp vector SVG or 300+ DPI images adjacent to the relevant question.

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
