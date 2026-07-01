import re

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_user.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 4. Update /checkout logic
checkout_logic = """@app.route('/checkout', methods=['GET', 'POST'])
def checkout():
    if 'user_id' in session:
        conn = get_db_connection()
        db_cart = conn.execute("SELECT boot_id, jersey_id, quantity FROM user_carts WHERE user_id = ?", (session['user_id'],)).fetchall()
        cart = {}
        for item in db_cart:
            if item['boot_id']:
                cart[f"boot_{item['boot_id']}"] = item['quantity']
            elif item['jersey_id']:
                cart[f"jersey_{item['jersey_id']}"] = item['quantity']
        conn.close()
    else:
        cart = session.get('cart', {})
        
    if not cart:
        return redirect(url_for('cart'))
        
    if request.method == 'POST':
        # Process Mock Billing
        total_price = 0
        conn = get_db_connection()
        for key, quantity in cart.items():
            if key.startswith('boot_'):
                boot_id = key.split('_')[1]
                boot = conn.execute("SELECT price FROM boots WHERE id = ?", (boot_id,)).fetchone()
                if boot:
                    total_price += boot['price'] * quantity
            elif key.startswith('jersey_'):
                jersey_id = key.split('_')[1]
                jersey = conn.execute("SELECT price FROM jerseys WHERE id = ?", (jersey_id,)).fetchone()
                if jersey:
                    total_price += jersey['price'] * quantity
        
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
        for key, quantity in cart.items():
            if key.startswith('boot_'):
                boot_id = key.split('_')[1]
                boot = conn.execute("SELECT price FROM boots WHERE id = ?", (boot_id,)).fetchone()
                if boot:
                    cursor.execute("INSERT INTO order_items (order_id, boot_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                                   (order_id, boot_id, quantity, boot['price']))
            elif key.startswith('jersey_'):
                jersey_id = key.split('_')[1]
                jersey = conn.execute("SELECT price FROM jerseys WHERE id = ?", (jersey_id,)).fetchone()
                if jersey:
                    cursor.execute("INSERT INTO order_items (order_id, jersey_id, quantity, price_at_purchase) VALUES (?, ?, ?, ?)",
                                   (order_id, jersey_id, quantity, jersey['price']))
        
        # Clear Cart
        if user_id:
            cursor.execute("DELETE FROM user_carts WHERE user_id = ?", (user_id,))
        else:
            session.pop('cart', None)
            
        conn.commit()
        conn.close()
        return redirect(url_for('profile', success="Order Placed Successfully!"))
        
    return render_template('checkout.html')

"""
content = re.sub(r"@app\.route\('/checkout', methods=\['GET', 'POST'\]\).*?return render_template\('checkout\.html'\)\n\n", checkout_logic, content, flags=re.DOTALL)

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_user.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated API checkout route!")
