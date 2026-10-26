# Cloudflare Worker API Pitfalls: PUT User-Agent + Stale GET Cache (validated 2026-09)

Two class-level lessons from a Worker + D1 backend fronted by Cloudflare.

## 1. PUT/POST without `User-Agent` gets 403 while GET with the same token returns 200

**Symptom:** CI push step fails on every `PUT /api/sites/:id` with `HTTP 403 Forbidden`,
but `GET /api/data` with the identical `Authorization: Bearer` token returns 200.
Local reproduction confirmed: same token, same endpoint — PUT without `User-Agent`
→ 403; PUT with `User-Agent: site-summarizer-ci` → 200 for all records.

**Root cause:** Cloudflare WAF / Bot Fight Mode treats headerless non-GET requests
(`Python-urllib/...` default or no UA at all) as bots and blocks them, while GETs pass.

**Rule:** every `urllib`/`fetch` call to a Worker API must set an explicit UA —
`GET` and `PUT`/`POST` alike. Never rely on the runtime default:
```python
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + ADMIN_TOKEN,
    "User-Agent": "site-summarizer-ci",  # NOT optional — WAF blocks UA-less PUTs with 403
}
```
The same applies to `curl` from CI (`-H "User-Agent: ..."`). When a PUT 403s but GET
200s with the same credential, check the `User-Agent` header before rotating tokens.

## 2. Successful PUT followed by stale GET — add `no-store` + client cache-bust

**Symptom:** `PUT` returns `{"ok":true}` HTTP 200, but the next `GET` returns the old
record. Looks like the write failed; it didn't — the edge served a cached GET.

**Fix (both sides):**
- Worker: `Cache-Control: no-store` + `Pragma: no-cache` on all JSON API responses.
- Client: cache-bust reads (`GET /api/data?_=` + `Date.now()`).

**Rule:** for any Worker-backed admin panel, ship `no-store` from day one; debugging
"lost writes" that were actually stale reads wastes entire sessions.
