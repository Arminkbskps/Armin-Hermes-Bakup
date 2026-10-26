---
name: persian-colloquial-prompts
description: Use when an LLM must write colloquial Persian product copy.
version: 0.1.0
author: Hermes Agent
license: MIT
metadata:
  hermes:
    tags: [Persian, colloquial, prompting, product-copy]
    related_skills: [persian-writing]
---

# Persian Colloquial Prompts

## When to Use

- Prompting any LLM (Gemini, GPT, g4f) to write short colloquial Persian
  (خودمونی Light) summaries, card descriptions, highlights, or tags for use
  inside a product UI — not articles, not social posts.
- Model output keeps drifting back to کتابی Persian despite a "friendly tone"
  instruction.

Prompting pattern for LLM-generated short colloquial Persian summaries used
inside a product (site summaries, card descriptions, highlights). A plain
"write in a friendly tone" instruction fails: the model drifts back to کتابی
Persian (است، می‌شود، فعالیت دارد).

## Recipe

1. **Persona, not role title.** Bad: «شما یک تحلیلگر ارشد هستید» (invites
   article register). Good: «تو رفیق صمیمی کاربری هستی که لینک‌های جالب رو
   معرفی می‌کنی — مثل یه دوست که خودش سایت رو باز کرده و ذوق کرده، جواب
   بده. نه مثل ربات، نه مثل مقاله.»
2. **Ban list must include است.** Banning only می‌باشد/می‌شود is NOT enough —
   the model keeps the single loudest tell. Frame as "if any of these words
   is in the summary, the summary is broken": است، می‌شود، می‌باشد، می‌گردد،
   فعالیت دارد، محسوب می‌شود، به شمار می‌رود، ارائه می‌دهد، بهره‌مند شوید،
   در دنیای امروز، در عصر دیجیتال، نه تنها … بلکه، لازم به ذکر است، از
   اهمیت ویژه، نقش بسزا.
3. **Bad-vs-good few-shot pair on the SAME site.** One contrasting pair beats
   a paragraph of tone adjectives. Bad (dry, never write like this):
   «وایب‌فارسی مجموعه‌ای رایگان از کامپوننت‌های راست‌چین برای React و Next.js
   است...» Good (colloquial, write like this): «با وایب‌فارسی می‌تونید
   کامپوننت‌های راست‌چین آماده برای React بردارید؛ فونت و تقویم شمسی هم
   همراهشه، دیگه درگیر چپ‌چین شدن متن نمی‌شید.»
4. **Mandatory self-check line.** «خلاصه‌ت رو دوباره بخون. اگه حتی یه «است»
   توش هست، بازنویسی‌ش کن. اگه شبیه مقاله‌ست نه حرف رفیق، از نو بنویس.»
5. **Settings.** temperature 0.95 (0.7 gives flat uniform sentences).
   Highlights must ALSO be colloquial («کامپوننت آماده راست‌چین داره» — not
   «ارائه کامپوننت‌های تخصصی»). Ask the MODEL to write short (۱–۲ جمله،
   ۱۲۰–۱۸۰ کاراکتر، جمله کامل) — never truncate server-side mid-sentence.
6. **Expect tone variance.** Same prompt + force-regenerate can return a split
   batch (some colloquial, some formal). Mitigation: re-run with force and
   spot-check output with a mechanical banned-word grep
   (است/می‌شود/ارائه می‌دهد) as an accept/reject gate.

## Pitfalls

- Colloquial verbs must stay consistent (میشه/می‌تونید/داره) — never mix
  میشه and می‌شود in one piece.
- Numbers/dates in Persian digits, نیم‌فاصله respected.
- One music particle per summary max (دیگه/راستش/ببین/خب) — not every sentence.
