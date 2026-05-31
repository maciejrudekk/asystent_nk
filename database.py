import sqlite3
import os
import sys
import platform
from pathlib import Path

class DatabaseManager:
    def __init__(self, db_name="asystent_nk.db"):
        # Obsługa ścieżek na Androidzie
        if platform.system() == "Linux" and os.path.exists("/proc/version") and "Android" in open("/proc/version").read():
            # Na Androidzie zapisuj w app storage
            db_dir = Path.home() / "asystent_nk"
            db_dir.mkdir(parents=True, exist_ok=True)
            db_path = db_dir / db_name
        else:
            # Na innych platformach użyj obecnego katalogu
            db_path = Path.cwd() / db_name
        
        self.conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self.init_db()

    def init_db(self):
        # Tabela teczek
        self.conn.execute('''CREATE TABLE IF NOT EXISTS Teczki 
            (id INTEGER PRIMARY KEY, nr_jed TEXT, data_wszczecia TEXT, ma_bron INTEGER,
             jest_zolnierzem INTEGER, nkb_przekazane INTEGER, sprawca_nieletni INTEGER,
             ofiara_maloletnia INTEGER, policjant INTEGER, nakaz_zakaz_policja INTEGER,
             nakaz_zakaz_sad INTEGER, zatrzymany_bron INTEGER, czestotliwosc_kontroli INTEGER,
             nr_nakazu TEXT)''')
        # Tabela historii wizyt/kontroli
        self.conn.execute('''CREATE TABLE IF NOT EXISTS Historia 
            (id INTEGER PRIMARY KEY, teczka_id INTEGER, data TEXT, typ TEXT)''')
        self.conn.commit()
        # jeśli starsza tabela istnieje bez kolumny nr_nakazu, spróbuj ją dodać
        try:
            self.conn.execute("ALTER TABLE Teczki ADD COLUMN nr_nakazu TEXT")
            self.conn.commit()
        except Exception:
            # kolumna może już istnieć lub nie można jej dodać — ignoruj
            pass

    def zapisz_teczke(self, nr, data, ma_bron, jest_zolnierzem, nkb_przekazane, 
                      sprawca_nieletni, ofiara_maloletnia, policjant, nakaz_policja, nakaz_sad, zatrzymany_bron, czestotliwosc, nr_nakazu=None):
        self.conn.execute('''INSERT INTO Teczki VALUES (NULL, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''', 
            (nr, data, int(ma_bron), int(jest_zolnierzem), int(nkb_przekazane), int(sprawca_nieletni), 
             int(ofiara_maloletnia), int(policjant), int(nakaz_policja), int(nakaz_sad), int(zatrzymany_bron), int(czestotliwosc), nr_nakazu))
        self.conn.commit()

    def dodaj_wpis_historii(self, teczka_id, data, typ):
        self.conn.execute("INSERT INTO Historia VALUES (NULL, ?, ?, ?)", (teczka_id, data, typ))
        self.conn.commit()

    def pobierz_historie(self, teczka_id):
        return self.conn.execute("SELECT data, typ FROM Historia WHERE teczka_id = ? ORDER BY data DESC", (teczka_id,)).fetchall()

    def pobierz_wszystkie(self):
        return self.conn.execute("SELECT * FROM Teczki").fetchall()
    
    def usun_teczke(self, id):
        self.conn.execute("DELETE FROM Teczki WHERE id = ?", (id,))
        self.conn.execute("DELETE FROM Historia WHERE teczka_id = ?", (id,))
        self.conn.commit()

    def aktualizuj_wizyte(self, teczka_id, data):
        # dodajemy wpis do historii typu 'wizyta'
        self.dodaj_wpis_historii(teczka_id, data, 'wizyta')

    def aktualizuj_kontrole(self, teczka_id, data):
        # dodajemy wpis do historii typu 'kontrola'
        self.dodaj_wpis_historii(teczka_id, data, 'kontrola')

    def close(self):
        try:
            self.conn.close()
        except Exception:
            pass

    def ustaw_nakaz(self, teczka_id, nakaz_policja, nakaz_sad, czestotliwosc, nr_nakazu=None):
        # aktualizuj także numer nakazu, jeśli podano
        if nr_nakazu is not None:
            self.conn.execute('''UPDATE Teczki 
                SET nakaz_zakaz_policja = ?, nakaz_zakaz_sad = ?, czestotliwosc_kontroli = ?, nr_nakazu = ? 
                WHERE id = ?''', (int(nakaz_policja), int(nakaz_sad), int(czestotliwosc), nr_nakazu, teczka_id))
        else:
            self.conn.execute('''UPDATE Teczki 
                SET nakaz_zakaz_policja = ?, nakaz_zakaz_sad = ?, czestotliwosc_kontroli = ? 
                WHERE id = ?''', (int(nakaz_policja), int(nakaz_sad), int(czestotliwosc), teczka_id))
        self.conn.commit()

    def pobierz_teczke(self, teczka_id):
        return self.conn.execute("SELECT * FROM Teczki WHERE id = ?", (teczka_id,)).fetchone()