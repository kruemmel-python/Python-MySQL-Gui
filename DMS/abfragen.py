# abfragen.py

# Beispiel für eine Funktion, die eine Standardabfrage für eine Tabelle ausführt
def tabelleninhalte(tabelle):
    # Erstellt eine Abfrage basierend auf dem Namen der Tabelle
    abfrage = f"SELECT * FROM {tabelle}"
    return abfrage



# Beispiel für eine Funktion, die eine Standardabfrage für eine andere Tabelle ausführt
def primaerschluessel_abfrage(tabelle):
    abfrage = f"SELECT column_name FROM information_schema.key_column_usage WHERE table_name = '{tabelle}' AND constraint_name = 'PRIMARY'"
    return abfrage

def fremdschluessel_abfrage(tabelle):
    abfrage = f"SELECT CONSTRAINT_NAME, TABLE_NAME, COLUMN_NAME, REFERENCED_TABLE_NAME, REFERENCED_COLUMN_NAME FROM information_schema.key_column_usage WHERE REFERENCED_TABLE_NAME = '{tabelle}'"
    return abfrage

def spalten_datentypen_abfrage(tabelle):
    abfrage = f"SELECT COLUMN_NAME, DATA_TYPE FROM information_schema.columns WHERE table_name = '{tabelle}'"
    return abfrage

def zaehle_eintraege(tabelle):
    abfrage = f"SELECT COUNT(*) FROM {tabelle}"
    return abfrage

def erstelle_tabelle(name, spalten):
    # Erstellt eine Tabelle mit dem gegebenen Namen und den Spalten
    abfrage = f"CREATE TABLE {name} ("
    abfrage += ", ".join([f"{spalte[0]} {spalte[1]}" for spalte in spalten])
    abfrage += ")"
    return abfrage

def erstelle_datenbank(name):
    # Erstellt eine Datenbank mit dem gegebenen Namen
    return f"CREATE DATABASE {name}"

def erstelle_index(tabelle, spalten):
    # Erstellt einen Index für die gegebenen Spalten auf der angegebenen Tabelle
    index_name = "_".join(spalten) + "_index"
    abfrage = f"CREATE INDEX {index_name} ON {tabelle} ("
    abfrage += ", ".join(spalten)
    abfrage += ")"
    return abfrage
def tabelle_in_Megabyte_abfrage(datenbankschema, tabelle):
    abfrage = f"""SELECT table_name AS 'Tabelle', ROUND(((data_length + index_length) / 1024 / 1024), 2) AS 'Größe in MB' FROM information_schema.TABLES WHERE table_schema = '{datenbankschema}' AND table_name = '{tabelle}';"""
    return abfrage