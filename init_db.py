import sqlite3
import os

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'database.db')

def initialize_database():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('DROP TABLE IF EXISTS boots')
    cursor.execute('''
    CREATE TABLE boots (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        brand TEXT NOT NULL,
        gender TEXT NOT NULL,
        position TEXT NOT NULL,
        price REAL NOT NULL,
        rating REAL NOT NULL,
        description TEXT NOT NULL,
        key_features TEXT NOT NULL,
        image_url TEXT NOT NULL,
        colorway TEXT NOT NULL,
        legends TEXT NOT NULL,
        priority TEXT NOT NULL,
        stud_type TEXT NOT NULL DEFAULT "FG",
        surface TEXT NOT NULL DEFAULT "Natural Grass",
        boot_category TEXT NOT NULL DEFAULT "Speed",
        era TEXT NOT NULL DEFAULT "Modern"
    )
    ''')

    cursor.execute('DROP TABLE IF EXISTS admins')
    cursor.execute('''
    CREATE TABLE admins (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL UNIQUE,
        password_hash TEXT NOT NULL
    )
    ''')
    import werkzeug.security
    cursor.execute('INSERT INTO admins (username, password_hash) VALUES (?, ?)', 
                   ('admin', werkzeug.security.generate_password_hash('admin123')))

    cursor.execute('DROP TABLE IF EXISTS jerseys')
    cursor.execute('''
    CREATE TABLE jerseys (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        team TEXT NOT NULL,
        era TEXT NOT NULL,
        price REAL NOT NULL,
        image_url TEXT NOT NULL
    )
    ''')

    jerseys_data = [
        ("Brazil 1994 Home Retro", "Brazil", "Retro", 120.00, "/static/images/jersey_retro.jpg"),
        ("Italy 1990 Home Retro", "Italy", "Retro", 130.00, "/static/images/jersey_retro.jpg"),
        ("France 1998 Home Retro", "France", "Retro", 125.00, "/static/images/jersey_retro.jpg"),
        ("Argentina 1986 Away Retro", "Argentina", "Retro", 140.00, "/static/images/jersey_retro.jpg"),
        ("England 1966 Home Retro", "England", "Retro", 115.00, "/static/images/jersey_retro.jpg"),
        ("Germany 1990 Home Retro", "Germany", "Retro", 135.00, "/static/images/jersey_retro.jpg"),
        
        ("France 2024 Home Modern", "France", "Modern", 150.00, "/static/images/jersey_modern.jpg"),
        ("Argentina 2022 Home Modern", "Argentina", "Modern", 145.00, "/static/images/jersey_modern.jpg"),
        ("Brazil 2022 Away Modern", "Brazil", "Modern", 145.00, "/static/images/jersey_modern.jpg"),
        ("Spain 2024 Home Modern", "Spain", "Modern", 155.00, "/static/images/jersey_modern.jpg"),
        ("Portugal 2024 Away Modern", "Portugal", "Modern", 150.00, "/static/images/jersey_modern.jpg"),
        ("Japan 2022 Home Modern", "Japan", "Modern", 160.00, "/static/images/jersey_modern.jpg")
    ]
    cursor.executemany('''
        INSERT INTO jerseys (name, team, era, price, image_url)
        VALUES (?, ?, ?, ?, ?)
    ''', jerseys_data)

    cursor.execute('DROP TABLE IF EXISTS user_carts')
    cursor.execute('''
    CREATE TABLE user_carts (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER NOT NULL,
        boot_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL DEFAULT 1,
        added_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(user_id, boot_id),
        FOREIGN KEY (user_id) REFERENCES users(id),
        FOREIGN KEY (boot_id) REFERENCES boots(id)
    )
    ''')

    cursor.execute('DROP TABLE IF EXISTS orders')
    cursor.execute('''
    CREATE TABLE orders (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        total_price REAL NOT NULL,
        status TEXT NOT NULL DEFAULT 'Placed',
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
        risk_score INTEGER DEFAULT 0,
        fraud_reason TEXT,
        is_flagged BOOLEAN DEFAULT 0
    )
    ''')

    cursor.execute('DROP TABLE IF EXISTS order_items')
    cursor.execute('''
    CREATE TABLE order_items (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        order_id INTEGER NOT NULL,
        boot_id INTEGER NOT NULL,
        quantity INTEGER NOT NULL,
        price_at_purchase REAL NOT NULL,
        FOREIGN KEY (order_id) REFERENCES orders(id),
        FOREIGN KEY (boot_id) REFERENCES boots(id)
    )
    ''')

    cursor.execute('DROP TABLE IF EXISTS feedback')
    cursor.execute('''
    CREATE TABLE feedback (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        message TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')

    # ─── ERA VALUES: Modern | Vintage ────────────────────────────────────────
    # STUD TYPES: FG | SG | AG | TF | IC | HG | MG | Futsal
    # ─────────────────────────────────────────────────────────────────────────

    boots_data = [

        # ══════════════════════════════════════════════════════════
        #  VINTAGE CLASSICS — Men's
        # ══════════════════════════════════════════════════════════

        # ─ Vintage: Adidas Copa Mundial (1982) ─
        ("Adidas Copa Mundial (1982)", "Adidas", "Male", "Midfielder", 320.00, 5.0,
         "The most sold football boot in history. Hand-stitched kangaroo leather upper with a clean K-leather feel that no modern synthetic has ever matched. Worn by legends across five World Cups.",
         "Premium Kangaroo Leather Upper;Hand-Stitched Construction;Classic Conical FG Studs;Thin Leather Lining;Timeless 3-Stripe Design",
         "/static/images/boot_adidas.png", "Tan/White/Black",
         "Diego Maradona;Franz Beckenbauer;Michel Platini;Lothar Matthaus;Roberto Baggio;Ronaldo R9",
         "Touch", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ─ Vintage: Adidas World Cup (1970) ─
        ("Adidas World Cup (1970)", "Adidas", "Male", "Attacker", 280.00, 4.9,
         "The boot Pelé wore in Mexico 1970. One of the most iconic studs in football history. A timeless full-grain leather construction with replaceable screw-in studs built for mud and glory.",
         "Full-Grain Leather Upper;Screw-In SG Replaceable Studs;Reinforced Toe Box;Classic 3-Stripe Side;Minimal Padding Lining",
         "/static/images/boot_adidas.png", "Black/White",
         "Pele;Gerd Muller;Johan Cruyff;Eusebio",
         "Touch", "SG", "Natural Grass – Soft / Wet", "Touch", "Vintage"),

        # ─ Vintage: Puma King (1968) ─
        ("Puma King (1968)", "Puma", "Male", "Attacker", 260.00, 4.9,
         "Eusebio's boot. Pelé's boot. Johan Cruyff's boot. The Puma King defined an era of attacking football. Handcrafted full-grain leather with a wide toe box for maximum ball feel.",
         "Full-Grain Leather Upper;Wide Toe Box;Classic Conical Studs;Minimal Leather Lining;Iconic Crown Badge",
         "/static/images/boot_puma.png", "Black/White/Gold",
         "Pele;Eusebio;Johan Cruyff;Gerd Muller;Lothar Matthaus",
         "Touch", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ─ Vintage: Adidas Predator (1994 Original) ─
        ("Adidas Predator Rapier (1994)", "Adidas", "Male", "Midfielder", 350.00, 5.0,
         "Craig Johnston's revolutionary invention. The world's first boot with rubber swerve elements grafted onto the upper. Zidane and Beckham redefined the art of the free-kick in these studs.",
         "Natural Leather Upper;Rubber Swerve Fins on Strike Zone;Classic FG Blade Studs;Ankle Collar Design;Original 3-Stripe Branding",
         "/static/images/boot_adidas.png", "Black/Red/White",
         "Zinedine Zidane;David Beckham;Patrick Kluivert;Roberto Carlos",
         "Control", "FG", "Natural Grass – Firm", "Control", "Vintage"),

        # ─ Vintage: Nike Mercurial R9 (1998) ─
        ("Nike Mercurial R9 (1998)", "Nike", "Male", "Attacker", 400.00, 5.0,
         "Designed exclusively for Ronaldo Nazario for the 1998 World Cup. The boot that launched the speed revolution in football. Shockingly light at the time, with an aggressive blade pattern that changed everything.",
         "Thin Synthetic Speed Upper;Pioneering Blade Stud Configuration;Laceless Speed Plate Concept;R9 Monogram;Revolutionary Ultra-Light Construction",
         "/static/images/boot_nike.png", "Silver/Blue/Black",
         "Ronaldo R9;Thierry Henry;Ronaldinho",
         "Speed", "FG", "Natural Grass – Firm", "Speed", "Vintage"),

        # ─ Vintage: Nike Tiempo Air (1994) ─
        ("Nike Tiempo Air (1994)", "Nike", "Male", "Defender", 230.00, 4.7,
         "Nike's first serious attempt at the beautiful game. Air cushioning in the heel decades before anyone else. Full-grain leather upper made for commanding centre-backs who dominate the air.",
         "Full-Grain Leather Upper;Nike Air Cushioning in Heel;Reinforced Ankle Collar;Classic Conical Studs;Deep Toe Box",
         "/static/images/boot_nike.png", "Black/Dark Green/White",
         "Alessandro Del Piero;Gabriel Batistuta;Jorge Campos",
         "Stability", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ─ Vintage: Puma Future Cat (Maradona) ─
        ("Puma Future Cat (1986)", "Puma", "Male", "Attacker", 290.00, 5.0,
         "Maradona's boot in the 1986 World Cup when he single-handedly carried Argentina to glory, scoring the Goal of the Century against England. A symbol of pure genius.",
         "Argentina Blue Suede Upper;Screw-In SG Metal Studs;Narrow Last Design;Padded Ankle Collar;Classic Puma Cat Badge",
         "/static/images/boot_puma.png", "Argentina Blue/White/Gold",
         "Diego Maradona;Jorge Valdano;Jorge Burruchaga",
         "Control", "SG", "Natural Grass – Soft / Wet", "Control", "Vintage"),

        # ─ Vintage: Asics Testastretta (2000s) ─
        ("Asics Testastretta (2006)", "Asics", "Male", "Attacker", 190.00, 4.6,
         "A true cult classic from the 2000s. Handcrafted leather meets an aggressive stud pattern, famously worn by Italian snipers during the golden era of Serie A.",
         "K-Leather Upper;Conical FG Studs;Classic Asics Tiger Stripes;Padded Tongue;Wide Toe Box",
         "/static/images/boot_placeholder_1782470970616.jpg", "White/Red/Black",
         "Fabio Grosso;Alvaro Recoba",
         "Stability", "FG", "Natural Grass – Firm", "Power", "Vintage"),

        # ─ Vintage: Umbro Speciali (1992) ─
        ("Umbro Speciali (1992)", "Umbro", "Male", "Attacker", 175.00, 4.5,
         "The iconic English boot. Roberto Carlos's impossible free-kick and Alan Shearer's endless goals. Premium leather upper with a distinctive diamond-toe box.",
         "Premium Calf Leather Upper;Diamond Toe Box;Classic Conical FG Studs;Umbro Diamond Branding;Minimal Internal Lining",
         "/static/images/vintage_umbro.jpg", "Black/White",
         "Alan Shearer;Roberto Carlos;Michael Owen",
         "Power", "FG", "Natural Grass – Firm", "Power", "Vintage"),

        # ─ Vintage: Mizuno Morelia (1985) ─
        ("Mizuno Morelia (1985)", "Mizuno", "Male", "Midfielder", 310.00, 4.8,
         "Lightweight Japanese craftsmanship meeting premium K-leather. A cult classic among true playmakers.",
         "Hand-Stitched Kangaroo Leather Upper;Custom Mould-To-Foot Design;Classic Conical FG Studs;Feather-Light 195g Construction;Made in Japan",
         "/static/images/vintage_mizuno.jpg", "Black/White",
         "Rivaldo;Roberto Carlos;Careca",
         "Touch", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ─ Vintage: Diadora Brasil (1984) ─
        ("Diadora Brasil (1984)", "Diadora", "Male", "Midfielder", 220.00, 4.9,
         "Italian elegance. The undisputed boot of the 90s Serie A golden era and countless Ballon d'Or winners.",
         "K-Leather Upper;Italian Craftsmanship;Classic FG Studs;Diadora Logo;Fold-over tongue",
         "/static/images/vintage_diadora.jpg", "Black/Neon Yellow",
         "Roberto Baggio;Roy Keane;Zico",
         "Control", "FG", "Natural Grass – Firm", "Control", "Vintage"),

        # ─ Vintage: Nike Tiempo Premier (1994) ─
        ("Nike Tiempo Premier (1994)", "Nike", "Male", "Defender", 250.00, 4.7,
         "Worn by almost half the players in the '94 World Cup final. The boot that established Nike in world football.",
         "Full-Grain Leather Upper;Nike Air Cushioning;Classic Conical Studs;Deep Toe Box",
         "/static/images/vintage_nike_tiempo.jpg", "Black/White",
         "Romario;Paolo Maldini;Eric Cantona",
         "Touch", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ─ Vintage: Lotto Stadio (1990) ─
        ("Lotto Stadio (1990)", "Lotto", "Male", "Midfielder", 195.00, 4.6,
         "Defined by its vibrant green emblem, the Stadio was the boot of European champions and midfield generals.",
         "Premium Leather Upper;Stitching detail;Classic FG Soleplate;Iconic Green Logo",
         "/static/images/vintage_lotto.jpg", "Black/Green",
         "Ruud Gullit;Andriy Shevchenko;Cafu",
         "Touch", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ─ Vintage: Adidas F50 (2004) ─
        ("Adidas F50 (2004)", "Adidas", "Male", "Attacker", 285.00, 4.8,
         "The dawn of Adidas speed. Concealed laces and a striking chassis that birthed a legendary lineage.",
         "Synthetic Speed Upper;Concealed Lace Cover;Blade Stud Configuration;SprintFrame prototype",
         "/static/images/vintage_adidas_f50.jpg", "Yellow/Black",
         "Arjen Robben;Lionel Messi;Ashley Cole",
         "Speed", "FG", "Natural Grass – Firm", "Speed", "Vintage"),

        # ─ Vintage: Women's Copa Mundial Heritage ─
        ("Adidas Copa Mundial Heritage W (1982)", "Adidas", "Female", "Midfielder", 300.00, 4.9,
         "A women's tribute edition of the most iconic boot ever made. Kangaroo leather crafted on a women's last — worn by the pioneering generation of women's footballers who fought to play on the same stage as men.",
         "Kangaroo Leather Women's Last;Classic Conical FG Studs;Thin Leather Lining;Narrow Heel Counter;Heritage 3-Stripe Design",
         "/static/images/boot_adidas.png", "Tan/White/Black",
         "Mia Hamm;Sun Wen;April Heinrichs;Michelle Akers",
         "Touch", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ─ Vintage: Women's Puma King Heritage ─
        ("Puma King Heritage W (1970s)", "Puma", "Female", "Attacker", 240.00, 4.8,
         "The women's version of football's most storied boot. Handcrafted leather on a low-volume women's last, worn by the legends who built women's football from the ground up in its earliest tournaments.",
         "Full-Grain Leather Women's Last;Wide Forefoot Women's Fit;Classic Conical FG Studs;Gold Crown Puma Badge;Heritage White/Black Colorway",
         "/static/images/boot_puma.png", "White/Black/Gold",
         "Michelle Akers;Mia Hamm;Birgit Prinz;Hege Riise",
         "Touch", "FG", "Natural Grass – Firm", "Touch", "Vintage"),

        # ═══════════════════════════════════════════════
        #  INDOOR / FUTSAL — Men's
        # ═══════════════════════════════════════════════

        ("Nike Mercurial Vapor 15 Academy IC", "Nike", "Male", "Attacker", 85.00, 4.5,
         "The fastest indoor boot Nike has ever made. Gripknit upper provides the same tactile touch as the FG version on polished futsal court surfaces. Flat rubber sole grips without marking indoor courts.",
         "Gripknit Upper;Flat Non-Marking Rubber Sole;Speed Rib Traction Pattern;Minimal Boot Weight;Low-Cut Collar",
         "/static/images/boot_nike.png", "Hot Pink/Black/Chrome",
         "Kylian Mbappe;Vinicius Jr;Rodrygo", "Speed", "IC", "Indoor Court / Futsal Hall", "Speed", "Modern"),

        ("Adidas Copa Gloro IC", "Adidas", "Male", "Midfielder", 90.00, 4.4,
         "Soft leather touch in an indoor-ready flat sole format. The Copa Gloro IC is the futsal coach's recommendation for players who want Copa-level first touch control during indoor tactical sessions.",
         "Leather Touch Upper;Flat IC Non-Marking Sole;Clean Laceless Design;Padded Ankle Collar;Copa Heritage Toe Box",
         "/static/images/boot_adidas.png", "Cloud White/Red/Black",
         "Andres Iniesta;Xavi Hernandez;Toni Kroos", "Touch", "IC", "Indoor Court / Futsal Hall", "Touch", "Modern"),

        ("Puma Clyde Futsal", "Puma", "Male", "Attacker", 78.00, 4.3,
         "Named after Walt 'Clyde' Frazier, this iconic silhouette was reimagined for futsal. A low-profile flat rubber outsole with a suede-like upper gives exceptional court feel during fast 5-a-side combinations.",
         "Suede-Feel Synthetic Upper;Full-Length Flat Futsal Rubber Sole;Padded Collar;Classic Puma Formstrip;Low-Profile Design",
         "/static/images/boot_puma.png", "Black/Red/White",
         "Neymar Jr;Falcao (Futsal);Thiago Silva", "Control", "IC", "Indoor Court / Futsal Hall", "Control", "Modern"),

        ("New Balance Audazo v6+ IC", "New Balance", "Male", "Midfielder", 95.00, 4.6,
         "NB's flagship futsal shoe. The wrap-around Hypoknit construction locks the foot in place during sharp directional changes on polished futsal floors, with a herringbone rubber sole for maximum court grip.",
         "Hypoknit Wrap Upper;Herringbone IC Rubber Sole;Anti-Slip Heel Grip;Padded Tongue and Collar;EVA Insole Cushioning",
         "/static/images/boot_nb.png", "Neon Pink/Black/White",
         "Rose Lavelle;Adam Lallana;Ferrao", "Control", "IC", "Indoor Court / Futsal Hall", "Control", "Modern"),

        ("Nike Phantom GT Academy IC Futsal", "Nike", "Male", "Midfielder", 80.00, 4.3,
         "The Gripknit IC delivers pinpoint passing accuracy on futsal courts. Ghost lacing keeps the striking surface completely clean for clinical finishing in tight futsal penalty areas.",
         "Gripknit Futsal Upper;Ghost Lacing System;Flat IC Non-Marking Sole;Thin Forefoot Foam;Low-Cut Design",
         "/static/images/boot_nike.png", "Black/Pink/White",
         "Luka Modric;Kevin De Bruyne;Ferrao", "Control", "IC", "Indoor Court / Futsal Hall", "Control", "Modern"),

        ("Adidas Predator Accuracy IC", "Adidas", "Male", "Midfielder", 92.00, 4.5,
         "Rubber grip zones across the forefoot translate directly to futsal — perfect for the player who wants to add swerve and power to indoor long-range strikes. Full flat IC sole for gym and court play.",
         "HD Grip Rubber Zones;Laceless IC Upper;Flat Non-Marking Rubber Sole;Wide Futsal Platform;ACC Coating",
         "/static/images/boot_adidas.png", "Core Black/Red/White",
         "Jude Bellingham;Bruno Fernandes;Thiago Alcantara", "Control", "IC", "Indoor Court / Futsal Hall", "Control", "Modern"),

        ("Skechers SKX Futsal IC", "Skechers", "Male", "Attacker", 75.00, 4.4,
         "Skechers brings their signature comfort tech to the indoor court. The SKX Futsal features a hyper-burst foam midsole and a grippy flat rubber sole for maximum control.",
         "Performance Knit Upper;Flat IC Rubber Sole;Hyper-Burst Cushioning;Comfort Fit Collar;Simple Lace System",
         "/static/images/boot_placeholder_1782470970616.jpg", "Blue/Neon Yellow",
         "Harry Kane;Oleksandr Zinchenko", "Control", "IC", "Indoor Court / Futsal Hall", "Control", "Modern"),

        # ─ Women's Indoor ─
        ("Nike Mercurial Vapor 15 W IC", "Nike", "Female", "Attacker", 82.00, 4.5,
         "Women's IC version of the world's fastest indoor boot. Narrower women's last with Gripknit upper and flat IC sole for explosive futsal play in women's indoor competitions.",
         "Women's Gripknit Upper;Flat Non-Marking IC Sole;Women's Narrow Last;Speed Rib Sole Pattern;Low Ankle Collar",
         "/static/images/boot_nike.png", "Fierce Pink/Black/Chrome",
         "Sophia Smith;Sam Kerr;Trinity Rodman", "Speed", "IC", "Indoor Court / Futsal Hall", "Speed", "Modern"),

        ("Adidas Copa Gloro W IC", "Adidas", "Female", "Midfielder", 88.00, 4.4,
         "Women's Copa leather touch for indoor futsal. Narrower heel fit and lightweight IC flat sole for women's futsal players who demand Copa-quality touch in training and competition.",
         "Women's Leather Touch Upper;Women's Copa Last;Flat IC Non-Marking Sole;Copa Toe Box Design;Padded Ankle",
         "/static/images/boot_adidas.png", "White/Pink/Gold",
         "Alexia Putellas;Caroline Graham Hansen;Marta", "Touch", "IC", "Indoor Court / Futsal Hall", "Touch", "Modern"),

        ("Puma Futura Futsal W IC", "Puma", "Female", "Attacker", 75.00, 4.2,
         "Lightweight women's futsal shoe with a breathable knit upper and herringbone flat IC rubber sole. Ideal for fast breaks and tight-space dribbling in women's futsal leagues.",
         "Women's Knit Upper;Herringbone Flat IC Sole;Women's Narrow Last;Padded Heel Collar;Lightweight EVA Midsole",
         "/static/images/boot_puma.png", "Pink/Black/White",
         "Tobin Heath;Christine Sinclair;Deyna Castellanos", "Speed", "IC", "Indoor Court / Futsal Hall", "Speed", "Modern"),

        # ═══════════════════════════════════════════════
        #  MULTI-GROUND (MG) — Men's & Women's
        # ═══════════════════════════════════════════════

        ("Nike Mercurial Superfly 9 Academy MG", "Nike", "Male", "Attacker", 130.00, 4.5,
         "The MG version of the world's fastest boot adapts across dry FG and light AG surfaces. Mixed rubber and TPU stud configuration handles both natural and artificial pitches without compromising sprint speed.",
         "Flyknit Upper;MG Mixed Stud Configuration (Rubber + TPU);Aerotrak MG Plate;Laceless Design;Speed Collar",
         "/static/images/boot_nike.png", "Volt/Black/Hot Pink",
         "Mbappe;Cristiano Ronaldo;Marcus Rashford;Vinicius Jr", "Speed", "MG", "Multi-Ground – FG + AG", "Speed", "Modern"),

        ("Adidas X Crazyfast Club MG", "Adidas", "Male", "Attacker", 110.00, 4.3,
         "Entry-level Crazyfast MG for weekend warriors and academy players who train on multiple surfaces. Lightweight synthetic upper with an MG dual-compound soleplate that handles both grass and 3G turf.",
         "Lightweight Synthetic Upper;Dual-Compound MG Soleplate;Mixed Short+Long Stud Layout;Energy-Return Sockliner;Tight Collar Fit",
         "/static/images/boot_adidas.png", "Core Black/Red/Solar Red",
         "Erling Haaland;Bukayo Saka;Gabriel Martinelli", "Speed", "MG", "Multi-Ground – FG + AG", "Speed", "Modern"),

        ("Puma Ultra 5 Play MG", "Puma", "Male", "Attacker", 95.00, 4.2,
         "Puma's versatile MG speed boot for players who split time between natural grass and academy 3G pitches. ULTRAWEAVE construction keeps weight minimal while the MG plate handles any surface.",
         "ULTRAWEAVE Synthetic Upper;MG Dual-Rubber + TPU Stud Plate;SpeedUnit Sole;Laceless Design;Anti-Clog Stud Design",
         "/static/images/boot_puma.png", "Black/Red/Fizzy Light",
         "Neymar Jr;Leroy Sane;Antoine Griezmann", "Speed", "MG", "Multi-Ground – FG + AG", "Speed", "Modern"),

        ("New Balance Furon v7 Pro MG", "New Balance", "Male", "Attacker", 155.00, 4.5,
         "NB's most versatile MG speed boot. The MG Furon delivers consistent acceleration traction across multiple surfaces — ideal for semi-professional players who play on park pitches one weekend and 3G the next.",
         "Cyclone Knit Upper;MG Hybrid Stud Plate (FG+AG Combo);Laceless Lock-In;EVA Midsole;Ankle Tension Band",
         "/static/images/boot_nb.png", "Black/Hot Pink/White",
         "Sadio Mane;Gareth Bale;James Maddison", "Speed", "MG", "Multi-Ground – FG + AG", "Speed", "Modern"),

        ("Nike Phantom GX II Club MG", "Nike", "Male", "Midfielder", 90.00, 4.2,
         "Gripknit touch on a multi-ground soleplate. This entry-level Phantom delivers control-boot performance for midfielders who rotate between natural grass training and 3G matchday surfaces.",
         "Gripknit MG Upper;Mixed MG Stud Configuration;Ghost Lacing;EVA Flat Insole;ACC Coating",
         "/static/images/boot_nike.png", "Black/Pink/Chrome",
         "Kevin De Bruyne;Bruno Fernandes;Martin Odegaard", "Control", "MG", "Multi-Ground – FG + AG", "Control", "Modern"),

        ("Adidas Predator League MG", "Adidas", "Male", "Midfielder", 120.00, 4.4,
         "Grip zones meet multi-ground versatility. The Predator League MG is the workhorse control boot for players who demand rubber-grip passing accuracy on both natural grass and artificial training pitches.",
         "Recyclon MG Upper;HD Grip Rubber Zones;MG Mixed Stud Soleplate;Hybridtouch Construction;Energy Pulse Sockliner",
         "/static/images/boot_adidas.png", "Core Black/Red/White",
         "Jude Bellingham;Pedri;Thiago Alcantara", "Control", "MG", "Multi-Ground – FG + AG", "Control", "Modern"),

        # ─ Women's MG ─
        ("Nike Mercurial Superfly 9 W MG", "Nike", "Female", "Attacker", 125.00, 4.5,
         "Women's MG speed boot for the versatile attacker. Women's-specific Flyknit with a mixed MG stud plate covering natural grass, light turf, and 3G pitches encountered in women's league schedules.",
         "Women's Flyknit Upper;Women's MG Mixed Stud Plate;Aerotrak W Plate;Zoom Air Heel Unit;Speed Collar",
         "/static/images/boot_nike.png", "Fierce Pink/Black/Chrome",
         "Sophia Smith;Sam Kerr;Trinity Rodman;Marta", "Speed", "MG", "Multi-Ground – FG + AG", "Speed", "Modern"),

        ("Adidas Copa Pure.1 W MG", "Adidas", "Female", "Midfielder", 145.00, 4.4,
         "Women's Copa leather touch on a multi-ground plate — the choice for attacking midfielders who want silky first-touch precision on any surface they encounter in women's domestic competitions.",
         "Women's Fusionskin Leather;Women's Copa Last;MG Hybrid Stud Plate;Torsionframe W;Narrow Heel Counter",
         "/static/images/boot_adidas.png", "Crystal White/Pink/Gold",
         "Sam Kerr;Vivianne Miedema;Ji So-Yun", "Touch", "MG", "Multi-Ground – FG + AG", "Touch", "Modern"),

        # ═══════════════════════════════════════════════
        #  MODERN FG — Key positions (keeping from before)
        # ═══════════════════════════════════════════════

        # Male FG
        ("Nike Zoom Mercurial Superfly 9 Elite FG", "Nike", "Male", "Attacker", 280.00, 4.9,
         "The world's fastest football boot. Zoom Air heel unit and Aerotrak blade soleplate for instant explosive acceleration. Worn by the game's elite speedsters on firm natural pitches.",
         "Ultra-Thin Flyknit Upper;Zoom Air Heel Unit;Aerotrak FG Blade Soleplate;Speed Rib Traction;Laceless Design",
         "/static/images/boot_nike.png", "Volt/Black/Metallic Silver",
         "Kylian Mbappe;Cristiano Ronaldo;Marcus Rashford;Vinicius Jr", "Speed", "FG", "Natural Grass – Firm", "Speed", "Modern"),

        ("Adidas X Crazyfast.1 FG", "Adidas", "Male", "Attacker", 265.00, 4.8,
         "Ultralight Carbonskin upper at just 165g. Aggressive chevron blade stud layout for explosive acceleration on firm ground. The boot of Messi and Haaland.",
         "Carbonskin Ultra-Thin Upper (165g);Aeropulsion FG Carbon-Composite Plate;Chevron Blade Studs;360-Degree Lockdown Collar;Speed Sockliner",
         "/static/images/boot_adidas.png", "Solar Red/Black",
         "Lionel Messi;Erling Haaland;Bukayo Saka", "Speed", "FG", "Natural Grass – Firm", "Speed", "Modern"),

        ("Adidas Predator Accuracy+ Elite FG", "Adidas", "Male", "Midfielder", 275.00, 4.9,
         "275 high-definition rubber grip elements for surgical passing, set-piece swerve, and first-touch mastery. The definitive control boot for the modern game.",
         "HD Grip Rubber Zones (275 elements);Laceless Hybridtouch Upper;FacetFrame FG Soleplate;Energy-Return Midsole;Tight Collar Fit",
         "/static/images/boot_adidas.png", "Core Black/Pink/White",
         "Jude Bellingham;Pedri;Zinedine Zidane;Luka Modric", "Control", "FG", "Natural Grass – Firm", "Control", "Modern"),

        ("Nike Tiempo Legend 10 Elite FG", "Nike", "Male", "Defender", 230.00, 4.8,
         "FlyTouch Plus leather gives defenders premium touch during long clearances and distribution. The gold standard for centre-backs who want leather touch without sacrificing modern performance.",
         "FlyTouch Plus Leather;ACC (All Conditions Control);Conical FG Studs;Cushioned Lining;Heel Counter",
         "/static/images/boot_nike.png", "Emerald Green/White",
         "Thibaut Courtois;Alisson Becker;Virgil van Dijk", "Touch", "FG", "Natural Grass – Firm", "Touch", "Modern"),

        ("Puma Future Ultimate FG", "Puma", "Male", "Attacker", 245.00, 4.7,
         "PWRFRAME with FUZIONFIT+ adaptive compression for midfielders and forwards. Multi-directional acceleration with a mixed stud layout for firm natural pitches.",
         "PWRFRAME Upper;FUZIONFIT+ Adaptive Compression;PWRTAPE Closure;FG Mixed Stud Configuration;SpeedUnit Soleplate",
         "/static/images/boot_puma.png", "Sunset Glow/Gold/White",
         "Neymar Jr;Antoine Griezmann;Thomas Muller", "Speed", "FG", "Natural Grass – Firm", "Speed", "Modern"),

        ("New Balance Tekela v4+ Pro FG", "New Balance", "Male", "Defender", 215.00, 4.5,
         "Full-foot Hypoknit wrap with 3D rim outsole gives defenders unrivalled foot-lock during hard sprints and recovery challenges on firm ground.",
         "Hypoknit Compression Upper;Laceless Lock-In System;3D Rim Outsole;FG Bladed Studs;Narrow Heel Counter",
         "/static/images/boot_nb.png", "Neo Flame Red/Silver",
         "Harvey Elliott;Timothy Weah;Lisandro Martinez", "Touch", "FG", "Natural Grass – Firm", "Touch", "Modern"),

        ("Under Armour Magnetico Pro 3", "Under Armour", "Male", "Midfielder", 180.00, 4.7,
         "The Magnetico Pro 3 moulds to your foot instantly with no break-in required. Featuring Clone upper technology for a truly customized fit and a flexible FG soleplate.",
         "UA Clone Upper;Flexible FG Studs;Form-fitting Collar;Internal Cushioning;Wide Platform",
         "/static/images/boot_placeholder_1782470970616.jpg", "Black/Gold",
         "Trent Alexander-Arnold;Antonio Rudiger", "Control", "FG", "Natural Grass – Firm", "Control", "Modern"),

        ("Skechers SKX_01 FG", "Skechers", "Male", "Attacker", 210.00, 4.8,
         "The ultimate comfort striking boot. Engineered alongside Harry Kane to deliver precision, power, and unparalleled 90-minute comfort on firm ground pitches.",
         "Precise Strike Zones;Hyper-burst Midsole Tech;Conical FG Studs;Seamless Knit Upper;Lockdown Fit",
         "/static/images/boot_placeholder_1782470970616.jpg", "White/Blue",
         "Harry Kane", "Power", "FG", "Natural Grass – Firm", "Power", "Modern"),

        # Female FG
        ("Nike Zoom Mercurial Superfly 9 Elite W FG", "Nike", "Female", "Attacker", 275.00, 4.9,
         "Women's speed boot with Zoom Air heel unit tuned for lighter athletes. Aerotrak soleplate maximises ground contact efficiency for elite women's forwards.",
         "Women's Flyknit;Zoom Air Heel Unit;Aerotrak W FG Plate;Speed Rib Traction;Women's Speed Collar",
         "/static/images/boot_nike.png", "Volt/Deep Jungle/White",
         "Sophia Smith;Sam Kerr;Lindsey Horan;Marta", "Speed", "FG", "Natural Grass – Firm", "Speed", "Modern"),

        ("Adidas Predator Accuracy+ Elite W FG", "Adidas", "Female", "Midfielder", 270.00, 4.9,
         "Elite women's control boot with HD rubber grip zones across forefoot engineered for women's narrower foot geometry. The choice of Sam Kerr and Alexia Putellas.",
         "Women's HD Grip Upper;FacetFrame W Soleplate;Laceless Hybridtouch;FG Bladed Studs;Women's V-Heel",
         "/static/images/boot_adidas.png", "Wonder White/Pink",
         "Sam Kerr;Alex Morgan;Lindsey Horan;Rose Lavelle", "Control", "FG", "Natural Grass – Firm", "Control", "Modern"),

        # SG Modern
        ("Nike Mercurial Superfly 9 SG-Pro", "Nike", "Male", "Attacker", 255.00, 4.7,
         "Anti-Clog SG-Pro traction ejects mud plugs automatically. For wingers and strikers who need explosive cutting speed in winter mud conditions.",
         "Flyknit Upper;Anti-Clog SG-Pro Traction (8 Removable Metal Studs);Zoom Air Forefoot;ACC Coating;Speed Collar",
         "/static/images/boot_nike.png", "Black/Summit White",
         "Cristiano Ronaldo;Marcus Rashford;Alphonso Davies", "Speed", "SG", "Natural Grass – Soft / Wet", "Speed", "Modern"),

        # AG Modern
        ("Adidas X Crazyfast.1 AG", "Adidas", "Male", "Attacker", 220.00, 4.6,
         "AG certified Aeropulsion plate for 3G/4G artificial surfaces. Maintains sprint traction without the hard landings of FG studs on artificial turf.",
         "Carbonskin Upper;Aeropulsion AG Plate;AG Certified Rubber Short Studs;Collar Fit Sock;Speed Sockliner",
         "/static/images/boot_adidas.png", "Core Black/Blue Rush",
         "Lionel Messi;Erling Haaland;Gabriel Martinelli", "Speed", "AG", "Artificial Turf – 3G/4G", "Speed", "Modern"),

        # TF Modern
        ("Nike Phantom GX II Club TF", "Nike", "Male", "Midfielder", 80.00, 4.1,
         "Dense rubber TF nub sole for cage football and astroturf 5-a-side arenas. Gripknit upper gives control-level touch in the closest thing to a futsal setting outdoors.",
         "Gripknit Upper;Full TF Rubber Nub Outsole;Ghost Lacing;EVA Insole;ACC Coating",
         "/static/images/boot_nike.png", "Black/Pink/White",
         "Bruno Fernandes;Martin Odegaard", "Control", "TF", "Astroturf / Hard Turf", "Control", "Modern"),

        # HG Modern
        ("Adidas Copa Pure.1 HG", "Adidas", "Male", "Defender", 130.00, 4.3,
         "Compact rubber studs for compressed, sun-baked HG pitches. Ideal for players in South Asia, North Africa, and Middle East leagues where the pitch surface can feel like concrete.",
         "Fusionskin Leather;Short Rubber HG Studs;Torsionframe Plate;Breathable Mesh Lining;Wide Base",
         "/static/images/boot_adidas.png", "Sand/White",
         "Achraf Hakimi;Youssef En-Nesyri;Hakim Ziyech", "Touch", "HG", "Hard Ground / Dry Compact Soil", "Touch", "Modern"),
    ]

    cursor.executemany('''
        INSERT INTO boots
        (name, brand, gender, position, price, rating, description,
         key_features, image_url, colorway, legends, priority,
         stud_type, surface, boot_category, era)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    ''', boots_data)

    conn.commit()
    conn.close()
    print(f"[OK] Database re-seeded with {len(boots_data)} boots ({sum(1 for b in boots_data if b[-1]=='Vintage')} vintage, {sum(1 for b in boots_data if b[13] in ('IC','Futsal'))} indoor/futsal, {sum(1 for b in boots_data if b[13]=='MG')} multi-ground).")

if __name__ == '__main__':
    initialize_database()
