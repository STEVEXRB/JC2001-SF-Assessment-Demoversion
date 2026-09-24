# figures_impl.py - implementation figures incl. sequence diagrams (Chapter 5)
from svgkit import *


# ------------------------------------------------------------ sequence helper
class Seq:
    def __init__(self, w, h, actors, head_y=84, head_h=46):
        self.c = Canvas(w, h)
        self.actors = actors           # [(x, label, sub), ...]
        self.head_y = head_y
        self.head_h = head_h
        self.bottom = head_h + head_y

    def draw_heads(self):
        for x, label, sub in self.actors:
            self.c.seq_actor(x, self.head_y, 176, label, sub=sub, h=self.head_h)

    def lines(self, bottom):
        for x, _, _ in self.actors:
            self.c.line(x, self.head_y + self.head_h, x, bottom, stroke=GRID, sw=1.2, dash="4 5")

    def msg(self, y, i, j, label, kind="call", lx=None, size=9.4):
        c = self.c
        x1, x2 = self.actors[i][0], self.actors[j][0]
        if kind == "call":
            c.line(x1, y, x2, y, stroke=PRIMARY, sw=1.5, arrow=PRIMARY)
        elif kind == "ret":
            c.line(x1, y, x2, y, stroke=FAINT, sw=1.2, dash="6 4", arrow=FAINT)
        elif kind == "meta":
            c.line(x1, y, x2, y, stroke=TEAL, sw=1.5, arrow=TEAL)
        c.arrow_label(lx if lx is not None else (x1 + x2) / 2, y - 8, label,
                      bg="#ffffff", size=size,
                      fill=PRIMARY if kind == "call" else (TEAL if kind == "meta" else MUTED))
        return y

    def self(self, y, i, label, w=120, h=24, right=True, size=9.2):
        c = self.c
        x = self.actors[i][0]
        if right:
            c.path(f"M {x} {y} h {w} v {h} h {-w}", stroke=PRIMARY, sw=1.3, arrow=PRIMARY)
            c.text(x + w + 8, y + h / 2 + 3.4, label, size=size)
        else:
            c.path(f"M {x} {y} h {-w} v {h} h {w}", stroke=PRIMARY, sw=1.3, arrow=PRIMARY)
            c.text(x - w - 8, y + h / 2 + 3.4, label, size=size, anchor="end")
        return y

    def note(self, y, x, text, h=56, w=560, size=9.2, fill=AMBER_F, stroke=AMBER):
        self.c.note(x, y, w, h, [text], fill=fill, stroke=stroke, size=size)
        return y


def head(c, title, note=None, width=None):
    c.text(24, 34, title, size=13, weight="bold")
    if note:
        c.text(24, 52, note, size=10, fill=MUTED)


# ---------------------------------------------------------------- 5.1 publish
def seq_publish():
    actors = [(185, "main.js", "controller and view state"),
              (440, "api.js", "one method per endpoint"),
              (700, "app.py", "Flask route handler"),
              (920, "models + SQLite", "connection and tables")]
    s = Seq(1010, 1000, actors, head_y=84, head_h=46)
    c = s.c
    head(c, "Sequence diagram - publish a listing, from form submit to committed row",
         "Solid arrows are calls; dashed arrows are returns. Self-calls are work done inside one component.")

    y = 214
    st = 40
    s.self(y, 0, "validate the form"); y += st
    s.self(y, 0, "check files"); y += st
    s.msg(y, 0, 1, "uploadImages(formData)"); y += st
    s.msg(y, 1, 2, "POST /api/upload"); y += st
    s.self(y, 2, "@login_required", w=150, right=False); y += st
    s.self(y, 2, "allowed_file()", w=150, right=False); y += st
    s.msg(y, 2, 3, "save as <uuid>.ext"); y += st
    s.msg(y, 3, 2, "saved file names", "ret"); y += st
    s.msg(y, 2, 1, "200 { data: ['9f3c….jpg'] }", "ret"); y += st
    s.msg(y, 1, 0, "resolved image names", "ret"); y += st
    s.msg(y, 0, 1, "createItem({ title, price, … })"); y += st
    s.msg(y, 1, 2, "POST /api/items  ·  JSON"); y += st
    s.self(y, 2, "re-validate input", w=150, right=False); y += st
    s.msg(y, 2, 3, "INSERT INTO items"); y += st
    s.msg(y, 3, 2, "item_id ← lastrowid", "ret"); y += st
    s.msg(y, 2, 3, "INSERT INTO images"); y += st
    s.self(y, 2, "commit and close", w=150, right=False); y += st
    s.msg(y, 2, 1, "200 · item_id = 42", "ret"); y += st
    s.self(y, 0, "toast + reload", w=150); y += st
    s.lines(y + 30)
    return c


