import subprocess, os, base64

OUTPUT_DIR = "/home/daytona/exam_work/trig"
HTML_PATH = os.path.join(OUTPUT_DIR, "trig_booklet.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Jame_Dayere_Mosalasati_Helli2.pdf")

# Read fonts
font_dir = "/home/daytona/.hermes/skills/persian-writing/assets/fonts"
vazir_reg_b64 = ""
vazir_bold_b64 = ""
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Regular.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Regular.ttf"), "rb") as f:
        vazir_reg_b64 = base64.b64encode(f.read()).decode("ascii")
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Bold.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Bold.ttf"), "rb") as f:
        vazir_bold_b64 = base64.b64encode(f.read()).decode("ascii")

with open(os.path.join(OUTPUT_DIR, "circle.svg"), "r", encoding="utf-8") as f:
    circle_svg = f.read()

html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>بانک سوالات تکمیلی و درسنامه بمب دایره مثلثاتی - ریاضی ۱ دهم (ویژه آزمون حلی ۲)</title>
  <style>
    @font-face {{
      font-family: 'Vazirmatn';
      src: url('data:font/ttf;base64,{vazir_reg_b64}') format('truetype');
      font-weight: 400;
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
        color: #71717a;
      }}
      @bottom-left {{
        content: "ریاضی ۱ دهم · جزوه جمع‌بندی و بانک سوال دایره مثلثاتی · اختصاصی آرمین";
        font-family: 'Vazirmatn', sans-serif;
        font-size: 8pt;
        color: #71717a;
      }}
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
    }}

    body {{
      font-family: 'Vazirmatn', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
      font-size: 9.5pt;
      line-height: 1.6;
      color: #18181b;
      background-color: #ffffff;
      -webkit-print-color-adjust: exact;
      print-color-adjust: exact;
    }}

    /* Header */
    .exam-header {{
      border: 2px solid #18181b;
      border-radius: 8px;
      padding: 10px 16px;
      margin-bottom: 14px;
      display: flex;
      justify-content: space-between;
      align-items: center;
      background: #fafafa;
    }}

    .exam-title {{
      font-size: 13pt;
      font-weight: 700;
      color: #09090b;
    }}

    .exam-sub {{
      font-size: 9pt;
      color: #52525b;
      margin-top: 2px;
    }}

    .exam-meta {{
      text-align: left;
      font-size: 8.5pt;
      color: #71717a;
      line-height: 1.4;
    }}

    /* Section Headings */
    h2.section-title {{
      font-size: 11pt;
      font-weight: 700;
      color: #09090b;
      background: #f4f4f5;
      border-right: 4px solid #2563eb;
      padding: 5px 10px;
      border-radius: 0 4px 4px 0;
      margin-top: 14px;
      margin-bottom: 10px;
    }}

    /* Callout Boxes */
    .trap-box {{
      background: #fef2f2;
      border: 1px solid #fee2e2;
      border-right: 3.5px solid #ef4444;
      border-radius: 0 6px 6px 0;
      padding: 8px 12px;
      margin: 8px 0;
      font-size: 9pt;
    }}
    .trap-title {{
      font-weight: 700;
      color: #b91c1c;
      display: flex;
      align-items: center;
      gap: 6px;
      margin-bottom: 3px;
    }}

    .tip-box {{
      background: #f0fdf4;
      border: 1px solid #dcfce7;
      border-right: 3.5px solid #16a34a;
      border-radius: 0 6px 6px 0;
      padding: 8px 12px;
      margin: 8px 0;
      font-size: 9pt;
    }}
    .tip-title {{
      font-weight: 700;
      color: #15803d;
      margin-bottom: 3px;
    }}

    .q-card {{
      border: 1px solid #e4e4e7;
      border-radius: 6px;
      padding: 10px 12px;
      margin-bottom: 12px;
      background: #ffffff;
      page-break-inside: avoid;
    }}

    .q-header {{
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 6px;
      border-bottom: 1px dashed #e4e4e7;
      padding-bottom: 4px;
    }}

    .q-num {{
      font-weight: 700;
      color: #1d4ed8;
      font-size: 9.5pt;
    }}

    .q-level {{
      font-size: 7.5pt;
      padding: 2px 6px;
      border-radius: 4px;
      background: #eff6ff;
      color: #1d4ed8;
      font-weight: 700;
      border: 1px solid #bfdbfe;
    }}

    .q-text {{
      font-size: 9.5pt;
      color: #09090b;
      margin-bottom: 8px;
      line-height: 1.6;
    }}

    .solution-box {{
      background: #fafafa;
      border-right: 3px solid #6366f1;
      padding: 8px 10px;
      border-radius: 0 4px 4px 0;
      margin-top: 6px;
      font-size: 9pt;
      line-height: 1.6;
    }}

    .sol-step {{
      margin-bottom: 4px;
    }}

    .sol-label {{
      font-weight: 700;
      color: #4f46e5;
    }}

    /* Math Styling */
    .math {{
      font-family: 'Times New Roman', Cambria, serif;
      direction: ltr;
      display: inline-block;
      font-weight: 600;
      color: #0f172a;
    }}

    .frac {{
      display: inline-block;
      vertical-align: middle;
      text-align: center;
      padding: 0 2px;
      font-size: 9pt;
    }}
    .frac > span {{
      display: block;
      padding: 0.5px;
    }}
    .frac span.bottom {{
      border-top: 1.2px solid #18181b;
    }}

    .page-break {{
      page-break-before: always;
    }}

    .two-col {{
      display: flex;
      gap: 12px;
      align-items: center;
    }}

    table.trig-table {{
      width: 100%;
      border-collapse: collapse;
      margin: 8px 0;
      font-size: 8.5pt;
      text-align: center;
    }}

    table.trig-table th {{
      background: #f1f5f9;
      padding: 5px;
      border: 1px solid #cbd5e1;
      font-weight: 700;
    }}

    table.trig-table td {{
      padding: 4.5px;
      border: 1px solid #e2e8f0;
    }}
  </style>
