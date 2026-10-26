import subprocess, os, base64

OUTPUT_DIR = "/home/daytona/exam_work/trig"
HTML_PATH = os.path.join(OUTPUT_DIR, "trig_booklet.html")
PDF_PATH = os.path.join(OUTPUT_DIR, "Pasokhname_Jame_Dayere_Mosalasati_Helli2.pdf")

# Read fonts
font_dir = "/home/daytona/.hermes/skills/persian-writing/assets/fonts"
vazir_reg_b64 = ""
vazir_bold_b64 = ""
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Regular.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Regular.ttf"), "rb") as f:
        vazir_reg_b64 = base64.b64encode(f.read()).decode("ascii")
if os.path.exists(os.path.join(font_dir, "Vazirmatn-Bold.ttf")):
    with open(os.path.join(font_dir, "Vazirmatn-Bold.ttf"), "rb") as f:
        vazir_bold_b64 = base64.b64encode(f.read()).decode("ascii")

with open(os.path.join(OUTPUT_DIR, "circle.svg"), "r", encoding="utf-8") as f:
    circle_svg = f.read()

# Build HTML without f-string syntax collision
template_file = "/home/daytona/exam_work/trig/template.html"
with open("/home/daytona/exam_work/trig/build_trig_booklet.py", "r", encoding="utf-8") as f:
    text = f.read()

# Extract from html_content = f"""<!DOCTYPE html> to """
start = text.find('<!DOCTYPE html>')
end = text.rfind('</html>') + 7
raw_html = text[start:end]

# Replace placeholders
raw_html = raw_html.replace("{vazir_reg_b64}", vazir_reg_b64)
raw_html = raw_html.replace("{vazir_bold_b64}", vazir_bold_b64)
raw_html = raw_html.replace("{circle_svg}", circle_svg)

with open(HTML_PATH, "w", encoding="utf-8") as f:
    f.write(raw_html)

print("HTML successfully generated!")

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
    print(f"SUCCESS: PDF generated at {PDF_PATH} ({sz / 1024:.1f} KB)")
else:
    print("FAILED:", res.stderr)
