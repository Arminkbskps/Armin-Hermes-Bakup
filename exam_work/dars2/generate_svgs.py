import os

OUTPUT_DIR = "/home/daytona/exam_work/dars2/assets"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 1. River Diagram
river_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 540 260" width="100%" height="220" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
  <defs>
    <linearGradient id="riverGrad" x1="0%" y1="0%" x2="0%" y2="100%">
      <stop offset="0%" stop-color="#bfdbfe" stop-opacity="0.6"/>
      <stop offset="50%" stop-color="#93c5fd" stop-opacity="0.8"/>
      <stop offset="100%" stop-color="#bfdbfe" stop-opacity="0.6"/>
    </linearGradient>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#0284c7" />
    </marker>
    <marker id="arrowRed" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#e11d48" />
    </marker>
  </defs>

  <!-- River Water -->
  <rect x="20" y="50" width="500" height="110" fill="url(#riverGrad)" rx="6"/>
  <!-- Water wave lines -->
  <path d="M 40,75 Q 80,68 120,75 T 200,75 T 280,75 T 360,75 T 440,75" fill="none" stroke="#60a5fa" stroke-width="2" opacity="0.6"/>
  <path d="M 60,115 Q 100,108 140,115 T 220,115 T 300,115 T 380,115 T 460,115" fill="none" stroke="#60a5fa" stroke-width="2" opacity="0.6"/>

  <!-- Bank Borders -->
  <line x1="20" y1="50" x2="520" y2="50" stroke="#047857" stroke-width="4" stroke-dasharray="8 4"/>
  <line x1="20" y1="160" x2="520" y2="160" stroke="#047857" stroke-width="4"/>
  
  <text x="35" y="42" font-family="Vazirmatn, sans-serif" font-size="12" fill="#047857" font-weight="bold">ساحل روبه‌رو (محل قرارگیری نقطه A)</text>
  <text x="35" y="180" font-family="Vazirmatn, sans-serif" font-size="12" fill="#047857" font-weight="bold">ساحل مبدأ (مسیر حرکت ناظر از C به B)</text>

  <!-- Points & Triangle -->
  <!-- Point A (top bank) -->
  <circle cx="100" cy="50" r="5" fill="#e11d48"/>
  <text x="92" y="35" font-family="Cambria, serif" font-size="16" font-weight="bold" fill="#e11d48">A</text>

  <!-- Point C (bottom bank, directly opposite A) -->
  <circle cx="100" cy="160" r="5" fill="#1e293b"/>
  <text x="88" y="185" font-family="Cambria, serif" font-size="16" font-weight="bold" fill="#1e293b">C</text>

  <!-- Point B (bottom bank, 200m to the right) -->
  <circle cx="420" cy="160" r="5" fill="#1e293b"/>
  <text x="425" y="185" font-family="Cambria, serif" font-size="16" font-weight="bold" fill="#1e293b">B</text>

  <!-- Right angle at C -->
  <path d="M 100,145 L 115,145 L 115,160" fill="none" stroke="#e11d48" stroke-width="2"/>
  <circle cx="107" cy="152" r="1.5" fill="#e11d48"/>

  <!-- Line AC (River Width, Unknown) -->
  <line x1="100" y1="50" x2="100" y2="160" stroke="#e11d48" stroke-width="2.5" stroke-dasharray="5 3"/>
  
  <!-- Dimension Label AC -->
  <line x1="65" y1="55" x2="65" y2="155" stroke="#e11d48" stroke-width="1.5" marker-start="url(#arrowRed)" marker-end="url(#arrowRed)"/>
  <text x="30" y="110" font-family="Vazirmatn, sans-serif" font-size="13" font-weight="bold" fill="#e11d48">عرض رودخانه d = ?</text>

  <!-- Line BC (Bank Distance = 200m) -->
  <line x1="100" y1="160" x2="420" y2="160" stroke="#0284c7" stroke-width="3"/>
  <line x1="105" y1="210" x2="415" y2="210" stroke="#0284c7" stroke-width="1.5" marker-start="url(#arrow)" marker-end="url(#arrow)"/>
  <text x="220" y="230" font-family="Vazirmatn, sans-serif" font-size="14" font-weight="bold" fill="#0284c7" text-anchor="middle">مسیر حرکت روی ساحل = ۲۰۰ متر (BC = 200 m)</text>

  <!-- Hypotenuse AB (Line of sight) -->
  <line x1="100" y1="50" x2="420" y2="160" stroke="#475569" stroke-width="2"/>
  
  <!-- Angle at B (20 deg) -->
  <path d="M 370,160 A 50 50 0 0 0 380,146" fill="none" stroke="#d97706" stroke-width="2.5"/>
  <text x="350" y="152" font-family="Vazirmatn, sans-serif" font-size="13" font-weight="bold" fill="#d97706">20°</text>
  <text x="435" y="145" font-family="Vazirmatn, sans-serif" font-size="11" fill="#475569">زاویه دید ناظر</text>
