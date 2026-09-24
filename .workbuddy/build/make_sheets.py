# make_sheets.py - compose contact sheets from the interface captures.
# Grouping four screens per sheet keeps the evidence in the report while using a
# fraction of the pages.
import os
from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "figures")
OUT = SRC

CELL_W = 1180
GUTTER = 44
LABEL_H = 52
BG = "#ffffff"
FRAME = "#c8d2dd"
TEXT = "#14181f"

try:
    FONT = ImageFont.truetype("arialbd.ttf", 27)
except Exception:
    FONT = ImageFont.load_default()


def sheet(name, cells, cols=2):
    """cells = [(file, label), ...] laid out in a grid."""
    tiles = []
    for fn, label in cells:
        im = Image.open(os.path.join(SRC, fn)).convert("RGB")
        w, h = im.size
        nh = int(h * CELL_W / w)
        im = im.resize((CELL_W, nh), Image.LANCZOS)
        tiles.append((im, label))

    rows = (len(tiles) + cols - 1) // cols
    row_h = max(t[0].height for t in tiles) + LABEL_H
    width = cols * CELL_W + (cols + 1) * GUTTER
    height = rows * row_h + (rows + 1) * GUTTER

    canvas = Image.new("RGB", (width, height), BG)
    d = ImageDraw.Draw(canvas)
    for i, (im, label) in enumerate(tiles):
        r, c = divmod(i, cols)
        x = GUTTER + c * (CELL_W + GUTTER)
        y = GUTTER + r * (row_h + GUTTER)
        d.text((x + 2, y + 12), label, fill=TEXT, font=FONT)
        canvas.paste(im, (x, y + LABEL_H))
        d.rectangle([x, y + LABEL_H, x + im.width - 1, y + LABEL_H + im.height - 1],
                    outline=FRAME, width=2)

    path = os.path.join(OUT, name + ".png")
    canvas.save(path)
    print("ok  %-26s %5dx%-5d %6.1f KB" % (name, canvas.width, canvas.height,
                                           os.path.getsize(path) / 1024))


if __name__ == "__main__":
    sheet("ui_sheet_browse", [
        ("ui_home.png", "(a)  The catalogue: header, hero, category chips, listing grid"),
        ("ui_search.png", "(b)  A keyword search, with the matching count stated"),
        ("ui_empty.png", "(c)  A search that matches nothing: the empty state"),
        ("ui_auth.png", "(d)  Log in and sign up, sharing one view"),
    ])
    sheet("ui_sheet_detail", [
        ("ui_detail_guest.png", "(a)  Detail as an anonymous visitor sees it"),
        ("ui_detail_buyer.png", "(b)  Detail for a signed-in buyer"),
        ("ui_detail_seller.png", "(c)  Detail for the seller: management actions only"),
        ("ui_confirm.png", "(d)  The shared confirmation dialog"),
    ])
    sheet("ui_sheet_profile", [
        ("ui_profile_items.png", "(a)  Personal centre: profile summary and own listings"),
        ("ui_profile_favourites.png", "(b)  Saved listings"),
        ("ui_profile_messages.png", "(c)  Conversation list, one row per partner"),
        ("ui_chat.png", "(d)  An open conversation"),
    ])
