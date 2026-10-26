with open('/home/daytona/exam_work/full_solutions.typ', 'r', encoding='utf-8') as f:
    text = f.read()

# Replace block margins
text = text.replace("  margin: (bottom: 6pt),", "  spacing: 6pt,")
text = text.replace("  margin: (top: 3pt, bottom: 3pt),", "  spacing: 4pt,")

with open('/home/daytona/exam_work/full_solutions.typ', 'w', encoding='utf-8') as f:
    f.write(text)

print("Block margins fixed.")
