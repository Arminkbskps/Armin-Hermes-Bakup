# g4f Fallback That Actually Works (gpt-4o, no-auth providers)

Default g4f usage (`g4f.ChatCompletion.create(model="gpt-4o-mini")` with no
provider) dies with `NoValidHarFileError: No .har file found` because it lands
on `OpenaiChat`, which needs login. The fix is explicit no-auth provider
discovery.

## Recipe

1. Collect provider classes from `g4f.Provider`, prefer known no-login names
   (`PollinationsAI`, `Blackbox`, `DuckDuckGo`, ...) then auto-discover the rest.
2. Skip any provider with `needs_auth is True`, `working is False`, or without
   `create_async_generator`.
3. Cap attempts: `G4F_MAX_PROVIDERS_TO_TRY = 5`, `G4F_TIMEOUT_SECONDS = 300`,
   model `G4F_MODEL = "gpt-4o"` (user's explicit choice; `gpt-4o-mini` kept
   hitting the broken path).
4. Drop unsupported kwargs via `inspect.signature(create).parameters` before
   calling — providers disagree on accepted args.
5. Skip empty responses and anything containing `No .har file` / `NoValidHar`;
   try the next provider. Log the winner: `g4f fallback OK via <Provider>`.
6. Return provider tag `g4f/<ProviderName>` so stats show which path served.

## Failure modes to surface, not swallow

- `g4f not installed` → tell the user `pip install g4f` (server step).
- `g4f has no usable providers installed` / `all g4f providers failed` →
  enqueue retry, don't fabricate output.

Never substitute a plausible-looking rewrite you didn't actually generate —
report the blocker and queue the retry.
