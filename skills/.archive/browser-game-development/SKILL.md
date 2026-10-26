---
name: browser-game-development
trigger: "When building HTML5 browser games."
description: "HTML5 game dev patterns and pitfalls."
---

# Browser Game Development

Patterns for HTML5 browser games with vanilla JS + Canvas 2D.

## Canvas Setup
DPR cap at 2. Always call setTransform after resize.

## Game Loop
Clamp dt to 0.033 max. Tab-background without clamp causes physics explosion.

## SVG Ships
Render to offscreen canvas via Blob URL. Pre-render in initLevel before loop starts.

## Periodic Table Puzzles / Interactive Grids
- **CSS Grid:** Use 18 columns (`repeat(18, minmax(45px, 1fr))`) and place elements precisely via `grid-column: X; grid-row: Y;` based on their real Group and Period.
- **Direction:** Set the grid container to `dir="ltr"` so Group 1 is properly on the far left, even in RTL interfaces (like Persian). Inside the element, enforce `direction: ltr` for the symbol and number to prevent layout breaking.
- **Font Switching:** If the puzzle switches between English symbols and localized names, toggle a CSS class (e.g., `font-english` vs `font-vazirmatn`) directly on the text element to prevent messy rendering of localized text in Latin-only fonts.
- **Data Source & Detail Richness:** Use a complete data mapping file (like `element_facts.js`) to decouple extensive educational descriptions and multi-point facts from the layout logic. Make descriptions high-quality, scientifically accurate, and rich in everyday applications.
- **Fact Carousels & Controls:** When presenting fact carousels, the next/prev buttons must map to standard reading directions:
  - *Next:* Moves index forward (`index = (index + 1) % length`) and shows a right-facing arrow (`>`).
  - *Prev:* Moves index backward (`index = (index - 1 + length) % length`) and shows a left-facing arrow (`<`).
- **Font & Theme Consistency:**
  - *Font Family:* For projects requiring strict aesthetic alignment, enforce the target font (e.g. `Vazirmatn`) globally on all text classes (including `.font-english`, timers, numbers, and inputs) to prevent visual inconsistency.
  - *Theme Toggle / Light Mode:* Add a toggle mechanism (using e.g. `[data-theme="light"]`) with transitions. Light themes must override primary dark colors carefully (e.g. backgrounds to `#f1f5f9`, cards/modals to `#ffffff`, text to `#0f172a`, and elements/selectors with proper contrast ratios) while preserving original distinct element category colors. Store the theme state in `localStorage` to persist across reloads.
- **Responsive Wrappers:** Allow overflow-x auto (`-webkit-overflow-scrolling: touch`) with a `min-width` on the grid container so mobile users can swipe-scroll the grid without breaking cells or text size.
- **Quiz Range Settings:** Allow user-defined ranges:
  1. *Category/Period filters:* Filter elements by periods or chemical categories using checkboxes. Keep game state elements in a filtered `currentPool`.
  2. *Interactive Grid Selection (Direct Click):* Let users directly click on elements on the grid itself to build their quiz pool. Create a distinct visual state (e.g. `.selection-mode` where unselected elements have lower opacity/saturation, and selected elements have a high-contrast shadow/border). Avoid overlapping click handlers by toggling cell behavior based on an `isSelectionMode` state variable.
- **Table Spacing & Layout:** In grid-based periodic tables, place an empty row spacer (e.g. `.period-8 { grid-row: 8; grid-column: 1 / span 18; height: 30px; pointer-events: none; background: transparent; }`) to create a clear visual separation between the main table blocks and the Lanthanide/Actinide block at the bottom. **Keep Lanthanides and Actinides stacked adjacent to one another** (e.g. period 9 and period 10 with no vertical margin or spacer between them) to maintain standard IUPAC layout representation.
- **In-Grid Column/Row Selectors:** When implementing manual selection mode, display inline click handles directly inside the grid layout to select entire rows/columns instead of separate control menus. 
  1. *Grid Dimensions:* Expand the grid columns to include an extra first column for row selector buttons, and add a first row for column selector buttons (e.g. 19 columns and 11 rows).
  2. *Position Shifts:* Dynamically offset element `grid-row` and `grid-column` coordinates by 1 when selector buttons are rendered to keep grid alignment correct. 
  3. *Dynamic Headers:* Add CSS buttons (e.g., class `.col-selector-btn` and `.row-selector-btn`) styled with unique hover outlines and small text labels (e.g., `C1`–`C18`, `R1`–`R7`, `La`, `Ac`) in the first row/column cells. Trigger batch selection logic on click. Ensure these headers are completely removed and coordinates shifted back when exiting selection mode.
  4. *Toggle Behavior:* Selectors must implement a true toggle action: if **all** target elements in that row/column are already selected, deselect them all. Otherwise, select them all.
  5. *Alignment & Spacing:* Ensure that the grid layout placement styles (like `.period-9` or `.group-18` in CSS) do not override the dynamic inline style coordinates (`grid-row`/`grid-column`) when headers are injected. In CSS, scope base coordinate classes (e.g., using `:not([style*="grid-row"])`) so that dynamic Javascript alignments take precedence. Ensure the spacer element (`.period-8`) is dynamically created exactly once, positioned at row 9 (under header layout) or row 8 (under normal layout), and spans the correct column count (19 columns with headers, 18 columns without).

