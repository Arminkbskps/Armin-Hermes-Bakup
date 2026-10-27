import math

# 1. Question 8 SVG (Zigzag Thales on Angle)
def make_q8_svg():
    # O at (40, 200)
    # Ox is horizontal to right
    # Oy is at angle -35 deg
    ox, oy = 40, 200
    angle_y = math.radians(-32)
    
    # OA = 3, OC = 3*sqrt(3) ~= 5.196, OE = 9
    # Scale: 30 px per unit
    s = 28
    
    ax = ox + 3 * s
    ay = oy
    
    cx = ox + 3 * math.sqrt(3) * s
    cy = oy
    
    ex = ox + 9 * s
    ey = oy
    
    # B is on Oy such that BA is vertical (since BA perp Ox)
    # So bx = ax = 40 + 3*s
    bx = ax
    # On Oy: (bx - ox) / cos(angle_y) * sin(angle_y) + oy
    by = oy + (bx - ox) * math.tan(angle_y)
    
    # D is on Oy such that DC is vertical (since DC perp Ox)
    dx = cx
    dy = oy + (dx - ox) * math.tan(angle_y)
    
    # Ray Ox end
    rx_end = ex + 45
    # Ray Oy end
    ry_len = (dx - ox) / math.cos(angle_y) + 40
    ry_end_x = ox + ry_len * math.cos(angle_y)
    ry_end_y = oy + ry_len * math.sin(angle_y)
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 250" width="100%" height="220" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#475569" />
        </marker>
      </defs>
      
      <!-- Rays Ox and Oy -->
      <line x1="{ox}" y1="{oy}" x2="{rx_end}" y2="{oy}" stroke="#1e293b" stroke-width="2.2" marker-end="url(#arrow)" />
      <line x1="{ox}" y1="{oy}" x2="{ry_end_x}" y2="{ry_end_y}" stroke="#1e293b" stroke-width="2.2" marker-end="url(#arrow)" />
      
      <!-- Vertical segments BA and DC (perpendicular to Ox) -->
      <line x1="{bx}" y1="{by}" x2="{ax}" y2="{ay}" stroke="#0284c7" stroke-width="2.2" />
      <line x1="{dx}" y1="{dy}" x2="{cx}" y2="{cy}" stroke="#0284c7" stroke-width="2.2" />
      
      <!-- Perpendicular symbols -->
      <path d="M {ax} {ay-14} L {ax+14} {ay-14} L {ax+14} {ay}" fill="none" stroke="#0284c7" stroke-width="1.5" />
      <path d="M {cx} {cy-14} L {cx+14} {cy-14} L {cx+14} {cy}" fill="none" stroke="#0284c7" stroke-width="1.5" />
      
      <!-- Zigzag lines: BC and DE (parallel) -->
      <line x1="{bx}" y1="{by}" x2="{cx}" y2="{cy}" stroke="#e11d48" stroke-width="2.2" />
      <line x1="{dx}" y1="{dy}" x2="{ex}" y2="{ey}" stroke="#e11d48" stroke-width="2.2" stroke-dasharray="6,4" />
      
      <!-- Parallel indicator arrows on BC and DE -->
      <polygon points="{(bx+cx)/2-3},{(by+cy)/2+6} {(bx+cx)/2+5},{(by+cy)/2} {(bx+cx)/2-3},{(by+cy)/2-6}" fill="#e11d48" />
      <polygon points="{(dx+ex)/2-3},{(dy+ey)/2+6} {(dx+ex)/2+5},{(dy+ey)/2} {(dx+ex)/2-3},{(dy+ey)/2-6}" fill="#e11d48" />
      
      <!-- Points -->
      <circle cx="{ox}" cy="{oy}" r="4" fill="#0f172a" />
      <circle cx="{ax}" cy="{ay}" r="4" fill="#0284c7" />
      <circle cx="{cx}" cy="{cy}" r="4" fill="#0284c7" />
      <circle cx="{ex}" cy="{ey}" r="4" fill="#0f172a" />
      <circle cx="{bx}" cy="{by}" r="4" fill="#e11d48" />
      <circle cx="{dx}" cy="{dy}" r="4" fill="#e11d48" />
      
      <!-- Labels -->
      <text x="{ox - 18}" y="{oy + 6}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">O</text>
      <text x="{rx_end + 8}" y="{oy + 5}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#475569">x</text>
      <text x="{ry_end_x + 8}" y="{ry_end_y - 2}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#475569">y</text>
      
      <text x="{ax - 4}" y="{ay + 20}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0284c7">A</text>
      <text x="{cx - 4}" y="{cy + 20}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0284c7">C</text>
      <text x="{ex - 4}" y="{ey + 20}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">E</text>
      
      <text x="{bx - 5}" y="{by - 10}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#e11d48">B</text>
      <text x="{dx - 5}" y="{dy - 10}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#e11d48">D</text>
      
      <!-- Dimensions bracket/text -->
      <text x="{(ox+ax)/2 - 5}" y="{oy + 38}" font-family="Vazirmatn, sans-serif" font-size="11" font-weight="bold" fill="#0369a1">OA = ۳</text>
      <text x="{(ox+ex)/2 - 5}" y="{oy - 10}" font-family="Vazirmatn, sans-serif" font-size="11" font-weight="bold" fill="#0f172a">OE = ۹</text>
      <text x="{(ax+cx)/2 - 5}" y="{oy - 10}" font-family="Vazirmatn, sans-serif" font-size="11" font-weight="bold" fill="#e11d48">OC = ؟</text>
      
      <!-- Legend box -->
      <rect x="235" y="15" width="130" height="56" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="245" y="32" font-family="Vazirmatn, sans-serif" font-size="10.5" fill="#0369a1">BA ⊥ Ox , DC ⊥ Ox</text>
      <text x="245" y="48" font-family="Vazirmatn, sans-serif" font-size="10.5" fill="#e11d48">BC ∥ DE (قضیه تالس)</text>
      <text x="245" y="64" font-family="Vazirmatn, sans-serif" font-size="10.5" font-weight="bold" fill="#166534">OC² = OA · OE</text>
    </svg>'''
    with open('/home/daytona/exam_work/geometry_camscanner/assets/q8_geometry.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

# 2. Question 10 SVG (Three Squares: 3, 4, 5)
def make_q10_svg():
    # Base line at y = 200
    # Squares: 3, 4, 5 units
    # Scale: s = 24 px per unit
    # Base total: 3 + 4 + 5 = 12 units = 288 px
    # Left margin: 40 px
    ox, oy = 45, 190
    s = 24
    
    # Square 1: (3, 3)
    x0 = ox
    x1 = ox + 3 * s
    # Square 2: (4, 4)
    x2 = x1 + 4 * s
    # Square 3: (5, 5)
    x3 = x2 + 5 * s
    
    y_base = oy
    y_sq1_top = y_base - 3 * s
    y_sq2_top = y_base - 4 * s
    y_sq3_top = y_base - 5 * s
    
    # Line AB: A is (x0, y_base), B is (x3, y_sq3_top)
    # Line equation: y - y_base = (y_sq3_top - y_base)/(x3 - x0) * (x - x0)
    # Slope m = (-5*s) / (12*s) = -5/12
    # At x = x2 (x = x0 + 7*s):
    # y_P = y_base - (5/12) * 7 * s = y_base - (35/12) * s
    y_P = y_base - (35.0 / 12.0) * s
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 240" width="100%" height="210" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
      <!-- Base Line AC -->
      <line x1="{x0 - 15}" y1="{y_base}" x2="{x3 + 20}" y2="{y_base}" stroke="#0f172a" stroke-width="2.2" />
      
      <!-- Square 1 (3x3): Light Sky Fill -->
      <rect x="{x0}" y="{y_sq1_top}" width="{3*s}" height="{3*s}" fill="#e0f2fe" fill-opacity="0.6" stroke="#0284c7" stroke-width="1.8" />
      <!-- Square 2 (4x4): Light Amber Fill -->
      <rect x="{x1}" y="{y_sq2_top}" width="{4*s}" height="{4*s}" fill="#fef3c7" fill-opacity="0.6" stroke="#d97706" stroke-width="1.8" />
      <!-- Square 3 (5x5): Light Emerald Fill -->
      <rect x="{x2}" y="{y_sq3_top}" width="{5*s}" height="{5*s}" fill="#dcfce7" fill-opacity="0.6" stroke="#16a34a" stroke-width="1.8" />
      
      <!-- Vertical edge KD (height 5 units) -->
      <line x1="{x2}" y1="{y_sq3_top}" x2="{x2}" y2="{y_base}" stroke="#0f172a" stroke-width="2.5" />
      
      <!-- Diagonal line AB (from A to B) -->
      <line x1="{x0}" y1="{y_base}" x2="{x3}" y2="{y_sq3_top}" stroke="#e11d48" stroke-width="2.2" />
      
      <!-- Intersection Point P -->
      <circle cx="{x2}" cy="{y_P}" r="4.5" fill="#e11d48" />
      
      <!-- Important Vertices -->
      <circle cx="{x0}" cy="{y_base}" r="4" fill="#0f172a" />
      <circle cx="{x2}" cy="{y_base}" r="4" fill="#0f172a" />
      <circle cx="{x3}" cy="{y_base}" r="4" fill="#0f172a" />
      <circle cx="{x2}" cy="{y_sq3_top}" r="4" fill="#0f172a" />
      <circle cx="{x3}" cy="{y_sq3_top}" r="4" fill="#0f172a" />
      
      <!-- Labels -->
      <text x="{x0 - 15}" y="{y_base + 18}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">A</text>
      <text x="{x2 - 5}" y="{y_base + 18}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">D</text>
      <text x="{x3 + 6}" y="{y_base + 18}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">C</text>
      <text x="{x2 - 16}" y="{y_sq3_top - 6}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">K</text>
      <text x="{x3 + 6}" y="{y_sq3_top - 6}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">B</text>
      <text x="{x2 + 8}" y="{y_P + 4}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#e11d48">P</text>
      
      <!-- Side lengths inside squares -->
      <text x="{(x0+x1)/2 - 5}" y="{y_base - 1.5*s + 4}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="12" fill="#0369a1">۳</text>
      <text x="{(x1+x2)/2 - 5}" y="{y_base - 2*s + 4}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="12" fill="#b45309">۴</text>
      <text x="{(x2+x3)/2 - 5}" y="{y_base - 2.5*s + 4}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="12" fill="#15803d">۵</text>
      
      <!-- Dimension KP indicator -->
      <path d="M {x2-8} {y_sq3_top} L {x2-8} {y_P}" stroke="#e11d48" stroke-width="1.8" />
      <line x1="{x2-12}" y1="{y_sq3_top}" x2="{x2-4}" y2="{y_sq3_top}" stroke="#e11d48" stroke-width="1.5" />
      <line x1="{x2-12}" y1="{y_P}" x2="{x2-4}" y2="{y_P}" stroke="#e11d48" stroke-width="1.5" />
      <text x="{x2 - 32}" y="{(y_sq3_top + y_P)/2 + 4}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="10.5" fill="#e11d48">KP = ؟</text>
      
      <!-- Dimension PD indicator -->
      <path d="M {x2-8} {y_P} L {x2-8} {y_base}" stroke="#64748b" stroke-width="1.2" stroke-dasharray="3,3" />
      <text x="{x2 - 38}" y="{(y_P + y_base)/2 + 4}" font-family="Vazirmatn, sans-serif" font-size="9.5" fill="#64748b">PD=۳۵/۱۲</text>
    </svg>'''
    with open('/home/daytona/exam_work/geometry_camscanner/assets/q10_geometry.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

# 3. Question 11 SVG (Trapezoid ABCD with Median to Base)
def make_q11_svg():
    # Base CD on bottom: D at (50, 180), C at (310, 180)
    # Upper base AB: A at (110, 70), B at (250, 70)
    # M is midpoint of CD -> M at (180, 180)
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 230" width="100%" height="200" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
      <!-- Trapezoid base ABCD -->
      <polygon points="110,70 250,70 310,180 50,180" fill="#f1f5f9" stroke="#0f172a" stroke-width="2" />
      
      <!-- Triangle BCD: dashed outline -->
      <polygon points="250,70 310,180 50,180" fill="#0284c7" fill-opacity="0.1" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="5,4" />
      
      <!-- Triangle ADM: fill emerald -->
      <polygon points="110,70 50,180 180,180" fill="#10b981" fill-opacity="0.25" stroke="#059669" stroke-width="2.2" />
      
      <!-- Line AC (diagonal) -->
      <line x1="110" y1="70" x2="310" y2="180" stroke="#64748b" stroke-width="1.5" stroke-dasharray="4,3" />
      
      <!-- Median AM -->
      <line x1="110" y1="70" x2="180" y2="180" stroke="#059669" stroke-width="2.2" />
      
      <!-- Height h (from B to CD and A to CD) -->
      <line x1="250" y1="70" x2="250" y2="180" stroke="#e11d48" stroke-width="1.5" stroke-dasharray="3,3" />
      <path d="M 250 170 L 260 170 L 260 180" fill="none" stroke="#e11d48" stroke-width="1.2" />
      <text x="254" y="130" font-family="Vazirmatn, sans-serif" font-size="11" font-weight="bold" fill="#e11d48">ارتفاع h</text>
      
      <!-- Points -->
      <circle cx="110" cy="70" r="4" fill="#0f172a" />
      <circle cx="250" cy="70" r="4" fill="#0f172a" />
      <circle cx="50" cy="180" r="4" fill="#0f172a" />
      <circle cx="310" cy="180" r="4" fill="#0f172a" />
      <circle cx="180" cy="180" r="4.5" fill="#059669" />
      
      <!-- Equal tick marks on DM and MC -->
      <line x1="110" y1="176" x2="110" y2="184" stroke="#059669" stroke-width="2" />
      <line x1="114" y1="176" x2="114" y2="184" stroke="#059669" stroke-width="2" />
      <line x1="240" y1="176" x2="240" y2="184" stroke="#059669" stroke-width="2" />
      <line x1="244" y1="176" x2="244" y2="184" stroke="#059669" stroke-width="2" />
      
      <!-- Labels -->
      <text x="102" y="58" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">A</text>
      <text x="248" y="58" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">B</text>
      <text x="35" y="195" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">D</text>
      <text x="318" y="195" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">C</text>
      <text x="175" y="200" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#059669">M</text>
      
      <!-- Area Notes -->
      <text x="90" y="150" font-family="Vazirmatn, sans-serif" font-size="11" font-weight="bold" fill="#065f46">S(ADM) = ۱۲</text>
      <text x="180" y="110" font-family="Vazirmatn, sans-serif" font-size="10.5" fill="#0369a1">S(BCD) = ۲۴</text>
    </svg>'''
    with open('/home/daytona/exam_work/geometry_camscanner/assets/q11_geometry.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

# 4. Question 2 SVG (Acute Triangle Orthocenter Inside)
def make_q2_svg():
    # Acute triangle ABC with altitudes meeting at H inside
    # A at (180, 40), B at (60, 180), C at (300, 180)
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 230" width="100%" height="200" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
      <!-- Triangle ABC -->
      <polygon points="180,40 60,180 300,180" fill="#f8fafc" stroke="#0f172a" stroke-width="2.2" />
      
      <!-- Altitude 1: from A to BC (vertical) -->
      <line x1="180" y1="40" x2="180" y2="180" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="4,3" />
      <!-- Altitude 2: from B to AC -->
      <!-- AC line: (180,40) to (300,180). dx=120, dy=140. Slope = 7/6. Normal slope = -6/7 -->
      <!-- Foot of altitude from B(60, 180) to AC: approx (233, 102) -->
      <line x1="60" y1="180" x2="233" y2="102" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="4,3" />
      <!-- Altitude 3: from C to AB -->
      <!-- Foot from C(300, 180) to AB: approx (127, 102) -->
      <line x1="300" y1="180" x2="127" y2="102" stroke="#0284c7" stroke-width="1.8" stroke-dasharray="4,3" />
      
      <!-- Orthocenter H: intersection at (180, 140) -->
      <circle cx="180" cy="140" r="5" fill="#e11d48" />
      <text x="190" y="142" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="12" fill="#e11d48">H (همرسی ارتفاع‌ها درون مثلث)</text>
      
      <!-- Points -->
      <circle cx="180" cy="40" r="4" fill="#0f172a" />
      <circle cx="60" cy="180" r="4" fill="#0f172a" />
      <circle cx="300" cy="180" r="4" fill="#0f172a" />
      
      <!-- Labels -->
      <text x="175" y="28" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">A (زاویه حاده)</text>
      <text x="35" y="195" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">B = ۳x − ۱۵°</text>
      <text x="245" y="195" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0f172a">C = ۱۷۵° − ۴x</text>
      <text x="145" y="60" font-family="Vazirmatn, sans-serif" font-size="11" fill="#0369a1">A = x + ۲۰°</text>
      
      <!-- Note box -->
      <rect x="15" y="15" width="145" height="42" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <text x="22" y="32" font-family="Vazirmatn, sans-serif" font-size="10" font-weight="bold" fill="#166534">شرط همرسی درون مثلث:</text>
      <text x="22" y="48" font-family="Vazirmatn, sans-serif" font-size="10" fill="#0f172a">هر سه زاویه حاده (&lt; ۹۰°)</text>
    </svg>'''
    with open('/home/daytona/exam_work/geometry_camscanner/assets/q2_geometry.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

make_q8_svg()
make_q10_svg()
make_q11_svg()
make_q2_svg()
print("All 4 geometry SVGs created successfully!")
