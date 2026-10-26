# Python Library RAM Consumption Diagnostics

Debugging why a Python bot uses unexpectedly high memory. Key findings from a real session analyzing 5 bots.

## Approximate RAM Footprint per Library

| Library | RAM (estimate) | Why it's heavy |
|---|---|---|
| `requests` + `sqlite3` | ~15 MB | Pure Python HTTP + stdlib; baseline for any bot |
| `aiogram` | ~40 MB | Full async framework: Dispatcher, Router, FSM, aiohttp session |
| `BeautifulSoup` (bs4) | ~15 MB | HTML parser with Unicode support; pulls in `lxml` or `html.parser` |
| `RapidFuzz` | ~10 MB | C-accelerated fuzzy string matching; moderate |
| `g4f` | ~15 MB | Third-party OpenAI-compatible client |
| `numpy` | ~40 MB | Array library; heavy C extensions |
| `matplotlib` | ~80 MB | **The heaviest**. Pulls in `numpy`, `PIL/Pillow`, `tkinter`, font caches |
| `Pillow` | ~15 MB | Image processing; pulled by matplotlib indirectly |

## Total Estimated Footprint

| Bot | Stack | Total RAM |
|---|---|---|
| bot1/bot2 (sync) | requests + sqlite3 | **~15 MB** ✅ |
| bot3 (aiogram) | aiogram | **~40 MB** ⚠️ |
| bot4 (content) | aiogram + bs4 + rapidfuzz | **~60 MB** 🔴 |
| bot5 (gold) | aiogram + matplotlib + numpy + bs4 + g4f + Pillow | **~150 MB** 🛑 |

## Diagnosis Method
Run a minimal import test to see base RAM usage:
```python
import os, psutil
proc = psutil.Process(os.getpid())
before = proc.memory_info().rss
import matplotlib  # or the suspected library
after = proc.memory_info().rss
print(f"RAM delta: {(after - before) / 1024 / 1024:.1f} MB")
```

## Key Insight
`matplotlib` is almost always the wrong choice for bot-generated charts. Even with `matplotlib.use("Agg")` (which disables the GUI backend), the import itself pulls in numpy and Pillow. Alternatives:
- **Plotly HTML charts** — rendered as `<div>` in the browser, no server-side rendering needed
- **Pillow + custom drawing** — lighter if you need a static image
- **ASCII charts** (plotext) — zero overhead for terminal bots
- **Chart.js** (client-side) — send raw data as JSON, render in browser