# ---------------------------------------------------------------- 5.2 deal
def seq_deal():
    actors = [(140, "Buyer browser", "detail view"),
              (430, "app.py", "status endpoint"),
              (680, "SQLite", "items table"),
              (910, "Seller browser", "detail view")]
    s = Seq(1010, 872, actors, head_y=84, head_h=46)
    c = s.c
    head(c, "Sequence diagram - reserving an item and confirming the sale",
         "Both transitions are validated against the same rule table before either row is written.")

    y = 214
    st = 40
    s.msg(y, 0, 1, "POST /items/42/status  ·  reserve"); y += st
    s.self(y, 1, "look up the rule", w=150, right=False); y += st
    s.msg(y, 1, 2, "SELECT * FROM items WHERE id = 42"); y += st
    s.msg(y, 2, 1, "status = 'ON_SALE'", "ret"); y += st
    y += 48
    s.msg(y, 1, 2, "UPDATE … SET status = 'RESERVED'"); y += st
    s.msg(y, 1, 0, "200 · status updated", "ret"); y += st
    s.self(y, 0, "toast and re-render", w=140); y += st
    y += 18
    s.msg(y, 3, 1, "POST /items/42/status  ·  sell", lx=800); y += st
    s.self(y, 1, "look up the rule", w=150, right=False); y += st
    s.msg(y, 1, 2, "SELECT * FROM items WHERE id = 42"); y += st
    s.msg(y, 2, 1, "status = 'RESERVED'", "ret"); y += st
    s.msg(y, 1, 2, "UPDATE … SET status = 'SOLD'"); y += st
    s.msg(y, 1, 3, "200 · status updated", "ret", lx=800); y += st
    s.lines(y + 34)
    return c


# ---------------------------------------------------------------- 5.3 messages
def seq_message():
    actors = [(160, "main.js", "profile view and chat panel"),
              (520, "app.py", "message endpoints"),
              (860, "SQLite", "messages table")]
    s = Seq(1010, 890, actors, head_y=84, head_h=46)
    c = s.c
    head(c, "Sequence diagram - conversation list, opening a thread and sending a reply",
         "The list is produced by one aggregate query rather than one query per conversation.")

    y = 214
    st = 40
    s.msg(y, 0, 1, "GET /api/messages   (conversation list)"); y += st
    s.self(y, 1, "one aggregate query", w=180, right=False); y += st
    s.msg(y, 1, 2, "SELECT … MAX(id) … GROUP BY CASE …"); y += st
    s.msg(y, 2, 1, "one row per partner, newest first", "ret"); y += st
    s.msg(y, 1, 0, "200 { data: [ … ] }", "ret"); y += st
    s.self(y, 0, "render the list", w=140); y += st
    y += 16
    s.msg(y, 0, 1, "GET /api/messages/7   (open a thread)"); y += st
    s.msg(y, 1, 2, "SELECT … both directions, ordered by time"); y += st
    s.msg(y, 1, 2, "UPDATE … SET is_read = 1"); y += st
    s.msg(y, 1, 0, "200 { data: [ … ] }", "ret"); y += st
    s.self(y, 0, "render the bubbles", w=140); y += st
    y += 16
    s.msg(y, 0, 1, "POST /api/messages   { receiver_id: 7, … }"); y += st
    s.msg(y, 1, 2, "INSERT INTO messages ( … )"); y += st
    s.msg(y, 1, 0, "200 · message sent", "ret"); y += st
    s.self(y, 0, "re-fetch the thread", w=140); y += st
    s.lines(y + 30)
    return c