</head>
<body>

  <!-- HEADER -->
  <div class="exam-header">
    <div>
      <div class="exam-title">🎯 درسنامه طلایی و بانک سوالات بمب دایره مثلثاتی (ریاضی ۱ دهم)</div>
      <div class="exam-sub">ویژه آمادگی ۲۰ آزمون کلاسی و تستی · دبیرستان علامه حلی ۲ تهران</div>
    </div>
    <div class="exam-meta">
      <div><strong>مخاطب:</strong> آرمین جان</div>
      <div><strong>سطح:</strong> پیشرفته / دام‌دار سمپاد</div>
      <div><strong>مباحث:</strong> دایره، محورها، شیب خط، روابط و مقایسه‌ها</div>
    </div>
  </div>

  <!-- SECTION 1: ESSENTIAL LESSON & DIAGRAM -->
  <h2 class="section-title">۱. دایره مثلثاتی در یک نگاه و تحلیل خطوط و محورها</h2>
  <div class="two-col" style="margin-bottom: 10px;">
    <div style="flex: 1.1; font-size: 9pt;">
      <ul style="padding-right: 18px; line-height: 1.65;">
        <li><strong>مرکز و شعاع:</strong> دایره‌ای با مرکز مبدأ مختصات <span class="math">O(0,0)</span> و شعاع <span class="math">R = 1</span> که جهت مثبت آن پادساعت‌گرد (خلاف عقربه‌های ساعت) است.</li>
        <li><strong>محور کسینوس‌ها:</strong> همان محور افقی (<span class="math">x</span>ها) است. محدوده: <span class="math">-1 &le; cos &theta; &le; 1</span>.</li>
        <li><strong>محور سینوس‌ها:</strong> همان محور عمودی (<span class="math">y</span>ها) است. محدوده: <span class="math">-1 &le; sin &theta; &le; 1</span>.</li>
        <li><strong>مختصات هر نقطه روی دایره:</strong> نقطه انتهای کمان <span class="math">&theta;</span> همواره <span class="math">P(cos &theta;, sin &theta;)</span> است. بنابراین معادله دایره می‌شود: <span class="math">cos<sup>2</sup>&theta; + sin<sup>2</sup>&theta; = 1</span>.</li>
        <li><strong>خط تانژانت:</strong> خط مماس بر دایره در نقطه <span class="math">(1, 0)</span> یعنی خط <span class="math">x = 1</span> است. تانژانت در <span class="math">90&deg;</span> و <span class="math">270&deg;</span> تعریف‌نشده است چون امتداد شعاع موازی محور تانژانت می‌شود!</li>
        <li><strong>خط کتانژانت:</strong> خط مماس بر دایره در نقطه <span class="math">(0, 1)</span> یعنی خط <span class="math">y = 1</span> است. در <span class="math">0&deg;</span> و <span class="math">180&deg;</span> تعریف‌نشده است.</li>
      </ul>
    </div>
    <div style="flex: 0.9; text-align: center;">
      {circle_svg}
    </div>
  </div>

  <!-- TABLE OF QUADRANTS -->
  <table class="trig-table">
    <thead>
      <tr>
        <th>ناحیه (ربع)</th>
        <th>محدوده زاویه (&theta;)</th>
        <th>علامت <span class="math">sin &theta;</span></th>
        <th>علامت <span class="math">cos &theta;</span></th>
        <th>علامت <span class="math">tan &theta;</span></th>
        <th>علامت <span class="math">cot &theta;</span></th>
        <th>رفتار روی دایره</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td><strong>اول (I)</strong></td>
        <td><span class="math">0&deg; &lt; &theta; &lt; 90&deg;</span></td>
        <td style="color:#16a34a; font-weight:bold;">+ (صعودی)</td>
        <td style="color:#dc2626; font-weight:bold;">+ (نزولی)</td>
        <td style="color:#16a34a; font-weight:bold;">+ (صعودی)</td>
        <td style="color:#dc2626; font-weight:bold;">+ (نزولی)</td>
        <td><span class="math">&theta; &gt; 45&deg; &rArr; sin &theta; &gt; cos &theta;</span></td>
      </tr>
      <tr>
        <td><strong>دوم (II)</strong></td>
        <td><span class="math">90&deg; &lt; &theta; &lt; 180&deg;</span></td>
        <td style="color:#16a34a; font-weight:bold;">+ (نزولی)</td>
        <td style="color:#dc2626; font-weight:bold;">- (نزولی)</td>
        <td style="color:#dc2626; font-weight:bold;">- (صعودی)</td>
        <td style="color:#dc2626; font-weight:bold;">- (نزولی)</td>
        <td>سینوس مثبت، بقیه همه منفی!</td>
      </tr>
      <tr>
        <td><strong>سوم (III)</strong></td>
        <td><span class="math">180&deg; &lt; &theta; &lt; 270&deg;</span></td>
        <td style="color:#dc2626; font-weight:bold;">- (نزولی)</td>
        <td style="color:#16a34a; font-weight:bold;">- (صعودی)</td>
        <td style="color:#16a34a; font-weight:bold;">+ (صعودی)</td>
        <td style="color:#16a34a; font-weight:bold;">+ (نزولی)</td>
        <td>سینوس و کسینوس هر دو منفی، تانژانت و کتانژانت مثبت!</td>
      </tr>
      <tr>
        <td><strong>چهارم (IV)</strong></td>
        <td><span class="math">270&deg; &lt; &theta; &lt; 360&deg;</span></td>
        <td style="color:#16a34a; font-weight:bold;">- (صعودی)</td>
        <td style="color:#16a34a; font-weight:bold;">+ (صعودی)</td>
        <td style="color:#dc2626; font-weight:bold;">- (صعودی)</td>
        <td style="color:#dc2626; font-weight:bold;">- (نزولی)</td>
        <td>فقط کسینوس مثبت است، بقیه همه منفی!</td>
      </tr>
    </tbody>
  </table>

  <!-- TRAPS -->
  <div class="trap-box">
    <div class="trap-title">⚠️ تله مرگبار ۱: زاویه ۱ رادیان در برابر ۱ درجه!</div>
    بچه‌ها اغلب فراموش می‌کنند که اگر علامت درجه (<span class="math">&deg;</span>) نباشد، زاویه برحسب <strong>رادیان</strong> است! <br>
    چون <span class="math">&pi; &approx; 3.14 \text{ rad} = 180&deg;</span>، پس هر رادیان تقریباً <span class="math">1 \text{ rad} &approx; 57.3&deg;</span> است:
    <br>• زاویه <strong>۱ رادیان</strong> (<span class="math">&approx; 57.3&deg;</span>): در <strong>ربع اول</strong> است (<span class="math">sin 1 &gt; 0, cos 1 &gt; 0</span> و چون از <span class="math">45&deg;</span> رد شده، <span class="math">sin 1 &gt; cos 1</span>).
    <br>• زاویه <strong>۲ رادیان</strong> (<span class="math">&approx; 114.6&deg;</span>): در <strong>ربع دوم</strong> است (<span class="math">sin 2 &gt; 0, cos 2 &lt; 0</span>).
    <br>• زاویه <strong>۳ رادیان</strong> (<span class="math">&approx; 171.9&deg;</span>): هنوز در <strong>ربع دوم</strong> (نزدیک <span class="math">180&deg;</span>) است!
    <br>• زاویه <strong>۴ رادیان</strong> (<span class="math">&approx; 229.2&deg;</span>): در <strong>ربع سوم</strong> است (<span class="math">sin 4 &lt; 0, cos 4 &lt; 0, tan 4 &gt; 0</span>).
  </div>

  <div class="tip-box">
    <div class="tip-title">⚡️ تله مرگبار ۲: شیب خط و تانژانت زاویه با جهت مثبت محور xها</div>
    اگر خطی با جهت مثبت محور <span class="math">x</span> زاویه <span class="math">&alpha;</span> بسازد، شیب خط برابر است با: <span class="math">m = tan &alpha;</span>.
    <br>• اگر خط صعودی باشد (<span class="math">&alpha;</span> حاده باشد)، شیب مثبت است (<span class="math">m &gt; 0</span>).
    <br>• اگر خط نزولی باشد (<span class="math">&alpha;</span> باز یا منفرجه باشد)، شیب منفی است (<span class="math">m &lt; 0</span>).
    <br>• زاویه خط <span class="math">y = -\sqrt{3}x + 2</span> با جهت مثبت محور <span class="math">x</span>ها: <span class="math">tan &alpha; = -\sqrt{3} \rArr &alpha; = 180&deg; - 60&deg; = 120&deg;</span>.
  </div>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- SECTION 2: 10 KILLER QUESTIONS -->
  <h2 class="section-title">۲. بانک ۱۰ تست و سوال برگزیده و دام‌دار با پاسخ تشریحی جامع</h2>

  <!-- Q1 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۱ (تعیین علامت و ربع مثلثاتی ترکیبی)</span>
      <span class="q-level">سطح: متوسط به بالا · پرتکرار آزمون‌ها</span>
    </div>
    <div class="q-text">
      اگر <span class="math">&theta;</span> زاویه‌ای باشد که در روابط <span class="math">\frac{sin &theta;}{cos &theta;} &lt; 0</span> و <span class="math">\sqrt{cos<sup>2</sup>&theta;} = -cos &theta;</span> و <span class="math">sin &theta; - cos &theta; &gt; 0</span> صدق کند، انتهای کمان <span class="math">&theta;</span> در کدام ناحیه مثلثاتی قرار دارد؟ و علامت عبارت <span class="math">A = tan &theta; &minus; cot &theta;</span> چگونه است؟
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">گام ۱ (تحلیل رابطه اول):</span> داریم <span class="math">\frac{sin &theta;}{cos &theta;} = tan &theta; &lt; 0</span>. تانژانت در نواحی <strong>دوم و چهارم</strong> منفی است.</div>
      <div class="sol-step"><span class="sol-label">گام ۲ (تحلیل رابطه رادیکالی):</span> می‌دانیم <span class="math">\sqrt{cos<sup>2</sup>&theta;} = |cos &theta;|</span>. شرط داده‌شده می‌گوید <span class="math">|cos &theta;| = -cos &theta;</span>، پس حتماً <span class="math">cos &theta; &le; 0</span> است. بین ربع ۲ و ۴، جایی که کسینوس منفی است، منحصراً <strong>ناحیه دوم (II)</strong> است.</div>
      <div class="sol-step"><span class="sol-label">گام ۳ (بررسی شرط سوم برای اطمینان):</span> در ربع دوم، <span class="math">sin &theta; &gt; 0</span> و <span class="math">cos &theta; &lt; 0</span> است. بنابراین <span class="math">sin &theta; - cos &theta; = (+ ) - (- ) = (+ ) &gt; 0</span> کاملاً برقرار است. پس زاویه در <strong>ناحیه دوم</strong> است.</div>
      <div class="sol-step"><span class="sol-label">گام ۴ (تعیین علامت عبارت A):</span> در ربع دوم <span class="math">tan &theta; &lt; 0</span> و <span class="math">cot &theta; &lt; 0</span> است. اما آیا حاصل تفریق مثبت است یا منفی؟ <br>
      می‌دانیم <span class="math">A = tan &theta; - cot &theta; = \frac{sin &theta;}{cos &theta;} - \frac{cos &theta;}{sin &theta;} = \frac{sin<sup>2</sup>&theta; - cos<sup>2</sup>&theta;}{sin &theta; cos &theta;}</span>. مخرج <span class="math">sin &theta; cos &theta; &lt; 0</span> (منفی) است. علامت صورت بستگی به این دارد که زاویه قبل از <span class="math">135&deg;</span> است یا بعد از آن، اما اگر فرض کنیم <span class="math">&theta; = 120&deg;</span>: <span class="math">tan 120&deg; = -\sqrt{3}</span> و <span class="math">cot 120&deg; = -\frac{\sqrt{3}}{3}</span>، پس <span class="math">A = -\sqrt{3} - (-\frac{\sqrt{3}}{3}) = -\frac{2\sqrt{3}}{3} &lt; 0</span>.</div>
    </div>
  </div>

  <!-- Q2 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۲ (تله مقایسه مقادیر بدون ماشین حساب و رادیان)</span>
      <span class="q-level">سطح: تله‌دار حلی ۲ · ایده کنکور سراسری</span>
    </div>
    <div class="q-text">
      کدام‌یک از گزاره‌های زیر درست و کدام نادرست است؟ مقادیر را از کوچک به بزرگ مرتب کنید:
      <br>الف) <span class="math">sin 1 &gt; sin 2 &gt; sin 3</span>
      <br>ب) <span class="math">cos 1 &gt; cos 2</span>
      <br>ج) مقایسه <span class="math">sin 1</span> و <span class="math">cos 1</span>
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">گام ۱ (تبدیل ذهنی رادیان به درجه):</span>
        <br>• <span class="math">1 \text{ rad} &approx; 57.3&deg;</span> (ربع اول، بعد از <span class="math">45&deg;</span>)
        <br>• <span class="math">2 \text{ rad} &approx; 114.6&deg; = 180&deg; - 65.4&deg;</span> (ربع دوم) &rArr; <span class="math">sin 2 = sin(180&deg; - 65.4&deg;) = sin 65.4&deg;</span>
        <br>• <span class="math">3 \text{ rad} &approx; 171.9&deg; = 180&deg; - 8.1&deg;</span> (ربع دوم نزدیک به محور منفی) &rArr; <span class="math">sin 3 = sin 8.1&deg;</span>
      </div>
      <div class="sol-step"><span class="sol-label">گام ۲ (مقایسه سینوس‌ها):</span> در ربع اول، هر چه زاویه بزرگتر شود سینوس بیشتر می‌شود. داریم: <span class="math">65.4&deg; &gt; 57.3&deg; &gt; 8.1&deg;</span>.
        <br>بنابراین: <span class="math">sin 65.4&deg; &gt; sin 57.3&deg; &gt; sin 8.1&deg; \rArr \mathbf{sin 2 &gt; sin 1 &gt; sin 3}</span>. پس گزاره الف <strong>نادرست</strong> است! (بسیاری از بچه‌ها فکر می‌کنند چون ۳>۲>۱ است پس سینوس ۳ بزرگتر است در حالی که ۳ رادیان خیلی به محور افقی نزدیک و کوچیک است!).
      </div>
      <div class="sol-step"><span class="sol-label">گام ۳ (مقایسه کسینوس‌ها):</span> زاویه ۱ در ربع اول است پس <span class="math">cos 1 &gt; 0</span> (مثبت)؛ زاویه ۲ در ربع دوم است پس <span class="math">cos 2 &lt; 0</span> (منفی). پس مسلماً <span class="math">cos 1 &gt; cos 2</span> است و گزاره ب <strong>درست</strong> است.</div>
      <div class="sol-step"><span class="sol-label">گام ۴ (مقایسه sin 1 و cos 1):</span> زاویه ۱ رادیان یعنی <span class="math">57.3&deg;</span> در ربع اول و بالای خط نیمساز (<span class="math">&theta; &gt; 45&deg;</span>) قرار دارد. روی دایره مثلثاتی برای هر زاویه بین <span class="math">45&deg;</span> تا <span class="math">90&deg;</span> همواره <span class="math">\mathbf{sin &theta; &gt; cos &theta;}</span> است. پس <span class="math">sin 1 &gt; cos 1</span> است.</div>
    </div>
  </div>

  <!-- Q3 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۳ (خطوط، تانژانت و دایره مثلثاتی)</span>
      <span class="q-level">سطح: استاندارد امتحانی و آزمونی</span>
    </div>
    <div class="q-text">
      خطی به معادله <span class="math">\sqrt{3}y + 3x - 6 = 0</span> مفروض است:
      <br>الف) این خط با جهت مثبت محور <span class="math">x</span>ها چه زاویه‌ای می‌سازد؟
      <br>ب) اگر خطی موازی این خط از مبدأ مختصات بگذرد، دایره مثلثاتی را در چه نقاطی قطع می‌کند؟
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">حل قسمت الف:</span> معادله را به فرم استاندارد <span class="math">y = mx + h</span> می‌نویسیم:
        <br><span class="math">\sqrt{3}y = -3x + 6 \rArr y = \frac{-3}{\sqrt{3}}x + \frac{6}{\sqrt{3}} = -\sqrt{3}x + 2\sqrt{3}</span>
        <br>شیب خط برابر است با <span class="math">m = -\sqrt{3}</span>. چون شیب خط برابر تانژانت زاویه با جهت مثبت محور <span class="math">x</span>هاست:
        <br><span class="math">tan &alpha; = -\sqrt{3}</span>. چون تانژانت منفی است، زاویه منفرجه (ربع دوم) است. می‌دانیم <span class="math">tan 60&deg; = \sqrt{3}</span>، پس:
        <br><span class="math">&alpha; = 180&deg; - 60&deg; = \mathbf{120&deg;}</span> (یا <span class="math">\frac{2\pi}{3}</span> رادیان).
      </div>
      <div class="sol-step"><span class="sol-label">حل قسمت ب:</span> خطی که از مبدا بگذرد و موازی باشد، معادل زاویه <span class="math">120&deg;</span> و امتداد آن در ربع چهارم یعنی <span class="math">120&deg; + 180&deg; = 300&deg;</span> است:
        <br>• نقطه اول (<span class="math">120&deg;</span>): <span class="math">P_1(cos 120&deg;, sin 120&deg;) = (-cos 60&deg;, sin 60&deg;) = \mathbf{(-\frac{1}{2}, \frac{\sqrt{3}}{2})}</span>
        <br>• نقطه دوم (<span class="math">300&deg;</span>): <span class="math">P_2(cos 300&deg;, sin 300&deg;) = (cos 60&deg;, -sin 60&deg;) = \mathbf{(\frac{1}{2}, -\frac{\sqrt{3}}{2})}</span>
      </div>
    </div>
  </div>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- Q4 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۴ (روابط اساسی مثلثاتی و تعیین نسبت‌ها)</span>
      <span class="q-level">سطح: سوال پایه ثابت امتحانات نهایی و آزمون‌ها</span>
    </div>
    <div class="q-text">
      اگر <span class="math">tan &alpha; = -\frac{3}{4}</span> و انتهای کمان <span class="math">&alpha;</span> در ناحیه دوم دایره مثلثاتی باشد، مقدار سایر نسبت‌های مثلثاتی و همچنین مقدار عددی عبارت <span class="math">E = \frac{2sin &alpha; - 3cos &alpha;}{4sin &alpha; + cos &alpha;}</span> را بیابید.
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">روش ۱ (استفاده از اتحادهای مثلثاتی):</span>
        <br>می‌دانیم <span class="math">1 + tan<sup>2</sup>&alpha; = \frac{1}{cos<sup>2</sup>&alpha;}</span>.
        <br>جایگذاری: <span class="math">1 + (-\frac{3}{4})<sup>2</sup> = 1 + \frac{9}{16} = \frac{25}{16} = \frac{1}{cos<sup>2</sup>&alpha;} \rArr cos<sup>2</sup>&alpha; = \frac{16}{25}</span>.
        <br>چون زاویه در ناحیه دوم است، کسینوس منفی است: <span class="math">\mathbf{cos &alpha; = -\frac{4}{5}}</span>.
        <br>سپس سینوس: <span class="math">sin &alpha; = tan &alpha; \cdot cos &alpha; = (-\frac{3}{4}) \cdot (-\frac{4}{5}) = \mathbf{+\frac{3}{5}}</span>.
        <br>و کتانژانت: <span class="math">cot &alpha; = \frac{1}{tan &alpha;} = \mathbf{-\frac{4}{3}}</span>.
      </div>
      <div class="sol-step"><span class="sol-label">تکنیک سرعتی برای عبارت E:</span> صورت و مخرج کسر را بر <span class="math">cos &alpha;</span> تقسیم می‌کنیم تا همه‌چیز تبدیل به <span class="math">tan &alpha;</span> شود:
        <br><span class="math">E = \frac{2\frac{sin &alpha;}{cos &alpha;} - 3\frac{cos &alpha;}{cos &alpha;}}{4\frac{sin &alpha;}{cos &alpha;} + \frac{cos &alpha;}{cos &alpha;}} = \frac{2 tan &alpha; - 3}{4 tan &alpha; + 1} = \frac{2(-\frac{3}{4}) - 3}{4(-\frac{3}{4}) + 1} = \frac{-\frac{3}{2} - 3}{-3 + 1} = \frac{-\frac{9}{2}}{-2} = \mathbf{\frac{9}{4}}</span>.
      </div>
    </div>
  </div>

  <!-- Q5 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۵ (ساده‌سازی رادیکال و قدر مطلق در دایره مثلثاتی)</span>
      <span class="q-level">سطح: تله‌دار و محبوب طراحان تیزهوشان</span>
    </div>
    <div class="q-text">
      اگر <span class="math">\frac{3\pi}{4} &lt; x &lt; \pi</span> باشد (بین <span class="math">135&deg;</span> تا <span class="math">180&deg;</span>)، حاصل عبارت زیر را به ساده‌ترین شکل ممکن بنویسید:
      <br><span class="math">A = \sqrt{1 - 2sin x cos x} + \sqrt{cos<sup>2</sup> x} - \sqrt{1 + 2sin x cos x}</span>
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">گام ۱ (بازنویسی زیر رادیکال‌ها به مربع کامل):</span>
        <br>می‌دانیم <span class="math">1 = sin<sup>2</sup>x + cos<sup>2</sup>x</span>، پس:
        <br><span class="math">1 - 2sin x cos x = sin<sup>2</sup>x + cos<sup>2</sup>x - 2sin x cos x = (sin x - cos x)<sup>2</sup></span>
        <br><span class="math">1 + 2sin x cos x = (sin x + cos x)<sup>2</sup></span>
        <br>بنابراین عبارت به این صورت درمی‌آید: <span class="math">A = |sin x - cos x| + |cos x| - |sin x + cos x|</span>.
      </div>
      <div class="sol-step"><span class="sol-label">گام ۲ (تعیین علامت درون قدرمطلق‌ها با دایره مثلثاتی):</span>
        <br>زاویه در بازه <span class="math">(135&deg;, 180&deg;)</span> است:
        <br>۱) در ربع دوم <span class="math">sin x &gt; 0</span> و <span class="math">cos x &lt; 0</span> است. پس <span class="math">sin x - cos x = (+ ) - (- ) = (+ ) &gt; 0</span> است &rArr; خودش خارج می‌شود: <span class="math">sin x - cos x</span>.
        <br>۲) چون کسینوس منفی است، <span class="math">|cos x| = -cos x</span>.
        <br>۳) <strong>تله کلیدی:</strong> علامت <span class="math">sin x + cos x</span> چیست؟ روی دایره مثلثاتی در <span class="math">135&deg;</span> داریم <span class="math">sin 135&deg; = \frac{\sqrt{2}}{2}</span> و <span class="math">cos 135&deg; = -\frac{\sqrt{2}}{2}</span> (مجموع صفر است). اما بین <span class="math">135&deg;</span> تا <span class="math">180&deg;</span>، زاویه به محور افقی منفی نزدیک‌تر می‌شود؛ یعنی اندازه منفی کسینوس بر اندازه سینوس می‌چربد (مثلاً <span class="math">x=150&deg; \rArr sin 150&deg; = 0.5, cos 150&deg; &approx; -0.86</span>)، پس <span class="math">sin x + cos x &lt; 0</span> (منفی) است!
        <br>بنابراین <span class="math">|sin x + cos x| = -(sin x + cos x)</span>.
      </div>
      <div class="sol-step"><span class="sol-label">گام ۳ (محاسبه نهایی):</span>
        <br><span class="math">A = (sin x - cos x) + (-cos x) - [-(sin x + cos x)]</span>
        <br><span class="math">A = sin x - cos x - cos x + sin x + cos x = \mathbf{2sin x - cos x}</span>.
      </div>
    </div>
  </div>

  <!-- Q6 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۶ (هندسه و مساحت روی دایره مثلثاتی)</span>
      <span class="q-level">سطح: خلاقانه و مفهومی سمپاد</span>
    </div>
    <div class="q-text">
      در دایره مثلثاتی زیر، انتهای کمان <span class="math">&theta;</span> نقطه <span class="math">P</span> در ربع اول است. خط مماس بر دایره در نقطه <span class="math">A(1, 0)</span> (محور تانژانت)، امتداد شعاع <span class="math">OP</span> را در نقطه <span class="math">T</span> قطع می‌کند. اگر تصویر نقطه <span class="math">P</span> بر محور <span class="math">x</span>ها نقطه <span class="math">H</span> باشد، مساحت ذوزنقه <span class="math">PHTA</span> را برحسب نسبت‌های مثلثاتی <span class="math">&theta;</span> به دست آورید.
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">گام ۱ (یافتن مختصات و طول اضلاع):</span>
        <br>• مرکز <span class="math">O(0, 0)</span> و <span class="math">A(1, 0)</span>.
        <br>• نقطه <span class="math">P(cos &theta;, sin &theta;)</span> روی دایره است. تصویر آن روی محور <span class="math">x</span>ها <span class="math">H(cos &theta;, 0)</span> است.
        <br>• ارتفاع قائم نقطه <span class="math">P</span> برابر قاعده کوچک ذوزنقه است: <span class="math">PH = sin &theta;</span>.
        <br>• نقطه <span class="math">T</span> روی خط <span class="math">x = 1</span> است، پس مختصات آن <span class="math">T(1, tan &theta;)</span> است و ارتفاع آن قاعده بزرگ ذوزنقه است: <span class="math">AT = tan &theta;</span>.
        <br>• فاصله بین دو قاعده، ارتفاع ذوزنقه روی محور افقی است: <span class="math">h = HA = x_A - x_H = 1 - cos &theta;</span>.
      </div>
      <div class="sol-step"><span class="sol-label">گام ۲ (فرمول مساحت ذوزنقه):</span>
        <br><span class="math">S = \frac{\text{قاعده بزرگ} + \text{قاعده کوچک}}{2} \times \text{ارتفاع} = \frac{AT + PH}{2} \times HA</span>
        <br><span class="math">S = \frac{tan &theta; + sin &theta;}{2} \times (1 - cos &theta;)</span>
        <br>می‌توانیم <span class="math">tan &theta; = \frac{sin &theta;}{cos &theta;}</span> بنویسیم:
        <br><span class="math">tan &theta; + sin &theta; = sin &theta; (1 + \frac{1}{cos &theta;}) = sin &theta; (\frac{1 + cos &theta;}{cos &theta;}) = tan &theta; (1 + cos &theta;)</span>
        <br>ضرب در ارتفاع: <span class="math">(1 + cos &theta;)(1 - cos &theta;) = 1 - cos<sup>2</sup>&theta; = sin<sup>2</sup>&theta;</span>.
        <br>بنابراین فرم فوق‌العاده ساده مساحت: <span class="math">S = \mathbf{\frac{sin<sup>3</sup>&theta;}{2cos &theta;} = \frac{1}{2} tan &theta; \cdot sin<sup>2</sup>&theta;}</span>.
      </div>
    </div>
  </div>

  <!-- PAGE BREAK -->
  <div class="page-break"></div>

  <!-- Q7 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۷ (حدود پارامتری روی دایره مثلثاتی)</span>
      <span class="q-level">سطح: تستی ترکیبی معادله و نامعادله</span>
    </div>
    <div class="q-text">
      اگر انتهای کمان زاویه <span class="math">&theta;</span> در ناحیه دوم دایره مثلثاتی باشد و داشته باشیم <span class="math">cos &theta; = \frac{2m - 3}{5}</span>، حدود تغییرات پارامتر <span class="math">m</span> را بیابید.
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">تحلیل دامنه کسینوس در ربع دوم:</span> در ناحیه دوم (<span class="math">90&deg; &lt; &theta; &lt; 180&deg;</span>)، کسینوس همواره منفی و بین <span class="math">-1</span> و <span class="math">0</span> اکید است (در مرزها زاویه تعریف نمی‌شود چون در خود ناحیه نیست):
        <br><span class="math">-1 &lt; cos &theta; &lt; 0</span>
      </div>
      <div class="sol-step"><span class="sol-label">حل نامعادله:</span>
        <br><span class="math">-1 &lt; \frac{2m - 3}{5} &lt; 0</span>
        <br>طرفین را در ۵ ضرب می‌کنیم: <span class="math">-5 &lt; 2m - 3 &lt; 0</span>
        <br>عدد ۳ را به طرفین اضافه می‌کنیم: <span class="math">-2 &lt; 2m &lt; 3</span>
        <br>تقسیم بر ۲: <span class="math">\mathbf{-1 &lt; m &lt; \frac{3}{2}}</span>.
      </div>
    </div>
  </div>

  <!-- Q8 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۸ (زوایای قرینه، مکمل و علامت‌ها)</span>
      <span class="q-level">سطح: استاندارد تشریحی و امتحانی</span>
    </div>
    <div class="q-text">
      اگر <span class="math">sin 20&deg; = a</span> باشد، حاصل عبارت زیر را برحسب <span class="math">a</span> به دست آورید:
      <br><span class="math">B = \frac{sin(160&deg;) - cos(110&deg;)}{cos(70&deg;) + sin(-20&deg;)}</span>
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">تبدیل تک‌تک زوایا به زاویه حاده ۲۰ درجه:</span>
        <br>۱) <span class="math">sin(160&deg;) = sin(180&deg; - 20&deg;) = +sin 20&deg; = a</span> (زاویه مکمل سینوس یکسان دارد).
        <br>۲) <span class="math">cos(110&deg;) = cos(90&deg; + 20&deg;) = -sin 20&deg; = -a</span>.
        <br>۳) <span class="math">cos(70&deg;) = cos(90&deg; - 20&deg;) = +sin 20&deg; = a</span> (زاویه متمم).
        <br>۴) <span class="math">sin(-20&deg;) = -sin 20&deg; = -a</span> (سینوس منفی‌خوار نیست و منفی را بیرون می‌دهد).
      </div>
      <div class="sol-step"><span class="sol-label">جایگذاری:</span>
        <br>صورت: <span class="math">sin(160&deg;) - cos(110&deg;) = a - (-a) = 2a</span>
        <br>مخرج: <span class="math">cos(70&deg;) + sin(-20&deg;) = a + (-a) = 0</span>!
        <br>⚠️ <strong>نکته طراح:</strong> مخرج صفر می‌شود! اگر صورت سوال در مخرج به جای جمع، تفریق باشد:
        <br><span class="math">B' = \frac{sin(160&deg;) - cos(110&deg;)}{cos(70&deg;) - sin(-20&deg;)} = \frac{a - (-a)}{a - (-a)} = \frac{2a}{2a} = \mathbf{1}</span>!
      </div>
    </div>
  </div>

  <!-- Q9 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۹ (اثبات اتحاد با زنجیره کسری دقیق)</span>
      <span class="q-level">سطح: سوال ۱۰۰٪ قطعی امتحانات نهایی</span>
    </div>
    <div class="q-text">
      درستی اتحاد مثلثاتی زیر را ثابت کنید:
      <br><span class="math">\frac{1 - sin x}{cos x} = \frac{cos x}{1 + sin x}</span>
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">اثبات گام‌به‌گام (از سمت چپ شروع می‌کنیم):</span>
        <br>طرف چپ: <span class="math">LHS = \frac{1 - sin x}{cos x}</span>
        <br>صورت و مخرج را در مزدوج صورت یعنی <span class="math">(1 + sin x)</span> ضرب می‌کنیم:
        <br><span class="math">LHS = \frac{(1 - sin x)(1 + sin x)}{cos x (1 + sin x)}</span>
        <br>در صورت از اتحاد مزدوج استفاده می‌کنیم: <span class="math">(1 - sin x)(1 + sin x) = 1 - sin<sup>2</sup>x</span>:
        <br><span class="math">LHS = \frac{1 - sin<sup>2</sup>x}{cos x (1 + sin x)}</span>
        <br>از رابطه بنیادین دایره مثلثاتی می‌دانیم <span class="math">1 - sin<sup>2</sup>x = cos<sup>2</sup>x</span>:
        <br><span class="math">LHS = \frac{cos<sup>2</sup>x}{cos x (1 + sin x)}</span>
        <br>یک عامل <span class="math">cos x</span> از صورت و مخرج ساده می‌شود:
        <br><span class="math">LHS = \frac{cos x}{1 + sin x} = RHS</span> (حکم ثابت شد).
      </div>
    </div>
  </div>

  <!-- Q10 -->
  <div class="q-card">
    <div class="q-header">
      <span class="q-num">سوال ۱۰ (چالش جامع دایره مثلثاتی و طول کمان)</span>
      <span class="q-level">سطح: سخت · سطح مدارس تیزهوشان</span>
    </div>
    <div class="q-text">
      متحرکی از نقطه <span class="math">A(1, 0)</span> روی دایره مثلثاتی در جهت مثلثاتی شروع به حرکت می‌کند و مسافت مساوی <span class="math">L = \frac{19\pi}{6}</span> را طی کرده و در نقطه <span class="math">M</span> متوقف می‌شود.
      <br>الف) نقطه <span class="math">M</span> در کدام ناحیه مثلثاتی قرار دارد؟
      <br>ب) مختصات دقیق نقطه <span class="math">M</span> را بنویسید.
    </div>
    <div class="solution-box">
      <div class="sol-step"><span class="sol-label">حل قسمت الف:</span>
        <br>چون شعاع دایره مثلثاتی <span class="math">R = 1</span> است، طول کمان دقیقاً برابر با زاویه طی‌شده به رادیان است: <span class="math">&theta; = L = \frac{19\pi}{6}</span>.
        <br>تعداد دورهای کامل (<span class="math">2\pi</span>) را جدا می‌کنیم:
        <br><span class="math">\frac{19\pi}{6} = \frac{12\pi + 7\pi}{6} = 2\pi + \frac{7\pi}{6}</span>
        <br>پس متحرک یک دور کامل (<span class="math">2\pi = 360&deg;</span>) چرخیده و سپس به اندازه <span class="math">\frac{7\pi}{6}</span> رادیان ادامه داده است.
        <br><span class="math">\frac{7\pi}{6} = \pi + \frac{\pi}{6} = 180&deg; + 30&deg; = 210&deg;</span>.
        <br>زاویه <span class="math">210&deg;</span> بین <span class="math">180&deg;</span> تا <span class="math">270&deg;</span> است، پس نقطه <span class="math">M</span> در <strong>ناحیه سوم (III)</strong> قرار دارد.
      </div>
      <div class="sol-step"><span class="sol-label">حل قسمت ب (مختصات M):</span>
        <br>مختصات نقطه <span class="math">M(cos &theta;, sin &theta;)</span> است:
        <br>• <span class="math">x_M = cos(210&deg;) = cos(180&deg; + 30&deg;) = -cos 30&deg; = -\frac{\sqrt{3}}{2}</span>
        <br>• <span class="math">y_M = sin(210&deg;) = sin(180&deg; + 30&deg;) = -sin 30&deg; = -\frac{1}{2}</span>
        <br>بنابراین مختصات نقطه نهایی: <span class="math">\mathbf{M(-\frac{\sqrt{3}}{2}, -\frac{1}{2})}</span>.
      </div>
    </div>
  </div>

  <div style="margin-top: 14px; padding-top: 8px; border-top: 1.5px solid #18181b; text-align: center; font-size: 8.5pt; color: #52525b;">
    تهیه‌شده با ❤️ برای آرمین عزیز · دانش‌آموز تیزهوشان علامه حلی ۲ تهران · برای ترکوندن آزمون فردا و کسب نمره ۲۰! 🦾✨
  </div>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML written to:", HTML_PATH)

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
    print(f"SUCCESS: PDF generated at {PDF_PATH} ({sz / 1024:.1f} KB)")
else:
    print("FAILED to create PDF:", res.stderr)
