# docxkit.py - builds a Word document that satisfies the JC2001 formatting rules:
# A4, 1 inch margins on all four sides, single column, 12 pt Times New Roman,
# 1.5 line spacing, automatic table of contents, list of figures and list of tables.
import copy
import os

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Inches, Pt, RGBColor

BODY_FONT = "Times New Roman"

# Word needs an explicit East Asian face, otherwise a Chinese document falls back
# to whatever the reader's machine happens to have. The Latin font stays Times New
# Roman so that identifiers, SQL and citations keep their intended shape.
EA = {"font": None}


def set_east_asian(font):
    EA["font"] = font


# Caption vocabulary, so a localized build can say "图 4.1" instead of "Figure 4.1".
LBL = {"fig": "Figure", "tab": "Table", "sep": "   "}


def set_labels(fig=None, tab=None, sep=None):
    if fig:
        LBL["fig"] = fig
    if tab:
        LBL["tab"] = tab
    if sep is not None:
        LBL["sep"] = sep
INK = RGBColor(0x00, 0x00, 0x00)
MUTED = RGBColor(0x44, 0x4A, 0x53)
RULE = "9AA5B1"
HEAD_FILL = "EDF1F6"
ZEBRA_FILL = "F7F9FB"


# --------------------------------------------------------------------- helpers
def _el(tag, **attrs):
    node = OxmlElement(tag)
    for k, v in attrs.items():
        node.set(qn(k), str(v))
    return node


def _set_borders(tbl, top=None, bottom=None, inside_h=None, inside_v=None, left=None, right=None):
    tblPr = tbl._tbl.tblPr
    borders = _el("w:tblBorders")
    for name, spec in (("top", top), ("bottom", bottom), ("left", left), ("right", right),
                       ("insideH", inside_h), ("insideV", inside_v)):
        node = _el("w:" + name)
        if spec is None:
            node.set(qn("w:val"), "none")
            node.set(qn("w:sz"), "0")
            node.set(qn("w:space"), "0")
        else:
            sz, color = spec
            node.set(qn("w:val"), "single")
            node.set(qn("w:sz"), str(sz))
            node.set(qn("w:space"), "0")
            node.set(qn("w:color"), color)
        borders.append(node)
    tblPr.append(borders)


def _shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    tcPr.append(_el("w:shd", **{"w:val": "clear", "w:color": "auto", "w:fill": fill}))


def _cell_margins(tbl, top=60, bottom=60, left=110, right=110):
    tblPr = tbl._tbl.tblPr
    mar = _el("w:tblCellMar")
    for name, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        mar.append(_el("w:" + name, **{"w:w": str(val), "w:type": "dxa"}))
    tblPr.append(mar)


def add_field(paragraph, instruction, placeholder="", dirty=True):
    """Insert a real Word field so Word can compute it on update."""
    run = paragraph.add_run()
    fld = _el("w:fldChar", **{"w:fldCharType": "begin"})
    if dirty:
        fld.set(qn("w:dirty"), "true")
    run._r.append(fld)

    run = paragraph.add_run()
    instr = _el("w:instrText")
    instr.set(qn("xml:space"), "preserve")
    instr.text = instruction
    run._r.append(instr)

    run = paragraph.add_run()
    run._r.append(_el("w:fldChar", **{"w:fldCharType": "separate"}))

    if placeholder:
        paragraph.add_run(placeholder)

    run = paragraph.add_run()
    run._r.append(_el("w:fldChar", **{"w:fldCharType": "end"}))
    return paragraph


def set_outline(paragraph, level):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.append(_el("w:outlineLvl", **{"w:val": str(level)}))


def keep_with_next(paragraph, on=True):
    pPr = paragraph._p.get_or_add_pPr()
    pPr.append(_el("w:keepNext", **{"w:val": "1" if on else "0"}))


