import sqlite3

DB_NAME = "troskovi.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Tabela Lokacije (id, naziv) 
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Lokacije (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT UNIQUE NOT NULL
        )
    ''')

    # Tabela Troskovi povezana sa Lokacijama
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS Troskovi (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            naziv TEXT NOT NULL,
            iznos REAL NOT NULL,
            tip TEXT NOT NULL,
            namjena TEXT NOT NULL,
            lokacija_id INTEGER,
            FOREIGN KEY (lokacija_id) REFERENCES Lokacije(id)
        )
    ''')
    conn.commit()
    conn.close()

def get_or_create_location_id(grad_naziv):
    """Vraća ID lokacije. Ako grad ne postoji, kreira ga. [cite: 7, 8]"""
    grad_naziv = grad_naziv.strip().title()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    cursor.execute("SELECT id FROM Lokacije WHERE naziv = ?", (grad_naziv,))
    res = cursor.fetchone()
    
    if res:
        loc_id = res[0]
    else:
        cursor.execute("INSERT INTO Lokacije (naziv) VALUES (?)", (grad_naziv,))
        conn.commit()
        loc_id = cursor.lastrowid
        
    conn.close()
    return loc_id

def dodaj_trosak_db(naziv, iznos, tip, namjena, grad):
    # Validacija stringa 5-50 karaktera
    if not (5 <= len(naziv) <= 50):
        raise ValueError("Naziv mora imati između 5 i 50 karaktera.")
    
    loc_id = get_or_create_location_id(grad)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Troskovi (naziv, iznos, tip, namjena, lokacija_id)
        VALUES (?, ?, ?, ?, ?)
    ''', (naziv, float(iznos), tip, namjena, loc_id))
    conn.commit()
    conn.close()

def dobavi_sve_troskove():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # Spajamo tabele da dobijemo naziv grada umjesto ID-a
    cursor.execute('''
        SELECT T.id, T.naziv, T.iznos, T.tip, T.namjena, L.naziv 
        FROM Troskovi T
        JOIN Lokacije L ON T.lokacija_id = L.id
    ''')
    podaci = cursor.fetchall()
    conn.close()
    return podaci

def azuriraj_trosak_db(trosak_id, naziv, iznos, tip, namjena, grad):
    # Logika za ažuriranje 
    if not (5 <= len(naziv) <= 50):
        raise ValueError("Naziv mora imati između 5 i 50 karaktera.")
        
    loc_id = get_or_create_location_id(grad)
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        UPDATE Troskovi 
        SET naziv=?, iznos=?, tip=?, namjena=?, lokacija_id=?
        WHERE id=?
    ''', (naziv, float(iznos), tip, namjena, loc_id, trosak_id))
    conn.commit()
    conn.close()

def obrisi_trosak_db(trosak_id):
    # Brisanje troška
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM Troskovi WHERE id=?", (trosak_id,))
    conn.commit()
    conn.close()

# Statistike za tačke e) i f)
def top_lokacije(limit=5, min_ponavljanja=0):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    # SQL upit za brojanje i grupisanje
    query = '''
        SELECT L.naziv, COUNT(T.id) as br
        FROM Troskovi T
        JOIN Lokacije L ON T.lokacija_id = L.id
        GROUP BY L.naziv
        HAVING br > ?
        ORDER BY br DESC
        LIMIT ?
    '''
    cursor.execute(query, (min_ponavljanja, limit))
    podaci = cursor.fetchall()
    conn.close()
    return podaci

def filtriraj_troskove(tip=None, namjena=None):
    # Filtriranje
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    query = '''
        SELECT T.id, T.naziv, T.iznos, T.tip, T.namjena, L.naziv 
        FROM Troskovi T
        JOIN Lokacije L ON T.lokacija_id = L.id
        WHERE 1=1
    '''
    params = []
    if tip:
        query += " AND T.tip = ?"
        params.append(tip)
    if namjena and namjena != "Sve":
        query += " AND T.namjena = ?"
        params.append(namjena)
        
    cursor.execute(query, params)
    podaci = cursor.fetchall()
    conn.close()
    return podaci

# Inicijalizuj bazu pri pokretanju
init_db()