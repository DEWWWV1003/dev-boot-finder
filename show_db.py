import sqlite3

def show_data():
    conn = sqlite3.connect('database.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    c.execute('SELECT brand, name, gender, position, price, rating FROM boots LIMIT 8')
    rows = c.fetchall()
    
    print("-" * 90)
    print(f"{'Brand':<15} | {'Product Name':<30} | {'Gender':<8} | {'Position':<12} | {'Price':<8} | {'Rating'}")
    print("-" * 90)
    for r in rows:
        print(f"{r['brand']:<15} | {r['name']:<30} | {r['gender']:<8} | {r['position']:<12} | ${r['price']:<7.2f} | {r['rating']:.1f} stars")
    print("-" * 90)
    conn.close()

if __name__ == '__main__':
    show_data()
