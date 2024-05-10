# Importieren der notwendigen Bibliotheken
import tkinter as tk
from tkinter import ttk, simpledialog, messagebox
import sqlite3
from mysql.connector import Error
import configparser
import mysql.connector
from abfragen import (tabelleninhalte, primaerschluessel_abfrage, 
                      fremdschluessel_abfrage, zaehle_eintraege, 
                      spalten_datentypen_abfrage, tabelle_in_Megabyte_abfrage)

# Globale Variablen für das aktuelle Datenbankschema und die aktuelle Datenbank
aktuelles_datenbankschema = None
aktuelle_datenbank = None
listbox = None  # Wird später initialisiert

# Hauptfenster der Anwendung erstellen
root = tk.Tk()
root.title("Datenbankabfragen")

# Tabellenansicht für die Ergebnisse initialisieren
tabellenbox = ttk.Treeview(root, show='headings')
tabellenbox.grid(row=0, column=0, columnspan=3, sticky='nsew')

# Spalten für die Tabellenansicht definieren
tabellenbox['columns'] = ('Spalte1', 'Spalte2', 'Spalte3')

# Spaltenkonfiguration
tabellenbox.column('#0', width=0, stretch=tk.NO)
tabellenbox.column('Spalte1', anchor=tk.CENTER, width=80)
tabellenbox.column('Spalte2', anchor=tk.W, width=120)
tabellenbox.column('Spalte3', anchor=tk.W, width=120)

# Spaltenüberschriften
tabellenbox.heading('#0', text='', anchor=tk.CENTER)
tabellenbox.heading('Spalte1', text='ID', anchor=tk.CENTER)
tabellenbox.heading('Spalte2', text='Name', anchor=tk.W)
tabellenbox.heading('Spalte3', text='Wert', anchor=tk.W)

# Beispiel-Daten in die Tabellenansicht einfügen
tabellenbox.insert("", index='end', iid=0, text='', values=('1', 'arbeitsmarktstatistik', '123'))
tabellenbox.insert("", index='end', iid=1, text='', values=('2', 'frueheresbundesgebiet', '456'))
tabellenbox.insert("", index='end', iid=2, text='', values=('3', 'neuelaender', '789'))

# Eingabefeld für SQL-Abfragen
eingabe_label = tk.Label(root, text="SQL-Abfrage:")
eingabe_label.grid(row=1, column=0, sticky='w')
eingabe = tk.Text(root, width=50, height=20)
eingabe.grid(row=1, column=1, pady=(0, 20), sticky='e')

# Funktion zum Lesen der Datenbankkonfiguration aus der db.cfg Datei
def datenbank_config_laden():
    config = configparser.ConfigParser()
    config.read('db.cfg')
    return {
        'host': config['mysql_database']['host'],
        'database': config['mysql_database']['database'],
        'user': config['mysql_database']['user'],
        'password': config['mysql_database']['password']
    }

# Funktion zum Herstellen einer Verbindung zur Datenbank
def verbinde_zur_datenbank():
    db_config = datenbank_config_laden()
    try:
        conn = mysql.connector.connect(
            host=db_config['host'],
            database=db_config['database'],
            user=db_config['user'],
            password=db_config['password']
        )
        return conn
    except mysql.connector.Error as e:
        messagebox.showerror("Datenbankverbindungsfehler", f"Fehler bei der Verbindung zur Datenbank: {e}")
        return None

# Funktion zum Aktualisieren der Datenbankkonfiguration in der db.cfg Datei
def datenbank_konfiguration_aktualisieren(ausgewaehlte_datenbank):
    config = configparser.ConfigParser()
    config.read('db.cfg')
    config.set('mysql_database', 'database', ausgewaehlte_datenbank)
    with open('db.cfg', 'w') as configfile:
        config.write(configfile) 

# Funktion zum Nutzen der ausgewählten Datenbank
def datenbank_nutzen(event):
    global aktuelles_datenbankschema
    auswahl_index = listbox.curselection()
    if auswahl_index:
        aktuelles_datenbankschema = listbox.get(auswahl_index[0])
        datenbank_konfiguration_aktualisieren(aktuelles_datenbankschema)
        messagebox.showinfo("Datenbank ausgewählt", f"Die Datenbank '{aktuelles_datenbankschema}' wird jetzt genutzt.")

