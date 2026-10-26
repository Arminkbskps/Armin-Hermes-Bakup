---
name: vibefarsi
description: Install VibeFarsi RTL Persian components in React apps.
version: 0.1.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [Persian, RTL, React, Components]
    related_skills: []
---

# VibeFarsi — کامپوننت‌های فارسی RTL برای React

CLI دستور `vibefarsi` کامپوننت‌ها را از رجیستری `https://vibefarsi.ir/r`
به سبک shadcn (کپی فایل داخل پروژه، نه نصب پکیج) می‌آورد.
سورس واقعی همان سایت است: گیت‌هاب `TronIsHere/vibafarsiui` (پوشه‌ی `registry/`).
کل رجیستری ≈ ۲۰۰ آیتم است: ۶۷ کامپوننت (components)، ۳۹ انیمیشن (animations)،
۴۴ پس‌زمینه (backgrounds، شامل shaderهای WebGL)، ۲۴ قالب صفحه (templates)،
۸ بلاک (blocks)، ۶ تم، ۵ فایل lib، و ۱۳ اسکیل/راهنما (skills) —
پس هرگز اسلاگی را حدس نزن؛ اول در ریپو جست‌وجو کن (بخش «پیدا کردن آیتم»).

## Strategy: TEACH, MIRROR, ADD

1. TEACH — سورس آیتم را از ریپوی محلی `vibafarsiui/registry/` بخوان
   (`read_file`) و API واقعی‌اش (پراپ‌ها، ایمپورت‌ها، CSS لازم) را یاد بگیر.
2. MIRROR — اگر `vibefarsi.ir` در دسترس نبود، میرور لوکال را اجرا کن (بخش Mirror fallback).
3. ADD — با همان CLI رسمی نصب کن: `npx vibefarsi add <slug...>`

هیچ‌وقت کامپوننت را از حفظ ننویس و هیچ‌وقت کل ریپو را لوکال «نصب» نکن —
فقط آیتمِ خواسته‌شده با CLI وارد پروژه‌ی هدف می‌شود.

## پیدا کردن آیتم (قبل از هر کاری)

تعریف‌ها در `vibafarsiui/lib/registry/<category>.ts` است (فیلدهای `slug، name، desc، file، deps، registryDeps، usage، props، css`).
فایل سورس از `file` می‌آید: `registry/ui/<slug>.tsx`، `registry/animations/<slug>.tsx`،
`registry/backgrounds/<slug>.tsx`، `registry/templates/<slug>.tsx`، `registry/blocks/<slug>.tsx`،
`lib/<slug>.ts`، `registry/themes/<slug>.css`، `registry/skills/<slug>/SKILL.md`.

- نام فارسی/انگلیسی/کاربرد را با `search_files` در `vibafarsiui/lib/registry/` پیدا کن
  (مثلاً «تقویم» → calendar/date-picker؛ «شبا» → iban-input؛ «لندینگ» → templates).
- بعد `usage` و `props` همان رکورد + سورس فایل را با `read_file` بخوان.
- `registryDeps` یعنی CLI خودش وابستگی را می‌کشد؛ `deps` یعنی پکیج npm لازم است (معمولاً `lucide-react`).
- فیلد `css` یعنی کی‌فریم/CSS اضافه به `globals.css` می‌رود — خروجی `add` را چک کن که بلوک `/* --- vibefarsi:<slug> --- */` ساخته شده باشد.

## کاتالوگ

لیست کامل ≈ ۲۰۰ اسلاگ در `references/catalog.md` همین اسکیل است — فقط برای پیدا
کردن اسم درست، نه برای خواندن کامل. قبل از نصب، رکورد همان آیتم در
`vibafarsiui/lib/registry/<category>.ts` (`usage، props، deps، registryDeps، css`)
و سورس فایلش را بخوان.

## When to Use

- پروژه‌ی فارسی/RTL با React (Vite یا Next) که فرم، ورودی ایرانی یا انیمیشن فارسی می‌خواهد.
- کاربر اسم کامپوننتی از vibefarsi برد (مثلاً phone-input، tilt-card) یا گفت «مثل vibefarsi».
- Don't use for: پروژه‌ی غیرفارسی، بک‌اند، یا VOID CLUB (HTML خام — کامپوننت ری‌اکت آنجا کاربرد ندارد).

## Prerequisites

- Node >= 18 و پروژه‌ی React با `package.json` (دستورات از طریق `terminal`).
- برای هر تماس شبکه‌ای (npm، curl، git، خود CLI) اول پراکسی مرده‌ی محیط را خنثی کن:
  `export http_proxy="" https_proxy="" HTTP_PROXY="" HTTPS_PROXY="" all_proxy="" ALL_PROXY=""`
  (پراکسی `127.0.0.1:10808` قطع است؛ اتصال مستقیم کار می‌کند.)

## نصب استاندارد (بعد از TEACH)

