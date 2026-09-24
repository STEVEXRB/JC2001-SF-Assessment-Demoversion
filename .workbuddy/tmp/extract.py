import sys
from pypdf import PdfReader
src = r"C:/Users/Administrator/Downloads/JC2001-GroupProjectDescription-and-Requirements-2026-27 (1).pdf"
r = PdfReader(src)
print("PAGES:", len(r.pages))
out = []
for i, p in enumerate(r.pages, 1):
    try:
        t = p.extract_text() or ""
    except Exception as e:
        t = f"[ERR {e}]"
    out.append(f"\n===== PAGE {i} =====\n{t}")
txt = "".join(out)
with open(r"C:/Users/Administrator/Desktop/JC2001-SF-Assessment/.workbuddy/tmp/pdf.txt", "w", encoding="utf-8") as f:
    f.write(txt)
print("CHARS:", len(txt))