# Funktion zum Auflisten aller Datenbanken
def datenbanken_auflisten():
    global listbox
    conn = verbinde_zur_datenbank()
    if conn is not None:
        cursor = conn.cursor()
        cursor.execute("SHOW DATABASES")
        datenbanken_fenster = tk.Toplevel(root)
        datenbanken_fenster.title("Verfügbare Datenbanken")
        listbox = tk.Listbox(datenbanken_fenster)
        listbox.pack(fill=tk.BOTH, expand=True)
        for db in cursor:
            listbox.insert(tk.END, db[0])
        cursor.close()
        conn.close()
        listbox.bind('<Double-1>', datenbank_nutzen) 

# Funktion zum Ausführen von Abfragen und Anzeigen der Ergebnisse
def abfrage_durchfuehren(abfrage=None):
    # Wenn keine Abfrage übergeben wurde, wird die Abfrage aus dem Eingabefeld geholt
    if abfrage is None:
        abfrage = eingabe.get("1.0", "end-1c")
    # Verbindung zur Datenbank herstellen
    conn = verbinde_zur_datenbank()
    # Nur fortfahren, wenn die Verbindung erfolgreich war
    if conn is not None:
        cursor = conn.cursor()
        try:
            # Die Abfrage ausführen
            cursor.execute(abfrage)
            # Überprüfen, ob das cursor.description-Attribut nicht None ist
            if cursor.description:
                spalten = [beschreibung[0] for beschreibung in cursor.description]
                tabellenbox['columns'] = spalten
                tabellenbox.delete(*tabellenbox.get_children())
                for spalte in spalten:
                    tabellenbox.heading(spalte, text=spalte)
                    tabellenbox.column(spalte, width=100, stretch=True)
                ergebnisse = cursor.fetchall()
                for ergebnis in ergebnisse:
                    tabellenbox.insert("", "end", values=ergebnis)
            else:
                messagebox.showinfo("Information", "Die Abfrage lieferte keine Ergebnisse.")
        except mysql.connector.Error as e:
            messagebox.showerror("Abfragefehler", f"Fehler bei der Ausführung der Abfrage: {e}")
        finally:
            # Ressourcen freigeben
            cursor.close()
            conn.close()   

 # Funktion zum Speichern einer Abfrage
def abfrage_speichern():
    titel = simpledialog.askstring("Titel", "Gib einen Titel für die Abfrage ein:")  # Dialog zum Eingeben des Titels
    kommentar = simpledialog.askstring("Kommentar", "Gib einen Kommentar für die Abfrage ein:")  # Dialog zum Eingeben des Kommentars
    abfrage = eingabe.get("1.0", "end-1c")  # Abfrage aus dem Eingabefeld holen
    if titel and abfrage:  # Überprüfen, ob Titel und Abfrage eingegeben wurden
        conn = sqlite3.connect('abfragen.db')  # Verbindung zur SQLite-Datenbank herstellen
        cursor = conn.cursor()  # Cursor-Objekt erstellen
        # SQL-Befehl zum Einfügen der neuen Abfrage in die Tabelle
        cursor.execute('INSERT INTO gespeicherte_abfragen (titel, kommentar, abfrage) VALUES (?, ?, ?)', (titel, kommentar, abfrage))
        conn.commit()  # Änderungen in der Datenbank speichern
        conn.close()  # Verbindung zur Datenbank schließen
        messagebox.showinfo("Gespeichert", "Die Abfrage wurde gespeichert.")  # Bestätigung anzeigen
    else:     # Ralf Krümmel
        messagebox.showwarning("Fehler", "Titel und Abfrage müssen eingegeben werden.")  # Fehlermeldung anzeigen

# Button zum Speichern der Abfrage
speichern_button = tk.Button(root, text="Abfrage speichern", command=abfrage_speichern)
speichern_button.grid(row=2, column=2, pady=(0, 20), sticky='w')
             # Ralf Krümmel
