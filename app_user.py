import sqlite3
import os
import json
import hashlib
import secrets
from flask import Flask, jsonify, render_template, request, redirect, url_for, session
import joblib
import pandas as pd
import ai_model

base_dir = os.path.dirname(os.path.abspath(__file__))
template_dir = os.path.join(base_dir, 'templates')
static_dir = os.path.join(base_dir, 'static')

# Fallback just in case GitHub drag-and-drop flattened the folders
if not os.path.isdir(template_dir):
    template_dir = base_dir
if not os.path.isdir(static_dir):
    static_dir = base_dir

app = Flask(__name__, template_folder=template_dir, static_folder=static_dir)
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

# ─── GLOBAL SECURITY LOCK ──────────────────────────────────────────────────────
def load_settings():
    try:
        with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'settings.json'), 'r') as f:
            return json.load(f)
    except:
        return {"high_security_lock": True, "terms_of_service_text": "Error loading terms."}

@app.before_request
def require_login():
    settings = load_settings()
    if not settings.get('high_security_lock', True):
        return # Skip lock if it's disabled
        
    allowed_endpoints = ['login', 'signup', 'static']
    if request.endpoint not in allowed_endpoints and 'user_id' not in session:
        return redirect(url_for('login', error='auth_required'))

# ─── AUTH ROUTES ──────────────────────────────────────────────────────────────

