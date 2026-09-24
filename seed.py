"""Seed the PoC database with a small, coherent demo dataset.

`data.db` and `uploads/` are git-ignored, so this script is the reproducible way
to get from a clean checkout to a dataset that has something to show on every
screen: four accounts, eleven listings spread over all five categories and all
four statuses, ten cover illustrations, three favourites, five comments and
eight private messages.

Usage
-----
    python seed.py            # seed only when the database is empty
    python seed.py --force    # wipe the six tables and seed again

Beside the rows themselves the script also materialises the ten cover
illustrations listed in `demo_covers.py` into `uploads/`. Those files cannot ship
with the repository — `uploads/` is git-ignored — so without this step every
listing cover would 404 on a fresh clone.
"""

import argparse
import os
import sqlite3
import sys

from werkzeug.security import generate_password_hash

import demo_covers
import models

# Where the cover illustrations are materialised. Mirrors app.UPLOAD_FOLDER.
UPLOAD_DIR = 'uploads'

# All demo accounts share this password, so the marker accounts are easy to
# hand to a marker without a lookup table.
DEMO_PASSWORD = '123456'

# Cover illustrations that belong in uploads/. `None` means "no photo", which
# exercises the empty-gallery placeholder on the detail page. The artwork itself
# lives in demo_covers.py, which seed() writes out via write_covers().
COVER = {
    'book': 'demo-book.svg',
    'laptop': 'demo-laptop.svg',
    'headphones': 'demo-headphones.svg',
    'mouse': 'demo-mouse.svg',
    'lamp': 'demo-lamp.svg',
    'backpack': 'demo-backpack.svg',
    'bicycle': 'demo-bicycle.svg',
    'racket': 'demo-racket.svg',
    'calculator': 'demo-calculator.svg',
    'notes': 'demo-notes.svg',
}

# --------------------------------------------------------------------------
# Demo content
# --------------------------------------------------------------------------
# (username, nickname, email, student_id)
USERS = [
    ('demo_wang', 'Alex Wang', 'alex.wang@campus.edu', '2023010101'),
    ('demo_li', 'Brian Li', 'brian.li@campus.edu', '2023010102'),
    ('demo_zhang', 'Cindy Zhang', 'cindy.zhang@campus.edu', '2023010103'),
    ('demo_chen', 'Dana Chen', 'dana.chen@campus.edu', '2023010104'),
]

