import math

def make_trig_circle_svg():
    # 400x400 SVG of unit circle with quadrants, axes, angle theta, P(cos, sin), T(1, tan)
    svg = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="-220 -220 440 440" width="360" height="360" style="background:#fff; font-family:'Vazirmatn', sans-serif;">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#3f3f46"/>
    </marker>
    <marker id="arrow-green" viewBox="0 0 10 10" refX="5" refY="5" markerWidth="6" markerHeight="6" orient="auto-start-reverse">
      <path d="M 0 1.5 L 10 5 L 0 8.5 z" fill="#16a34a"/>
    </marker>
  </defs>

  <!-- Axes -->
  <line x1="-200" y1="0" x2="200" y2="0" stroke="#71717a" stroke-width="1.5" marker-end="url(#arrow)"/>
  <line x1="0" y1="200" x2="0" y2="-200" stroke="#71717a" stroke-width="1.5" marker-end="url(#arrow)"/>

  <!-- Axis labels -->
  <text x="180" y="20" font-size="13" font-weight="bold" fill="#18181b">x (cos)</text>
  <text x="10" y="-185" font-size="13" font-weight="bold" fill="#18181b">y (sin)</text>
  <text x="-12" y="15" font-size="12" fill="#71717a">O</text>

  <!-- Circle R=140 -->
  <circle cx="0" cy="0" r="140" fill="none" stroke="#2563eb" stroke-width="2"/>

  <!-- Tangent axis at x=140 -->
  <line x1="140" y1="200" x2="140" y2="-200" stroke="#dc2626" stroke-width="1.5" stroke-dasharray="4 3" marker-end="url(#arrow)"/>
  <text x="145" y="-185" font-size="12" font-weight="bold" fill="#dc2626">محور تانژانت (x=1)</text>

  <!-- Quadrants labels -->
  <text x="60" y="-70" font-size="14" font-weight="bold" fill="#9333ea">ناحیه اول (I)</text>
  <text x="40" y="-50" font-size="11" fill="#6b7280">sin&gt;0 , cos&gt;0</text>

  <text x="-120" y="-70" font-size="14" font-weight="bold" fill="#9333ea">ناحیه دوم (II)</text>
  <text x="-135" y="-50" font-size="11" fill="#6b7280">sin&gt;0 , cos&lt;0</text>

  <text x="-125" y="80" font-size="14" font-weight="bold" fill="#9333ea">ناحیه سوم (III)</text>
  <text x="-135" y="100" font-size="11" fill="#6b7280">sin&lt;0 , cos&lt;0</text>

  <text x="50" y="80" font-size="14" font-weight="bold" fill="#9333ea">ناحیه چهارم (IV)</text>
  <text x="40" y="100" font-size="11" fill="#6b7280">sin&lt;0 , cos&gt;0</text>

  <!-- Angle theta = 50 deg -->
  <!-- 50 deg: cos = 0.6428 -> x = 90, sin = 0.766 -> y = -107.2 -->
  <line x1="0" y1="0" x2="140" y2="-166.8" stroke="#16a34a" stroke-width="2"/>
  <circle cx="90" cy="-107.2" r="4.5" fill="#16a34a"/>
  <text x="65" y="-115" font-size="12" font-weight="bold" fill="#16a34a">P(cos θ, sin θ)</text>

  <!-- Dashed lines to axes -->
  <line x1="90" y1="0" x2="90" y2="-107.2" stroke="#16a34a" stroke-dasharray="3 3"/>
  <line x1="0" y1="-107.2" x2="90" y2="-107.2" stroke="#16a34a" stroke-dasharray="3 3"/>
  
  <text x="85" y="15" font-size="11" font-weight="bold" fill="#16a34a">cos θ</text>
  <text x="-35" y="-103" font-size="11" font-weight="bold" fill="#16a34a">sin θ</text>

  <!-- Tangent intersection T(140, -166.8) -->
  <circle cx="140" cy="-166.8" r="4.5" fill="#dc2626"/>
  <text x="148" y="-160" font-size="11" font-weight="bold" fill="#dc2626">T(1, tan θ)</text>

  <!-- Arc for theta -->
  <path d="M 40 0 A 40 40 0 0 0 25.7 -30.6" fill="none" stroke="#ea580c" stroke-width="1.8"/>
  <text x="35" y="-12" font-size="12" font-weight="bold" fill="#ea580c">θ</text>
</svg>"""
    return svg

with open("/home/daytona/exam_work/trig/circle.svg", "w", encoding="utf-8") as f:
    f.write(make_trig_circle_svg())

print("SVG created successfully!")
