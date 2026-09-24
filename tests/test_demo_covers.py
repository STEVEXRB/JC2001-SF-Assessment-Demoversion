"""Regression tests for the demo cover illustrations.

`seed.py` stores filenames such as ``demo-book.svg`` in the ``images`` table while
``uploads/`` is git-ignored, so the artwork cannot ship with the repository — it has
to be generated on the machine that runs the seed (``demo_covers.py``). These tests
lock that contract in. The bug they guard against: a freshly seeded catalogue whose
nine covers all resolve to 404s.
"""
import sqlite3
import xml.etree.ElementTree as ET

import pytest

import app as app_module
import demo_covers
import models
import seed as seed_module


@pytest.fixture()
def seeded(tmp_path, monkeypatch):
    """A throwaway database plus upload directory, seeded with the demo data."""
    db_path = str(tmp_path / "seed.db")
    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(models, "DB_FILE", db_path)
    counts = seed_module.seed(force=True, db_file=db_path, upload_dir=str(upload_dir))
    assert counts["images"] == len(demo_covers.COVERS)
    return upload_dir


class TestDemoCovers:
    def test_seeded_image_rows_resolve_to_real_files(self, seeded):
        upload_dir = seeded
        conn = sqlite3.connect(models.DB_FILE)
        names = [row[0] for row in conn.execute("SELECT file_path FROM images")]
        conn.close()
        assert names, "the demo dataset must reference cover images"
        for name in names:
            assert (upload_dir / name).is_file(), f"{name} is referenced by the seed but missing"

    def test_every_cover_is_a_well_formed_svg(self, seeded):
        upload_dir = seeded
        for name in demo_covers.COVERS:
            root = ET.fromstring((upload_dir / name).read_text(encoding="utf-8"))
            assert root.tag.endswith("svg"), name
            assert root.get("viewBox") == "0 0 800 600", name

    def test_write_covers_is_idempotent(self, seeded, tmp_path):
        empty = tmp_path / "second"
        assert len(demo_covers.write_covers(str(empty))) == len(demo_covers.COVERS)
        assert demo_covers.write_covers(str(empty)) == []

    def test_reseeding_keeps_a_replaced_cover(self, seeded):
        """A placeholder swapped for a real photo must survive a re-seed."""
        target = seeded / "demo-book.svg"
        target.write_text("<svg>user photo</svg>", encoding="utf-8")
        seed_module.seed(force=True, db_file=models.DB_FILE, upload_dir=str(seeded))
        assert target.read_text(encoding="utf-8") == "<svg>user photo</svg>"

    def test_upload_route_serves_the_generated_covers(self, client, seeded, monkeypatch):
        # Flask's Config is a dict subclass, so patch the mapping key, not the attribute.
        monkeypatch.setitem(app_module.app.config, "UPLOAD_FOLDER", str(seeded))
        response = client.get("/uploads/demo-book.svg")
        assert response.status_code == 200
        assert b"<svg" in response.data

    def test_upload_route_reports_a_missing_cover_as_404(self, client, monkeypatch):
        monkeypatch.setitem(app_module.app.config, "UPLOAD_FOLDER", "uploads")
        assert client.get("/uploads/does-not-exist.svg").status_code == 404
