# Asystent NK Dzielnicowego

System wspomagania dzielnicowego w postępowaniu z procedurą Niebieskiej Karty oraz nakazami/zakazami w sprawach przemocy domowej.

## Funkcjonalności

- 📋 Kreator nowych teczek zagadnieniowych (NK)
- 📅 Zarządzanie terminami wizyt i kontroli nakazu/zakazu
- 📊 Monitorowanie procedur i historii interwencji
- 📖 Wytyczne proceduralne (Wytyczne nr 3 KGP)
- 💾 Baza SQLite do przechowywania danych
- 📱 Responsywny interfejs Flet (web, desktop, mobile)

## Technologia

- **Python 3.11+**
- **Flet** - framework UI (cross-platform)
- **SQLite3** - baza danych
- **Buildozer** - kompilacja Android APK

## Instalacja i uruchomienie (lokalne)

### Wymagania
- Python 3.11+
- pip

### Kroki

1. Sklonuj repo:
```bash
git clone https://github.com/your-username/asystent-nk.git
cd asystent-nk
```

2. Zainstaluj zależności:
```bash
pip install flet sqlite3
```

3. Uruchom aplikację:
```bash
python main.py
```

Aplikacja będzie dostępna pod adresem `http://localhost:8550`

## Budowa APK dla Androida

### Opcja 1: GitHub Actions (automatyczna)

1. Wgraj repo na GitHub
2. GitHub Actions automatycznie zbuduje APK na każdy push do `main`
3. Pobierz APK z sekcji `Artifacts` w workflow runs

### Opcja 2: Lokalna budowa (wymaga zasobów)

Wymagania:
- Java JDK 11+
- Android SDK
- Android NDK
- Gradle

Polecenie:
```bash
pip install buildozer cython
buildozer android debug
```

Gotowy APK będzie w `bin/` katalogu.

## Struktura projektu

```
asystent-nk/
├── main.py                 # Główna aplikacja Flet
├── database.py            # Menedżer bazy danych SQLite
├── models.py              # Modele danych (TeczkaNK, Zadanie)
├── buildozer.spec         # Konfiguracja Buildozera
├── .github/workflows/     # GitHub Actions workflows
└── wytyczne_nr3_KGP.pdf   # Wytyczne proceduralne
```

## API bazy danych

### DatabaseManager

```python
db = DatabaseManager()

# Zapisz teczkę
db.zapisz_teczke(nr_jed, data_wszczecia, ma_bron, jest_zolnierzem, ...)

# Pobierz teczkę
row = db.pobierz_teczke(id)

# Ustaw nakaz/zakaz
db.ustaw_nakaz(id, nakaz_policja, nakaz_sad, czestotliwosc, nr_nakazu)

# Pobierz historię
historia = db.pobierz_historie(id)

# Zamknij bazę
db.close()
```

## Wytyczne

Aplikacja zawiera pełne wytyczne proceduralne:
- Kiedy wszcząć procedurę Niebieska Karta
- Co sprawdzić na początku
- Dokumenty w teczce
- Nakaz/zakaz
- Wnioski do GOPS i Komisji Alkoholowych

Wytyczne są zintegrowane w sekcji "Pomoce" aplikacji.

## Licencja

Projekt stworzony dla Polskiej Policji — zainteresowanych dzielnicowych.

## Autor

Asystent Dzielnicowego v1.0.0

---

**Uwaga**: Aplikacja zawiera dane wrażliwe związane z procedurami policyjnymi. Należy chronić dostęp do zainstalowanej aplikacji i bazy danych.