</svg>"""

with open(f"{OUTPUT_DIR}/river_geometry.svg", "w", encoding="utf-8") as f:
    f.write(river_svg)

# 2. Comprehensive Unit Circle with 4 Quadrants & HASTAK Mnemonic
circle_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 460 380" width="100%" height="280" style="background:#ffffff; border-radius:8px; border:1px solid #cbd5e1;">
  <defs>
    <marker id="axisArrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#334155" />
    </marker>
  </defs>

  <!-- Coordinate Axes -->
  <line x1="30" y1="190" x2="430" y2="190" stroke="#334155" stroke-width="1.8" marker-end="url(#axisArrow)"/>
  <line x1="230" y1="350" x2="230" y2="30" stroke="#334155" stroke-width="1.8" marker-end="url(#axisArrow)"/>
  
  <!-- Axis Labels -->
  <text x="435" y="195" font-family="Vazirmatn, sans-serif" font-size="13" font-weight="bold" fill="#1e293b">x (cos)</text>
  <text x="235" y="25" font-family="Vazirmatn, sans-serif" font-size="13" font-weight="bold" fill="#1e293b">y (sin)</text>
  <text x="218" y="205" font-family="Cambria, serif" font-size="12" fill="#64748b">O(0,0)</text>

  <!-- Unit Circle (R = 120) -->
  <circle cx="230" cy="190" r="120" fill="none" stroke="#2563eb" stroke-width="2.5"/>
  
  <!-- Boundary Points -->
  <circle cx="350" cy="190" r="3.5" fill="#2563eb"/>
  <text x="355" y="180" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#2563eb">(1, 0) | 0°</text>

  <circle cx="230" cy="70" r="3.5" fill="#2563eb"/>
  <text x="235" y="65" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#2563eb">(0, 1) | 90°</text>

  <circle cx="110" cy="190" r="3.5" fill="#2563eb"/>
  <text x="50" y="180" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#2563eb">180° | (-1, 0)</text>

  <circle cx="230" cy="310" r="3.5" fill="#2563eb"/>
  <text x="235" y="328" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#2563eb">(0, -1) | 270°</text>

  <!-- Quadrant Badges -->
  <!-- Quadrant I -->
  <rect x="260" y="90" width="135" height="75" rx="6" fill="#f0fdf4" stroke="#86efac" stroke-width="1.2"/>
  <text x="270" y="110" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#166534">ربع اول (0° تا 90°)</text>
  <text x="270" y="128" font-family="Vazirmatn, sans-serif" font-size="11" fill="#15803d">کد هستک: «هـ» = همه مثبت</text>
  <text x="270" y="145" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#166534">sin&gt;0, cos&gt;0, tan&gt;0, cot&gt;0</text>

  <!-- Quadrant II -->
  <rect x="65" y="90" width="140" height="75" rx="6" fill="#eff6ff" stroke="#93c5fd" stroke-width="1.2"/>
  <text x="75" y="110" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#1e40af">ربع دوم (90° تا 180°)</text>
  <text x="75" y="128" font-family="Vazirmatn, sans-serif" font-size="11" fill="#1d4ed8">کد هستک: «س» = فقط سینوس +</text>
  <text x="75" y="145" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#1e40af">sin&gt;0 | cos&lt;0, tan&lt;0, cot&lt;0</text>

  <!-- Quadrant III -->
  <rect x="65" y="215" width="140" height="75" rx="6" fill="#fefce8" stroke="#fde047" stroke-width="1.2"/>
  <text x="75" y="235" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#854d0e">ربع سوم (180° تا 270°)</text>
  <text x="75" y="253" font-family="Vazirmatn, sans-serif" font-size="11" fill="#a16207">کد هستک: «ت» = تانژانت و کتانژانت +</text>
  <text x="75" y="270" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#854d0e">tan&gt;0, cot&gt;0 | sin&lt;0, cos&lt;0</text>

  <!-- Quadrant IV -->
  <rect x="260" y="215" width="135" height="75" rx="6" fill="#fdf2f8" stroke="#f472b6" stroke-width="1.2"/>
  <text x="270" y="235" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#9d174d">ربع چهارم (270° تا 360°)</text>
  <text x="270" y="253" font-family="Vazirmatn, sans-serif" font-size="11" fill="#be185d">کد هستک: «ک» = فقط کسینوس +</text>
  <text x="270" y="270" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#9d174d">cos&gt;0 | sin&lt;0, tan&lt;0, cot&lt;0</text>
</svg>"""

