"""Unit and component tests for the Campus Market JSON API.

The suite is organised by the same modules the application is divided into, so a
failing test names the component that regressed:

    TC-A  accounts      registration, login, session, profile
    TC-C  catalogue     listing, search, filtering, sorting, pagination, detail
    TC-L  listings      create, update, soft delete
    TC-U  upload        file type validation and storage
    TC-T  transitions   the item status state machine
    TC-S  social        favourites, comments, private messages
    TC-P  personal      "my listings" and "sold"
"""
import io
import json

from conftest import login, make_user, png_bytes, register, register_and_login


# --------------------------------------------------------------------- TC-A
class TestAccountsA:
    def test_a01_register_returns_200(self, client):
        r = register(client, "stu01", nickname="Stu")
        assert r.status_code == 200 and r.get_json()["code"] == 200

    def test_a02_register_persists_profile_fields(self, client):
        register(client, "stu02", nickname="Nick", email="a@b.c", student_id="S100")
        login(client, "stu02")
        me = client.get("/api/user/me").get_json()["data"]
        assert me["nickname"] == "Nick" and me["student_id"] == "S100"
        assert me["username"] == "stu02" and me["email"] == "a@b.c"

    def test_a03_register_rejects_duplicate_username(self, client):
        register(client, "stu03")
        r = register(client, "stu03")
        assert r.status_code == 400 and "already" in r.get_json()["msg"].lower()

    def test_a04_register_rejects_empty_credentials(self, client):
        assert client.post("/api/register", json={"username": "", "password": ""}).status_code == 400

    def test_a05_password_is_never_returned(self, client):
        register_and_login(client, "stu05")
        me = client.get("/api/user/me").get_json()["data"]
        assert "password_hash" not in me and "password" not in me

    def test_a06_login_rejects_wrong_password(self, client):
        register(client, "stu06")
        r = client.post("/api/login", json={"username": "stu06", "password": "nope"})
        assert r.status_code == 401

    def test_a07_login_rejects_unknown_user(self, client):
        assert client.post("/api/login", json={"username": "ghost", "password": "x"}).status_code == 401

    def test_a08_me_requires_a_session(self, client):
        assert client.get("/api/user/me").status_code == 401

    def test_a09_logout_clears_the_session(self, client):
        register_and_login(client, "stu09")
        assert client.get("/api/user/me").status_code == 200
        client.post("/api/logout")
        assert client.get("/api/user/me").status_code == 401

    def test_a10_stored_password_is_hashed(self, client, tmp_path):
        import models
        import sqlite3
        register(client, "stu10", password="plaintext")
        conn = sqlite3.connect(models.DB_FILE)
        stored = conn.execute("SELECT password_hash FROM users WHERE username='stu10'").fetchone()[0]
        conn.close()
        assert "plaintext" not in stored and stored.startswith("pbkdf2:")


