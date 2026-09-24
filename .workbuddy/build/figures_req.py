# figures_req.py - requirements and modelling figures (Chapter 3)
from svgkit import *


# ---------------------------------------------------------------- 3.1 context
def ctx():
    c = Canvas(900, 566)
    c.text(45, 34, "System context - who and what the PoC interacts with", size=13, weight="bold")

    c.box(340, 218, 220, 110, "Campus Market PoC", "Flask web application + client code",
          fill=PRIMARY_F, stroke=PRIMARY, sw=2, title_size=13, shadow=True)

    ents = [
        (45, 62, 215, 80, "Visitor", "unregistered student", GREY_F, GREY),
        (45, 330, 215, 80, "Registered student", "buyer and seller roles", GREY_F, GREY),
        (640, 62, 215, 80, "Web browser", "renders the single-page client", AMBER_F, AMBER),
        (640, 330, 215, 80, "Local filesystem", "data.db  ·  uploads/", TEAL_F, TEAL),
        (340, 468, 220, 80, "Course assessor", "installs and evaluates the PoC", VIOLET_F, VIOLET),
    ]
    for x, y, w, h, t, s, f, st in ents:
        c.box(x, y, w, h, t, s, fill=f, stroke=st, title_size=12, sub_size=10)

    c.line(260, 102, 352, 244, stroke=GREY, arrow=GREY, sw=1.5)
    c.line(260, 370, 352, 306, stroke=GREY, arrow=GREY, sw=1.5)
    c.line(640, 102, 548, 244, stroke=AMBER, arrow=AMBER, sw=1.5)
    c.line(640, 370, 548, 306, stroke=TEAL, arrow=TEAL, sw=1.5)
    c.line(450, 468, 450, 330, stroke=VIOLET, arrow=VIOLET, sw=1.5, dash="6 4")

    c.arrow_label(288, 152, "browses", size=9.5, bg="#ffffff")
    c.arrow_label(300, 372, "trades", size=9.5, bg="#ffffff")
    c.arrow_label(604, 152, "HTTP", size=9.5, bg="#ffffff")
    c.arrow_label(628, 374, "file I/O", size=9.5, bg="#ffffff")
    c.arrow_label(464, 402, "runs locally", size=9.5, bg="#ffffff", anchor="start")

    return c


# ---------------------------------------------------------------- 3.2 use cases
def usecase():
    c = Canvas(1000, 946)
    c.text(40, 34, "Use case diagram - Campus Market", size=13, weight="bold")

    bx, by, bw, bh = 352, 66, 406, 886
    c.rect(bx, by, bw, bh, fill="#fcfdfe", stroke=FAINT, rx=10, dash="7 5", sw=1.3)
    c.text(bx + bw / 2, by + 24, "Campus Market", size=12.5, weight="bold",
           anchor="middle", fill=MUTED)

    visitor_ucs = ["Register an account", "Log in", "Browse listings", "Search and filter listings",
                   "View listing detail", "Read comments", "Log out"]
    student_ucs = ["Publish a listing", "Upload listing photos", "Edit own listing",
                   "Take listing offline", "Relist an item", "Reserve an item", "Confirm the sale",
                   "Cancel a reservation", "Save a favourite", "Post a comment",
                   "Send a direct message", "View personal centre"]
    ucs = [(n, "v") for n in visitor_ucs] + [(n, "s") for n in student_ucs]

    cx, rx, ry, y0, step = 530, 134, 19, 96, 46
    pos = {}
    for i, (name, kind) in enumerate(ucs):
        y = y0 + i * step
        pos[name] = (cx, y)
        c.ellipse(cx, y, rx, ry, fill=PRIMARY_F if kind == "v" else "#ffffff",
                  stroke=PRIMARY if kind == "v" else TEAL, sw=1.4)
        c.text(cx, y + 3.6, name, size=10, anchor="middle")

    c.actor(150, 240, "Visitor", sub="not logged in")
    c.actor(150, 720, "Registered", sub="student")

    for name in visitor_ucs:
        c.line(164, 255, cx - rx, pos[name][1], stroke="#c9d2dd", sw=1.0)
    for name in student_ucs:
        c.line(164, 735, cx - rx, pos[name][1], stroke="#c9d2dd", sw=1.0)

    # generalisation Visitor <- Registered student
    c.line(150, 690, 150, 350, stroke=GREY, sw=1.4)
    c.poly([(150, 342), (143.5, 356), (156.5, 356)], fill="#ffffff", stroke=GREY)
    c.text(162, 524, "«generalisation»", size=9.5, fill=MUTED)

    # include: publish a listing -> upload listing photos
    y1 = pos["Publish a listing"][1]
    y2 = pos["Upload listing photos"][1]
    c.path(f"M {cx + rx} {y1} H 706 V {y2} H {cx + rx}", stroke=FAINT, sw=1.2,
           dash="5 4", arrow=FAINT)
    c.text(714, (y1 + y2) / 2 + 3.4, "«include»", size=9.5, fill=MUTED)

    return c


