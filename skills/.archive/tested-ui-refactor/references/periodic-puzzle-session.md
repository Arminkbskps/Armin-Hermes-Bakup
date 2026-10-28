# Session notes: Periodic-Puzzle UI overhaul (2026-09-23)

Persian RTL chemistry game (Tailwind + vanilla JS + PWA). 6-item request:
fix modal X overlap, emoji → SVG icons, swap prev/next fact buttons,
Duolingo-style story map, quick-review flashcards, general beautification.

## Parallel-work incident (the reason step 1 exists)

- First reads showed `script.js` (2052 lines), `style.css` (921 lines), no
  `icons.js`. Based on that stale snapshot I did a full `write_file` of
  `index.html` (inline SVG sprite, new modals).
- `git status` afterwards revealed another session was active: `icons.js`
  (new, 11KB `ICON_PATHS` + `icon(name, cls)` helper), edits to `script.js`
  (+390), `style.css` (+1782), `sw.js`, and three test files. My full-file
  write silently discarded that session's `index.html` side (script tag for
  `icons.js`, `fact-box` markup it depended on).
- Recovery: `git diff --stat` + targeted `patch` instead of rewrites;
  adopted the existing `icon()` convention instead of the inline sprite.

## Test-hook contract found by grepping `test_*.mjs`

- IDs clicked/read: `player-name-input`, `submit-name-btn`, `start-btn`,
  `story-map-btn`, `begin-level-btn`, `restart-btn`, `quit-game-btn`,
  `challenge-mode-check`, `sound-toggle-btn`, `heatmap-btn`, `hint-btn`,
  `level-intro-modal`, `element-modal`, `story-map-modal`,
  `game-over-modal`, `leaderboard-modal`, `game-dashboard`,
  `challenge-bar-container`, `story-banner-live`, `bootcamp-overlay`,
  `locate-marker-box`, `modal-title`, `end-stats`, `final-score`.
- Classes counted: `.map-region`, `.map-level-btn`, `.puzzle-target`
  (+`:not(.filled)`), `.filled`, `.teach-element-chip`,
  `.teach-locate-btn`, `.teach-locate`, `.bootcamp-dim`, `.hint-pulse`,
  `.confetti-container`, `[class*="heat-"]`, `#info-desc .prop-box`.
- Text assertions: `modal-title` includes 'تبریک'; hearts counted via
  `textContent.match(/❤️/g)` → migrated to `#lives .life-on` class query
  (parallel session added `.life-on`/`.life-off` spans + updated 3 test
  files atomically in the same change).
- Data validators: `node validate_map.cjs` (teach-before-quiz golden rule),
  `node check_coverage.cjs` (118-element coverage) — run before DOM tests.

## Emoji inventory (60 hits: index.html 12, script.js 35, story_map.js 13)

Hearts ❤️🤍, trophy 🏆, map 🗺️, thermometer 🌡️, bulb 💡, flame 🔥,
lock 🔒, check ✅, grad 🎓, pin 📍, rocket 🚀, swords ⚔️, party 🎉,
skull 💀, target 🎯, mouse 🖱️, hand 👈, pencil ✍️, plus 12 region
emoji in `story_map.js` (🌋🔥💎🧪👑🏭⚙️🔮☢️🛸🏆) — region emoji need
per-region icon mapping, not 1:1 deletion.
