#!/usr/bin/env python3
"""Generate a publication-grade, clean light-themed 16:9 poster for @ai_pro_center.
Features the real @SpaceXSI profile screenshot with real SpaceX Starbase background."""
import math
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080

# Load fonts
IRAN_BLACK = "/home/daytona/.fonts/iransans/IRANSansX-Black.ttf"
IRAN_BOLD = "/home/daytona/.fonts/iransans/IRANSansX-Bold.ttf"
TAHAMTAN = "/home/daytona/.fonts/tahamtan/Tahamtan.ttf"
HASTI = "/home/daytona/.fonts/hasti/Hasti-Heavy.ttf"

def F(p, s):
    return ImageFont.truetype(p, s)

# 1. Real SpaceX Background with Frosted Light Editorial Wash
starbase = Image.open("/tmp/starbase.jpg")
scale = max(W / starbase.width, H / starbase.height)
new_w, new_h = int(starbase.width * scale), int(starbase.height * scale)
sb_resized = starbase.resize((new_w, new_h), Image.LANCZOS)
left = (new_w - W) // 2
top = (new_h - H) // 2
bg = sb_resized.crop((left, top, left + W, top + H))
# Soft photographic blur so the background provides depth without noise
bg = bg.filter(ImageFilter.GaussianBlur(8))

# Frosted Light Glass Overlay (Clean slate-white with subtle tech gradient)
overlay = Image.new("RGBA", (W, H), 0)
od = ImageDraw.Draw(overlay)
for x in range(W):
    t = x / W
    # Left side: 80% opacity so SpaceX facility subtly shows through
    # Right side: 92% opacity for maximum typographic clarity
    alpha = int(205 + 32 * t)
    od.line([(x, 0), (x, H)], fill=(244, 247, 251, alpha))

bg = Image.alpha_composite(bg.convert("RGBA"), overlay)
d = ImageDraw.Draw(bg, "RGBA")

# Subtle ambient light glow on left behind the profile card
orb = Image.new("RGBA", (W, H), 0)
ImageDraw.Draw(orb).ellipse([80, 200, 850, 900], fill=(186, 230, 253, 110))
orb = orb.filter(ImageFilter.GaussianBlur(80))
bg = Image.alpha_composite(bg, orb)
d = ImageDraw.Draw(bg, "RGBA")

# 2. Left Side: Real Screenshot in Modern macOS / App Window Card
user_img = Image.open("/home/daytona/.hermes/cache/images/img_10256b132710.jpg")
# Crop profile card (top banner down to followers)
card_crop = user_img.crop((0, 0, user_img.width, 630))

# Window dimensions
card_w = 720
card_h = int(card_crop.height * (card_w / card_crop.width)) # ~391px
top_bar_h = 38
total_win_w = card_w
total_win_h = card_h + top_bar_h
win_radius = 20

# Create window container
window = Image.new("RGBA", (total_win_w, total_win_h), (255, 255, 255, 255))
wd = ImageDraw.Draw(window)

# Top browser/app bar
wd.rounded_rectangle([0, 0, total_win_w, top_bar_h + 10], radius=win_radius, fill=(241, 245, 249, 255))
wd.rectangle([0, top_bar_h, total_win_w, top_bar_h + 1], fill=(226, 232, 240, 255))

# 3 macOS window control dots
dot_y = top_bar_h // 2
wd.ellipse([18, dot_y-5, 28, dot_y+5], fill=(239, 68, 68, 255))   # Red
wd.ellipse([34, dot_y-5, 44, dot_y+5], fill=(245, 158, 11, 255))  # Yellow
wd.ellipse([50, dot_y-5, 60, dot_y+5], fill=(34, 197, 94, 255))   # Green

# URL bar in header
f_url = F(HASTI, 16)
wd.rounded_rectangle([80, dot_y-11, 270, dot_y+11], radius=6, fill=(226, 232, 240, 200))
wd.text((95, dot_y-8), "x.com / @SpaceXSI", font=f_url, fill=(100, 116, 139, 255))

# Verified badge text in window bar
f_tag = F(HASTI, 15)
wd.text((total_win_w - 180, dot_y-8), "Official X Account", font=f_tag, fill=(148, 163, 184, 255))

# Resize and paste real screenshot inside window below top bar
card_resized = card_crop.resize((card_w, card_h), Image.LANCZOS)
window.paste(card_resized, (0, top_bar_h))

# Mask window with rounded corners
win_mask = Image.new("L", (total_win_w, total_win_h), 0)
ImageDraw.Draw(win_mask).rounded_rectangle([0, 0, total_win_w, total_win_h], radius=win_radius, fill=255)

# Calculate placement on canvas
win_x = 90
win_y = (H - total_win_h) // 2 + 10

