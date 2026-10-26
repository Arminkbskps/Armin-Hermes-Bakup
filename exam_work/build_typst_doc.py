import os

typst_content = """#set text(font: "Vazirmatn", lang: "fa", dir: rtl, size: 9.5pt)
#set page(
  paper: "a4",
  margin: (x: 1.2cm, top: 1.5cm, bottom: 1.5cm),
  header: locate(loc => {
    if loc.page() > 1 [
      #grid(
        columns: (1fr, 1fr),
        align: (right, left),
        [ #text(size: 7.5pt, fill: rgb("#64748b"))[*پاسخ‌نامه تشریحی ۵۶ تست جامع شیمی* • ساختار اتم، ایزوتوپ‌ها و استوکیومتری] ],
        [ #text(size: 7.5pt, fill: rgb("#64748b"))[*دبیرستان علامه حلی ۲ تهران*] ]
      )
      #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    ]
  }),
  footer: locate(loc => [
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2pt)
    #grid(
      columns: (1fr, 1fr),
      align: (right, left),
      [ #text(size: 7.5pt, fill: rgb("#94a3b8"))[تهیه شده اختصاصی برای آرمین • مهر ۱۴۰۵] ],
      [ #text(size: 7.5pt, fill: rgb("#94a3b8"))[صفحه #loc.page() از #counter(page).final(loc).at(0)] ]
    )
  ])
)

#show heading: it => [
  #v(8pt)
  #text(fill: rgb("#1e3a8a"), weight: "bold")[#it.body]
  #v(4pt)
]

// Cover Header
#align(center)[
  #block(
    stroke: 1.5pt + rgb("#1e3a8a"),
    radius: 10pt,
    inset: 12pt,
    fill: rgb("#f8fafc"),
    width: 100%,
    [
      #grid(
        columns: (1fr, 2.5fr, 1fr),
        align: (center + horizon, center + horizon, center + horizon),
        [
          #text(size: 9pt, weight: "bold", fill: rgb("#0f172a"))[دبیرستان علامه حلی ۲ تهران] \\
          #text(size: 8pt, fill: rgb("#2563eb"))[استعدادهای درخشان (سمپاد)] \\
          #text(size: 7.5pt, fill: rgb("#64748b"))[پایه دهم ریاضی و تجربی]
        ],
        [
          #text(size: 15pt, weight: "black", fill: rgb("#1e3a8a"))[پاسخ‌نامه تشریحی و تحلیلی ۵۶ تست جامع شیمی] \\
          #v(2pt)
          #text(size: 9.5pt, weight: "bold", fill: rgb("#059669"))[ساختار اتم • رادیوایزوتوپ‌ها و نیم‌عمر • جرم اتمی میانگین • استوکیومتری و مول] \\
          #text(size: 8pt, fill: rgb("#64748b"))[بررسی کامل و موشکافانه تک‌تک سوالات همراه با روش‌های تستی و محاسبات دقیق نمادین]
        ],
        [
          #text(size: 8pt, fill: rgb("#0f172a"))[*آزمون‌های جامع الگو و کنکور*] \\
          #text(size: 7.5pt, fill: rgb("#64748b"))[تاریخ: مهر ۱۴۰۵] \\
          #text(size: 7.5pt, fill: rgb("#059669"))[*۵۶ تست حل‌شده کامل*]
        ]
      )
    ]
  )
]

#v(8pt)

// Fast Answer Key Table
#block(
  stroke: 1pt + rgb("#cbd5e1"),
  radius: 8pt,
  inset: 8pt,
  fill: rgb("#ffffff"),
  width: 100%,
  [
    #align(center)[#text(size: 10pt, weight: "bold", fill: rgb("#1e3a8a"))[📊 جدول کلید سریع ۵۶ سوال]]
    #v(4pt)
    #table(
      columns: (1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr),
      align: center + horizon,
      stroke: 0.5pt + rgb("#e2e8f0"),
      fill: (col, row) => if row == 0 { rgb("#eff6ff") } else if calc.even(row) { rgb("#f8fafc") } else { rgb("#ffffff") },
      [#text(size: 7.5pt, weight: "bold")[سوال]], [#text(size: 7.5pt, weight: "bold")[گزینه]],
      [#text(size: 7.5pt, weight: "bold")[سوال]], [#text(size: 7.5pt, weight: "bold")[گزینه]],
      [#text(size: 7.5pt, weight: "bold")[سوال]], [#text(size: 7.5pt, weight: "bold")[گزینه]],
      [#text(size: 7.5pt, weight: "bold")[سوال]], [#text(size: 7.5pt, weight: "bold")[گزینه]],
      [#text(size: 7.5pt, weight: "bold")[سوال]], [#text(size: 7.5pt, weight: "bold")[گزینه]],
      [#text(size: 7.5pt, weight: "bold")[سوال]], [#text(size: 7.5pt, weight: "bold")[گزینه]],
      [#text(size: 7.5pt, weight: "bold")[سوال]], [#text(size: 7.5pt, weight: "bold")[گزینه]],

      [1], [*2*], [9], [*1*], [17], [*1*], [25], [*3*], [33], [*4*], [41], [*1*], [49], [*2*],
      [2], [*4*], [10], [*3*], [18], [*1*], [26], [*3*], [34], [*4*], [42], [*2*], [50], [*4*],
      [3], [*4*], [11], [*3*], [19], [*3*], [27], [*3*], [35], [*1*], [43], [*4*], [51], [*2*],
      [4], [*1*], [12], [*4*], [20], [*3*], [28], [*1*], [36], [*2*], [44], [*1*], [52], [*1*],
      [5], [*4*], [13], [*2*], [21], [*1*], [29], [*2*], [37], [*2*], [45], [*4*], [53], [*4*],
      [6], [*4*], [14], [*2*], [22], [*2*], [30], [*3*], [38], [*3*], [46], [*2*], [54], [*3*],
      [7], [*2*], [15], [*1*], [23], [*3*], [31], [*3*], [39], [*3*], [47], [*1*], [55], [*1*],
      [8], [*1*], [16], [*3*], [24], [*1*], [32], [*1*], [40], [*4*], [48], [*2*], [56], [*2*]
    )
  ]
)

#v(8pt)
"""

print("Header & Key table generated.")
