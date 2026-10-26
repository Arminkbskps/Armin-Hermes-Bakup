# Let's generate the complete Typst booklet with full solutions
import sys

with open('/home/daytona/exam_work/full_solutions.typ', 'w', encoding='utf-8') as f:
    f.write("""#set text(font: "Vazirmatn", lang: "fa", dir: rtl, size: 9pt)
#set page(
  paper: "a4",
  margin: (x: 1.2cm, top: 1.4cm, bottom: 1.4cm),
  header: locate(loc => {
    if loc.page() > 1 [
      #grid(
        columns: (1fr, 1fr),
        align: (right, left),
        [ #text(size: 7.5pt, fill: rgb("#64748b"))[*پاسخ‌نامه تشریحی و جامع ۵۶ تست شیمی کنکور* • ساختار اتم، ایزوتوپ‌ها و استوکیومتری] ],
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

#let qbox(num, title, orig, key, content) = block(
  stroke: 1pt + rgb("#e2e8f0"),
  radius: 6pt,
  inset: 7pt,
  fill: rgb("#ffffff"),
  width: 100%,
  margin: (bottom: 6pt),
  [
    #grid(
      columns: (1fr, auto),
      align: (right + horizon, left + horizon),
      [
        #text(size: 9.5pt, weight: "bold", fill: rgb("#1e3a8a"))[تست #num]
        #h(4pt)
        #text(size: 8pt, fill: rgb("#64748b"))[(#orig • #title)]
      ],
      [
        #block(
          fill: rgb("#ecfdf5"),
          stroke: 1pt + rgb("#10b981"),
          radius: 4pt,
          inset: (x: 6pt, y: 2pt),
          [#text(size: 8.5pt, weight: "black", fill: rgb("#065f46"))[پاسخ: گزینه #key]]
        )
      ]
    )
    #v(3pt)
    #line(length: 100%, stroke: 0.4pt + rgb("#f1f5f9"))
    #v(3pt)
    #content
  ]
)

#let tip(body) = block(
  fill: rgb("#eff6ff"),
  stroke: (right: 3pt + rgb("#2563eb")),
  inset: (x: 8pt, y: 4pt),
  radius: (left: 4pt),
  margin: (top: 3pt, bottom: 3pt),
  [
    #text(size: 8pt, weight: "bold", fill: rgb("#1e40af"))[💡 نکته آموزشی و کنکوری:] #h(4pt)
    #text(size: 8pt, fill: rgb("#1e293b"))[#body]
  ]
)

// Main Title Banner
#align(center)[
  #block(
    stroke: 1.5pt + rgb("#1e3a8a"),
    radius: 10pt,
    inset: 10pt,
    fill: rgb("#f8fafc"),
    width: 100%,
    [
      #grid(
        columns: (1fr, 2.8fr, 1fr),
        align: (center + horizon, center + horizon, center + horizon),
        [
          #text(size: 9pt, weight: "bold", fill: rgb("#0f172a"))[دبیرستان علامه حلی ۲ تهران] \\
          #text(size: 8pt, fill: rgb("#2563eb"))[استعدادهای درخشان (سمپاد)] \\
          #text(size: 7.5pt, fill: rgb("#64748b"))[پایه دهم ریاضی و تجربی]
        ],
        [
          #text(size: 14pt, weight: "black", fill: rgb("#1e3a8a"))[پاسخ‌نامه تشریحی و تحلیلی ۵۶ تست جامع شیمی] \\
          #v(1pt)
          #text(size: 9pt, weight: "bold", fill: rgb("#059669"))[ساختار اتم • رادیوایزوتوپ‌ها و نیم‌عمر • جرم اتمی میانگین • استوکیومتری و مول] \\
          #text(size: 7.5pt, fill: rgb("#64748b"))[حل گام‌به‌گام و دقیق تمامی ۵۶ تست مندرج در جزوه ۶ صفحه‌ای]
        ],
        [
          #text(size: 8pt, fill: rgb("#0f172a"))[*آزمون جامع الگو و کنکور*] \\
          #text(size: 7.5pt, fill: rgb("#64748b"))[تاریخ: مهر ۱۴۰۵] \\
          #text(size: 7.5pt, fill: rgb("#059669"))[*۵۶ تست حل‌شده ۱۰۰٪*]
        ]
      )
    ]
  )
]

#v(4pt)

// Fast Answer Key Table
#block(
  stroke: 1pt + rgb("#cbd5e1"),
  radius: 8pt,
  inset: 6pt,
  fill: rgb("#ffffff"),
  width: 100%,
  [
    #align(center)[#text(size: 9.5pt, weight: "bold", fill: rgb("#1e3a8a"))[📊 جدول کلید پاسخ سریع ۵۶ سوال (تست‌های ۱ تا ۵۶)]]
    #v(3pt)
    #table(
      columns: (1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr, 1fr, 1.2fr),
      align: center + horizon,
      stroke: 0.4pt + rgb("#e2e8f0"),
      fill: (col, row) => if row == 0 { rgb("#eff6ff") } else if calc.even(row) { rgb("#f8fafc") } else { rgb("#ffffff") },
      [#text(size: 7pt, weight: "bold")[سوال]], [#text(size: 7pt, weight: "bold")[پاسخ]],
      [#text(size: 7pt, weight: "bold")[سوال]], [#text(size: 7pt, weight: "bold")[پاسخ]],
      [#text(size: 7pt, weight: "bold")[سوال]], [#text(size: 7pt, weight: "bold")[پاسخ]],
      [#text(size: 7pt, weight: "bold")[سوال]], [#text(size: 7pt, weight: "bold")[پاسخ]],
      [#text(size: 7pt, weight: "bold")[سوال]], [#text(size: 7pt, weight: "bold")[پاسخ]],
      [#text(size: 7pt, weight: "bold")[سوال]], [#text(size: 7pt, weight: "bold")[پاسخ]],
      [#text(size: 7pt, weight: "bold")[سوال]], [#text(size: 7pt, weight: "bold")[پاسخ]],

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

#v(6pt)
#text(size: 11pt, weight: "black", fill: rgb("#1e3a8a"))[بخش اول: پاسخ تشریحی تست‌های صفحه ۱ (سوالات ۱ تا ۶)]
#v(3pt)
""")

    # We will write out each question's detailed solution block
print("Base structure written.")
