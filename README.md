# Campus Second-hand Trading Platform (PoC)

A lightweight web application that lets students buy, sell and exchange second-hand
goods inside a university campus. It is the Proof of Concept delivered for **JC2001
Introduction to Software Engineering** (AI Group 9): a single-page front end talking
to a JSON API, with no framework and no build step.

The PoC covers the full trading loop — register, publish, browse, search, discuss,
message, reserve and complete a sale — plus the personal centre and the transaction
status machine that holds the loop together.

---

## Table of contents

- [Features](#features)
- [Screens](#screens)
- [UI / UX](#ui--ux)
- [Transaction status model](#transaction-status-model)
- [Tech stack](#tech-stack)
- [Project structure](#project-structure)
- [API reference](#api-reference)
- [Database schema](#database-schema)
- [Demo data](#demo-data)
- [Setup and run](#setup-and-run)
- [Tests and performance](#tests-and-performance)
- [Known limitations](#known-limitations)
- [Course deliverables](#course-deliverables)

---

## Features

**Accounts**
- Registration with username, password, nickname, email and student ID
- Session-based login / logout; passwords stored as Werkzeug hashes, never returned by the API
- Role-aware UI: controls you are not allowed to use are not rendered at all

**Listings**
- Publish with title, description, price, category, condition and up to 3 images
- Edit and soft-delete (take offline) your own listings; ownership enforced server-side
- Browse with keyword search (title + description, case-insensitive), category filter, status filter, price/latest sorting and 12-per-page pagination
- Filter state is preserved in the URL hash, so the browser back button returns to the same result set

**Product detail**
- Image gallery with thumbnail switching
- Seller card with avatar and join date
- Public comment thread
- One-click favourite toggle
- Deep link to any listing via `#item-<id>` — the hash is the router

**Private messaging**
- Buyer↔seller conversations grouped by partner, newest first
- Per-listing chat entry point from the detail page
- Unread counts refresh when you open the message centre; reading a thread marks it read

**Personal centre**
- Three tabs: my listings, my favourites, my sold items
- Live counters for listings / favourites / sold / unread
- Inline status actions (reserve, confirm sale, take offline, relist) from the listing card

**Uploads**
- Drag-and-drop dropzone with thumbnail preview and per-image removal
- Extension allow-list (`png jpg jpeg gif webp`), 5 MB request cap, server-side random UUID filenames
- Images are stored on the local filesystem and served back from `/uploads/<filename>`

## Screens

Five full-page views are swapped client-side inside a single document:

| View | Route / trigger | Contents |
|------|-----------------|----------|
| Home | `#` | Search bar, category chips, sort control, listing grid, pagination |
| Detail | `#item-<id>` | Two-column layout: gallery + comments on the left, sticky purchase card on the right |
| Publish | nav → Sell | Listing form with chip selectors, dropzone and a live card preview |
| Auth | nav → Log in, or any guarded action | Tabbed login / register panel |
| Profile | nav → avatar | Profile header, stat tiles, three tabs, message centre and chat overlay |

## UI / UX

The whole interface is vanilla HTML/CSS/JS served from one template.

- **Design tokens** — 38 CSS custom properties in `:root` (colour, radius, shadow, spacing) so the theme can be retuned from one block.
- **Feedback layer** — `alert()` is replaced by a toast system (success / error / info) and a reusable confirm dialog for destructive actions such as taking a listing offline.
- **Loading and empty states** — skeleton cards while the grid loads, inline empty states with actionable hints, three-dot loaders for panels.
- **Forms** — labelled fields with hints, a live description counter, category/condition chip selectors kept in sync with hidden `<select>` elements, and a live product-card preview beside the publish form.
- **Detail page** — gallery with thumbnail switching on the left; sticky purchase card with a status badge, meta list and role-aware actions on the right.
- **Chat** — bubble layout with own/other alignment, timestamps and bottom-anchored messages.
- **Responsive** — breakpoints at 1040 / 900 / 760 px; the grid collapses to two columns on phones, and `prefers-reduced-motion` is honoured.
- **Accessibility** — visible keyboard focus rings, `aria-*` on tabs and dialogs, `Esc` closes menus and overlays, and all user-supplied content is HTML-escaped before rendering.

## Transaction status model

A listing moves through a small guarded state machine. Every transition is checked
for both the caller's role and the current status, so an illegal action is rejected
without touching the row.

```
                 reserve (buyer)              sell (seller)
   ON_SALE ─────────────────────▶ RESERVED ─────────────────────▶ SOLD
      │  ▲                            │                              (terminal)
      │  │ cancel_reserve (seller)    │
      │  └────────────────────────────┘
      │  ▲
      │  │ relist (seller)
      ▼  │
   OFF_SHELF
```

| Action | From → To | Allowed role |
|--------|-----------|--------------|
| `reserve` | `ON_SALE` → `RESERVED` | buyer (never the seller) |
| `sell` | `RESERVED` → `SOLD` | seller |
| `cancel_reserve` | `RESERVED` → `ON_SALE` | seller |
| `off_shelf` | `ON_SALE` → `OFF_SHELF` | seller |
| `relist` | `OFF_SHELF` → `ON_SALE` | seller |

`SOLD` is terminal, and offline listings disappear from the public catalogue.

## Tech stack

| Layer | Choice |
|-------|--------|
| Backend | Python + Flask 2.3 |
| Database | SQLite (single file, no server) |
| Frontend | Vanilla HTML / CSS / JavaScript — no framework, no bundler |
| Image storage | Local filesystem (`uploads/`) |
| Auth | Flask session cookie + Werkzeug password hashing |
| Tests | pytest (86 cases) |

## Project structure

```
JC2001-SF-Assessment/
├── app.py                     # Flask application: 23 routes, app factory + API
├── models.py                  # Schema definition and connection helper
├── requirements.txt
├── start.bat                  # Windows launcher
├── seed.py                    # Reproducible demo dataset; `python seed.py`
├── demo_covers.py             # The ten demo cover illustrations seed.py writes out
├── data.db                    # SQLite database, seeded with demo data
├── data.db.backup-20260923    # Pre-seeding snapshot, for restoring a clean dataset
├── static/
│   ├── css/
│   │   └── style.css          # Design tokens + component styles (~1,000 lines)
│   ├── js/
│   │   ├── api.js             # fetch wrapper: JSON, credentials, error surfacing
│   │   └── main.js            # Views, router, rendering, form and chat logic
│   └── images/
│       └── favicon.svg
├── templates/
│   └── index.html             # The single page: all five views
├── tests/
│   ├── conftest.py            # Fixtures: throwaway DB + upload dir per test
│   ├── test_api.py            # 80 API tests across seven areas
│   ├── benchmark.py           # In-process latency harness
│   └── scale.py               # Read-path scaling from 100 to 2,000 rows
├── uploads/                   # Uploaded and demo cover images
└── README.md
```

Runtime code totals roughly 3,350 lines; tests add another ~700.

## API reference

All endpoints return JSON in the shape `{"code": <int>, "msg": <string>, "data": <any>}`.
HTTP status codes mirror `code`, so a failed call is always a non-2xx response.

### Pages

| Method | Path | Purpose |
|--------|------|---------|
| `GET` | `/` | The single-page shell |
| `GET` | `/uploads/<filename>` | Serves an uploaded image |

### Accounts

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `POST` | `/api/register` | — | Create an account; rejects duplicate usernames and empty credentials |
| `POST` | `/api/login` | — | Start a session |
| `POST` | `/api/logout` | — | Clear the session |
| `GET` | `/api/user/me` | ✔ | Current profile; strips the password hash |

### Listings

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `GET` | `/api/items` | — | Catalogue. Query: `keyword`, `category`, `status`, `sort` (`latest`/`price_asc`/`price_desc`), `page` |
| `GET` | `/api/items/<id>` | — | Detail, including all images and the comment thread |
| `POST` | `/api/items` | ✔ | Publish a listing |
| `PUT` | `/api/items/<id>` | ✔ | Edit a listing (owner only) |
| `DELETE` | `/api/items/<id>` | ✔ | Soft delete → `OFF_SHELF` (owner only) |
| `POST` | `/api/items/<id>/status` | ✔ | Apply a status transition (see above) |

### Images, favourites, comments, messages

| Method | Path | Auth | Purpose |
|--------|------|------|---------|
| `POST` | `/api/upload` | ✔ | Upload 1..n images, returns generated filenames |
| `GET` | `/api/favorites` | ✔ | My favourites, newest first |
| `POST` | `/api/favorites` | ✔ | Add a favourite; duplicates rejected by a unique constraint |
| `DELETE` | `/api/favorites/<item_id>` | ✔ | Remove a favourite |
| `GET` | `/api/items/<id>/comments` | — | Public comment list, oldest first |
| `POST` | `/api/items/<id>/comments` | ✔ | Post a comment |
| `GET` | `/api/messages` | ✔ | Conversation list: one row per partner, latest message |
| `GET` | `/api/messages/<user_id>` | ✔ | Full thread with one partner; marks received messages read |
| `POST` | `/api/messages` | ✔ | Send a message, optionally attached to a listing |
| `GET` | `/api/user/items` | ✔ | My listings, all statuses |
| `GET` | `/api/user/sold` | ✔ | My sold listings |

## Database schema

Six tables, all foreign keys declared at creation time.

| Table | Key columns | Notes |
|-------|-------------|-------|
| `users` | `id`, `username` (unique), `password_hash`, `nickname`, `email`, `student_id`, `avatar`, `created_at` | `username` is the login handle |
| `items` | `id`, `seller_id` → `users`, `title`, `description`, `price`, `category`, `condition`, `status`, `created_at`, `updated_at` | `status` defaults to `ON_SALE` |
| `images` | `id`, `item_id` → `items`, `file_path`, `created_at` | Insertion order is the gallery order |
| `favorites` | `id`, `user_id`, `item_id`, `created_at` | `UNIQUE(user_id, item_id)` blocks duplicates |
| `comments` | `id`, `item_id`, `user_id`, `content`, `created_at` | Public, permanently attached to a listing |
| `messages` | `id`, `sender_id`, `receiver_id`, `item_id`, `content`, `is_read`, `created_at` | `item_id` is optional: a thread can start from a listing or from the message centre |

## Demo data

The repository ships with a seeded `data.db` so every screen has something to show:
**11 listings** across all five categories and all four statuses, 10 cover illustrations,
3 favourites, 5 comments and 8 private messages across two conversations.

| Account | Password | Display name | Listings | Notes |
|---------|----------|--------------|----------|-------|
| `demo_wang` | `123456` | Alex Wang | 3 (2 on sale, 1 removed) | Textbooks and a desk lamp; the removed drafting kit shows the `OFF_SHELF` state |
| `demo_li` | `123456` | Brian Li | 3 (2 on sale, 1 sold) | The sold ThinkPad demonstrates the terminal state; holds 3 favourites; has an active thread with Dana Chen |
| `demo_zhang` | `123456` | Cindy Zhang | 2 (1 reserved) | The reserved mountain bike demonstrates the mid-transaction state |
| `demo_chen` | `123456` | Dana Chen | 3 (all on sale) | The buyer side of the ThinkPad conversation |

| Category | Listings | | Status | Listings |
|----------|---------:|-|--------|---------:|
| Textbooks | 2 | | `ON_SALE` | 8 |
| Electronics | 4 | | `RESERVED` | 1 |
| Daily use | 2 | | `SOLD` | 1 |
| Sports gear | 2 | | `OFF_SHELF` | 1 |
| Other | 1 | | | |

One of the eleven listings (the off-shelf drafting kit) deliberately has no
photo, so the empty-gallery placeholder on the detail page stays demonstrable —
open it from the seller's personal centre. The ten covers under
`uploads/demo-*.svg` are generated flat illustrations, not photographs — upload
real images through the publish form to replace them.

Because `uploads/` is git-ignored, the illustrations cannot ship with the
repository. `seed.py` materialises them from `demo_covers.py` on the machine that
runs the seed, so a fresh clone gets working covers instead of 404s. A file that
is already on disk is never overwritten, so a placeholder you swapped for a real
photo survives a re-seed.

Because `data.db` and `uploads/` are git-ignored, **`seed.py` is the reproducible
way to rebuild this dataset**:

```bash
python seed.py            # seeds only when users + items are both empty
python seed.py --force    # wipes the six tables and seeds again (ids stay stable)
```

To discard the demo data and start from an empty catalogue instead, restore the
snapshot taken before seeding:

```bash
cp data.db.backup-20260923 data.db
```

## Setup and run

**Prerequisites** — Python 3.8 or newer.

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Load the demo dataset (optional, but recommended for a walkthrough)
python seed.py

# 3. Start the server
python app.py
```

Then open <http://127.0.0.1:5000>. On Windows you can also double-click `start.bat`.

The app stores everything locally: the SQLite file `data.db` and uploaded images in
`uploads/`. Both are created automatically on first run, and both are git-ignored — which
is why a fresh clone starts with an empty catalogue until you run `seed.py`.

### Run against a clean database

`python app.py` calls `models.init_db()`, which only creates tables that are missing —
it never drops or overwrites data. To start from scratch, delete `data.db`, restart, and
run `python seed.py` again if you want the demo listings back.

### Optional: single-file executable

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
```

PyInstaller cannot cross-compile, so a Windows `.exe` will not run on macOS — each
platform needs its own build. The bundled file still expects a writable working
directory for `data.db` and `uploads/`.

## Tests and performance

```bash
python -m pytest tests/ -q      # 86 tests
python tests/benchmark.py       # latency per endpoint
python tests/scale.py           # read paths from 100 to 2,000 rows
```

Every test runs against a throwaway SQLite file and upload directory, so the shipped
`data.db` is never touched. Current status: **86 passed**.

| Area | Prefix | Cases | Covers |
|------|--------|-------|--------|
| Accounts | `A` | 10 | Registration, duplicate rejection, hashing, session guards |
| Catalogue | `C` | 14 | Search, filters, sorting, pagination, detail payload |
| Listings | `L` | 12 | Publish/edit/soft-delete, validation, ownership |
| Uploads | `U` | 8 | Extension allow-list, UUID names, size cap, multi-file |
| Transitions | `T` | 15 | Every legal and illegal status transition, terminal states |
| Social | `S` | 16 | Favourites, comments, messaging, read receipts |
| Personal | `P` | 5 | Ownership scoping of the personal endpoints |
| Assets | `test_demo_covers.py` | 6 | Demo cover artwork exists, is valid SVG and is served |

`benchmark.py` measures in-process request handling with Flask's test client, on a
database of 500 listings, 22 users, 61 conversation threads and a 40-message thread.
Because the network and the browser are removed, these figures are a **lower bound on
what a user experiences** and an upper bound on what the application code contributes.

| Operation | Median (ms) | p95 (ms) |
|-----------|------------:|---------:|
| Comment thread | 1.87 | 2.13 |
| Conversation list (60 threads) | 1.96 | 2.19 |
| Open a 40-message thread | 2.42 | 2.73 |
| Browse the catalogue | 2.51 | 2.71 |
| Keyword search, no match | 2.51 | 2.90 |
| Category filter + price sort | 2.54 | 2.82 |
| Keyword search across title + description | 2.58 | 2.95 |
| Open a listing detail page | 2.82 | 3.25 |
| Personal centre grid | 3.48 | 3.76 |
| Publish a listing | 4.49 | 4.94 |
| Add and remove a favourite | 9.02 | 9.65 |
| Toggle offline + relist | 9.98 | 10.67 |

Reads stay in the low single-digit millisecond range at 500 rows. The two write figures
cover a round trip of *two* mutations each; the pair is dominated by the cost of opening
a fresh SQLite connection per request, which is where the obvious optimisation lies.

## Known limitations

These are deliberate PoC boundaries, documented rather than hidden:

- **`app.secret_key` is hard-coded.** It must come from the environment before any real deployment.
- **SQLite foreign keys are not enabled.** The schema declares them, but no `PRAGMA foreign_keys = ON` is issued, so referential integrity is not enforced at runtime.
- **Conversation ordering is undefined on tied timestamps.** `SECOND`-resolution `created_at` plus a `MAX(id)` grouping means two threads created in the same second may order arbitrarily. Reproduced by `test_s14`.
- **The "1 to 3 images" rule is client-side only.** `POST /api/items` accepts an arbitrary image list, so the constraint is trusted, not enforced.
- **Private messaging is poll-based.** There is no push channel; updates appear when you navigate.
- **No CSRF protection** on the JSON endpoints, and no rate limiting on login.
- **Python 3.12+ emits a `DeprecationWarning`** for the default `datetime` adapters used in `sqlite3` (16 warnings across the suite). Functionally harmless today.

## Course deliverables

| Deliverable | Weight | Status |
|-------------|--------|--------|
| Project Proposal | required, ungraded | Submitted — 4..8 body pages |
| Technical Report | 50% | 40..60 body pages, eight chapters, figure and table lists |
| PoC software | 30% | This repository, plus an 8..12 page user manual |
| Presentation | 20% | Slide deck and a recorded walkthrough |

All written deliverables follow the same formatting rules: A4, 1-inch margins, single
column, 12 pt Times New Roman, 1.5 line spacing, submitted as a single PDF. Source code
is kept out of the report body.

---

*Group 9 — JC2001 Introduction to Software Engineering.*
