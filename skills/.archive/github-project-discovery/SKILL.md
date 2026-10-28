---
name: github-project-discovery
description: Use when finding or vetting GitHub repos, tools, libraries.
category: research
version: 1.1.0
author: hermes
license: MIT
metadata:
  hermes:
    tags: [github, research, repos, mcp]
    related_skills: [agent-reach]
---

# GitHub Project Discovery

## When to Use

Trigger whenever the user asks to find, search, or vet a GitHub project, library, MCP server, or open-source tool ("پروژه‌ای تو گیت‌هاب پیدا کن که...", "find a repo that does X"). Also for deep-read verdicts: "این ریپو رو کامل بخون ببین خوبه یا خودمون بسازیمش", "can I self-host X on my host", "build vs buy". Check the pre-vetted shortlist in `references/` before re-searching a known domain.

**Class of task:** "پروژه‌ای تو گیت‌هاب پیدا کن که..." / "find me a repo/tool/library that does X" — including MCP servers and libraries. The deliverable is **verified** repos — tagline, tradeoffs, recommendation — never a list of unverified guesses.

## Validated workflow

1. **Draft candidates from your own knowledge first.** Ecosystem staples for a domain rarely change; arrive with 3–6 names before touching the network.
2. **Verify each candidate by opening its repo page:** `open_preview("https://github.com/owner/repo")` then `read_preview()`. From the rendered text confirm: what it does (the repo's own tagline is in the page `<title>` and About), license, recent activity (commits/releases), popularity ("Used by"/contributors), language. Stars/lang/stats sit at the README tail.
3. **When the verdict is "is it stable / can I run it on my host / should we build our own" — run the repo's own gates; page text cannot answer those.**
   - Clone shallow for reading, unshallow for history health: `git clone --depth 1 https://github.com/<owner>/<repo>.git "$LOCALAPPDATA/Temp/<repo>-review"` then `git fetch --unshallow` and `git log --format='%ad' --date=format:'%Y-%m' | sort | uniq -c` → commits-per-month trend (a repo born 5 months ago with a fresh burst of commits is *active*, not *established* — say which).
   - Run install → test → typecheck → lint → build with the project's own scripts (npm: `env -u http_proxy -u https_proxy npm ci` / `npm test` / `npm run typecheck` / `npm run lint` / `npm run build`). Report real numbers ("284 passed / 12 skipped, build exit 0"), never a vibe.
   - **Pitfalls:** (a) codegen repos fail at import until you run their generator — Prisma needs `npx prisma generate` first, and "failed test files" often disappear after it; (b) DB-backed tests SKIP without `TEST_DATABASE_URL` — a skip is environmental, not a failure; (c) `npm test 2>&1 | tail` reports **tail's** exit code (0) even when tests failed — read the `Test Files X failed` summary line or use `${PIPESTATUS[0]}`.
   - Read `package.json`, the Dockerfile, and the schema's DB provider for the hard runtime requirements (which language/process model/databases/daemons the host must supply) — that is what answers "will it run on X" concretely.
4. **Present a ranked list:** ⭐ scale, one-line "what it does" quoting the tagline, tradeoffs (OSS vs hosted/paid, browser-driven vs API/scrape, language), and a bottom-line recommendation tied to the user's actual use case. Offer to set the winner up.
5. **Leave the best repo open** in the preview pane so the user can browse it live; `close_preview` the rest (close each by URL).

On this machine the in-app preview is the reliable path to github.com — see tool ladder below.

## GitHub search pitfalls (universal)

- Repository search is effectively **AND** over words: 4–5 specific words ⇒ "0 results". Use 2–3 broad words (`browser use AI agent`) or browse `github.com/topics/<topic>` pages.
- Unauthenticated search hits a **secondary rate limit fast** ("Too many requests"; can last minutes to an hour). Once you have candidates, go direct to repo URLs; never loop searches back-to-back.
- Query shape: `type=repositories&s=stars&o=desc`.

## Extracting results from a search page

`read_preview` returns page text; to list repos from the DOM, match hrefs of shape `/owner/repo` and exclude noise prefixes: topics, search, sponsors, features, collections, trending, orgs, marketplace, settings, notifications, login, signup, about, pricing, security, enterprise, customer-stories, readme, events, site, git, docs, github, advisories, apps, codespaces, copilot, issues, pulls, discussions, explore, assets.

## Tool ladder for github.com on this Windows machine (retest if env changes)

| Attempt | Result |
|---|---|
| `gh search repos` | installed npm `gh` is a different package — crashes with TypeError |
| `curl api.github.com` | SSL failure / exit 35 (proxy blocks CLI HTTPS to GitHub) |
| ✅ `git ls-remote` / `git clone --depth 1` on github.com | works direct (retested 2026-09-02) — best fidelity for reading docs/source |
| ✅ `git fetch --unshallow` on that clone | full history for commit-frequency health stats (2026-09-25) |
| ✅ `open_preview` + `read_preview` on repo URLs | works every time; user watches live |
| ✅ `drive_preview` elements → click → `read_preview` | walks the GitHub UI (Issues/PR tabs, About) when the README lacks the signal (2026-09-25) |
| ⭐ star/fork counts | invisible while signed out in the preview — substitute signals: commits/month, contributors, open vs closed issues, releases |
| `web_extract` on developers.facebook.com | blocked as "private/internal network address" (false positive); `open_preview` renders it fine, following redirects to new canonical doc URLs (2026-09-25) |

(web_extract on github.com → Exa keyless 403; r.jina.ai via curl → empty. Retest the whole ladder before trusting it again if the CLI/network stack changes. 2026-09-02 retest: git transport to github.com works direct; `npm` fails through the proxy env — use `env -u http_proxy -u https_proxy npm ...`. 2026-09-25: when `web_search` keyless backends are down (SSL timeouts / 403), skip search and `open_preview` the known canonical doc URL directly.)

## Pre-vetted shortlist

`references/ai-agent-content-access.md` — vetted 2026-09: projects giving AI agents access to YouTube/Instagram/X/LinkedIn/web content (browser-use, playwright-mcp, apify-mcp-server, crawl4ai, firecrawl, youtube-transcript-api) with recommendation logic.

`references/instagram-comment-to-dm.md` — 2026-09-25 deep-vet of OpenReply (Instagram comment-to-DM): verification results, hard hosting requirements, and the official Meta private-reply policy behind the build-vs-buy and ban-risk verdicts.
