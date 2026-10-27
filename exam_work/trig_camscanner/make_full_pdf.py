import os, base64, subprocess

OUTPUT_DIR = "/home/daytona/exam_work/trig_camscanner"
HTML_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Jame_Mosalasat_Dahom.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Jame_Mosalasat_Dahom.pdf")

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
with open(os.path.join(OUTPUT_DIR, "assets/test3_geometry.svg"), "r", encoding="utf-8") as f:
    test3_svg = f.read()

with open(os.path.join(OUTPUT_DIR, "assets/q9_geometry.svg"), "r", encoding="utf-8") as f:
    q9_svg = f.read()

with open(os.path.join(OUTPUT_DIR, "assets/q10_geometry.svg"), "r", encoding="utf-8") as f:
    q10_svg = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>پاسخ‌نامه تشریحی و راهنمای جامع ۱۴ تست برگزیده مثلثات پایه دهم و کنکور</title>
  <style>
    @font-face {{
      font-family: 'Vazirmatn';
      src: url('data:font/ttf;base64,{vazir_reg_b64}') format('truetype');
      font-weight: 400;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Vazirmatn';
      src: url('data:font/ttf;base64,{vazir_med_b64}') format('truetype');
      font-weight: 500;
      font-style: normal;
    }}
    @font-face {{
      font-family: 'Vazirmatn';
      src: url('data:font/ttf;base64,{vazir_bold_b64}') format('truetype');
      font-weight: 700;
      font-style: normal;
    }}

    @page {{
      size: A4 portrait;
      margin: 12mm 12mm 14mm 12mm;
      @bottom-right {{
        content: "صفحه " counter(page);
        font-family: 'Vazirmatn', sans-serif;
        font-size: 8pt;
        color: #64748b;
      }}
      @bottom-left {{
        content: "ریاضی ۱ دهم · پاسخ‌نامه تشریحی ۱۴ تست برگزیده کنکور سراسری (مثلثات)";
        font-family: 'Vazirmatn', sans-serif;
        font-size: 8pt;
        color: #64748b;
      }}
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Vazirmatn', sans-serif;
      font-size: 9.2pt;
      line-height: 1.62;
      color: #1e293b;
      background-color: #ffffff;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}

    /* Math typography engine */
    .math {{
      font-family: 'Cambria Math', 'Times New Roman', serif;
      direction: ltr;
      display: inline-flex;
      align-items: center;
      font-size: 1.02rem;
      color: #0f172a;
      font-weight: 600;
      margin: 0 3px;
      vertical-align: middle;
    }}
    .math-block {{
      direction: ltr;
      display: flex;
      align-items: center;
      justify-content: center;
      margin: 8px 0;
      padding: 7px 12px;
      background: #f8fafc;
      border-radius: 6px;
      border-left: 3px solid #0284c7;
      font-family: 'Cambria Math', 'Times New Roman', serif;
      font-size: 1.04rem;
      font-weight: 600;
      color: #0f172a;
    }}
    .frac {{
      display: inline-flex;
      flex-direction: column;
      vertical-align: middle;
      text-align: center;
      padding: 0 3px;
      font-size: 0.88em;
      line-height: 1.15;
      margin: 0 2px;
    }}
    .num {{
      border-bottom: 1.5px solid #0f172a;
      padding: 0 2px 2px 2px;
    }}
    .den {{
      padding: 2px 2px 0 2px;
    }}
    .sqrt {{
      display: inline-flex;
      align-items: center;
    }}
    .sqrt-sym {{
      font-size: 1.25em;
      margin-right: 1px;
    }}
    .sqrt-bar {{
      border-top: 1.5px solid #0f172a;
      padding: 0 2px;
    }}

    /* Header banner */
    .header-banner {{
      border: 2px solid #0f172a;
      border-radius: 10px;
      padding: 12px 18px;
      margin-bottom: 16px;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .header-title-box {{
      flex: 1;
    }}
    .header-title {{
      font-size: 13.5pt;
      font-weight: 700;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 8px;
    }}
    .header-subtitle {{
      font-size: 9.3pt;
      color: #475569;
      margin-top: 4px;
    }}
    .header-meta {{
      text-align: left;
      font-size: 8.5pt;
      color: #334155;
      border-right: 2px solid #cbd5e1;
      padding-right: 14px;
      margin-right: 14px;
      line-height: 1.7;
    }}
    .badge-top {{
      display: inline-block;
      padding: 2px 8px;
      border-radius: 4px;
      font-size: 8pt;
      font-weight: 700;
      background: #0284c7;
      color: #ffffff;
      margin-bottom: 4px;
    }}

    /* Section divider */
    .section-bar {{
      display: flex;
      align-items: center;
      gap: 10px;
      margin: 18px 0 12px 0;
      padding-bottom: 6px;
      border-bottom: 2px solid #0284c7;
    }}
    .section-bar h2 {{
      font-size: 11.5pt;
      font-weight: 700;
      color: #0f172a;
    }}
    .section-bar .section-badge {{
      background: #e0f2fe;
      color: #0369a1;
      font-size: 8pt;
      padding: 2px 7px;
      border-radius: 4px;
      font-weight: 600;
    }}

    /* Question cards */
    .q-card {{
      background: #ffffff;
      border: 1px solid #cbd5e1;
      border-radius: 8px;
      margin-bottom: 16px;
      box-shadow: 0 1px 4px rgba(0,0,0,0.03);
      page-break-inside: avoid;
      overflow: hidden;
    }}
    .q-header {{
      background: #f8fafc;
      border-bottom: 1px solid #e2e8f0;
      padding: 8px 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}
    .q-title {{
      font-weight: 700;
      font-size: 10pt;
      color: #0f172a;
      display: flex;
      align-items: center;
      gap: 6px;
    }}
    .q-tag {{
      font-size: 7.8pt;
      padding: 2px 8px;
      border-radius: 4px;
      font-weight: 600;
    }}
    .tag-national {{ background: #f3e8ff; color: #6b21a8; border: 1px solid #e9d5ff; }}
    .tag-concept {{ background: #fef3c7; color: #92400e; border: 1px solid #fde68a; }}

    .q-body {{
      padding: 10px 14px;
      font-size: 9.3pt;
      color: #1e293b;
    }}
    .q-statement {{
      font-weight: 500;
      color: #0f172a;
      line-height: 1.65;
      margin-bottom: 8px;
    }}

    /* Options grid */
    .options-grid {{
      display: grid;
      grid-template-columns: repeat(4, 1fr);
      gap: 8px;
      margin: 10px 0;
      padding: 8px 12px;
      background: #f8fafc;
      border-radius: 6px;
      border: 1px solid #e2e8f0;
    }}
    .opt-item {{
      display: flex;
      align-items: center;
      gap: 5px;
      font-size: 9pt;
      padding: 3px 6px;
    }}
    .opt-num {{
      font-weight: 700;
      color: #0369a1;
    }}
    .opt-correct {{
      background: #dcfce7;
      border-radius: 4px;
      border: 1.2px solid #86efac;
      font-weight: 700;
      color: #166534;
    }}

    /* Solution Box */
    .sol-box {{
      background: #ffffff;
      border-top: 1px dashed #cbd5e1;
      padding: 10px 14px;
    }}
    .sol-header {{
      display: flex;
      align-items: center;
      gap: 6px;
      font-size: 9.2pt;
      font-weight: 700;
      color: #047857;
      margin-bottom: 8px;
    }}

    /* Strategic Insight Box */
    .strategy-box {{
      background: #f0fdf4;
      border: 1px solid #bbf7d0;
      border-radius: 6px;
      padding: 7px 11px;
      margin-bottom: 9px;
      font-size: 8.8pt;
      line-height: 1.55;
      color: #166534;
    }}
    .strategy-box strong {{
      color: #14532d;
    }}

    /* Step flow */
    .step-item {{
      margin-bottom: 8px;
      padding-right: 10px;
      border-right: 2px solid #94a3b8;
    }}
    .step-label {{
      font-weight: 700;
      font-size: 8.8pt;
      color: #0369a1;
      margin-bottom: 2px;
    }}

    /* Teacher's Trap Box */
    .trap-box {{
      background: #fffbeb;
      border: 1px solid #fde68a;
      border-radius: 6px;
      padding: 7px 11px;
      margin-top: 9px;
      font-size: 8.7pt;
      color: #92400e;
      line-height: 1.55;
    }}
    .trap-box strong {{
      color: #78350f;
    }}

    /* Final Answer Highlight */
    .ans-highlight {{
      display: inline-block;
      background: #fef08a;
      padding: 1px 7px;
      border-radius: 4px;
      font-weight: 700;
      color: #854d0e;
      border: 1px solid #facc15;
    }}

    /* Fast summary table */
    .summary-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 12px 0;
      font-size: 8.8pt;
    }}
    .summary-table th, .summary-table td {{
      border: 1px solid #cbd5e1;
      padding: 6px 8px;
      text-align: center;
    }}
    .summary-table th {{
      background: #f1f5f9;
      color: #0f172a;
      font-weight: 700;
    }}
  </style>
</head>
<body>

  <!-- Header Banner -->
  <div class="header-banner">
    <div class="header-title-box">
      <div class="header-title">
        <span>📐</span>
        <span>پاسخ‌نامه کاملاً تشریحی و راهنمای گام‌به‌گام ۱۴ تست برگزیده مثلثات</span>
      </div>
      <div class="header-subtitle">
        ریاضی ۱ دهم دورۀ دوم متوسّطه · بررسی جامع اتحادها، علامت نسبت‌ها در دایره مثلثاتی، مساحت و روابط هندسی
      </div>
    </div>
    <div class="header-meta">
      <span class="badge-top">سراسری و سمپاد</span><br>
      سال تحصیلی ۱۴۰۵ – ۱۴۰۴<br>
      مرجع: کنکورهای داخل و خارج ۱۴۰۳ - ۱۳۹۹
    </div>
  </div>

  <!-- Table of Keys at top -->
  <div style="background:#f8fafc; border:1px solid #cbd5e1; border-radius:8px; padding:10px 14px; margin-bottom:16px;">
    <div style="font-weight:700; color:#0f172a; margin-bottom:6px; font-size:9.5pt;">🔑 جدول پاسخ‌های سریع و کلید آزمون (۱۴ تست):</div>
    <table class="summary-table">
      <thead>
        <tr>
          <th>شماره سوال</th>
          <th>تست ۱۸</th>
          <th>تست ۱۹</th>
          <th>تست ۲۰</th>
          <th>تست ۱</th>
          <th>تست ۲</th>
          <th>تست ۳</th>
          <th>تست ۴</th>
          <th>تست ۵</th>
          <th>تست ۶</th>
          <th>تست ۷</th>
          <th>تست ۸</th>
          <th>تست ۹</th>
          <th>تست ۱۰</th>
          <th>تست ۱۵</th>
        </tr>
      </thead>
      <tbody>
        <tr>
          <td style="font-weight:700; background:#f1f5f9;">گزینه صحیح</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۳</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۴</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۲</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۲</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۴</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۳</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۳</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۴</td>
          <td style="font-weight:700; color:#166534; background:#dcfce7;">گزینه ۱</td>
        </tr>
      </tbody>
    </table>
  </div>

  <!-- SECTION 1 -->
  <div class="section-bar">
    <h2>بخش ۱: اتحادهای مثلثاتی و محاسبات جبری (صفحه ۱۴۸)</h2>
    <span class="section-badge">۳ تست</span>
  </div>

  <!-- Q18 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۱۸</span>
        <span class="q-tag tag-concept">اتحادهای مثلثاتی · توان دوم</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">sin α + cos α = <span class="frac"><span class="num">1</span><span class="den">4</span></span></span> باشد، حاصل <span class="math">|sin α − cos α|</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> <span class="math"><span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">31</span></span></span><span class="den">4</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">31</span></span></span><span class="den">2</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar"><span class="frac"><span class="num">33</span><span class="den">4</span></span></span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">33</span></span></span><span class="den">2</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>راهبرد طلایی:</strong> دو اتحاد مربع دو جمله‌ای در مثلثات پیوند مستقیمی با یکدیگر دارند:
        <span class="math">(sin α + cos α)<sup>2</sup> = 1 + 2 sin α cos α</span> و 
        <span class="math">(sin α − cos α)<sup>2</sup> = 1 − 2 sin α cos α</span>.
        جمع این دو اتحاد همواره برابر <span class="math">(sin α + cos α)<sup>2</sup> + (sin α − cos α)<sup>2</sup> = 2</span> می‌باشد.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: رابطه بین مربع مجموع و مربع تفاضل</div>
        طبق اتحاد بنیادین، داریم:
        <div class="math-block">
          (sin α − cos α)<sup>2</sup> = 2 − (sin α + cos α)<sup>2</sup>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: جای‌گذاری دادهٔ مسئله و محاسبه</div>
        با جای‌گذاری <span class="math">sin α + cos α = <span class="frac"><span class="num">1</span><span class="den">4</span></span></span> خواهیم داشت:
        <div class="math-block">
          (sin α − cos α)<sup>2</sup> = 2 − <span class="frac"><span class="num">1</span><span class="den">16</span></span> = <span class="frac"><span class="num">32 − 1</span><span class="den">16</span></span> = <span class="frac"><span class="num">31</span><span class="den">16</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: جذر گرفتن و قدرمطلق</div>
        <div class="math-block">
          |sin α − cos α| = <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar"><span class="frac"><span class="num">31</span><span class="den">16</span></span></span></span> = <span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">31</span></span></span><span class="den">4</span></span>
        </div>
      </div>
      <div class="trap-box">
        <strong>دام تستی:</strong> برخی دانش‌آموزان هنگام جذر گرفتن مخرج را فراموش کرده و کسر زیر رادیکال را ۲ محاسبه می‌کنند که منجر به انتخاب اشتباه گزینه ۲ می‌گردد!
      </div>
    </div>
  </div>

  <!-- Q19 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۱۹</span>
        <span class="q-tag tag-concept">نسبت‌های همگن · تبدیل به تانژانت</span>
      </div>
      <div><span class="ans-highlight">گزینه ۳ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">5(sin x − cos x) = 2 cos x + sin x</span> باشد، مقدار <span class="math">sin x · cos x</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math"><span class="frac"><span class="num">80</span><span class="den">81</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num">28</span><span class="den">33</span></span></span></div>
        <div class="opt-item opt-correct"><span class="opt-num">۳)</span> <span class="math"><span class="frac"><span class="num">28</span><span class="den">65</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="frac"><span class="num">72</span><span class="den">37</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>راهبرد طلایی:</strong> وقتی معادله‌ای خطی از سینوس و کسینوس داده شده است، بهترین روش تقسیم بر کسینوس برای یافتن مقدار عددی <span class="math">tan x</span> و سپس استفاده از فرمول <span class="math">sin x cos x = <span class="frac"><span class="num">tan x</span><span class="den">1 + tan<sup>2</sup> x</span></span></span> است.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: ساده‌سازی معادله و استخراج تانژانت</div>
        <div class="math-block">
          5 sin x − 5 cos x = 2 cos x + sin x  ⇒  4 sin x = 7 cos x  ⇒  tan x = <span class="frac"><span class="num">sin x</span><span class="den">cos x</span></span> = <span class="frac"><span class="num">7</span><span class="den">4</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: محاسبه ضرب سینوس در کسینوس بر حسب تانژانت</div>
        <div class="math-block">
          sin x · cos x = <span class="frac"><span class="num">tan x</span><span class="den">1 + tan<sup>2</sup> x</span></span> = <span class="frac"><span class="num"><span class="frac"><span class="num">7</span><span class="den">4</span></span></span><span class="den">1 + <span class="frac"><span class="num">49</span><span class="den">16</span></span></span></span> = <span class="frac"><span class="num"><span class="frac"><span class="num">7</span><span class="den">4</span></span></span><span class="den"><span class="frac"><span class="num">65</span><span class="den">16</span></span></span></span> = <span class="frac"><span class="num">7</span><span class="den">4</span></span> × <span class="frac"><span class="num">16</span><span class="den">65</span></span> = <span class="frac"><span class="num">28</span><span class="den">65</span></span>
        </div>
      </div>
    </div>
  </div>

  <!-- Q20 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۲۰</span>
        <span class="q-tag tag-concept">ساده‌سازی عبارات مثلثاتی</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">A = <span class="frac"><span class="num">1</span><span class="den">4 − sin<sup>2</sup> 10°</span></span> ( <span class="frac"><span class="num">4</span><span class="den">1 + tan<sup>2</sup> 10°</span></span> + 3 sin<sup>2</sup> 10° )</span> و <span class="math">B = <span class="frac"><span class="num">cot<sup>2</sup> 10° − cos<sup>2</sup> 10°</span><span class="den">cot<sup>2</sup> 10° · cos<sup>2</sup> 10°</span></span></span> باشد، حاصل <span class="math">A + B</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> <span class="math">2</span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math">3</span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math">1</span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math">4</span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: ساده‌سازی عبارت A</div>
        می‌دانیم <span class="math"><span class="frac"><span class="num">1</span><span class="den">1 + tan<sup>2</sup> θ</span></span> = cos<sup>2</sup> θ</span>. بنابراین داخل پرانتز داریم:
        <div class="math-block">
          4 cos<sup>2</sup> 10° + 3 sin<sup>2</sup> 10° = 4(1 − sin<sup>2</sup> 10°) + 3 sin<sup>2</sup> 10° = 4 − sin<sup>2</sup> 10°
        </div>
        در نتیجه: <span class="math">A = <span class="frac"><span class="num">4 − sin<sup>2</sup> 10°</span><span class="den">4 − sin<sup>2</sup> 10°</span></span> = 1</span>.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: ساده‌سازی عبارت B</div>
        صورت کسر B را بازنویسی می‌کنیم:
        <div class="math-block">
          cot<sup>2</sup> 10° − cos<sup>2</sup> 10° = <span class="frac"><span class="num">cos<sup>2</sup> 10°</span><span class="den">sin<sup>2</sup> 10°</span></span> − cos<sup>2</sup> 10° = cos<sup>2</sup> 10° ( <span class="frac"><span class="num">1</span><span class="den">sin<sup>2</sup> 10°</span></span> − 1 ) = cos<sup>2</sup> 10° · cot<sup>2</sup> 10°
        </div>
        چون صورت کسر دقیقاً برابر با مخرج شد، پس: <span class="math">B = 1</span>.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: محاسبه نهایی</div>
        <div class="math-block">
          A + B = 1 + 1 = 2
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 2 -->
  <div class="section-bar">
    <h2>بخش ۲: تست‌های کنکور سراسری (صفحه ۱۴۹)</h2>
    <span class="section-badge">۴ تست</span>
  </div>

  <!-- Test 1 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۱</span>
        <span class="q-tag tag-national">سراسری ریاضی داخل</span>
      </div>
      <div><span class="ans-highlight">گزینه ۴ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر انتهای کمان <span class="math">α</span> در ناحیهٔ چهارم دایرهٔ مثلثاتی باشد، حاصل عبارت <span class="math">(1 + cos α) ( <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">1 + cot<sup>2</sup> α</span></span> + <span class="frac"><span class="num">1</span><span class="den">tan α</span></span> )</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math">cos α</span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math">sin α</span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math">−cos α</span></div>
        <div class="opt-item opt-correct"><span class="opt-num">۴)</span> <span class="math">−sin α</span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>نکته تعیین ربع:</strong> در ربع چهارم، سینوس منفی (<span class="math">sin α &lt; 0</span>) و کسینوس مثبت (<span class="math">cos α &gt; 0</span>) است؛ خروج از زیر رادیکال زوج با قدرمطلق انجام می‌گیرد!
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: ساده‌سازی پرانتز دوم</div>
        <div class="math-block">
          <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">1 + cot<sup>2</sup> α</span></span> = <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar"><span class="frac"><span class="num">1</span><span class="den">sin<sup>2</sup> α</span></span></span></span> = <span class="frac"><span class="num">1</span><span class="den">|sin α|</span></span>
        </div>
        چون <span class="math">α</span> در ناحیه ۴ است، <span class="math">|sin α| = −sin α</span>. همچنین <span class="math"><span class="frac"><span class="num">1</span><span class="den">tan α</span></span> = <span class="frac"><span class="num">cos α</span><span class="den">sin α</span></span></span>. پس پرانتز دوم برابر است با:
        <div class="math-block">
          −<span class="frac"><span class="num">1</span><span class="den">sin α</span></span> + <span class="frac"><span class="num">cos α</span><span class="den">sin α</span></span> = <span class="frac"><span class="num">cos α − 1</span><span class="den">sin α</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: ضرب دو پرانتز با اتحاد مزدوج</div>
        <div class="math-block">
          (1 + cos α) × <span class="frac"><span class="num">cos α − 1</span><span class="den">sin α</span></span> = <span class="frac"><span class="num">cos<sup>2</sup> α − 1</span><span class="den">sin α</span></span> = <span class="frac"><span class="num">−sin<sup>2</sup> α</span><span class="den">sin α</span></span> = −sin α
        </div>
      </div>
    </div>
  </div>

  <!-- Test 2 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۲</span>
        <span class="q-tag tag-national">سراسری ریاضی خارج</span>
      </div>
      <div><span class="ans-highlight">گزینه ۲ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر انتهای کمان <span class="math">α</span> در ناحیهٔ دوم دایرهٔ مثلثاتی باشد، حاصل عبارت <span class="math"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar"><span class="frac"><span class="num">1 + sin α</span><span class="den">1 − sin α</span></span></span></span> − <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">1 + tan<sup>2</sup> α</span></span></span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math">−cot α</span></div>
        <div class="opt-item opt-correct"><span class="opt-num">۲)</span> <span class="math">−tan α</span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math">cot α</span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math">tan α</span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: ساده‌سازی کسر زیر رادیکال اول (گویاسازی مخرج)</div>
        صورت و مخرج را در <span class="math">1 + sin α</span> ضرب می‌کنیم:
        <div class="math-block">
          <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar"><span class="frac"><span class="num">(1 + sin α)<sup>2</sup></span><span class="den">1 − sin<sup>2</sup> α</span></span></span></span> = <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar"><span class="frac"><span class="num">(1 + sin α)<sup>2</sup></span><span class="den">cos<sup>2</sup> α</span></span></span></span> = <span class="frac"><span class="num">|1 + sin α|</span><span class="den">|cos α|</span></span>
        </div>
        در ربع دوم، <span class="math">1 + sin α &gt; 0</span> و <span class="math">cos α &lt; 0</span>، بنابراین:
        <div class="math-block">
          <span class="frac"><span class="num">1 + sin α</span><span class="den">−cos α</span></span> = −<span class="frac"><span class="num">1</span><span class="den">cos α</span></span> − tan α
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: ساده‌سازی رادیکال دوم</div>
        <div class="math-block">
          <span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">1 + tan<sup>2</sup> α</span></span> = <span class="frac"><span class="num">1</span><span class="den">|cos α|</span></span> = −<span class="frac"><span class="num">1</span><span class="den">cos α</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: تفاضل دو رادیکال</div>
        <div class="math-block">
          ( −<span class="frac"><span class="num">1</span><span class="den">cos α</span></span> − tan α ) − ( −<span class="frac"><span class="num">1</span><span class="den">cos α</span></span> ) = −tan α
        </div>
      </div>
    </div>
  </div>

  <!-- Test 3 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۳</span>
        <span class="q-tag tag-national">سراسری تجربی داخل ۱۴۰۲</span>
      </div>
      <div><span class="ans-highlight">گزینه ۲ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        در شکل زیر، اختلاف مساحت مثلث‌های <span class="math">ABC</span> و <span class="math">ADE</span> برابر <span class="math">1.75</span> است. مقدار <span class="math">tan ∠A</span> کدام است؟
      </div>
      <div style="display:flex; justify-content:center; margin:10px 0;">
        {test3_svg}
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">2</span></span></span></span></span></div>
        <div class="opt-item opt-correct"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">3</span></span></span></span></span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">3</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">2</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="strategy-box">
        <strong>فرمول مساحت مثلث با زاویه:</strong> مساحت هر مثلث برابر با نصف حاصل‌ضرب دو ضلع در سینوس زاویه بین آن‌هاست: <span class="math">S = <span class="frac"><span class="num">1</span><span class="den">2</span></span> a b sin θ</span>.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۱: مشخص کردن اضلاع دو مثلث</div>
        برای مثلث <span class="math">ABC</span>: اضلاع دربرگیرنده زاویه A عبارتند از <span class="math">AB = 5</span> و <span class="math">AC = 4 + 3 = 7</span>.<br>
        برای مثلث <span class="math">ADE</span>: اضلاع دربرگیرنده زاویه A عبارتند از <span class="math">AD = 5 + 2 = 7</span> و <span class="math">AE = 4</span>.
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: محاسبه مساحت‌ها و اختلاف آن‌ها</div>
        <div class="math-block">
          S<sub>ABC</sub> = <span class="frac"><span class="num">1</span><span class="den">2</span></span> × 5 × 7 × sin A = <span class="frac"><span class="num">35</span><span class="den">2</span></span> sin A
        </div>
        <div class="math-block">
          S<sub>ADE</sub> = <span class="frac"><span class="num">1</span><span class="den">2</span></span> × 7 × 4 × sin A = <span class="frac"><span class="num">28</span><span class="den">2</span></span> sin A
        </div>
        <div class="math-block">
          |S<sub>ABC</sub> − S<sub>ADE</sub>| = <span class="frac"><span class="num">7</span><span class="den">2</span></span> sin A = 1.75 = <span class="frac"><span class="num">7</span><span class="den">4</span></span>  ⇒  sin A = <span class="frac"><span class="num">1</span><span class="den">2</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: محاسبه تانژانت زاویه A</div>
        چون زاویه A یک زاویه حاده است و <span class="math">sin A = <span class="frac"><span class="num">1</span><span class="den">2</span></span></span>، پس <span class="math">∠A = 30°</span> می‌باشد:
        <div class="math-block">
          tan A = tan 30° = <span class="frac"><span class="num">1</span><span class="den"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">3</span></span></span></span>
        </div>
      </div>
    </div>
  </div>

  <!-- Test 4 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۴</span>
        <span class="q-tag tag-national">سراسری ریاضی خارج</span>
      </div>
      <div><span class="ans-highlight">گزینه ۴ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">cot x = 4</span> باشد، مقدار کسر <span class="math"><span class="frac"><span class="num">3 cos x − sin x</span><span class="den">cos x + sin x</span></span></span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math">0.2</span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math">0.4</span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math">1.4</span></div>
        <div class="opt-item opt-correct"><span class="opt-num">۴)</span> <span class="math">2.2</span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: همگن‌سازی کسر با تقسیم بر sin x</div>
        صورت و مخرج کسر را بر <span class="math">sin x</span> تقسیم می‌کنیم:
        <div class="math-block">
          <span class="frac"><span class="num"><span class="frac"><span class="num">3 cos x</span><span class="den">sin x</span></span> − <span class="frac"><span class="num">sin x</span><span class="den">sin x</span></span></span><span class="den"><span class="frac"><span class="num">cos x</span><span class="den">sin x</span></span> + <span class="frac"><span class="num">sin x</span><span class="den">sin x</span></span></span></span> = <span class="frac"><span class="num">3 cot x − 1</span><span class="den">cot x + 1</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: جای‌گذاری مقدار عددی</div>
        <div class="math-block">
          <span class="frac"><span class="num">3(4) − 1</span><span class="den">4 + 1</span></span> = <span class="frac"><span class="num">12 − 1</span><span class="den">5</span></span> = <span class="frac"><span class="num">11</span><span class="den">5</span></span> = 2.2
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 3 -->
  <div class="section-bar">
    <h2>بخش ۳: تست‌های کنکور سراسری ۱۴۰۳ – ۱۴۰۱ (صفحه ۱۵۰)</h2>
    <span class="section-badge">۴ تست</span>
  </div>

  <!-- Test 5 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۵</span>
        <span class="q-tag tag-national">سراسری تجربی خارج ۱۴۰۳</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math"><span class="frac"><span class="num">1</span><span class="den"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">cos<sup>2</sup> α</span></span></span></span> − <span class="frac"><span class="num">1</span><span class="den">cot α</span></span> = <span class="frac"><span class="num">1 − sin α</span><span class="den">|cos α|</span></span></span> و <span class="math">cot α = −<span class="frac"><span class="num">cos α</span><span class="den"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">1 − cos<sup>2</sup> α</span></span></span></span></span> باشد، انتهای کمان <span class="math">α</span> در کدام ناحیه مثلثاتی قرار دارد؟
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> چهارم</div>
        <div class="opt-item"><span class="opt-num">۲)</span> سوم</div>
        <div class="opt-item"><span class="opt-num">۳)</span> دوم</div>
        <div class="opt-item"><span class="opt-num">۴)</span> اول</div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: تحلیل تساوی اول (علامت کسینوس)</div>
        <div class="math-block">
          <span class="frac"><span class="num">1</span><span class="den">|cos α|</span></span> − <span class="frac"><span class="num">sin α</span><span class="den">cos α</span></span> = <span class="frac"><span class="num">1 − sin α</span><span class="den">|cos α|</span></span>
        </div>
        برای اینکه سمت چپ برابر با سمت راست شود، باید مخرج مشترک دقیقاً <span class="math">|cos α| = cos α</span> باشد که مستلزم <span class="math">cos α &gt; 0</span> است (ربع ۱ یا ۴).
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: تحلیل تساوی دوم (علامت سینوس)</div>
        می‌دانیم <span class="math"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">1 − cos<sup>2</sup> α</span></span> = |sin α|</span>. پس تساوی دوم به صورت زیر درمی‌آید:
        <div class="math-block">
          <span class="frac"><span class="num">cos α</span><span class="den">sin α</span></span> = −<span class="frac"><span class="num">cos α</span><span class="den">|sin α|</span></span>  ⇒  sin α = −|sin α|  ⇒  sin α &lt; 0
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: تعیین ربع مثلثاتی</div>
        تنها ناحیه‌ای که در آن <span class="math">cos α &gt; 0</span> و <span class="math">sin α &lt; 0</span> است، <strong>ناحیه چهارم</strong> است.
      </div>
    </div>
  </div>

  <!-- Test 6 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۶</span>
        <span class="q-tag tag-national">سراسری ریاضی داخل ۱۴۰۳</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">3 sin<sup>2</sup> x + a cos<sup>2</sup> x = 4</span> باشد، مقدار <span class="math">cot<sup>2</sup> x</span> با کدام مورد برابر است؟
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den">a − 4</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den">4 − a</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den">a − 3</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den">3 − a</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: تقسیم بر sin² x برای تولید کتانژانت</div>
        طرفین معادله را بر <span class="math">sin<sup>2</sup> x</span> تقسیم می‌کنیم:
        <div class="math-block">
          3 + a <span class="frac"><span class="num">cos<sup>2</sup> x</span><span class="den">sin<sup>2</sup> x</span></span> = <span class="frac"><span class="num">4</span><span class="den">sin<sup>2</sup> x</span></span>  ⇒  3 + a cot<sup>2</sup> x = 4(1 + cot<sup>2</sup> x) = 4 + 4 cot<sup>2</sup> x
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: جداسازی cot² x</div>
        <div class="math-block">
          a cot<sup>2</sup> x − 4 cot<sup>2</sup> x = 4 − 3  ⇒  (a − 4) cot<sup>2</sup> x = 1  ⇒  cot<sup>2</sup> x = <span class="frac"><span class="num">1</span><span class="den">a − 4</span></span>
        </div>
      </div>
    </div>
  </div>

  <!-- Test 7 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۷</span>
        <span class="q-tag tag-national">سراسری تجربی داخل ۱۴۰۲</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">sin α = 2 cos α</span> و انتهای کمان <span class="math">α</span> در ربع سوم مثلثاتی باشد، مقدار <span class="math">cos α</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> <span class="math">−<span class="frac"><span class="num">2<span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">10</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">5</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math"><span class="frac"><span class="num">2<span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">5</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">10</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: جای‌گذاری در اتحاد اصلی مثلثات</div>
        در رابطه <span class="math">sin<sup>2</sup> α + cos<sup>2</sup> α = 1</span> به جای سینوس، مقدار <span class="math">2 cos α</span> را قرار می‌دهیم:
        <div class="math-block">
          (2 cos α)<sup>2</sup> + cos<sup>2</sup> α = 1  ⇒  4 cos<sup>2</sup> α + cos<sup>2</sup> α = 1  ⇒  5 cos<sup>2</sup> α = 1  ⇒  cos<sup>2</sup> α = <span class="frac"><span class="num">1</span><span class="den">5</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: اعمال علامت ربع سوم و هم‌ارزی گزینه</div>
        در ربع سوم کسینوس منفی است:
        <div class="math-block">
          cos α = −<span class="frac"><span class="num">1</span><span class="den"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span></span> = −<span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">5</span></span> = −<span class="frac"><span class="num">2<span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">10</span></span>
        </div>
      </div>
    </div>
  </div>

  <!-- Test 8 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۸</span>
        <span class="q-tag tag-national">سراسری تجربی داخل ۱۴۰۱</span>
      </div>
      <div><span class="ans-highlight">گزینه ۳ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">2 sin<sup>2</sup> x + cos<sup>2</sup> x = <span class="frac"><span class="num">4</span><span class="den">3</span></span></span> باشد، حاصل <span class="math">tan<sup>2</sup> x</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> <span class="math"><span class="frac"><span class="num">3</span><span class="den">2</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num">2</span><span class="den">3</span></span></span></div>
        <div class="opt-item opt-correct"><span class="opt-num">۳)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den">2</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="frac"><span class="num">1</span><span class="den">4</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: تفکیک جمله و استخراج سینوس</div>
        <div class="math-block">
          sin<sup>2</sup> x + (sin<sup>2</sup> x + cos<sup>2</sup> x) = sin<sup>2</sup> x + 1 = <span class="frac"><span class="num">4</span><span class="den">3</span></span>  ⇒  sin<sup>2</sup> x = <span class="frac"><span class="num">4</span><span class="den">3</span></span> − 1 = <span class="frac"><span class="num">1</span><span class="den">3</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: محاسبه کسینوس و تانژانت</div>
        <div class="math-block">
          cos<sup>2</sup> x = 1 − sin<sup>2</sup> x = 1 − <span class="frac"><span class="num">1</span><span class="den">3</span></span> = <span class="frac"><span class="num">2</span><span class="den">3</span></span>
        </div>
        <div class="math-block">
          tan<sup>2</sup> x = <span class="frac"><span class="num">sin<sup>2</sup> x</span><span class="den">cos<sup>2</sup> x</span></span> = <span class="frac"><span class="num"><span class="frac"><span class="num">1</span><span class="den">3</span></span></span><span class="den"><span class="frac"><span class="num">2</span><span class="den">3</span></span></span></span> = <span class="frac"><span class="num">1</span><span class="den">2</span></span>
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 4 -->
  <div class="section-bar">
    <h2>بخش ۴: هندسه و ارتفاع مثلث‌ها (کنکور سراسری ۹۹ - صفحه ۱۵۱)</h2>
    <span class="section-badge">۲ تست</span>
  </div>

  <!-- Q9 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۹</span>
        <span class="q-tag tag-national">سراسری ریاضی خارج ۱۳۹۹</span>
      </div>
      <div><span class="ans-highlight">گزینه ۳ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        در شکل زیر، <span class="math">cot C = <span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">2</span></span></span> و <span class="math">AC = 96</span> است. اندازهٔ ارتفاع <span class="math">AH</span> کدام است؟
      </div>
      <div style="display:flex; justify-content:center; margin:10px 0;">
        {q9_svg}
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> ۴۸</div>
        <div class="opt-item"><span class="opt-num">۲)</span> ۵۶</div>
        <div class="opt-item opt-correct"><span class="opt-num">۳)</span> ۶۴</div>
        <div class="opt-item"><span class="opt-num">۴)</span> ۷۲</div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: رابطه اضلاع در مثلث قائم‌الزاویه AHC</div>
        در مثلث قائم‌الزاویه <span class="math">AHC</span> که زاویه قائمه در رأس <span class="math">H</span> قرار دارد، نسبت کتانژانت برابر با مجاور به مقابل است:
        <div class="math-block">
          cot C = <span class="frac"><span class="num">CH</span><span class="den">AH</span></span> = <span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">2</span></span>  ⇒  CH = <span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">2</span></span> AH
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: رابطه فیثاغورس در مثلث AHC</div>
        <div class="math-block">
          AC<sup>2</sup> = AH<sup>2</sup> + CH<sup>2</sup> = AH<sup>2</sup> + (<span class="frac"><span class="num"><span class="sqrt"><span class="sqrt-sym">√</span><span class="sqrt-bar">5</span></span></span><span class="den">2</span></span> AH)<sup>2</sup> = AH<sup>2</sup> + <span class="frac"><span class="num">5</span><span class="den">4</span></span> AH<sup>2</sup> = <span class="frac"><span class="num">9</span><span class="den">4</span></span> AH<sup>2</sup>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: محاسبه اندازه ارتفاع AH</div>
        با جذر گرفتن از دو طرف:
        <div class="math-block">
          AC = <span class="frac"><span class="num">3</span><span class="den">2</span></span> AH  ⇒  AH = <span class="frac"><span class="num">2</span><span class="den">3</span></span> AC = <span class="frac"><span class="num">2</span><span class="den">3</span></span> × 96 = 64
        </div>
      </div>
    </div>
  </div>

  <!-- Q10 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۱۰</span>
        <span class="q-tag tag-national">سراسری ریاضی داخل ۱۳۹۹</span>
      </div>
      <div><span class="ans-highlight">گزینه ۴ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        در شکل زیر، فرض کنید <span class="math">sin C = <span class="frac"><span class="num">5</span><span class="den">13</span></span></span> و <span class="math">CH = 9</span> باشد. اندازهٔ ارتفاع <span class="math">AH</span> کدام است؟
      </div>
      <div style="display:flex; justify-content:center; margin:10px 0;">
        {q10_svg}
      </div>
      <div class="options-grid">
        <div class="opt-item"><span class="opt-num">۱)</span> ۳/۲۵</div>
        <div class="opt-item"><span class="opt-num">۲)</span> ۳/۵</div>
        <div class="opt-item"><span class="opt-num">۳)</span> ۳/۶</div>
        <div class="opt-item opt-correct"><span class="opt-num">۴)</span> ۳/۷۵</div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: تعیین نسبت تانژانت در مثلث قائم‌الزاویه AHC</div>
        مثلث <span class="math">AHC</span> قائم‌الزاویه در رأس <span class="math">H</span> است و زاویه <span class="math">C</span> حاده است. با داشتن <span class="math">sin C = <span class="frac"><span class="num">5</span><span class="den">13</span></span></span> طبق سه‌گانه فیثاغورسی (۵، ۱۲، ۱۳) داریم:
        <div class="math-block">
          cos C = <span class="frac"><span class="num">12</span><span class="den">13</span></span>  ⇒  tan C = <span class="frac"><span class="num">sin C</span><span class="den">cos C</span></span> = <span class="frac"><span class="num">5</span><span class="den">12</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: محاسبه ارتفاع AH بر حسب CH</div>
        در مثلث قائم‌الزاویه <span class="math">AHC</span>، تانژانت زاویه C برابر است با نسبت ضلع مقابل به ضلع مجاور:
        <div class="math-block">
          tan C = <span class="frac"><span class="num">AH</span><span class="den">CH</span></span>  ⇒  AH = CH × tan C = 9 × <span class="frac"><span class="num">5</span><span class="den">12</span></span> = <span class="frac"><span class="num">45</span><span class="den">12</span></span> = <span class="frac"><span class="num">15</span><span class="den">4</span></span> = 3.75
        </div>
      </div>
    </div>
  </div>

  <!-- SECTION 5 -->
  <div class="section-bar">
    <h2>بخش ۵: اتحاد مجموع مکعبات (صفحه آخر جزوه)</h2>
    <span class="section-badge">۱ تست</span>
  </div>

  <!-- Q15 -->
  <div class="q-card">
    <div class="q-header">
      <div class="q-title">
        <span>تست ۱۵</span>
        <span class="q-tag tag-concept">اتحاد چاق و لاغر · مکعبات</span>
      </div>
      <div><span class="ans-highlight">گزینه ۱ صحیح است</span></div>
    </div>
    <div class="q-body">
      <div class="q-statement">
        اگر <span class="math">sin x + cos x = <span class="frac"><span class="num">1</span><span class="den">3</span></span></span> باشد، حاصل عبارت <span class="math">sin<sup>3</sup> x + cos<sup>3</sup> x</span> کدام است؟
      </div>
      <div class="options-grid">
        <div class="opt-item opt-correct"><span class="opt-num">۱)</span> <span class="math"><span class="frac"><span class="num">13</span><span class="den">27</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۲)</span> <span class="math"><span class="frac"><span class="num">13</span><span class="den">81</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۳)</span> <span class="math"><span class="frac"><span class="num">17</span><span class="den">27</span></span></span></div>
        <div class="opt-item"><span class="opt-num">۴)</span> <span class="math"><span class="frac"><span class="num">17</span><span class="den">81</span></span></span></div>
      </div>
    </div>
    <div class="sol-box">
      <div class="sol-header"><span>✓</span><span>تحلیل مفهومی و حل گام‌به‌گام:</span></div>
      <div class="step-item">
        <div class="step-label">گام ۱: محاسبه حاصل‌ضرب sin x cos x</div>
        طرفین تساوی داده شده را به توان دو می‌رسانیم:
        <div class="math-block">
          (sin x + cos x)<sup>2</sup> = 1 + 2 sin x cos x = <span class="frac"><span class="num">1</span><span class="den">9</span></span>  ⇒  2 sin x cos x = −<span class="frac"><span class="num">8</span><span class="den">9</span></span>  ⇒  sin x cos x = −<span class="frac"><span class="num">4</span><span class="den">9</span></span>
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۲: باز کردن اتحاد مجموع مکعبات</div>
        <div class="math-block">
          sin<sup>3</sup> x + cos<sup>3</sup> x = (sin x + cos x)(sin<sup>2</sup> x − sin x cos x + cos<sup>2</sup> x) = (sin x + cos x)(1 − sin x cos x)
        </div>
      </div>
      <div class="step-item">
        <div class="step-label">گام ۳: جای‌گذاری مقادیر عددی</div>
        <div class="math-block">
          sin<sup>3</sup> x + cos<sup>3</sup> x = <span class="frac"><span class="num">1</span><span class="den">3</span></span> × ( 1 − (−<span class="frac"><span class="num">4</span><span class="den">9</span></span>) ) = <span class="frac"><span class="num">1</span><span class="den">3</span></span> × ( 1 + <span class="frac"><span class="num">4</span><span class="den">9</span></span> ) = <span class="frac"><span class="num">1</span><span class="den">3</span></span> × <span class="frac"><span class="num">13</span><span class="den">9</span></span> = <span class="frac"><span class="num">13</span><span class="den">27</span></span>
        </div>
      </div>
    </div>
  </div>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print(f"HTML generated at {HTML_PATH} ({len(html_content)} bytes).")
print("Compiling to PDF with Chromium headless...")

cmd = [
    "chromium",
    "--headless",
    "--no-sandbox",
    "--disable-gpu",
    "--run-all-compositor-stages-before-draw",
    f"--print-to-pdf={PDF_PATH}",
    HTML_PATH
]

res = subprocess.run(cmd, capture_output=True, text=True)
print("Chromium exit code:", res.returncode)
if os.path.exists(PDF_PATH):
    sz = os.path.getsize(PDF_PATH)
    print(f"SUCCESS: PDF created at {PDF_PATH} ({sz / 1024:.1f} KB)")
else:
    print("FAILED: PDF not created!")
