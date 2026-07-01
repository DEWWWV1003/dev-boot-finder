import os
import shutil
import sqlite3

# Define source and destination
src_dir = r"C:\Users\SB Info\.gemini\antigravity\brain\a3b52162-541e-462f-9cfa-e755157d16a0"
dest_dir = r"C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\static\images\jerseys"
os.makedirs(dest_dir, exist_ok=True)

# Files from the latest upload
files = [
    "media__1782874830695.jpg",
    "media__1782874830697.jpg",
    "media__1782874830700.jpg",
    "media__1782874830702.jpg",
    "media__1782874863991.jpg"
]

retro_jerseys_data = [
    {"name": "Barcelona 1980s Home Retro Kit", "brand": "Meyba", "team": "FC Barcelona", "image": "barcelona_retro.jpg", "price": 120.00, "era": "Retro"},
    {"name": "Brazil 1998 World Cup Retro Kit", "brand": "Nike", "team": "Brazil National Team", "image": "brazil_retro.jpg", "price": 140.00, "era": "Retro"},
    {"name": "Italy 1998 Home Retro Kit", "brand": "Kappa", "team": "Italy National Team", "image": "italy_retro.jpg", "price": 135.00, "era": "Retro"},
    {"name": "England 1990s Polo Retro Kit", "brand": "Umbro", "team": "England National Team", "image": "england_retro.jpg", "price": 115.00, "era": "Retro"},
    {"name": "Liverpool 1990s Home Retro Kit", "brand": "Adidas", "team": "Liverpool FC", "image": "liverpool_retro.jpg", "price": 125.00, "era": "Retro"}
]

# Copy files
for i, f in enumerate(files):
    if i < len(retro_jerseys_data):
        src_path = os.path.join(src_dir, f)
        dest_path = os.path.join(dest_dir, retro_jerseys_data[i]["image"])
        if os.path.exists(src_path):
            shutil.copy(src_path, dest_path)
            print(f"Copied {f} to {retro_jerseys_data[i]['image']}")
        else:
            print(f"File not found: {f}")

# Update Database
db_path = r"C:\Users\SB Info\.gemini\antigravity\scratch\football_boots_store\database.db"
conn = sqlite3.connect(db_path)
c = conn.cursor()

# Clear old retro jerseys
c.execute("DELETE FROM jerseys WHERE era = 'Retro'")

# Insert new retro jerseys
for j in retro_jerseys_data:
    c.execute(
        "INSERT INTO jerseys (name, team, price, image_url, era) VALUES (?, ?, ?, ?, ?)",
        (f"{j['name']} ({j['brand']})", j['team'], j['price'], f"/static/images/jerseys/{j['image']}", j['era'])
    )

conn.commit()
conn.close()
print("Retro jerseys updated successfully!")
