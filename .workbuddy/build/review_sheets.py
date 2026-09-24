# review_sheets.py - tile rendered figures into a few sheets for visual review.
import os
import sys

from PIL import Image, ImageDraw, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "figures")
OUT = os.path.join(HERE, "review")

TILE_W = 900
PAD = 26
LABEL = 30

try:
    FONT = ImageFont.truetype("arialbd.ttf", 19)
except Exception:
    FONT = ImageFont.load_default()


def sheet(name, names, cols=2):
    tiles = []
    for n in names:
        p = os.path.join(SRC, n + ".png")
        im = Image.open(p).convert("RGB")
        im = im.resize((TILE_W, max(1, int(im.height * TILE_W / im.width))), Image.LANCZOS)
        tiles.append((n, im))
    rows = (len(tiles) + cols - 1) // cols
    rh = max(t[1].height for t in tiles) + LABEL
    W = cols * (TILE_W + PAD) + PAD
    H = rows * (rh + PAD) + PAD
    canvas = Image.new("RGB", (W, H), "#e9edf2")
    d = ImageDraw.Draw(canvas)
    for i, (n, im) in enumerate(tiles):
        r, c = divmod(i, cols)
        x = PAD + c * (TILE_W + PAD)
        y = PAD + r * (rh + PAD)
        d.text((x + 3, y + 6), n, fill="#14181f", font=FONT)
        canvas.paste(im, (x, y + LABEL))
    os.makedirs(OUT, exist_ok=True)
    path = os.path.join(OUT, name + ".png")
    canvas.save(path)
    print("ok", path, canvas.size)


if __name__ == "__main__":
    groups = {
        "r1": ["fig_ctx", "fig_bpm_trade", "fig_arch_layers", "fig_arch_modules"],
        "r2": ["fig_class_domain", "fig_er", "fig_state_item", "fig_route_map"],
        "r3": ["fig_algo_status", "fig_algo_conversation", "fig_stack", "fig_ui_states"],
        "r4": ["fig_seq_publish", "fig_seq_deal", "fig_seq_message", "fig_act_publish"],
        "r5": ["fig_usecase", "fig_route_map"],
    }
    for k, v in groups.items():
        sheet(k, v)
