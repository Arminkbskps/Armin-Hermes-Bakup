# g4f No-Auth Fallback (gpt-4o in bots)

Problem: `g4f.ChatCompletion.create(model="gpt-4o-mini", messages=[...])` with no
`provider` picks a default provider that needs auth (`OpenaiChat`) and always dies with
`g4f.errors.NoValidHarFileError: No .har file found`. As a fallback this never works —
verified in a production Telegram bot log (every Google outage cascaded into this).

Fix: pass an explicit no-auth provider, try several, request `gpt-4o`.

```python
import contextlib, inspect
import g4f
import g4f.Provider as GProviders

PREFERRED = ["PollinationsAI", "Blackbox", "DuckDuckGo", "DeepInfraChat",
             "GeminiPro", "FreeGpt", "Liaobots", "ChatGot", "AItianhu"]

def candidates(limit=5):
    found = []
    for name in PREFERRED:
        p = getattr(GProviders, name, None)
        if p is not None and p not in found:
            found.append(p)
    for attr in dir(GProviders):  # auto-discover the rest
        if len(found) >= 25:
            break
        with contextlib.suppress(Exception):
            p = getattr(GProviders, attr)
            if not (inspect.isclass(p) or hasattr(p, "create_async_generator")):
                continue
            if p in found or getattr(p, "needs_auth", False):
                continue
            if getattr(p, "working", None) is False:
                continue
            found.append(p)
    return found[:limit]

def call(prompt, model="gpt-4o", timeout=300):
    last = "no providers"
    for prov in candidates():
        try:
            kw = {"model": model, "messages": [{"role": "user", "content": prompt}], "provider": prov}
            try:  # drop kwargs this g4f version does not accept
                params = inspect.signature(g4f.ChatCompletion.create).parameters
                kw = {k: v for k, v in kw.items() if k in params}
            except Exception:
                pass
            out = str(g4f.ChatCompletion.create(**kw)).strip()
            if out and "No .har file" not in out and "NoValidHar" not in out:
                return out, getattr(prov, "__name__", str(prov))
            last = f"{getattr(prov, '__name__', prov)} returned no usable text"
        except Exception as e:
            last = f"{getattr(prov, '__name__', prov)} failed: {e}"[:200]
    raise RuntimeError(last)
```

Notes:
- Filter is `needs_auth == True` → skip. Never include `OpenaiChat` family.
- Validate output text (empty / `.har` mention = try next provider).
- Keep sync `g4f` call in a thread (`asyncio.to_thread`) with a timeout; it blocks.
- `G4F_MAX_PROVIDERS_TO_TRY = 5`, timeout ~300s worked; lower to 2–3 if it stalls a scan loop.
