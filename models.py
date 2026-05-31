from datetime import datetime, timedelta

class Zadanie:
    def __init__(self, nazwa, podstawa_prawna):
        self.nazwa = nazwa
        self.podstawa_prawna = podstawa_prawna

class TeczkaNK:
    def __init__(self, row, historia):
        # Rozpakuj wiersz i przypisz wszystkie pola do atrybutów instancji
        (self.id, self.nr_jed, data_wsz, ma_bron, jest_zolnierzem,
         nkb_przekazane, sprawca_nieletni, ofiara_maloletnia,
         policjant, self.nakaz_policja, self.nakaz_sad, zatrzymany_bron, self.czestotliwosc, nr_nakazu) = row

        self.nkb_przekazane = bool(nkb_przekazane)
        self.sprawca_nieletni = bool(sprawca_nieletni)
        self.ofiara_maloletnia = bool(ofiara_maloletnia)
        self.policjant = policjant
        self.zatrzymany_bron = bool(zatrzymany_bron)

        self.ma_bron = bool(ma_bron)
        self.jest_zolnierzem = bool(jest_zolnierzem)
        self.nakaz_zakaz = bool(self.nakaz_policja or self.nakaz_sad)

        self.nr_nakazu = nr_nakazu

        self.data_wsz = datetime.strptime(data_wsz, "%Y-%m-%d") if data_wsz else None
        self.historia = historia or []
        self.data_ostatniej_wizyty = self._pobierz_ostatnia("wizyta")
        self.data_ostatniej_kontroli = self._pobierz_ostatnia("kontrola")

    def _pobierz_ostatnia(self, typ):
        wpisy = [datetime.strptime(h[0], "%Y-%m-%d") for h in self.historia if len(h) >= 2 and h[1] == typ and h[0]]
        return max(wpisy) if wpisy else None

    def oblicz_termin_wizyty(self):
        if self.data_ostatniej_wizyty:
            termin = self.data_ostatniej_wizyty + timedelta(days=30)
        elif self.data_wsz:
            termin = self.data_wsz + timedelta(days=5)
        else:
            return None
        return termin.strftime("%Y-%m-%d")

    def oblicz_termin_kontroli(self):
        if not self.nakaz_zakaz:
            return None
        if self.data_ostatniej_kontroli:
            termin = self.data_ostatniej_kontroli + timedelta(days=self.czestotliwosc)
        elif self.data_wsz:
            termin = self.data_wsz + timedelta(days=self.czestotliwosc)
        else:
            return None
        return termin.strftime("%Y-%m-%d")

    def dni_do_wizyty(self):
        termin = self.oblicz_termin_wizyty()
        if not termin:
            return None
        return (datetime.strptime(termin, "%Y-%m-%d") - datetime.now()).days

    def dni_do_kontroli(self):
        if not self.nakaz_zakaz:
            return None
        termin = self.oblicz_termin_kontroli()
        if not termin:
            return None
        return (datetime.strptime(termin, "%Y-%m-%d") - datetime.now()).days

    # TO JEST METODA, KTÓREJ BRAKOWAŁO:
    def pobierz_liste_zadan(self):
        zadania = []
        zadania.append(Zadanie("Założenie teczki zagadnieniowej", "Wytyczne nr 3, Rozdział 3, § 14"))
        
        if self.nakaz_zakaz:
            zadania.append(Zadanie("Kontrola przestrzegania nakazu/zakazu", "Wytyczne nr 3, Rozdział 3, § 17"))
            
        if self.ma_bron:
            zadania.append(Zadanie("Powiadomienie WPA o posiadaniu broni", "Wytyczne nr 3, Rozdział 2, § 12"))
            
        return zadania