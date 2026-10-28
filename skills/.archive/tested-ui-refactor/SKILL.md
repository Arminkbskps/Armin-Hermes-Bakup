---
name: tested-ui-refactor
description: >-
  Refactor tested frontend UI without breaking its harness.
version: 1.0.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Frontend, Refactor, Testing, DOM, CDP]
    related_skills: [merge-reconciler]
---

# Refactoring a Tested UI Without Breaking It

## When to Use

Load this skill when you are about to restyle, re-markup, or migrate icons in
a frontend project that has DOM-querying tests (CDP scripts, `getElementById`
/ `querySelector` assertions, `textContent` matching) — before you write any
markup. Triggers: emoji-to-SVG migration, component redesign, visual overhaul,
"beautify" requests on a tested app.

Visual overhauls on a project with a DOM-querying test harness (CDP-driven
`.mjs` scripts, `getElementById` / `querySelector` assertions) need two extra
checks beyond normal polish work: don't clobber parallel work, and don't break
the harness contract.

## Procedure

### 1. Check for parallel work before writing anything

Run `git status` and `git diff --stat` first. Uncommitted modifications you did
not make, or untracked files you did not create (e.g. a new `icons.js`, edited
tests), mean another session is active in the same tree.

- Treat any write-tool "file was modified since you last read it" warning as
  STOP: re-read the current disk state and reconcile — never blind-overwrite
  with a full-file write.
- Prefer `patch` (targeted edits) over `write_file` (whole-file rewrite) on
  files another session may be touching.

### 2. Inventory test hooks before changing markup

Grep the test scripts for `getElementById`, `querySelector`, and
`textContent` / `innerHTML` matches. Every ID, class, and data attribute the
harness queries is a contract: keep those hooks stable, or update the tests in
the same change. Pay special attention to:

- IDs the harness clicks or reads (`start-btn`, `story-map-list`, modals).
- Classes the harness counts (`.map-level-btn`, `.puzzle-target`, `.filled`).
- `textContent` assertions (`modal-title` includes 'تبریک', win-path checks).

### 3. Migrating emoji to SVG icons

- Establish ONE icon convention matching the repo (inline SVG sprite with
  `<use>`, or a JS `icon(name, cls)` helper returning SVG strings) — never
  introduce a second system.
- When tests count rendered characters (e.g.
  `(livesEl.textContent.match(/❤️/g) || []).length`), give the new icon markup
  semantic classes (e.g. `#lives .life-on` for filled hearts, `.life-off` for
  empty) and switch the harness to the class selector in the same change.
- Keep dynamic regions' text hooks intact: combo popups, score popups, and
  stat chips are asserted via `textContent.slice(...)` — icons added alongside
  the text are fine, replacing the asserted text is not.
- Match icon stroke weight to adjacent text weight (1.5px beside regular,
  2px beside semibold); one stroke weight per set; `currentColor` for states.

### 4. Verify

- Run the project's own validators first if present (e.g. `node
  validate_map.cjs`, `node check_coverage.cjs` for data invariants like
  full 118-element coverage or teach-before-quiz rules).
- Run the DOM harness suites that touch the refactored surfaces and confirm
  green before handing back.
- If the app is a PWA, bump the service-worker cache name and add any new
  asset (e.g. `./icons.js`) to the precache list so offline tests see fresh
  files.

Worked example with hook inventory, emoji counts, and a parallel-work
recovery transcript: `references/periodic-puzzle-session.md`.

## Pitfalls

- **Full-file writes over parallel work**: a `write_file` based on a stale
  read silently discards the other session's changes (new script tags, new
  helpers, test updates). Re-read after any staleness warning.
- **Changing counted content without updating the counter**: replacing `❤️`
  text with SVG drops `match(/❤️/g)` counts to zero — the game logic is fine
  but every hearts assertion fails. Update harness selectors atomically.
- **Renaming classes the harness queries**: `.map-region` / `.map-level-btn`
  style redesigns must keep those class names (add new classes alongside).
- **New modal/section, missing test IDs**: any new interactive surface (e.g. a
  quick-review flashcard modal) should get stable IDs from the start so the
  harness can reach it later.