with open(f"{OUTPUT_DIR}/unit_circle_overview.svg", "w", encoding="utf-8") as f:
    f.write(circle_svg)

# 3. Angle 210 degrees and Point P Diagram
angle210_svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 320" width="100%" height="240" style="background:#ffffff; border-radius:8px; border:1px solid #cbd5e1;">
  <defs>
    <marker id="axisArrow2" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#475569" />
    </marker>
  </defs>

  <!-- Axes -->
  <line x1="20" y1="160" x2="360" y2="160" stroke="#64748b" stroke-width="1.5" marker-end="url(#axisArrow2)"/>
  <line x1="190" y1="300" x2="190" y2="20" stroke="#64748b" stroke-width="1.5" marker-end="url(#axisArrow2)"/>
  <text x="365" y="165" font-family="Cambria, serif" font-size="13" font-weight="bold" fill="#334155">x</text>
  <text x="195" y="18" font-family="Cambria, serif" font-size="13" font-weight="bold" fill="#334155">y</text>

  <!-- Unit Circle (R = 100) -->
  <circle cx="190" cy="160" r="100" fill="none" stroke="#cbd5e1" stroke-width="2"/>

  <!-- Angle 210: cos 210 = -sqrt(3)/2 = -0.866 (dx = -86.6), sin 210 = -1/2 = -0.5 (dy = 50) -->
  <!-- Target Point P: cx = 190 - 86.6 = 103.4, cy = 160 + 50 = 210 -->
  <!-- Ray from Origin to P -->
  <line x1="190" y1="160" x2="90" y2="218" stroke="#0284c7" stroke-width="3"/>

  <!-- Arc 210 degrees (from (290, 160) to (103.4, 210)) -->
  <path d="M 230,160 A 40 40 0 1 1 155,180" fill="none" stroke="#e11d48" stroke-width="2.5"/>
  <text x="180" y="125" font-family="Vazirmatn, sans-serif" font-size="13" font-weight="bold" fill="#e11d48">210°</text>

  <!-- Reference Angle 30 deg between negative x-axis and ray -->
  <path d="M 150,160 A 40 40 0 0 0 155,180" fill="none" stroke="#d97706" stroke-width="2"/>
  <text x="135" y="175" font-family="Vazirmatn, sans-serif" font-size="11" font-weight="bold" fill="#d97706">30°</text>

  <!-- Projection Dashes -->
  <line x1="103.4" y1="210" x2="103.4" y2="160" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 3"/>
  <line x1="103.4" y1="210" x2="190" y2="210" stroke="#94a3b8" stroke-width="1.5" stroke-dasharray="4 3"/>

  <!-- Coordinates on Axes -->
  <circle cx="103.4" cy="160" r="3" fill="#0284c7"/>
  <text x="75" y="150" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#0284c7">-&radic;3/2</text>

  <circle cx="190" cy="210" r="3" fill="#0284c7"/>
  <text x="200" y="215" font-family="Cambria, serif" font-size="11" font-weight="bold" fill="#0284c7">-1/2</text>

  <!-- Point P -->
  <circle cx="103.4" cy="210" r="5" fill="#e11d48"/>
  <text x="20" y="235" font-family="Cambria, serif" font-size="13" font-weight="bold" fill="#e11d48">P(-&radic;3/2, -1/2)</text>
</svg>"""

with open(f"{OUTPUT_DIR}/angle_210_geometry.svg", "w", encoding="utf-8") as f:
    f.write(angle210_svg)

print("Generated all SVGs successfully!")
