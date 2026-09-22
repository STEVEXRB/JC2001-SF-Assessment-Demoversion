"""生成技术报告中文版。

与英文版结构完全一致，区别只有三处：内容模块换成 tech_zh_*，图表取自 figures_zh/
（界面截图与量化图表中，界面本身是英文的，因此中英文版本共用同一批截图），
以及排版引擎启用中文字体与「图 / 表」题注。
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

from docx.enum.text import WD_ALIGN_PARAGRAPH          # noqa: E402
from docx.shared import Pt                             # noqa: E402

import docxkit                                         # noqa: E402
from docxkit import Report, add_field                  # noqa: E402
import tech_zh_a as A                                  # noqa: E402
import tech_zh_b as B                                  # noqa: E402
import tech_zh_c as C                                  # noqa: E402

OUT_DIR = os.environ.get("OUTDIR", r"C:\Users\Administrator\Desktop\JC2001-SF-Assessment\deliverables")
BASENAME = "JC2001_Group9_Technical_Report_ZH"

CHAPTERS = (A.chapter1, A.chapter2, A.chapter3, B.chapter4, B.chapter5,
            C.chapter6, C.chapter7)


def collect():
    probe = Report(A.TITLE)
    for fn in CHAPTERS:
        fn(probe)
    return probe.figures, probe.tables


def page_numbers(path):
    if not path or not os.path.exists(path):
        return {}
    out = {}
    with open(path, encoding="utf-8-sig") as f:
        for line in f:
            parts = line.strip().split("|")
            if len(parts) == 3:
                # Word reports "Figure 4.6"; the Chinese build labels them "图 4.6"
                kind = {"Figure": "图", "Table": "表", "ZH_FIG": "图",
                        "ZH_TAB": "表"}.get(parts[0], parts[0])
                out["%s %s" % (kind, parts[1])] = parts[2]
    return out


def number_footer(R):
    s = R.doc.sections[0]
    s.different_first_page_header_footer = True
    p = s.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    add_field(p, " PAGE \\* ARABIC ", "2")
    for run in p.runs:
        run.font.size = Pt(10)
        run.font.name = "Times New Roman"


def build(pages=None):
    # a Chinese document needs its own body face and caption vocabulary
    docxkit.set_east_asian("宋体")
    docxkit.set_labels("图", "表", "   ")

    figures, tables = collect()
    pages = pages or {}

    def entry(label, caption):
        return (label, caption, pages.get(label, "—"))

    R = Report(A.TITLE)
    number_footer(R)

    A.title_page(R)
    R.toc("目录", depth=2)
    R.static_list("图目录", [entry(l, c) for l, c in figures])
    R.static_list("表目录", [entry(l, c) for l, c in tables])
    for fn in CHAPTERS:
        fn(R)

    C.references(R)
    C.appendix_a(R)
    C.appendix_b(R)
    C.appendix_c(R)

    target = os.path.join(OUT_DIR, BASENAME + ".docx")
    R.save(target)
    print("report zh ->", target)
    print("  图:", len(figures), " 表:", len(tables), " 段落:", len(R.doc.paragraphs))
    return target


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    pages = page_numbers(sys.argv[1]) if len(sys.argv) > 1 else None
    build(pages)


if __name__ == "__main__":
    main()
