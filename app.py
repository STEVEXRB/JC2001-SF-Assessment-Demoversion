# app.py
import os
import uuid
import json
import sqlite3
from datetime import datetime
from functools import wraps

from flask import Flask, render_template, request, jsonify, session, send_from_directory
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import models

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Configure the upload folder
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# Ensure the upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ Helper functions ------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """Decorator: requires login"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'msg': 'Please log in first'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """Get the current logged-in user's information"""
    if 'user_id' not in session:
        return None
    conn = models.get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return dict(user) if user else None

# ------------------ Page routes ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------ User API ------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    email = data.get('email', '').strip()
    student_id = data.get('student_id', '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'msg': 'Username and password cannot be empty'}), 400

    conn = models.get_db()
    # Check whether the username already exists
    existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'code': 400, 'msg': 'Username has already been registered'}), 400

    # Password hashing
    password_hash = generate_password_hash(password)
    conn.execute(
        'INSERT INTO users (username, password_hash, nickname, email, student_id) VALUES (?, ?, ?, ?, ?)',
        (username, password_hash, nickname, email, student_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Registration successful'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    conn = models.get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'code': 401, 'msg': 'Incorrect username or password'}), 401

    session['user_id'] = user['id']
    return jsonify({'code': 200, 'msg': 'Login successful', 'data': {'id': user['id'], 'username': user['username']}})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'code': 200, 'msg': 'Logged out successfully'})

@app.route('/api/user/me', methods=['GET'])
@login_required
def get_me():
    user = get_current_user()
    if user:
        # Do not return sensitive information such as password hashes
        safe_user = {k: user[k] for k in ['id', 'username', 'nickname', 'email', 'student_id', 'avatar', 'created_at']}
        return jsonify({'code': 200, 'data': safe_user})
    return jsonify({'code': 401, 'msg': 'Not logged in'}), 401

# ------------------ Item API ------------------
@app.route('/api/items', methods=['GET'])
def get_items():
    """Product list, supports keyword, category, status, page, sort"""
    keyword = request.args.get('keyword', '').strip()
    category = request.args.get('category', '').strip()
    status = request.args.get('status', '').strip()
    page = int(request.args.get('page', 1))
    per_page = 12
    sort = request.args.get('sort', 'latest')  # latest, price_asc, price_desc

    offset = (page - 1) * per_page

    query = "SELECT i.*, u.nickname AS seller_nickname, " \
            "(SELECT file_path FROM images WHERE item_id = i.id LIMIT 1) AS cover_image " \
            "FROM items i JOIN users u ON i.seller_id = u.id WHERE 1=1 "
    params = []

    if keyword:
        query += " AND (i.title LIKE ? OR i.description LIKE ?) "
        params.extend([f'%{keyword}%', f'%{keyword}%'])
    if category:
        query += " AND i.category = ? "
        params.append(category)
    if status:
        query += " AND i.status = ? "
        params.append(status)

    # Sorting
    if sort == 'price_asc':
        query += " ORDER BY i.price ASC "
    elif sort == 'price_desc':
        query += " ORDER BY i.price DESC "
    else:
        query += " ORDER BY i.created_at DESC "

    query += " LIMIT ? OFFSET ?"
    params.extend([per_page, offset])

    conn = models.get_db()
    items = conn.execute(query, params).fetchall()
    # Query total count (for pagination)
    count_query = "SELECT COUNT(*) FROM items i WHERE 1=1 "
    count_params = []
    if keyword:
        count_query += " AND (i.title LIKE ? OR i.description LIKE ?) "
        count_params.extend([f'%{keyword}%', f'%{keyword}%'])
    if category:
        count_query += " AND i.category = ? "
        count_params.append(category)
    if status:
        count_query += " AND i.status = ? "
        count_params.append(status)
    total = conn.execute(count_query, count_params).fetchone()[0]
    conn.close()

    items_list = [dict(item) for item in items]
    return jsonify({
        'code': 200,
        'data': {
            'items': items_list,
            'total': total,
            'page': page,
            'per_page': per_page,
            'total_pages': (total + per_page - 1) // per_page
        }
    })