# (seller, title, description, price, category, condition, status, cover,
#  created_at, updated_at)
ITEMS = [
    (
        'demo_wang',
        'Data Structures and Algorithm Analysis in C (2nd ed.)',
        'The standard C edition. No highlighting, no torn pages, spine still tight. '
        'Sold because I have already finished the course.\n'
        'Pick up at the library help desk, or the east gate around 18:00.',
        32,
        'textbook',
        'good',
        'ON_SALE',
        COVER['book'],
        '2026-09-22 10:12:00',
        None,
    ),
    (
        'demo_wang',
        'Adjustable LED Desk Lamp (warm / cool, USB-C)',
        'Three colour temperatures, stepless dimming, clamps onto the desk edge. '
        'Comes with the USB-C cable and the original box.\n'
        'Bought last semester for the dorm, replaced by a floor lamp.',
        45,
        'daily_use',
        'like_new',
        'ON_SALE',
        COVER['lamp'],
        '2026-09-18 20:41:00',
        None,
    ),
    (
        'demo_wang',
        'Drafting kit: T-square, set squares, scale ruler',
        'Everything the engineering drawing course asks for: 600 mm T-square, '
        'two set squares, a scale ruler and a compass in a canvas roll.\n'
        'A little wear on the T-square edge, which does not affect the drawings.',
        28,
        'other',
        'good',
        'OFF_SHELF',
        None,
        '2026-09-05 09:30:00',
        '2026-09-11 14:05:00',
    ),
    (
        'demo_li',
        'ThinkPad X1 Carbon Gen 9 - 16G / 512G',
        'i7-1165G7, 16 GB RAM, 512 GB SSD, 14 inch 1920x1200 screen. Battery holds '
        'about six hours of light use. Charger and sleeve included.\n'
        'Small scuff on the outer lid, shown in the photo. Keyboard and trackpad are '
        'spotless. Sold to a buyer from the same department.',
        3200,
        'digital',
        'good',
        'SOLD',
        COVER['laptop'],
        '2026-09-03 15:20:00',
        '2026-09-10 11:40:00',
    ),
    (
        'demo_li',
        'Logitech MX Master 3S Wireless Mouse',
        'Boxed, with the USB receiver and the charging cable. Silent switches, '
        'multi-device pairing over Bluetooth or the dongle.\n'
        'Switched to a trackball, so this one has been sitting in the drawer.',
        380,
        'digital',
        'like_new',
        'ON_SALE',
        COVER['mouse'],
        '2026-09-20 11:05:00',
        None,
    ),
    (
        'demo_li',
        'Sony WH-1000XM4 Noise-cancelling Headphones',
        'Black, with the hard case, 3.5 mm cable and flight adapter. Firmware updated, '
        'ear pads replaced in June so they are still firm.\n'
        'Noise cancelling and battery life both behave as they did on day one.',
        890,
        'digital',
        'good',
        'ON_SALE',
        COVER['headphones'],
        '2026-09-14 19:48:00',
        None,
    ),
    (
        'demo_zhang',
        '26 inch campus commuter mountain bike',
        '17 inch alloy frame, 21 speeds, mechanical disc brakes, mudguards and a rear '
        'rack already fitted. Serviced in August: new chain and brake pads.\n'
        'Reserved by a buyer who is coming to look at it this weekend.',
        420,
        'sports_equipment',
        'good',
        'RESERVED',
        COVER['bicycle'],
        '2026-09-16 08:15:00',
        '2026-09-21 17:22:00',
    ),
    (
        'demo_zhang',
        'Yonex badminton racket + grip tape',
        'Nanoray series, fitted with BG65 at 24 lb. Two spare grips and the full-size '
        'racket bag are included.\n'
        'Used for one season of the departmental league.',
        160,
        'sports_equipment',
        'like_new',
        'ON_SALE',
        COVER['racket'],
        '2026-09-21 13:02:00',
        None,
    ),
    (
        'demo_chen',
        '30L water-resistant campus backpack',
        'Laptop sleeve fits up to 15 inch, separate shoe compartment, padded straps. '
        'Zip pull on the front pocket was replaced with a new one.\n'
        'Survived a whole term of rain without anything inside getting damp.',
        120,
        'daily_use',
        'good',
        'ON_SALE',
        COVER['backpack'],
        '2026-09-19 10:26:00',
        None,
    ),
    (
        'demo_chen',
        'Casio fx-991CN X scientific calculator',
        'The model the maths and circuits courses allow in the exam. Works perfectly, '
        'slide cover included, solar cell and button battery both fine.\n'
        'Bought for the entrance exam, no longer needed.',
        70,
        'digital',
        'like_new',
        'ON_SALE',
        COVER['calculator'],
        '2026-09-13 21:10:00',
        None,
    ),
    (
        'demo_chen',
        'Introduction to Software Engineering - lecture notes',
        'Complete set of handwritten notes for the JC2001 lectures, plus the three '
        'most recent past papers with my own answers marked up.\n'
        'Great for the final revision week. Happy to hand over near the teaching '
        'building.',
        25,
        'textbook',
        'good',
        'ON_SALE',
        COVER['notes'],
        '2026-09-08 16:20:00',
        None,
    ),
]

