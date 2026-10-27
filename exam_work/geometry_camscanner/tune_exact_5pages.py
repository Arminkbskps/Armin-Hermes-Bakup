with open("/home/daytona/exam_work/geometry_camscanner/make_pdf.py", "r", encoding="utf-8") as f:
    code = f.read()

# 1. Compact header and key table
code = code.replace(".header-banner {", """.header-banner {
      border: 1.5px solid #0f172a;
      border-radius: 8px;
      padding: 8px 14px;
      margin-bottom: 8px;
      background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
      display: flex;
      justify-content: space-between;
      align-items: center;
    }
    .header-banner-old {""")

code = code.replace(".summary-table th, .summary-table td {", """.summary-table th, .summary-table td {
      border: 1px solid #cbd5e1;
      padding: 3px 5px;
      text-align: center;
      font-size: 8pt;
    }
    .summary-table-old {""")

code = code.replace("height=\"220\"", "height=\"165\"")
code = code.replace("height=\"210\"", "height=\"160\"")
code = code.replace("height=\"200\"", "height=\"155\"")

# Ensure Section 3 title stays WITH Question 2
code = code.replace('<div style="page-break-before: always;"></div>\n  <!-- SECTION 3 -->', '')
code = code.replace('<!-- Question 2 -->', '<div style="page-break-before: always;"></div>\n  <!-- SECTION 3 -->\n  <div class="section-bar">\n    <h2>بخش ۳: همرسی خطوط ویژه و نامساوی مثلثاتی (صفحه ۳ آزمون)</h2>\n    <span class="section-badge">۱ سوال</span>\n  </div>\n  <!-- Question 2 -->')

# In Question 2, make steps a bit tighter
code = code.replace("margin-bottom: 8px;\n      padding-right: 10px;", "margin-bottom: 5px;\n      padding-right: 8px;")
code = code.replace("margin: 8px 0;\n      padding: 7px 12px;", "margin: 4px 0;\n      padding: 4px 8px;")

with open("/home/daytona/exam_work/geometry_camscanner/make_pdf.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Tuning applied.")
