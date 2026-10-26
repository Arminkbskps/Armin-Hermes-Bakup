# VibeFarsi Catalog — لیست کامل اسلاگ‌ها

منبع به‌روز همیشه ریپو است: `vibafarsiui/lib/registry/<category>.ts`.
این فایل فقط برای پیدا کردن سریع اسم درست است؛ قبل از نصب، رکورد همان آیتم
(`usage، props، deps، registryDeps، css`) و سورس فایلش را بخوان.

## فرم (→ `@/components/ui/<slug>`)

button، input، textarea، select، combobox، combobox-async، otp-field، number-field،
checkbox-group (فایل checkbox)، radio-group، switch، slider، rating، file-upload،
calendar (شمسی، به jalali نیاز دارد)، date-picker، date-range-picker، time-picker،
password-input، iban-input، phone-input، national-id-input، card-number-input،
plate-input، amount-input (به number-to-words نیاز دارد)، search-input، tags-input،
multi-select، toggle، segmented-control، form (هوک useForm)، prompt-input، notification-inbox.

## نمایش (→ `@/components/ui/<slug>`)

badge، avatar، table، data-table، chart، stat، price (تومان)، timeline، accordion،
kbd، card، carousel، separator، collapsible، empty-state.

## اوورلی/ناوبری/فیدبک (→ `@/components/ui/<slug>`)

command، dialog، alert-dialog، dropdown-menu، context-menu، tooltip، sheet،
hover-card، popover، tabs، pagination، breadcrumb، stepper، sidebar، toast،
alert، progress، skeleton، spinner.

## انیمیشن (→ `@/components/animations/<slug>`، بدون وابستگی اضافه مگر گفته شده)

text-shimmer، typewriter، counter، blur-text، animated-tabs، border-beam،
shine-button (به button)، dock، animated-list، orbit، tilt-card، loading-dots،
marquee، reveal، word-rotate، text-scramble، odometer، ripple-button (به button)،
magnetic-button (به button)، progress-ring، success-check، meteors، spotlight-card،
grid-reveal، text-reveal، highlight-text، gradient-text، flip-card، animated-beam،
confetti، swipe-to-confirm، terminal، card-stack، morph-button، compare-slider،
scratch-card، sparkles، scroll-progress، pulse-button (به button).

## پس‌زمینه (→ `@/components/backgrounds/<slug>`؛ shaderها WebGL با `speed/opacity`)

grid، dots، girih (گره ایرانی)، hatch، aurora، spotlight، grain، retro-grid، mesh،
flicker، rings، gradient-mesh، conic-spin، light-leak، stars، sonar، dot-wave،
aurora-ribbons، gradient-grain، moving-stripes، shader (primitive)، silk، fog،
nebula، contour، voronoi، warp-grid، godrays، water-ripple، dither، halftone،
waves، plasma، truchet، hex-grid، marble، metaballs، kaleidoscope، cursor-trail،
particles، moire، scanlines، iso-cubes، liquid-gradient، paper.

## قالب صفحه (→ `@/components/templates/<slug>` — صفحه‌ی کامل، registryDeps خودش کشیده می‌شود)

shop-dashboard، auth، startup-landing، pricing، ai-chat، invoice، blog، settings،
checkout، store، onboarding، admin-orders، booking، wallet، error-pages، email،
saas-landing، finance-dashboard، food-delivery، kanban، course، receipt،
travel-search، coming-soon.

## بلاک (→ `@/components/blocks/<slug>`)

hero، features + ۶ تای دیگر (در blocks.ts ببین).

## تم (→ توکن‌های CSS در globals.css)

graphite (پیش‌فرض، تیره)، turquoise، saffron، pomegranate، lapis، paper (روشن).

## lib (→ `@/lib/<slug>`)

utils (فا/تومان/cn)، persian (موبایل/شبا/کدملی/کارت/پلاک)، jalali (شمسی)،
number-to-words (مبلغ به حروف)، float (پورتال شناور).

## اسکیل‌های رسمی (→ `registry/skills/` — قوانین نگارشی، نه کد)

persian-conversational (خودمونی)، persian-formal (اداری)، persian-ui-copy،
persian-rtl-ui (قوانین RTL)، jalali-calendar، iran-validation، persian-seo،
agents-md-persian، persian-typography، persian-writing + راهنماهای kavenegar-otp،
zarinpal-payment، parspack-s3-upload.