# ---------------------------------------------------------------- 5.4 route map
def route_map():
    c = Canvas(960, 900)
    head(c, "JSON endpoint surface, grouped by resource",
         "23 routes in total: 2 page routes, 21 JSON endpoints. Shaded badges mark methods that need a session.")

    groups = [
        ("Accounts", [("POST", "/api/register", False), ("POST", "/api/login", False),
                      ("POST", "/api/logout", False), ("GET", "/api/user/me", True)]),
        ("Catalogue", [("GET", "/api/items", False), ("GET", "/api/items/<id>", False)]),
        ("Listing management", [("POST", "/api/items", True), ("PUT", "/api/items/<id>", True),
                                ("DELETE", "/api/items/<id>", True)]),
        ("Media", [("POST", "/api/upload", True), ("GET", "/uploads/<filename>", False)]),
        ("Transactions", [("POST", "/api/items/<id>/status", True)]),
        ("Social", [("GET", "/api/favorites", True), ("POST", "/api/favorites", True),
                    ("DELETE", "/api/favorites/<id>", True),
                    ("GET", "/api/items/<id>/comments", False),
                    ("POST", "/api/items/<id>/comments", True),
                    ("GET", "/api/messages", True), ("POST", "/api/messages", True),
                    ("GET", "/api/messages/<uid>", True)]),
        ("Personal centre", [("GET", "/api/user/items", True), ("GET", "/api/user/sold", True)]),
    ]
    y = 84
    for name, eps in groups:
        h = 24 + len(eps) * 26
        c.rect(24, y, 912, h, fill="#fbfcfd", stroke=GRID, rx=8)
        c.text(38, y + 22, name, size=11.5, weight="bold")
        for i, (m, path, auth) in enumerate(eps):
            yy = y + 24 + 12 + i * 26
            col = {"GET": TEAL, "POST": PRIMARY, "PUT": AMBER, "DELETE": RED}[m]
            c.rect(210, yy - 13, 62, 18, fill="#ffffff", stroke=col, rx=4, sw=1.2)
            c.text(241, yy, m, size=8.8, anchor="middle", weight="bold", fill=col)
            c.text(286, yy, path, size=9.6, family=MONO)
            c.text(920, yy, "session" if auth else "public", size=9,
                   anchor="end", fill=AMBER if auth else MUTED)
        y += h + 12

    return c


# ---------------------------------------------------------------- 5.5 view router
def ui_states():
    c = Canvas(960, 470)
    head(c, "Client-side view router",
         "One HTML document, five views, and a hash route that makes a single listing shareable.")

    def v(cx, cy, label, sub, fill=PRIMARY_F, stroke=PRIMARY, w=150, h=62):
        c.rect(cx - w / 2, cy - h / 2, w, h, fill=fill, stroke=stroke, rx=10, sw=1.6, shadow=True)
        c.text(cx, cy - 3, label, size=11.5, anchor="middle", weight="bold")
        c.text(cx, cy + 15, sub, size=8.8, fill=MUTED, anchor="middle")

    c.rect(60, 74, 840, 36, fill="#fbfcfd", stroke=FAINT, rx=8, dash="6 4")
    c.text(480, 97, "persistent header  ·  brand   ·   search   ·   \"Sell an item\"   ·   avatar menu",
           size=10.5, anchor="middle", weight="bold", fill=MUTED)

    v(190, 190, "home", "catalogue, filters")
    v(540, 190, "auth", "log in / sign up", AMBER_F, AMBER)
    v(850, 190, "profile", "4 tabs", TEAL_F, TEAL)
    v(190, 420, "detail", "gallery, comments", GREY_F, GREY)
    v(540, 420, "publish", "form + live preview", AMBER_F, AMBER)

    def dbl(x1, y1, x2, y2, label, lx, ly):
        c.line(x1, y1, x2, y2, stroke=FAINT, sw=1.5, arrow=FAINT, arrow_start=FAINT)
        c.arrow_label(lx, ly, label, size=9.2, bg="#ffffff")

    for x, label in ((190, "brand"), (540, "Log in / Sign up"), (850, "avatar menu")):
        c.line(x, 110, x, 159, stroke=FAINT, sw=1.4, arrow=FAINT, dash="5 4")
        c.arrow_label(x + 52, 136, label, size=9, bg="#ffffff")
    c.path("M 660 110 V 420 H 615", stroke=FAINT, sw=1.4, dash="5 4", arrow=FAINT)
    c.arrow_label(700, 462, "\"Sell an item\"", size=9, anchor="end")

    dbl(190, 221, 190, 389, "open a card   ·   #item-<id>   ·   back", 190, 309)
    dbl(265, 205, 465, 205, "log in  ·  log out", 365, 205)
    c.line(520, 221, 520, 389, stroke=FAINT, sw=1.4, arrow=FAINT, dash="5 4")
    c.arrow_label(528, 306, "requires a session", size=9, anchor="start")

    c.legend(24, 452, [("anyone", PRIMARY_F, PRIMARY), ("session required", AMBER_F, AMBER)])
    return c


