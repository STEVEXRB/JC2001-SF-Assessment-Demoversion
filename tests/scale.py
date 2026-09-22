"""How catalogue reads scale with the number of rows.

Seeds the same shape of data at several sizes and measures the three read paths
that touch the items table. Writes JSON on stdout.
"""
import json
import os
import statistics
import sys
import tempfile
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)

import app as app_module      # noqa: E402
import models                 # noqa: E402

SIZES = [100, 250, 500, 1000, 2000]
REPEATS = 60


def measure(tmp, n):
    models.DB_FILE = os.path.join(tmp, "scale.db")
    if os.path.exists(models.DB_FILE):
        os.remove(models.DB_FILE)
    app_module.app.config["UPLOAD_FOLDER"] = tmp
    models.init_db()
    client = app_module.app.test_client()
    client.post("/api/register", json={"username": "scaler", "password": "123456"})
    client.post("/api/login", json={"username": "scaler", "password": "123456"})

    cat = ["textbook", "digital", "daily_use", "sports_equipment", "other"]
    for i in range(n):
        client.post("/api/items", json={
            "title": "Item %05d advanced mathematics" % i,
            "description": "description %d" % i,
            "price": float(i % 500 + 1),
            "category": cat[i % 5],
            "condition": "good", "images": [],
        })

    paths = {
        "Catalogue page 1": "/api/items?status=ON_SALE",
        "Keyword search (LIKE on two columns)": "/api/items?keyword=mathematics",
        "Category filter + sort by price": "/api/items?category=textbook&sort=price_asc",
    }
    out = {}
    for label, url in paths.items():
        for _ in range(5):
            client.get(url)
        samples = []
        for _ in range(REPEATS):
            t0 = time.perf_counter()
            client.get(url)
            samples.append((time.perf_counter() - t0) * 1000.0)
        out[label] = round(statistics.median(samples), 3)
    out["_rows"] = n
    out["_db_bytes"] = os.path.getsize(models.DB_FILE)
    return out


def main():
    series = []
    with tempfile.TemporaryDirectory() as tmp:
        for n in SIZES:
            row = measure(tmp, n)
            print("  %5d rows -> %s" % (n, {k: v for k, v in row.items() if not k.startswith("_")}),
                  file=sys.stderr)
            series.append(row)
    print(json.dumps(series, indent=2))


if __name__ == "__main__":
    main()
