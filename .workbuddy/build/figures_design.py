# figures_design.py - architecture, domain model and state figures (Chapter 4)
from svgkit import *


# ---------------------------------------------------------------- 4.1 layers
def arch_layers():
    c = Canvas(960, 726)
    c.text(24, 34, "Layered architecture and the responsibility of each layer", size=13, weight="bold")

    bands = [
        (76, 158, "Presentation layer", "runs in the browser", GREY_F, GREY),
        (252, 260, "Application layer", "Flask route handlers in app.py", PRIMARY_F, PRIMARY),
        (528, 168, "Data layer", "persistence and file storage", TEAL_F, TEAL),
    ]
    for y, h, name, sub, f, st in bands:
        c.rect(24, y, 912, h, fill="#ffffff", stroke=GRID, rx=10)
        c.rect(24, y, 190, h, fill=f, stroke=st, rx=10)
        c.text(119, y + h / 2 - 6, name, size=12, weight="bold", anchor="middle")
        c.text(119, y + h / 2 + 12, sub, size=9.2, fill=MUTED, anchor="middle")

    # presentation
    pres = [("index.html", "5 views + 2 modals + icon sprite"),
            ("style.css", "design tokens · components · responsive"),
            ("api.js / main.js", "state, rendering, event wiring")]
    for i, (t, s) in enumerate(pres):
        x = 232 + i * 234
        c.box(x, 112, 220, 84, t, s, fill="#ffffff", stroke=GREY, title_size=11.5, sub_size=9.2,
              wrap_chars=24)

    # application
    routes = [("Auth", "/register · /login · /logout · /user/me"),
              ("Catalogue", "GET /items · GET /items/<id>"),
              ("Listing CRUD", "POST · PUT · DELETE /items/<id>"),
              ("Upload", "POST /upload"),
              ("Transitions", "POST /items/<id>/status"),
              ("Favourites", "GET · POST · DELETE /favorites"),
              ("Comments", "GET · POST /items/<id>/comments"),
              ("Messaging", "GET · POST /messages"),
              ("Personal centre", "GET /user/items · /user/sold")]
    for i, (t, s) in enumerate(routes):
        col, row = i % 3, i // 3
        x = 232 + col * 234
        y = 288 + row * 74
        c.rect(x, y, 220, 62, fill=PRIMARY_F, stroke=PRIMARY, rx=7, sw=1.3)
        c.text(x + 110, y + 25, t, size=11, anchor="middle", weight="bold")
        c.text(x + 110, y + 42, s, size=8.4, fill=MUTED, anchor="middle")

    # data
    data = [("models.get_db()", "connection factory · sqlite3.Row"),
            ("data.db", "users · items · images · favourites\ncomments · messages"),
            ("uploads/", "one file per uploaded photo")]
    for i, (t, s) in enumerate(data):
        x = 232 + i * 234
        c.box(x, 570, 220, 88, t, s, fill="#ffffff", stroke=TEAL, title_size=11.5, sub_size=9,
              wrap_chars=26)

    for x in (342, 576, 810):
        c.line(x, 234, x, 252, stroke=FAINT, sw=1.4, arrow=FAINT)
        c.line(x, 512, x, 528, stroke=FAINT, sw=1.4, arrow=FAINT)
    c.arrow_label(600, 306 - 22, "fetch() / JSON over HTTP", bg="#ffffff", size=9.5)
    c.arrow_label(600, 545, "SQL + file I/O", bg="#ffffff", size=9.5)

    return c