# ---------------------------------------------------------------- 5.6 aggregate query
def algo_conversation():
    c = Canvas(960, 356)
    head(c, "Rendering the conversation list without a query per conversation",
         "One grouped aggregate returns the newest message of every thread the caller takes part in.")

    c.rect(24, 84, 420, 250, fill="#fbfcfd", stroke=GRID, rx=8)
    c.text(38, 108, "messages table (before)", size=11, weight="bold")
    c.text(38, 126, "sender, receiver, content, created_at", size=9, fill=MUTED)

    rows = [(1, 3, 7, "Is the bike still available?"),
            (2, 7, 3, "Yes, free tomorrow."),
            (3, 3, 7, "Can we meet at the library?"),
            (4, 3, 9, "Textbook still on sale?"),
            (5, 9, 3, "Still on sale."),
            (6, 9, 3, "Great, I'll take it.")]
    y = 150
    c.rect(38, y - 13, 392, 20, fill=GREY_F, stroke="none", rx=3)
    for i, (h1, h2, h3, h4) in enumerate([("id", "sender", "receiver", "content")]):
        pass
    c.text(48, y, "id", size=9, weight="bold")
    c.text(80, y, "sender", size=9, weight="bold")
    c.text(140, y, "receiver", size=9, weight="bold")
    c.text(206, y, "content", size=9, weight="bold")
    y += 26
    for rid, snd, rcv, txt in rows:
        keep = rid in (3, 4, 6)
        if keep:
            c.rect(38, y - 13, 392, 20, fill=GREEN_F, stroke="none", rx=3)
        c.text(48, y, str(rid), size=9, fill=INK if keep else MUTED)
        c.text(80, y, str(snd), size=9, fill=INK if keep else MUTED)
        c.text(140, y, str(rcv), size=9, fill=INK if keep else MUTED)
        c.text(206, y, txt[:26], size=9, fill=INK if keep else MUTED)
        y += 24
    c.text(38, 330, "Highlighted rows are the surviving MAX(id) per partner group.", size=9, fill=GREEN)

    c.path("M 452 210 H 512", stroke=PRIMARY, sw=1.6, arrow=PRIMARY)
    c.text(482, 202, "", size=9)

    c.rect(530, 84, 406, 250, fill=PRIMARY_F, stroke=PRIMARY, rx=8)
    c.text(544, 108, "single aggregate query", size=11, weight="bold")
    lines = [
        "SELECT m.*, u.nickname AS other_nickname",
        "FROM messages m JOIN users u",
        "  ON u.id = CASE WHEN m.sender_id = ?",
        "                THEN m.receiver_id",
        "                ELSE m.sender_id END",
        "WHERE m.id IN (",
        "  SELECT MAX(id) FROM messages",
        "  WHERE sender_id = ? OR receiver_id = ?",
        "  GROUP BY CASE WHEN sender_id = ?",
        "                THEN receiver_id",
        "                ELSE sender_id END)",
        "ORDER BY m.created_at DESC",
    ]
    c.multiline(548, 132, lines, size=9.4, lh=15, family=MONO)

    return c