# Funktion zum Anzeigen gespeicherter Abfragen mit Rechtsklick-Funktionalität
def gespeicherte_abfragen_anzeigen():
    neues_fenster = tk.Toplevel(root)  # Neues Fenster erstellen
    neues_fenster.title("Gespeicherte Abfragen")  # Titel des neuen Fensters setzen
    listbox = tk.Listbox(neues_fenster)  # Listbox für die gespeicherten Abfragen erstellen
    listbox.pack(fill=tk.BOTH, expand=True)  # Listbox im neuen Fenster platzieren
           # Ralf Krümmel
    # Kontextmenü für Rechtsklick hinzufügen
    kontextmenue = tk.Menu(neues_fenster, tearoff=0)  # Kontextmenü erstellen
    def kontextmenue_oeffnen(event): # Ralf Krümmel
        listbox = event.widget  # Listbox, in der das Ereignis aufgetreten ist
        auswahl_index = listbox.nearest(event.y)  # Index des Eintrags, der am nächsten zur Mausposition ist
        if auswahl_index is not None:  # Überprüfen, ob ein Eintrag ausgewählt wurde
            listbox.selection_set(auswahl_index)  # Den ausgewählten Eintrag markieren
            auswahl_id = listbox.get(auswahl_index).split(' - ')[0]  # ID des ausgewählten Eintrags holen
            kontextmenue.entryconfigure("Kommentar anzeigen", command=lambda: kommentar_anzeigen(auswahl_id))  # Kontextmenü-Eintrag konfigurieren
            kontextmenue.post(event.x_root, event.y_root)  # Kontextmenü an der Mausposition anzeigen

    listbox.bind('<Button-3>', kontextmenue_oeffnen)  # Ereignis für Rechtsklick binden

    kontextmenue.add_command(label="Kommentar anzeigen")  # Eintrag zum Anzeigen des Kommentars hinzufügen
             # Ralf Krümmel
    # Funktion zum Anzeigen des Kommentars einer gespeicherten Abfrage
    def kommentar_anzeigen(auswahl_id):
        conn = sqlite3.connect('abfragen.db')  # Verbindung zur SQLite-Datenbank herstellen
        cursor = conn.cursor()  # Cursor-Objekt erstellen
        cursor.execute('SELECT kommentar FROM gespeicherte_abfragen WHERE id = ?', (auswahl_id,))  # SQL-Befehl zum Holen des Kommentars
        kommentar = cursor.fetchone()[0]  # Kommentar aus dem Ergebnis holen
        messagebox.showinfo("Kommentar", kommentar if kommentar else "Kein Kommentar vorhanden.")  # Nachrichtenbox mit dem Kommentar anzeigen
        conn.close()  # Verbindung zur Datenbank schließen
               # Ralf Krümmel
    # Funktion zum Ausführen einer ausgewählten Abfrage
    def abfrage_ausfuehren(event):
        auswahl_index = listbox.curselection()  # Index des ausgewählten Eintrags holen
        if auswahl_index:  # Überprüfen, ob ein Eintrag ausgewählt wurde
            auswahl_id = listbox.get(auswahl_index[0]).split(' - ')[0]  # ID des ausgewählten Eintrags holen
            conn = sqlite3.connect('abfragen.db')  # Verbindung zur SQLite-Datenbank herstellen
            cursor = conn.cursor()  # Cursor-Objekt erstellen
            cursor.execute('SELECT abfrage FROM gespeicherte_abfragen WHERE id = ?', (auswahl_id,))  # SQL-Befehl zum Holen der Abfrage
            abfrage = cursor.fetchone()[0]  # Abfrage aus dem Ergebnis holen
            conn.close()  # Verbindung zur Datenbank schließen
            eingabe.delete("1.0", "end")  # Eingabefeld leeren
            eingabe.insert("1.0", abfrage)  # Abfrage in das Eingabefeld einfügen
            abfrage_durchfuehren()  # Ausgewählte Abfrage ausführen

    listbox.bind('<Double-1>', abfrage_ausfuehren)  # Ereignis für Doppelklick binden
      # Ralf Krümmel
  # Laden der gespeicherten Abfragen in die Listbox und Ermittlung der maximalen Titellänge
    conn = sqlite3.connect('abfragen.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, titel FROM gespeicherte_abfragen')
    max_titel_laenge = 0
    for row in cursor.fetchall():
        listbox.insert(tk.END, f"{row[0]} - {row[1]}")
        max_titel_laenge = max(max_titel_laenge, len(row[1]))
    conn.close()
    
    # Fenstergröße an den längsten Titel anpassen
    neues_fenster.geometry(f"{max_titel_laenge * 7 + 20}x200")  # Die Breite wird basierend auf der maximalen Titellänge gesetzt
 
# Kontextmenü erstellen
kontextmenue = tk.Menu(root, tearoff=0)

def kontextmenue_befuellen(tabelle, spalten, datenbankschema):
    kontextmenue.delete(0, tk.END)  # Vorherige Einträge löschen
    # Fügen Sie die Abfragen aus der abfragen.py zum Kontextmenü hinzu
    kontextmenue.add_command(label="Tabelleninhalt komplett", command=lambda: abfrage_durchfuehren(tabelleninhalte(tabelle)))
    kontextmenue.add_command(label="Primärschlüssel anzeigen", command=lambda: abfrage_durchfuehren(primaerschluessel_abfrage(tabelle)))
    kontextmenue.add_command(label="Fremdschlüssel anzeigen", command=lambda: abfrage_durchfuehren(fremdschluessel_abfrage(tabelle)))
    kontextmenue.add_command(label="Anzahl der Tabellen Einträge", command=lambda: abfrage_durchfuehren(zaehle_eintraege(tabelle)))
    kontextmenue.add_command(label="Datentypen anzeigen", command=lambda: abfrage_durchfuehren(spalten_datentypen_abfrage(tabelle)))
    kontextmenue.add_command(label="Größe in MB anzeigen", command=lambda: abfrage_durchfuehren(tabelle_in_Megabyte_abfrage(aktuelles_datenbankschema, tabelle)))
