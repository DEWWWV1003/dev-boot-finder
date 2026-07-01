import sqlite3
import os

db_path = r"C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\database.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Migrate user_carts
print("Migrating user_carts...")
c.execute('''
    CREATE TABLE user_carts_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        boot_id INTEGER,
        jersey_id INTEGER,
        quantity INTEGER NOT NULL DEFAULT 1,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (boot_id) REFERENCES boots(id),
        FOREIGN KEY (jersey_id) REFERENCES jerseys(id)
    )
''')
c.execute("INSERT INTO user_carts_new (id, user_id, boot_id, quantity, added_at) SELECT id, user_id, boot_id, quantity, added_at FROM user_carts")
c.execute("DROP TABLE user_carts")
c.execute("ALTER TABLE user_carts_new RENAME TO user_carts")

# Migrate order_items
print("Migrating order_items...")
c.execute('''
    CREATE TABLE order_items_new (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        boot_id INTEGER,
        jersey_id INTEGER,
        quantity INTEGER NOT NULL,
        price_at_purchase REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (boot_id) REFERENCES boots(id),
        FOREIGN KEY (jersey_id) REFERENCES jerseys(id)
    )
''')
c.execute("INSERT INTO order_items_new (id, order_id, boot_id, quantity, price_at_purchase) SELECT id, order_id, boot_id, quantity, price_at_purchase FROM order_items")
c.execute("DROP TABLE order_items")
c.execute("ALTER TABLE order_items_new RENAME TO order_items")

conn.commit()
conn.close()
print("Migration completed successfully!")