# ---------------------------------------------------------------- 4.2 modules
def arch_modules():
    c = Canvas(960, 620)
    c.text(24, 34, "Module decomposition and the direction of each dependency", size=13, weight="bold")

    c.box(40, 100, 210, 66, "templates/index.html", "escaped template, no logic",
          fill=GREY_F, stroke=GREY, title_size=11, sub_size=9)
    c.box(40, 200, 210, 60, "static/css/style.css", "design tokens + components",
          fill=GREY_F, stroke=GREY, title_size=11, sub_size=9)
    c.box(40, 300, 210, 60, "static/js/api.js", "one method per endpoint",
          fill=AMBER_F, stroke=AMBER, title_size=11, sub_size=9)
    c.box(40, 400, 210, 60, "static/js/main.js", "view state and rendering",
          fill=AMBER_F, stroke=AMBER, title_size=11, sub_size=9)

    c.box(392, 230, 216, 100, "app.py", "Flask app · 21 JSON endpoints\nlogin_required · upload config",
          fill=PRIMARY_F, stroke=PRIMARY, sw=2, title_size=12.5, sub_size=9, shadow=True, wrap_chars=28)
    c.box(392, 396, 216, 64, "models.py", "get_db() · init_db()",
          fill=TEAL_F, stroke=TEAL, title_size=11.5, sub_size=9)

    c.box(742, 132, 180, 62, "data.db", "six relational tables",
          fill=TEAL_F, stroke=TEAL, title_size=11.5, sub_size=9)
    c.box(742, 232, 180, 62, "uploads/", "one file per photo",
          fill=TEAL_F, stroke=TEAL, title_size=11.5, sub_size=9)
    c.box(742, 396, 180, 62, "Werkzeug", "hashing · secure_filename",
          fill=VIOLET_F, stroke=VIOLET, title_size=11.5, sub_size=9)

    c.line(250, 133, 392, 262, stroke=GREY, sw=1.3, arrow=GREY)
    c.line(145, 260, 145, 300, stroke=GREY, sw=1.2)
    c.line(250, 330, 392, 290, stroke=AMBER, sw=1.4, arrow=AMBER)
    c.line(145, 360, 145, 400, stroke=AMBER, sw=1.2)
    c.line(250, 430, 392, 320, stroke=AMBER, sw=1.4, arrow=AMBER)
    c.arrow_label(300, 214, "renders", size=9, bg="#ffffff")
    c.arrow_label(300, 336, "fetch()", size=9, bg="#ffffff")

    c.line(608, 300, 700, 300, stroke=PRIMARY, sw=1.4)
    c.line(700, 300, 700, 163, stroke=PRIMARY, sw=1.4, arrow=PRIMARY)
    c.line(742, 263, 700, 263, stroke=PRIMARY, sw=1.4)
    c.line(608, 172, 742, 163, stroke=TEAL, sw=1.4, arrow=TEAL)

    c.line(500, 396, 500, 330, stroke=TEAL, sw=1.4, arrow=TEAL)
    c.line(500, 460, 742, 427, stroke=VIOLET, sw=1.3, arrow=VIOLET, dash="5 4")

    c.arrow_label(700, 284, "SQL", size=9, bg="#ffffff")
    c.arrow_label(676, 214, "image files", size=9, bg="#ffffff")
    c.arrow_label(516, 386, "queries", size=9, bg="#ffffff")
    c.arrow_label(660, 478, "hash", size=9, bg="#ffffff")

    c.legend(40, 560, [("asset", GREY_F, GREY), ("script", AMBER_F, AMBER),
                       ("server", PRIMARY_F, PRIMARY), ("data", TEAL_F, TEAL),
                       ("library", VIOLET_F, VIOLET)])
    return c


