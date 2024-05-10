import sqlite3
from mysql.connector import connect, Error
from config_handler import lade_konfiguration
from tkinter import messagebox

# Funktion zum Initialisieren der SQLite-Datenbank und Erstellen der Tabelle für gespeicherte Abfragen
def datenbank_initialisieren():
    conn = sqlite3.connect('abfragen.db')  # Verbindung zur SQLite-Datenbank herstellen
    cursor = conn.cursor()  # Cursor-Objekt erstellen
    # SQL-Befehl zum Erstellen der Tabelle, falls sie noch nicht existiert
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS gespeicherte_abfragen (
            id INTEGER PRIMARY KEY,
            titel TEXT NOT NULL,
            kommentar TEXT,
            abfrage TEXT NOT NULL
        )
    ''')
    conn.commit()  # Änderungen in der Datenbank speichern
    conn.close()  # Verbindung zur Datenbank schließen

# Funktion zum Herstellen einer Verbindung zur MySQL-Datenbank
def verbinde_zur_datenbank():
    db_config = lade_konfiguration()
    try:
        conn = connect(
            host=db_config['host'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        if conn.is_connected():
            return conn
    except Error as e:
        if 'Unknown database' in str(e):
            messagebox.showerror("Datenbankfehler", "Fehler: Die angegebene Datenbank existiert nicht.")
        else:
            messagebox.showerror("Verbindungsfehler", f"Fehler bei der Verbindung zur MySQL-Datenbank: {e}")
        return None