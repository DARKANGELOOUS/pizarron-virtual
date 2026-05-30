import sqlite3

def conectar_db():
    # Usamos pizarron_v3.db para iniciar limpios y probar la nueva estructura
    conn = sqlite3.connect('pizarron_v3.db', timeout=15)
    # Magia de concurrencia: Activa el Write-Ahead Logging
    conn.execute('PRAGMA journal_mode=WAL;')
    return conn

def init_db():
    conn = conectar_db()
    c = conn.cursor()
    # Agregamos owner_email para la seguridad y trazabilidad de cada alumno
    c.execute('''CREATE TABLE IF NOT EXISTS trazos
                 (id TEXT PRIMARY KEY, data TEXT, owner_email TEXT)''')
    conn.commit()
    conn.close()