# ---------------------------------------------------------------- 3.3 swimlane
def bpm_lifecycle():
    c = Canvas(940, 592)
    c.text(20, 32, "Business process - one complete second-hand transaction", size=13, weight="bold")
    c.text(20, 50, "One lane per role; time flows left to right. Dashed edges cross a lane boundary.",
           size=10, fill=MUTED)

    lane_spec = [("Buyer", 84, PRIMARY_F, PRIMARY),
                 ("Seller", 236, TEAL_F, TEAL),
                 ("System", 388, GREY_F, GREY)]
    for name, y, f, st in lane_spec:
        c.rect(20, y, 900, 144, fill="#ffffff", stroke=GRID, rx=8)
        c.rect(20, y, 148, 144, fill=f, stroke=st, rx=8)
        c.text(94, y + 78, name, size=12.5, weight="bold", anchor="middle")

    lane_cy = {name: y + 72 for name, y, _, _ in lane_spec}

    def step(x, lane, label, sub=None, fill="#ffffff", stroke=LINE, w=158, h=68):
        y = lane_cy[lane] - h / 2
        c.rect(x, y, w, h, fill=fill, stroke=stroke, rx=8, sw=1.6)
        lines = wrap(T(label), 21)
        top = y + (h / 2 - 4 if sub else h / 2 + 3)
        c.multiline(x + w / 2, top - (len(lines) - 1) * 6.5, lines, size=10.5,
                    anchor="middle", weight="bold")
        if sub:
            c.text(x + w / 2, y + h - 13, sub, size=9, fill=MUTED, anchor="middle")
        return x, x + w

    a = step(172, "Buyer", "Browse and open", "GET /api/items")
    b = step(378, "Buyer", "Reserve the item", "action=reserve", AMBER_F, AMBER)
    d = step(378, "Seller", "Reservation appears", "status = RESERVED", AMBER_F, AMBER)
    e = step(584, "Seller", "Hand over and confirm", "action=sell")
    f = step(584, "System", "Validate and persist", "UPDATE items", GREY_F, GREY)
    g = step(754, "Buyer", "Listing shows as sold", "status = SOLD", GREEN_F, GREEN)
    h = step(754, "System", "Reject an illegal act", "400 / 403", RED_F, RED)

    def link(p, q, a_lane, b_lane, stroke=FAINT, dash=None):
        c.line(p, lane_cy[a_lane], q, lane_cy[b_lane], stroke=stroke, sw=1.4,
               dash=dash, arrow=stroke)

    link(a[1], b[0], "Buyer", "Buyer", LINE)
    link(b[1], d[0], "Buyer", "Seller", dash="5 4")
    link(d[1], e[0], "Seller", "Seller", LINE)
    link(e[1], f[0], "Seller", "System", dash="5 4")
    link(f[1], g[0], "System", "Buyer", dash="5 4")

    c.path("M 378 %d H 870 V %d H 172" %
           (lane_cy["Buyer"] + 64, lane_cy["Buyer"] + 64),
           stroke=FAINT, sw=1.4, arrow=FAINT)
    c.text(524, lane_cy["Buyer"] + 58,
           "cancel the reservation  ·  take the listing offline  ·  relist",
           size=9.5, fill=MUTED, anchor="middle")

    c.legend(24, 560, [("normal flow", "#ffffff", LINE), ("cross-lane handover", "#ffffff", FAINT),
                       ("error path", RED_F, RED), ("terminal outcome", GREEN_F, GREEN)])
    return c


