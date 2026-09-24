# svgkit.py - a tiny SVG drawing kit for report figures.
# Light theme, print-friendly, fixed visual language:
#   steel blue = app / primary component, teal = data layer, amber = external / highlighted,
#   grey = neutral container, red = error / failure path.
import html as _html
import os

# ---------------------------------------------------------------- palette
INK = "#14181f"
MUTED = "#5b6472"
FAINT = "#8b95a3"
LINE = "#9aa5b1"
GRID = "#dde3ea"

PRIMARY = "#2f5d8c"
PRIMARY_F = "#eaf1f8"
TEAL = "#0f766e"
TEAL_F = "#e6f4f2"
AMBER = "#a8610a"
AMBER_F = "#fdf3e4"
GREY = "#5b6472"
GREY_F = "#f4f6f8"
RED = "#b3261e"
RED_F = "#fdeceb"
GREEN = "#2f7d4f"
GREEN_F = "#eaf5ee"
VIOLET = "#5b4a9e"
VIOLET_F = "#efecf9"

FONT = "Arial, 'Segoe UI', Helvetica, sans-serif"
MONO = "'Consolas', 'Courier New', monospace"


def esc(s):
    return _html.escape(str(s), quote=True)


# Coordinate scale applied to every diagram.  The docx places figures at a fixed
# physical width, so what governs legibility is font_px / canvas_px.  Shrinking
# the drawing while keeping the type sizes raises that ratio by 1/K.
K = float(os.environ.get("DIAGRAM_K", "0.62"))

# Optional label translation.  A figure module installs a dict of english ->
# localized strings; anything absent passes through untouched, so code,
# identifiers and enumerated constants keep their source form.
TR = {}


def set_translation(mapping):
    global TR
    TR = dict(mapping or {})


def T(s):
    return TR.get(s, s)


def is_cjk(ch):
    o = ord(ch)
    return 0x2E80 <= o <= 0x9FFF or 0xF900 <= o <= 0xFAFF or 0xFF00 <= o <= 0xFF65


def adv_ratio(text):
    """Average advance width per character, in units of the font size.

    Latin glyphs average roughly half an em in Arial; CJK glyphs are full width,
    so a Chinese label needs about twice the character budget of an English one.
    """
    if not text:
        return 0.52
    n = len(text)
    cjk = sum(1 for ch in text if is_cjk(ch))
    return (cjk * 1.0 + (n - cjk) * 0.52) / n


def fit_chars(text, avail_px, font_px):
    return max(3, int(avail_px / (font_px * adv_ratio(text))))


