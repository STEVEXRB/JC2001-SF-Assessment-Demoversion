from svgkit import *


def f():
    c = Canvas(760, 300)
    c.box(30, 40, 200, 80, "Browser", "HTML / CSS / JS", fill=GREY_F, stroke=GREY)
    c.box(300, 40, 180, 80, "Flask app", "app.py", fill=PRIMARY_F, stroke=PRIMARY)
    c.box(530, 40, 190, 80, "SQLite", "data.db", fill=TEAL_F, stroke=TEAL)
    c.line(230, 80, 300, 80, arrow=PRIMARY, sw=1.6)
    c.line(480, 80, 530, 80, arrow=TEAL, sw=1.6)
    c.arrow_label(265, 72, "HTTP", bg="#ffffff")
    c.arrow_label(505, 72, "SQL", bg="#ffffff")
    c.text(30, 200, "Probe figure - testing the SVG to PNG pipeline.", size=12, fill=MUTED)
    c.legend(30, 240, [("presentation", GREY_F, GREY), ("application", PRIMARY_F, PRIMARY),
                       ("data", TEAL_F, TEAL)])
    return c


FIGS = {"_probe": f}
ORDER = ["_probe"]
