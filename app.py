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

# 配置上传文件夹
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5MB
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_CONTENT_LENGTH

# 确保上传目录存在
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# ------------------ 辅助函数 ------------------
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def login_required(f):
    """装饰器：要求登录"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'code': 401, 'msg': '请先登录'}), 401
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    """获取当前登录用户信息"""
    if 'user_id' not in session:
        return None
    conn = models.get_db()
    user = conn.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],)).fetchone()
    conn.close()
    return dict(user) if user else None

# ------------------ 页面路由 ------------------
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# ------------------ 用户 API ------------------
@app.route('/api/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')
    nickname = data.get('nickname', '').strip()
    email = data.get('email', '').strip()
    student_id = data.get('student_id', '').strip()

    if not username or not password:
        return jsonify({'code': 400, 'msg': '用户名和密码不能为空'}), 400

    conn = models.get_db()
    # 检查用户名是否已存在
    existing = conn.execute('SELECT id FROM users WHERE username = ?', (username,)).fetchone()
    if existing:
        conn.close()
        return jsonify({'code': 400, 'msg': '用户名已被注册'}), 400

    # 密码哈希
    password_hash = generate_password_hash(password)
    conn.execute(
        'INSERT INTO users (username, password_hash, nickname, email, student_id) VALUES (?, ?, ?, ?, ?)',
        (username, password_hash, nickname, email, student_id)
    )
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '注册成功'})

@app.route('/api/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username', '').strip()
    password = data.get('password', '')

    conn = models.get_db()
    user = conn.execute('SELECT * FROM users WHERE username = ?', (username,)).fetchone()
    conn.close()

    if not user or not check_password_hash(user['password_hash'], password):
        return jsonify({'code': 401, 'msg': '用户名或密码错误'}), 401

    session['user_id'] = user['id']
    return jsonify({'code': 200, 'msg': '登录成功', 'data': {'id': user['id'], 'username': user['username']}})

@app.route('/api/logout', methods=['POST'])
def logout():
    session.pop('user_id', None)
    return jsonify({'code': 200, 'msg': '已退出登录'})

@app.route('/api/user/me', methods=['GET'])
@login_required
def get_me():
    user = get_current_user()
    if user:
        # 不返回密码哈希等敏感信息
        safe_user = {k: user[k] for k in ['id', 'username', 'nickname', 'email', 'student_id', 'avatar', 'created_at']}
        return jsonify({'code': 200, 'data': safe_user})
    return jsonify({'code': 401, 'msg': '未登录'}), 401

# ------------------ 商品 API ------------------
@app.route('/api/items', methods=['GET'])
def get_items():
    """商品列表，支持 keyword, category, status, page, sort"""
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

    # 排序
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
    # 查询总数（用于分页）
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
    """商品详情"""
    conn = models.get_db()
    item = conn.execute('''
        SELECT i.*, u.nickname AS seller_nickname, u.email AS seller_email
        FROM items i JOIN users u ON i.seller_id = u.id
        WHERE i.id = ?
    ''', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': '商品不存在'}), 404

    # 获取所有图片
    images = conn.execute('SELECT file_path FROM images WHERE item_id = ?', (item_id,)).fetchall()
    image_list = [row['file_path'] for row in images]

    # 获取留言
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
    """发布商品（包含图片文件名列表）"""
    data = request.get_json()
    title = data.get('title', '').strip()
    description = data.get('description', '').strip()
    price = data.get('price')
    category = data.get('category', '').strip()
    condition = data.get('condition', '').strip()
    images = data.get('images', [])  # 图片文件名列表，需要先通过上传接口获得

    if not title or not price:
        return jsonify({'code': 400, 'msg': '标题和价格不能为空'}), 400

    try:
        price = float(price)
    except ValueError:
        return jsonify({'code': 400, 'msg': '价格格式不正确'}), 400

    user_id = session['user_id']
    conn = models.get_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO items (seller_id, title, description, price, category, condition, status)
        VALUES (?, ?, ?, ?, ?, ?, 'ON_SALE')
    ''', (user_id, title, description, price, category, condition))
    item_id = cursor.lastrowid

    # 插入图片记录
    for img_name in images:
        cursor.execute('INSERT INTO images (item_id, file_path) VALUES (?, ?)', (item_id, img_name))

    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '发布成功', 'data': {'item_id': item_id}})

@app.route('/api/items/<int:item_id>', methods=['PUT'])
@login_required
def update_item(item_id):
    """更新商品信息（仅卖家）"""
    data = request.get_json()
    conn = models.get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': '商品不存在'}), 404
    if item['seller_id'] != session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': '无权操作'}), 403

    title = data.get('title', item['title'])
    description = data.get('description', item['description'])
    price = data.get('price', item['price'])
    category = data.get('category', item['category'])
    condition = data.get('condition', item['condition'])

    try:
        price = float(price)
    except ValueError:
        conn.close()
        return jsonify({'code': 400, 'msg': '价格格式不正确'}), 400

    conn.execute('''
        UPDATE items SET title=?, description=?, price=?, category=?, condition=?, updated_at=?
        WHERE id=?
    ''', (title, description, price, category, condition, datetime.now(), item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '更新成功'})

@app.route('/api/items/<int:item_id>', methods=['DELETE'])
@login_required
def delete_item(item_id):
    """下架商品（软删除，状态改为 OFF_SHELF）"""
    conn = models.get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': '商品不存在'}), 404
    if item['seller_id'] != session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': '无权操作'}), 403

    conn.execute("UPDATE items SET status='OFF_SHELF', updated_at=? WHERE id=?", (datetime.now(), item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '商品已下架'})

# ------------------ 图片上传 API ------------------
@app.route('/api/upload', methods=['POST'])
@login_required
def upload_image():
    """上传单张或多张图片，返回文件名列表"""
    if 'files' not in request.files:
        return jsonify({'code': 400, 'msg': '没有文件'}), 400

    files = request.files.getlist('files')
    saved_names = []
    for file in files:
        if file and allowed_file(file.filename):
            original = secure_filename(file.filename)
            ext = original.rsplit('.', 1)[1].lower()
            # 生成唯一文件名
            new_name = f"{uuid.uuid4().hex}.{ext}"
            file.save(os.path.join(app.config['UPLOAD_FOLDER'], new_name))
            saved_names.append(new_name)
        else:
            return jsonify({'code': 400, 'msg': '不支持的文件类型'}), 400

    return jsonify({'code': 200, 'data': saved_names})

# ------------------ 收藏 API ------------------
@app.route('/api/favorites', methods=['POST'])
@login_required
def add_favorite():
    data = request.get_json()
    item_id = data.get('item_id')
    if not item_id:
        return jsonify({'code': 400, 'msg': '缺少 item_id'}), 400

    conn = models.get_db()
    try:
        conn.execute('INSERT INTO favorites (user_id, item_id) VALUES (?, ?)', (session['user_id'], item_id))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.close()
        return jsonify({'code': 400, 'msg': '已收藏过该商品'}), 400
    conn.close()
    return jsonify({'code': 200, 'msg': '收藏成功'})

@app.route('/api/favorites/<int:item_id>', methods=['DELETE'])
@login_required
def remove_favorite(item_id):
    conn = models.get_db()
    conn.execute('DELETE FROM favorites WHERE user_id = ? AND item_id = ?', (session['user_id'], item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '取消收藏成功'})

@app.route('/api/favorites', methods=['GET'])
@login_required
def get_favorites():
    """获取我的收藏列表"""
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

# ------------------ 留言 API ------------------
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
        return jsonify({'code': 400, 'msg': '留言内容不能为空'}), 400

    conn = models.get_db()
    conn.execute('INSERT INTO comments (item_id, user_id, content) VALUES (?, ?, ?)',
                 (item_id, session['user_id'], content))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '留言成功'})

# ------------------ 私信 API ------------------
@app.route('/api/messages', methods=['POST'])
@login_required
def send_message():
    data = request.get_json()
    receiver_id = data.get('receiver_id')
    content = data.get('content', '').strip()
    item_id = data.get('item_id')

    if not receiver_id or not content:
        return jsonify({'code': 400, 'msg': '缺少接收者或消息内容'}), 400

    conn = models.get_db()
    # 检查接收者是否存在
    receiver = conn.execute('SELECT id FROM users WHERE id = ?', (receiver_id,)).fetchone()
    if not receiver:
        conn.close()
        return jsonify({'code': 404, 'msg': '接收者不存在'}), 404

    conn.execute('INSERT INTO messages (sender_id, receiver_id, item_id, content) VALUES (?, ?, ?, ?)',
                 (session['user_id'], receiver_id, item_id, content))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '消息已发送'})

@app.route('/api/messages', methods=['GET'])
@login_required
def get_messages():
    """获取当前用户的私信列表（按其他用户分组，显示每个会话最后一条消息）"""
    conn = models.get_db()
    user_id = session['user_id']
    # 查询与每个其他用户的最后一条消息
    rows = conn.execute('''
        SELECT m1.*, u.nickname AS other_nickname
        FROM messages m1
        JOIN users u ON (CASE WHEN m1.sender_id = ? THEN m1.receiver_id ELSE m1.sender_id END) = u.id
        JOIN (
            SELECT MAX(id) AS max_id,
                   CASE WHEN sender_id = ? THEN receiver_id ELSE sender_id END AS other_id
            FROM messages
            WHERE sender_id = ? OR receiver_id = ?
            GROUP BY other_id
        ) m2 ON m1.id = m2.max_id
        ORDER BY m1.created_at DESC
    ''', (user_id, user_id, user_id, user_id, user_id)).fetchall()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

@app.route('/api/messages/<int:other_user_id>', methods=['GET'])
@login_required
def get_conversation(other_user_id):
    """获取与某人的聊天记录"""
    conn = models.get_db()
    user_id = session['user_id']
    rows = conn.execute('''
        SELECT * FROM messages
        WHERE (sender_id = ? AND receiver_id = ?) OR (sender_id = ? AND receiver_id = ?)
        ORDER BY created_at ASC
    ''', (user_id, other_user_id, other_user_id, user_id)).fetchall()
    # 将接收的消息标记为已读
    conn.execute('UPDATE messages SET is_read=1 WHERE sender_id=? AND receiver_id=? AND is_read=0',
                 (other_user_id, user_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

# ------------------ 交易状态 API ------------------
@app.route('/api/items/<int:item_id>/status', methods=['POST'])
@login_required
def change_item_status(item_id):
    """更新商品状态，action: reserve, sell, cancel_reserve, off_shelf, relist"""
    data = request.get_json()
    action = data.get('action')
    if not action:
        return jsonify({'code': 400, 'msg': '缺少 action'}), 400

    # 状态迁移规则
    transitions = {
        'reserve': {'from': 'ON_SALE', 'to': 'RESERVED', 'role': 'buyer'},   # 买家预订
        'sell': {'from': 'RESERVED', 'to': 'SOLD', 'role': 'seller'},       # 卖家确认售出
        'cancel_reserve': {'from': 'RESERVED', 'to': 'ON_SALE', 'role': 'seller'}, # 卖家取消预订
        'off_shelf': {'from': 'ON_SALE', 'to': 'OFF_SHELF', 'role': 'seller'},
        'relist': {'from': 'OFF_SHELF', 'to': 'ON_SALE', 'role': 'seller'}
    }
    if action not in transitions:
        return jsonify({'code': 400, 'msg': '无效操作'}), 400

    rule = transitions[action]
    conn = models.get_db()
    item = conn.execute('SELECT * FROM items WHERE id = ?', (item_id,)).fetchone()
    if not item:
        conn.close()
        return jsonify({'code': 404, 'msg': '商品不存在'}), 404

    # 权限检查
    if rule['role'] == 'seller' and item['seller_id'] != session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': '只有卖家可以执行此操作'}), 403
    if rule['role'] == 'buyer' and item['seller_id'] == session['user_id']:
        conn.close()
        return jsonify({'code': 403, 'msg': '不能预订自己的商品'}), 403

    # 状态前置条件检查
    if item['status'] != rule['from']:
        conn.close()
        return jsonify({'code': 400, 'msg': f'当前状态为 {item["status"]}，不能执行此操作'}), 400

    conn.execute('UPDATE items SET status=?, updated_at=? WHERE id=?',
                 (rule['to'], datetime.now(), item_id))
    conn.commit()
    conn.close()
    return jsonify({'code': 200, 'msg': '状态更新成功'})

# ------------------ 个人中心数据 ------------------
@app.route('/api/user/items', methods=['GET'])
@login_required
def get_my_items():
    """我发布的商品（所有状态）"""
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
    """我卖出的商品（status = SOLD）"""
    conn = models.get_db()
    rows = conn.execute('''
        SELECT i.*, (SELECT file_path FROM images WHERE item_id = i.id LIMIT 1) AS cover_image
        FROM items i WHERE i.seller_id = ? AND i.status = 'SOLD' ORDER BY i.updated_at DESC
    ''', (session['user_id'],)).fetchall()
    conn.close()
    return jsonify({'code': 200, 'data': [dict(r) for r in rows]})

# ------------------ 启动 ------------------
if __name__ == '__main__':
    models.init_db()
    app.run(debug=True, port=5000)