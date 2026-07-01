import re

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_user.py', 'r', encoding='utf-8') as f:
    content = f.read()

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
        
        order_dict = dict(o)
        order_dict['items'] = [dict(i) for i in boot_items] + [dict(i) for i in jersey_items]
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
    
    return render_template('profile.html', user=user, message=message, orders=orders, wishlist=wishlist)

"""

content = re.sub(r"@app\.route\('/profile'\).*?return render_template\('profile\.html', user=user, message=message, orders=orders, wishlist=wishlist\)\n\n", profile_logic, content, flags=re.DOTALL)

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_user.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated API profile route!")