@app.route('/api/items/<int:item_id>', methods=['GET'])
def get_item_detail(item_id):
    """Item details"""
    conn = models.get_db()
    item = conn.execute('''
        SELECT i.*, u.nickname AS seller_nickname, u.email AS seller_email
        FROM items i JOIN users u ON i.seller_id = u.id
        WHERE i.id = ?
    ''', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': 'Item does not exist'}), 404

    # Get all images
    images = conn.execute('SELECT file_path FROM images WHERE item_id = ?', (item_id,)).fetchall()
    image_list = [row['file_path'] for row in images]

    # Get comments
    comments = conn.execute('''
        SELECT c.*, u.nickname AS user_nickname
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.item_id = ?
        ORDER BY c.created_at ASC
    ''', (item_id,)).fetchall()
    comments_list = [dict(c) for c in comments]

    conn.close()
    item_dict = dict(item)
    item_dict['images'] = image_list
    item_dict['comments'] = comments_list
    return jsonify({'code': 200, 'data': item_dict})

@app.route('/api/items', methods=['POST'])
@login_required
def create_item():
    """Publish an item (including a list of image filenames)"""
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price')
    category = data.get('category', '').strip()
    condition = data.get('condition', '').strip()
    images = data.get('images', [])  # List of image filenames; obtain them via the upload API first

    if not title or not price:
        return jsonify({'code': 400, 'msg': 'Title and price cannot be empty'}), 400

    try:
        price = float(price)
    except ValueError:
        return jsonify({'code': 400, 'msg': 'Price format is incorrect'}), 400

    user_id = session['user_id']
    conn = models.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (seller_id, title, description, price, category, condition, status)
        VALUES (?, ?, ?, ?, ?, ?, 'ON_SALE')
    ''', (user_id, title, description, price, category, condition))
    item_id = cursor.lastrowid

    # Insert image records
    for img_name in images:
        cursor.execute('INSERT INTO images (item_id, file_path) VALUES (?, ?)', (item_id, img_name))

    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Published successfully', 'data': {'item_id': item_id}})

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """Update item information (seller only)"""
    data = request.get_json()
    conn = models.get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': 'Item does not exist'}), 404
    if item['seller_id'] != session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': 'No permission to perform this action'}), 403

    title = data.get('title', item['title'])
    description = data.get('description', item['description'])
    price = data.get('price', item['price'])
    category = data.get('category', item['category'])
    condition = data.get('condition', item['condition'])

    try:
        price = float(price)
    except ValueError:
        conn.close()
        return jsonify({'code': 400, 'msg': 'Price format is incorrect'}), 400

    conn.execute('''
        UPDATE items SET title=?, description=?, price=?, category=?, condition=?, updated_at=?
        WHERE id=?
    ''', (title, description, price, category, condition, datetime.now(), item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Updated successfully'})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """Take item offline (soft delete, status changed to OFF_SHELF)"""
    conn = models.get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': 'Item does not exist'}), 404
    if item['seller_id'] != session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': 'No permission to perform this action'}), 403

    conn.execute("UPDATE items SET status='OFF_SHELF', updated_at=? WHERE id=?", (datetime.now(), item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Item has been taken offline'})

# ------------------ Image upload API ------------------
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_image():
    """Upload one or more images and return a list of filenames"""
    if 'files' not in request.files:
        return jsonify({'code': 400, 'msg': 'No file uploaded'}), 400

    files = request.files.getlist('files')
    saved_names = []
    for file in files:
        if file and allowed_file(file.filename):
            original = secure_filename(file.filename)
            ext = original.rsplit('.', 1)[1].lower()
            # Generate a unique filename
            new_name = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
            saved_names.append(new_name)
        else:
            return jsonify({'code': 400, 'msg': 'Unsupported file type'}), 400

    return jsonify({'code': 200, 'data': saved_names})

# ------------------ Favorite API ------------------
@app.route('/api/favorites', methods=['POST'])
@login_required
def add_favorite():
    data = request.get_json()
    item_id = data.get('item_id')
    if not item_id:
        return jsonify({'code': 400, 'msg': 'Missing item_id'}), 400

    conn = models.get_db()
    try:
        conn.execute('INSERT INTO favorites (user_id, item_id) VALUES (?, ?)', (session['user_id'], item_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'code': 400, 'msg': 'This item has already been favorited'}), 400
    conn.close()
    return jsonify({'code': 200, 'msg': 'Favorite added successfully'})

@app.route('/api/favorites/<int:item_id>', methods=['DELETE'])
@login_required
def remove_favorite(item_id):
    conn = models.get_db()
    conn.execute('DELETE FROM favorites WHERE user_id = ? AND item_id = ?', (session['user_id'], item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Favorite removed successfully'})

@app.route('/api/favorites', methods=['GET'])
@login_required
def get_favorites():
    """Get my favorites list"""
    conn = models.get_db()
    rows = conn.execute('''
        SELECT i.*, u.nickname AS seller_nickname,
               (SELECT file_path FROM images WHERE item_id = i.id LIMIT 1) AS cover_image
        FROM favorites f
        JOIN items i ON f.item_id = i.id
        JOIN users u ON i.seller_id = u.id
        WHERE f.user_id = ?
        ORDER BY f.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

# ------------------ Comment API ------------------
@app.route('/api/items/<int:item_id>/comments', methods=['GET'])
def get_comments(item_id):
    conn = models.get_db()
    comments = conn.execute('''
        SELECT c.*, u.nickname AS user_nickname
        FROM comments c JOIN users u ON c.user_id = u.id
        WHERE c.item_id = ?
        ORDER BY c.created_at ASC
    ''', (item_id,)).fetchall()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(c) for c in comments]})

@app.route('/api/items/<int:item_id>/comments', methods=['POST'])
@login_required
def add_comment(item_id):
    data = request.get_json()
    content = data.get('content', '').strip()
    if not content:
        return jsonify({'code': 400, 'msg': 'Comment content cannot be empty'}), 400

    conn = models.get_db()
    conn.execute('INSERT INTO comments (item_id, user_id, content) VALUES (?, ?, ?)',
                 (item_id, session['user_id'], content))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Comment posted successfully'})

