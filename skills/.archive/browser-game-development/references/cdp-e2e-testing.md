# E2E Testing Browser Games over Chrome DevTools Protocol (Windows)

Validated workflow for driving a local web game headlessly and asserting real
gameplay (clicks, score, lives, modals, unlocks) without any test framework.
Everything below was exercised end-to-end on Windows 11 + git-bash + Node 22.

## Architecture

1. **Static server**: `python -m http.server`-style script bound to the project
   folder (e.g. port 8888). Run via `terminal(background=true)`.
2. **Headless Chrome** with its own profile and a debug port:
   ```
   "/c/Program Files/Google/Chrome/Application/chrome.exe" --headless=new \
     --remote-debugging-port=9333 --user-data-dir="$LOCALAPPDATA/Temp/pp-test-profile" \
     --no-first-run --disable-gpu about:blank
   ```
   Also run in background. GCM/PHONE_REGISTRATION_ERROR lines in its output are noise — ignore them.
3. **Node driver script** (`test_*.mjs`) using `npm install ws` plus plain `http`
   against `127.0.0.1:9333`. Each script is standalone; keep several focused ones.

## Driver skeleton

- Open tab: newer Chrome requires **PUT** `/json/new?<url-encoded target>`.
- Connect a WebSocket to `target.webSocketDebuggerUrl`; wrap `send(method, params)`
  with an incrementing id → pending-promise map.
- Enable `Page`, `Runtime`, `Network` domains. Set
  `Network.setCacheDisabled {cacheDisabled:true}` before navigating.
- Evaluate JS via `Runtime.evaluate {expression, returnByValue:true, awaitPromise:true}`;
  throw if `exceptionDetails` present.
- For async page snippets pass an IIFE returning a Promise and await it from Node.

## Critical pitfalls

- **The user's own Chrome debug port lies.** A LISTENING socket on 9222 can still
  return HTTP 404 for `/json/version` and `/json/list` (Chrome rejects the Host
  header / handshake on user-profile ports). Don't fight it — spin up your own
  headless instance on a fresh port instead.
- **Service worker serves stale files to your tests.** If the app registers a SW,
  tests will silently load the OLD cached app even after you fix files on disk
  (symptom: assertions fail with old z-indexes / old data even though grep shows
  new content on disk). Fix in-test before navigation:
  ```js
  navigator.serviceWorker.getRegistrations()
    .then(rs => Promise.all(rs.map(r => r.unregister()))).then(() => 'ok')
  ```
  then navigate with cache disabled. Sanity-check one known-changed value first.
- **Hermes file-write path doubling:** writing `Project/file.js` while cwd is the
  project dir can create `Project/Project/file.js` or truncate the real file to 0
  bytes. After bulk writes, `wc -l` / `node --check` immediately; recover with
  `git checkout HEAD -- <file>`.
- **Watchdog everything.** Wrap the whole script in
  `setTimeout(() => process.exit(2), 110000)` printing the current step label;
  add per-send timeouts so one hung evaluate doesn't stall the suite.
- **Keep steps small & logged:** print `STEP:` before each phase so failures name
  the exact stage. Prefer several small `.mjs` scripts over one giant file.
- **Real-click simulation:** synthetic `element.click()` bypasses hit-testing. To
  verify what a USER's click lands on (z-order bugs!), dispatch the full sequence
  (`pointerdown,mousedown,pointerup,mouseup,click`) on
  `document.elementFromPoint(cx, cy)` using the target's rect center.

## Reusable assertion patterns

```js
// Modal visibility
!document.getElementById('x-modal').classList.contains('hidden')

// Z-order actually effective (computed, not just class)
parseInt(getComputedStyle(a).zIndex) > parseInt(getComputedStyle(b).zIndex)

// Hearts rendered vs state
(livesEl.textContent.match(/❤️/g)||[]).length === lives

// Animation class re-trigger
el.classList.remove('anim'); void el.offsetWidth; el.classList.add('anim');

// Play-to-win loop (correct answers only)
let guard = 0;
while (!overModal.offsetParent && guard++ < N) {
  const cell = document.querySelector(`.puzzle-target[data-atomic="${currentElement.num}"]:not(.filled)`);
  if (!cell) break;
  cell.click();
  await new Promise(r => setTimeout(r, 350));
}
```

Always leave a `guard` counter on game loops so a logic bug can't hang the test.

## Screenshots without vision tooling

`Page.captureScreenshot {format:'png'}` → write Buffer to disk. Even when image
analysis is unavailable, screenshots document UI states for the user. Combine
with `Emulation.setDeviceMetricsOverride` for a consistent viewport size.

## Deploy verification

After `git push`, check GitHub Pages build status via
`GET /repos/<owner>/<repo>/pages/builds/latest` (Bearer PAT) → wait for
`status: built` with the matching commit sha. Then fetch live assets and `grep`
for a string only present in the NEW code. Note: curl may time out mid-download
of large JS files (exit 56) even though the served content is correct — use
`--max-time`, `-o file`, then grep the downloaded file rather than piping curl
straight into grep.