# ---------------------------------------------------------------- 5.7 status guard
def algo_status():
    c = Canvas(960, 362)
    head(c, "How a status request is validated before the row is written",
         "The same five-entry rule table drives every transition, so authorisation and state cannot drift apart.")

    c.rect(24, 84, 340, 232, fill="#fbfcfd", stroke=GRID, rx=8)
    c.text(38, 108, "transitions (server-side rule table)", size=11, weight="bold")
    c.text(38, 126, "action  →  from  →  to  →  role", size=9, fill=MUTED)
    rules = [("reserve", "ON_SALE", "RESERVED", "buyer"),
             ("sell", "RESERVED", "SOLD", "seller"),
             ("cancel_reserve", "RESERVED", "ON_SALE", "seller"),
             ("off_shelf", "ON_SALE", "OFF_SHELF", "seller"),
             ("relist", "OFF_SHELF", "ON_SALE", "seller")]
    y = 152
    for a, f, t, r in rules:
        c.text(38, y, a, size=9.4, family=MONO)
        c.text(150, y, f, size=9.4, family=MONO, fill=MUTED)
        c.text(238, y, "→ " + t, size=9.4, family=MONO, fill=TEAL)
        c.text(352, y, r, size=9.4, fill=AMBER, anchor="end")
        y += 26

    steps = [("1", "Is the action known?", "400 invalid action"),
             ("2", "Does the item exist?", "404 not found"),
             ("3", "Does the caller hold the role?", "403 refused"),
             ("4", "Is the stored status the required source?", "400 refused"),
             ("5", "UPDATE items SET status = ?", "200 one row changed")]
    y = 96
    for n, q, out in steps:
        c.rect(400, y, 500, 40, fill="#ffffff", stroke=LINE, rx=7, sw=1.3)
        c.circle(424, y + 20, 12, fill=PRIMARY_F, stroke=PRIMARY, sw=1.3)
        c.text(424, y + 23.5, n, size=10, anchor="middle", weight="bold", fill=PRIMARY)
        c.text(446, y + 24, q, size=10)
        c.text(930, y + 24, out, size=8.8, fill=RED if not out.startswith("200") else GREEN,
               anchor="end")
        y += 48

    return c


# ---------------------------------------------------------------- 5.8 stack
def stack():
    c = Canvas(960, 500)
    head(c, "Technology choices and the reasoning behind them",
         "Every component was chosen to keep the proof of concept installable on a laptop with one command.")

    items = [
        ("Python 3.8+", "language", "already available on the lab and staff machines; no runtime purchase", PRIMARY_F, PRIMARY),
        ("Flask 2.3.3", "web framework", "routing, sessions and JSON helpers in one small dependency", PRIMARY_F, PRIMARY),
        ("Werkzeug 2.3.7", "security utilities", "password hashing and secure_filename without extra libraries", VIOLET_F, VIOLET),
        ("SQLite 3", "database", "file-based, no server to install; the schema travels with the submission", TEAL_F, TEAL),
        ("Vanilla JS / CSS", "client", "no build step, no node_modules; the marker opens index.html from Flask", AMBER_F, AMBER),
        ("Playwright + Edge", "verification", "used to capture the interface states reproduced in this report", GREY_F, GREY),
    ]
    y = 84
    for name, role, why, f, st in items:
        c.rect(24, y, 912, 62, fill="#ffffff", stroke=GRID, rx=8)
        c.rect(24, y, 178, 62, fill=f, stroke=st, rx=8)
        c.text(113, y + 27, name, size=11.5, anchor="middle", weight="bold")
        c.text(113, y + 44, role, size=9, fill=MUTED, anchor="middle")
        c.text(220, y + 36, why, size=9.8)
        y += 70

    return c


FIGS = {
    "fig_seq_publish": seq_publish,
    "fig_seq_deal": seq_deal,
    "fig_seq_message": seq_message,
    "fig_route_map": route_map,
    "fig_ui_states": ui_states,
    "fig_algo_conversation": algo_conversation,
    "fig_algo_status": algo_status,
    "fig_stack": stack,
}
ORDER = ["fig_seq_publish", "fig_seq_deal", "fig_seq_message", "fig_route_map",
         "fig_ui_states", "fig_algo_conversation", "fig_algo_status", "fig_stack"]