# ---------------------------------------------------------------- 4.3 classes
def class_domain():
    c = Canvas(1040, 830)
    c.text(24, 34, "Domain class diagram (persistence-oriented)", size=13, weight="bold")

    def cls(x, y, name, stereo, attrs, w=280, methods=()):
        h_head = 26 + (14 if stereo else 0)
        h_attr = len(attrs) * 18 + 14
        h_meth = (len(methods) * 18 + 14) if methods else 0
        h = h_head + h_attr + h_meth
        c.rect(x, y, w, h, fill="#ffffff", stroke=INK, rx=6, sw=1.5)
        c.text(x + w / 2, y + 17, name, size=12, anchor="middle", weight="bold")
        if stereo:
            c.text(x + w / 2, y + 31, stereo, size=9, anchor="middle", fill=MUTED)
        c.line(x, y + h_head, x + w, y + h_head, stroke=INK, sw=1.1)
        for i, a in enumerate(attrs):
            c.text(x + 11, y + h_head + 15 + i * 18, a, size=9.2,
                   fill=MUTED if a.startswith("«") else INK)
        if methods:
            c.line(x, y + h_head + h_attr, x + w, y + h_head + h_attr, stroke=INK, sw=1.1)
            for i, m in enumerate(methods):
                c.text(x + 11, y + h_head + h_attr + 15 + i * 18, m, size=9.2)
        return h

    cls(40, 80, "User", None,
        ["- id : int  «PK»", "- username : str  «unique»", "- password_hash : str", "- nickname : str",
         "- email : str", "- student_id : str", "- avatar : str", "- created_at : datetime"])
    cls(380, 80, "Item", None,
        ["- id : int  «PK»", "- seller_id : int  «FK → User»", "- title : str", "- description : str",
         "- price : float", "- category : Category", "- condition : Condition", "- status : ItemStatus",
         "- created_at : datetime", "- updated_at : datetime"],
        methods=["+ is_owner(uid) : bool", "+ can_transition(action) : bool"])
    cls(720, 80, "Image", None,
        ["- id : int  «PK»", "- item_id : int  «FK → Item»", "- file_path : str",
         "- created_at : datetime"])

    cls(40, 430, "Comment", None,
        ["- id : int  «PK»", "- item_id : int  «FK → Item»", "- user_id : int  «FK → User»",
         "- content : str", "- created_at : datetime"])
    cls(380, 430, "Favorite", None,
        ["- id : int  «PK»", "- user_id : int  «FK → User»", "- item_id : int  «FK → Item»",
         "- created_at : datetime", "«unique» (user_id, item_id)"])
    cls(720, 430, "Message", None,
        ["- id : int  «PK»", "- sender_id : int  «FK → User»", "- receiver_id : int  «FK → User»",
         "- item_id : int  «FK → Item, nullable»", "- content : str", "- is_read : int",
         "- created_at : datetime"])

    cls(40, 650, "ItemStatus", "«enumeration»", ["ON_SALE", "RESERVED", "SOLD", "OFF_SHELF"])
    cls(380, 650, "Category", "«enumeration»",
        ["textbook", "digital", "daily_use", "sports_equipment", "other"])
    cls(720, 650, "Condition", "«enumeration»", ["new", "like_new", "good", "fair"])

    # ---- association 1: User 1 -- 0..* Item
    c.line(320, 170, 380, 170, stroke=PRIMARY, sw=1.5)
    c.text(334, 162, "1", size=10, anchor="middle", fill=MUTED, weight="bold")
    c.text(368, 162, "0..*", size=10, anchor="middle", fill=MUTED, weight="bold")
    c.text(350, 194, "sells", size=9.2, anchor="middle", fill=INK)

    # ---- association 2: Item 1 -- 0..* Image
    c.line(660, 150, 720, 150, stroke=PRIMARY, sw=1.5)
    c.text(672, 142, "1", size=10, anchor="middle", fill=MUTED, weight="bold")
    c.text(712, 138, "0..*", size=10, anchor="middle", fill=MUTED, weight="bold")
    c.text(690, 188, "has photos", size=9.2, anchor="middle", fill=INK)

    # ---- association 3: Item 1 -- 0..* Favorite
    c.line(520, 372, 520, 430, stroke=PRIMARY, sw=1.5)
    c.text(511, 388, "1", size=10, anchor="end", fill=MUTED, weight="bold")
    c.text(511, 424, "0..*", size=10, anchor="end", fill=MUTED, weight="bold")
    c.text(531, 406, "saved as", size=9.2, anchor="start", fill=INK)

    # ---- association 4: User 1 -- 0..* Comment
    c.line(180, 268, 180, 430, stroke=PRIMARY, sw=1.5)
    c.text(171, 288, "1", size=10, anchor="end", fill=MUTED, weight="bold")
    c.text(171, 424, "0..*", size=10, anchor="end", fill=MUTED, weight="bold")
    c.text(191, 356, "writes", size=9.2, anchor="start", fill=INK)

    # ---- association 5: Item 0..* -- 1 Comment (elbow to the left)
    c.path("M 380 340 H 260 V 430", stroke=PRIMARY, sw=1.5, arrow=PRIMARY)
    c.text(268, 332, "0..*", size=10, anchor="start", fill=MUTED, weight="bold")
    c.text(252, 424, "1", size=10, anchor="end", fill=MUTED, weight="bold")

    # ---- association 6: User 1 -- 0..* Favorite (diagonal across the free corner)
    c.line(300, 268, 395, 430, stroke=PRIMARY, sw=1.5)
    c.text(303, 282, "1", size=10, anchor="start", fill=MUTED, weight="bold")
    c.text(386, 424, "0..*", size=10, anchor="end", fill=MUTED, weight="bold")
    c.text(330, 392, "saves", size=9.2, anchor="middle", fill=INK)

    # ---- enumeration usage bus
    c.path("M 660 300 H 690 V 640 H 860", stroke=FAINT, sw=1.2, dash="5 4")
    c.path("M 690 640 H 180", stroke=FAINT, sw=1.2, dash="5 4")
    for xx in (180, 520, 860):
        c.line(xx, 640, xx, 650, stroke=FAINT, sw=1.2, arrow=FAINT)
    c.text(686, 470, "«uses»", size=9.2, fill=MUTED, anchor="end")
    return c


