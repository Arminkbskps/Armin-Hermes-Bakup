import os, base64, subprocess

OUTPUT_DIR = "/home/daytona/exam_work/dars2"
HTML_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Tashrihi_Dars2_Dahom.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Tashrihi_Dars2_Dahom.pdf")

# Fonts base64
font_dir = "/home/daytona/.hermes/skills/persian-writing/assets/fonts"
vazir_reg_b64 = ""
vazir_bold_b64 = ""
vazir_med_b64 = ""
with open(os.path.join(font_dir, "Vazirmatn-Regular.ttf"), "rb") as f:
    vazir_reg_b64 = base64.b64encode(f.read()).decode("ascii")
with open(os.path.join(font_dir, "Vazirmatn-Bold.ttf"), "rb") as f:
    vazir_bold_b64 = base64.b64encode(f.read()).decode("ascii")
with open(os.path.join(font_dir, "Vazirmatn-Medium.ttf"), "rb") as f:
    vazir_med_b64 = base64.b64encode(f.read()).decode("ascii")

# SVGs
with open(os.path.join(OUTPUT_DIR, "assets/river_geometry.svg"), "r", encoding="utf-8") as f:
    river_svg = f.read()
with open(os.path.join(OUTPUT_DIR, "assets/unit_circle_overview.svg"), "r", encoding="utf-8") as f:
    circle_svg = f.read()
with open(os.path.join(OUTPUT_DIR, "assets/angle_210_geometry.svg"), "r", encoding="utf-8") as f:
    angle210_svg = f.read()

with open("/home/daytona/exam_work/dars2/template.html", "r", encoding="utf-8") as f:
    template = f.read()

html = template.replace("__VAZIR_REG_B64__", vazir_reg_b64)
html = html.replace("__VAZIR_BOLD_B64__", vazir_bold_b64)
html = html.replace("__VAZIR_MED_B64__", vazir_med_b64)
html = html.replace("__RIVER_SVG__", river_svg)
html = html.replace("__CIRCLE_SVG__", circle_svg)
html = html.replace("__ANGLE210_SVG__", angle210_svg)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(html)

print("Generated HTML! Now running Chromium headless...")
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
    print(f"SUCCESS: PDF created at {PDF_PATH} ({sz / 1024:.1f} KB)")
else:
    print("FAILED:", res.stderr)
