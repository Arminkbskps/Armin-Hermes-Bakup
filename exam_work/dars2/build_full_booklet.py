import os, base64, subprocess

OUTPUT_DIR = "/home/daytona/exam_work/dars2"
HTML_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Tashrihi_Dars2_Dahom.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Tashrihi_Dars2_Dahom.pdf")

# Read fonts
font_dir = "/home/daytona/.hermes/skills/persian-writing/assets/fonts"
vazir_reg_b64 = ""
vazir_bold_b64 = ""
vazir_med_b64 = ""
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Regular.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Regular.ttf"), "rb") as f:
        vazir_reg_b64 = base64.b64encode(f.read()).decode("ascii")
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Bold.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Bold.ttf"), "rb") as f:
        vazir_bold_b64 = base64.b64encode(f.read()).decode("ascii")
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Medium.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Medium.ttf"), "rb") as f:
        vazir_med_b64 = base64.b64encode(f.read()).decode("ascii")

# Read SVGs
with open(os.path.join(OUTPUT_DIR, "assets/river_geometry.svg"), "r", encoding="utf-8") as f:
    river_svg = f.read()

with open(os.path.join(OUTPUT_DIR, "assets/unit_circle_overview.svg"), "r", encoding="utf-8") as f:
    circle_svg = f.read()

with open(os.path.join(OUTPUT_DIR, "assets/angle_210_geometry.svg"), "r", encoding="utf-8") as f:
    angle210_svg = f.read()

print("Assets loaded successfully!")