# ---------------------------------------------------------------- 4.4 ER
def er():
    c = Canvas(1080, 596)
    c.text(24, 34, "Entity-relationship diagram of the SQLite schema", size=13, weight="bold")

    def entity(x, y, name, rows, w=250):
        h = 30 + len(rows) * 19 + 10
        c.rect(x, y, w, h, fill="#ffffff", stroke=INK, rx=6, sw=1.5)
        c.rect(x, y, w, 30, fill=TEAL_F, stroke=TEAL, rx=6, sw=1.5)
        c.rect(x, y + 20, w, 10, fill=TEAL_F, stroke="none", rx=0)
        c.line(x, y + 30, x + w, y + 30, stroke=INK, sw=1.1)
        c.text(x + w / 2, y + 20, name, size=12, anchor="middle", weight="bold")
        for i, (col, kind) in enumerate(rows):
            yy = y + 30 + 14 + i * 19
            c.text(x + 10, yy, col, size=9.3,
                   weight="bold" if kind.startswith("PK") else "normal")
            c.text(x + w - 10, yy, kind, size=8.6, anchor="end",
                   fill=AMBER if kind.startswith("FK") else MUTED)
        return h

    entity(24, 80, "users", [
        ("id", "PK · INTEGER"), ("username", "UNIQUE"), ("password_hash", "NOT NULL"),
        ("nickname", "TEXT"), ("email", "TEXT"), ("student_id", "TEXT"), ("avatar", "TEXT"),
        ("created_at", "TIME")])
    entity(378, 80, "items", [
        ("id", "PK · INTEGER"), ("seller_id", "FK → users.id"), ("title", "TEXT"),
        ("description", "TEXT"), ("price", "REAL"), ("category", "TEXT"),
        ("condition", "TEXT"), ("status", "DEF ON_SALE"), ("created_at", "TIMESTAMP"),
        ("updated_at", "TIME")])
    entity(732, 80, "images", [
        ("id", "PK · INTEGER"), ("item_id", "FK → items.id"), ("file_path", "TEXT"),
        ("created_at", "TIMESTAMP")], w=230)
    entity(24, 330, "favorites", [
        ("id", "PK · INTEGER"), ("user_id", "FK → users.id"), ("item_id", "FK → items.id"),
        ("created_at", "TIMESTAMP"), ("UNIQUE (user_id, item_id)", "constraint")])
    entity(378, 400, "comments", [
        ("id", "PK · INTEGER"), ("item_id", "FK → items.id"), ("user_id", "FK → users.id"),
        ("content", "TEXT"), ("created_at", "TIMESTAMP")])
    entity(732, 330, "messages", [
        ("id", "PK · INTEGER"), ("sender_id", "FK → users.id"), ("receiver_id", "FK → users.id"),
        ("item_id", "FK → items.id"), ("content", "NOT NULL"), ("is_read", "DEF 0"),
        ("created_at", "TIMESTAMP")], w=230)

    def rel(x1, y1, x2, y2, left, right, label=None, lx=None, ly=None, dash=None):
        c.line(x1, y1, x2, y2, stroke=PRIMARY, sw=1.5, dash=dash)
        if left:
            c.text(x1 + (11 if abs(y2 - y1) < 2 else -4), y1 - 8, left, size=9.6,
                   fill=MUTED, weight="bold",
                   anchor="start" if abs(y2 - y1) < 2 else "end")
        if right:
            c.text(x2 - (11 if abs(y2 - y1) < 2 else -4), y2 - 8, right, size=9.6,
                   fill=MUTED, weight="bold",
                   anchor="end" if abs(y2 - y1) < 2 else "start")
        if label:
            c.text(lx, ly, label, size=9.2, fill=INK, anchor="middle")

    rel(274, 150, 378, 150, "1", "0..*", "sells", 326, 172)
    rel(628, 150, 732, 150, "1", "0..*", "illustrated by", 680, 172)
    rel(155, 272, 155, 330, "1", "0..*", "saves", 200, 306)
    c.path("M 274 390 H 420 V 310", stroke=PRIMARY, sw=1.5, arrow=PRIMARY)
    c.text(284, 382, "0..*", size=9.6, fill=MUTED, weight="bold", anchor="start")
    c.text(414, 322, "1", size=9.6, fill=MUTED, weight="bold", anchor="end")
    c.text(300, 414, "refers to", size=9.2, fill=INK, anchor="middle")
    rel(500, 310, 500, 400, "1", "0..*", "receives comments", 560, 362)
    c.path("M 274 240 H 300 V 400", stroke=PRIMARY, sw=1.5)
    c.line(300, 400, 378, 400, stroke=PRIMARY, sw=1.5, arrow=PRIMARY)
    c.text(310, 396, "1", size=9.6, fill=MUTED, weight="bold", anchor="start")
    c.text(292, 262, "1", size=9.6, fill=MUTED, weight="bold", anchor="end")
    c.text(306, 250, "writes", size=9.2, fill=INK, anchor="start")
    c.path("M 732 400 H 690 V 250 H 628", stroke=PRIMARY, sw=1.5, arrow=PRIMARY)
    c.text(724, 392, "0..*", size=9.6, fill=MUTED, weight="bold", anchor="end")
    c.text(636, 242, "1", size=9.6, fill=MUTED, weight="bold", anchor="end")
    c.text(700, 330, "about", size=9.2, fill=INK, anchor="start")

    return c


