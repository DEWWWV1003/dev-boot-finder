import sqlite3
import os
import json
import hashlib
import secrets
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import joblib
import pandas as pd
app = Flask(__name__)
app.secret_key = secrets.token_hex(32)

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def init_users_table():
    conn = get_db_connection()
    conn.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            favorite_position TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# ─── ADMIN ROUTES ─────────────────────────────────────────────────────────────

from werkzeug.security import check_password_hash

@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        
        conn = get_db_connection()
        admin = conn.execute("SELECT * FROM admins WHERE username=?", (username,)).fetchone()
        conn.close()
        
        if admin and check_password_hash(admin['password_hash'], password):
            session['admin_id'] = admin['id']
            session['admin_username'] = admin['username']
            return redirect(url_for('admin_dashboard'))
        
        return render_template('admin_login.html', error="Invalid admin credentials.")
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_id', None)
    session.pop('admin_username', None)
    return redirect(url_for('admin_login'))

@app.route('/admin/dashboard')
def admin_dashboard():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    # Fetch top 4 rated boots
    top_boots = conn.execute("SELECT * FROM boots ORDER BY rating DESC LIMIT 4").fetchall()
    # Fetch latest 3 feedbacks
    feedbacks = conn.execute("SELECT * FROM feedback ORDER BY timestamp DESC LIMIT 3").fetchall()
    conn.close()
    
    return render_template('admin.html', top_boots=top_boots, feedbacks=feedbacks)

@app.route('/admin/profile', methods=['GET', 'POST'])
def admin_profile():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    conn = get_db_connection()
    message = None
    if request.method == 'POST':
        new_username = request.form.get('username')
        new_password = request.form.get('password')
        if new_username and new_password:
            import werkzeug.security
            hashed_pw = werkzeug.security.generate_password_hash(new_password)
            conn.execute("UPDATE admins SET username=?, password_hash=? WHERE id=?", (new_username, hashed_pw, session['admin_id']))
            conn.commit()
            session['admin_username'] = new_username
            message = "Profile updated successfully!"
            
    admin = conn.execute("SELECT * FROM admins WHERE id=?", (session['admin_id'],)).fetchone()
    conn.close()
    return render_template('admin_profile.html', admin=admin, message=message)

@app.route('/admin/users')
def admin_users():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    users = conn.execute("SELECT id, username, email, full_name, favorite_position, created_at FROM users ORDER BY created_at DESC").fetchall()
    
    total_users = len(users)
    
    conn.close()
    return render_template('admin_users.html', users=users, total_users=total_users)

@app.route('/admin/compare')
def admin_compare():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    boots = conn.execute("SELECT * FROM boots ORDER BY name").fetchall()
    
    boot1_id = request.args.get('boot1')
    boot2_id = request.args.get('boot2')
    
    b1 = None
    b2 = None
    if boot1_id:
        b1 = conn.execute("SELECT * FROM boots WHERE id=?", (boot1_id,)).fetchone()
    if boot2_id:
        b2 = conn.execute("SELECT * FROM boots WHERE id=?", (boot2_id,)).fetchone()
        
    conn.close()
    return render_template('admin_compare.html', boots=boots, b1=b1, b2=b2)

@app.route('/admin/banking')
def admin_banking():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    orders = conn.execute('''
        SELECT o.*, u.username, u.email 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id 
        ORDER BY o.timestamp DESC
    ''').fetchall()
    
    orders_with_items = []
    total_revenue = 0
    total_pending = 0
    
    for o in orders:
        boot_items = conn.execute('''
            SELECT oi.*, b.name as item_name 
            FROM order_items oi 
            JOIN boots b ON oi.boot_id = b.id 
            WHERE oi.order_id = ?
        ''', (o['id'],)).fetchall()
        
        jersey_items = conn.execute('''
            SELECT oi.*, j.name as item_name 
            FROM order_items oi 
            JOIN jerseys j ON oi.jersey_id = j.id 
            WHERE oi.order_id = ?
        ''', (o['id'],)).fetchall()
        
        custom_items = conn.execute("SELECT oi.*, 'custom' as type FROM order_items oi WHERE oi.custom_data IS NOT NULL AND oi.order_id = ?", (o['id'],)).fetchall()
        
        order_dict = dict(o)
        
        items_list = [dict(i) for i in boot_items] + [dict(i) for i in jersey_items]
        
        for c in custom_items:
            cd = dict(c)
            data = json.loads(cd['custom_data'])
            cd['item_name'] = f"PRO Custom Boot ({data.get('text', '')})"
            items_list.append(cd)
            
        # Rename item_name to boot_name for template compatibility
        for item in items_list:
            item['boot_name'] = item['item_name']
            
        order_dict['items'] = items_list
        orders_with_items.append(order_dict)
        
        if o['status'] != 'Refunded' and o['status'] != 'Cancelled':
            total_revenue += o['total_price']
        if o['status'] == 'Placed':
            total_pending += o['total_price']
            
    conn.close()
    
    return render_template('admin_banking.html', 
                           orders=orders_with_items, 
                           total_revenue=total_revenue,
                           total_pending=total_pending,
                           total_orders=len(orders))

@app.route('/admin/banking/update_status', methods=['POST'])
def admin_update_order_status():
    if 'admin_id' not in session:
        return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
    order_id = request.json.get('order_id')
    new_status = request.json.get('status')
    
    if not order_id or not new_status:
        return jsonify({'success': False, 'error': 'Missing parameters'}), 400
        
    conn = get_db_connection()
    conn.execute("UPDATE orders SET status = ? WHERE id = ?", (new_status, order_id))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True})

