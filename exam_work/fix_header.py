with open('/home/daytona/exam_work/full_solutions.typ', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace header/footer with Typst 0.11+ context syntax
old_header = """  header: locate(loc => {
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
  ])"""

new_header = """  header: context {
    if here().page() > 1 [
      #grid(
        columns: (1fr, 1fr),
        align: (right, left),
        [ #text(size: 7.5pt, fill: rgb("#64748b"))[*پاسخ‌نامه تشریحی و جامع ۵۶ تست شیمی کنکور* • ساختار اتم، ایزوتوپ‌ها و استوکیومتری] ],
        [ #text(size: 7.5pt, fill: rgb("#64748b"))[*دبیرستان علامه حلی ۲ تهران*] ]
      )
      #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    ]
  },
  footer: context [
    #line(length: 100%, stroke: 0.5pt + rgb("#cbd5e1"))
    #v(2pt)
    #grid(
      columns: (1fr, 1fr),
      align: (right, left),
      [ #text(size: 7.5pt, fill: rgb("#94a3b8"))[تهیه شده اختصاصی برای آرمین • مهر ۱۴۰۵] ],
      [ #text(size: 7.5pt, fill: rgb("#94a3b8"))[صفحه #here().page() از #counter(page).final().at(0)] ]
    )
  ]"""

text = text.replace(old_header, new_header)

with open('/home/daytona/exam_work/full_solutions.typ', 'w', encoding='utf-8') as f:
    f.write(text)

print("Updated to Typst 0.11+ context syntax.")
