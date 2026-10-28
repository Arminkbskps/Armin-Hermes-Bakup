# AI agents with web/social-media content access — vetted 2026-09

Session context: user (Armin) asked for GitHub projects that give AI agents access to YouTube videos, Instagram, X, LinkedIn, and web content generally. All repos below were verified live (opened each repo page in the in-app preview and read the rendered README). Star counts are approximate/from prior knowledge — recheck on the repo page when precision matters.

## The shortlist

| Project | What it is | Access model | License |
|---|---|---|---|
| [browser-use/browser-use](https://github.com/browser-use/browser-use) | Python lib + CLI: an AI agent controls a real browser like a human (open pages, click, type, fill forms). Tagline: "Make websites accessible for AI agents." | OSS core, optional paid cloud (stealth, proxies, captcha solving) | MIT |
| [apify/apify-mcp-server](https://github.com/apify/apify-mcp-server) | MCP server (hosted at mcp.apify.com) exposing thousands of Apify Store scrapers/actors for social media, search engines, e-commerce — YouTube, Instagram, X, LinkedIn, maps | Apify platform (paid; token/OAuth) | MIT |
| [microsoft/playwright-mcp](https://github.com/microsoft/playwright-mcp) | Official Playwright MCP server: LLM drives a browser via structured accessibility snapshots (no vision model needed). Also has a CLI+SKILLS mode for coding agents | OSS | MIT |
| [unclecode/crawl4ai](https://github.com/unclecode/crawl4ai) | Open-source LLM-friendly crawler/scraper: turns pages into clean Markdown for RAG, agents, pipelines. 50k+ stars, very active | OSS (self-host Docker API or Python lib) | Apache-2.0 (with fair-use clause) |
| [firecrawl/firecrawl](https://github.com/firecrawl/firecrawl) | "Web context API": search, scrape, crawl, interact at scale; outputs clean Markdown/structured JSON; pre-extract actions (click/scroll/type); PDF/DOCX parsing | OSS (AGPL-3.0) + hosted service | AGPL-3.0 |
| [jdepoix/youtube-transcript-api](https://github.com/jdepoix/youtube-transcript-api) | Python: transcripts/subtitles for any YouTube video incl. auto-generated + translation, no API key, no headless browser; CLI included | OSS | MIT |

## Recommendation logic

- Agent must **browse and interact like a human** (watch feeds, click through YouTube/IG/X) → **browser-use**
- MCP client (Claude, Cursor, Hermes) needs **structured social-media data** → **apify-mcp-server** (paid, easiest) or **playwright-mcp** (free, generic browsing)
- Just need **page content as Markdown** for an LLM → **crawl4ai** (self-host) or **firecrawl** (hosted, scale, anti-bot handled)
- Only **YouTube transcripts** → **youtube-transcript-api**

## Integration notes (browser-use)

- Install: `pip install browser-use` / `uv add browser-use` (Python ≥ 3.11)
- Its README ships a copy-paste setup prompt for coding agents (installs, runs `browser-use skill install`, connects to the user's browser)
- LLM keys via `.env`: `BROWSER_USE_API_KEY` or bring-your-own (`GOOGLE_API_KEY`, `ANTHROPIC_API_KEY`, …)