from pypdf import PdfReader
src = r"C:/Users/Administrator/Downloads/Proposal_Template.pdf"
r = PdfReader(src)
print("PAGES:", len(r.pages))
for i, p in enumerate(r.pages, 1):
    print(f"\n===== PAGE {i} =====")
    print(p.extract_text() or "")
