#!/usr/bin/env python3
"""Generate a high-impact, crisp 16:9 poster for @ai_pro_center covering SpaceXSI rebrand."""
import math, random
from PIL import Image, ImageDraw, ImageFont, ImageFilter

W, H = 1920, 1080
random.seed(42)

IRAN_BLACK = "/home/daytona/.fonts/iransans/IRANSansX-Black.ttf"
IRAN_BOLD = "/home/daytona/.fonts/iransans/IRANSansX-Bold.ttf"
ROKH_BLACK = "/home/daytona/.fonts/rokh/Rokh-Black.ttf"
TAHAMTAN = "/home/daytona/.fonts/tahamtan/Tahamtan.ttf"
HASTI = "/home/daytona/.fonts/hasti/Hasti-Heavy.ttf"

def F(p, s):
    return ImageFont.truetype(p, s)

# Base Canvas (Deep Midnight Space)
bg = Image.new("RGBA", (W, H), (5, 9, 20, 255))
d = ImageDraw.Draw(bg, "RGBA")

# 1. Cosmic Glow & Stars
# Soft nebula glow
for r, a, c in ((500, 28, (2, 132, 199)), (340, 48, (59, 130, 246)), (200, 65, (99, 102, 241))):
    d.ellipse([380-r, 520-r, 380+r, 520+r], fill=(*c, a))

# Starfield
for _ in range(240):
    x = random.randint(0, int(W * 0.72))
    y = random.randint(0, H)
    sz = random.choices([1, 2, 3], weights=[0.8, 0.16, 0.04])[0]
    alpha = random.randint(50, 240)
    col = (255, 255, 255, alpha) if random.random() > 0.25 else (147, 197, 253, alpha)
    d.ellipse([x-sz, y-sz, x+sz, y+sz], fill=col)

# 2. SpaceX Orbital Arcs & Trajectories (Clean & futuristic)
ox, oy = 260, 780
for r_orbit, alpha_val in ((520, 65), (660, 45), (820, 25)):
    d.arc([ox-r_orbit, oy-r_orbit, ox+r_orbit, oy+r_orbit], 215, 345, fill=(56, 189, 248, alpha_val), width=3)
    d.arc([ox-r_orbit-25, oy-r_orbit+45, ox+r_orbit+25, oy+r_orbit-45], 235, 325, fill=(129, 140, 248, alpha_val-10), width=2)

# Digital constellation network
nodes = [(160, 220), (320, 160), (480, 220), (140, 430), (520, 360), (160, 670), (420, 760), (620, 690)]
for i, n1 in enumerate(nodes):
    for n2 in nodes[i+1:]:
        dist = math.hypot(n1[0]-n2[0], n1[1]-n2[1])
        if dist < 260:
            d.line([n1, n2], fill=(56, 189, 248, max(15, int(75 - dist*0.22))), width=1)
    d.ellipse([n1[0]-4, n1[1]-4, n1[0]+4, n1[1]+4], fill=(56, 189, 248, 200))

# 3. Floating Glassmorphism Profile Card
CARD_W, CARD_H = 700, 430
CX, CY = 480, 520
c_left = CX - CARD_W // 2
c_top = CY - CARD_H // 2
c_right = CX + CARD_W // 2
c_bottom = CY + CARD_H // 2

# Card glow
card_glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
cgd = ImageDraw.Draw(card_glow, "RGBA")
for pad, a_glow in ((32, 16), (20, 32), (8, 65)):
    cgd.rounded_rectangle([c_left-pad, c_top-pad, c_right+pad, c_bottom+pad],
                          radius=32, fill=(2, 132, 199, a_glow))
card_glow = card_glow.filter(ImageFilter.GaussianBlur(16))
bg = Image.alpha_composite(bg, card_glow)
d = ImageDraw.Draw(bg, "RGBA")

# Card Body (Dark glass with crisp glowing border)
d.rounded_rectangle([c_left, c_top, c_right, c_bottom], radius=28,
                    fill=(11, 20, 38, 240), outline=(56, 189, 248, 180), width=2)

# Top Header banner inside card
d.rounded_rectangle([c_left+3, c_top+3, c_right-3, c_top+110], radius=25,
                    fill=(16, 29, 56, 255))
d.line([(c_left+24, c_top+110), (c_right-24, c_top+110)], fill=(56, 189, 248, 120), width=2)

# Official Rebrand Badge inside card header
f_badge = F(HASTI, 21)
b_txt = "OFFICIAL REBRAND"
bb_b = d.textbbox((0, 0), b_txt, font=f_badge)
bw, bh = bb_b[2]-bb_b[0]+32, bb_b[3]-bb_b[1]+18
bx2, by2 = c_right - 26 - bw, c_top + 26
d.rounded_rectangle([bx2, by2, bx2+bw, by2+bh], radius=12,
                    fill=(6, 78, 59, 120), outline=(16, 185, 129, 230), width=2)
