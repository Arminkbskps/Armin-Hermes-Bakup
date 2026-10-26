import subprocess, os, base64

OUTPUT_DIR = "/home/daytona/roast-room/sessions/2026-10-18-voidclubs-future"
HTML_PATH = os.path.join(OUTPUT_DIR, "report_fa.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Roast_Room_VoidClubs_Strategy_FA.pdf")

# Read Vazirmatn font if available or use web font
font_dir = "/home/daytona/.hermes/skills/persian-writing/assets/fonts"
vazir_reg_b64 = ""
vazir_bold_b64 = ""
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Regular.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Regular.ttf"), "rb") as f:
        vazir_reg_b64 = base64.b64encode(f.read()).decode("ascii")
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Bold.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Bold.ttf"), "rb") as f:
        vazir_bold_b64 = base64.b64encode(f.read()).decode("ascii")

html_content = f"""<!DOCTYPE html>
<html lang="fa" dir="rtl">
<head>
  <meta charset="UTF-8">
  <title>صورت‌جلسه شورای مشاوران استراتژیک Roast Room - برند voidclubs.ir</title>
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
      margin: 14mm 14mm 16mm 14mm;
      @bottom-right {{
        content: "صفحه " counter(page);
        font-family: 'Vazirmatn', sans-serif;
        font-size: 8pt;
        color: #71717a;
      }}
      @bottom-left {{
        content: "Roast Room · جلسه محرمانه استراتژی voidclubs.ir";
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

    .header-box {{
      border-bottom: 2.5px solid #18181b;
      padding-bottom: 12px;
      margin-bottom: 16px;
      display: flex;
      justify-content: space-between;
      align-items: flex-end;
    }}

    .title-area h1 {{
      font-size: 16pt;
      font-weight: 700;
      color: #09090b;
      letter-spacing: -0.5px;
      margin-bottom: 4px;
    }}

    .title-area .subtitle {{
      font-size: 9.5pt;
      color: #52525b;
      font-weight: 400;
    }}

    .meta-area {{
      text-align: left;
      font-size: 8.5pt;
      color: #71717a;
      line-height: 1.4;
    }}

    .verdict-banner {{
      background: #09090b;
      color: #fafafa;
      border-radius: 8px;
      padding: 14px 18px;
      margin-bottom: 18px;
      display: flex;
      justify-content: space-between;
      align-items: center;
    }}

    .verdict-call {{
      font-size: 12pt;
      font-weight: 700;
      color: #22c55e;
    }}

    .verdict-desc {{
      font-size: 9pt;
      color: #d4d4d8;
      margin-top: 4px;
      max-width: 78%;
    }}

    .verdict-score {{
      background: #27272a;
      border: 1px solid #3f3f46;
      border-radius: 6px;
      padding: 6px 14px;
      text-align: center;
    }}

    .verdict-score .num {{
      font-size: 15pt;
      font-weight: 700;
      color: #4ade80;
      display: block;
      line-height: 1;
    }}

    .verdict-score .lbl {{
      font-size: 7pt;
      color: #a1a1aa;
      text-transform: uppercase;
    }}

    h2 {{
      font-size: 11pt;
      font-weight: 700;
      color: #09090b;
      border-right: 3px solid #09090b;
      padding-right: 8px;
      margin-top: 14px;
      margin-bottom: 10px;
    }}

    .options-grid {{
      display: grid;
      grid-template-columns: 1fr 1fr 1fr;
      gap: 10px;
      margin-bottom: 16px;
    }}

    .option-card {{
      border: 1px solid #e4e4e7;
      border-radius: 6px;
      padding: 10px;
      background: #fafafa;
      position: relative;
    }}

    .option-card.winner {{
      border: 1.5px solid #22c55e;
      background: #f0fdf4;
    }}

    .option-card .badge {{
      display: inline-block;
      font-size: 7.5pt;
      font-weight: 700;
      padding: 2px 6px;
      border-radius: 4px;
      margin-bottom: 6px;
    }}

    .badge-win {{ background: #22c55e; color: #fff; }}
    .badge-lose {{ background: #ef4444; color: #fff; }}
    .badge-neutral {{ background: #e4e4e7; color: #52525b; }}

    .option-title {{
      font-size: 9.5pt;
      font-weight: 700;
      color: #09090b;
      margin-bottom: 4px;
    }}

    .option-desc {{
      font-size: 8pt;
      color: #52525b;
      line-height: 1.45;
    }}

    .option-score-row {{
      margin-top: 8px;
      font-weight: 700;
      font-size: 8.5pt;
      color: #18181b;
      border-top: 1px dashed #d4d4d8;
      padding-top: 6px;
    }}

    .advisors-table {{
      width: 100%;
      border-collapse: collapse;
      margin-top: 8px;
      margin-bottom: 16px;
      font-size: 8.5pt;
    }}

    .advisors-table th {{
      background: #f4f4f5;
      color: #27272a;
      font-weight: 700;
      text-align: right;
      padding: 6px 8px;
      border: 1px solid #e4e4e7;
    }}

    .advisors-table td {{
      padding: 6px 8px;
      border: 1px solid #e4e4e7;
      vertical-align: top;
      line-height: 1.45;
    }}

    .advisors-table tr:nth-child(even) {{
      background: #fafafa;
    }}

    .seat-name {{
      font-weight: 700;
      color: #09090b;
      white-space: nowrap;
    }}

    .seat-pillar {{
      font-size: 7.5pt;
      color: #71717a;
      display: block;
    }}

    .quote-box {{
      background: #f8fafc;
      border-right: 3px solid #3b82f6;
      padding: 8px 12px;
      margin: 10px 0;
      font-size: 8.5pt;
      border-radius: 0 4px 4px 0;
    }}

    .crux-box {{
      background: #fffbeb;
      border: 1px solid #fef3c7;
      border-right: 3px solid #f59e0b;
      padding: 8px 12px;
      border-radius: 0 4px 4px 0;
      margin-bottom: 12px;
      font-size: 8.5pt;
    }}

    .crux-title {{
      font-weight: 700;
      color: #92400e;
      margin-bottom: 3px;
    }}

    .action-steps {{
      background: #f4f4f5;
      border-radius: 6px;
      padding: 10px 14px;
      margin-top: 10px;
    }}

    .action-step-item {{
      margin-bottom: 6px;
      font-size: 8.5pt;
      display: flex;
      align-items: flex-start;
    }}

    .step-num {{
      background: #18181b;
      color: #fff;
      font-size: 7.5pt;
      font-weight: 700;
      width: 17px;
      height: 17px;
      border-radius: 50%;
      display: inline-flex;
      align-items: center;
      justify-content: center;
      margin-left: 8px;
      flex-shrink: 0;
      margin-top: 2px;
    }}

    .page-break {{
      page-break-before: always;
    }}
  </style>
</head>
<body>

  <!-- PAGE 1 -->
  <div class="header-box">
    <div class="title-area">
      <h1>THE ROAST ROOM · اتاق استراتژی</h1>
      <div class="subtitle">حکم نهایی و صورت‌جلسه شورای ۷ نفره مشاوران درباره آینده برند <strong>voidclubs.ir</strong></div>
    </div>
    <div class="meta-area">
      <div><strong>تاریخ جلسه:</strong> ۲۷ مهر ۱۴۰۵</div>
      <div><strong>موسس:</strong> آرمین (علامه حلی ۲ تهران)</div>
      <div><strong>محدودیت اصلی:</strong> زمان مطالعه کنکور (۵ تا ۱۰ ساعت/هفته)</div>
    </div>
  </div>

  <div class="verdict-banner">
    <div>
      <div class="verdict-call">حکم قطعی شورا: تایید کامل گزینه الف (درآپ‌های کپسولی اختصاصی)</div>
      <div class="verdict-desc">
        برند <strong>voidclubs.ir</strong> باید منحصراً در قامت یک بوتیک استریت‌ویر زیرزمینی با درآپ‌های بسیار محدود (سالانه ۲ الی ۳ درآپ ۵۰ تا ۱۰۰ تایی) اداره شود. فروش فقط با قیمت پرمیوم و پیش‌فروش انجام شود تا ریسک سرمایه و اتلاف وقت کنکور به صفر برسد.
      </div>
    </div>
    <div class="verdict-score">
      <span class="num">۹.۱</span>
      <span class="lbl">امتیاز شورا از ۱۰</span>
    </div>
  </div>

  <h2>۱. ارزیابی گزینه‌های روی میز</h2>
  <div class="options-grid">
    <div class="option-card winner">
      <span class="badge badge-win">گزینه منتخب شورا</span>
      <div class="option-title">گزینه الف: درآپ‌های کپسولی لیمیتد</div>
      <div class="option-desc">
        سالانه ۲ تا ۳ درآپ فصلی خاص. تیراژ فقط ۵۰ تا ۱۰۰ عدد شماره‌گذاری شده. پیش‌فروش بدون انبارداری. مارجین سود ۶۵٪+.
      </div>
      <div class="option-score-row">امتیاز موزون: ۹.۱ از ۱۰ (موافقت قاطع)</div>
    </div>

    <div class="option-card">
      <span class="badge badge-lose">مردود با ریسک فاجعه</span>
      <div class="option-title">گزینه ب: پلتفرم باز مرچ و کریتورها</div>
      <div class="option-desc">
        فروشگاه همیشه‌فعال، همکاری با یوتیوبرها/گیمرها، تولید با Print-On-Demand. درگیری دائمی با لجستیک و مرجوعی.
      </div>
      <div class="option-score-row">امتیاز موزون: ۱.۴ از ۱۰ (مردود)</div>
    </div>

    <div class="option-card">
      <span class="badge badge-neutral">گزینه تلفیقی</span>
      <div class="option-title">گزینه ج: باشگاه ساب‌کالچر و عضویت</div>
      <div class="option-desc">
        فروش حق عضویت و کلاب اختصاصی. دسترسی به لینک‌های مخفی و رویدادهای تهران با کمترین درگیری با پارچه و دوخت.
      </div>
      <div class="option-score-row">امتیاز موزون: ۵.۸ از ۱۰ (تلفیق در درآپ)</div>
    </div>
  </div>

  <h2>۲. جدول آرا و تحلیل اعضای ۷ نفره شورا</h2>
  <table class="advisors-table">
    <thead>
      <tr>
        <th style="width: 18%;">مشاور و رکن</th>
        <th style="width: 10%;">رای و امتیاز</th>
        <th style="width: 42%;">استدلال محوری و نقل‌قول اختصاصی</th>
        <th style="width: 30%;">شرط یا هشدار کلیدی</th>
      </tr>
    </thead>
    <tbody>
      <tr>
        <td>
          <span class="seat-name">Jeff Bezos</span>
          <span class="seat-pillar">استراتژی و تصمیم‌گیری</span>
        </td>
        <td><strong>الف</strong> (۸/۱۰)<br><small>ضریب ۲</small></td>
        <td>
          گزینه الف یک <strong>«در دوطرفه» (Type 2 Decision)</strong> است. اگر درآپ جواب نداد، با زیان ناچیز برمی‌گردی. اما گزینه ب یک در یک‌طرفه خطرناک است که وقت و تمرکزت را می‌بلعد.
        </td>
        <td>تمرکز وسواس‌گونه روی کیفیت پارچه و رضایت ۵۰ خریدار اول، نه وسعت فروشگاه.</td>
      </tr>
      <tr>
        <td>
          <span class="seat-name">Paul Graham</span>
          <span class="seat-pillar">استارتاپ و عمق نیاز</span>
        </td>
        <td><strong>الف</strong> (۹/۱۰)<br><small>ضریب ۲</small></td>
        <td>
          <strong>«کارهایی بکن که مقیاس‌پذیر نیستند!»</strong> در استریت‌ویر، ۵۰ نفر خریدار متعصب و کشته‌مرده در کافه‌های تهران، هزار برابر ارزشمندتر از ۵۰۰۰ خریدار بی‌تفاوت پلتفرم‌های انبوه هستند.
        </td>
        <td>قبل از رسیدن به جاافتادگی شدید محصول (Product-Market Fit)، هرگز به فکر پلتفرم نباش.</td>
      </tr>
      <tr>
        <td>
          <span class="seat-name">Alex Hormozi</span>
          <span class="seat-pillar">آفر و قیمت‌گذاری</span>
        </td>
        <td><strong>الف</strong> (۹/۱۰)<br><small>ضریب ۳</small></td>
        <td>
          <strong>«حجم فروش بدون سود، فقط سروصدای گران‌قیمت است!»</strong> ذات استریت‌ویر با کمیابی زنده است. وقتی می‌گویی فقط ۵۰ عدد وجود دارد و دیگر تکرار نمی‌شود، حق داری بالاترین قیمت بازار را بگیری.
        </td>
        <td>مارجین سود هر هودی باید بالای ۶۵٪ باشد. اگر سود کم است، اصلاً وقتت را تلف نکن.</td>
      </tr>
      <tr>
        <td>
          <span class="seat-name">Gary Vaynerchuk</span>
          <span class="seat-pillar">مارکتینگ و توجه</span>
        </td>
        <td><strong>الف</strong> (۹/۱۰)<br><small>ضریب ۲</small></td>
        <td>
          برندهای اسطوره‌ای مثل Supreme با دراپ‌شیپینگ بالا نیامدند، با <strong>«فرهنگ و داستان‌سرایی»</strong> رشد کردند. تو یک دانش‌آموز ۱۶ ساله در بهترین مدرسه سمپاد تهرانی؛ فرآیند ساخت و دوخت را مستند کن!
        </td>
        <td>مدل درآپ باعث هایپ و هیجان در تلگرام/اینستاگرام می‌شود و خرید را به مسابقه تبدیل می‌کند.</td>
      </tr>
      <tr>
        <td>
          <span class="seat-name">Dan Martell</span>
          <span class="seat-pillar">زمان و تقویم موسس</span>
        </td>
        <td><strong>الف</strong> (۱۰/۱۰)<br><small>ضریب ۳</small></td>
        <td>
          <strong>«زمانت را پس بخر!»</strong> ارزشمندترین دارایی تو در ۱۶ سالگی، مغز و رتبه کنکورت است. گزینه ب (پلتفرم) یعنی بردگی در پشتیبانی دایرکت‌ها! گزینه الف را در ۲ هفته در سال جمع می‌کنی.
        </td>
        <td>خط قرمز: در ماه‌های امتحانات (دی، خرداد و سال کنکور) هیچ درآپی نباید ران شود.</td>
      </tr>
      <tr>
        <td>
          <span class="seat-name">Gino Wickman</span>
          <span class="seat-pillar">عملیات و سیستم EOS</span>
        </td>
        <td><strong>الف</strong> (۹/۱۰)<br><small>ضریب ۲</small></td>
        <td>
          <strong>«روی تمرکز اصلی (Core Focus) بمان.»</strong> اداره همزمان یک برند پوشاک و یک پلتفرم کریتور با صفر نیروی فول‌تایم، آشوب مطلق است. درآپ یک فرآیند ۵ مرحله‌ای شفاف و روتین دارد.
        </td>
        <td>تنها ۱ هدف ۹۰ روزه (Rock) بگذار: طراحی و اجرای اولین درآپ ۵۰ عددی.</td>
      </tr>
      <tr>
        <td>
          <span class="seat-name">Warren Buffett</span>
          <span class="seat-pillar">سرمایه و حاشیه امنیت</span>
        </td>
        <td><strong>الف</strong> (۹/۱۰)<br><small>ضریب ۲</small></td>
        <td>
          <strong>«قانون اول: پول از دست نده. قانون دوم: قانون اول را فراموش نکن!»</strong> گورستان خرده‌فروشی پوشاک، اجناس فروش‌نرفته زیر تخت است! با پیش‌فروش درآپ، سرمایه کار در گردش منفی است.
        </td>
        <td>مشتری اول پول می‌دهد، با پول او تولید می‌کنی و سود خالص را قبل از ارسال برمی‌داری.</td>
      </tr>
    </tbody>
  </table>

  <!-- PAGE BREAK FOR CLEAN EXECUTIVE SUMMARY -->
  <div class="page-break"></div>

  <h2>۳. نقاط برخورد اصلی و مناظره میان اعضای شورا (Cruxes)</h2>
  
  <div class="crux-box">
    <div class="crux-title">مناظره اول: قیمت‌گذاری نجومی در برابر تضمین کیفیت واقعی (هورموزی در برابر وارن بافت)</div>
    <div>
      <strong>الکس هورموزی</strong> اصرار داشت قیمت هودی‌های درآپ حداقل ۲ تا ۲.۵ میلیون تومان تعیین شود تا پرستیژ برند حفظ شود. <strong>وارن بافت</strong> پاسخ داد اگر هودی گران باشد اما بعد از دو بار شستشو دون‌دون شود، خریداران بعدی را از دست می‌دهی و موات برند نابود می‌شود.<br>
      <strong>نتیجه توافق شورا:</strong> قیمت پرمیوم تصویب شد، به این شرط که مشخصات پارچه در سایت شفاف باشد (پارچه دورس سه نخ پنبه ۳۵۰+ گرم واقعی، چاپ باکیفیت و دوخت صنعتی).
    </div>
  </div>

  <div class="crux-box">
    <div class="crux-title">مناظره دوم: حل معضل بسته‌بندی و ارسال بدون سوزاندن وقت مدرسه (دن مارتل در برابر جینو ویکمن)</div>
    <div>
      <strong>دن مارتل</strong> اخطار داد که بسته‌بندی ۵۰ جعبه، نوشتن آدرس‌ها و صف پست می‌تواند یک هفته کامل وقت آرمین را تلف کند. <strong>جینو ویکمن</strong> پیشنهاد ساخت یک چک‌لیست و فرآیند عملیاتی فشرده (SOP) داد.<br>
      <strong>نتیجه توافق شورا:</strong> روز بسته‌بندی باید در یک بعدازظهر جمعه خلاصه شود، جعبه‌ها و بسته‌بندی از قبل آماده باشد و ارسال یکجا با پیک/اسنپ‌باکس یا باجه مرکزی پست تحویل داده شود، یا به یک دوست/کمک‌کار واگذار گردد.
    </div>
  </div>

  <h2>۴. الحاقیه‌های مصوب شورا (Amendments)</h2>
  <div class="quote-box">
    <strong>الحاقیه ۱ (تلفیق با گزینه ج - پیشنهاد گری وی و هورموزی):</strong> به همراه هر سفارش درآپ، یک «کارت عضویت اختصاصی شماره‌گذاری‌شده» (مثلاً No. 01/50) با طراحی متالیک/تاریک ارسال شود. این کارت به خریدار حس تعلق به یک کلاب مخفی می‌دهد و دسترسی زودهنگام به درآپ بعدی را تضمین می‌کند.
  </div>
  <div class="quote-box">
    <strong>الحاقیه ۲ (سرمایه در گردش منفی - پیشنهاد وارن بافت و بزوس):</strong> سیستم سفارش‌گیری وب‌سایت voidclubs.ir به شکل پیش‌فروش ۱۰ روزه با شمارش معکوس باز شود. تولید دقیقاً به اندازه سفارشات ثبت‌شده (حداکثر سقف ۵۰ تا ۷۰ عدد) به کارگاه کرج/تهران سپرده شود.
  </div>

  <h2>۵. نقشه راه اجرایی ۹۰ روزه برای آرمین (Action Plan)</h2>
  <div class="action-steps">
    <div class="action-step-item">
      <span class="step-num">۱</span>
      <div>
        <strong>هفته ۱ تا ۳: نهایی‌کردن ۱ طرح تک و دوخت نمونه اولیه (Sample):</strong> فقط یک طرح آیکونیک (مثلاً هودی اورسایز مشکی با گرافیتی مینیمال و بروتالیست). یک نمونه از کارگاه تحویل بگیر و تست کیفیت و فیت تن‌خور را انجام بده.
      </div>
    </div>
    <div class="action-step-item">
      <span class="step-num">۲</span>
      <div>
        <strong>هفته ۴ تا ۶: محتوای ویدیویی و ساخت کشش در چنل/پیج:</strong> انتشار ویدیوهای کوتاه از تن‌خور، جنس سنگین پارچه، بسته اختصاصی و اعلام رسمی: «درآپ زمستانه: فقط ۵۰ عدد شماره‌گذاری‌شده».
      </div>
    </div>
    <div class="action-step-item">
      <span class="step-num">۳</span>
      <div>
        <strong>هفته ۷: باز شدن درگاه پیش‌فروش در voidclubs.ir:</strong> سایت برای ۴۸ ساعت فعال می‌شود تا ۵۰ عدد پر شود؛ بلافاصله درگاه بسته و وضعیت سایت به Sold Out تغییر می‌کند.
      </div>
    </div>
    <div class="action-step-item">
      <span class="step-num">۴</span>
      <div>
        <strong>هفته ۸ تا ۱۰: تولید کارگاهی و ماراتن ۴ ساعته ارسال:</strong> تحویل از کارگاه، یک بعدازظهر جمعه بسته‌بندی با کارت‌های کلاب، و ارسال کامل به مشتریان.
      </div>
    </div>
  </div>

  <div style="margin-top: 20px; padding-top: 10px; border-top: 1px solid #e4e4e7; font-size: 8pt; color: #71717a; text-align: center;">
    این سند بر اساس شبیه‌سازی دقیق آرای عمومی و چارچوب‌های فکری ۷ مشاور در پلتفرم Roast Room تولید شده است. · جلسه محرمانه استراتژیک voidclubs.ir
  </div>

</body>
</html>
"""

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html_content)

print("HTML written to:", HTML_PATH)

# Render PDF using Chromium headless
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
