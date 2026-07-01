import re
import os

filepath = r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_user.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

# Make sure json is imported
if 'import json' not in content:
    content = content.replace('import sqlite3', 'import sqlite3\nimport json')

# Add /customizer and /api/cart/add_custom
new_routes = """
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
"""

# Insert before /cart
content = content.replace("@app.route('/cart')", new_routes + "\n@app.route('/cart')")

# Update /cart
cart_logic = """@app.route('/cart')
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
"""
content = re.sub(r"@app\.route\('/cart'\).*?return render_template\('cart\.html', cart_items=cart_items, total_price=total_price\)", cart_logic, content, flags=re.DOTALL)


# Update /checkout
checkout_logic = """@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' in session:
        conn = get_db_connection()
        db_cart = conn.execute("SELECT boot_id, jersey_id, custom_data, quantity FROM user_carts WHERE user_id = ?", (session['user_id'],)).fetchall()
        cart = {}
        for item in db_cart:
            if item['boot_id']:
                cart[f"boot_{item['boot_id']}"] = item['quantity']
            elif item['jersey_id']:
                cart[f"jersey_{item['jersey_id']}"] = item['quantity']
            elif item['custom_data']:
                import uuid
                key = f"custom_{uuid.uuid4().hex[:8]}"
                cart[key] = {'quantity': item['quantity'], 'data': json.loads(item['custom_data'])}
        conn.close()
    else:
        cart = session.get('cart', {})
        
    if not cart:
        return redirect(url_for('cart'))
        
    if request.method == 'POST':
        # Process Mock Billing
        total_price = 0
        conn = get_db_connection()
        for key, val in cart.items():
            if key.startswith('boot_'):
                boot_id = key.split('_')[1]
                boot = conn.execute("SELECT price FROM boots WHERE id = ?", (boot_id,)).fetchone()
                if boot:
                    total_price += boot['price'] * val
            elif key.startswith('jersey_'):
                jersey_id = key.split('_')[1]
                jersey = conn.execute("SELECT price FROM jerseys WHERE id = ?", (jersey_id,)).fetchone()
                if jersey:
                    total_price += jersey['price'] * val
            elif key.startswith('custom_'):
                total_price += val['data'].get('price', 250.0) * val['quantity']
        
        user_id = session.get('user_id', None)
        
        # Fraud Detection Heuristics
        risk_score = 0
        fraud_reasons = []
        if total_price > 500:
            risk_score += 30
            fraud_reasons.append("High value transaction (>$500)")
        if total_price > 1000:
            risk_score += 50
            fraud_reasons.append("Exceptionally high value (>$1000)")
            
        status = 'Placed'
        is_flagged = 1 if risk_score >= 50 else 0
        if is_flagged:
            status = 'Under Review'
            
        fraud_reason_str = ", ".join(fraud_reasons) if fraud_reasons else None
        
        # Create Order
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO orders (user_id, total_price, status, risk_score, fraud_reason, is_flagged)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, total_price, status, risk_score, fraud_reason_str, is_flagged))
        order_id = cursor.lastrowid
        
        # Create Order Items
        for key, val in cart.items():
            if key.startswith('boot_'):
                boot_id = key.split('_')[1]
                boot = conn.execute("SELECT price FROM boots WHERE id = ?", (boot_id,)).fetchone()
                if boot:
                    cursor.execute("INSERT INTO order_items (order_id, boot_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                                   (order_id, boot_id, val, boot['price']))
            elif key.startswith('jersey_'):
                jersey_id = key.split('_')[1]
                jersey = conn.execute("SELECT price FROM jerseys WHERE id = ?", (jersey_id,)).fetchone()
                if jersey:
                    cursor.execute("INSERT INTO order_items (order_id, jersey_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                                   (order_id, jersey_id, val, jersey['price']))
            elif key.startswith('custom_'):
                price = val['data'].get('price', 250.0)
                cursor.execute("INSERT INTO order_items (order_id, custom_data, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                               (order_id, json.dumps(val['data']), val['quantity'], price))
        
        # Clear Cart
        if user_id:
            cursor.execute("DELETE FROM user_carts WHERE user_id = ?", (user_id,))
        else:
            session.pop('cart', None)
            
        conn.commit()
        conn.close()
        return redirect(url_for('profile', success="Order Placed Successfully!"))
        
    return render_template('checkout.html')"""
content = re.sub(r"@app\.route\('/checkout', methods=\['GET', 'POST'\]\).*?return render_template\('checkout\.html'\)", checkout_logic, content, flags=re.DOTALL)


# Update profile
profile_logic = """@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
        
    conn = get_db_connection()
    user = conn.execute("SELECT * FROM users WHERE id = ?", (session['user_id'],)).fetchone()
    message = request.args.get('success')
    
    # Fetch Orders
    orders_raw = conn.execute("SELECT * FROM orders WHERE user_id = ? ORDER BY timestamp DESC", (session['user_id'],)).fetchall()
    orders = []
    for o in orders_raw:
        boot_items = conn.execute('''
            SELECT oi.*, b.name as item_name, b.image_url, 'boot' as type 
            FROM order_items oi 
            JOIN boots b ON oi.boot_id = b.id 
            WHERE oi.order_id = ?
        ''', (o['id'],)).fetchall()
        
        jersey_items = conn.execute('''
            SELECT oi.*, j.name as item_name, j.image_url, 'jersey' as type 
            FROM order_items oi 
            JOIN jerseys j ON oi.jersey_id = j.id 
            WHERE oi.order_id = ?
        ''', (o['id'],)).fetchall()
        
        custom_items = conn.execute("SELECT oi.*, 'custom' as type FROM order_items oi WHERE oi.custom_data IS NOT NULL AND oi.order_id = ?", (o['id'],)).fetchall()
        
        custom_dicts = []
        for c in custom_items:
            cd = dict(c)
            data = json.loads(cd['custom_data'])
            cd['item_name'] = f"PRO Custom Boot ({data.get('text', '')})"
            cd['image_url'] = 'https://i.ibb.co/3s6S3fB/custom-placeholder.png'
            custom_dicts.append(cd)
            
        order_dict = dict(o)
        order_dict['items'] = [dict(i) for i in boot_items] + [dict(i) for i in jersey_items] + custom_dicts
        orders.append(order_dict)
        
    # Fetch Wishlist (user_carts)
    wishlist_boots = conn.execute('''
        SELECT uc.quantity, b.*, 'boot' as type 
        FROM user_carts uc 
        JOIN boots b ON uc.boot_id = b.id 
        WHERE uc.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    wishlist_jerseys = conn.execute('''
        SELECT uc.quantity, j.*, 'jersey' as type 
        FROM user_carts uc 
        JOIN jerseys j ON uc.jersey_id = j.id 
        WHERE uc.user_id = ?
    ''', (session['user_id'],)).fetchall()
    
    wishlist = [dict(w) for w in wishlist_boots] + [dict(w) for w in wishlist_jerseys]
    
    conn.close()
    
    return render_template('profile.html', user=user, message=message, orders=orders, wishlist=wishlist)"""

content = re.sub(r"@app\.route\('/profile'\).*?return render_template\('profile\.html', user=user, message=message, orders=orders, wishlist=wishlist\)", profile_logic, content, flags=re.DOTALL)


with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app_user.py with customizer routes!")