@app.route('/admin/wishlist')
def admin_wishlist():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
        
    conn = get_db_connection()
    raw_wishlists_boots = conn.execute('''
        SELECT uc.quantity, uc.added_at, u.username, u.email, u.id as user_id,
               b.name as item_name, b.price, b.image_url
        FROM user_carts uc
        JOIN users u ON uc.user_id = u.id
        JOIN boots b ON uc.boot_id = b.id
    ''').fetchall()
    
    raw_wishlists_jerseys = conn.execute('''
        SELECT uc.quantity, uc.added_at, u.username, u.email, u.id as user_id,
               j.name as item_name, j.price, j.image_url
        FROM user_carts uc
        JOIN users u ON uc.user_id = u.id
        JOIN jerseys j ON uc.jersey_id = j.id
    ''').fetchall()
    
    raw_wishlists = [dict(w) for w in raw_wishlists_boots] + [dict(w) for w in raw_wishlists_jerseys]
    # Sort by added_at desc
    raw_wishlists.sort(key=lambda x: x['added_at'], reverse=True)
    
    conn.close()
    
    grouped_wishlists = {}
    for item in raw_wishlists:
        uid = item['user_id']
        if uid not in grouped_wishlists:
            grouped_wishlists[uid] = {
                'username': item['username'],
                'email': item['email'],
                'items': [],
                'total_value': 0
            }
            
        subtotal = item['price'] * item['quantity']
        grouped_wishlists[uid]['items'].append({
            'boot_name': item['item_name'],  # keep boot_name key for template
            'quantity': item['quantity'],
            'price': item['price'],
            'subtotal': subtotal,
            'image_url': item['image_url'],
            'added_at': item['added_at']
        })
        grouped_wishlists[uid]['total_value'] += subtotal
        
    return render_template('admin_wishlist.html', wishlists=grouped_wishlists.values())

@app.route('/api/admin/alerts')
def admin_alerts():
    if 'admin_id' not in session:
        return jsonify({'count': 0})
    conn = get_db_connection()
    count = conn.execute("SELECT COUNT(*) as cnt FROM orders WHERE is_flagged = 1").fetchone()['cnt']
    conn.close()
    return jsonify({'count': count})

@app.route('/admin/ai')
def admin_ai():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    scans = conn.execute('''
        SELECT a.*, u.username, u.email 
        FROM ai_scans a 
        LEFT JOIN users u ON a.user_id = u.id 
        ORDER BY a.scan_date DESC
    ''').fetchall()
    conn.close()
    return render_template('admin_ai.html', scans=scans)

@app.route('/admin/fraud')
def admin_fraud():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    flagged_orders = conn.execute('''
        SELECT o.*, u.username, u.email 
        FROM orders o 
        LEFT JOIN users u ON o.user_id = u.id 
        WHERE o.is_flagged = 1 
        ORDER BY o.timestamp DESC
    ''').fetchall()
    conn.close()
    return render_template('admin_fraud.html', flagged_orders=flagged_orders)

@app.route('/admin/fraud/resolve', methods=['POST'])
def admin_fraud_resolve():
    if 'admin_id' not in session:
        return jsonify({'success': False})
    
    order_id = request.json.get('order_id')
    action = request.json.get('action')
    
    conn = get_db_connection()
    if action == 'mark_safe':
        conn.execute("UPDATE orders SET is_flagged = 0, risk_score = 0, fraud_reason = 'Marked Safe by Admin' WHERE id = ?", (order_id,))
    elif action == 'cancel':
        conn.execute("UPDATE orders SET status = 'Cancelled', is_flagged = 0, fraud_reason = 'Cancelled for Fraud' WHERE id = ?", (order_id,))
    
    conn.commit()
    conn.close()
    return jsonify({'success': True})

@app.route('/admin/inventory')
def admin_inventory():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    conn = get_db_connection()
    boots = conn.execute("SELECT * FROM boots").fetchall()
    conn.close()
    return render_template('admin_inventory.html', boots=boots)

@app.route('/admin/marketing')
def admin_marketing():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_marketing.html')

@app.route('/admin/analytics')
def admin_analytics():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_analytics.html')

@app.route('/admin/support')
def admin_support():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    return render_template('admin_support.html')

def get_settings_path():
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json')

def load_settings():
    try:
        with open(get_settings_path(), 'r') as f:
            return json.load(f)
    except:
        return {"high_security_lock": True, "terms_of_service_text": ""}

def save_settings(data):
    with open(get_settings_path(), 'w') as f:
        json.dump(data, f, indent=2)

@app.route('/admin/settings', methods=['GET', 'POST'])
def admin_settings():
    if 'admin_id' not in session:
        return redirect(url_for('admin_login'))
    
    settings = load_settings()
    
    if request.method == 'POST':
        lock_enabled = request.form.get('high_security_lock') == 'on'
        terms_text = request.form.get('terms_of_service_text', '')
        
        settings['high_security_lock'] = lock_enabled
        settings['terms_of_service_text'] = terms_text
        save_settings(settings)
        
        return render_template('admin_settings.html', settings=settings, success="Settings updated successfully.")
        
    return render_template('admin_settings.html', settings=settings)

# ─── STARTUP ──────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    init_users_table()
    app.run(debug=True, port=5001)
