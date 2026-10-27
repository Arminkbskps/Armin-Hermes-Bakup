import os, base64, subprocess

OUTPUT_DIR = "/home/daytona/exam_work/geometry_camscanner"
HTML_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Tashrihi_Hendlseh_Dahom.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Tashrihi_Hendlseh_Dahom.pdf")

# Read fonts
font_dir = "/home/daytona/.hermes/skills/persian-writing/assets/fonts"
vazir_reg_b64 = ""
vazir_bold_b64 = ""
vazir_med_b64 = ""
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Regular.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Regular.ttf"), "rb") as f:
        vazir_reg_b64 = base64.b64encode(f.read()).decode("ascii")
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Bold.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Bold.ttf"), "rb") as f:
        vazir_bold_b64 = base64.b64encode(f.read()).decode("ascii")
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Medium.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Medium.ttf"), "rb") as f:
        vazir_med_b64 = base64.b64encode(f.read()).decode("ascii")

# Read SVGs
with open(os.path.join(OUTPUT_DIR, "assets/q8_geometry.svg"), "r", encoding="utf-8") as f:
    q8_svg = f.read()

with open(os.path.join(OUTPUT_DIR, "assets/q10_geometry.svg"), "r", encoding="utf-8") as f:
    q10_svg = f.read()

with open(os.path.join(OUTPUT_DIR, "assets/q11_geometry.svg"), "r", encoding="utf-8") as f:
    q11_svg = f.read()

with open(os.path.join(OUTPUT_DIR, "assets/q2_geometry.svg"), "r", encoding="utf-8") as f:
    q2_svg = f.read()

