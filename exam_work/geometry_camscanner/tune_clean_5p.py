with open("/home/daytona/exam_work/geometry_camscanner/generate_booklet.py", "r", encoding="utf-8") as f:
    code = f.read()

# Remove the page break before Section 3
code = code.replace('<div style="page-break-before: always;"></div>\n\n  <!-- SECTION 3 -->', '<!-- SECTION 3 -->')

# Make the page break happen right before Section 3 + Question 2 container
old_sec3 = """  <!-- SECTION 3 -->
  <div class="section-bar">
    <h2>بخش ۳: همرسی خطوط ویژه و نامساوی مثلثاتی (صفحه ۳ آزمون)</h2>
    <span class="section-badge">۱ سوال</span>
  </div>

  <!-- Question 2 -->"""

new_sec3 = """  <div style="page-break-before: always;"></div>
  <!-- SECTION 3 -->
  <div class="section-bar" style="margin-top: 0;">
    <h2>بخش ۳: همرسی خطوط ویژه و نامساوی مثلثاتی (صفحه ۳ آزمون)</h2>
    <span class="section-badge">۱ سوال</span>
  </div>

  <!-- Question 2 -->"""

code = code.replace(old_sec3, new_sec3)

# Make Question 2 slightly more compact so it fits within 1 page (P5):
# SVG height 135px instead of 155px
code = code.replace('height="155"', 'height="135"')
code = code.replace('viewBox="0 0 380 230"', 'viewBox="0 0 380 205"')

with open("/home/daytona/exam_work/geometry_camscanner/generate_booklet.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated script.")
