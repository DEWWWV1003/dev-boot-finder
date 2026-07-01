import sqlite3
conn = sqlite3.connect('database.db')
cursor = conn.cursor()

cursor.execute('SELECT id FROM boots WHERE position="Goalkeeper" ORDER BY id')
ids = [row[0] for row in cursor.fetchall()]

if len(ids) >= 3:
    cursor.execute('UPDATE boots SET name="Nike Tiempo Legend X", brand="Nike", image_url="/static/images/studs_nike_tiempo.jpg", description="Premium leather providing ultimate comfort and a clean touch, focusing on the conical studs and premium traction pattern." WHERE id=?', (ids[0],))
    cursor.execute('UPDATE boots SET name="Nike Mercurial Superfly", brand="Nike", image_url="/static/images/studs_nike_mercurial.jpg", description="Explosive speed focusing on the aggressive chevron bladed studs designed for quick reflexes and lateral movement." WHERE id=?', (ids[1],))
    cursor.execute('UPDATE boots SET name="Adidas Copa Pure", brand="Adidas", image_url="/static/images/studs_adidas_copa.jpg", description="Classic semi-conical studs for perfect pivoting and control. Buttery soft leather ensures zero distractions." WHERE id=?', (ids[2],))
    conn.commit()
    print('Updated Goalkeeper boots with new images and Mercurial!')
else:
    print('Error: Could not find exactly 3 Goalkeeper boots. Found', len(ids))

conn.close()
