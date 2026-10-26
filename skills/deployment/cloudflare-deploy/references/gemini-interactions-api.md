# Gemini API via `google-genai` SDK — Interactions API (validated 2026-09)

AI Studio moved fast: new SDK surface, new model IDs, new key format — all in
weeks. Do NOT hardcode any of these; verify empirically every time.

## Working call path (CI-tested, end-to-end success)

```python
from google import genai
client = genai.Client(api_key=GOOGLE_API_KEY)
interaction = client.interactions.create(model=model, input=prompt)
text = (interaction.output_text or "").strip()
```

- `requirements.txt` needs `google-genai` (in addition to `g4f`/`requests`/`beautifulsoup4`).
- Keep a REST fallback for environments without the SDK:
  `POST https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={key}`
  with `{"contents":[{"parts":[{"text": prompt}]}], "generationConfig":{...}}`,
  parsed at `data["candidates"][0]["content"]["parts"][0]["text"]`.

## Model IDs move fast — keep them in settings, never in code

Observed progression within weeks: `gemini-1.5-flash` → `gemini-2.5-flash` →
`gemini-3.8-flash` (with older ones shut down server-side, returning 403/404).
Read the model from D1/settings/panel (`google_model` key); the code must only
do `SETTINGS.get("google_model", <last-known-good>)`.

## Key format changed — never validate keys by prefix

AI Studio keys historically started with `AIza` (39 chars). Observed valid,
working keys starting with `AQ.` (53 chars). A key that "looks wrong" can be
fully functional, and `models.list` / old REST endpoints can 403 while the SDK
path with the same key succeeds. Rule: **never declare a user's key invalid by
shape — run one real call on the exact path CI uses and read the result.**

## Correction protocol (user pasted a working snippet, agent disagreed)

When the user contradicts your provider assumption with a concrete snippet,
test the snippet first, argue later. In this session the agent insisted the key
was invalid (prefix check) while the user's `interactions.create` snippet was
correct — the fix was adopting their snippet verbatim plus `google-genai` in
requirements. The wasted round-trips were entirely avoidable.
