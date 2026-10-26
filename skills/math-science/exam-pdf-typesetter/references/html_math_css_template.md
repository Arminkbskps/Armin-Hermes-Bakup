# Pure CSS Math Layout for Headless Chromium PDF

To prevent unrendered raw LaTeX artifacts (e.g., `\frac{...}{...}`) from appearing in generated exam PDFs, use this battle-tested flexbox CSS math layout. It requires zero JS dependencies and renders with sharp vector horizontal vinculums.

```css
.math {
  font-family: 'Cambria Math', 'Times New Roman', serif;
  direction: ltr;
  display: inline-flex;
  align-items: center;
  font-size: 1.02rem;
  color: #0f172a;
  font-weight: 600;
  margin: 0 3px;
  vertical-align: middle;
}
.frac {
  display: inline-flex;
  flex-direction: column;
  vertical-align: middle;
  text-align: center;
  padding: 0 3px;
  font-size: 0.88em;
  line-height: 1.15;
  margin: 0 2px;
}
.num {
  border-bottom: 1.5px solid #0f172a;
  padding: 0 2px 2px 2px;
}
.den {
  padding: 2px 2px 0 2px;
}
.sqrt {
  display: inline-flex;
  align-items: center;
}
.sqrt-sym {
  font-size: 1.25em;
  margin-right: 1px;
}
.sqrt-bar {
  border-top: 1.5px solid #0f172a;
  padding: 0 2px;
}
.exp, .math sup {
  font-size: 0.75em !important;
  vertical-align: super !important;
  line-height: 0 !important;
  position: relative;
  top: -0.45em;
  margin-left: 1px;
}
```

## Superscript Rule
Never rely on unstyled `<sup>` inside `inline-flex` math containers — Chromium flattens `<sup>` baseline offset, rendering `(x + 1)²` as `(x + 1)2=`.
Always use native Unicode superscripts (`²`, `³`, `⁴`, `⁶`, `⁰`, `¹`) or `<span class="exp">2</span>`.

## HTML Usage Examples

- **Fraction**: `<span class="math"><span class="frac"><span class="num">sin &theta;</span><span class="den">cos &theta;</span></span></span>`
- **Radical**: `<span class="math"><span class="sqrt"><span class="sqrt-sym">&radic;</span><span class="sqrt-bar">25 - cot²&alpha;</span></span></span>`
- **Mixed**: `<span class="math">cos &alpha; = - <span class="frac"><span class="num">12</span><span class="den">13</span></span></span>`

## Anti-Raw-LaTeX Pre-Flight Validator

When generating math solutions, models frequently leak unparsed LaTeX control strings into HTML blocks. These look broken in the final PDF:

| Raw Leaked String | Forbidden Output | Correct Clean HTML / Persian Replacement |
| :--- | :--- | :--- |
| `\text{LHS}` | `\text{LHS} = ...` | `طرف اول:` |
| `\text{RHS}` | `= \text{RHS}` | `= طرف دوم` |
| `\checkmark` | `\checkmark` | `&#10003;` or `✓ (حکم ثابت شد)` |
| `\quad` | `\quad` | `&nbsp;&nbsp;` |
| `\left( ... \right)` | `\left( ... \right)` | `( ... )` |
| `\implies` | `\implies` or `&implies;` (INVALID) | `&nbsp;&rArr;&nbsp;` or literal `⇒` |
| `\text{...}` | `\text{متر}` | `متر` (plain Persian text) |

### Automated Pre-Flight & Post-Build Check
Before and after running `chromium --print-to-pdf`, always run this validation:
```python
import re, html, pypdf

# 1. HTML validation
with open("exam.html") as f:
    html_text = f.read()

raw_latex = re.findall(r'\\[a-zA-Z]+', html_text)
if raw_latex:
    raise ValueError(f"CRITICAL: Found unrendered LaTeX commands in HTML: {set(raw_latex)}")

for ent in set(re.findall(r'&[a-zA-Z0-9#]+;', html_text)):
    if html.unescape(ent) == ent:
        raise ValueError(f"CRITICAL: Found invalid unescaped HTML entity: {ent}")

# 2. PDF text extraction verification
reader = pypdf.PdfReader("exam.pdf")
pdf_text = ''.join(p.extract_text() or '' for p in reader.pages)
if '&implies;' in pdf_text or '&' in pdf_text and ';' in pdf_text:
    raise ValueError("Found leaked entity string in compiled PDF text!")
if re.search(r'\)\d+=', pdf_text):
    raise ValueError("Found flattened exponent like ')2=' in PDF text! Use Unicode ² instead.")
```
