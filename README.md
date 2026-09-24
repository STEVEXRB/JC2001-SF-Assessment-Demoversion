# JC2001-SF-Assessment
AI Group 9 assessment for the course of JC2001-Introduction To Software Engineering

# Campus Second-hand Trading Platform (PoC)

A lightweight web application for students to buy, sell, and exchange second-hand goods within a university campus. Built as a Proof of Concept (PoC) for a Software Engineering course, this project demonstrates core functionalities like user authentication, product listing, search, favorites, comments, private messaging, and transaction status management.

## Features

- User registration and login (session-based)
- Publish products with title, description, price, category, condition, and up to 3 images
- Browse and search products with keyword, category filter, and sorting
- Product detail page with image gallery, seller info, comments, and favorite button
- Private messaging between buyers and sellers (polling-based)
- Transaction status management: ON_SALE → RESERVED → SOLD (or OFF_SHELF)
- Personal center: my listings, favorites, sold items, and message inbox
- Deep link to a single product via `#item-<id>`

## UI / UX

The interface is a single-page app built with vanilla HTML/CSS/JS — no framework, no build step.

- **Design tokens** — colors, radii, shadows and spacing are declared as CSS custom properties in `:root`, so the whole theme can be retuned from one place.
- **Feedback layer** — `alert()` is replaced by a toast system (success / error / info) plus a reusable confirm dialog for destructive actions such as taking an item offline.
- **Loading & empty states** — skeleton cards while the grid loads, inline empty states with actionable hints, three-dot loaders for panels.
- **Forms** — labelled fields with hints, a desc counter, category/condition chip selectors kept in sync with hidden `<select>` elements, a drag-and-drop image dropzone with thumbnail removal, and a live product-card preview.
- **Detail page** — two-column layout: gallery with thumbnail switching on the left, sticky purchase card with status badge, meta list and role-aware actions on the right.
- **Chat** — bubble layout with own/other alignment, timestamps, and bottom-anchored messages.
- **Responsive** — breakpoints at 1040 / 900 / 760 px; the grid collapses to two columns on phones.
- **Accessibility** — keyboard focus rings, `aria-*` on tabs and dialogs, `Esc` closes menus and overlays, and all user content is HTML-escaped before rendering.

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (file-based)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Image Storage**: Local filesystem (`uploads/` directory)

## Project Structure
   
```
campus-market-poc/
├── app.py                     # Flask application entry point
├── models.py                  # Database initialization
├── requirements.txt
├── start.bat                  # Windows launcher
├── static/
│   ├── css/
│   │   └── style.css          # Design tokens + component styles
│   ├── js/
│   │   ├── api.js             # API request wrapper
│   │   └── main.js            # Frontend logic
│   └── images/
│       └── favicon.svg        # Site icon
├── templates/
│   └── index.html             # Single-page HTML template
├── uploads/                   # Uploaded images (created at runtime)
├── data.db                    # SQLite database file (created at runtime)
└── README.md
```


## Demo Data

The repository ships with demo data in `data.db` so every screen has content to show:

| Account | Password | Display name | Listings |
|---------|----------|--------------|----------|
| `demo_wang` | `123456` | Alex Wang | 2 items |
| `demo_li` | `123456` | Brian Li | 3 items, 4 favorites, an active conversation |
| `demo_zhang` | `123456` | Cindy Zhang | 2 items (one reserved) |
| `demo_chen` | `123456` | Dana Chen | 3 items |

Product covers under `uploads/demo-*.svg` are generated flat illustrations — replace them with real photos by uploading through the publish form.

To drop the demo data and return to your own dataset, restore the backup that was taken before seeding:

```bash
cp data.db.backup-20260919 data.db
```

## Setup and Run

### Prerequisites
- Python 3.8+

### Installation

1. Clone the repository:

   ```bash
   git clone https://github.com/yourusername/campus-market-poc.git
   cd campus-market-poc
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Run the application:

   ```bash
   python app.py
   ```

   Then open <http://127.0.0.1:5000>. The app stores everything locally: the
   SQLite file `data.db` and uploaded images in `uploads/`.

### Run as Single Executable (Optional)

```bash
pip install pyinstaller
pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
```

PyInstaller cannot cross-compile, so a Windows `.exe` will not run on macOS —
each platform needs its own build.

