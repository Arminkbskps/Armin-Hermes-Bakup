with open("/home/daytona/exam_work/geometry_camscanner/generate_booklet.py", "r", encoding="utf-8") as f:
    code = f.read()

# In Question 2, replace the SVG placeholder with empty or a compact badge
code = code.replace('<div style="display:flex; justify-content:center; margin:8px 0;">\n        __Q2_SVG__\n      </div>', '')

with open("/home/daytona/exam_work/geometry_camscanner/generate_booklet.py", "w", encoding="utf-8") as f:
    f.write(code)

print("Removed extra SVG from Q2.")