# Dual-layer diffused drop shadow
shadow = Image.new("RGBA", (W, H), 0)
sd = ImageDraw.Draw(shadow)
sd.rounded_rectangle([win_x-12, win_y+16, win_x+total_win_w+12, win_y+total_win_h+38],
                     radius=win_radius+8, fill=(15, 23, 42, 35))
sd.rounded_rectangle([win_x-4, win_y+8, win_x+total_win_w+4, win_y+total_win_h+16],
                     radius=win_radius+4, fill=(15, 23, 42, 50))
shadow = shadow.filter(ImageFilter.GaussianBlur(24))
bg = Image.alpha_composite(bg, shadow)
d = ImageDraw.Draw(bg, "RGBA")

# Paste window onto canvas
bg.paste(window, (win_x, win_y), win_mask)

# Crisp outer border frame
win_frame = Image.new("RGBA", (W, H), 0)
ImageDraw.Draw(win_frame).rounded_rectangle([win_x, win_y, win_x+total_win_w, win_y+total_win_h],
                                            radius=win_radius, outline=(203, 213, 225, 255), width=2)
bg = Image.alpha_composite(bg, win_frame)
d = ImageDraw.Draw(bg, "RGBA")

# Floating accent badge above the window
f_pill = F(IRAN_BOLD, 22)
pill_txt = "تغییر رسمی برند • از AI به SI"
pbb = d.textbbox((0, 0), pill_txt, font=f_pill, direction="rtl", language="fa")
pw, ph = pbb[2]-pbb[0]+42, pbb[3]-pbb[1]+20
px, py = win_x + 24, win_y - 32
# Pill shadow & body
d.rounded_rectangle([px, py+3, px+pw, py+ph+3], radius=16, fill=(15, 23, 42, 20))
d.rounded_rectangle([px, py, px+pw, py+ph], radius=16,
                    fill=(255, 255, 255, 255), outline=(29, 155, 240, 220), width=2)
d.ellipse([px+16, py+ph//2-4, px+24, py+ph//2+4], fill=(29, 155, 240, 255))
d.text((px+pw-18, py+10), pill_txt, font=f_pill, fill=(2, 132, 199, 255),
       anchor="ra", direction="rtl", language="fa")

# 3. Right Side: Pure Bold Headline (صرفاً تیتر)
RX = W - 100 # Right anchor margin
kw = {"direction": "rtl", "language": "fa"}

f_t1 = F(TAHAMTAN, 102)
f_hook = F(IRAN_BLACK, 116)
f_t3 = F(TAHAMTAN, 102)

# Line 1: خداحافظ AI، سلام به
y1 = 280
d.text((RX, y1), "خداحافظ AI، سلام به", font=f_t1, fill=(15, 23, 42, 255), anchor="ra", **kw)

# Line 2 (HOOK): Vibrant Twitter Blue Banner with "SpaceXSI!"
hook_txt = "SpaceXSI!"
bb_hook = d.textbbox((0, 0), hook_txt, font=f_hook)
hw, hh = bb_hook[2]-bb_hook[0], bb_hook[3]-bb_hook[1]
y2 = 450
pad_x = 48
pad_y = 16

banner_right = RX + 20
banner_left = banner_right - hw - pad_x * 2
banner_top = y2 - pad_y
banner_bottom = y2 + hh + pad_y + 10

# Banner soft shadow
b_shadow = Image.new("RGBA", (W, H), 0)
ImageDraw.Draw(b_shadow).rounded_rectangle([banner_left-2, banner_top+6, banner_right+2, banner_bottom+16],
                                           radius=24, fill=(29, 155, 240, 80))
b_shadow = b_shadow.filter(ImageFilter.GaussianBlur(16))
bg = Image.alpha_composite(bg, b_shadow)
d = ImageDraw.Draw(bg, "RGBA")

# Banner body (Vibrant electric blue #1d9bf0)
d.rounded_rectangle([banner_left, banner_top, banner_right, banner_bottom],
                    radius=22, fill=(29, 155, 240, 255))
# White text inside banner
d.text((banner_right - pad_x, y2 - 4), hook_txt, font=f_hook,
       fill=(255, 255, 255, 255), anchor="ra")

# Line 3: تولد ابرهوش ایلان ماسک
y3 = 665
d.text((RX, y3), "تولد ابرهوش ایلان ماسک", font=f_t3, fill=(15, 23, 42, 255), anchor="ra", **kw)

# 4. Channel Branding (Bottom-Right)
f_brand = F(HASTI, 36)
br_x = RX
br_y = H - 85
d.text((br_x, br_y), "@ai_pro_center", font=f_brand, fill=(100, 116, 139, 255), anchor="ra")
d.ellipse([br_x - 305, br_y+10, br_x - 291, br_y+24], fill=(29, 155, 240, 255))

# Save output
out_file = "/home/daytona/spacexsi_poster_light_16x9.png"
bg.convert("RGB").save(out_file, quality=95)
print(f"Poster successfully generated at {out_file} (1920x1080)")
