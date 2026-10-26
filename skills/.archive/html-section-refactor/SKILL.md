---
name: html-section-refactor
description: Edit sections of existing single-file HTML websites.
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [html, css, javascript, refactoring, single-file, web, edit, enhance]
    related_skills: [claude-design, simplify-code]
---

# HTML Section Refactor

Use this skill when the task is to **edit, enhance, or refactor a specific section** of an existing single-file HTML website — not create a new artifact from scratch.

This is distinct from `claude-design` (which creates new HTML artifacts) and `simplify-code` (which cleans up existing code). This skill handles the workflow of modifying coordinated CSS + HTML + JS sections within a single file.

## Linked References

- `references/github-contents-api-push.md` — fallback for deploying single-file HTML to GitHub Pages when `git push` fails (proxy/firewall). Includes SHA requirement, base64 truncation pitfall, and size verification.

## When To Use

- Enhancing a specific section of an existing HTML landing page
- Adding new CSS animations/styles to an existing page
- Refactoring JavaScript functions while keeping the single-file structure
- Updating content in a section (management panels, dashboards, etc.)
- Applying the same changes to multiple copies of a file (e.g. different platform versions)

## When NOT To Use

- Creating a new HTML artifact from scratch → use `claude-design`
- Cleaning up code quality across multiple files → use `simplify-code`
- The file is part of a multi-file project with build tools → use standard dev workflow

## Core Workflow

### Step 1: Understand the File Structure

Read the full file (or key sections) to identify:
- **Section markers** — HTML comments like `<!-- SECTION 3: ... -->`
- **CSS block** — locate `</style>` closing tag
- **JS function locations** — grep for function names, variable declarations
- **Initialization code** — where functions are called (e.g. inside `DOMContentLoaded`)

```bash
# Quick way to find section boundaries
grep -n "SECTION\|</style>\|function \|const " file.html | head -30
```

### Step 2: Create Temp Files for New Content

Write new content to temporary files rather than trying to inline complex changes:
- `_new_css.css` — new CSS additions
- `_new_section3.html` — replacement HTML for a section
- `_new_js.js` — replacement JavaScript

This lets you preview and edit the new content before applying.

### Step 3: Apply with `execute_code` + Python

Use `execute_code` (not `delegate_task`) to do coordinated replacements:

```python
from hermes_tools import read_file

# Read temp files
new_css = open("_new_css.css", "r", encoding="utf-8").read()
new_section = open("_new_section3.html", "r", encoding="utf-8").read()

# Apply to the main file
with open("index.html", "r", encoding="utf-8") as f:
    content = f.read()

# Replace CSS (add before </style>)
css_end = content.find("</style>")
content = content[:css_end] + new_css + "\n    " + content[css_end:]

# Replace HTML section (between comment markers)
start = content.find("<!-- SECTION 3: ... -->")
end = content.find("<!-- SECTION 4: ... -->")
content = content[:start] + new_section + content[end:]

# Replace JS section (between function markers)
js_start = content.find("const managementData = [")
js_end = content.find("// Next section")
content = content[:js_start] + new_js + content[js_end:]

# Write back
with open("index.html", "w", encoding="utf-8") as f:
    f.write(content)
```

### Step 4: Clean Up

Remove temp files after successful application:
```bash
rm -f _new_css.css _new_section3.html _new_js.js
```

### Step 5: Verify

- Check line count changed as expected
- Grep for key new elements to confirm they're present
- If possible, open in browser to verify

## Why NOT Use `delegate_task`

**Subagents get stuck on `execute_code` approval.** When a subagent tries to run `execute_code`, it hits an approval prompt that requires user interaction — but subagents can't interact with users. This causes them to hang indefinitely.

For coordinated single-file HTML edits, always use direct `execute_code` in the parent session where approval is one-shot.

## Duplicate File Pattern

When the same site exists in multiple copies (e.g. different platform versions with minor URL changes):

```python
for filepath in ["site-ble/index.html", "site-telegram/index.html"]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Apply same replacements
    content = content[:start] + new_content + content[end:]
    
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(content)
```

## RTL Web UI / Localization
- If a UI dynamically switches languages or localized text modes (e.g., Arabic/Persian vs English), ensure you toggle fonts and text-direction explicitly on the elements displaying the text.
- Relying on Latin-only fonts (like `Outfit`) for RTL languages breaks font rendering. Apply a class (like `font-vazirmatn`) via JS when injecting localized names.
- When creating puzzles, grids, or data layouts that require exact directional ordering (like a Periodic Table where Group 1 must be on the left), set the container and elements to `dir="ltr"` so RTL global settings do not flip the scientific layout.
- Decouple modal content clicks from modal background clicks to allow for easy "click-outside-to-close" behavior (`onclick="event.stopPropagation()"` on content, `onclick="close()"` on background).

## Section Boundary Patterns

Common patterns for finding where to make replacements:

| What | Marker Pattern | Example |
|------|---------------|---------|
| HTML section | `<!-- SECTION N: NAME -->` | `<!-- SECTION 3: MANAGEMENT -->` |
| CSS block | `</style>` | Add new CSS before this |
| JS functions | Function/variable names | `const managementData = [` |
| JS sections | Comment dividers | `// ========== SECTION ==========` |
| Init code | DOMContentLoaded | `selectManagementTab(0);` |

## Pitfalls

- **Never use `delegate_task` for this workflow** — subagents hang on `execute_code` approval
- **Always use `encoding="utf-8"`** when reading/writing files — especially for Persian/Arabic/RTL content
- **Find exact markers** before replacing — read the file first, don't guess
- **Test on one file first** before applying to duplicates
- **Preserve file encoding** — RTL files may have specific encoding requirements
- **Check for trailing whitespace** in markers — `find()` is exact string matching
- **NEVER patch minified single-line JS with the `patch` tool** — minified functions are often 1000+ char single lines; `patch` old_string/new_string matching on fragments of these lines silently corrupts brace balance, merges adjacent functions, or drops function bodies. Instead: extract the `<script>` block to a temp `.js` file, edit it there with proper formatting, validate with `node -e "new Function(fs.readFileSync('temp.js','utf-8'))"`, then reassemble the HTML via `execute_code`.
- **Validate JS after EVERY edit** — run `node -e "new Function(jsContent)"` or use `execute_code` to check brace balance. Python's `compile()` cannot validate JS (it flags valid JS Unicode chars like `─` as errors). Node.js `new Function()` is the correct validator.
- **GitHub Contents API base64 payload size pitfall** — when constructing base64 payloads for the GitHub API using shell commands like `$(python -c "import base64; print(...)")`, large files (like 50KB+ HTML) will get truncated because shell variable substitution and command-line length limits clip the base64 string. This results in the API uploading a truncated file (e.g., 3KB instead of 50KB) that only contains the start of your code. **Fix:** build and submit the API payload entirely within an `execute_code` Python script, avoiding shell pipes entirely (e.g., write the base64 to a temp file, construct the JSON, and use `requests` or `subprocess.run` to call curl with `-d @payload.json`).
- **Brace-counting is unreliable for minified JS** — braces inside string literals, template literals, and regex skew simple `{`/`}` counts. Always use a real JS parser (Node.js) for validation, never character counting.
- **When JS is broken after multiple patch attempts, stop patching** — restore from git (`git show <hash>:file`) or rewrite the JS block entirely via `write_file`/`execute_code`. Three failed patches on the same region means the approach is wrong.