# ------------------------------------------------------- 3.4 activity: publish
def activity_publish():
    c = Canvas(900, 1046)
    c.text(30, 32, "Activity diagram - publish a listing", size=13, weight="bold")
    c.text(30, 50, "Rounded bars are decisions; the guard is written on the outgoing edge.",
           size=10, fill=MUTED)

    cx = 330
    y = 96
    c.circle(cx, y, 11, fill=INK, stroke=INK)
    y += 40

    flow = [
        ("act", "Open the \"Sell an item\" view", "redirects to the auth view if no session"),
        ("act", "Fill in title, description, price, category and condition", None),
        ("dec", "Client validation passes?", None),
        ("act", "POST /api/upload with the selected photos", "multipart/form-data"),
        ("dec", "Is each extension allowed?", None),
        ("data", "Save each file under a random UUID name", "os.makedirs + file.save"),
        ("act", "POST /api/items with the returned file names", "application/json"),
        ("dec", "Are title and price present?", None),
        ("data", "INSERT into items, then one row per image in images", "single transaction"),
        ("ok", "Commit and return the new item_id", None),
    ]
    boxes = []
    for kind, label, sub in flow:
        if kind == "dec":
            w, h = 260, 62
            c.poly([(cx, y), (cx + w / 2, y + h / 2), (cx, y + h), (cx - w / 2, y + h / 2)],
                   fill=AMBER_F, stroke=AMBER)
            lines = wrap(T(label), 21)
            c.multiline(cx, y + h / 2 - (len(lines) - 1) * 6 + 4, lines, size=10, anchor="middle")
        else:
            fill, stroke = {"act": ("#ffffff", LINE), "data": (TEAL_F, TEAL),
                            "ok": (GREEN_F, GREEN)}[kind]
            w, h = 388, 56 if sub else 46
            c.rect(cx - w / 2, y, w, h, fill=fill, stroke=stroke, rx=7, sw=1.5)
            lines = wrap(T(label), 52)
            c.multiline(cx, y + h / 2 - (len(lines) - 1) * 6 + (3 if not sub else -1),
                        lines, size=10, anchor="middle", weight="bold")
            if sub:
                c.text(cx, y + h - 11, sub, size=8.8, fill=MUTED, anchor="middle")
        boxes.append((kind, y, h))
        y += h + 32

    prev = 96 + 11
    for kind, by, bh in boxes:
        c.line(cx, prev, cx, by, stroke=LINE, sw=1.4, arrow=LINE)
        prev = by + bh
    c.circle(cx, prev + 26, 13, fill="#ffffff", stroke=INK)
    c.circle(cx, prev + 26, 7.5, fill=INK, stroke=INK)
    c.line(cx, prev, cx, prev + 13, stroke=LINE, sw=1.4, arrow=LINE)
    c.text(cx + 24, prev + 30, "end", size=9, fill=MUTED)

    for kind, by, bh in boxes:
        if kind == "dec":
            c.line(cx + 131, by + bh / 2, 700, by + bh / 2, stroke=RED, sw=1.4,
                   dash="5 4", arrow=RED)
            c.text(716, by + bh / 2 + 3.6, "no → 400 / toast", size=9.2, fill=RED)

    return c


FIGS = {
    "fig_ctx": ctx,
    "fig_usecase": usecase,
    "fig_bpm_trade": bpm_lifecycle,
    "fig_act_publish": activity_publish,
}
ORDER = ["fig_ctx", "fig_usecase", "fig_bpm_trade", "fig_act_publish"]
