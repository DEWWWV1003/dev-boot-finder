import re

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_user.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update /api/cart/add
cart_add_logic = """
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
"""
content = re.sub(r"@app\.route\('/api/cart/add', methods=\['POST'\]\).*?(?=@app\.route\('/api/cart/remove)", cart_add_logic, content, flags=re.DOTALL)

# 2. Update /api/cart/remove
cart_remove_logic = """@app.route('/api/cart/remove', methods=['POST'])
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

"""
content = re.sub(r"@app\.route\('/api/cart/remove', methods=\['POST'\]\).*?(?=# ─── ML & DETAIL ROUTES)", cart_remove_logic, content, flags=re.DOTALL)

# 3. Update /cart logic
cart_logic = """@app.route('/cart')
def cart():
    conn = get_db_connection()
    cart_items = []
    total_price = 0
    
    if 'user_id' in session:
        boots = conn.execute("SELECT uc.quantity, b.*, 'boot' as type FROM user_carts uc JOIN boots b ON uc.boot_id = b.id WHERE uc.user_id = ?", (session['user_id'],)).fetchall()
        jerseys = conn.execute("SELECT uc.quantity, j.*, 'jersey' as type FROM user_carts uc JOIN jerseys j ON uc.jersey_id = j.id WHERE uc.user_id = ?", (session['user_id'],)).fetchall()
        
        items = [dict(i) for i in boots] + [dict(i) for i in jerseys]
        
        for item in items:
            item['subtotal'] = item['price'] * item['quantity']
            total_price += item['subtotal']
            cart_items.append(item)
    else:
        cart = session.get('cart', {})
        for key, quantity in cart.items():
            if key.startswith('boot_'):
                boot_id = key.split('_')[1]
                boot = conn.execute("SELECT *, 'boot' as type FROM boots WHERE id = ?", (boot_id,)).fetchone()
                if boot:
                    item = dict(boot)
                    item['quantity'] = quantity
                    item['subtotal'] = item['price'] * quantity
                    total_price += item['subtotal']
                    cart_items.append(item)
            elif key.startswith('jersey_'):
                jersey_id = key.split('_')[1]
                jersey = conn.execute("SELECT *, 'jersey' as type FROM jerseys WHERE id = ?", (jersey_id,)).fetchone()
                if jersey:
                    item = dict(jersey)
                    item['quantity'] = quantity
                    item['subtotal'] = item['price'] * quantity
                    total_price += item['subtotal']
                    cart_items.append(item)
            
    conn.close()
    return render_template('cart.html', cart_items=cart_items, total_price=total_price)

"""
content = re.sub(r"@app\.route\('/cart'\)\n.*?return render_template\('cart.html'.*?\n\n", cart_logic, content, flags=re.DOTALL)


# Write back
with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_user.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated API cart routes!")