@app.route('/')
def index():
    return render_template('index.html', username=session.get('username'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.args.get('error') == 'auth_required':
        error = "Access Denied: High Security Lock Active. You must log in."
        
    if request.method == 'POST':
        identifier = request.form.get('identifier', '').strip()
        password   = request.form.get('password', '').strip()
        if not identifier or not password:
            return render_template('login.html', error="Please fill in all fields.")
        conn = get_db_connection()
        user = conn.execute(
            "SELECT * FROM users WHERE username=? OR email=?",
            (identifier, identifier)
        ).fetchone()
        conn.close()
        if user and user['password_hash'] == hash_password(password):
            session['user_id']   = user['id']
            session['username']  = user['username']
            session['full_name'] = user['full_name']
            
            # Merge session cart to DB
            cart = session.get('cart', {})
            if cart:
                conn = get_db_connection()
                for boot_id_str, qty in cart.items():
                    boot_id = int(boot_id_str)
                    existing = conn.execute("SELECT quantity FROM user_carts WHERE user_id=? AND boot_id=?", (user['id'], boot_id)).fetchone()
                    if existing:
                        conn.execute("UPDATE user_carts SET quantity=? WHERE user_id=? AND boot_id=?", (existing['quantity'] + qty, user['id'], boot_id))
                    else:
                        conn.execute("INSERT INTO user_carts (user_id, boot_id, quantity) VALUES (?, ?, ?)", (user['id'], boot_id, qty))
                conn.commit()
                conn.close()
                session.pop('cart', None)
                
            return redirect(url_for('index'))
        return render_template('login.html', error="Invalid credentials. Please try again.")
    return render_template('login.html', error=error)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        username  = request.form.get('username', '').strip()
        email     = request.form.get('email', '').strip()
        password  = request.form.get('password', '').strip()
        confirm   = request.form.get('confirm_password', '').strip()
        position  = request.form.get('favorite_position', '').strip()
        if not all([full_name, username, email, password, confirm]):
            return render_template('signup.html', error="All fields are required.")
        if password != confirm:
            return render_template('signup.html', error="Passwords do not match.")
        if len(password) < 6:
            return render_template('signup.html', error="Password must be at least 6 characters.")
        conn = get_db_connection()
        try:
            conn.execute(
                "INSERT INTO users (username, email, password_hash, full_name, favorite_position) VALUES (?,?,?,?,?)",
                (username, email, hash_password(password), full_name, position)
            )
            conn.commit()
            conn.close()
            return redirect(url_for('login', success="Account created! Please log in."))
        except sqlite3.IntegrityError:
            conn.close()
            return render_template('signup.html', error="Username or email already exists.")
    return render_template('signup.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('login'))

# ─── JERSEYS, NEWS, PROFILE & CART ROUTES ──────────────────────────────────────────────

@app.route('/jerseys')
def jerseys():
    conn = get_db_connection()
    retro_jerseys = conn.execute("SELECT * FROM jerseys WHERE era = 'Retro'").fetchall()
    modern_jerseys = conn.execute("SELECT * FROM jerseys WHERE era = 'Modern'").fetchall()
    conn.close()
    return render_template('jerseys.html', retro=retro_jerseys, modern=modern_jerseys)

@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' in session:
        conn = get_db_connection()
        db_cart = conn.execute("SELECT boot_id, quantity FROM user_carts WHERE user_id = ?", (session['user_id'],)).fetchall()
        cart = {str(item['boot_id']): item['quantity'] for item in db_cart}
        conn.close()
    else:
        cart = session.get('cart', {})
        
    if not cart:
        return redirect(url_for('cart'))
        
    if request.method == 'POST':
        # Process Mock Billing
        total_price = 0
        conn = get_db_connection()
        for boot_id, quantity in cart.items():
            boot = conn.execute("SELECT price FROM boots WHERE id = ?", (boot_id,)).fetchone()
            if boot:
                total_price += boot['price'] * quantity
        
        user_id = session.get('user_id', None)
        
        # Fraud Detection Heuristics
        risk_score = 0
        fraud_reasons = []
        
        if total_price > 500:
            risk_score += 30
            fraud_reasons.append("High value transaction (>$500)")
        if total_price > 1000:
            risk_score += 50
            fraud_reasons.append("Extremely high value transaction (>$1000)")
            
        if user_id is None:
            risk_score += 20
            fraud_reasons.append("Guest checkout")
            
        is_flagged = 1 if risk_score >= 70 else 0
        fraud_reason_str = " | ".join(fraud_reasons) if fraud_reasons else None
        
        cursor = conn.execute(
            "INSERT INTO orders (user_id, total_price, risk_score, fraud_reason, is_flagged) VALUES (?, ?, ?, ?, ?)", 
            (user_id, total_price, risk_score, fraud_reason_str, is_flagged)
        )
        order_id = cursor.lastrowid
        
        for boot_id, quantity in cart.items():
            boot = conn.execute("SELECT price FROM boots WHERE id = ?", (boot_id,)).fetchone()
            if boot:
                conn.execute("INSERT INTO order_items (order_id, boot_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)", 
                             (order_id, boot_id, quantity, boot['price']))
                             
        if 'user_id' in session:
            conn.execute("DELETE FROM user_carts WHERE user_id = ?", (session['user_id'],))
            
        conn.commit()
        conn.close()
        
        session.pop('cart', None)
        return render_template('checkout.html', success=True)
        
    return render_template('checkout.html', success=False)

@app.route('/api/feedback', methods=['POST'])
def feedback():
    message = request.json.get('message')
    if message:
        user_id = session.get('user_id', None)
        conn = get_db_connection()
        conn.execute("INSERT INTO feedback (user_id, message) VALUES (?, ?)", (user_id, message))
        conn.commit()
        conn.close()
    return jsonify({'success': True})

@app.route('/news')
def news():
    return render_template('news.html')

@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    conn = get_db_connection()
    message = None
    if request.method == 'POST':
        full_name = request.form.get('full_name')
        email = request.form.get('email')
        position = request.form.get('favorite_position')
        
        conn.execute("UPDATE users SET full_name=?, email=?, favorite_position=? WHERE id=?", (full_name, email, position, session['user_id']))
        conn.commit()
        
        session['full_name'] = full_name
        message = "Profile updated successfully!"
        
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    
    # Fetch Order History
    orders_raw = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY timestamp DESC", (session['user_id'],)).fetchall()
    orders = []
    for o in orders_raw:
        items = conn.execute('''
            SELECT oi.*, b.name as boot_name, b.image_url 
            FROM order_items oi 
            JOIN boots b ON oi.boot_id = b.id 
            WHERE oi.order_id = ?
        ''', (o['id'],)).fetchall()
        order_dict = dict(o)
        order_dict['items'] = [dict(i) for i in items]
        orders.append(order_dict)
        
    # Fetch Wishlist (user_carts)
    wishlist = conn.execute('''
        SELECT uc.quantity, b.* 
        FROM user_carts uc 
        JOIN boots b ON uc.boot_id = b.id 
        WHERE uc.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    conn.close()
    
    return render_template('profile.html', user=user, message=message, orders=orders, wishlist=wishlist)



@app.route('/customizer')
def customizer():
    return render_template('customizer.html')

@app.route('/api/cart/add_custom', methods=['POST'])
def add_custom_to_cart():
    custom_data = request.json
    if not custom_data:
        return jsonify({'error': 'No data provided'}), 400
        
    if 'user_id' in session:
        conn = get_db_connection()
        conn.execute("INSERT INTO user_carts (user_id, quantity, custom_data) VALUES (?, ?, ?)", (session['user_id'], 1, json.dumps(custom_data)))
        conn.commit()
        total_items = conn.execute("SELECT SUM(quantity) as total FROM user_carts WHERE user_id=?", (session['user_id'],)).fetchone()['total'] or 0
        conn.close()
        return jsonify({'success': True, 'cart_count': total_items})
    else:
        cart = session.get('cart', {})
        # Simple hack for anonymous custom cart items
        import uuid
        key = f"custom_{uuid.uuid4().hex[:8]}"
        cart[key] = {'quantity': 1, 'data': custom_data}
        session['cart'] = cart
        return jsonify({'success': True, 'cart_count': len(cart)})

@app.route('/cart')
def cart():
    conn = get_db_connection()
    cart_items = []
    total_price = 0
    
    if 'user_id' in session:
        boots = conn.execute("SELECT uc.quantity, b.*, 'boot' as type FROM user_carts uc JOIN boots b ON uc.boot_id = b.id WHERE uc.user_id = ?", (session['user_id'],)).fetchall()
        jerseys = conn.execute("SELECT uc.quantity, j.*, 'jersey' as type FROM user_carts uc JOIN jerseys j ON uc.jersey_id = j.id WHERE uc.user_id = ?", (session['user_id'],)).fetchall()
        customs = conn.execute("SELECT uc.quantity, uc.custom_data, 'custom' as type FROM user_carts uc WHERE uc.custom_data IS NOT NULL AND uc.user_id = ?", (session['user_id'],)).fetchall()
        
        items = [dict(i) for i in boots] + [dict(i) for i in jerseys]
        for c in customs:
            data = json.loads(c['custom_data'])
            items.append({
                'name': f"PRO Custom Boot ({data.get('text', '')})",
                'type': 'custom',
                'price': data.get('price', 250.0),
                'quantity': c['quantity'],
                'image_url': 'https://i.ibb.co/3s6S3fB/custom-placeholder.png', # Placeholder or SVG string
                'custom_details': data
            })
            
        for item in items:
            item['subtotal'] = item['price'] * item['quantity']
            total_price += item['subtotal']
            cart_items.append(item)
    else:
        cart = session.get('cart', {})
        for key, quantity_or_dict in cart.items():
            if key.startswith('boot_'):
                boot_id = key.split('_')[1]
                boot = conn.execute("SELECT *, 'boot' as type FROM boots WHERE id = ?", (boot_id,)).fetchone()
                if boot:
                    item = dict(boot)
                    item['quantity'] = quantity_or_dict
                    item['subtotal'] = item['price'] * quantity_or_dict
                    total_price += item['subtotal']
                    cart_items.append(item)
            elif key.startswith('jersey_'):
                jersey_id = key.split('_')[1]
                jersey = conn.execute("SELECT *, 'jersey' as type FROM jerseys WHERE id = ?", (jersey_id,)).fetchone()
                if jersey:
                    item = dict(jersey)
                    item['quantity'] = quantity_or_dict
                    item['subtotal'] = item['price'] * quantity_or_dict
                    total_price += item['subtotal']
                    cart_items.append(item)
            elif key.startswith('custom_'):
                data = quantity_or_dict['data']
                q = quantity_or_dict['quantity']
                item = {
                    'name': f"PRO Custom Boot ({data.get('text', '')})",
                    'type': 'custom',
                    'price': data.get('price', 250.0),
                    'quantity': q,
                    'image_url': 'https://i.ibb.co/3s6S3fB/custom-placeholder.png',
                    'subtotal': data.get('price', 250.0) * q,
                    'custom_details': data
                }
                total_price += item['subtotal']
                cart_items.append(item)
            
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)



@app.route('/ar-tryon')
def ar_tryon():
    return render_template('ar_tryon.html')

@app.route('/api/cart/add', methods=['POST'])
def add_to_cart():
    boot_id = request.json.get('boot_id')
    jersey_id = request.json.get('jersey_id')
    
    if not boot_id and not jersey_id:
        return jsonify({'error': 'No boot_id or jersey_id provided'}), 400
        
    if 'user_id' in session:
        conn = get_db_connection()
        if boot_id:
            existing = conn.execute("SELECT quantity FROM user_carts WHERE user_id=? AND boot_id=?", (session['user_id'], boot_id)).fetchone()
            if existing:
                conn.execute("UPDATE user_carts SET quantity=? WHERE user_id=? AND boot_id=?", (existing['quantity'] + 1, session['user_id'], boot_id))
            else:
                conn.execute("INSERT INTO user_carts (user_id, boot_id, quantity) VALUES (?, ?, 1)", (session['user_id'], boot_id))
        elif jersey_id:
            existing = conn.execute("SELECT quantity FROM user_carts WHERE user_id=? AND jersey_id=?", (session['user_id'], jersey_id)).fetchone()
            if existing:
                conn.execute("UPDATE user_carts SET quantity=? WHERE user_id=? AND jersey_id=?", (existing['quantity'] + 1, session['user_id'], jersey_id))
            else:
                conn.execute("INSERT INTO user_carts (user_id, jersey_id, quantity) VALUES (?, ?, 1)", (session['user_id'], jersey_id))
        
        conn.commit()
        total_items = conn.execute("SELECT SUM(quantity) as total FROM user_carts WHERE user_id=?", (session['user_id'],)).fetchone()['total'] or 0
        conn.close()
        return jsonify({'success': True, 'cart_count': total_items})
    else:
        cart = session.get('cart', {})
        if boot_id:
            key = f"boot_{boot_id}"
        elif jersey_id:
            key = f"jersey_{jersey_id}"
        cart[key] = cart.get(key, 0) + 1
        session['cart'] = cart
        return jsonify({'success': True, 'cart_count': sum(cart.values())})
@app.route('/api/cart/remove', methods=['POST'])
def remove_from_cart():
    boot_id = request.json.get('boot_id')
    jersey_id = request.json.get('jersey_id')
    
    if 'user_id' in session:
        conn = get_db_connection()
        if boot_id:
            conn.execute("DELETE FROM user_carts WHERE user_id=? AND boot_id=?", (session['user_id'], boot_id))
        elif jersey_id:
            conn.execute("DELETE FROM user_carts WHERE user_id=? AND jersey_id=?", (session['user_id'], jersey_id))
        conn.commit()
        conn.close()
    else:
        cart = session.get('cart', {})
        if boot_id:
            key = f"boot_{boot_id}"
        elif jersey_id:
            key = f"jersey_{jersey_id}"
            
        if key in cart:
            del cart[key]
            session['cart'] = cart
            
    return jsonify({'success': True})

# ─── ML & DETAIL ROUTES ───────────────────────────────────────────────────────

@app.route('/boot/<int:boot_id>')
def boot_detail(boot_id):
    conn = get_db_connection()
    boot = conn.execute("SELECT * FROM boots WHERE id = ?", (boot_id,)).fetchone()
    conn.close()
    if boot is None:
        return "Boot not found", 404
    return render_template('boot_detail.html', boot=boot_row_to_dict(boot))
@app.route('/position-guide')
def position_guide():
    conn = get_db_connection()
    positions = ['Goalkeeper', 'Defender', 'Midfielder', 'Attacker']
    boots_by_position = {}
    
    for pos in positions:
        query = '''
            SELECT * FROM boots 
            WHERE position = ? 
            ORDER BY rating DESC LIMIT 3
        '''
        cursor = conn.execute(query, (pos,))
        boots_by_position[pos] = [boot_row_to_dict(row) for row in cursor.fetchall()]
        
    conn.close()
    return render_template('position_guide.html', boots_by_position=boots_by_position)

@app.route('/recommend', methods=['GET', 'POST'])
def recommend():
    if request.method == 'POST':
        # Get data from form
        gender = request.form.get('gender')
        position = request.form.get('position')
        weight_kg = float(request.form.get('weight_kg', 75.0))
        foot_width = request.form.get('foot_width')
        play_style = request.form.get('play_style')
        
        # Format for pandas and model prediction
        input_data = pd.DataFrame([{
            'gender': gender,
            'position': position,
            'weight_kg': weight_kg,
            'foot_width': foot_width,
            'play_style': play_style
        }])
        
        # Load model and predict
        model_path = os.path.join(os.path.dirname(__file__), 'ml_model', 'boot_recommender.pkl')
        try:
            model = joblib.load(model_path)
            prediction = model.predict(input_data)[0]
        except Exception as e:
            prediction = "Error loading model. Make sure to train it first!"
            
        # Fetch actual boot choices from the database based on prediction
        recommended_boots = []
        if "Error" not in prediction:
            db = get_db_connection()
            # Match the predicted category to the priority column, order by rating
            query = '''
                SELECT * FROM boots 
                WHERE priority = ? AND gender = ?
                ORDER BY rating DESC LIMIT 3
            '''
            cursor = db.execute(query, (prediction, gender))
            recommended_boots = [boot_row_to_dict(row) for row in cursor.fetchall()]
            
            # If no gender match, fallback to just priority
            if not recommended_boots:
                query = 'SELECT * FROM boots WHERE priority = ? ORDER BY rating DESC LIMIT 3'
                cursor = db.execute(query, (prediction,))
                recommended_boots = [boot_row_to_dict(row) for row in cursor.fetchall()]

        return render_template('recommend.html', prediction=prediction, boots=recommended_boots)
        
    return render_template('recommend.html')

# ─── API ROUTES ───────────────────────────────────────────────────────────────

def boot_row_to_dict(r):
    return {
        'id'           : r['id'],
        'name'         : r['name'],
        'brand'        : r['brand'],
        'gender'       : r['gender'],
        'position'     : r['position'],
        'price'        : r['price'],
        'rating'       : r['rating'],
        'description'  : r['description'],
        'key_features' : [f.strip() for f in r['key_features'].split(';') if f.strip()],
        'image_url'    : r['image_url'],
        'colorway'     : r['colorway'],
        'legends'      : [p.strip() for p in r['legends'].split(';') if p.strip()],
        'priority'     : r['priority'],
        'stud_type'    : r['stud_type'],
        'surface'      : r['surface'],
        'boot_category': r['boot_category'],
        'era'          : r['era'] if 'era' in r.keys() else 'Modern',
    }

@app.route('/api/boots')
def get_boots():
    gender        = request.args.get('gender')
    position      = request.args.get('position')
    brands        = request.args.get('brands')
    search        = request.args.get('search')
    max_price     = request.args.get('max_price')
    priority      = request.args.get('priority')
    stud_types    = request.args.get('stud_types')
    boot_category = request.args.get('boot_category')
    era           = request.args.get('era')

    query  = "SELECT * FROM boots WHERE 1=1"
    params = []

    if gender:
        query += " AND gender = ?";   params.append(gender)
    if position:
        query += " AND position = ?"; params.append(position)
    if brands:
        bl = [b.strip() for b in brands.split(',') if b.strip()]
        if bl:
            query += f" AND brand IN ({','.join(['?']*len(bl))})"; params.extend(bl)
    if search:
        query += " AND (name LIKE ? OR description LIKE ? OR key_features LIKE ? OR legends LIKE ? OR stud_type LIKE ? OR surface LIKE ? OR era LIKE ?)"
        sp = f"%{search}%"
        params.extend([sp, sp, sp, sp, sp, sp, sp])
    if max_price:
        try:
            query += " AND price <= ?"; params.append(float(max_price))
        except ValueError:
            pass
    if priority:
        query += " AND priority = ?"; params.append(priority)
    if stud_types:
        sl = [s.strip() for s in stud_types.split(',') if s.strip()]
        if sl:
            query += f" AND stud_type IN ({','.join(['?']*len(sl))})"; params.extend(sl)
    if boot_category:
        query += " AND boot_category = ?"; params.append(boot_category)
    if era:
        query += " AND era = ?"; params.append(era)

    conn = get_db_connection()
    rows = conn.execute(query, params).fetchall()
    conn.close()
    return jsonify([boot_row_to_dict(r) for r in rows])

@app.route('/api/boots/<int:boot_id>')
def get_boot_detail(boot_id):
    conn = get_db_connection()
    row  = conn.execute("SELECT * FROM boots WHERE id=?", (boot_id,)).fetchone()
    conn.close()
    if row is None:
        return jsonify({'error': 'Boot not found'}), 404
    return jsonify(boot_row_to_dict(row))

@app.route('/api/stud_types')
def get_stud_types():
    conn  = get_db_connection()
    rows  = conn.execute("SELECT DISTINCT stud_type FROM boots ORDER BY stud_type").fetchall()
    conn.close()
    return jsonify([r['stud_type'] for r in rows])

@app.route('/api/me')
def get_me():
    if 'user_id' not in session:
        return jsonify({'error': 'Not logged in'}), 401
    return jsonify({'username': session['username'], 'full_name': session.get('full_name', '')})

@app.route('/terms')
def terms():
    user = None
    if 'user_id' in session:
        conn = get_db_connection()
        user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
        conn.close()
    
    settings = load_settings()
    terms_text = settings.get('terms_of_service_text', 'No terms provided.')
    return render_template('terms.html', user=user, terms_text=terms_text)

@app.route('/ai-sizing')
def ai_sizing():
    return render_template('ai_scanner.html')

@app.route('/api/analyze-foot', methods=['POST'])
def analyze_foot():
    data = request.json
    if not data or 'image' not in data:
        return jsonify({'success': False, 'error': 'No image provided'})

    # Mock extraction from image
    import random
    mock_len = random.uniform(25.0, 29.5)
    mock_wid = mock_len * random.uniform(0.35, 0.42)
    
    result = ai_model.predict_foot_size(mock_len, mock_wid)
    
    # Save to database
    user_id = session.get('user_id', None)
    conn = get_db_connection()
    conn.execute('INSERT INTO ai_scans (user_id, predicted_size, foot_shape, accuracy) VALUES (?, ?, ?, ?)',
                 (user_id, result['predicted_size'], result['foot_shape'], result['accuracy']))
    conn.commit()
    conn.close()

    result['success'] = True
    return jsonify(result)

# ─── STARTUP ──────────────────────────────────────────────────────────────────
# Initialize database tables for production (Render) environments
try:
    init_users_table()
except Exception as e:
    print("Warning: Database initialization failed:", e)

if __name__ == '__main__':
    app.run(debug=True, port=5000)
