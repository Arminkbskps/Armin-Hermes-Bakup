import re

with open("/home/daytona/exam_work/geometry_camscanner/make_pdf.py", "r", encoding="utf-8") as f:
    code = f.read()

# Let's inspect where the cards are and insert explicit page breaks or adjust padding
# Specifically, we can adjust:
# font-size: 9pt
# line-height: 1.55
# margin-bottom on q-card: 10px
# padding on sol-box and q-body: 8px 12px

code = code.replace("font-size: 9.3pt;", "font-size: 8.9pt;")
code = code.replace("line-height: 1.62;", "line-height: 1.52;")
code = code.replace("margin: 12mm 12mm 14mm 12mm;", "margin: 10mm 12mm 10mm 12mm;")
code = code.replace("margin-bottom: 16px;", "margin-bottom: 10px;")
code = code.replace("padding: 10px 14px;", "padding: 7px 12px;")
code = code.replace("margin-bottom: 9px;", "margin-bottom: 6px;")
code = code.replace("padding: 7px 11px;", "padding: 5px 10px;")

# Add explicit page breaks before Question 8, Question 10, Question 11, Question 2
code = code.replace('<!-- Question 8 -->', '<div style="page-break-before: always;"></div>\n  <!-- Question 8 -->')
code = code.replace('<!-- SECTION 2 -->', '<div style="page-break-before: always;"></div>\n  <!-- SECTION 2 -->')
code = code.replace('<!-- Question 11 -->', '<div style="page-break-before: always;"></div>\n  <!-- Question 11 -->')
code = code.replace('<!-- SECTION 3 -->', '<div style="page-break-before: always;"></div>\n  <!-- SECTION 3 -->')

with open("/home/daytona/exam_work/geometry_camscanner/make_pdf.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Updated styling for 5-page exact layout.")
