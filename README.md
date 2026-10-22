# 🩺 Wirtualna Pracownia Biofizyki Medycznej

Nowoczesna, interaktywna aplikacja edukacyjna w języku Python / **Streamlit** przeznaczona dla studentów kierunków medycznych (Lekarski, Lekarsko-Dentystyczny, Farmacja, Fizjoterapia, Analityka Medyczna). 

---

## 🏛️ Dwie Wersje Aplikacji w Projekcie

Projekt zawiera dwie zoptymalizowane wersje aplikacji:

1. **`app.py` – Wersja Laboratoryjna ("Soft" dla Studentów - Domyślna):**
   - Działa jak realistyczne, wirtualne przyrządy pomiarowe na sali ćwiczeń (stymulator z oscyloskopem, manometry przepływowe, cyfrowy przelicznik impulsów dozymetrycznych).
   - **Brak automatycznych gotowców:** student nie dostaje gotowej krzywej Weissa ani obliczonego współczynnika osłabiania – sam dobiera parametry, odczytuje wskazania z ekranu i samodzielnie sporządza wykresy oraz obliczenia w swoim protokole laboratoryjnym.
   - Wyczyszczona z podpowiedzi i wzorów – wymaga aktywnego myślenia i analizy przebiegów.

2. **`app_docelowa.py` – Wersja Demonstracyjna / Zaawansowana (dla Prowadzących / Wzorcowa):**
   - Pełne opracowanie dydaktyczne z automatyczną bisekcją progu pobudliwości, wykresem Weissa-Lapicque'a, automatyczną regresją liniową, generatorami tabel protokołu i modułem klinicznym.

---

## 📑 Spis Modułów i Działanie Stanowisk (wersja `app.py`)

### ⚡ 1. Potencjał Czynnościowy & Pobudliwość Komórkowa
- **Wirtualny Stymulator:** Użytkownik ręcznie ustala czas trwania bodźca ($\Delta t_1$) i natężenie ($I_1$), a także opcjonalnie parametry drugiego impulsu ($\Delta t_2$, $I_2$, odstęp $\Delta\tau$).
- **Oscyloskop:** Trzykanałowy ekran przedstawiający prąd bodźca $I(t)$, potencjał błony $V(t)$ oraz przewodności sodową $g_{Na}(t)$ i potasową $g_K(t)$.
- **Zadanie Studenta:** Samodzielna identyfikacja progu pobudzenia, obserwacja generowania potencjału czynnościowego lub stanu podprogowego, rejestracja par $(\Delta t, I_p)$ i własnoręczne wykreślenie krzywej $I_p = f(\Delta t)$ na papierze milimetrowym.

---

### 🩸 2. Prawa Przepływu Cieczy & Hemodynamika
- **Stanowisko Przepływowe:** Regulacja geometrii naczynia ($r_1$, $r_2$, opcja przewężenia/stenozy) oraz właściwości cieczy (strumień objętości $Q$, lepkość $\eta$, gęstość $\rho$).
- **Wirtualne Mierniki Laboratoryjne:**
  - Odczyty ciśnienia statycznego ($p_{s1}, p_{s2}$) i całkowitego ($p_1, p_2$).
  - Odczyt różnicy ciśnień ($\Delta p$).
  - Wskaźniki liczby Reynoldsa ($N_{R1}, N_{R2}$) dla obu sekcji naczynia.
- **Zadanie Studenta:** Odczytanie wskazań manometrów dla kolejnych wartości promienia $r$, spisanie ich do tabeli w protokole i samodzielne wykreślenie zależności $R_N(r)$ oraz $v(r)$.

---

### ☢️ 3. Osłabianie Promieniowania Jonizującego w Tkankach
- **Stanowisko Dozymetryczne:** Wybór źródła (Cez-137, Kobalt-60, Technet-99m) oraz materiału osłony (Ołów, Beton, Kość, Tkanka miękka, Aluminium).
- **Cyfrowy Przelicznik Impulsów:** Pomiar tła naturalnego lub zliczeń z absorbentem o zadanej grubości $x$ w wybranym czasie bramkowania $t_{pom}$ z realistyczną fluktuacją kwantową Poissona ($\sigma_N = \sqrt{N}$).
- **Zadanie Studenta:** Krok po kroku rejestrowanie liczby zliczeń dla kolejnych grubości płytki, obliczenie częstości netto $a(x)$, transformacja $\ln a$ i samodzielne wyznaczenie współczynnika osłabiania $\mu$ z nachylenia prostej.

---

## 🚀 Uruchomienie Lokalne

### Wymagania
- Python 3.10, 3.11, 3.12, 3.13 lub 3.14
- Zainstalowane biblioteki z `requirements.txt`

### Krok po kroku:

1. **Sklonuj lub pobierz repozytorium:**
   ```bash
   git clone https://github.com/<twoj-login>/biofizyka-pracownia.git
   cd biofizyka-pracownia
   ```

2. **(Opcjonalnie) Utwórz i aktywuj środowisko wirtualne:**
   ```bash
   python -m venv .venv
   # Windows (PowerShell):
   .venv\Scripts\Activate.ps1
   # Linux / macOS:
   source .venv/bin/activate
   ```

3. **Zainstaluj zależności:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Uruchom aplikację:**
   ```bash
   streamlit run app.py
   ```
   Aplikacja automatycznie otworzy się w domyślnej przeglądarce pod adresem: `http://localhost:8501`.

---

## 🌐 Publikacja na GitHub i Streamlit Community Cloud (Krok po Kroku)

Aplikacja jest w 100% gotowa do darmowego wdrożenia w chmurze **Streamlit Community Cloud**, dzięki czemu studenci mogą z niej korzystać na dowolnym urządzeniu (laptop, tablet, smartfon) bez instalowania Pythona!

### Krok 1: Wypchnięcie projektu na GitHub
1. Zainicjalizuj lokalne repozytorium git w folderze projektu:
   ```bash
   git init
   git add .
   git commit -m "Wdrożenie aplikacji Wirtualna Pracownia Biofizyki Medycznej"
   ```
2. Załóż nowe repozytorium na stronie [github.com](https://github.com) (np. o nazwie `biofizyka-medyczna`).
3. Połącz lokalne repozytorium i wyślij pliki:
   ```bash
   git branch -M main
   git remote add origin https://github.com/<twoj-login>/biofizyka-medyczna.git
   git push -u origin main
   ```

### Krok 2: Wdrożenie na Streamlit Cloud
1. Zaloguj się na platformie [share.streamlit.io](https://share.streamlit.io/) (używając swojego konta GitHub).
2. Kliknij przycisk **"Create app"** (lub **"New app"**).
3. Wybierz:
   - **Repository:** `<twoj-login>/biofizyka-medyczna`
   - **Branch:** `main`
   - **Main file path:** `app.py`
4. Kliknij **"Deploy!"**.
5. Po kilkudziesięciu sekundach Twoja aplikacja będzie dostępna pod publicznym adresem URL, np.:  
   `https://biofizyka-medyczna.streamlit.app`

---

## 📊 Eksport Danych dla Studentów
W każdej zakładce student ma możliwość pobrania wygenerowanych danych pomiarowych w formacie **CSV** (jednym kliknięciem), co pozwala na bezpośrednie przeniesienie liczb do Excela, Worda lub wklejenie do drukowanego protokołu laboratoryjnego.

---

## 📄 Licencja i Informacje o Audycie
Szczegółowy audyt fizykalny, numeryczny i dydaktyczny znajduje się w dołączonym pliku `AUDYT_I_OPRACOWANIE.md`.
Projekt stworzony dla celów dydaktycznych na uczelniach medycznych.
