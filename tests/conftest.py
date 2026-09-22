"""Shared pytest fixtures.

Every test runs against a throwaway SQLite file and a throwaway upload directory,
so the real data.db shipped with the repository is never touched.
"""
import os
import sys

import pytest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

import app as app_module          # noqa: E402
import models                     # noqa: E402


@pytest.fixture()
def client(tmp_path, monkeypatch):
    """A Flask test client backed by an empty database."""
    db_path = tmp_path / "test.db"
    upload_dir = tmp_path / "uploads"
    upload_dir.mkdir()

    monkeypatch.setattr(models, "DB_FILE", str(db_path))
    app_module.app.config["UPLOAD_FOLDER"] = str(upload_dir)
    app_module.app.config["TESTING"] = True
    app_module.app.config["WTF_CSRF_ENABLED"] = False

    models.init_db()
    with app_module.app.test_client() as c:
        c.upload_dir = str(upload_dir)
        yield c


def register(client, username, password="123456", **extra):
    payload = {"username": username, "password": password}
    payload.update(extra)
    return client.post("/api/register", json=payload)


def login(client, username, password="123456"):
    return client.post("/api/login", json={"username": username, "password": password})


def register_and_login(client, username, password="123456", **extra):
    register(client, username, password, **extra)
    return login(client, username, password)


def make_user(client, username, nickname=None, **extra):
    """Register, log in, create one listing and return (user_id, item_id)."""
    register_and_login(client, username, nickname=nickname or username, **extra)
    me = client.get("/api/user/me").get_json()["data"]
    item = client.post("/api/items", json={
        "title": f"{nickname or username} item",
        "description": "used once",
        "price": 25.0,
        "category": "textbook",
        "condition": "good",
        "images": [],
    }).get_json()["data"]["item_id"]
    return me["id"], item


@pytest.fixture()
def seller(client):
    uid, item_id = make_user(client, "seller_a", "Alice")
    return {"id": uid, "item_id": item_id}


@pytest.fixture()
def buyer(client):
    uid, item_id = make_user(client, "buyer_b", "Bob")
    return {"id": uid, "item_id": item_id}


def png_bytes(size=64):
    """A minimal but valid 1x1 PNG, padded to `size` bytes."""
    head = bytes.fromhex(
        "89504e470d0a1a0a0000000d49484452000000010000000108060000001f15c489"
        "0000000a49444154789c6360000002000100ffff03000006000557bfabd400"
        "00000049454e44ae426082")
    return head + b"\x00" * max(0, size - len(head))
