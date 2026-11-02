---
name: persian-stem-typesetting
description: "Use when typesetting Persian STEM exam PDFs with KaTeX."
version: 1.0.0
author: Armin & Hermes
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [exam, test, pdf, typst, persian, katex, svg, stem]
---

# Persian STEM Typesetting & PDF Generation

Production-ready typesetting of Persian multiple-choice and descriptive STEM exams and answer booklets using KaTeX and headless Chromium.

## When to Use
- Use when generating or repairing print-ready PDF exam booklets, solutions, or drills in Persian (Math, Physics, Chemistry).
- Use when rendering mathematical formulas with KaTeX in RTL HTML/PDF documents.
- Use when embedding SVG geometric figures or diagrams alongside Persian math text.

## Core Rules & Typography Standards
1. **KaTeX Delimiter & Purity Rules**:
   - **Zero Persian Characters Inside KaTeX**: KaTeX math fonts lack metrics for Arabic/Persian glyphs. Writing Persian words inside `\text{...}` in KaTeX (e.g., `H_{\text{کل}}` or `(x \text{ در ربع اول})`) causes missing font metrics, layout glitches, or runtime process aborts (`SIGABRT`). Always place Persian labels in standard HTML tags outside math delimiters.
   - **Syntax Validation**: Never leave unclosed braces (e.g., `\frac{1}{\sqrt{3}` missing `}`). In KaTeX, any syntax error emits a `<span class="katex-error" style="color:#cc0000">` element, which leaks raw red LaTeX code directly onto the printed page.
   - **Strict Stacked Fractions**: Always use vertical fractions (`\frac{a}{b}`) rather than inline slashes (`a/b`), which read as decimal separators in Persian (e.g., `1/3` reading as `۱٫۳`). Multi-story fractions must have distinct, thicker main division bars.

2. **SVG BiDi Protection for Numerics & Radicals**:
   - In RTL documents (`<html dir="rtl">`), the browser's Unicode Bidirectional (BiDi) algorithm flips neutral mathematical symbols between numbers. Expressions like `5√2` or `32√5` or `45°` inside SVG `<text>` elements get rendered in reverse (`2√5`, `5√32`).
   - ALWAYS explicitly set `direction="ltr"` (or `<tspan direction="ltr">`) on every SVG text element containing numbers, radicals, coordinates, or units.

3. **Sampad / Konkur Pedagogical & Form Standards**:
   - **Rationalization (گویا کردن مخرج)**: Fractions with radicals in denominators (e.g., $\frac{\sqrt{3}a^2}{2(1+\sqrt{3})}$) must always be accompanied by their rationalized form ($\frac{(3-\sqrt{3})a^2}{4}$), as Iranian examiners and Sampad answer keys consider unrationalized answers incomplete.
   - **Kinematics & Multi-Link Angle Reference**: In mechanics / robotics problems with articulated arms, always explicitly clarify whether joint angle $\alpha$ is measured relative to the global horizontal reference or relative to the previous link.
   - **Option Audit Against Source**: Transcribe exam options with exact precision (e.g., verifying whether an option has $\sqrt{3} - 1$ or $\sqrt{2} - 1$, and checking open `<` vs closed `≤` inequalities on interval bounds).

4. **Automated Pre-Flight Gate (Run Before Every PDF Delivery)**:
   Always verify the generated HTML and PDF before sending to the user:
   ```bash
   python3 -c "
   import re, pypdf
   # 1. HTML validation
   html = open('output.html', encoding='utf-8').read()
   assert 'katex-error' not in html, 'KaTeX syntax error found in HTML!'
   raw_leaks = re.findall(r'\\\\[a-zA-Z]+', re.sub(r'<span class=\"katex\">.*?</span></span></span>', '', html, flags=re.DOTALL))
   assert not raw_leaks, f'Raw LaTeX leaked into text: {raw_leaks}'

   # 2. PDF text validation
   reader = pypdf.PdfReader('output.pdf')
   full_text = ''.join(p.extract_text() or '' for p in reader.pages)
   assert 'katex-error' not in full_text
   for name in ['armin', 'آرمین']:
       assert name not in full_text.lower(), f'Anonymity breach: {name}'
   print('Pre-flight gate passed: 100% clean PDF text!')
   "
   ```