# --------------------------------------------------------------------- TC-C
class TestCatalogueC:
    def test_c01_empty_catalogue_returns_zero_total(self, client):
        body = client.get("/api/items").get_json()["data"]
        assert body["items"] == [] and body["total"] == 0 and body["total_pages"] == 0

    def test_c02_catalogue_is_public(self, client, seller):
        assert client.get("/api/items").status_code == 200

    def test_c03_listing_carries_seller_and_cover(self, client, seller):
        item = client.get("/api/items").get_json()["data"]["items"][0]
        assert item["seller_nickname"] == "Alice" and "cover_image" in item

    def test_c04_keyword_matches_title(self, client, seller):
        body = client.get("/api/items?keyword=Alice").get_json()["data"]
        assert body["total"] == 1

    def test_c05_keyword_matches_description(self, client, seller):
        assert client.get("/api/items?keyword=used").get_json()["data"]["total"] == 1

    def test_c06_keyword_is_case_insensitive(self, client, seller):
        assert client.get("/api/items?keyword=alice").get_json()["data"]["total"] == 1

    def test_c07_unknown_keyword_returns_empty(self, client, seller):
        assert client.get("/api/items?keyword=zzzz").get_json()["data"]["total"] == 0

    def test_c08_category_filter(self, client, seller):
        assert client.get("/api/items?category=textbook").get_json()["data"]["total"] == 1
        assert client.get("/api/items?category=digital").get_json()["data"]["total"] == 0

    def test_c09_status_filter(self, client, seller):
        assert client.get("/api/items?status=ON_SALE").get_json()["data"]["total"] == 1
        assert client.get("/api/items?status=SOLD").get_json()["data"]["total"] == 0

    def test_c10_sort_by_price_ascending(self, client, seller):
        client.post("/api/items", json={"title": "cheap", "price": 5})
        client.post("/api/items", json={"title": "dear", "price": 500})
        titles = [i["title"] for i in
                  client.get("/api/items?sort=price_asc").get_json()["data"]["items"]]
        assert titles == ["cheap", "Alice item", "dear"]

    def test_c11_sort_by_price_descending(self, client, seller):
        client.post("/api/items", json={"title": "cheap", "price": 5})
        client.post("/api/items", json={"title": "dear", "price": 500})
        titles = [i["title"] for i in
                  client.get("/api/items?sort=price_desc").get_json()["data"]["items"]]
        assert titles[0] == "dear" and titles[-1] == "cheap"

    def test_c12_pagination_page_size_is_twelve(self, client, seller):
        for n in range(20):
            client.post("/api/items", json={"title": f"bulk {n:02d}", "price": n + 1})
        first = client.get("/api/items?page=1").get_json()["data"]
        second = client.get("/api/items?page=2").get_json()["data"]
        assert first["per_page"] == 12 and len(first["items"]) == 12
        assert len(second["items"]) == 9
        assert first["total_pages"] == 2 and second["page"] == 2

    def test_c13_item_detail_returns_images_and_comments(self, client, seller):
        body = client.get(f"/api/items/{seller['item_id']}").get_json()["data"]
        assert body["images"] == [] and body["comments"] == []

    def test_c14_missing_item_returns_404(self, client):
        assert client.get("/api/items/9999").status_code == 404


# --------------------------------------------------------------------- TC-L
class TestListingsL:
    def test_l01_publishing_requires_a_session(self, client):
        assert client.post("/api/items", json={"title": "x", "price": 1}).status_code == 401

    def test_l02_publish_returns_the_new_id(self, client, seller):
        r = client.post("/api/items", json={"title": "new thing", "price": 3.5})
        assert r.status_code == 200 and r.get_json()["data"]["item_id"] > 0

    def test_l03_publish_rejects_missing_title(self, client, seller):
        assert client.post("/api/items", json={"price": 3}).status_code == 400

    def test_l04_publish_rejects_missing_price(self, client, seller):
        assert client.post("/api/items", json={"title": "no price"}).status_code == 400

    def test_l05_publish_rejects_non_numeric_price(self, client, seller):
        assert client.post("/api/items", json={"title": "t", "price": "abc"}).status_code == 400

    def test_l06_new_listing_starts_on_sale(self, client, seller):
        body = client.get(f"/api/items/{seller['item_id']}").get_json()["data"]
        assert body["status"] == "ON_SALE"

    def test_l07_update_changes_the_stored_values(self, client, seller):
        client.put(f"/api/items/{seller['item_id']}", json={"title": "renamed", "price": 99})
        body = client.get(f"/api/items/{seller['item_id']}").get_json()["data"]
        assert body["title"] == "renamed" and body["price"] == 99

    def test_l08_update_is_refused_for_a_non_owner(self, client, seller, buyer):
        assert client.put(f"/api/items/{seller['item_id']}",
                          json={"title": "hijack"}).status_code == 403

    def test_l09_update_of_a_missing_item_returns_404(self, client, seller):
        assert client.put("/api/items/9999", json={"title": "x"}).status_code == 404

    def test_l10_delete_is_a_soft_delete(self, client, seller):
        client.delete(f"/api/items/{seller['item_id']}")
        body = client.get(f"/api/items/{seller['item_id']}").get_json()["data"]
        assert body["status"] == "OFF_SHELF"

    def test_l11_offline_items_leave_the_catalogue(self, client, seller):
        client.delete(f"/api/items/{seller['item_id']}")
        assert client.get("/api/items?status=ON_SALE").get_json()["data"]["total"] == 0

    def test_l12_delete_is_refused_for_a_non_owner(self, client, seller, buyer):
        assert client.delete(f"/api/items/{seller['item_id']}").status_code == 403