d.ellipse([bx2+12, by2+bh//2-5, bx2+22, by2+bh//2+5], fill=(52, 211, 153, 255))
d.text((bx2+30, by2+8), b_txt, font=f_badge, fill=(209, 250, 229, 255))

# Avatar Frame & Image
av_size = 114
av_x = c_left + 36
av_y = c_top + 50
avatar_im = Image.open("/tmp/clean_avatar.png").convert("RGBA")
avatar_res = avatar_im.resize((av_size, av_size), Image.LANCZOS)
av_mask = Image.new("L", (av_size, av_size), 0)
ImageDraw.Draw(av_mask).rounded_rectangle([0, 0, av_size, av_size], radius=24, fill=255)

# Outer avatar rim
d.rounded_rectangle([av_x-5, av_y-5, av_x+av_size+5, av_y+av_size+5], radius=28,
                    fill=(11, 20, 38, 255), outline=(56, 189, 248, 240), width=3)
bg.paste(avatar_res, (av_x, av_y), av_mask)
d = ImageDraw.Draw(bg, "RGBA")

# Account Title & Gold Checkmark
f_name = F(IRAN_BOLD, 31)
name_txt = "SpaceX Super Intelligence"
d.text((c_left + 172, c_top + 120), name_txt, font=f_name, fill=(255, 255, 255, 255))

bb_name = d.textbbox((c_left + 172, c_top + 120), name_txt, font=f_name)
gold_x = bb_name[2] + 12
gold_y = c_top + 124
# Gold badge
d.rounded_rectangle([gold_x, gold_y, gold_x+25, gold_y+25], radius=6, fill=(234, 179, 8, 255))
d.line([(gold_x+6, gold_y+13), (gold_x+11, gold_y+18)], fill=(0, 0, 0, 255), width=3)
d.line([(gold_x+11, gold_y+18), (gold_x+19, gold_y+8)], fill=(0, 0, 0, 255), width=3)

# Handle @SpaceXSI
f_hnd = F(HASTI, 26)
d.text((c_left + 172, c_top + 162), "@SpaceXSI", font=f_hnd, fill=(56, 189, 248, 255))

# Bio line (High contrast & crisp)
f_bio = F(IRAN_BOLD, 23)
d.text((c_left + 36, c_top + 205), "Leading the Frontier from Artificial to Super Intelligence.",
       font=f_bio, fill=(241, 245, 249, 255))

# Metadata Row: Website & Joined Date
f_meta = F(HASTI, 23)
d.rounded_rectangle([c_left+36, c_top+252, c_left+152, c_top+296], radius=12,
                    fill=(15, 34, 64, 230), outline=(56, 189, 248, 160), width=1)
d.text((c_left+50, c_top+260), "🔗 x.ai", font=f_meta, fill=(56, 189, 248, 255))

d.text((c_left+175, c_top+262), "📅 عضویت: May 2023", font=F(IRAN_BOLD, 22), fill=(203, 213, 225, 255))

# Metrics divider line
d.line([(c_left+24, c_top+325), (c_right-24, c_top+325)], fill=(30, 58, 95, 200), width=1)

# Metrics numbers (Clean & large)
f_num = F(IRAN_BOLD, 27)
f_lbl = F(IRAN_BOLD, 21)

d.text((c_left + 40, c_top + 355), "2,000,000", font=f_num, fill=(255, 255, 255, 255))
d.text((c_left + 185, c_top + 360), "دنبال‌کننده (Followers)", font=f_lbl, fill=(148, 163, 184, 255))

d.text((c_left + 460, c_top + 355), "6", font=f_num, fill=(255, 255, 255, 255))
d.text((c_left + 485, c_top + 360), "دنبال‌شده", font=f_lbl, fill=(148, 163, 184, 255))

# 4. Floating Badges around Card
# Top badge: AI ➔ SI with vector arrow
f_pill = F(HASTI, 32)
px, py, pw, ph = 130, 245, 220, 68
d.rounded_rectangle([px, py, px+pw, py+ph], radius=22,
                    fill=(10, 25, 54, 245), outline=(56, 189, 248, 240), width=3)
d.text((px+42, py+ph//2), "AI", font=f_pill, fill=(255, 255, 255, 255), anchor="mm")
# Draw vector cyan arrow ->
ax1, ay1 = px + 88, py + ph//2
ax2 = px + 132
d.line([(ax1, ay1), (ax2, ay1)], fill=(56, 189, 248, 255), width=4)
d.line([(ax2-12, ay1-8), (ax2, ay1)], fill=(56, 189, 248, 255), width=4)
d.line([(ax2-12, ay1+8), (ax2, ay1)], fill=(56, 189, 248, 255), width=4)
d.text((px+176, py+ph//2), "SI", font=f_pill, fill=(56, 189, 248, 255), anchor="mm")

# Bottom badge: Trump & Musk
f_pill2 = F(IRAN_BOLD, 22)
p2x, p2y, p2w, p2h = 370, 780, 340, 56
d.rounded_rectangle([p2x, p2y, p2x+p2w, p2y+p2h], radius=18,
                    fill=(24, 20, 52, 235), outline=(168, 85, 247, 200), width=2)
d.text((p2x+p2w//2, p2y+p2h//2), "پیشنهاد ترامپ • اقدام ماسک", font=f_pill2,
       fill=(233, 213, 255, 255), anchor="mm")

# 5. Right-side Deep Gradient (Ensures 100% Contrast for Headline)
grad = Image.new("L", (W, H), 0)
gd = ImageDraw.Draw(grad)
for x in range(W):
    t = (x - W * 0.36) / (W * 0.64)
    t = max(0.0, min(1.0, t))
    smooth_t = t * t * (3 - 2 * t)
    gd.line([(x, 0), (x, H)], fill=int(145 + 110 * smooth_t))

grad = grad.filter(ImageFilter.GaussianBlur(50))
black = Image.new("RGBA", (W, H), (4, 7, 16, 255))
bg = Image.composite(black, bg, grad)

# Vignette
vig = Image.new("L", (W, H), 255)
vd = ImageDraw.Draw(vig)
for i in range(100):
    vd.rectangle([i*2, i*2, W-i*2, H-i*2], outline=int(255 - 75*(i/100)))
vig = vig.filter(ImageFilter.GaussianBlur(30))
bg = Image.composite(bg, Image.new("RGBA", (W, H), (0, 0, 0, 255)),
                     vig.point(lambda v: 255 - (255 - v)))

# 6. Headline Typography (Right-Aligned, Clean & Flat Modern)
d = ImageDraw.Draw(bg)
RX = W - 100  # Right margin anchor
kw = {"direction": "rtl", "language": "fa"}

f_line1 = F(IRAN_BLACK, 102)
f_hook = F(HASTI, 126)
f_line3 = F(IRAN_BLACK, 96)

def text_shadow(xy, text, font, fill, anchor="ra", is_fa=True):
    x, y = xy
    extra = kw if is_fa else {}
    for dx, dy in ((0, 6), (4, 0), (-4, 0), (0, -2)):
        d.text((x+dx, y+dy), text, font=font, fill=(0, 0, 0, 240), anchor=anchor, **extra)
    d.text((x, y), text, font=font, fill=fill, anchor=anchor, **extra)

# Line 1: خداحافظ AI، سلام به
y_line1 = 285
text_shadow((RX, y_line1), "خداحافظ AI، سلام به", f_line1, (255, 255, 255, 255))

# Line 2 (HOOK BANNER): Sleek flat modern rounded banner
hook_txt = "SpaceXSI!"
bb_hook = d.textbbox((0, 0), hook_txt, font=f_hook)
hw, hh = bb_hook[2]-bb_hook[0], bb_hook[3]-bb_hook[1]
y_hook = 455
pad_x = 44
pad_y = 20

banner_right = RX + 20
banner_left = banner_right - hw - pad_x * 2
banner_top = y_hook - pad_y
banner_bottom = y_hook + hh + pad_y + 8

# Banner outer soft glow
for bg_pad, bg_a in ((20, 25), (10, 50), (4, 90)):
    d.rounded_rectangle([banner_left-bg_pad, banner_top-bg_pad, banner_right+bg_pad, banner_bottom+bg_pad],
                        radius=26, fill=(2, 132, 199, bg_a))

# Main Banner body (Electric Blue / Azure)
d.rounded_rectangle([banner_left, banner_top, banner_right, banner_bottom],
                    radius=22, fill=(2, 132, 199, 255), outline=(125, 211, 252, 230), width=3)

# Draw Hook Text inside banner
text_shadow((banner_right - pad_x, y_hook - 6), hook_txt, f_hook, (255, 255, 255, 255), anchor="ra", is_fa=False)

# Line 3: عصر جدید ابرهوش ماسک
y_line3 = 655
text_shadow((RX, y_line3), "عصر جدید ابرهوش ماسک", f_line3, (248, 250, 252, 255))

# Explainer Subtitle below headline
f_sub = F(IRAN_BOLD, 32)
d.text((RX, y_line3 + 130), "جایگزینی رسمی عبارت هوش مصنوعی با «هوش برتر»",
       font=f_sub, fill=(148, 163, 184, 255), anchor="ra", **kw)

# 7. Channel Branding (Bottom-Right)
f_brand = F(HASTI, 36)
br_x = RX
br_y = H - 75
d.text((br_x, br_y), "@ai_pro_center", font=f_brand, fill=(186, 215, 255, 240), anchor="ra")
d.ellipse([br_x - 305, br_y+10, br_x - 291, br_y+24], fill=(56, 189, 248, 255))

# Save Poster
out_path = "/home/daytona/spacexsi_poster_16x9.png"
bg.convert("RGB").save(out_path, quality=95)
print(f"Refined poster saved successfully at {out_path} ({W}x{H})")
