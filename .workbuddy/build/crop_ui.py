# crop_ui.py - derive legible detail figures from the full interface captures.
# A full-page capture is fine as an overview, but its body text is unreadable once
# the image is scaled to a 6.27 in text column. Cropping the region of interest and
# placing it at a smaller physical width keeps the interface type at 7-9 pt.
import os

from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "figures")

# (source, output, left, top, right, bottom) as fractions of the capture
CROPS = [
    ("ui_detail_buyer_vp.png", "ui_crop_buy_panel", 0.480, 0.09, 0.855, 0.80),
    ("ui_detail_seller_vp.png", "ui_crop_sell_panel", 0.480, 0.09, 0.855, 0.80),
    ("ui_publish_vp.png", "ui_crop_publish", 0.05, 0.11, 0.50, 1.0),
    ("ui_chat_vp.png", "ui_crop_chat", 0.300, 0.09, 0.700, 0.95),
    ("ui_confirm_vp.png", "ui_crop_confirm", 0.355, 0.32, 0.645, 0.64),
    ("ui_profile_items_vp.png", "ui_crop_profile", 0.06, 0.02, 0.62, 0.42),
    ("ui_home_vp.png", "ui_crop_grid", 0.06, 0.30, 0.70, 0.86),
    ("ui_empty_vp.png", "ui_crop_empty", 0.22, 0.28, 0.78, 0.74),
]


def main():
    for src, out, l, t, r, b in CROPS:
        im = Image.open(os.path.join(SRC, src))
        W, H = im.size
        box = (int(l * W), int(t * H), int(r * W), int(b * H))
        crop = im.crop(box)
        path = os.path.join(SRC, out + ".png")
        crop.save(path)
        print("ok  %-22s from %-24s %4dx%-5d  (aspect %.2f)"
              % (out, src, crop.width, crop.height, crop.height / crop.width))


if __name__ == "__main__":
    main()