# --------------------------------------------------------------------- TC-U
class TestUploadU:
    def test_u01_upload_requires_a_session(self, client):
        assert client.post("/api/upload", data={}).status_code == 401

    def test_u02_upload_rejects_an_empty_request(self, client, seller):
        assert client.post("/api/upload", content_type="multipart/form-data").status_code == 400

    def test_u03_upload_accepts_png(self, client, seller):
        r = client.post("/api/upload", data={"files": (io.BytesIO(png_bytes()), "a.png")},
                        content_type="multipart/form-data")
        assert r.status_code == 200 and len(r.get_json()["data"]) == 1

    def test_u04_stored_name_is_a_random_uuid(self, client, seller):
        r = client.post("/api/upload", data={"files": (io.BytesIO(png_bytes()), "orig.png")},
                        content_type="multipart/form-data")
        name = r.get_json()["data"][0]
        assert name.endswith(".png") and len(name) == 36

    def test_u05_upload_rejects_a_disallowed_extension(self, client, seller):
        r = client.post("/api/upload", data={"files": (io.BytesIO(b"<svg/>"), "a.svg")},
                        content_type="multipart/form-data")
        assert r.status_code == 400

    def test_u06_upload_accepts_several_files_at_once(self, client, seller):
        r = client.post("/api/upload", data={"files": [(io.BytesIO(png_bytes()), "a.png"),
                                                       (io.BytesIO(png_bytes()), "b.jpg")]},
                        content_type="multipart/form-data")
        assert len(r.get_json()["data"]) == 2

    def test_u07_upload_oversize_body_is_refused(self, client, seller):
        big = png_bytes(6 * 1024 * 1024)
        r = client.post("/api/upload", data={"files": (io.BytesIO(big), "big.png")},
                        content_type="multipart/form-data")
        assert r.status_code == 413

    def test_u08_published_images_are_returned_in_order(self, client, seller):
        r = client.post("/api/upload", data={"files": [(io.BytesIO(png_bytes()), "1.png"),
                                                       (io.BytesIO(png_bytes()), "2.png")]},
                        content_type="multipart/form-data")
        names = r.get_json()["data"]
        client.post("/api/items", json={"title": "with pics", "price": 1, "images": names})
        listed = [i for i in client.get("/api/items").get_json()["data"]["items"]
                  if i["title"] == "with pics"][0]
        detail = client.get(f"/api/items/{listed['id']}").get_json()["data"]
        assert detail["images"] == names


# --------------------------------------------------------------------- TC-T
class TestTransitionsT:
    def _action(self, client, item_id, action):
        return client.post(f"/api/items/{item_id}/status", json={"action": action})

    def test_t01_unknown_action_is_rejected(self, client, seller):
        assert self._action(client, seller["item_id"], "explode").status_code == 400

    def test_t02_missing_action_is_rejected(self, client, seller):
        assert client.post(f"/api/items/{seller['item_id']}/status", json={}).status_code == 400

    def test_t03_transition_on_missing_item_returns_404(self, client, seller):
        assert self._action(client, 9999, "reserve").status_code == 404

    def test_t04_reserve_requires_a_session(self, client, seller):
        client.post("/api/logout")
        assert self._action(client, seller["item_id"], "reserve").status_code == 401

    def test_t05_seller_cannot_reserve_their_own_item(self, client, seller):
        assert self._action(client, seller["item_id"], "reserve").status_code == 403

    def test_t06_buyer_reserves_an_on_sale_item(self, client, seller, buyer):
        assert self._action(client, seller["item_id"], "reserve").status_code == 200
        assert client.get(f"/api/items/{seller['item_id']}").get_json()["data"]["status"] == "RESERVED"

    def test_t07_buyer_cannot_confirm_a_reservation(self, client, seller, buyer):
        self._action(client, seller["item_id"], "reserve")
        assert self._action(client, seller["item_id"], "sell").status_code == 403

    def test_t08_seller_confirms_the_sale(self, client, seller, buyer):
        self._action(client, seller["item_id"], "reserve")
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        assert self._action(client, seller["item_id"], "sell").status_code == 200
        assert client.get(f"/api/items/{seller['item_id']}").get_json()["data"]["status"] == "SOLD"

    def test_t09_selling_an_unreserved_item_is_refused(self, client, seller, buyer):
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        assert self._action(client, seller["item_id"], "sell").status_code == 400

    def test_t10_seller_cancels_a_reservation(self, client, seller, buyer):
        self._action(client, seller["item_id"], "reserve")
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        assert self._action(client, seller["item_id"], "cancel_reserve").status_code == 200
        assert client.get(f"/api/items/{seller['item_id']}").get_json()["data"]["status"] == "ON_SALE"

    def test_t11_buyer_cannot_take_an_item_offline(self, client, seller, buyer):
        assert self._action(client, seller["item_id"], "off_shelf").status_code == 403

    def test_t12_seller_takes_the_item_offline_and_relists_it(self, client, seller):
        assert self._action(client, seller["item_id"], "off_shelf").status_code == 200
        assert self._action(client, seller["item_id"], "relist").status_code == 200
        assert client.get(f"/api/items/{seller['item_id']}").get_json()["data"]["status"] == "ON_SALE"

    def test_t13_relist_is_refused_while_on_sale(self, client, seller):
        assert self._action(client, seller["item_id"], "relist").status_code == 400

    def test_t14_sold_is_terminal(self, client, seller, buyer):
        self._action(client, seller["item_id"], "reserve")
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        self._action(client, seller["item_id"], "sell")
        for action in ("relist", "off_shelf", "sell"):
            assert self._action(client, seller["item_id"], action).status_code == 400

    def test_t15_a_failed_guard_leaves_the_row_unchanged(self, client, seller, buyer):
        self._action(client, seller["item_id"], "reserve")
        client.post("/api/logout")
        client.post("/api/login", json={"username": "buyer_b", "password": "123456"})
        self._action(client, seller["item_id"], "sell")          # 403, must not change anything
        assert client.get(f"/api/items/{seller['item_id']}").get_json()["data"]["status"] == "RESERVED"