```bash
npx vibefarsi init --font vazirmatn   # یک‌بار برای هر پروژه
npx vibefarsi add <slug...>           # مثلاً: add calendar date-picker price
npx vibefarsi list [components|animations|backgrounds|templates|themes|lib]
```

`init` چه می‌کند: `lang="fa" dir="rtl"` روی html، فونت Vazirmatn (گوگل‌فونت در CSS)،
توکن‌های تم graphite، فایل‌های `lib/utils.ts` و `lib/jalali.ts`، alias مسیر `@/*`، فایل `vibefarsi.json`.

## ۷ آیتمِ از قبل نصب‌شده در particle-test/demo

tilt-card، highlight-text، text-reveal، reveal، iban-input، phone-input،
password-input — به‌علاوه‌ی `lib/utils.ts`، `lib/persian.ts`، `lib/jalali.ts` و تم
graphite. صفحه‌ی smoke-test: `particle-test/demo/src/vibe-demo.tsx` (بدون تغییر `App.tsx`).
برای آیتم جدید دوباره TEACH → MIRROR → ADD را برو؛ چیزی را از قبل «نصب لوکال» نکن.

## Mirror fallback (وقتی vibefarsi.ir جواب نمی‌دهد)

از این محیط سایت معمولاً تایم‌اوت می‌دهد (`curl` به `/r` و `npm view` با پراکسی). راه جایگزین:

1. کلون سورس (با پراکسی unset): `git clone --depth 1 https://github.com/TronIsHere/vibafarsiui.git`
2. اجرای میرور لوکال: `node vibefarsi-mirror/registry-server.mjs` → `http://127.0.0.1:3891/r`
   (فرمت کاتالوگ و payload دقیقاً مثل `/r` واقعی است: `GET /r` و `GET /r/{collection}/{slug}.json`)
3. دستورات CLI با فلگ رجیستری: `node <cli>/dist/index.js add <slug...> --registry http://127.0.0.1:3891/r --cwd <project> --no-install`
4. توجه: CLI مسیر `components/` و `lib/` را در **ریشه‌ی پروژه** می‌سازد (نه `src/`) مگر `src/app` یا `src/pages` وجود داشته باشد؛ پس alias `@` باید به ریشه مپ شود.

## سیم‌کشی پروژه‌ی Vite بعد از add (چک‌لیست)

- نصب وابستگی‌ها: `lucide-react` (+ `tailwindcss` و `@tailwindcss/vite` اگر نیست).
- پلاگین tailwind در `vite.config.ts` و `@import "tailwindcss";` در CSS.
- ایمپورت فونت گوگل باید **خط اول** فایل CSS باشد (قبل از همه‌ی رول‌ها)، وگرنه بیلد وارنینگ می‌دهد.
- alias در `vite.config.ts` (`resolve.alias: { '@': import.meta.dirname }`) و `paths: { "@/*": ["./*"] }` در tsconfig؛ در TS 6 از `baseUrl` استفاده نکن (deprecated است).
- `index.html`: `<html lang="fa" dir="rtl">`.
- استایل‌های `page/bar/...` خود دمو دست نخورده می‌ماند؛ فقط بلوک‌های `/* --- vibefarsi:* --- */` مال CLI است.

## قوانین RTL (خلاصه)

- فقط کلاس‌های منطقی: `ms/me/ps/pe/start/end/text-start` — هرگز `ml/pl/left/text-left`.
- فاصله با `gap` نه `space-x`؛ بدون `flex-row-reverse` برای «درست کردن» جهت.
- فیلدهای phone/iban/otp/card-number: `dir="ltr"` روی خود کنترل.
- ارقام نمایشی فارسی (`fa`/`faNumber`)، ولی مقادیر فرم، URL و JSON لاتین.
- `letter-spacing: 0` روی متن فارسی؛ فونت Vazirmatn یا IRANSans.

## Pitfalls

- `"use client"` بالای فایل‌های رجیستری در Vite بی‌ضرر است، پاکش نکن (با آپدیت بعدی برمی‌گردد).
- `highlight-text` بدون توکن‌های تم (`--brand`) هایلایت نامرئی می‌شود — اول `init` بزن.
- `text-reveal` بدون کی‌فریم `wipe-in` هیچ انیمیشنی ندارد — خروجی `add` را چک کن که بلوک CSS را اضافه کرده باشد.
- `vibefarsi.json` رجیستری را پین می‌کند؛ اگر میرور خاموش باشد `add` بعدی شکست می‌خورد — میرور را دوباره اجرا کن.

## Verification

- `npx tsc --noEmit -p tsconfig.app.json` → exit 0، بدون خطا.
- `npm run build` → `vite build` موفق.
- صفحه‌ی smoke-test: `particle-test/demo/src/vibe-demo.tsx` هر ۷ کامپوننت را رندر می‌کند (بدون تغییر `App.tsx`).