# --------------------------------------------------------------------- document
class Report:
    def __init__(self, title=""):
        self.doc = Document()
        self.fig_no = 0
        self.tab_no = 0
        self.figures = []          # [(label, caption)]
        self.tables = []
        self._setup_styles()
        self._setup_page()
        self.core_title = title

    # ---------------------------------------------------------------- setup
    def _setup_page(self):
        for s in self.doc.sections:
            s.page_width = Cm(21.0)
            s.page_height = Cm(29.7)
            s.left_margin = Inches(1)
            s.right_margin = Inches(1)
            s.top_margin = Inches(1)
            s.bottom_margin = Inches(1)
            s.header_distance = Inches(0.5)
            s.footer_distance = Inches(0.5)

    def _setup_styles(self):
        normal = self.doc.styles["Normal"]
        normal.font.name = BODY_FONT
        normal.font.size = Pt(12)
        normal.font.color.rgb = INK
        rpr = normal.element.get_or_add_rPr()
        rfonts = rpr.find(qn("w:rFonts"))
        if rfonts is None:
            rfonts = _el("w:rFonts")
            rpr.append(rfonts)
        for attr in ("w:ascii", "w:hAnsi", "w:cs"):
            rfonts.set(qn(attr), BODY_FONT)
        rfonts.set(qn("w:eastAsia"), EA["font"] or BODY_FONT)
        pf = normal.paragraph_format
        pf.line_spacing = 1.5
        pf.space_after = Pt(2)
        pf.space_before = Pt(0)

        for name, size, bold, before, after in (
                ("Heading 1", 15.5, True, 12, 6),
                ("Heading 2", 13.5, True, 10, 5),
                ("Heading 3", 12, True, 8, 4),
                ("Heading 4", 11.5, True, 7, 3)):
            st = self.doc.styles[name]
            st.font.name = BODY_FONT
            st.font.size = Pt(size)
            st.font.bold = bold
            st.font.color.rgb = INK
            st.font.italic = False
            rpr = st.element.get_or_add_rPr()
            rf = rpr.find(qn("w:rFonts"))
            if rf is None:
                rf = _el("w:rFonts")
                rpr.append(rf)
            for attr in ("w:ascii", "w:hAnsi", "w:cs"):
                rf.set(qn(attr), BODY_FONT)
            rf.set(qn("w:eastAsia"), EA["font"] or BODY_FONT)
            st.paragraph_format.line_spacing = 1.15
            st.paragraph_format.space_before = Pt(before)
            st.paragraph_format.space_after = Pt(after)
            st.paragraph_format.keep_with_next = True

    # ---------------------------------------------------------------- blocks
    def para(self, text, size=12, align="left", italic=False, bold=False, spacing=1.5,
             space_after=6, space_before=0, indent=None, color=None):
        p = self.doc.add_paragraph()
        p.paragraph_format.line_spacing = spacing
        p.paragraph_format.space_after = Pt(space_after)
        p.paragraph_format.space_before = Pt(space_before)
        if indent is not None:
            p.paragraph_format.left_indent = Inches(indent)
        p.alignment = {"left": WD_ALIGN_PARAGRAPH.LEFT, "center": WD_ALIGN_PARAGRAPH.CENTER,
                       "right": WD_ALIGN_PARAGRAPH.RIGHT,
                       "justify": WD_ALIGN_PARAGRAPH.JUSTIFY}[align]
        if text:
            self._rich(p, text, size, italic, bold, color)
        return p

    @staticmethod
    def _rich(p, text, size=12, italic=False, bold=False, color=None):
        """`text` may contain **bold** and `code` spans."""
        import re
        tokens = re.split(r"(\*\*[^*]+\*\*|`[^`]+`)", text)
        for tok in tokens:
            if not tok:
                continue
            if tok.startswith("**") and tok.endswith("**") and len(tok) > 4:
                r = p.add_run(tok[2:-2]); r.bold = True
            elif tok.startswith("`") and tok.endswith("`") and len(tok) > 2:
                r = p.add_run(tok[1:-1]); r.font.name = "Consolas"; r.font.size = Pt(size - 1.5)
            else:
                r = p.add_run(tok)
            r.font.size = Pt(size)
            r.italic = italic
            if bold:
                r.bold = True
            if color is not None:
                r.font.color.rgb = color
            r.font.element.get_or_add_rPr()

    def h1(self, text, page_break=True):
        if page_break:
            self.doc.add_page_break()
        p = self.doc.add_paragraph(style="Heading 1")
        p.add_run(text)
        return p

    def h2(self, text):
        p = self.doc.add_paragraph(style="Heading 2")
        p.add_run(text)
        return p

    def h3(self, text):
        p = self.doc.add_paragraph(style="Heading 3")
        p.add_run(text)
        return p

    def h4(self, text):
        p = self.doc.add_paragraph(style="Heading 4")
        p.add_run(text)
        return p

    def bullets(self, items, size=12, spacing=1.32, space_after=1, level=0, marker="•"):
        out = []
        for it in items:
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Inches(0.30 + 0.28 * level)
            pf.first_line_indent = Inches(-0.22)
            pf.line_spacing = spacing
            pf.space_after = Pt(space_after)
            r = p.add_run(marker + "\t")
            r.font.size = Pt(size)
            self._rich(p, it, size)
            for run in p.runs:
                run.font.size = Pt(size)
            out.append(p)
        return out

    def numbered(self, items, size=12, spacing=1.32, space_after=1, start=1, prefix="("):
        for i, it in enumerate(items, start):
            p = self.doc.add_paragraph()
            pf = p.paragraph_format
            pf.left_indent = Inches(0.38)
            pf.first_line_indent = Inches(-0.30)
            pf.line_spacing = spacing
            pf.space_after = Pt(space_after)
            r = p.add_run("%s%d)%s " % (prefix if prefix != "(" else "(", i, ""))
            r.font.size = Pt(size)
            self._rich(p, it, size)
            for run in p.runs:
                run.font.size = Pt(size)

    def definition(self, term, text, size=12, spacing=1.4, space_after=6):
        p = self.doc.add_paragraph()
        pf = p.paragraph_format
        pf.left_indent = Inches(0.30)
        pf.line_spacing = spacing
        pf.space_after = Pt(space_after)
        r = p.add_run(term + "  ")
        r.bold = True
        r.font.size = Pt(size)
        self._rich(p, text, size)
        for run in p.runs:
            run.font.size = Pt(size)
        return p

    # ---------------------------------------------------------------- figures
    def figure(self, path, caption, width_in=6.2, chapter=None, space_after=3,
               max_h_in=3.95):
        """Insert a picture, scaled so that it never exceeds the text column.

        The image is fitted to min(max width, max height) while preserving its
        aspect ratio, so a tall screenshot cannot overflow the page.
        """
        self.fig_no += 1
        label = ("%s %s.%d" % (LBL["fig"], chapter, self.fig_no) if chapter
                 else "%s %d" % (LBL["fig"], self.fig_no))

        try:
            from PIL import Image
            with Image.open(path) as im:
                px_w, px_h = im.size
            aspect = px_h / float(px_w)
        except Exception:
            aspect = 0.62
        width_in = min(width_in, 6.27, max_h_in / aspect if aspect > 0 else 6.27)
        width_in = max(width_in, 1.4)

        p = self.doc.add_paragraph()
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p.paragraph_format.space_before = Pt(3)
        p.paragraph_format.space_after = Pt(1)
        p.paragraph_format.line_spacing = 1.0
        keep_with_next(p)
        p.add_run().add_picture(path, width=Inches(width_in))

        cap = self.doc.add_paragraph()
        cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
        cap.paragraph_format.space_after = Pt(space_after + 5)
        cap.paragraph_format.line_spacing = 1.15
        r = cap.add_run(label + LBL["sep"])
        r.bold = True
        r.font.size = Pt(10)
        r2 = cap.add_run(caption)
        r2.font.size = Pt(10)
        r2.italic = True
        self.figures.append((label, caption))
        return label

    def reset_figure_counter(self):
        self.fig_no = 0

    def reset_table_counter(self):
        self.tab_no = 0

    # ---------------------------------------------------------------- tables
    def table(self, caption, headers, rows, widths=None, size=8.4, chapter=None,
              zebra=True, align=None, space_after=4, number=None):
        self.tab_no += 1
        label = number or ("%s %s.%d" % (LBL["tab"], chapter, self.tab_no) if chapter
                           else "%s %d" % (LBL["tab"], self.tab_no))

        cap = self.doc.add_paragraph()
        cap.paragraph_format.space_before = Pt(3)
        cap.paragraph_format.space_after = Pt(2)
        cap.paragraph_format.line_spacing = 1.15
        keep_with_next(cap)
        r = cap.add_run(label + LBL["sep"])
        r.bold = True
        r.font.size = Pt(10)
        r2 = cap.add_run(caption)
        r2.italic = True
        r2.font.size = Pt(10)

        tbl = self.doc.add_table(rows=1, cols=len(headers))
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        _set_borders(tbl, top=(12, RULE), bottom=(12, RULE), inside_h=(4, "D6DEE6"))
        _cell_margins(tbl, top=26, bottom=26, left=62, right=62)

        hdr = tbl.rows[0].cells
        for i, h in enumerate(headers):
            hdr[i].text = ""
            p = hdr[i].paragraphs[0]
            p.paragraph_format.line_spacing = 1.08
            p.paragraph_format.space_after = Pt(1)
            run = p.add_run(str(h))
            run.bold = True
            run.font.size = Pt(size)
            _shade(hdr[i], HEAD_FILL)
        # repeat the header row on every page
        trPr = tbl.rows[0]._tr.get_or_add_trPr()
        trPr.append(_el("w:tblHeader"))

        for ri, row in enumerate(rows):
            cells = tbl.add_row().cells
            for ci, val in enumerate(row):
                cells[ci].text = ""
                p = cells[ci].paragraphs[0]
                p.paragraph_format.line_spacing = 1.08
                p.paragraph_format.space_after = Pt(1)
                if align and align[ci] == "r":
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                elif align and align[ci] == "c":
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                self._rich(p, str(val), size)
                for run in p.runs:
                    run.font.size = Pt(size)
                if zebra and ri % 2 == 1:
                    _shade(cells[ci], ZEBRA_FILL)

        if widths:
            total = sum(widths)
            for r_ in tbl.rows:
                for i, w in enumerate(widths):
                    r_.cells[i].width = Inches(6.27 * w / total)

        tail = self.doc.add_paragraph()
        tail.paragraph_format.space_after = Pt(space_after)
        tail.paragraph_format.line_spacing = 1.0
        tail.add_run("").font.size = Pt(2)
        self.tables.append((label, caption))
        return label

    # ---------------------------------------------------------------- front matter
    def toc(self, title="Table of Contents", depth=3):
        self.heading_plain(title)
        p = self.doc.add_paragraph()
        p.paragraph_format.line_spacing = 1.3
        add_field(p, ' TOC \\o "1-%d" \\h \\z \\u ' % depth,
                  "Select all and press F9 to build the table of contents.")
        self.doc.add_page_break()

    def static_list(self, title, entries, placeholder="—"):
        self.heading_plain(title)
        tbl = self.doc.add_table(rows=0, cols=3)
        tbl.alignment = WD_TABLE_ALIGNMENT.CENTER
        tbl.autofit = False
        _set_borders(tbl, top=(12, RULE), bottom=(12, RULE), inside_h=(4, "D6DEE6"))
        _cell_margins(tbl, top=40, bottom=40)
        for label, caption, page in entries:
            cells = tbl.add_row().cells
            for ci, val in enumerate((label, caption, page)):
                cells[ci].text = ""
                p = cells[ci].paragraphs[0]
                p.paragraph_format.line_spacing = 1.1
                p.paragraph_format.space_after = Pt(1)
                if ci == 2:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
                r = p.add_run(str(val))
                r.font.size = Pt(10)
                if ci == 0:
                    r.bold = True
            cells[0].width = Inches(0.95)
            cells[1].width = Inches(4.97)
            cells[2].width = Inches(0.35)
        self.doc.add_page_break()

    def heading_plain(self, text):
        p = self.doc.add_paragraph(style="Heading 1")
        p.paragraph_format.space_before = Pt(0)
        p.add_run(text)
        return p

    # ---------------------------------------------------------------- structural
    def page_break(self):
        self.doc.add_page_break()

    def new_section(self, page_numbers=True, fmt="decimal", start=None, restart=True,
                    header_text=None):
        s = self.doc.add_section(WD_SECTION.NEW_PAGE)
        s.page_width, s.page_height = Cm(21.0), Cm(29.7)
        s.left_margin = s.right_margin = s.top_margin = s.bottom_margin = Inches(1)
        s.footer_distance = Inches(0.5)
        s.header_distance = Inches(0.5)
        s.footer.is_linked_to_previous = False
        s.header.is_linked_to_previous = False
        if page_numbers:
            p = s.footer.paragraphs[0]
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.line_spacing = 1.0
            add_field(p, " PAGE \\* %s " % ("ROMAN" if fmt == "roman" else "ARABIC"), "1")
            for r in p.runs:
                r.font.size = Pt(10)
                r.font.name = BODY_FONT
        if header_text:
            hp = s.header.paragraphs[0]
            hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            hp.paragraph_format.line_spacing = 1.0
            r = hp.add_run(header_text)
            r.font.size = Pt(9)
            r.font.color.rgb = MUTED
        if restart:
            sectPr = s._sectPr
            pg = _el("w:pgNumType", **{"w:fmt": "upperRoman" if fmt == "roman" else "decimal"})
            if start is not None:
                pg.set(qn("w:start"), str(start))
            sectPr.append(pg)
        return s

    def save(self, path):
        self.doc.save(path)
        return path


def add_footer_page_numbers(report, first_section=True, fmt="decimal", start=1):
    s = report.doc.sections[0]
    s.footer.is_linked_to_previous = False
    p = s.footer.paragraphs[0]
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p.paragraph_format.line_spacing = 1.0
    add_field(p, " PAGE \\* %s " % ("ROMAN" if fmt == "roman" else "ARABIC"), "1")
    for r in p.runs:
        r.font.size = Pt(10)
        r.font.name = BODY_FONT
    pg = _el("w:pgNumType", **{"w:fmt": "upperRoman" if fmt == "roman" else "decimal"})
    if start is not None:
        pg.set(qn("w:start"), str(start))
    s._sectPr.append(pg)
