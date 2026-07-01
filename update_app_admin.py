import re

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_admin.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Update admin_banking loop
banking_logic = """    for o in orders:
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
        
        order_dict = dict(o)
        order_dict['items'] = [dict(i) for i in boot_items] + [dict(i) for i in jersey_items]
        # Rename item_name to boot_name for template compatibility
        for item in order_dict['items']:
            item['boot_name'] = item['item_name']
            
        orders_with_items.append(order_dict)"""

content = re.sub(r"    for o in orders:\n        items = conn\.execute\('''.*?WHERE oi\.order_id = \?\n        ''', \(o\['id'\],\)\)\.fetchall\(\)\n        \n        order_dict = dict\(o\)\n        order_dict\['items'\] = \[dict\(i\) for i in items\]\n        orders_with_items\.append\(order_dict\)", banking_logic, content, flags=re.DOTALL)

# Update admin_wishlist
wishlist_logic = """    conn = get_db_connection()
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
        grouped_wishlists[uid]['total_value'] += subtotal"""

content = re.sub(r"    conn = get_db_connection\(\)\n    raw_wishlists = conn\.execute\('''.*?ORDER BY uc\.added_at DESC\n    '''\)\.fetchall\(\)\n    conn\.close\(\)\n    \n    grouped_wishlists = \{\}\n    for item in raw_wishlists:.*?grouped_wishlists\[uid\]\['total_value'\] \+= subtotal", wishlist_logic, content, flags=re.DOTALL)

with open(r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_admin.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app_admin routes!")
