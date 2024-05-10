import configparser
import os

# Funktion zum Überprüfen, ob die Konfigurationsdatei existiert und zum Erstellen, falls nicht
def erstelle_db_cfg_wenn_nicht_vorhanden():
    # Pfad zur Konfigurationsdatei
    config_datei_pfad = 'db.cfg'
    
    # Überprüfen, ob die Datei bereits existiert
    if not os.path.isfile(config_datei_pfad):
        # Erstellen einer neuen Konfigurationsdatei
        config = configparser.ConfigParser()
        config['mysql_database'] = {
            'host': 'localhost',
            'database': 'deine_datenbank',
            'user': 'dein_benutzer',
            'password': 'dein_passwort'
        }
        # Schreiben der Konfigurationsdaten in die Datei
        with open(config_datei_pfad, 'w') as configdatei:
            config.write(configdatei)
        print(f"Die Datei {config_datei_pfad} wurde erstellt.")
    else:
        print(f"Die Datei {config_datei_pfad} existiert bereits.")

# Funktion zum Laden der Konfigurationsdaten
def lade_konfiguration():
    config = configparser.ConfigParser()
    config.read('db.cfg')
    return config['mysql_database']
