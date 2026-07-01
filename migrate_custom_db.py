import sqlite3
import os

db_path = r"C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\database.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

print("Adding custom_data to user_carts...")
try:
    c.execute("ALTER TABLE user_carts ADD COLUMN custom_data TEXT")
except sqlite3.OperationalError as e:
    print(e) # Might already exist

print("Adding custom_data to order_items...")
try:
    c.execute("ALTER TABLE order_items ADD COLUMN custom_data TEXT")
except sqlite3.OperationalError as e:
    print(e)

conn.commit()
conn.close()
print("Migration completed successfully!")