class Canvas:
    """Collects SVG shapes then emits a standalone <svg> document string."""

    def __init__(self, width, height, background="#ffffff", k=None):
        self.k = K if k is None else k
        self.W = width
        self.H = height
        self.w = max(1, int(round(width * self.k)))
        self.h = max(1, int(round(height * self.k)))
        self.bg = background
        self.parts = []
        self._defs = []
        self._markers_seen = set()

    def s(self, v):
        return round(v * self.k, 2)

    # ------------------------------------------------------------ defs
    def _ensure_marker(self, name, color):
        key = (name, color)
        if key in self._markers_seen:
            return
        self._markers_seen.add(key)
        if name == "arrow":
            self._defs.append(
                f'<marker id="arw-{color.lstrip("#")}" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="7" markerHeight="7" orient="auto-start-reverse">'
                f'<path d="M 0 1 L 10 5 L 0 9 z" fill="{color}"/></marker>')
        elif name == "arrow-o":
            self._defs.append(
                f'<marker id="arwo-{color.lstrip("#")}" viewBox="0 0 12 12" refX="10" refY="6" '
                f'markerWidth="8" markerHeight="8" orient="auto-start-reverse">'
                f'<path d="M 0 1.5 L 11 6 L 0 10.5" fill="none" stroke="{color}" stroke-width="1.6"/></marker>')
        elif name == "diamond":
            self._defs.append(
                f'<marker id="dia-{color.lstrip("#")}" viewBox="0 0 12 12" refX="11" refY="6" '
                f'markerWidth="11" markerHeight="11" orient="auto-start-reverse">'
                f'<path d="M 0 6 L 6 1 L 12 6 L 6 11 z" fill="{color}"/></marker>')

    @staticmethod
    def _marker_url(name, color):
        if name == "arrow":
            return f'url(#arw-{color.lstrip("#")})'
        if name == "arrow-o":
            return f'url(#arwo-{color.lstrip("#")})'
        if name == "diamond":
            return f'url(#dia-{color.lstrip("#")})'
        return None

    # ------------------------------------------------------------ primitives
    def rect(self, x, y, w, h, fill="#ffffff", stroke=LINE, sw=1.4, rx=8,
             dash=None, shadow=False, opacity=None):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        o = f' opacity="{opacity}"' if opacity is not None else ""
        f = f' filter="url(#soft)"' if shadow else ""
        self.parts.append(
            f'<rect x="{self.s(x)}" y="{self.s(y)}" width="{self.s(w)}" '
            f'height="{self.s(h)}" rx="{self.s(rx)}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}"{d}{o}{f}/>')

    def line(self, x1, y1, x2, y2, stroke=LINE, sw=1.4, dash=None, arrow=None,
             arrow_start=None, cap="round"):
        d = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if arrow:
            self._ensure_marker("arrow", arrow)
            m += f' marker-end="{self._marker_url("arrow", arrow)}"'
        if arrow_start:
            self._ensure_marker("arrow", arrow_start)
            m += f' marker-start="{self._marker_url("arrow", arrow_start)}"'
        self.parts.append(
            f'<line x1="{self.s(x1)}" y1="{self.s(y1)}" x2="{self.s(x2)}" '
            f'y2="{self.s(y2)}" stroke="{stroke}" stroke-width="{sw}" '
            f'stroke-linecap="{cap}"{d}{m}/>')

    def path(self, d, stroke=LINE, sw=1.4, fill="none", dash=None, arrow=None, arrow_start=None):
        da = f' stroke-dasharray="{dash}"' if dash else ""
        m = ""
        if arrow:
            self._ensure_marker("arrow", arrow)
            m += f' marker-end="{self._marker_url("arrow", arrow)}"'
        if arrow_start:
            self._ensure_marker("arrow", arrow_start)
            m += f' marker-start="{self._marker_url("arrow", arrow_start)}"'
        self.parts.append(
            f'<path d="{self.scale_path(d)}" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="{sw}" stroke-linejoin="round"{da}{m}/>')

    def scale_path(self, d):
        """Scale every number appearing in an SVG path command string."""
        out = []
        for tok in str(d).replace(",", " ").split():
            try:
                out.append(str(self.s(float(tok))))
            except ValueError:
                out.append(tok)
        return " ".join(out)

    def poly(self, pts, fill="#ffffff", stroke=LINE, sw=1.4, dash=None):
        p = " ".join("%s,%s" % (self.s(a), self.s(b)) for a, b in pts)
        d = f' stroke-dasharray="{dash}"' if dash else ""
        self.parts.append(f'<polygon points="{p}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"{d}/>')

    def circle(self, cx, cy, r, fill="#ffffff", stroke=LINE, sw=1.4):
        self.parts.append(
            f'<circle cx="{self.s(cx)}" cy="{self.s(cy)}" r="{self.s(r)}" '
            f'fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def ellipse(self, cx, cy, rx, ry, fill="#ffffff", stroke=LINE, sw=1.4):
        self.parts.append(
            f'<ellipse cx="{self.s(cx)}" cy="{self.s(cy)}" rx="{self.s(rx)}" '
            f'ry="{self.s(ry)}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')

    def text(self, x, y, s, size=12, fill=INK, anchor="start", weight="normal",
             style="normal", family=None, ls=None):
        s = T(s)
        fam = family or FONT
        extra = f' letter-spacing="{ls}"' if ls else ""
        self.parts.append(
            f'<text x="{self.s(x)}" y="{self.s(y)}" font-family="{fam}" '
            f'font-size="{size}" fill="{fill}" text-anchor="{anchor}" '
            f'font-weight="{weight}" font-style="{style}"{extra}>{esc(s)}</text>')

    def multiline(self, x, y, lines, size=12, fill=INK, anchor="start", weight="normal",
                  lh=None, family=None):
        lh = lh or size * 1.32
        for i, ln in enumerate(lines):
            self.text(x, y + i * lh, ln, size=size, fill=fill, anchor=anchor,
                      weight=weight, family=family)

    def textblock(self, x, y, s, size=12, fill=INK, anchor="middle", weight="normal",
                  max_chars=None, lh=None, family=None):
        """Draw text, wrapping on spaces at roughly max_chars per line."""
        lines = wrap(s, max_chars) if max_chars else [s]
        self.multiline(x, y, lines, size=size, fill=fill, anchor=anchor,
                       weight=weight, lh=lh, family=family)

    # ------------------------------------------------------------ composites
    def box(self, x, y, w, h, label, sub=None, fill="#ffffff", stroke=LINE, sw=1.4,
            title_size=12.5, sub_size=10.5, ink=INK, sub_ink=MUTED, rx=8, dash=None,
            shadow=False, wrap_chars=None, badge=None, badge_fill=None):
        self.rect(x, y, w, h, fill=fill, stroke=stroke, sw=sw, rx=rx, dash=dash, shadow=shadow)
        cx = x + w / 2
        label = T(label)
        sub = T(sub)
        wrap_chars = wrap_chars or fit_chars(label or sub or "", w - 18, title_size)
        lines = wrap(label, wrap_chars) if label else []
        sub_lines = wrap(sub, wrap_chars) if sub else []
        total = len(lines) * title_size * 1.3 + (len(sub_lines) * sub_size * 1.35 if sub_lines else 0)
        top = y + h / 2 - total / 2 + title_size * 0.95
        if sub_lines:
            top -= 1.5
        self.multiline(cx, top, lines, size=title_size, fill=ink, anchor="middle",
                       weight="bold", lh=title_size * 1.3)
        if sub_lines:
            self.multiline(cx, top + len(lines) * title_size * 1.3 + sub_size * 0.6,
                           sub_lines, size=sub_size, fill=sub_ink, anchor="middle",
                           lh=sub_size * 1.35)
        if badge:
            bw = max(38, len(badge) * 6.6 + 12)
            self.rect(x + w - bw - 8, y + 8, bw, 17, fill=badge_fill or GREY_F,
                      stroke="none", rx=8.5)
            self.text(x + w - bw / 2 - 8, y + 20, badge, size=9.5, fill=sub_ink,
                      anchor="middle", weight="bold")

    def actor(self, x, y, label, fill=GREY_F, stroke=GREY, scale=1.0, sub=None):
        """Stick-figure actor. (x, y) is the centre top of the head."""
        r = 9 * scale
        self.circle(x, y, r, fill=fill, stroke=stroke, sw=1.5)
        self.line(x, y + r, x, y + r + 26 * scale, stroke=stroke, sw=1.5)
        self.line(x - 14 * scale, y + r + 10 * scale, x + 14 * scale, y + r + 10 * scale, stroke=stroke, sw=1.5)
        self.line(x, y + r + 26 * scale, x - 11 * scale, y + r + 44 * scale, stroke=stroke, sw=1.5)
        self.line(x, y + r + 26 * scale, x + 11 * scale, y + r + 44 * scale, stroke=stroke, sw=1.5)
        ty = y + r + 44 * scale + 15 * scale
        self.text(x, ty, label, size=11.5 * scale, fill=INK, anchor="middle", weight="bold")
        if sub:
            self.text(x, ty + 13 * scale, sub, size=9.5 * scale, fill=MUTED, anchor="middle")

    def arrow_label(self, x, y, s, size=10, fill=MUTED, anchor="middle", weight="normal",
                    bg=None):
        if bg:
            w = len(s) * size * 0.55 + 8
            self.rect(x - w / 2, y - size * 0.95, w, size * 1.5, fill=bg, stroke="none", rx=3)
        self.text(x, y, s, size=size, fill=fill, anchor=anchor, weight=weight)

    def seq_actor(self, x, y, w, label, fill=PRIMARY_F, stroke=PRIMARY, sub=None, h=40):
        self.rect(x - w / 2, y, w, h, fill=fill, stroke=stroke, rx=6)
        ty = y + (h / 2 + 4 if not sub else h / 2 - 3)
        self.text(x, ty, label, size=11.5, fill=INK, anchor="middle", weight="bold")
        if sub:
            self.text(x, y + h / 2 + 12, sub, size=9.5, fill=MUTED, anchor="middle")

    def selfcall(self, x, y, w, h, label, size=10.5, stroke=PRIMARY, fill="#ffffff"):
        self.path(f"M {x} {y} h {w} v {h} h {-w}", stroke=stroke, sw=1.3,
                  arrow=stroke, fill="none")
        self.text(x + w + 6, y + h / 2 + 3.5, label, size=size, fill=INK)

    def note(self, x, y, w, h, lines, fill=AMBER_F, stroke=AMBER, size=10, fold=12):
        self.path(
            f"M {x} {y} h {w - fold} l {fold} {fold} v {h - fold} h {-w} z",
            fill=fill, stroke=stroke, sw=1.2)
        self.path(f"M {x + w - fold} {y} v {fold} h {fold}", fill="none", stroke=stroke, sw=1.2)
        if isinstance(lines, str):
            lines = [lines]
        lines = [T(x) for x in lines]
        maxc = fit_chars(" ".join(lines), w - 24, size)
        flat = []
        for chunk in lines:
            flat.extend(wrap(chunk, maxc))
        self.multiline(x + 9, y + size + 6, flat, size=size, fill=INK, lh=size * 1.38)

    def legend(self, x, y, items, size=10, gap=15, swatch=11):
        """items = [(label, fill, stroke), ...] laid out horizontally."""
        cx = x
        for label, fill, stroke in items:
            self.rect(cx, y - swatch + 2, swatch, swatch, fill=fill, stroke=stroke, rx=2.5, sw=1.1)
            self.text(cx + swatch + 5, y + 1.5, label, size=size, fill=MUTED)
            lab = T(label)
            cx += swatch + 5 + len(lab) * size * adv_ratio(lab) + gap

    # ------------------------------------------------------------ output
    def svg(self):
        defs = ('<filter id="soft" x="-12%" y="-12%" width="124%" height="124%">'
                '<feDropShadow dx="0" dy="1.6" stdDeviation="2" flood-color="#0f172a" '
                'flood-opacity="0.10"/></filter>')
        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" width="{self.w}" height="{self.h}" '
            f'viewBox="0 0 {self.w} {self.h}">'
            f'<defs>{defs}{"".join(self._defs)}</defs>'
            f'<rect width="{self.w}" height="{self.h}" fill="{self.bg}"/>'
            f'{"".join(self.parts)}</svg>')

    def html(self, scale=2):
        return (f'<!DOCTYPE html><html><head><meta charset="utf-8">'
                f'<style>html,body{{margin:0;padding:0;background:#fff;}}'
                f'svg{{display:block;width:{self.w}px;height:{self.h}px;}}</style></head>'
                f'<body>{self.svg()}</body></html>')


def wrap(text, max_chars):
    """Greedy word wrap; honour explicit \n."""
    if text is None:
        return []
    out = []
    for para in str(text).split("\n"):
        words = para.split()
        if not words:
            out.append("")
            continue
        pieces = []
        for word in words:
            while len(word) > max_chars:          # CJK runs carry no spaces
                pieces.append(word[:max_chars])
                word = word[max_chars:]
            pieces.append(word)
        line = pieces[0]
        for w in pieces[1:]:
            joined = line + " " + w
            if len(joined) <= max_chars:
                line = joined
            else:
                out.append(line)
                line = w
        out.append(line)
    return out


def title_block(c, title, subtitle=None, y=26):
    """Small figure-internal title (used sparingly; captions live in the docx)."""
    c.text(0, y, title, size=13, weight="bold")
    if subtitle:
        c.text(0, y + 16, subtitle, size=10.5, fill=MUTED)
