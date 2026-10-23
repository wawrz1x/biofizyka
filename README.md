# ⚡ Wirtualna Pracownia Biofizyki Medycznej — Wersja 2.1
### Ćwiczenie: Potencjał Czynnościowy Neuronu i Pobudliwość Błony Komórkowej
*Zgodne z Rozdziałem 21 podręcznika biofizyki medycznej oraz elektrycznym modelem zastępczym (Ryc. 7)*

---

## 🏛️ Struktura Repozytorium

Aplikacja w wersji 2.1 jest w pełni zogniskowana na badaniu **potencjału czynnościowego neuronu** oraz dynamiki nieliniowej błony komórkowej.

### 🔹 Aktywne pliki aplikacji (Wersja 2.1):
* **`app.py`** — Główna aplikacja w języku Python / Streamlit:
  * Trzykanałowy zintegrowany oscyloskop cyfrowy (Napięcie $U(t)$, Przewodności jonowe $g_{Na}(t), g_K(t)$, Prąd bodźca $J(t)$) ze zsynchronizowanym pionowym kursorem *crosshair*.
  * Niezależne legendy dla każdego z 3 kanałów oscyloskopu.
  * Wielokanałowy **Tryb Ducha** (zapamiętanie do 5 niezależnych kolorowych przebiegów referencyjnych).
  * Wirtualny stymulator laboratoryjny (bodziec pojedynczy, podwójny do badania refrakcji/akomodacji, seria 3 bodźców do sumowania w czasie).
  * Cyfrowy Dziennik Pomiarowy z kalkulatorem bisekcji oraz elastycznym Kreatorem Wykresu z linearyzacją $I_p = f(1/\Delta t)$.
  * Zabezpieczenie hasłem dostępu (`APP_PASSWORD`) oparte o `st.secrets` i `st.session_state`.
* **`hh_model.py`** — Skalibrowany silnik numeryczny modelu Hodgkina-Huxleya:
  * Potencjały równowagowe Nernsta: $U_{spocz} = -90.0\text{ mV}$, $E_{Na} = +66.0\text{ mV}$, $E_K = -97.0\text{ mV}$, $E_{Cl} = -90.0\text{ mV}$.
  * Całkowanie numeryczne metodą Eulera ($dt = 0.01\text{ ms}$).
  * Zrównoważenie prądów w spoczynku ($\frac{dU}{dt} \equiv 0$ bez bodźca).
* **`test_hh_model.py`** — Zestaw 7 testów jednostkowych weryfikujący stabilność spoczynkową, osobliwości, próg bifurkacji, zbieżność kroku czasowego i sumowanie bodźców.
* **`requirements.txt`** — Czyste, minimalne zależności produkcyjne (`streamlit`, `numpy`, `plotly`, `pandas`).
* **`.streamlit/`** — Pliki konfiguracyjne:
  * `config.toml` (ciemny motyw graficzny dopasowany do oscyloskopu),
  * `secrets.toml` (lokalne hasło testowe, ignorowane przez git).
* **`RAPORT_I_DOKUMENTACJA_V2.1.md`** — Pełny raport z audytu biofizycznego, parametryzacji numerycznej i weryfikacji.
* **`potencjal.md`** — Treść Rozdziału 21 podręcznika stanowiąca kanon fizykalny ćwiczenia.

### 📁 Archiwum ćwiczeń legacy (`labBB/`):
Wszystkie pozostałe ćwiczenia i materiały pomocnicze zostały zarchiwizowane w katalogu **`labBB/`**:
* `PP.py`, `prawa-przeplywu.pdf`, `prawa-przeplywu_extracted.txt` — Ćwiczenie: Prawa Przepływu Cieczy & Hemodynamika.
* `prom.py`, `l02-oslabianie-promieniowania-j.pdf`, `l02-oslabianie-promieniowania-j_extracted.txt` — Ćwiczenie: Osłabianie Promieniowania Jonizującego.
* `app_docelowa.py`, `AUDYT_I_OPRACOWANIE.md` — Wczesna demonstracyjna wersja wielomodułowa.
* `potencjal.pdf`, `potencjal_ocr.pdf` — Skany podręcznika akademickiego.
* `ac.py`, `l09b-*`, `audyt_potencjału.md`, `technologia.md`, `INSTRUKCJA_I_DOKUMENTACJA_V2.md` — Notatki projektowe i prototypy.

---

## 🚀 Uruchomienie Lokalne

### Wymagania:
* Python 3.10 – 3.12 (lub nowszy)

### Krok po kroku:
1. **Sklonuj repozytorium:**
   ```bash
   git clone https://github.com/wawrz1x/biofizyka.git
   cd biofizyka
   ```

2. **Utwórz i aktywuj środowisko wirtualne:**
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate  # Linux / macOS
   # .venv\Scripts\activate   # Windows
   ```

3. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uruchom testy jednostkowe:**
   ```bash
   python -m unittest test_hh_model.py
   ```

5. **Uruchom aplikację:**
   ```bash
   streamlit run app.py
   ```
   Aplikacja otworzy się w przeglądarce pod adresem: `http://localhost:8501`. Domyślne hasło lokalne: `haslo_lokalne_testowe`.

---

## 🌐 Wdrożenie na Streamlit Community Cloud

Aplikacja jest w 100% przygotowana do wdrożenia na **Streamlit Community Cloud**:
1. Połącz konto GitHub z [share.streamlit.io](https://share.streamlit.io/).
2. Wskaż repozytorium `wawrz1x/biofizyka`, gałąź `main` oraz plik główny `app.py`.
3. W sekcji **Settings ➔ Secrets** wprowadź hasło dostępu dla studentów:
   ```toml
   APP_PASSWORD = "twoje_haslo_dla_studentow"
   ```
4. Kliknij **Deploy!**.