# (username, item title fragment, content, created_at)
COMMENTS = [
    ('demo_chen', 'Logitech MX Master 3S',
     'Is the scroll wheel still smooth? Any double-click trouble on the main button?',
     '2026-09-20 13:40:00'),
    ('demo_li', 'Logitech MX Master 3S',
     'Wheel is smooth, no double-click. I can bring it to the library tomorrow if that helps.',
     '2026-09-20 14:02:00'),
    ('demo_li', '26 inch campus commuter mountain bike',
     'Is the frame 17 inch? I am 178 cm and want to be sure the size fits.',
     '2026-09-17 09:05:00'),
    ('demo_zhang', '26 inch campus commuter mountain bike',
     'Yes, 17 inch - comfortable for roughly 170 to 185 cm. You can try it before deciding.',
     '2026-09-17 09:31:00'),
    ('demo_chen', 'Data Structures and Algorithm Analysis',
     'Does this edition include the exercise solutions at the back?',
     '2026-09-22 12:18:00'),
]

# (sender, receiver, item title fragment or None, content, is_read, created_at)
MESSAGES = [
    ('demo_chen', 'demo_li', 'ThinkPad X1 Carbon',
     'Hi Brian, is the X1 Carbon still available? I saw the listing is marked sold.',
     1, '2026-09-17 09:12:00'),
    ('demo_li', 'demo_chen', 'ThinkPad X1 Carbon',
     'Hi Dana - it went last week. I do have a spare 65 W USB-C charger if you need one.',
     1, '2026-09-17 09:26:00'),
    ('demo_chen', 'demo_li', 'Logitech MX Master 3S',
     'Good to know. Is the mouse in your listings the same one you mentioned?',
     1, '2026-09-20 12:05:00'),
    ('demo_li', 'demo_chen', 'Logitech MX Master 3S',
     'That is the one. MX Master 3S, 380, boxed with the dongle and the cable.',
     1, '2026-09-20 12:19:00'),
    ('demo_chen', 'demo_li', 'Logitech MX Master 3S',
     'Perfect. Could I pick it up at the east gate on Friday afternoon?',
     0, '2026-09-22 18:47:00'),
    ('demo_zhang', 'demo_wang', 'Data Structures and Algorithm Analysis',
     'Hi Alex, is the data structures book still there? I need it before the midterm.',
     1, '2026-09-22 11:33:00'),
    ('demo_wang', 'demo_zhang', 'Data Structures and Algorithm Analysis',
     'Still available. I can leave it at the library help desk whenever suits you.',
     1, '2026-09-22 11:50:00'),
    ('demo_zhang', 'demo_wang', 'Data Structures and Algorithm Analysis',
     'That works, thanks. How about Friday afternoon?',
     0, '2026-09-23 08:21:00'),
]

# (username, item title fragment)
FAVORITES = [
    ('demo_li', '26 inch campus commuter mountain bike'),
    ('demo_li', 'Adjustable LED Desk Lamp'),
    ('demo_li', '30L water-resistant campus backpack'),
]

TABLES = ['messages', 'comments', 'favorites', 'images', 'items', 'users']


