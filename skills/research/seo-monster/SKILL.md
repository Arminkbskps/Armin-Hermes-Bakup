---
name: seo-monster
description: "Audit SEO, search console, and core web vitals via MCP."
version: 0.1.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [SEO, Google Search Console, GA4, PageSpeed, MCP]
    related_skills: [competitor-news-monitor, grounded-citations]
---

# SEO Monster Skill

Connect and query Google Search Console, Google Analytics 4, PageSpeed Insights, and IndexNow via SEOMonster (local MCP server).

## When to Use

- User asks to inspect Google Search Console or GA4 metrics without opening dashboards.
- Identifying low-hanging keyword opportunities (rankings 8–20 with high search impressions).
- Running Core Web Vitals (LCP, FID/INP, CLS) or PageSpeed audits before publishing.
- Submitting URLs to Google Indexing API or IndexNow (Bing, Yandex, Seznam).
- Evaluating before/after SEO performance following content or technical site updates.
- Don't use for: General non-search web scraping or keyword translation (use `persian-writing` or `agent-reach`).

## Prerequisites

- Python >= 3.10 and `uv` installed (`uvx seo-monster` is recommended).
- Credentials / API Keys as required by target providers:
  - Search Console / GA4: Google service account or OAuth client credentials.
  - PageSpeed Insights: `PAGESPEED_API_KEY` (or runs anonymously with lower rate limit).
  - Cloudflare / IndexNow: API token or site verification key.

## How to Configure MCP in Hermes

To register SEOMonster as a local MCP server in Hermes config (`~/.hermes/config.yaml`):

```yaml
mcp_servers:
  seomonster:
    command: "uvx"
    args: ["seo-monster"]
    env:
      GOOGLE_APPLICATION_CREDENTIALS: "/path/to/credentials.json"
      PAGESPEED_API_KEY: "optional_api_key"
```

## Quick Reference & Commands

Run standalone CLI commands via `terminal`:

```bash
# Verify SEOMonster CLI presence and tools
uvx seo-monster --help

# Run one-off audit or diagnostic
uvx seo-monster audit https://example.com
```

## Procedure

1. **Identify Target Goal:** Clarify whether the audit is technical (PageSpeed, structured data), demand-driven (Search Console near-ranking topics), or indexation.
2. **Credential Check:** Confirm credentials exist locally before firing Search Console queries.
3. **Query & Analyze:**
   - For content ideas: Look for queries with impressions > 500 and position between 8 and 20.
   - For performance: Run mobile and desktop audits; focus on LCP and CLS bottlenecks.
4. **Form Actionable Recommendations:** Pair findings with concrete code or copy changes rather than raw data dumps.

## Pitfalls

- **Search Console Data Latency:** Search Console data is 24–48 hours behind real-time; never confuse recent changes with immediate Search Console updates.
- **Quota Limits:** Batch queries when inspecting multiple URLs to avoid rate limits on PageSpeed API.
- **Proxy/VPN:** On hosts in Iran, Google APIs need direct connectivity or appropriate endpoint configuration.

## Verification

- Command `uvx seo-monster --version` exits with code 0.
- MCP server responds to tools list query with available SEO analysis tools.