def kontextmenue_oeffnen(event):
    item = event.widget.item(event.widget.focus())
    if 'values' in item and len(item['values']) > 0:
        tabelle = item['values'][0]  # ID der Abfrage aus dem ausgewählten Item holen
        spalten = item['values'][1:]  # Spalten aus dem ausgewählten Item holen
        kontextmenue_befuellen(tabelle, spalten, aktuelles_datenbankschema)  # Kontextmenü mit Funktionen befüllen
        kontextmenue.tk_popup(event.x_root, event.y_root)  # Kontextmenü anzeigen
    else:
        messagebox.showwarning("Warnung", "Kein Tabelleneintrag ausgewählt.")

 # Binden Sie die Funktion kontextmenue_oeffnen an die Tabellenbox
tabellenbox.bind('<Button-3>', kontextmenue_oeffnen)  # Für Windows
 # Funktion zum Speichern der Konfiguration in der db.cfg Datei
def konfiguration_speichern(host, database, user, password, fenster):
    config = configparser.ConfigParser()
    config['mysql_database'] = {
        'host': host,
        'database': database,
        'user': user,
        'password': password
    }
    with open('db.cfg', 'w') as configfile:
        config.write(configfile)
    messagebox.showinfo("Erfolg", "Die Konfiguration wurde gespeichert.")
    fenster.destroy()  # Schließt das Konfigurationsfenster

# Funktion zum Öffnen des Konfigurationsfensters
def konfigurationsfenster_oeffnen():
    konfig_fenster = tk.Toplevel(root)
    konfig_fenster.title("Datenbankkonfiguration")

    # Eingabefelder für die Konfiguration
    tk.Label(konfig_fenster, text="Host:").grid(row=0, column=0)
    host_entry = tk.Entry(konfig_fenster)
    host_entry.grid(row=0, column=1)

    tk.Label(konfig_fenster, text="Datenbank:").grid(row=1, column=0)
    database_entry = tk.Entry(konfig_fenster)
    database_entry.grid(row=1, column=1)

    tk.Label(konfig_fenster, text="Benutzer:").grid(row=2, column=0)
    user_entry = tk.Entry(konfig_fenster)
    user_entry.grid(row=2, column=1)

    tk.Label(konfig_fenster, text="Passwort:").grid(row=3, column=0)
    password_entry = tk.Entry(konfig_fenster, show="*")
    password_entry.grid(row=3, column=1)

     # Button zum Speichern der Konfiguration
    speichern_button = tk.Button(konfig_fenster, text="Speichern", command=lambda: konfiguration_speichern(
        host_entry.get(),
        database_entry.get(),
        user_entry.get(),
        password_entry.get(),
        konfig_fenster  # Übergibt das Fenster als Argument an die Funktion
    ))
    speichern_button.grid(row=4, column=0, columnspan=2)

# Button zum Ausführen der Abfrage
abfrage_button = tk.Button(root, text="Abfrage ausführen", command=abfrage_durchfuehren)
abfrage_button.grid(row=1, column=2, pady=(0, 20), sticky='w')


# Button zum Auflisten der Datenbanken
button = tk.Button(root, text="Datenbanken auflisten", command=datenbanken_auflisten)
button.grid(row=3, column=0, sticky='w')

# Button zum Öffnen des Konfigurationsfensters
konfig_button = tk.Button(root, text="Datenbankkonfiguration", command=konfigurationsfenster_oeffnen)
konfig_button.grid(row=3, column=1, sticky='w')

# Ereignisbindung für Rechtsklick
tabellenbox.bind("<Button-3>", kontextmenue_oeffnen)

# Button zum Speichern der Abfrage
speichern_button = tk.Button(root, text="Abfrage speichern", command=abfrage_speichern)
speichern_button.grid(row=2, column=2, pady=(0, 20), sticky='w')

# Button zum Anzeigen gespeicherter Abfragen
anzeigen_button = tk.Button(root, text="Gespeicherte Abfragen anzeigen", command=gespeicherte_abfragen_anzeigen)
anzeigen_button.grid(row=3, column=2, sticky='w')

root.mainloop()  # Hauptfenster starten
