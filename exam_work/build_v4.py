#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Build v4: fix missing class-drill Q12-16 between old v3 11 and 12.
Reorder v3 blocks; new order puts page-5 Q12-16 right after class Q1-11."""
import re, pathlib

SRC = pathlib.Path("/home/daytona/exam_work/full_solutions_v3.typ")
DST = pathlib.Path("/home/daytona/exam_work/full_solutions_v4.typ")
t = SRC.read_text(encoding="utf-8")

pat = re.compile(r"#qbox\(\d+,.*?\n\]\)", re.S)
blocks = {}
for m in pat.finditer(t):
    num = int(re.match(r"#qbox\((\d+),", m.group(0)).group(1))
    blocks[num] = m.group(0)
assert len(blocks) == 56, len(blocks)
preamble = t[:pat.search(t).start()]

# v3 -> new order
seq_v3 = (list(range(1,12)) + [52,53,54,55,56] + list(range(12,16))
          + list(range(16,28)) + list(range(28,34)) + list(range(34,38))
          + list(range(38,42)) + list(range(42,46)) + list(range(46,52)))
assert len(seq_v3) == 56 and set(seq_v3) == set(range(1,57)), len(seq_v3)

# keys from v3 blocks
def getkey(b):
    m = re.search(r', "([۱۲۳۴])", \[', b)
    fa = {"۱":1,"۲":2,"۳":3,"۴":4}
    return fa[m.group(1)]
v3key = {n: getkey(b) for n, b in blocks.items()}
newkey = {new+1: v3key[v3n] for new, v3n in enumerate(seq_v3)}

# fix answer-key table pairs [n], [*k*]
def fixpair(m):
    n = int(m.group(1))
    return f"[{n}], [*{newkey[n]}*]"
preamble2, nsub = re.subn(r"\[(\d+)\], \[\*(\d)\*\]", fixpair, preamble)
assert nsub == 56, nsub

# section setup for new order
SECHEAD = {
"A":("بخش اول: تمرین‌های کلاسی مسئله (تست‌های ۱ تا ۱۶)",
"مسیر یادگیری این بخش از پایه‌ترین تبدیل‌ها شروع می‌شود: جرم به مول با جرم مولی، شمار ذره به مول با عدد آووگادرو، و مقایسه مواد با واحد مشترک «مول اتم». تست‌های ۱۲ تا ۱۶ ادامه مستقیم همین مسیرند: استیک‌اسید و ترفتالیک‌اسید، اکسید فلز قلیایی، آلیاژ آهن و مس، مخلوط یون‌ها و واپاشی هیدروژن."),
"B":("بخش دوم: آزمون جامع ۱ — ساختار اتم (تست‌های ۱۷ تا ۲۰)",
"شناسنامه هر اتم را می‌سازی: عدد اتمی از معادله‌های پروتون و الکترون و نوترون، بعد آرایش الکترونی برای گروه و دوره، و سرانجام شمارش ذره‌ها در مخلوط‌ها."),
"C":("بخش سوم: آزمون جامع ۲ — ایزوتوپ‌ها و واپاشی، نیمه اول (تست‌های ۲۱ تا ۳۲)",
"دو ابزار را کنار هم می‌گذاری: میانگین وزنی برای فراوانی ایزوتوپ‌ها، و توان‌های ۲ برای نیم‌عمر. نمودار واپاشی هم چیزی جز خواندن همین دو ابزار از روی شکل نیست."),
"D":("بخش چهارم: آزمون جامع ۲ — ایزوتوپ‌ها و واپاشی، نیمه دوم (تست‌های ۳۳ تا ۳۸)",
"ادامه همان مسیر بخش سوم است ولی از سمت معادله‌های یون شروع می‌شود: اول عدد اتمی، بعد فراوانی، آرایش و نوترون."),
"E":("بخش پنجم: استوکیومتری شمارشی صفحه ۳ (تست‌های ۳۹ تا ۴۲)",
"چهار تست خالص شمارشی: از شمار اتم به مول ترکیب و از جرم مخلوط به درصد جرمی؛ زنجیره‌ها کوتاه‌اند ولی دقت در ضریب اتمی هر فرمول همه‌چیز است."),
"F":("بخش ششم: آزمون جامع ۳ (تست‌های ۴۳ تا ۴۶)",
"چهار تست ترکیبی سطح بالاتر: ایزوتوپ‌شناسی با عدد اتمی، سینتیک واپاشی دو ایزوتوپ، فرمول‌یابی از جرم مولی تجربی، و اختلاف جرم مولکول‌های ایزوتوپی."),
"G":("بخش هفتم: مولکول‌های خاص و یون‌های صفحه ۲ (تست‌های ۴۷ تا ۵۰)",
"مولکول‌هایی که ایزوتوپ‌هایشان شمرده شده‌اند و یون‌هایی که نوترون و الکترونشان معادله می‌سازد؛ همان زنجیره‌های بخش اول ولی با یک لایه تحلیل بیشتر."),
"H":("بخش هشتم: مخلوط‌ها و واپاشی پایه صفحه ۱ (تست‌های ۵۱ تا ۵۶)",
"آلیاژها و مخلوط‌های دوجزئی با دستگاه دو معادله (بقای مول و بقای جرم)، به‌علاوه واپاشی پایه و میانگین ایزوتوپی."),
}
GROUPS = [("A",list(range(1,17))),("B",list(range(17,21))),("C",list(range(21,33))),
          ("D",list(range(33,39))),("E",list(range(39,43))),("F",list(range(43,47))),
          ("G",list(range(47,51))),("H",list(range(51,57)))]

ORIG12_16 = {12:"تمرین کلاسی • مسئله ۱۲",13:"تمرین کلاسی • مسئله ۱۳",
             14:"تمرین کلاسی • مسئله ۱۴",15:"تمرین کلاسی • مسئله ۱۵",
             16:"تمرین کلاسی • مسئله ۱۶"}

out = [preamble2.rstrip() + "\n"]
for sk, nums in GROUPS:
    title, intro = SECHEAD[sk]
    out.append(f'\n#v(8pt)\n#text(size: 11pt, weight: "black", fill: rgb("#1e3a8a"))[{title}]\n#v(2pt)\n#block(fill: rgb("#f8fafc"), stroke: 0.5pt + rgb("#cbd5e1"), radius: 6pt, inset: 7pt, width: 100%)[{intro}]\n#v(3pt)\n')
    for new in nums:
        v3n = seq_v3[new-1]
        b = blocks[v3n]
        b = re.sub(r"#qbox\(\d+,", f"#qbox({new},", b, count=1)
        if new in ORIG12_16:
            b = re.sub(r'(#qbox\(\d+, "[^"]*", ")[^"]*(")', r"\g<1>" + ORIG12_16[new] + r"\g<2>", b, count=1)
        out.append(b + "\n")
DST.write_text("".join(out), encoding="utf-8")
print("v4 written, qboxes:", len(re.findall(r"#qbox\(", DST.read_text(encoding='utf-8'))))
print("new 12-16 orig:", [re.search(r'#qbox\(\d+, "[^"]*", "([^"]*)"', blocks[v]).group(1) for v in [52,53,54,55,56]])
