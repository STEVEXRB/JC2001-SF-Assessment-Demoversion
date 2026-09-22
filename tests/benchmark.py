"""Performance measurement harness for the Campus Market PoC.

Measures in-process request handling with Flask's test client, which gives the
application-side cost (routing, session handling, SQL, JSON serialisation) with
the network and the browser removed. The numbers are therefore a lower bound on
what a user experiences and an upper bound on what the application code itself
contributes.

Run:  python tests/benchmark.py            -> prints JSON on stdout
"""
import json
import os
import statistics
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import app as app_module      # noqa: E402
import models                 # noqa: E402

ITEMS = 500
USERS = 20
THREADS = 60
THREAD_LEN = 40
REPEATS = 200


def seed(tmp):
    models.DB_FILE = os.path.join(tmp, "bench.db")
    app_module.app.config["UPLOAD_FOLDER"] = os.path.join(tmp, "uploads")
    os.makedirs(app_module.app.config["UPLOAD_FOLDER"], exist_ok=True)
    models.init_db()
    client = app_module.app.test_client()

    cat = ["textbook", "digital", "daily_use", "sports_equipment", "other"]
    cond = ["new", "like_new", "good", "fair"]
    users = []
    for u in range(USERS):
        name = "bench_user_%02d" % u
        client.post("/api/register", json={"username": name, "password": "123456",
                                           "nickname": "Bench %02d" % u})
        users.append(name)

    client.post("/api/login", json={"username": users[0], "password": "123456"})
    me = client.get("/api/user/me").get_json()["data"]
    item_ids = []
    for n in range(ITEMS):
        r = client.post("/api/items", json={
            "title": "Listing %04d %s" % (n, "advanced mathematics textbook" if n % 3 == 0 else "item"),
            "description": "Benchmark description %d, used for one semester, price negotiable." % n,
            "price": float((n % 400) + 1),
            "category": cat[n % len(cat)],
            "condition": cond[n % len(cond)],
            "images": [],
        })
        item_ids.append(r.get_json()["data"]["item_id"])

    # one detail page with the maximum gallery and a busy comment thread
    hot = item_ids[0]
    for c in range(5):
        client.post("/api/items/%d/comments" % hot, json={"content": "comment %d" % c})

    # one partner with a long thread, plus many short conversations
    partner = app_module.app.test_client()
    partner.post("/api/register", json={"username": "bench_partner", "password": "123456",
                                        "nickname": "Partner"})
    partner.post("/api/login", json={"username": "bench_partner", "password": "123456"})
    partner_me = partner.get("/api/user/me").get_json()["data"]
    for m in range(THREAD_LEN):
        partner.post("/api/messages", json={"receiver_id": me["id"], "content": "msg %d" % m})
    for t in range(THREADS):
        sender = app_module.app.test_client()
        sender.post("/api/login", json={"username": users[1 + t % (USERS - 1)], "password": "123456"})
        sender.post("/api/messages", json={"receiver_id": me["id"], "content": "thread %d" % t})

    return client, {"me": me, "partner": partner_me, "hot": hot, "item_ids": item_ids,
                    "users": users}


def timeit(fn, repeats=REPEATS):
    samples = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        r = fn()
        samples.append((time.perf_counter() - t0) * 1000.0)
        if hasattr(r, "status_code") and r.status_code >= 400:
            raise SystemExit("benchmark request failed with %s" % r.status_code)
    samples.sort()
    return {
        "median": round(statistics.median(samples), 3),
        "p95": round(samples[int(len(samples) * 0.95) - 1], 3),
        "mean": round(statistics.fmean(samples), 3),
        "n": repeats,
    }


def main():
    import tempfile
    with tempfile.TemporaryDirectory() as tmp:
        client, ctx = seed(tmp)
        results = {}

        catalogue = [
            ("Browse the catalogue (page 1 of %d)" % ((ITEMS + 11) // 12),
             lambda: client.get("/api/items?status=ON_SALE")),
            ("Keyword search across title and description",
             lambda: client.get("/api/items?keyword=mathematics")),
            ("Keyword search with no match",
             lambda: client.get("/api/items?keyword=zzzzzz")),
            ("Filter by category and sort by price",
             lambda: client.get("/api/items?category=textbook&sort=price_asc")),
            ("Open a listing detail page",
             lambda: client.get("/api/items/%d" % ctx["item_ids"][7])),
            ("Open the busiest listing (5 comments)",
             lambda: client.get("/api/items/%d" % ctx["hot"])),
            ("Read the comment thread",
             lambda: client.get("/api/items/%d/comments" % ctx["hot"])),
            ("Load the personal centre listing grid",
             lambda: client.get("/api/user/items")),
        ]
        for label, fn in catalogue:
            results[label] = timeit(fn)

        client.post("/api/logout")
        client.post("/api/login", json={"username": ctx["users"][0], "password": "123456"})

        messaging = [
            ("Conversation list (%d threads)" % THREADS,
             lambda: client.get("/api/messages")),
            ("Open a %d-message thread" % THREAD_LEN,
             lambda: client.get("/api/messages/%d" % ctx["partner"]["id"])),
        ]
        for label, fn in messaging:
            results[label] = timeit(fn)

        writes = [
            ("Publish a listing",
             lambda: client.post("/api/items", json={"title": "bench publish", "price": 1.0,
                                                     "category": "other", "condition": "good"})),
        ]
        for label, fn in writes:
            results[label] = timeit(fn, repeats=100)

        def fav_cycle():
            client.post("/api/favorites", json={"item_id": ctx["item_ids"][3]})
            return client.delete("/api/favorites/%d" % ctx["item_ids"][3])
        results["Add and remove a favourite"] = timeit(fav_cycle, repeats=100)

        def toggle():
            client.post("/api/items/%d/status" % ctx["item_ids"][9], json={"action": "off_shelf"})
            return client.post("/api/items/%d/status" % ctx["item_ids"][9], json={"action": "relist"})
        results["Toggle a listing offline and back"] = timeit(toggle, repeats=100)

        meta = {
            "items": ITEMS, "users": USERS + 2, "threads": THREADS + 1,
            "thread_messages": THREAD_LEN, "repeats": REPEATS,
            "runtime": sys.version.split()[0],
            "db_bytes": os.path.getsize(models.DB_FILE),
        }
        print(json.dumps({"meta": meta, "results": results}, indent=2))


if __name__ == "__main__":
    main()
