import re
import os

filepath = r'C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\app_admin.py'
with open(filepath, 'r', encoding='utf-8') as f:
    content = f.read()

if 'import json' not in content:
    content = content.replace('import sqlite3', 'import sqlite3\nimport json')

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
        orders_with_items.append(order_dict)"""

content = re.sub(r"    for o in orders:\n        boot_items = conn\.execute\('''.*?orders_with_items\.append\(order_dict\)", banking_logic, content, flags=re.DOTALL)

with open(filepath, 'w', encoding='utf-8') as f:
    f.write(content)
print("Updated app_admin.py with customizer routes!")
