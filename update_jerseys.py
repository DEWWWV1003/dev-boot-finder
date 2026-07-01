import os
import shutil
import sqlite3

# Define source and destination
src_dir = r"C:\Users\SB Info\.gemini\antigravity\brain\a3b52162-541e-462f-9cfa-e755157d16a0"
dest_dir = r"C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\static\images\jerseys"
os.makedirs(dest_dir, exist_ok=True)

# File mappings (assuming order of timestamps matches prompt order)
# media__1782874199736.jpg, 738, 743, 748
files = sorted([f for f in os.listdir(src_dir) if f.startswith("media__1782874199")])

jerseys_data = [
    {"name": "Manchester City 24/25 Fourth Kit", "brand": "Puma", "team": "Manchester City", "image": "mancity_puma.jpg", "price": 95.00, "era": "Modern"},
    {"name": "Nigeria 24/25 Home Kit", "brand": "Nike", "team": "Nigeria National Team", "image": "nigeria_nike.jpg", "price": 90.00, "era": "Modern"},
    {"name": "Real Madrid Y-3 4th Kit", "brand": "Adidas", "team": "Real Madrid", "image": "realmadrid_y3.jpg", "price": 130.00, "era": "Modern"},
    {"name": "Barcelona 24/25 Away Kit", "brand": "Nike", "team": "FC Barcelona", "image": "barcelona_nike.jpg", "price": 105.00, "era": "Modern"}
]

# Copy files
for i, f in enumerate(files):
    if i < len(jerseys_data):
        src_path = os.path.join(src_dir, f)
        dest_path = os.path.join(dest_dir, jerseys_data[i]["image"])
        shutil.copy(src_path, dest_path)
        print(f"Copied {f} to {jerseys_data[i]['image']}")

# Update Database
db_path = r"C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\database.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Clear old jerseys
c.execute("DELETE FROM jerseys")

# Insert new jerseys
for j in jerseys_data:
    c.execute(
        "INSERT INTO jerseys (name, team, price, image_url, era) VALUES (?, ?, ?, ?, ?)",
        (f"{j['name']} ({j['brand']})", j['team'], j['price'], f"/static/images/jerseys/{j['image']}", j['era'])
    )

conn.commit()
conn.close()
print("Database updated successfully!")
