# build_proposal.py - assemble the Project Proposal
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from docxkit import Report                       # noqa: E402
import report_a                                  # noqa: E402

OUT_DIR = os.environ.get("OUTDIR", r"C:\Users\Administrator\Desktop\JC2001-SF-Assessment\deliverables")


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    R = Report(report_a.TITLE)
    R.reset_figure_counter()
    R.reset_table_counter()
    report_a.build(R)
    path = os.path.join(OUT_DIR, "JC2001_Group9_Project_Proposal.docx")
    R.save(path)
    print("proposal ->", path)
    print("  paragraphs:", len(R.doc.paragraphs), " tables:", len(R.doc.tables))
    print("  tables registered:", len(R.tables), " figures registered:", len(R.figures))


if __name__ == "__main__":
    main()
