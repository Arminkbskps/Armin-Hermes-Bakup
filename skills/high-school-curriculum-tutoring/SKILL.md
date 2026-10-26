---
name: high-school-curriculum-tutoring
description: "Interactive tutoring for Iranian high-school textbooks."
version: 1.0.0
author: Armin, Hermes Agent
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [tutoring, high-school, arabic, farsi, exam-prep, education, iran]
    related_skills: [stem-solver-verified, exam-pdf-typesetter, persian-writing]
---

# High-School Curriculum Tutoring

Interactive study, sentence-by-sentence translation, and grammatical drilling for Iranian secondary school textbooks (عربی، ادبیات فارسی، دین و زندگی و زبان).

## When to Use

- Student wants to study, translate, or drill high-school textbooks (کتاب‌های درسی پایه دهم، یازدهم، دوازدهم).
- Interactive translation drills (ترجمه کلمه به کلمه یا عبارت به عبارت) with morphological and grammatical challenges.
- Verifying textbook exercises (درک مطلب، صحیح/غلط، جای خالی، تست‌های قواعد و ترجمه).

## Core Tutoring Protocol

### 1. Sequential Progression Fidelity
- **Strict Page-by-Page Sequence:** Advance through the textbook in natural order. Never jump over intervening sections (such as `اِخْتَبِرْ نَفْسَكَ`, `اَلْحِوار` dialogues, vocabulary tables, or footnotes) straight to the main exercises unless explicitly directed by the student.
- **Maintain Progress Markers:** Clearly reference the current textbook page number and PDF page index when transitioning sections.

### 2. Rigorous Translation Scrutiny
When the student provides a translation, inspect every word for academic and exam-level precision. Never let subtle inaccuracies pass:
- **Bound Pronouns (ضمایر متصل):** Flag phantom pronouns. E.g., «أَرْبَعينَ صَباحاً» has no possessive pronoun and must be rendered as «چهل بامداد / چهل روز», never «۴۰ صبحش».
- **Kasre-ye Ezafe (کسره اضافه):** Enforce correct genitive connections in Persian transcription (e.g., «غذای یک نفر» not «غذا یک نفر»).
- **Conditional & Aspectual Shifts:** Recognize tense adaptations in conditional sentences (e.g., past verb in the apodosis of «مَنْ» translated to present: «مَنْ أَخْلَصَ... ظَهَرَتْ» -> «هر کس خالص کند... آشکار می‌شود»).
- **Nominal Sentences (جملات اسمیه):** Distinguish between copular «است» and possessive verbs (e.g., «اَلْعِبادَةُ عَشَرَةُ أَجْزاءٍ» is literally «عبادت، ده بخش است», not «عبادت ده بخش دارد»).
- **Idiomatic Accuracy:** Translate «جِدّاً» as «بسیار / خیلی» (not «واقعاً»), and convert Arabic past actions with current relevance appropriately («جِئْتُ» -> «آمده‌ام»).

### 3. Systematic Morphology & Verb Quizzing
After each paragraph or section, challenge the student on all extracted verbs:
- **Tense / Mood:** ماضی، مضارع اخباری/التزامی، امر، نهی (لا + مضارع مجزوم)، نفی (لا/ما + مضارع مرفوع).
  - *Negation vs Negative Imperative:* «لا تَفَرَّقوا» is نهی (imperative: پراکنده نشوید); «لا يَكْفي» is نفی مضارع (indicative: کافی نیست).
- **Person / Form (صیغه):** Demand exact standard terminology (للغائب، للغائبة، للغائبَينِ، للغائبينَ، للمخاطب، للمخاطبة، للمتکلم...).
- **Target Classical Traps:**
  - *Past Tense Suffixes:*
    - `ـتُ` (ضمه): متکلم وحده / ۱st person singular (جِئْتُ = آمدم / آمده‌ام; ذَهَبْتُ = رفتم).
    - `ـتَ` (فتحه): للمخاطب / ۲nd person singular masc (جِئْتَ = آمدی; ذَهَبْتَ = رفتی).
    - `ـتِ` (کسره): للمخاطبة / ۲nd person singular fem (جِئْتِ = آمدی).
    - `ـتْ` (ساکن): للغائبة / ۳rd person singular fem (ذَهَبَتْ، ظَهَرَتْ).
    - `ـنا`: متکلم مع‌الغیر / ۱st person plural (جِئْنا = آمدیم; أَرْسَلْنا = فرستادیم).
  - *Weak Roots (معتل ناقص):* Terminal «ی» in words like «يَكْفي» (root ک-ف-ی) is a root radical, not a plural pronoun (مفرد مذکر غائب, not جمع).
  - *Overt Subject Agreement (فاعل ظاهر):* In Arabic, when the subject is an overt noun, the preceding verb remains singular even if the subject is plural or collective (e.g., «يَتَراحَمُ الْخَلْقُ» -> verb is مفرد مذکر غائب).
  - *Non-Human Broken Plurals (جمع مکسر غیرانسان):* Treated grammatically as singular feminine (e.g., «ظَهَرَتْ يَنابيعُ» -> verb is مفرد مؤنث غائب).

### 4. Exercise & True/False Drills
- Check statements against the primary text without paraphrasing distortion.
- Pair every answer confirmation with a quick, punchy grammar diagnostic:
  - Distinguish between negative imperative (نهی: «لا تَفَرَّقوا») and negative indicative (نفی: «لا يَكْفي»).
  - Contrast verbal nouns (مصدر: «اِسْتِغْفار»، «حَفْر») with finite verbs.

### 5. Arabic Numbers & Ordinal Reference Rules
- **Counted Noun Agreement (المعدود):**
  - *1 & 2:* Follow noun as descriptive adjective (طالِبٌ واحِدٌ، طالِبانِ اثْنانِ).
  - *3 to 10:* معدود is plural and genitive (جمع مجرور): «سَبْعَةُ أَبْوابٍ»، «سِتَّةِ أَيّامٍ».
  - *11 to 99:* معدود is singular and accusative with tanween fath (مفرد منصوب): «ثَلاثينَ لَيْلَةً»، «سِتّينَ مِسْكيناً»، «أَحَدَ عَشَرَ كَوْكَباً».
- **Ordinal Numbers (الأعداد الترتيبية):**
  - Days of the week: السَّبْت (الأوَّل)، الأَحَد (الثّانی)، الإِثْنَيْن (الثّالث)، الثُّلاثاء (الرّابع)، الأَرْبِعاء (الخامس)، الخَميس (السّادس)، الجُمُعَة (السّابع).
  - Seasons of the year: الرَّبيع (الأوَّل)، الصَّيْف (الثّانی)، الخَريف (الثّالث)، الشِّتاء (الرّابع).
- **Arithmetic Expressions:**
  - `+` = زائد / ` - ` = ناقص / `×` = ضربٌ في (أو في) / `÷` = تقسيمٌ على / `=` = يُساوي.

## Tone & Delivery Rules
- Keep the interaction warm, energetic, and peer-like (صمیمی، دقیق، رفیقانه).
- Match the student's pace; praise correct answers immediately and clearly explain traps behind wrong ones.
