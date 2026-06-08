import flet as ft
from datetime import datetime, timedelta
from pathlib import Path
import os
import sys
import platform
from database import DatabaseManager
from models import TeczkaNK

def main(page: ft.Page):
    page.title = "Asystent NK Dzielnicowego"
    page.scroll = "adaptive"
    page.horizontal_alignment = ft.CrossAxisAlignment.CENTER 
    
    # WYMUSZENIE JĘZYKA POLSKIEGO W CAŁEJ APLIKACJI (W TYM KALENDARZU)
    if hasattr(ft, 'LocaleConfiguration'):
        page.locale_configuration = ft.LocaleConfiguration(
            supported_locales=[ft.Locale("pl", "PL")],
            current_locale=ft.Locale("pl", "PL")
        )

    db = DatabaseManager()
    # helper do wyświetlania komunikatów
    def show_snack(msg, color=None):
        sb = ft.SnackBar(ft.Text(msg))
        if color:
            sb.bgcolor = color
        page.snack_bar = sb
        page.snack_bar.open = True
        page.update()

    # zamknięcie DB przy zamykaniu strony
    def _on_close(e):
        try:
            db.close()
        except Exception:
            pass

    page.on_close = _on_close
    
    wybrana_teczka_id = None
    tryb_kalendarza = None 
    
    # === MAGIA PRZYCISKU WSTECZ (Android) ===
    def systemowy_przycisk_wstecz(e):
        """Obsługuje przycisk wstecz na Androidzie"""
        if len(page.views) > 1:
            page.views.pop()
            page.update()
    
    # Podpinamy event dla przycisku wstecz
    page.on_view_pop = systemowy_przycisk_wstecz

    # --- WSPÓLNY KALENDARZ ---
    def na_zmiane_daty(e):
        nonlocal wybrana_teczka_id, tryb_kalendarza
        if e.control.value and wybrana_teczka_id is not None:
            skorygowana_data = e.control.value + timedelta(hours=12)
            wybrana_data = skorygowana_data.strftime("%Y-%m-%d")
            
            if tryb_kalendarza == "wizyta":
                db.aktualizuj_wizyte(wybrana_teczka_id, wybrana_data)
            elif tryb_kalendarza == "kontrola":
                db.aktualizuj_kontrole(wybrana_teczka_id, wybrana_data)
                
            date_picker.open = False
            page.update()
            pokaz_aktywne()

    # POLSKIE ETYKIETY PRZYCISKÓW W KALENDARZU
    date_picker = ft.DatePicker(
        on_change=na_zmiane_daty,
        help_text="WYBIERZ DATĘ WYKONANIA CZYNNOŚCI",
        cancel_text="ANULUJ",
        confirm_text="ZAPISZ",
        error_format_text="Nieprawidłowy format daty",
        error_invalid_text="Data jest poza zakresem",
        field_hint_text="DD.MM.RRRR",
        field_label_text="Wpisz datę ręcznie"
    )
    page.overlay.append(date_picker)

    def otworz_kalendarz(teczka_id, tryb):
        nonlocal wybrana_teczka_id, tryb_kalendarza
        wybrana_teczka_id = teczka_id
        tryb_kalendarza = tryb
        date_picker.open = True
        page.update()

    # ==========================================
    #             WIDOKI (EKRANY)
    # ==========================================

    def pokaz_menu(e=None):
        """Wyświetla menu główne"""
        widok = ft.View(
            route="/menu",
            controls=[
                ft.SafeArea(
                    content=ft.Column([
                        ft.Container(height=50),
                        ft.Text("Asystent Dzielnicowego", size=30, weight="bold", text_align=ft.TextAlign.CENTER),
                        ft.Text("System Obsługi Niebieskiej Karty", size=14, italic=True, text_align=ft.TextAlign.CENTER),
                        ft.Container(height=40),
                        ft.Button("Kreator Nowej Teczki", width=280, height=60, on_click=pokaz_kreator),
                        ft.Container(height=10),
                        ft.Button("Aktywne Procedury", width=280, height=60, on_click=pokaz_aktywne),
                        ft.Container(height=10),
                        ft.Button("Pomoce (Wytyczne nr 3)", width=280, height=60, on_click=pokaz_pomoce)
                    ], spacing=0, horizontal_alignment=ft.CrossAxisAlignment.CENTER)
                )
            ]
        )
        page.views.clear()
        page.views.append(widok)
        page.update()

    def pokaz_kreator(e=None):
        """Wyświetla formularz do utworzenia nowej teczki"""
        nr_input = ft.TextField(label="Numer JED", width=300)
        data_input = ft.TextField(label="Data wszczęcia (RRRR-MM-DD)", value=datetime.now().strftime("%Y-%m-%d"), width=300)
        
        cb_nkb = ft.Checkbox(label="Przekazano NK-B na interwencji", value=True)
        cb_ofiara_maloletnia = ft.Checkbox(label="Ofiara to małoletni lub osoba nieporadna", value=False)
        cb_sprawca_nieletni = ft.Checkbox(label="Sprawca jest osobą niepełnoletnią (< 18 lat)", value=False)
        cb_policjant = ft.Checkbox(label="Uczestnikiem (sprawca/ofiara) jest pracownik Policji", value=False)
        cb_bron = ft.Checkbox(label="Sprawca posiada broń palną", value=False)
        cb_zatrzymany_bron = ft.Checkbox(label="Sprawcę zatrzymano i odebrano broń", value=False)
        cb_zolnierz = ft.Checkbox(label="Sprawca jest żołnierzem czynnej służby", value=False)
        cb_nakaz_pol = ft.Checkbox(label="Nakaz Policji", value=False)
        cb_nakaz_sad = ft.Checkbox(label="Nakaz Sądowy", value=False)
        nr_nakazu_input = ft.TextField(label="Numer nakazu/zakazu", value="", width=300)
        freq_input = ft.TextField(label="Częstotliwość kontroli (dni)", value="30", width=200)
        
        tekst_bledu = ft.Text(color="red", weight="bold")

        def zapisz_z_kreatora(e):
            nr = (nr_input.value or "").strip()
            data = (data_input.value or "").strip()

            if not nr:
                tekst_bledu.value = "BŁĄD: Musisz podać numer JED!"
                page.update()
                return
            try:
                nakaz_pol = bool(cb_nakaz_pol.value)
                nakaz_sad = bool(cb_nakaz_sad.value)
                try:
                    czest = int((freq_input.value or "30").strip())
                except Exception:
                    czest = 30

                db.zapisz_teczke(
                    nr, data,
                    cb_bron.value, cb_zolnierz.value, cb_nkb.value,
                    cb_sprawca_nieletni.value, cb_ofiara_maloletnia.value,
                    cb_policjant.value,
                    nakaz_pol, nakaz_sad,
                    cb_zatrzymany_bron.value,
                    czest,
                    nr_nakazu_input.value or None
                )
                show_snack("Teczka zapisana", color="green")
                pokaz_aktywne()
            except Exception as exc:
                show_snack(f"Błąd zapisu: {exc}", color="red")

        widok = ft.View(
            route="/kreator",
            controls=[
                ft.SafeArea(
                    content=ft.Column([
                        ft.Row([ft.Button("Powrót do menu głównego", on_click=pokaz_menu)]),
                        ft.Divider(),
                        ft.Text("Nowa Teczka NK", size=25, weight="bold"),
                        nr_input, 
                        data_input,
                        tekst_bledu,
                        ft.Container(height=10),
                        ft.Text("Ankieta początkowa (zaznacz właściwe):", weight="bold", size=16),
                        cb_nkb, cb_ofiara_maloletnia, cb_sprawca_nieletni, cb_policjant,
                        cb_bron, cb_zatrzymany_bron, cb_zolnierz, cb_nakaz_pol, cb_nakaz_sad, nr_nakazu_input, freq_input,
                        ft.Container(height=20),
                        ft.Button("Zapisz Teczkę", on_click=zapisz_z_kreatora, color="white", bgcolor="green", height=50)
                    ], scroll="auto")
                )
            ]
        )
        page.views.append(widok)
        page.update()

    def pokaz_aktywne(e=None):
        """Wyświetla listę aktywnych procedur"""
        rows = []
        for row in db.pobierz_wszystkie():
            historia = db.pobierz_historie(row[0])
            t = TeczkaNK(row, historia)
            
            dni_w = t.dni_do_wizyty()
            term_w = t.oblicz_termin_wizyty()
            kolor_w = "red" if (dni_w is not None and dni_w < 0) else "green"
            ost_w = t.data_ostatniej_wizyty.strftime("%Y-%m-%d") if t.data_ostatniej_wizyty else "Brak"
            
            btn_wizyta = ft.Button(f"📅 {term_w} ({dni_w}d)", on_click=lambda e, tid=t.id: otworz_kalendarz(tid, "wizyta"), color=kolor_w)

            if t.nakaz_zakaz:
                status_nakazu = ft.Text("TAK", color="red", weight="bold")
                dni_k = t.dni_do_kontroli()
                term_k = t.oblicz_termin_kontroli()
                kolor_k = "red" if (dni_k is not None and dni_k < 0) else "orange"
                ost_k = t.data_ostatniej_kontroli.strftime("%Y-%m-%d") if t.data_ostatniej_kontroli else "Brak"
                btn_kontrola = ft.Button(f"🔍 {term_k} ({dni_k}d)", on_click=lambda e, tid=t.id: otworz_kalendarz(tid, "kontrola"), color=kolor_k)
                txt_ost_k = ft.Text(ost_k)
            else:
                status_nakazu = ft.Text("NIE", color="grey")
                btn_kontrola = ft.Text("-")
                txt_ost_k = ft.Text("-")

            rows.append(
                ft.DataRow(cells=[
                    ft.DataCell(ft.Text(t.nr_jed, weight="bold")),
                    ft.DataCell(status_nakazu),
                    ft.DataCell(ft.Text(ost_w)),
                    ft.DataCell(btn_wizyta),
                    ft.DataCell(txt_ost_k),
                    ft.DataCell(btn_kontrola),
                    ft.DataCell(ft.Row(controls=[
                        ft.Button("Szcz.", on_click=lambda e, obj=t: otworz_szczegoly(obj)),
                        ft.Button("Edytuj Nakaz", on_click=lambda e, obj=t: pokaz_edytuj_nakaz_page(obj)),
                        ft.Button("Usuń", color="red", on_click=lambda e, tid=t.id: potwierdz_usuniecie(tid))
                    ], spacing=5))
                ])
            )

        tabela = ft.DataTable(
            columns=[
                ft.DataColumn(ft.Text("JED")),
                ft.DataColumn(ft.Text("Nakaz")), 
                ft.DataColumn(ft.Text("Ost. Wizyta")), 
                ft.DataColumn(ft.Text("Nast. Wizyta (Zmień)")), 
                ft.DataColumn(ft.Text("Ost. Kontrola")),
                ft.DataColumn(ft.Text("Nast. Kontrola (Zmień)")),
                ft.DataColumn(ft.Text("Akcje"))
            ],
            rows=rows
        )

        tabela_przewijana = ft.Row(controls=[tabela], scroll="always")

        widok = ft.View(
            route="/aktywne",
            controls=[
                ft.SafeArea(
                    content=ft.Column([
                        ft.Row([
                            ft.Button("Menu główne", on_click=pokaz_menu)
                        ]),
                        ft.Divider(),
                        ft.Text("Aktywne procedury", size=25, weight="bold"),
                        tabela_przewijana if rows else ft.Text("Brak aktywnych procedur.", italic=True, size=16)
                    ], scroll="auto")
                )
            ]
        )
        page.views.clear()
        page.views.append(widok)
        page.update()

    def pokaz_pomoce(e=None):
        """Wyświetla wytyczne i pomoce"""
        pdf_help = None
        for pdf_path in Path.cwd().glob("*.pdf"):
            if "wytycz" in pdf_path.name.lower() or "wytyczne" in pdf_path.name.lower():
                pdf_help = pdf_path
                break

        pomoce_controls = [
            ft.Row([ft.Button("Menu główne", on_click=pokaz_menu)]),
            ft.Divider(),
            ft.Text("Pomoce i Wytyczne", size=25, weight="bold"),
            ft.Text("Wytyczne nr 3 Komendanta Głównego Policji", weight="bold", size=18),
            ft.Text("Ściąga proceduralna dla postępowania z Niebieską Kartą i nakazami/zakazami."),
            ft.Container(height=20),
            ft.Text("Kiedy wszcząć procedurę:", weight="bold"),
            ft.Text("- Policjant wszczyna procedurę Niebieska Karta w każdym przypadku, gdy poweźmie uzasadnione podejrzenie przemocy domowej."),
            ft.Text("- Jeżeli zgłoszenie pochodzi od świadka lub osoby trzeciej, procedura również musi zostać wszczęta."),
            ft.Text("- NK-A należy wypełnić w obecności osoby doznającej przemocy, jeśli jej obecność jest możliwa i bezpieczna."),
            ft.Container(height=10),
            ft.Text("Co sprawdzić na początku:", weight="bold"),
            ft.Text("- Dane w KSIP i SWD: broń, wcześniejsze interwencje, informacje o przemocy, wcześniejsze nakazy/zakazy i ograniczenia."),
            ft.Text("- Okres co najmniej 12 miesięcy wstecz oraz istniejące relacje rodzinne i mieszkaniowe."),
            ft.Text("- Czy istnieje ryzyko eskalacji, alkoholizm, uzależnienia lub inne czynniki zwiększające zagrożenie."),
            ft.Container(height=10),
            ft.Text("Teczka zagadnieniowa powinna zawierać:", weight="bold"),
            ft.Text("- kopię formularza NK-A oraz potwierdzenie przekazania NK-B osobie pokrzywdzonej."),
            ft.Text("- notatki służbowe, protokoły czynności, daty i wyniki wizyt oraz informacje o osobach zamieszkałych."),
            ft.Text("- potwierdzenia doręczeń, decyzje o nałożeniu nakazu/zakazu, numer nakazu i datę wydania."),
            ft.Text("- informacje o kontaktach ze świadkami, członkach rodziny, służbach społecznych oraz innymi instytucjami."),
            ft.Text("- dokumenty dotyczące skierowania sprawy do GOPS lub Komisji ds. Alkoholowych oraz kopie wysłanych wniosków."),
            ft.Text("- harmonogram kontroli częstotliwości, terminy kolejnych wizyt oraz adnotacje o nieobecnościach."),
            ft.Text("- wyniki ustaleń podjętych działań pomocowych i środków ochrony."),
            ft.Text("- Nie umieszczaj w teczce: protokołów grupy diagnostyczno-pomocowej, dokumentacji postępowania przygotowawczego, kopii NK-C i NK-D oraz dokumentów objętych tajemnicą inną niż policja."),
            ft.Container(height=10),
            ft.Text("Kiedy składać wniosek do GOPS:", weight="bold"),
            ft.Text("- W sytuacji, gdy osoba pokrzywdzona potrzebuje wsparcia socjalnego, mieszkalnego lub pomocy w zapewnieniu bezpieczeństwa."),
            ft.Text("- Gdy konieczne jest zapewnienie tymczasowego schronienia, wsparcia finansowego, żywieniowego lub świadczeń rodzinnych."),
            ft.Text("- Wniosek do GOPS powinien trafić niezwłocznie po rozpoznaniu sytuacji, w szczególności gdy zagrożenie jest wysokie."),
            ft.Text("- Zaznacz w teczce datę skierowania wniosku i informacje o podjętych działaniach."),
            ft.Container(height=10),
            ft.Text("Kiedy informować Komisję ds. Alkoholowych:", weight="bold"),
            ft.Text("- Przy stwierdzeniu, że przemoc jest powiązana z nadużywaniem alkoholu lub innymi substancjami."),
            ft.Text("- Gdy zachowanie sprawcy wskazuje na konieczność oceny stanu trzeźwości, formułowania zalecenia lub działań zapobiegawczych."),
            ft.Text("- Skierowanie do komisji alkoholowej jest szczególnie ważne, gdy osoba sprawcy mieszka z osobą pokrzywdzoną oraz gdy istnieje uzasadnione ryzyko recydywy."),
            ft.Container(height=10),
            ft.Text("Nakaz / zakaz:", weight="bold"),
            ft.Text("- Nakaz natychmiastowego opuszczenia mieszkania wraz z bezpośrednim otoczeniem."),
            ft.Text("- Zakaz zbliżania się do mieszkania lub osoby doznającej przemocy domowej oraz kontaktowania się."),
            ft.Text("- Zakaz wstępu do szkoły, placówki, obiektu sportowego lub miejsca pracy, jeśli są osoby pokrzywdzone."),
            ft.Container(height=10),
            ft.Text("Co zrobić po wydaniu nakazu/zakazu:", weight="bold"),
            ft.Text("- Sporządź i dołącz do teczki protokół czynności opuszczenia miejsca oraz kopię zawiadomienia dla osoby pokrzywdzonej."),
            ft.Text("- Jeśli doręczenie dokumentów nie było możliwe, zostaw pisemne zawiadomienie i wpisz to do teczki."),
            ft.Text("- Ustal częstotliwość kontroli, zaktualizuj termin wizyt i zapisuj wyniki każdej interwencji."),
            ft.Text("- Monitoruj, czy sprawca stosuje się do nakazu/zakazu i czy osoba pokrzywdzona otrzymała odpowiednie wsparcie."),
        ]

        if pdf_help and platform.system() in ["Windows", "Linux", "Darwin"]:
            pomoce_controls.append(ft.Container(height=20))
            pomoce_controls.append(
                ft.Button("Otwórz wytyczne PDF", on_click=lambda e: os.startfile(str(pdf_help)), width=250, bgcolor="#2E7D32", color="white")
            )
        elif not pdf_help:
            pomoce_controls.append(ft.Container(height=20))
            pomoce_controls.append(
                ft.Text("Umieść plik PDF z wytycznami w katalogu projektu, np. wytyczne nr3 KGP.pdf.", color="grey")
            )

        widok = ft.View(
            route="/pomoce",
            controls=[
                ft.SafeArea(
                    content=ft.Column(pomoce_controls, scroll="auto")
                )
            ]
        )
        page.views.clear()
        page.views.append(widok)
        page.update()

    def otworz_edytuj_nakaz(t):
        cb_pol = ft.Checkbox(label="Nakaz Policji", value=bool(t.nakaz_policja))
        cb_sad = ft.Checkbox(label="Nakaz Sądowy", value=bool(t.nakaz_sad))
        nr_field = ft.TextField(label="Numer nakazu/zakazu", value=str(getattr(t, 'nr_nakazu', '') or ""), width=300)
        freq = ft.TextField(label="Częstotliwość (dni)", value=str(t.czestotliwosc), width=200)

        def zapisz_nakaz(ev):
            try:
                try:
                    cz = int((freq.value or "").strip())
                except Exception:
                    show_snack("Niepoprawna wartość częstotliwości — używam 30 dni", color="orange")
                    cz = 30
                db.ustaw_nakaz(t.id, bool(cb_pol.value), bool(cb_sad.value), cz, nr_nakazu=(nr_field.value or None))
                dlg.open = False
                page.update()
                show_snack(f"Nakaz zaktualizowany (czestotliwosc={cz})", color="green")
                otworz_szczegoly(t)
            except Exception as exc:
                show_snack(f"Błąd zapisu: {exc}", color="red")

        dlg = ft.AlertDialog(
            title=ft.Text('Edycja Nakazu / Zakazu'),
            content=ft.Column([cb_pol, cb_sad, nr_field, freq], tight=True),
            actions=[
                ft.TextButton('Anuluj', on_click=lambda e: (setattr(dlg, 'open', False), page.update())),
                ft.Button('Zapisz', on_click=zapisz_nakaz)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Dedykowany dialog do dodania/edycji tylko nakazu sądowego
    def otworz_dodaj_nakaz_sad(t):
        cb_sad = ft.Checkbox(label="Nakaz Sądowy", value=bool(t.nakaz_sad))
        nr_field = ft.TextField(label="Numer nakazu/zakazu", value=str(getattr(t, 'nr_nakazu', '') or ""), width=300)
        freq = ft.TextField(label="Częstotliwość (dni)", value=str(t.czestotliwosc), width=200)

        def zapisz(ev):
            try:
                try:
                    cz = int((freq.value or "").strip())
                except Exception:
                    show_snack("Niepoprawna wartość częstotliwości — używam 30 dni", color="orange")
                    cz = 30
                db.ustaw_nakaz(t.id, bool(t.nakaz_policja), bool(cb_sad.value), cz, nr_nakazu=(nr_field.value or None))
                dlg.open = False
                page.update()
                show_snack(f"Nakaz sądowy zapisany (czestotliwosc={cz})", color="green")
                otworz_szczegoly(t)
            except Exception as exc:
                show_snack(f"Błąd zapisu: {exc}", color="red")

        dlg = ft.AlertDialog(
            title=ft.Text('Dodaj / Edytuj Nakaz Sądowy'),
            content=ft.Column([cb_sad, nr_field, freq], tight=True),
            actions=[
                ft.TextButton('Anuluj', on_click=lambda e: setattr(dlg, 'open', False) or page.update()),
                ft.Button('Zapisz', on_click=zapisz)
            ],
            actions_alignment=ft.MainAxisAlignment.END
        )
        page.dialog = dlg
        dlg.open = True
        page.update()

    # Strona/zakładka do edycji nakazu/zakazu (pełny widok z informacjami)
    def pokaz_edytuj_nakaz_page(teczka):
        """Wyświetla stronę do edycji nakazu/zakazu"""
        # odśwież dane
        row = db.pobierz_teczke(teczka.id)
        historia = db.pobierz_historie(teczka.id)
        t = TeczkaNK(row, historia)

        nr_jed = ft.Text(f"Numer JED: {t.nr_jed}", size=16)
        kto = ft.Text(f"Wydano przez: {'Sąd' if t.nakaz_sad else ('Policja' if t.nakaz_policja else 'Brak')}")

        cb_pol = ft.Checkbox(label="Nakaz Policji", value=bool(t.nakaz_policja))
        cb_sad = ft.Checkbox(label="Nakaz Sądowy", value=bool(t.nakaz_sad))
        nr_field = ft.TextField(label="Numer nakazu/zakazu", value=str(getattr(t, 'nr_nakazu', '') or ""), width=300)
        freq = ft.TextField(label="Częstotliwość kontroli (dni)", value=str(t.czestotliwosc), width=200)

        def zapisz(e):
            try:
                try:
                    cz = int((freq.value or "").strip())
                except Exception:
                    show_snack("Niepoprawna wartość częstotliwości — używam 30 dni", color="orange")
                    cz = 30
                db.ustaw_nakaz(t.id, bool(cb_pol.value), bool(cb_sad.value), cz, nr_nakazu=(nr_field.value or None))
                show_snack(f"Nakaz zapisany (czestotliwosc={cz})", color="green")
                otworz_szczegoly(t)
            except Exception as exc:
                show_snack(f"Błąd zapisu: {exc}", color="red")

        widok = ft.View(
            route="/edytuj_nakaz",
            controls=[
                ft.SafeArea(
                    content=ft.Column([
                        ft.Row([
                            ft.Button("Powrót do szczegółów", on_click=lambda e: otworz_szczegoly(t)),
                            ft.Button("Powrót do listy", on_click=pokaz_aktywne)
                        ]),
                        ft.Divider(),
                        ft.Text("Edycja Nakazu / Zakazu", size=20, weight="bold"),
                        nr_jed,
                        kto,
                        cb_pol, cb_sad, nr_field, freq,
                        ft.Row([ft.Button("Zapisz", on_click=zapisz), ft.Button("Anuluj", on_click=lambda e: otworz_szczegoly(t))], spacing=10)
                    ], scroll="auto")
                )
            ]
        )
        page.views.append(widok)
        page.update()

    def otworz_szczegoly(teczka):
        """Wyświetla szczegóły teczki"""
        # rebuild teczka with fresh data and history
        row = db.pobierz_teczke(teczka.id)
        historia = db.pobierz_historie(teczka.id)
        t = TeczkaNK(row, historia)

        # Historia wizyt
        wizyty = [h[0] for h in historia if h[1] == 'wizyta']
        kontrole = [h[0] for h in historia if h[1] == 'kontrola']

        sekcja = [
            ft.Row([
                ft.Button("Powrót do listy", on_click=pokaz_aktywne),
                ft.Button("Do menu głównego", on_click=pokaz_menu)
            ]),
            ft.Divider(),
            ft.Text(f"Szczegóły JED: {t.nr_jed}", size=20, weight="bold"),
            ft.Text("Historia wizyt:", weight="bold"),
        ]
        
        if wizyty:
            for w in wizyty:
                sekcja.append(ft.Text(w))
        else:
            sekcja.append(ft.Text("Brak zapisanych wizyt."))

        sekcja.extend([
            ft.Container(height=8),
            ft.Divider(),
            ft.Text("Historia kontroli nakazu:", weight="bold"),
        ])
        
        if kontrole:
            for k in kontrole:
                sekcja.append(ft.Text(k))
        else:
            sekcja.append(ft.Text("Brak zapisanych kontroli."))

        sekcja.extend([
            ft.Container(height=8),
            ft.Divider(),
            ft.Text("Nakaz / Zakaz", weight="bold"),
            ft.Text(f"Aktywny: {'TAK' if t.nakaz_zakaz else 'NIE'}"),
            ft.Text(f"Numer nakazu/zakazu: {t.nr_nakazu if getattr(t, 'nr_nakazu', None) else 'Brak'}"),
            ft.Text(f"Częstotliwość kontroli: {t.czestotliwosc} dni"),
        ])

        widok = ft.View(
            route="/szczegoly",
            controls=[
                ft.SafeArea(
                    content=ft.Column(sekcja, scroll="auto")
                )
            ]
        )
        page.views.append(widok)
        page.update()

    # ==========================================
    #             FUNKCJE LOGICZNE
    # ==========================================

    def potwierdz_usuniecie(teczka_id):
        dlg = ft.AlertDialog(
            title=ft.Text("Usuwanie teczki"),
            content=ft.Text("Czy na pewno chcesz usunąć tę sprawę?"),
        )
        def zamknij(e):
            dlg.open = False
            page.update()

        def usun(e):
            dlg.open = False
            try:
                db.usun_teczke(teczka_id)
                show_snack("Teczka usunięta", color="green")
            except Exception as exc:
                show_snack(f"Błąd usuwania: {exc}", color="red")
            finally:
                pokaz_aktywne()

        dlg.actions = [
            ft.TextButton("Anuluj", on_click=zamknij),
            ft.Button("Usuń", color="red", on_click=usun)
        ]
        dlg.actions_alignment = ft.MainAxisAlignment.END

        page.overlay.append(dlg)
        dlg.open = True
        page.update()

    pokaz_menu()

if __name__ == "__main__":
    ft.app(target=main)