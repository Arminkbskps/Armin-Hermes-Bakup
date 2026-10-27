import math

# 1. Test 3: Shared angle A, rays with B, D and E, C
# A at (50, 200).
# Ray 1 goes to top right (angle ~ 45 deg). Ray 2 goes horizontal right (angle 0 deg).
# Let's place A at (40, 180).
# Ray 1: angle = -40 deg.
# AD = 7 units -> let scale = 35 px/unit. AD length = 245 px.
# AB = 5 units -> length = 175 px.
# Ray 2: angle = 10 deg.
# AC = 7 units -> length = 245 px.
# AE = 4 units -> length = 140 px.

def make_test3_svg():
    ax, ay = 50, 150
    # Ray 1: angle -35 deg
    r1_rad = math.radians(-35)
    r2_rad = math.radians(20)
    
    # Scale: 38 px per unit
    s = 38
    bx = ax + 5 * s * math.cos(r1_rad)
    by = ay + 5 * s * math.sin(r1_rad)
    
    dx = ax + 7 * s * math.cos(r1_rad)
    dy = ay + 7 * s * math.sin(r1_rad)
    
    ex = ax + 4 * s * math.cos(r2_rad)
    ey = ay + 4 * s * math.sin(r2_rad)
    
    cx = ax + 7 * s * math.cos(r2_rad)
    cy = ay + 7 * s * math.sin(r2_rad)
    
    svg = f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 380 260" width="100%" height="220" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
      <defs>
        <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
          <path d="M 0 1.5 L 8 5 L 0 8.5 z" fill="#64748b" />
        </marker>
      </defs>
      <!-- Rays -->
      <line x1="{ax}" y1="{ay}" x2="{dx + 30*math.cos(r1_rad)}" y2="{dy + 30*math.sin(r1_rad)}" stroke="#475569" stroke-width="2" marker-end="url(#arrow)" />
      <line x1="{ax}" y1="{ay}" x2="{cx + 30*math.cos(r2_rad)}" y2="{cy + 30*math.sin(r2_rad)}" stroke="#475569" stroke-width="2" marker-end="url(#arrow)" />
      
      <!-- Triangle ABC (A-B-C-A): fill light blue -->
      <polygon points="{ax},{ay} {bx},{by} {cx},{cy}" fill="#0284c7" fill-opacity="0.12" stroke="#0284c7" stroke-width="2" stroke-dasharray="4,3" />
      
      <!-- Triangle ADE (A-D-E-A): fill light emerald -->
      <polygon points="{ax},{ay} {dx},{dy} {ex},{ey}" fill="#10b981" fill-opacity="0.12" stroke="#10b981" stroke-width="2" />
      
      <!-- Cross segments: BE and DC -->
      <line x1="{bx}" y1="{by}" x2="{cx}" y2="{cy}" stroke="#0284c7" stroke-width="2" />
      <line x1="{dx}" y1="{dy}" x2="{ex}" y2="{ey}" stroke="#10b981" stroke-width="2" />
      
      <!-- Points -->
      <circle cx="{ax}" cy="{ay}" r="4" fill="#0f172a" />
      <circle cx="{bx}" cy="{by}" r="4" fill="#0284c7" />
      <circle cx="{dx}" cy="{dy}" r="4" fill="#10b981" />
      <circle cx="{ex}" cy="{ey}" r="4" fill="#10b981" />
      <circle cx="{cx}" cy="{cy}" r="4" fill="#0284c7" />
      
      <!-- Labels -->
      <text x="{ax - 18}" y="{ay + 5}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">A</text>
      <text x="{bx - 5}" y="{by - 12}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0284c7">B</text>
      <text x="{dx + 5}" y="{dy - 10}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#10b981">D</text>
      <text x="{ex + 5}" y="{ey + 20}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#10b981">E</text>
      <text x="{cx + 10}" y="{cy + 18}" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0284c7">C</text>
      
      <!-- Segment lengths -->
      <text x="{(ax+bx)/2 - 14}" y="{(ay+by)/2 - 8}" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#0369a1">۵</text>
      <text x="{(bx+dx)/2 - 14}" y="{(by+dy)/2 - 8}" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#047857">۲</text>
      
      <text x="{(ax+ex)/2 + 2}" y="{(ay+ey)/2 + 18}" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#047857">۴</text>
      <text x="{(ex+cx)/2 + 2}" y="{(ey+cy)/2 + 18}" font-family="Vazirmatn, sans-serif" font-size="12" font-weight="bold" fill="#0369a1">۳</text>
      
      <!-- Legend -->
      <rect x="230" y="15" width="135" height="48" rx="6" fill="#ffffff" stroke="#cbd5e1" />
      <line x1="240" y1="28" x2="260" y2="28" stroke="#0284c7" stroke-width="2" />
      <text x="268" y="32" font-family="Vazirmatn, sans-serif" font-size="10.5" fill="#1e293b">مثلث ABC (ضلع ۵ و ۷)</text>
      <line x1="240" y1="46" x2="260" y2="46" stroke="#10b981" stroke-width="2" />
      <text x="268" y="50" font-family="Vazirmatn, sans-serif" font-size="10.5" fill="#1e293b">مثلث ADE (ضلع ۷ و ۴)</text>
    </svg>'''
    with open('/home/daytona/exam_work/trig_camscanner/assets/test3_geometry.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

# 2. Question 9: Acute triangle ABC with altitude AH
def make_q9_svg():
    # A at top (150, 40)
    # B at bottom left (40, 200)
    # H at (150, 200)
    # C at bottom right (300, 200)
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 230" width="100%" height="200" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
      <!-- Base line BC -->
      <line x1="40" y1="180" x2="310" y2="180" stroke="#0f172a" stroke-width="2" />
      <!-- Sides AB and AC -->
      <line x1="40" y1="180" x2="160" y2="40" stroke="#0f172a" stroke-width="2" />
      <line x1="310" y1="180" x2="160" y2="40" stroke="#0f172a" stroke-width="2" />
      
      <!-- Altitude AH (dashed) -->
      <line x1="160" y1="40" x2="160" y2="180" stroke="#e11d48" stroke-width="2" stroke-dasharray="5,4" />
      
      <!-- Right angle at H -->
      <path d="M 160 166 L 174 166 L 174 180" fill="none" stroke="#e11d48" stroke-width="1.5" />
      
      <!-- Angle C arc -->
      <path d="M 275 180 A 35 35 0 0 0 286 160" fill="none" stroke="#0284c7" stroke-width="2" />
      
      <!-- Points -->
      <circle cx="160" cy="40" r="4" fill="#0f172a" />
      <circle cx="40" cy="180" r="4" fill="#0f172a" />
      <circle cx="310" cy="180" r="4" fill="#0f172a" />
      <circle cx="160" cy="180" r="4" fill="#e11d48" />
      
      <!-- Labels -->
      <text x="155" y="28" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">A</text>
      <text x="22" y="185" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">B</text>
      <text x="320" y="185" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">C</text>
      <text x="154" y="202" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#e11d48">H</text>
      
      <!-- Values -->
      <text x="166" y="115" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="12" fill="#e11d48">ارتفاع AH = ؟</text>
      <text x="245" y="100" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="13" fill="#0284c7">AC = ۹۶</text>
      <text x="260" y="165" font-family="Vazirmatn, sans-serif" font-size="11" fill="#0284c7">زاویه C</text>
    </svg>'''
    with open('/home/daytona/exam_work/trig_camscanner/assets/q9_geometry.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

# 3. Question 10: Obtuse triangle ABC with altitude AH outside
def make_q10_svg():
    # H at (40, 180)
    # B at (130, 180)
    # C at (310, 180)
    # A at (40, 50) -> AH is vertical!
    svg = '''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 350 230" width="100%" height="200" style="background:#f8fafc; border-radius:8px; border:1px solid #e2e8f0;">
      <!-- Base extension HB (dashed) and BC (solid) -->
      <line x1="40" y1="180" x2="130" y2="180" stroke="#64748b" stroke-width="1.8" stroke-dasharray="4,4" />
      <line x1="130" y1="180" x2="310" y2="180" stroke="#0f172a" stroke-width="2.2" />
      
      <!-- Triangle ABC (A at (40, 50), B at (130, 180), C at (310, 180)) -->
      <polygon points="40,50 130,180 310,180" fill="#0284c7" fill-opacity="0.08" />
      <line x1="40" y1="50" x2="130" y2="180" stroke="#0f172a" stroke-width="2.2" />
      <line x1="40" y1="50" x2="310" y2="180" stroke="#0f172a" stroke-width="2.2" />
      
      <!-- Altitude AH (dashed vertical) -->
      <line x1="40" y1="50" x2="40" y2="180" stroke="#e11d48" stroke-width="2" stroke-dasharray="5,4" />
      
      <!-- Right angle at H -->
      <path d="M 40 166 L 54 166 L 54 180" fill="none" stroke="#e11d48" stroke-width="1.5" />
      
      <!-- Angle C arc -->
      <path d="M 275 180 A 35 35 0 0 0 286 163" fill="none" stroke="#0284c7" stroke-width="2" />
      
      <!-- Points -->
      <circle cx="40" cy="50" r="4" fill="#0f172a" />
      <circle cx="130" cy="180" r="4" fill="#0f172a" />
      <circle cx="310" cy="180" r="4" fill="#0f172a" />
      <circle cx="40" cy="180" r="4" fill="#e11d48" />
      
      <!-- Labels -->
      <text x="35" y="38" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">A</text>
      <text x="135" y="172" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">B</text>
      <text x="320" y="185" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#0f172a">C</text>
      <text x="32" y="202" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="14" fill="#e11d48">H</text>
      
      <!-- Dimensions -->
      <text x="10" y="120" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="12" fill="#e11d48">AH = ؟</text>
      <path d="M 40 205 L 310 205" stroke="#0369a1" stroke-width="1.5" />
      <text x="160" y="222" font-family="Vazirmatn, sans-serif" font-weight="bold" font-size="12" fill="#0369a1">CH = ۹</text>
      <text x="250" y="155" font-family="Vazirmatn, sans-serif" font-size="11" fill="#0284c7">sin C = ۵/۱۳</text>
    </svg>'''
    with open('/home/daytona/exam_work/trig_camscanner/assets/q10_geometry.svg', 'w', encoding='utf-8') as f:
        f.write(svg)

make_test3_svg()
make_q9_svg()
make_q10_svg()
print("SVGs generated successfully!")