# --------------------------------------------------------------------- TC-S
class TestSocialS:
    def test_s01_favourite_can_be_added_and_removed(self, client, seller, buyer):
        assert client.post("/api/favorites", json={"item_id": seller["item_id"]}).status_code == 200
        assert len(client.get("/api/favorites").get_json()["data"]) == 1
        assert client.delete(f"/api/favorites/{seller['item_id']}").status_code == 200
        assert client.get("/api/favorites").get_json()["data"] == []

    def test_s02_duplicate_favourite_is_refused(self, client, seller, buyer):
        client.post("/api/favorites", json={"item_id": seller["item_id"]})
        assert client.post("/api/favorites", json={"item_id": seller["item_id"]}).status_code == 400

    def test_s03_favourite_requires_a_session(self, client, seller, buyer):
        client.post("/api/logout")
        assert client.post("/api/favorites", json={"item_id": seller["item_id"]}).status_code == 401

    def test_s04_favourite_without_item_id_is_refused(self, client, buyer):
        assert client.post("/api/favorites", json={}).status_code == 400

    def test_s05_comments_are_public_and_ordered(self, client, seller, buyer):
        client.post(f"/api/items/{seller['item_id']}/comments", json={"content": "first"})
        client.post(f"/api/items/{seller['item_id']}/comments", json={"content": "second"})
        client.post("/api/logout")
        rows = client.get(f"/api/items/{seller['item_id']}/comments").get_json()["data"]
        assert [r["content"] for r in rows] == ["first", "second"]
        assert rows[0]["user_nickname"] == "Bob"

    def test_s06_empty_comment_is_refused(self, client, seller, buyer):
        assert client.post(f"/api/items/{seller['item_id']}/comments",
                           json={"content": "   "}).status_code == 400

    def test_s07_commenting_requires_a_session(self, client, seller, buyer):
        client.post("/api/logout")
        assert client.post(f"/api/items/{seller['item_id']}/comments",
                           json={"content": "hi"}).status_code == 401

    def test_s08_comment_appears_on_the_detail_page(self, client, seller, buyer):
        client.post(f"/api/items/{seller['item_id']}/comments", json={"content": "still available?"})
        body = client.get(f"/api/items/{seller['item_id']}").get_json()["data"]
        assert len(body["comments"]) == 1

    def test_s09_message_can_be_sent_and_read_back(self, client, seller, buyer):
        client.post("/api/messages", json={"receiver_id": seller["id"], "content": "hello"})
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        rows = client.get(f"/api/messages/{buyer['id']}").get_json()["data"]
        assert rows[-1]["content"] == "hello"

    def test_s10_message_to_an_unknown_user_is_refused(self, client, buyer):
        assert client.post("/api/messages",
                           json={"receiver_id": 9999, "content": "x"}).status_code == 404

    def test_s11_message_without_content_is_refused(self, client, seller, buyer):
        assert client.post("/api/messages",
                           json={"receiver_id": seller["id"], "content": ""}).status_code == 400

    def test_s12_conversation_list_groups_by_partner(self, client, seller, buyer):
        client.post("/api/messages", json={"receiver_id": seller["id"], "content": "m1"})
        client.post("/api/messages", json={"receiver_id": seller["id"], "content": "m2"})
        rows = client.get("/api/messages").get_json()["data"]
        assert len(rows) == 1 and rows[0]["content"] == "m2"

    def test_s13_conversation_list_keeps_one_row_per_partner(self, client, seller, buyer):
        register_and_login(client, "third_c", nickname="Cleo")
        third = client.get("/api/user/me").get_json()["data"]["id"]
        client.post("/api/messages", json={"receiver_id": seller["id"], "content": "to alice"})
        client.post("/api/messages", json={"receiver_id": third, "content": "to cleo"})
        rows = client.get("/api/messages").get_json()["data"]
        assert len(rows) == 2
        assert {r["other_nickname"] for r in rows} == {"Alice", "Cleo"}

    def test_s14_conversation_order_is_undefined_when_timestamps_tie(self, client, seller, buyer):
        """Documents a real limitation rather than an expectation.

        The list is ordered by created_at DESC, and created_at defaults to
        CURRENT_TIMESTAMP, which SQLite resolves to whole seconds. Two
        conversations touched inside the same second therefore compare equal and
        SQLite is free to return them in any order. The test asserts only that
        both survive the grouping; the ordering guarantee is reported as a
        limitation in the technical report.
        """
        register_and_login(client, "third_d", nickname="Cleo")
        third = client.get("/api/user/me").get_json()["data"]["id"]
        client.post("/api/messages", json={"receiver_id": seller["id"], "content": "earlier"})
        client.post("/api/messages", json={"receiver_id": third, "content": "later"})
        rows = client.get("/api/messages").get_json()["data"]
        assert len(rows) == 2
        assert {r["other_nickname"] for r in rows} == {"Alice", "Cleo"}
        assert any(r["content"] == "later" for r in rows)

    def test_s15_reading_a_thread_marks_it_read(self, client, seller, buyer, tmp_path):
        import sqlite3
        import models
        client.post("/api/messages", json={"receiver_id": seller["id"], "content": "unread"})
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        client.get(f"/api/messages/{buyer['id']}")
        conn = sqlite3.connect(models.DB_FILE)
        pending = conn.execute("SELECT COUNT(*) FROM messages WHERE is_read = 0").fetchone()[0]
        conn.close()
        assert pending == 0

    def test_s16_messages_require_a_session(self, client):
        assert client.get("/api/messages").status_code == 401


# --------------------------------------------------------------------- TC-P
class TestPersonalP:
    def test_p01_my_items_lists_only_my_own(self, client, seller, buyer):
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        rows = client.get("/api/user/items").get_json()["data"]
        assert len(rows) == 1 and rows[0]["seller_id"] == seller["id"]

    def test_p02_sold_list_starts_empty(self, client, seller):
        assert client.get("/api/user/sold").get_json()["data"] == []

    def test_p03_sold_list_collects_transacted_items(self, client, seller, buyer):
        client.post(f"/api/items/{seller['item_id']}/status", json={"action": "reserve"})
        client.post("/api/logout")
        client.post("/api/login", json={"username": "seller_a", "password": "123456"})
        client.post(f"/api/items/{seller['item_id']}/status", json={"action": "sell"})
        rows = client.get("/api/user/sold").get_json()["data"]
        assert len(rows) == 1 and rows[0]["status"] == "SOLD"

    def test_p04_my_items_carries_a_cover_image_key(self, client, seller):
        assert "cover_image" in client.get("/api/user/items").get_json()["data"][0]

    def test_p05_personal_endpoints_require_a_session(self, client):
        assert client.get("/api/user/items").status_code == 401
        assert client.get("/api/user/sold").status_code == 401