# ---------------------------------------------------------------- 4.5 state
def state_item():
    c = Canvas(900, 566)
    c.text(24, 34, "State machine governing the life cycle of a listing", size=13, weight="bold")

    def st(cx, cy, label, sub, fill, stroke):
        w, h = 168, 60
        c.rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, rx=14, sw=1.8)
        c.text(cx, cy - 2, label, size=12.5, anchor="middle", weight="bold")
        c.text(cx, cy + 16, sub, size=9, fill=MUTED, anchor="middle")

    st(160, 240, "ON_SALE", "visible in the catalogue", GREEN_F, GREEN)
    st(470, 240, "RESERVED", "held for one buyer", AMBER_F, AMBER)
    st(770, 240, "SOLD", "terminal outcome", GREY_F, GREY)
    st(470, 466, "OFF_SHELF", "hidden, reversible", RED_F, RED)

    c.circle(40, 240, 9, fill=INK, stroke=INK)
    c.line(49, 240, 76, 240, stroke=INK, sw=1.5, arrow=INK)
    c.text(40, 214, "initial", size=9, fill=MUTED, anchor="middle")

    c.line(244, 240, 386, 240, stroke=PRIMARY, sw=1.7, arrow=PRIMARY)
    c.text(315, 218, "reserve", size=10.2, anchor="middle", weight="bold")
    c.text(315, 234, "actor: buyer", size=9, fill=MUTED, anchor="middle")

    c.line(554, 240, 686, 240, stroke=PRIMARY, sw=1.7, arrow=PRIMARY)
    c.text(620, 218, "sell", size=10.2, anchor="middle", weight="bold")
    c.text(620, 234, "actor: seller", size=9, fill=MUTED, anchor="middle")

    c.path("M 470 210 V 150 H 160 V 210", stroke=FAINT, sw=1.5, arrow=FAINT)
    c.text(315, 142, "cancel_reserve  ·  actor: seller", size=10, anchor="middle", weight="bold")

    c.path("M 160 270 V 466 H 386", stroke=FAINT, sw=1.5, arrow=FAINT)
    c.text(268, 458, "off_shelf  ·  actor: seller", size=10, anchor="middle", weight="bold")

    c.path("M 470 496 V 552 H 96 V 270", stroke=FAINT, sw=1.5, arrow=FAINT)
    c.text(300, 544, "relist  ·  actor: seller", size=10, anchor="middle", weight="bold")

    return c


FIGS = {
    "fig_arch_layers": arch_layers,
    "fig_arch_modules": arch_modules,
    "fig_class_domain": class_domain,
    "fig_er": er,
    "fig_state_item": state_item,
}
ORDER = ["fig_arch_layers", "fig_arch_modules", "fig_class_domain", "fig_er", "fig_state_item"]