html = """<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>پاسخ‌نامه تشریحی و راهنمای جامع آزمون هندسه و قضیه تالس — پایه دهم ریاضی</title>
  <style>
    @font-face {
      font-family: 'Vazirmatn';
      src: url('data:font/ttf;base64,__VAZIR_REG__') format('truetype');
      font-weight: 400;
      font-style: normal;
    }
    @font-face {
      font-family: 'Vazirmatn';
      src: url('data:font/ttf;base64,__VAZIR_MED__') format('truetype');
      font-weight: 500;
      font-style: normal;
    }
    @font-face {
      font-family: 'Vazirmatn';
      src: url('data:font/ttf;base64,__VAZIR_BOLD__') format('truetype');
      font-weight: 700;
      font-style: normal;
    }

    @page {
      size: A4 portrait;
      margin: 10mm 12mm 12mm 12mm;
      @bottom-right {
        content: "صفحه " counter(page);
        font-family: 'Vazirmatn', sans-serif;
        font-size: 8pt;
        color: #64748b;
      }
      @bottom-left {
        content: "هندسه ۱ دهم ریاضی · پاسخ‌نامه تشریحی آزمون سمپاد و تالس";
        font-family: 'Vazirmatn', sans-serif;
        font-size: 8pt;
        color: #64748b;
      }
    }

    * {
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }

    body {
      font-family: 'Vazirmatn', sans-serif;
      font-size: 9pt;
      line-height: 1.55;
      color: #1e293b;
      background-color: #ffffff;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }

    /* Math typography engine */
    .math {
      font-family: 'Cambria Math', 'Times New Roman', serif;
      direction: ltr;
      display: inline-flex;
      align-items: center;
      font-size: 1rem;
      color: #0f172a;
      font-weight: 600;
      margin: 0 3px;
      vertical-align: middle;
    }
    .math-block {
      direction: ltr;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 6px 0;
      padding: 6px 10px;
      background: #f8fafc;
      border-radius: 6px;
      border-left: 3px solid #0284c7;
      font-family: 'Cambria Math', 'Times New Roman', serif;
      font-size: 1.02rem;
      font-weight: 600;
      color: #0f172a;
    }
    .frac {
      display: inline-flex;
      flex-direction: column;
      vertical-align: middle;
      text-align: center;
      padding: 0 3px;
      font-size: 0.88em;
      line-height: 1.15;
      margin: 0 2px;
    }
    .num {
      border-bottom: 1.5px solid #0f172a;
      padding: 0 2px 2px 2px;
    }
    .den {
      padding: 2px 2px 0 2px;
    }
    .sqrt {
      display: inline-flex;
      align-items: center;
    }
    .sqrt-sym {
      font-size: 1.25em;
      margin-right: 1px;
    }
    .sqrt-bar {
      border-top: 1.5px solid #0f172a;
      padding: 0 2px;
    }

    /* Header banner */
    .header-banner {
      border: 1.5px solid #0f172a;
      border-radius: 8px;
      padding: 8px 14px;
      margin-bottom: 10px;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .header-title-box {
      flex: 1;
    }
    .header-title {
      font-size: 12.5pt;
      font-weight: 700;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
    }
    .header-subtitle {
      font-size: 8.8pt;
      color: #475569;
      margin-top: 3px;
    }
    .header-meta {
      text-align: left;
      font-size: 8.2pt;
      color: #334155;
      border-right: 2px solid #cbd5e1;
      padding-right: 12px;
      margin-right: 12px;
      line-height: 1.6;
    }
    .badge-top {
      display: inline-block;
      padding: 2px 7px;
      border-radius: 4px;
      font-size: 7.8pt;
      font-weight: 700;
      background: #0284c7;
      color: #ffffff;
      margin-bottom: 3px;
    }

    /* Section divider */
    .section-bar {
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 14px 0 10px 0;
      padding-bottom: 5px;
      border-bottom: 2px solid #0284c7;
    }
    .section-bar h2 {
      font-size: 11pt;
      font-weight: 700;
      color: #0f172a;
    }
    .section-bar .section-badge {
      background: #e0f2fe;
      color: #0369a1;
      font-size: 7.8pt;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 600;
    }

    /* Question cards */
    .q-card {
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      margin-bottom: 12px;
      box-shadow: 0 1px 3px rgba(0,0,0,0.03);
      page-break-inside: avoid;
      overflow: hidden;
    }
    .q-header {
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
      padding: 7px 12px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .q-title {
      font-weight: 700;
      font-size: 9.8pt;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 6px;
    }
    .q-tag {
      font-size: 7.8pt;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 600;
    }
    .tag-sampad { background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }
    .tag-thales { background: #e0f2fe; color: #0369a1; border: 1px solid #bae6fd; }
    .tag-area { background: #dcfce7; color: #166534; border: 1px solid #86efac; }

    .q-body {
      padding: 8px 12px;
      font-size: 9pt;
      color: #1e293b;
    }
    .q-statement {
      font-weight: 500;
      color: #0f172a;
      line-height: 1.6;
      margin-bottom: 6px;
    }

    /* Options grid */
    .options-grid {
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 6px;
      margin: 8px 0;
      padding: 6px 10px;
      background: #f8fafc;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
    }
    .opt-item {
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 8.8pt;
      padding: 3px 5px;
    }
    .opt-num {
      font-weight: 700;
      color: #0369a1;
    }
    .opt-correct {
      background: #dcfce7;
      border-radius: 4px;
      border: 1.2px solid #86efac;
      font-weight: 700;
      color: #166534;
    }

    /* Solution Box */
    .sol-box {
      background: #ffffff;
      border-top: 1px dashed #cbd5e1;
      padding: 8px 12px;
    }
    .sol-header {
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 9pt;
      font-weight: 700;
      color: #047857;
      margin-bottom: 6px;
    }

    /* Strategic Insight Box */
    .strategy-box {
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 6px;
      padding: 6px 10px;
      margin-bottom: 7px;
      font-size: 8.6pt;
      line-height: 1.5;
      color: #166534;
    }
    .strategy-box strong {
      color: #14532d;
    }

    /* Step flow */
    .step-item {
      margin-bottom: 6px;
      padding-right: 8px;
      border-right: 2px solid #94a3b8;
    }
    .step-label {
      font-weight: 700;
      font-size: 8.6pt;
      color: #0369a1;
      margin-bottom: 2px;
    }

    /* Teacher's Trap Box */
    .trap-box {
      background: #fffbeb;
      border: 1px solid #fde68a;
      border-radius: 6px;
      padding: 6px 10px;
      margin-top: 7px;
      font-size: 8.5pt;
      color: #92400e;
      line-height: 1.5;
    }
    .trap-box strong {
      color: #78350f;
    }

    /* Final Answer Highlight */
    .ans-highlight {
      display: inline-block;
      background: #fef08a;
      padding: 1px 7px;
      border-radius: 4px;
      font-weight: 700;
      color: #854d0e;
      border: 1px solid #facc15;
    }

    /* Summary table */
    .summary-table {
      width: 100%;
      border-collapse: collapse;
      margin: 8px 0;
      font-size: 8.2pt;
    }
    .summary-table th, .summary-table td {
      border: 1px solid #cbd5e1;
      padding: 4px 6px;
      text-align: center;
    }
    .summary-table th {
      background: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
    }
  </style>
</head>
<body>

  <!-- Header Banner -->
  <div class="header-banner">
    <div class="header-title-box">
      <div class="header-title">
        <span>📐</span>
        <span>پاسخ‌نامه تشریحی و راهنمای جامع آزمون هندسه و قضیه تالس</span>
      </div>
      <div class="header-subtitle">
        هندسه ۱ پایۀ دهم دورۀ دوم متوسّطه · مرکز پرورش استعدادهای درخشان (سمپاد) — دبیرستان علامه حلی ۲ تهران
      </div>
    </div>
    <div class="header-meta">
      <span class="badge-top">آزمون اختصاصی سمپاد</span><br>
      سال تحصیلی ۱۴۰۵ – ۱۴۰۴<br>
      مباحث: واسطه هندسی، قضیه تالس، تشابه و روابط مساحت
    </div>
  </div>

  <!-- Key Summary Table -->
  <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:8px 12px; margin-bottom:12px;">
    <div style="font-weight:700; color:#0f172a; margin-bottom:4px; font-size:9pt;">🔑 جدول پاسخ‌های سریع و کلید آزمون (۵ سوال):</div>
    <table class="summary-table">
      <thead>
        <tr>
          <th>شماره سوال</th>
          <th>سوال ۷ (واسطه هندسی)</th>
          <th>سوال ۸ (تالس متوالی در زاویه)</th>
          <th>سوال ۱۰ (مسئله سه مربع)</th>
          <th>سوال ۱۱ (مساحت در ذوزنقه)</th>
          <th>سوال ۲ (همرسی ارتفاع‌ها)</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="font-weight:700; background:#f1f5f9;">گزینه صحیح</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۲ (b = ۳)</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۴ (۳√۳)</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱ (۲۵/۱۲)</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱ (۱۲)</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۲ (۲۱٫۲۵° &lt; x &lt; ۳۵°)</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION 1 -->
  <div class="section-bar">
    <h2>بخش ۱: هندسه تحلیلی و تالس در زاویه (صفحه ۱ آزمون)</h2>
    <span class="section-badge">۲ سوال</span>
  </div>

  <!-- Question 7 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>سوال ۷</span>
        <span class="q-tag tag-sampad">واسطه هندسی · جبر در هندسه</span>
      </div>
      <div><span class="ans-highlight">گزینه ۲ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر عدد طبیعی <span class="math">2b</span> واسطۀ هندسی بین عددهای <span class="math">b − 1</span> و <span class="math">5b + 3</span> باشد، <span class="math">b</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> ۲</div>
        <div class="opt-item opt-correct"><span class="opt-num">۲)</span> ۳</div>
        <div class="opt-item"><span class="opt-num">۳)</span> ۴</div>
        <div class="opt-item"><span class="opt-num">۴)</span> ۵</div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>تعریف واسطه هندسی:</strong> اگر <span class="math">y</span> واسطهٔ هندسی بین دو عدد <span class="math">x</span> و <span class="math">z</span> باشد، رابطهٔ <span class="math">y<sup>2</sup> = x · z</span> بین آن‌ها برقرار است.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: تشکیل معادله درجه دوم</div>
        طبق تعریف واسطهٔ هندسی داریم:
        <div class="math-block">
          (2b)<sup>2</sup> = (b − 1)(5b + 3)
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: ساده‌سازی و انتقال به یک طرف</div>
        پرانتزها را بسط می‌دهیم:
        <div class="math-block">
          4b<sup>2</sup> = 5b<sup>2</sup> + 3b − 5b − 3 ⇒ 4b<sup>2</sup> = 5b<sup>2</sup> − 2b − 3
        </div>
        با انتقال تمام جملات به سمت راست:
        <div class="math-block">
          b<sup>2</sup> − 2b − 3 = 0
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: تجزیه و پیدا کردن ریشه طبیعی</div>
        معادله را با اتحاد جمله مشترک تجزیه می‌کنیم:
        <div class="math-block">
          (b − 3)(b + 1) = 0 ⇒ b = 3  یا  b = −1
        </div>
        چون در صورت سوال تصریح شده که <span class="math">2b</span> و در نتیجه <span class="math">b</span> یک <strong>عدد طبیعی</strong> (<span class="math">b ∈ ℕ</span>) است، مقدار <span class="math">b = −1</span> غیرقابل‌قبول بوده و تنها پاسخ <span class="math">b = 3</span> پذیرفته می‌شود.
      </div>
      <div class="check-box" style="background:#f0fdf4; border:1px solid #bbf7d0; padding:5px 9px; border-radius:5px; margin-top:6px;">
        <strong>بررسی صحت پاسخ:</strong> با <span class="math">b = 3</span> اعداد به صورت <span class="math">b − 1 = 2</span> و <span class="math">2b = 6</span> و <span class="math">5b + 3 = 18</span> درمی‌آیند. می‌بینیم که <span class="math">6<sup>2</sup> = 36 = 2 × 18</span> کاملاً صحیح است.
      </div>
    </div>
  </div>

  <div style="page-break-before: always;"></div>

  <!-- Question 8 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>سوال ۸</span>
        <span class="q-tag tag-thales">قضیه تالس · تعامد در زاویه</span>
      </div>
      <div><span class="ans-highlight">گزینه ۴ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        در شکل روبه‌رو، اگر <span class="math">OE = 3 OA = 9</span> باشد، آن‌گاه طول <span class="math">OC</span> کدام است؟
      </div>
      <div style="display:flex; justify-content:center; margin:8px 0;">
        __Q8_SVG__
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math">2<span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">3</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> ۴</div>
        <div class="opt-item"><span class="opt-num">۳)</span> ۶</div>
        <div class="opt-item opt-correct"><span class="opt-num">۴)</span> <span class="math">3<span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">3</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>راهبرد طلایی (تالس زیگزاگی):</strong> چون <span class="math">BA ⊥ Ox</span> و <span class="math">DC ⊥ Ox</span> هستند، دو خط <span class="math">BA</span> و <span class="math">DC</span> با یکدیگر موازی‌اند (<span class="math">BA ∥ DC</span>). از طرفی پاره‌خط‌های <span class="math">BC</span> و <span class="math">DE</span> نیز با هم موازی هستند (<span class="math">BC ∥ DE</span>). ترکیب این دو تالس رابطه واسطه هندسی را روی نیم‌خط <span class="math">Ox</span> می‌سازد.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: اعمال قضیه تالس در مثلث OCD</div>
        چون <span class="math">BA ∥ DC</span> است، طبق جزء به کل قضیه تالس روی زاویه <span class="math">xOy</span> داریم:
        <div class="math-block">
          <span class="frac"><span class="num">OA</span><span class="den">OC</span></span> = <span class="frac"><span class="num">OB</span><span class="den">OD</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: اعمال قضیه تالس در مثلث ODE</div>
        چون <span class="math">BC ∥ DE</span> است، مجدداً طبق قضیه تالس روی زاویه <span class="math">xOy</span> داریم:
        <div class="math-block">
          <span class="frac"><span class="num">OB</span><span class="den">OD</span></span> = <span class="frac"><span class="num">OC</span><span class="den">OE</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: ترکیب تساوی‌ها و محاسبه OC</div>
        از مقایسه دو نسبت بالا نتیجه می‌شود:
        <div class="math-block">
          <span class="frac"><span class="num">OA</span><span class="den">OC</span></span> = <span class="frac"><span class="num">OC</span><span class="den">OE</span></span> ⇒ OC<sup>2</sup> = OA · OE
        </div>
        با توجه به فرض مسئله: <span class="math">OE = 9</span> و <span class="math">3 OA = 9 ⇒ OA = 3</span>. بنابراین:
        <div class="math-block">
          OC<sup>2</sup> = 3 × 9 = 27 ⇒ OC = <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">27</span></span> = 3<span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">3</span></span>
        </div>
      </div>
      <div class="trap-box">
        <strong>دام تستی:</strong> برخی دانش‌آموزان به اشتباه <span class="math">OC</span> را واسطه حسابی فرض کرده و میانگین می‌گیرند: <span class="math">(3+9)/2 = 6</span> که باعث انتخاب اشتباه گزینه ۳ می‌گردد!
      </div>
    </div>
  </div>

  <div style="page-break-before: always;"></div>

  <!-- SECTION 2 -->
  <div class="section-bar">
    <h2>بخش ۲: مسائل مربع‌ها و ذوزنقه (صفحه ۲ آزمون)</h2>
    <span class="section-badge">۲ سوال</span>
  </div>

  <!-- Question 10 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>سوال ۱۰</span>
        <span class="q-tag tag-thales">تشابه در مربع‌ها · خط تقاطع</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        در شکل مقابل سه مربع با اضلاع ۳ و ۴ و ۵ در کنار هم قرار دارند. طول پاره‌خط <span class="math">KP</span> کدام است؟
      </div>
      <div style="display:flex; justify-content:center; margin:8px 0;">
        __Q10_SVG__
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> <span class="math"><span class="frac"><span class="num">25</span><span class="den">12</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num">16</span><span class="den">7</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math"><span class="frac"><span class="num">35</span><span class="den">12</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="frac"><span class="num">22</span><span class="den">7</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>راهبرد طلایی (تشابه یا شیب خط):</strong> در مثلث قائم‌الزاویهٔ بزرگ با رأس‌های <span class="math">A</span> و <span class="math">B</span> و <span class="math">C</span>، ضلع افقی برابر با مجموع اضلاع سه مربع (<span class="math">AC = 3 + 4 + 5 = 12</span>) و ضلع عمودی برابر با ضلع مربع سوم (<span class="math">BC = 5</span>) است.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: مشخص کردن فاصله افقی نقطه P از مبدأ</div>
        پاره‌خط عمودی <span class="math">KD</span> روی مرز مربع دوم و سوم قرار دارد. فاصله نقطه <span class="math">D</span> از نقطه <span class="math">A</span> برابر است با:
        <div class="math-block">
          AD = 3 + 4 = 7
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: استفاده از تشابه مثلث‌ها برای محاسبه PD</div>
        مثلث قائم‌الزاویه <span class="math">ADP</span> متشابه با مثلث بزرگ <span class="math">ACB</span> است:
        <div class="math-block">
          <span class="frac"><span class="num">PD</span><span class="den">BC</span></span> = <span class="frac"><span class="num">AD</span><span class="den">AC</span></span> ⇒ <span class="frac"><span class="num">PD</span><span class="den">5</span></span> = <span class="frac"><span class="num">7</span><span class="den">12</span></span> ⇒ PD = <span class="frac"><span class="num">35</span><span class="den">12</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: محاسبه طول پاره‌خط هدف KP</div>
        طول کل پاره‌خط عمودی <span class="math">KD</span> برابر با ضلع مربع سوم یعنی ۵ است. بنابراین:
        <div class="math-block">
          KP = KD − PD = 5 − <span class="frac"><span class="num">35</span><span class="den">12</span></span> = <span class="frac"><span class="num">60 − 35</span><span class="den">12</span></span> = <span class="frac"><span class="num">25</span><span class="den">12</span></span>
        </div>
      </div>
      <div class="trap-box">
        <strong>دام تستی بسیار خطرناک:</strong> مقدار <span class="math">PD = <span class="frac"><span class="num">35</span><span class="den">12</span></span></span> دقیقاً در <strong>گزینه ۳</strong> قرار داده شده است! طراح انتظار دارد داوطلب عجله کرده و مقدار <span class="math">PD</span> را علامت بزند، در حالی که صورت سوال طول بخش بالایی یعنی <span class="math">KP</span> را خواسته است!
      </div>
    </div>
  </div>

  <div style="page-break-before: always;"></div>

  <!-- Question 11 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>سوال ۱۱</span>
        <span class="q-tag tag-area">مساحت ذوزنقه · خاصیت میانه</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        در ذوزنقهٔ <span class="math">ABCD</span>، نقطهٔ <span class="math">M</span> وسط قاعدهٔ <span class="math">CD</span> و مساحت مثلث <span class="math">BCD</span> برابر ۲۴ است. مساحت مثلث <span class="math">ADM</span> کدام است؟
      </div>
      <div style="display:flex; justify-content:center; margin:8px 0;">
        __Q11_SVG__
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> ۱۲</div>
        <div class="opt-item"><span class="opt-num">۲)</span> ۱۸</div>
        <div class="opt-item"><span class="opt-num">۳)</span> ۱۶</div>
        <div class="opt-item"><span class="opt-num">۴)</span> ۱۴</div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>قضیه هم‌ارتفاعی و میانه:</strong> 
        ۱) در هر ذوزنقه با پایه‌های موازی، دو مثلث که قاعدهٔ مشترک روی یک پایه دارند و رأس سوم آن‌ها روی پایهٔ موازی دیگر است، مساحت برابر دارند.<br>
        ۲) میانه در هر مثلث، مساحت مثلث را به دو بخش کاملاً مساوی تقسیم می‌کند.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: برابری مساحت مثلث‌های BCD و ACD</div>
        در ذوزنقه <span class="math">ABCD</span> دو قاعده <span class="math">AB</span> و <span class="math">CD</span> موازی هستند (<span class="math">AB ∥ CD</span>). فاصله هر نقطه از خط <span class="math">AB</span> تا خط <span class="math">CD</span> همان ارتفاع ذوزنقه یعنی <span class="math">h</span> است.
        <div class="math-block">
          S<sub>BCD</sub> = <span class="frac"><span class="num">1</span><span class="den">2</span></span> × CD × h = 24
        </div>
        برای مثلث <span class="math">ACD</span> نیز قاعده <span class="math">CD</span> و ارتفاع فرود آمده از رأس <span class="math">A</span> دقیقاً برابر با <span class="math">h</span> است:
        <div class="math-block">
          S<sub>ACD</sub> = <span class="frac"><span class="num">1</span><span class="den">2</span></span> × CD × h = S<sub>BCD</sub> = 24
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: نقش میانه AM در مثلث ACD</div>
        چون نقطه <span class="math">M</span> وسط قاعده <span class="math">CD</span> است (<span class="math">DM = MC</span>)، پاره‌خط <span class="math">AM</span> میانهٔ مثلث <span class="math">ACD</span> است. میانه مساحت را نصف می‌کند:
        <div class="math-block">
          S<sub>ADM</sub> = <span class="frac"><span class="num">1</span><span class="den">2</span></span> S<sub>ACD</sub> = <span class="frac"><span class="num">24</span><span class="den">2</span></span> = 12
        </div>
      </div>
    </div>
  </div>

  <div style="page-break-before: always;"></div>
  <!-- SECTION 3 -->
  <div class="section-bar" style="margin-top: 0;">
    <h2>بخش ۳: همرسی خطوط ویژه و نامساوی مثلثاتی (صفحه ۳ آزمون)</h2>
    <span class="section-badge">۱ سوال</span>
  </div>

  <!-- Question 2 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>سوال ۲</span>
        <span class="q-tag tag-sampad">نقطه همرسی ارتفاع‌ها · شرایط زاویه</span>
      </div>
      <div><span class="ans-highlight">گزینه ۲ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        دو تا از زاویه‌های مثلثی <span class="math">x + 20°</span> و <span class="math">3x − 15°</span> هستند. حدود <span class="math">x</span> کدام باشد تا ارتفاع‌های این مثلث، در نقطه‌ای درون آن همرس باشند؟
      </div>
      
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math">5° &lt; x &lt; 35°</span></div>
        <div class="opt-item opt-correct"><span class="opt-num">۲)</span> <span class="math">21.25° &lt; x &lt; 35°</span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math">35° &lt; x &lt; 43.75°</span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math">21.25° &lt; x &lt; 43.75°</span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>قضیه مکان همرسی ارتفاع‌ها (Orthocenter):</strong><br>
        ۱) اگر مثلث <strong>حاده‌الزاویه</strong> باشد: محل همرسی ارتفاع‌ها <strong>درون مثلث</strong> است.<br>
        ۲) اگر مثلث قائم‌الزاویه باشد: محل همرسی روی رأس زاویه قائمه است.<br>
        ۳) اگر مثلث منفرجه‌الزاویه باشد: محل همرسی در خارج از مثلث قرار دارد.<br>
        بنابراین برای اینکه ارتفاع‌ها درون مثلث همرس باشند، باید <strong>هر سه زاویه مثلث اکیداً حاده (&lt; ۹۰°) و مثبت (&gt; ۰°)</strong> باشند.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: محاسبه زاویه سوم مثلث</div>
        دو زاویه معلوم را <span class="math">A = x + 20°</span> و <span class="math">B = 3x − 15°</span> می‌نامیم. مجموع زوایای مثلث <span class="math">180°</span> است:
        <div class="math-block">
          C = 180° − (A + B) = 180° − (4x + 5°) = 175° − 4x
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: اعمال شرط حاده و مثبت بودن برای تک‌تک زوایا</div>
        ۱) برای زاویه <span class="math">A</span>:
        <div class="math-block">
          0° &lt; x + 20° &lt; 90° ⇒ −20° &lt; x &lt; 70°
        </div>
        ۲) برای زاویه <span class="math">B</span>:
        <div class="math-block">
          0° &lt; 3x − 15° &lt; 90° ⇒ 15° &lt; 3x &lt; 105° ⇒ 5° &lt; x &lt; 35°
        </div>
        ۳) برای زاویه <span class="math">C</span> (زاویه سوم):
        <div class="math-block">
          0° &lt; 175° − 4x &lt; 90°
        </div>
        از نامساوی راست: <span class="math">175° − 4x &lt; 90° ⇒ 4x &gt; 85° ⇒ x &gt; 21.25°</span><br>
        از نامساوی چپ: <span class="math">175° − 4x &gt; 0° ⇒ 4x &lt; 175° ⇒ x &lt; 43.75°</span><br>
        بنابراین برای زاویه C داریم: <span class="math">21.25° &lt; x &lt; 43.75°</span>.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: اشتراک‌گیری بین حدود سه‌گانه</div>
        <div class="math-block">
          x ∈ (5°, 35°) ∩ (21.25°, 43.75°) ∩ (−20°, 70°)
        </div>
        کران پایین باید بزرگتر از هر دو باشد: <span class="math">x &gt; 21.25°</span>.<br>
        کران بالا باید کوچکتر از هر دو باشد: <span class="math">x &lt; 35°</span>.<br>
        بنابراین بازه نهایی برابر است با:
        <div class="math-block">
          21.25° &lt; x &lt; 35°
        </div>
      </div>
      <div class="trap-box">
        <strong>دام‌های تستی طراح:</strong><br>
        • اگر داوطلب فقط شرط زاویه B را چک کند، به اشتباه به گزینه ۱ (<span class="math">5° &lt; x &lt; 35°</span>) می‌رسد!<br>
        • اگر داوطلب فقط شرط زاویه سوم را چک کند، به اشتباه به گزینه ۴ (<span class="math">21.25° &lt; x &lt; 43.75°</span>) می‌رسد!<br>
        تنها با اشتراک‌گیری کامل بین تمام زوایای سه‌گانه به گزینه صحیح ۲ خواهید رسید.
      </div>
    </div>
  </div>

</body>
</html>
"""

html = html.replace("__VAZIR_REG__", vazir_reg_b64)
html = html.replace("__VAZIR_MED__", vazir_med_b64)
html = html.replace("__VAZIR_BOLD__", vazir_bold_b64)
html = html.replace("__Q8_SVG__", q8_svg)
html = html.replace("__Q10_SVG__", q10_svg)
html = html.replace("__Q11_SVG__", q11_svg)
html = html.replace("__Q2_SVG__", q2_svg)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("HTML written successfully. Running Chromium...")
cmd = [
    "chromium",
    "--headless",
    "--no-sandbox",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    "--no-pdf-header-footer",
    f"--print-to-pdf={PDF_PATH}",
    HTML_PATH
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Chromium exit code:", res.returncode)
if os.path.exists(PDF_PATH):
    print(f"SUCCESS: PDF created at {PDF_PATH} ({os.path.getsize(PDF_PATH) / 1024:.1f} KB)")
