---
name: search-engine-scraping
description: "Use when scraping search engines. Decodes Bing/Yahoo URLs."
version: 1.0.0
author: Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Scraping, Search Engines, Bing, Yahoo, Redirects, Decoding, Base64]
    related_skills: [blocked-page-recovery]
---

# Search Engine Scraping & URL Decoding

## When to Use
Use when you need to fetch search engine results (Google, Bing, Yahoo, DuckDuckGo) programmatically using standard HTTP libraries or curl, especially when encountering bot challenges, tracking redirect URLs, or geo-localized results.

## 1. Decoding Bing Redirect URLs (`/ck/a?u=...`)

Bing search results route outbound links through a tracking URL (e.g., `https://www.bing.com/ck/a?!&&p=...&u=a1<BASE64_URL>`). You can extract the target URL programmatically:

### The `u` Parameter Format
* The tracking parameter `u` starts with a two-character prefix (usually `a1`).
* The remaining characters are base64url encoded.

### Python Decoding Snippet

```python
import base64
import re
import urllib.parse

def decode_bing_redirect(url):
    m = re.search(r'[?&]u=([^&"]+)', url)
    if not m:
        return None
    
    u_val = m.group(1)
    if len(u_val) > 2 and u_val.startswith('a1'):
        u_val = u_val[2:]
        
    # Replace base64url characters to standard base64
    u_val = u_val.replace('-', '+').replace('_', '/')
    
    # Restore base64 padding
    missing_padding = len(u_val) % 4
    if missing_padding:
        u_val += '=' * (4 - missing_padding)
        
    try:
        decoded = base64.b64decode(u_val).decode('utf-8', errors='ignore')
        return decoded
    except Exception:
        return None
```

## 2. Parsing Yahoo Search Results (`RU=`)

Yahoo search result links often wrap the target URL in the `RU` query parameter.
* Example: `https://r.search.yahoo.com/.../RU=https%3a%2f%2fexample.com/RK=2/...`
* Extract the value of the `RU` parameter and pass it to `urllib.parse.unquote()`.

## 3. Bypassing Search Engine Blocks

* **DuckDuckGo**: High bot-detection rate on standard automated script headers. Often returns a minimal HTML page containing a CAPTCHA challenge (`anomaly.js?sv=html&cc=botnet...`).
* **Yahoo / AOL**: More lenient with scraping, but subject to intermittent 500 errors.
* **Bing**: Reliable fallback that rarely serves CAPTCHAs to basic scrapers, but returns relative or tracker URLs.

## 4. Handling Geo-Targeted / Localized Results

When searching via a SOCKS5/HTTP proxy, search engines automatically localize results based on the proxy's IP (e.g. returning German pages for a German proxy IP).
* **Fix**: Force localization query parameters (e.g., `&setlang=en` or `&cc=US` in the search URL) or wrap query terms in double quotes (`"free virtual card"`) to restrict results to exact matches.