## Custom Global Scrollbars
- **Theme Matching Scrollbars:** Replace standard browser scrollbars with custom neon/gradient variants. Use CSS pseudo-elements:
  ```css
  ::-webkit-scrollbar { width: 10px; height: 10px; }
  ::-webkit-scrollbar-track { background: #0b1329; border-radius: 8px; }
  ::-webkit-scrollbar-thumb {
      background: linear-gradient(180deg, #0ea5e9, #a855f7);
      border: 2.5px solid #0b1329;
      border-radius: 8px;
  }
  ::-webkit-scrollbar-thumb:hover {
      background: linear-gradient(180deg, #38bdf8, #c084fc);
  }
  ```
- **Horizontal Scroll Styling:** For components with horizontal scrolls (like `.table-wrapper`), use a horizontal gradient (`linear-gradient(90deg, ...)`) on the thumb to align with the scroll direction.

## GitHub Database (Leaderboard) Performance
- **Local Cache First:** To solve latency and API limitations of using GitHub repositories as database storage, always save the user's score to `localStorage` first and render the leaderboard immediately.
- **Background Async Syncing:** Save to the remote repository asynchronously in the background. Once the request resolves, update `localStorage` with the final sorted data from the server and refresh the UI.
- **Unique Records / Deduplication:** Maintain only a single record per user. Before pushing a score, search if the user exists and only overwrite it if their new score is higher (`score > existing.score`).
- **Responsive Design & Typography:** Apply vertical scroll wrappers (`max-h-[50vh] overflow-y-auto`) and text truncation (`truncate`, `max-w-[Xpx]`) on name strings so long names don't expand elements on mobile. Use flexbox with badge accents (#1 Gold, #2 Silver, #3 Bronze) and standard dark-mode borders for a polished, responsive dashboard look.

## Story / Adventure Map Mode (progressive learning campaigns)
- **Golden rule — teach what you quiz:** each level's quiz range must be exactly the set of elements taught so far (level 1 quizzes 1 element, level 2 quizzes both, ...). Compute quiz ranges *automatically and cumulatively* from `teachNums` arrays instead of hand-maintaining them; validate with a script that walks all levels and asserts every quiz element appears in some earlier-or-same teach list. Hand-written quiz lists WILL drift and the user will notice ("باید چیزی که درس داده رو امتحان بگیره").
- **Level/region gating:** a level unlocks only after the previous level is completed; a region unlocks after ALL its levels are done. Persist progress in localStorage keyed `'regionId/levelId'` → best score.
- **Story mode must NOT touch the global leaderboard** — no score submission, no leaderboard modal popup, no local_leaderboard writes. Guard with a `storySession` flag checked at endGame. Beware: clearing the flag inside `completeStoryLevel()` BEFORE the leaderboard check makes the guard always-pass; keep story identity intact through the whole endgame flow.
- **Teach-modal element locator:** each taught element gets a 📍 button that hides the intro modal, spotlights the element on the real table (rotating glow keyframe), shows a floating marker with row/column info positioned via `getBoundingClientRect()`, then auto-returns to the intro after ~4s.
- **Boot-camp sequence:** before the quiz starts, dim every cell (`opacity:.13 + grayscale`) then spotlight newly-taught elements one by one (~900ms apart) with rising musical notes; provide a skip button. Hide the start panel during it.
- **Modal stacking order matters:** stacked fixed modals need explicit descending z-indexes — info card ABOVE level-intro (`z-[70]` > `z-[60]`), bootcamp overlay `z-80`, confetti `z-95`. A card opening *under* its parent modal looks like "clicking does nothing" to the user.

## Web Audio SFX (no asset files)
Small `SFX` object of `playTone(freq, dur, type, gain, delay)` calls. Juice that lands well: correct-answer arpeggio whose base pitch rises with combo count; dramatic 3-note descending jingle + screen-shake class on life loss; heart-pop animation synced to lives render (re-trigger by toggling class + `void el.offsetWidth`); urgent high-pitch tick for final 3 countdown seconds; rising note per element in boot-camp. Keep a master sound toggle persisted in localStorage; create AudioContext lazily inside try/catch.

## Level Pagination
PER_PAGE=5. Show arrows + counter. overflow:hidden on container.

## 2P Input Isolation
P1: WASD only. P2: Arrow keys only. Never share key checks between players.

## Pitfalls
- isL scoping: pass theme to render sub-functions
- AudioContext: wrap in try/catch
- GitHub Pages cache: 15-30s stale, user needs Ctrl+Shift+R
- SSL on Windows: use GIT_SSL_NO_VERIFY=1
- **PWA service-worker cache trap (bites twice):** after ANY change to cached core assets, bump `CACHE_NAME` (e.g. `periodic-puzzle-v2` → `v3`) AND update the `CORE_ASSETS` list if files were added/renamed. Two failure modes: (1) your own E2E tests keep loading the OLD app from SW cache even though disk files are correct — unregister SWs and delete caches via CDP before asserting; (2) users see stale versions post-deploy — tell them to refresh once or twice so the new SW takes over (`clients.claim()`).
- **updateStats ordering:** render stats AFTER mutating lives/score, not before, or UI lags one event behind.
- **Double-penalty bug pattern:** when a wrong-answer handler calls a helper that already applies the score penalty, do not also subtract inline — audit both paths (click-wrong AND challenge-timeout) for duplicated mutations.
- Full E2E testing workflow over CDP: see [references/cdp-e2e-testing.md](references/cdp-e2e-testing.md)