# ------------------ Private message API ------------------
@app.route('/api/messages', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    item_id = data.get('item_id')

    if not receiver_id or not content:
        return jsonify({'code': 400, 'msg': 'Missing recipient or message content'}), 400

    conn = models.get_db()
    # Check whether the recipient exists
    receiver = conn.execute('SELECT id FROM users WHERE id = ?', (receiver_id,)).fetchone()
    if not receiver:
        conn.close()
        return jsonify({'code': 404, 'msg': 'Recipient does not exist'}), 404

    conn.execute('INSERT INTO messages (sender_id, receiver_id, item_id, content) VALUES (?, ?, ?, ?)',
                 (session['user_id'], receiver_id, item_id, content))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Message sent successfully'})

@app.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    """Retrieve the current user's list of private messages (grouped by other users, and displaying the last message of each conversation)"""
    conn = models.get_db()
    user_id = session['user_id']
    
    # Find the ID of the last message in each conversation
    rows = conn.execute('''
        SELECT m.*, u.nickname AS other_nickname
        FROM messages m
        JOIN users u ON u.id = CASE
            WHEN m.sender_id = ? THEN m.receiver_id
            ELSE m.sender_id
        END
        WHERE m.id IN (
            SELECT MAX(id)
            FROM messages
            WHERE sender_id = ? OR receiver_id = ?
            GROUP BY CASE
                WHEN sender_id = ? THEN receiver_id
                ELSE sender_id
            END
        )
        ORDER BY m.created_at DESC
    ''', (user_id, user_id, user_id, user_id)).fetchall()
    
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

@app.route('/api/messages/<int:other_user_id>', methods=['GET'])
@login_required
def get_conversation(other_user_id):
    """Get chat history with a specific user"""
    conn = models.get_db()
    user_id = session['user_id']
    rows = conn.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY created_at ASC
    ''', (user_id, other_user_id, other_user_id, user_id)).fetchall()
    # Mark received messages as read
    conn.execute('UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=? AND is_read=0',
                 (other_user_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

# ------------------ Transaction status API ------------------
@app.route('/api/items/<int:item_id>/status', methods=['POST'])
@login_required
def change_item_status(item_id):
    """Update item status, action: reserve, sell, cancel_reserve, off_shelf, relist"""
    data = request.get_json()
    action = data.get('action')
    if not action:
        return jsonify({'code': 400, 'msg': 'Missing action'}), 400

    # Status transition rules
    transitions = {
        'reserve': {'from': 'ON_SALE', 'to': 'RESERVED', 'role': 'buyer'},   # Buyer reserves item
        'sell': {'from': 'RESERVED', 'to': 'SOLD', 'role': 'seller'},       # Seller confirms the sale
        'cancel_reserve': {'from': 'RESERVED', 'to': 'ON_SALE', 'role': 'seller'}, # Seller cancels the reservation
        'off_shelf': {'from': 'ON_SALE', 'to': 'OFF_SHELF', 'role': 'seller'},
        'relist': {'from': 'OFF_SHELF', 'to': 'ON_SALE', 'role': 'seller'}
    }
    if action not in transitions:
        return jsonify({'code': 400, 'msg': 'Invalid action'}), 400

    rule = transitions[action]
    conn = models.get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': 'Item does not exist'}), 404

    # Permission checks
    if rule['role'] == 'seller' and item['seller_id'] != session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': 'Only the seller can perform this action'}), 403
    if rule['role'] == 'buyer' and item['seller_id'] == session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': 'You cannot reserve your own item'}), 403

    # Status precondition checks
    if item['status'] != rule['from']:
        conn.close()
        return jsonify({'code': 400, 'msg': f'Current status is {item["status"]}, and this action cannot be performed'}), 400

    conn.execute('UPDATE items SET status=?, updated_at=? WHERE id=?',
                 (rule['to'], datetime.now(), item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': 'Status updated successfully'})

# ------------------ Personal center data ------------------
@app.route('/api/user/items', methods=['GET'])
@login_required
def get_my_items():
    """My listed items (all statuses)"""
    conn = models.get_db()
    rows = conn.execute('''
        SELECT i.*, (SELECT file_path FROM images WHERE item_id = i.id LIMIT 1) AS cover_image
        FROM items i WHERE i.seller_id = ? ORDER BY i.created_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

@app.route('/api/user/sold', methods=['GET'])
@login_required
def get_sold_items():
    """My sold items (status = SOLD)"""
    conn = models.get_db()
    rows = conn.execute('''
        SELECT i.*, (SELECT file_path FROM images WHERE item_id = i.id LIMIT 1) AS cover_image
        FROM items i WHERE i.seller_id = ? AND i.status = 'SOLD' ORDER BY i.updated_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

# ------------------ Startup ------------------
if __name__ == '__main__':
    models.init_db()
    app.run(debug=True, port=5000)