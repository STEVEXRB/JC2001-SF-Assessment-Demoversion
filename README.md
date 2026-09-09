# JC2001-SF-Assessment
AI Group 9 assessment for the course of JC2001-Introduction To Software Engineering

# Campus Second-hand Trading Platform (PoC)

A lightweight web application for students to buy, sell, and exchange second-hand goods within a university campus. Built as a Proof of Concept (PoC) for a Software Engineering course, this project demonstrates core functionalities like user authentication, product listing, search, favorites, comments, private messaging, and transaction status management.

## Features

- User registration and login (session-based)
- Publish products with title, description, price, category, condition, and up to 3 images
- Browse and search products with keyword, category filter, and sorting
- Product detail page with images, seller info, comments, and favorite button
- Private messaging between buyers and sellers (polling-based)
- Transaction status management: ON_SALE → RESERVED → SOLD (or OFF_SHELF)
- Personal center: my listings, favorites, sold items, and message inbox

## Tech Stack

- **Backend**: Python Flask
- **Database**: SQLite (file-based)
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **Image Storage**: Local filesystem (`uploads/` directory)

## Project Structure

campus-market-poc/
├── app.py # Flask application entry point
├── models.py # Database initialization
├── requirements.txt
├── static/
│ ├── css/style.css
│ ├── js/api.js
│ ├── js/main.js
│ └── images/default.png
├── templates/index.html
├── uploads/ # Created at runtime
└── data.db # Created at runtime

## Setup and Run

### Prerequisites
- Python 3.8+

### Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/campus-market-poc.git
   cd campus-market-poc

2. Install dependencies:
   pip install -r requirements.txt

3. Run the application:
   python app.py

### Run as Single Executable (Optional)
   pip install pyinstaller
   pyinstaller --onefile --add-data "templates;templates" --add-data "static;static" app.py