def seed(force=False, db_file=None, upload_dir=UPLOAD_DIR):
    """Populate the database and write the cover files. Returns a dict of row
    counts, or None if the seed was skipped because data was already present."""
    if db_file:
        models.DB_FILE = db_file

    models.init_db()
    conn = models.get_db()
    conn.row_factory = sqlite3.Row

    existing = conn.execute('SELECT COUNT(*) FROM users').fetchone()[0] + \
        conn.execute('SELECT COUNT(*) FROM items').fetchone()[0]
    if existing and not force:
        conn.close()
        print(f'Database already holds data ({existing} rows in users + items).')
        print('Re-run with --force to wipe the six tables and seed again.')
        print('Missing cover illustrations are still repaired by re-running with --force.')
        return None

    # Materialise the cover illustrations the `images` rows point at. Idempotent:
    # a file that is already on disk is kept, so a real photo that replaced a
    # placeholder survives a re-seed.
    covers_written = demo_covers.write_covers(upload_dir)

    with conn:
        for table in TABLES:
            conn.execute(f'DELETE FROM {table}')
        # Restart AUTOINCREMENT counters so the demo ids are stable.
        try:
            conn.execute("DELETE FROM sqlite_sequence WHERE name IN "
                         "('messages','comments','favorites','images','items','users')")
        except sqlite3.OperationalError:
            pass  # sqlite_sequence only exists once an AUTOINCREMENT row was written

        # --- accounts -----------------------------------------------------
        user_ids = {}
        for username, nickname, email, student_id in USERS:
            cursor = conn.execute(
                'INSERT INTO users (username, password_hash, nickname, email, student_id) '
                'VALUES (?, ?, ?, ?, ?)',
                (username, generate_password_hash(DEMO_PASSWORD), nickname, email, student_id),
            )
            user_ids[username] = cursor.lastrowid

        # --- listings -----------------------------------------------------
        item_ids = {}
        for (seller, title, description, price, category, condition, status,
             cover, created_at, updated_at) in ITEMS:
            cursor = conn.execute(
                'INSERT INTO items (seller_id, title, description, price, category, '
                'condition, status, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)',
                (user_ids[seller], title, description, price, category, condition,
                 status, created_at, updated_at or created_at),
            )
            item_ids[title] = cursor.lastrowid
            if cover:
                conn.execute('INSERT INTO images (item_id, file_path) VALUES (?, ?)',
                             (cursor.lastrowid, cover))

        # --- favourites, comments, messages -------------------------------
        for username, fragment in FAVORITES:
            conn.execute('INSERT INTO favorites (user_id, item_id) VALUES (?, ?)',
                         (user_ids[username], _resolve(item_ids, fragment)))

        for username, fragment, content, created_at in COMMENTS:
            conn.execute(
                'INSERT INTO comments (item_id, user_id, content, created_at) VALUES (?, ?, ?, ?)',
                (_resolve(item_ids, fragment), user_ids[username], content, created_at),
            )

        for sender, receiver, fragment, content, is_read, created_at in MESSAGES:
            conn.execute(
                'INSERT INTO messages (sender_id, receiver_id, item_id, content, is_read, '
                'created_at) VALUES (?, ?, ?, ?, ?, ?)',
                (user_ids[sender], user_ids[receiver],
                 _resolve(item_ids, fragment) if fragment else None,
                 content, is_read, created_at),
            )

    counts = {t: conn.execute(f'SELECT COUNT(*) FROM {t}').fetchone()[0] for t in reversed(TABLES)}
    conn.close()
    counts['covers_written'] = covers_written
    return counts


def _resolve(item_ids, fragment):
    """Find an item id by a unique fragment of its title."""
    matches = [i for title, i in item_ids.items() if fragment in title]
    if len(matches) != 1:
        raise KeyError(f'"{fragment}" matched {len(matches)} listings, expected exactly 1')
    return matches[0]


def main():
    parser = argparse.ArgumentParser(description='Seed the PoC database with demo data.')
    parser.add_argument('--force', action='store_true',
                        help='wipe the six tables first, even if data is present')
    parser.add_argument('--db', default=None, help='alternative SQLite file to seed')
    parser.add_argument('--upload-dir', default=UPLOAD_DIR,
                        help='directory the cover illustrations are written into')
    args = parser.parse_args()

    counts = seed(force=args.force, db_file=args.db, upload_dir=args.upload_dir)
    if counts is None:
        return 0

    covers_written = counts.pop('covers_written', [])

    # Fail loudly if any image row still points at a file that is not on disk.
    missing = [
        row['file_path'] for row in models.get_db().execute('SELECT file_path FROM images')
        if not os.path.exists(os.path.join(args.upload_dir, row['file_path']))
    ]
    if missing:
        print('WARNING: cover illustrations missing from '
              f'{args.upload_dir}/:', ', '.join(sorted(set(missing))))

    print('Seeded', models.DB_FILE)
    for table, n in counts.items():
        print(f'  {table:<10} {n:>3}')
    print(f'  {"covers":<10} {len(covers_written):>3} written, '
          f'{len(demo_covers.COVERS) - len(covers_written)} already present')
    print(f'\nAccounts: {", ".join(u[0] for u in USERS)}  (password: {DEMO_PASSWORD})')
    return 0


if __name__ == '__main__':
    sys.exit(main())
