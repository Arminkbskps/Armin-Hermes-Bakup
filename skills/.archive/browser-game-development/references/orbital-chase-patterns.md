# Orbital Chase — Session Patterns

## Theme State Scoping Bug
When `const isL = ...` is defined inside `render()`, sub-functions like `drawPowerups()` don't have access.
Fix: pass `isL` as parameter to every render sub-function.

```javascript
// BUG
function render() {
  const isL = document.body.getAttribute('data-theme') === 'light';
  drawPowerups(); // isL is not defined here!
}
function drawPowerups() {
  X.fillStyle = isL ? '...' : '...'; // ReferenceError
}

// FIX
function render() {
  const isL = document.body.getAttribute('data-theme') === 'light';
  drawPowerups(isL); // pass it
}
function drawPowerups(isL) { // receive it
  X.fillStyle = isL ? '...' : '...';
}
```

## 2P Input Bug Pattern
Player 1 checking `keys['arrowup']` causes P2's arrow input to also move P1.

```javascript
// BUG: P1 uses both WASD and arrows
if (keys['w'] || keys['arrowup']) ay -= 1;

// FIX: P1 uses WASD only
if (keys['w']) ay -= 1;
// P2 uses arrows only (in else branch)
```

## Orbitron + Persian
Orbitron is Latin-only. Persian text renders as boxes. Use Lalezar for Persian headings.

## GitHub Pages Deployment
1. Create repo via API
2. Push code
3. Enable Pages via API: POST /repos/{owner}/{repo}/pages
4. Wait 15-30s for deploy
5. User must hard-refresh (Ctrl+Shift+R) to see updates

## Pagination HTML Pattern
```html
<div class="level-select-wrap">
  <button class="page-arrow" id="pagePrev" disabled>◀</button>
  <div class="level-select" id="levelSelect"></div>
  <button class="page-arrow" id="pageNext">▶</button>
</div>
<div class="page-counter" id="pageCounter">1 / 4</div>
```

CSS: overflow:hidden on .level-select, flex:1 on cards, flex-shrink:0 on arrows.
