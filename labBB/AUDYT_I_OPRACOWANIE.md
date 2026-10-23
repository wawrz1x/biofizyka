# AUDYT KODÓW SYMULACYJNYCH I OPRACOWANIE DYDAKTYCZNE DLA PRACOWNI BIOFIZYKI

**Data sporządzenia:** Październik 2026  
**Przeznaczenie:** Pracownia Fizyki i Biofizyki dla Studentów Uczelni Medycznych (Kierunek Lekarski, Lekarsko-Dentystyczny, Farmacja, Fizjoterapia)  
**Analizowane moduły źródłowe:** `ac.py`, `PP.py`, `prom.py`  
**Materiały odniesienia:** Protokoły ćwiczeń laboratoryjnych:
- `l09b-potencjal-czynnociowy.pdf`
- `prawa-przeplywu.pdf`
- `l02-oslabianie-promieniowania-j.pdf`

---

## 1. WPROWADZENIE I CELE AUDYTU

Celem audytu jest kompleksowa ocena poprawności merytorycznej (fizycznej, biologicznej i biofizycznej) oraz wartości dydaktycznej istniejących skryptów symulacyjnych, wykorzystywanych w pracowni biofizyki medycznej. Skrypty te zostały zestawione z aktualnymi protokołami sprawozdawczymi wypełnianymi przez studentów.

Audyt obejmuje:
1. Weryfikację fundamentalnych równań, stałych fizycznych i biofizycznych oraz konwencji znaków.
2. Analizę numeryczną algorytmów (stabilność, błędy zaokrągleń, osobliwości matematyczne).
3. Ocenę stopnia pokrycia wymagań protokołów studenckich (możliwość zebrania danych, linearyzacja, wyznaczanie parametrów).
4. Ocenę przydatności kliniczno-edukacyjnej dla przyszłego lekarza.
5. Rekomendacje modernizacyjne pod kątem stworzenia zintegrowanej aplikacji webowej w środowisku Python / Streamlit.

---

## 2. AUDYT MODUŁU 1: POTENCJAŁ CZYNNOŚCIOWY (`ac.py`)

### 2.1. Model biofizyczny i poprawność równań
Skrypt `ac.py` implementuje klasyczny model Hodgkina-Huxleya (1952) dla aksonu olbrzymiego kałamarnicy (*Loligo*), przesunięty do fizjologicznego potencjału spoczynkowego $V_{spocz} = -70\text{ mV}$.

Równanie różniczkowe bilansu prądów membranowych:
$$C_m \frac{dV_m}{dt} = I_{stim} - \left(I_{Na} + I_K + I_L\right)$$
gdzie:
- $I_{Na} = \bar{g}_{Na} m^3 h (V_m - E_{Na})$, $\bar{g}_{Na} = 120\text{ mS/cm}^2$, $E_{Na} = +45\text{ mV}$
- $I_K = \bar{g}_K n^4 (V_m - E_K)$, $\bar{g}_K = 36\text{ mS/cm}^2$, $E_K = -82\text{ mV}$
- $I_L = g_L (V_m - E_L)$, $g_L = 0.3\text{ mS/cm}^2$, $E_L = -59.4\text{ mV}$
- Pojemność błony $C_m = 1.0\ \mu\text{F/cm}^2$

**Wnioski z audytu biofizycznego:**
- **Zgodność modelowa:** Równania kinetyczne bramkowania ($n, m, h$) oraz potencjały równowagowe Nernsta są zgodne z kanonem biofizyki elektrofizjologicznej. Skrypt poprawnie generuje iglicę potencjału czynnościowego (depolaryzacja do ok. $+38.5\text{ mV}$ oraz hiperpolaryzację następczą do ok. $-81.2\text{ mV}$).
- **Błąd numeryczny (osobliwości dzielenia przez zero):**
  W liniach 25–26 skryptu znajduje się fragment:
  ```python
  if abs(mv - (-45.0)) < 1e-5: mv += 0.1
  if abs(mv - (-60.0)) < 1e-5: mv += 0.1
  ```
  Jest to **błąd metodyczny i fizyczny**. Osobliwości w kinetyce $\alpha_m$ i $\alpha_n$ wynikają z postaci funkcji $\frac{x}{e^x - 1}$ przy $x \to 0$. W skrypcie autor sztucznie zaburza zmienną stanu (napięcie błonowe $V_m$) o $0.1\text{ mV}$, co generuje sztuczny artefakt napięciowy w trakcie całkowania metodą Eulera. Poprawnym rozwiązaniem matematycznym jest zastosowanie reguły de l'Hôpitala lub rozwinięcia w szereg Taylora:
  $$\lim_{x \to 0} \frac{x}{e^{x/10} - 1} = 10$$
  bez jakiejkolwiek modyfikacji $V_m$.

### 2.2. Ocena edukacyjna i dydaktyczna (pod kątem studenta medycyny)
- **Brak interaktywności:** Kod jest statycznym skryptem z twardo zapisanymi wartościami parametrów (`stim0_a = 50.0`, `stim0_d = 1.0`, `stim1_a = 50`, `stim1_d = 1`, `dly = 20`). Student uruchamia skrypt i otrzymuje wyłącznie jeden, niezmienny wykres.
- **Niespełnienie wymagań protokołu `l09b-potencjal-czynnociowy.pdf`:**
  1. *Punkt 1 i 2 protokołu:* Student ma wyznaczyć natężenie bodźca progowego $I_p$ w funkcji czasu jego trwania $\Delta t$ i sporządzić tabelę $I_p = f(\Delta t)$ oraz $I_p = f(1/\Delta t)$. W `ac.py` nie ma mechanizmu wyznaczania progu ani pomiaru dla różnych czasów $\Delta t$. Bodziec $50\ \mu\text{A/cm}^2$ jest bodźcem dalece ponadprogowym (dla $\Delta t = 1\text{ ms}$ próg wynosi $6.78\ \mu\text{A/cm}^2$).
  2. *Punkt 3, 4, 5, 6 protokołu:* Wymagane jest sporządzenie wykresów prawa Weissa-Lapicque'a, wyznaczenie współczynnika kierunkowego $u$, reobazy $R$ i chronaksji $CH = u/R$. Kod tego w ogóle nie realizuje.
  3. *Punkt 7 protokołu:* Wymagane jest zbadanie sumowania podprogowego, refrakcji bezwzględnej i względnej oraz hiperpolaryzacji. W kodzie brak możliwości elastycznej regulacji odstępu $\Delta \tau$ i amplitudy.
- **Kontekst medyczny:** Dla studentów medycyny kluczowe jest powiązanie pojęć:
  - *Chronaksja i reobaza* a bezpieczna i energooszczędna stymulacja serca (rozruszniki, kardiowertery-defibrylatory ICD – impuls o czasie trwania równym chronaksji minimalizuje energię wymaganą do depolaryzacji mięśnia sercowego $E = I^2 R_{tkanki} \Delta t$).
  - *Refrakcja bezwzględna* jako mechanizm uniemożliwiający skurcz tężcowy mięśnia sercowego oraz zapobiegający krążeniu fal pobudzenia (arytmie, reentry).
  - *Leki miejscowo znieczulające* (lignokaina, bupiwakaina) blokujące bramkowane napięciem kanały sodowe $Na_v$ – w symulatorze brakuje suwaka blokady $g_{Na}$ (lub $g_K$ dla leków przeciwarytmicznych klasy III).

---

## 3. AUDYT MODUŁU 2: PRAWA PRZEPŁYWU CIECZY (`PP.py`)

### 3.1. Model fizyczny i poprawność równań
Skrypt `PP.py` modeluje przepływ krwi/cieczy przez sztywne naczynie cylindryczne podzielone na dwa odcinki (o promieniach $r_1$ i $r_2$).

Zastosowane równania:
1. Równanie ciągłości strugi: $Q = S_1 v_1 = S_2 v_2 \implies v = \frac{Q}{\pi r^2}$
2. Prawo Hagena-Poiseuille'a (opór naczyniowy): $R_N = \frac{8 \eta L}{\pi r^4}$
3. Ciśnienie dynamiczne: $p_d = \frac{1}{2} \rho v^2$
4. Liczba Reynoldsa: $N_R = \frac{\rho v (2r)}{\eta} = \frac{2 \rho Q}{\pi \eta r}$

**Wnioski z audytu hydrodynamicznego:**
- **Równania oporu i ciągłości:** Wzory na $v$, $p_d$, $R_N$ i $N_R$ są poprawne i zgodne z klasyczną mechaniką płynów.
- **Problem z obliczaniem ciśnień statycznych i całkowitych przy $r_1 \ne r_2$:**
  W kodzie linie 125–129:
  ```python
  Ps2 = self.P_out # stała 900 Pa
  Ps1 = Ps2 + (RN1 + RN2) * Q_m3s
  P_calk_1 = Ps1 + Pd1
  P_calk_2 = Ps2 + Pd2
  ```
  W fizyce płynów lepkich to **spadek ciśnienia całkowitego** odpowiada stratom energii mechanicznej na pokonanie oporów tarcia wiskotycznego:
  $$\Delta p_{calk} = p_{calk,1} - p_{calk,2} = R_{N,tot} \cdot Q$$
  Ciśnienie statyczne w danym przekroju wynika z różnicy $p_s = p_{calk} - p_d$.
  Gdy przekroje są równe ($r_1 = r_2$), $p_{d1} = p_{d2}$, więc $\Delta p_{stat} = \Delta p_{calk}$, co jest zgodne z protokołem.
  Jednak gdy $r_1 \ne r_2$ (np. zwężenie $r_2 < r_1$), ciśnienie dynamiczne $p_{d2}$ rośnie proporcjonalnie do $1/r_2^4$. Zgodnie z równaniem Bernoulliego dla płynu rzeczywistego, ciśnienie statyczne w miejscu zwężenia musi gwałtownie spaść ($p_{s2} = p_{calk,2} - p_{d2}$), co w medycynie odpowiada paradoksowi hydrodynamicznemu (ryzyko zapadnięcia się ściany naczynia w stenozie!). W kodzie `PP.py` ciśnienie $Ps2$ było sztywno przypisane do stałej 900 Pa, co zaburzało bilans energetyczny przy zmianie $r_2$.
- **Pominięcie liczby Reynoldsa w sekcji 2:** Na ekranie wyświetlana jest wyłącznie liczba $N_R$ dla sekcji 1. W przypadku zwężenia naczynia ($r_2 < r_1$) to w sekcji 2 prędkość jest znacznie wyższa i to tam dochodzi do przekroczenia wartości krytycznej $N_R > 2000$ (powstanie przepływu turbulentnego). Ukrycie $N_R$ dla sekcji 2 uniemożliwia studentowi zaobserwowanie powstawania turbulencji w stenozie.

### 3.2. Ocena edukacyjna i dydaktyczna
- **Technologia:** Kod napisany w bibliotece `tkinter`, co całkowicie uniemożliwia jego uruchomienie w przeglądarce internetowej i publikację na Streamlit Cloud / GitHub bez przepisania na webowy stos technologiczny.
- **Braki w odniesieniu do protokołu `prawa-przeplywu.pdf`:**
  - W protokole studenci mają zebrać 10 punktów pomiarowych dla różnych promieni $r$ i uzupełnić dwie duże tabele (Tabela 1: ciśnienia i odczytane $N_R$; Tabela 2: opór naczyniowy, ciśnienie dynamiczne, prędkość i obliczone $N_R$).
  - Wymagane jest sporządzenie wykresów $R_N = f(r)$ oraz $v = f(r)$. W aplikacji `PP.py` brak jakichkolwiek modułów kreślenia wykresów!
- **Kontekst medyczny:**
  - Zależność oporu od promienia w 4. potędze ($R_N \sim 1/r^4$) to najważniejsze prawo hemodynamiki – zmniejszenie promienia tętnicy o 16% (np. blaszka miażdżycowa) podwaja opór naczyniowy, a zmniejszenie o 50% zwiększa opór 16-krotnie!
  - Liczba Reynoldsa $N_R > 2000$ tłumaczy powstawanie szmerów sercowych i naczyniowych (stenoza aortalna, zwężenie tętnicy szyjnej), powstawanie skrzeplin przyściennych w wirach oraz fizyczną zasadę pomiaru ciśnienia tętniczego metodą Korotkowa. Nowa aplikacja musi to wprost uwypuklać.

---

## 4. AUDYT MODUŁU 3: OSŁABIANIE PROMIENIOWANIA (`prom.py`)

### 4.1. Model fizyczny i poprawność parametrów
Skrypt `prom.py` implementuje prawo osłabiania promieniowania gamma/rentgenowskiego (prawo Lamberta-Beera / Bouguera):
$$I(x) = I_0 e^{-\mu x}$$
gdzie $\mu = \mu_m \cdot \rho$ to liniowy współczynnik osłabiania ($1/\text{cm}$), a $\mu_m = \mu / \rho$ to masowy współczynnik osłabiania ($\text{cm}^2/\text{g}$).

Wartości w bazie danych kodu:
- **Cez-137 ($E_\gamma = 0.662\text{ MeV}$):**
  - Ołów: $\mu_m = 0.110\text{ cm}^2/\text{g}$, $\rho = 11.34\text{ g/cm}^3 \implies \mu = 1.247\text{ cm}^{-1}$
  - Beton: $\mu_m = 0.077\text{ cm}^2/\text{g}$, $\rho = 2.35\text{ g/cm}^3 \implies \mu = 0.181\text{ cm}^{-1}$
  - Kość: $\mu_m = 0.086\text{ cm}^2/\text{g}$, $\rho = 1.85\text{ g/cm}^3 \implies \mu = 0.159\text{ cm}^{-1}$
- **Kobalt-60 ($E_\gamma \approx 1.25\text{ MeV}$):**
  - Ołów: $\mu_m = 0.058\text{ cm}^2/\text{g} \implies \mu = 0.658\text{ cm}^{-1}$
  - Beton: $\mu_m = 0.058\text{ cm}^2/\text{g} \implies \mu = 0.136\text{ cm}^{-1}$
  - Kość: $\mu_m = 0.059\text{ cm}^2/\text{g} \implies \mu = 0.109\text{ cm}^{-1}$

**Weryfikacja fizyczna:** Wartości masowych współczynników osłabiania są w 100% autentyczne i zgodne z oficjalnymi tablicami **NIST XCOM (Photon Cross Sections Database)**.

### 4.2. Wady i braki w odniesieniu do protokołu `l02-oslabianie-promieniowania-j.pdf`
1. **Brak promieniowania tła ($a_t$):**
   W protokole punkty 2 i 7 wymagają zmierzenia szybkości zliczania tła naturalnego $a_t$. W `prom.py` tło w ogóle nie istnieje (krzywa dąży do zera). W rzeczywistym laboratorium sygnał detektora to $a_{brutto}(x) = a_0 e^{-\mu x} + a_t$.
2. **Brak statystyki zliczeń (rozkład Poissona) i niepewności pomiarowych:**
   Rejestracja promieniowania jądrowego licznikiem Geigera-Müllera lub scyntylacyjnym podlega fluktuacjom kwantowym opisanym rozkładem Poissona. Niepewność standardowa liczby zliczeń wynosi $\sigma_N = \sqrt{N}$, a szybkości zliczania $\sigma_a = \sqrt{a / t_{pom}}$. Protokół w punktach 3 i 8 wprost wymaga uzupełnienia kolumn z niepewnościami: $x \pm \Delta x$, $a \pm \Delta a$, $\ln(a) \pm \Delta \ln(a)$. `prom.py` generował wyłącznie idealną linię gładką bez symulacji eksperymentu pomiarowego.
3. **Brak wykresu półlogarytmicznego $\ln(a) = f(x)$:**
   Punkty 4 i 9 protokołu nakazują wykreślenie zależności liniowej $\ln(a) = f(x)$ oraz wyznaczenie współczynnika $\mu$ z nachylenia prostej regresji liniowej. W `prom.py` dostępny był tylko jeden wykres transmisji $I(\%)$.
4. **Brak tabeli pomiarowej:**
   Student nie miał jak odczytać 10 dyskretnych punktów do wpisania w protokół laboratoryjny.
5. **Ograniczona baza tkanek:**
   Dla studentów medycyny krytyczne jest porównanie kości z tkanką miękką / wodą (podstawa kontrastu w RTG i Tomografii Komputerowej) oraz aluminium (standardowy filtr w lampach rentgenowskich do odcinania promieniowania miękkiego).

---

## 5. ZESTAWIENIE WYNIKÓW AUDYTU

| Kryterium | Potencjał Czynnościowy (`ac.py`) | Prawa Przepływu (`PP.py`) | Osłabianie Promieniowania (`prom.py`) |
| :--- | :--- | :--- | :--- |
| **Zgodność z prawami fizyki/biofizyki** | 8.5/10 (poprawny HH, ale błąd osobliwości `mv += 0.1`) | 7.5/10 (błąd bilansu ciśnień przy $r_1 \ne r_2$, brak $N_{R2}$) | 9.0/10 (doskonałe dane NIST, brak tła $a_t$) |
| **Zgodność z protokołem studenckim** | 2.5/10 (brak badania $I_p(\Delta t)$, Weissa, refrakcji) | 4.0/10 (brak wykresów, brak tabeli 10 pkt) | 4.0/10 (brak $\ln a$, brak statystyki Poissona, brak tabeli) |
| **Wartość edukacyjna dla medycyny** | 3.0/10 (statyczny skrypt, brak odniesień klinicznych) | 5.0/10 (brak powiązania ze stenozą i szmerami) | 4.5/10 (brak powiązania z RTG/TK i ochroną ALARA) |
| **Stan technologiczny** | Skrypt CLI / Matplotlib | Tkinter (przestarzały GUI desktopowy) | Ipywidgets (tylko Jupyter/Colab) |
| **Gotowość do wdrożenia webowego** | Wymaga pełnej przebudowy | Wymaga pełnej migracji do Streamlit | Wymaga pełnej migracji do Streamlit |

---

## 6. PROJEKT NOWEJ APLIKACJI STREAMLIT: "WIRTUALNA PRACOWNIA BIOFIZYKI MEDYCZNEJ"

W ramach drugiego kroku przygotowano zintegrowaną, trójzakładkową aplikację w technologii **Streamlit**, która w pełni rozwiązuje wszystkie zidentyfikowane problemy:

### Zakładka 1: Potencjał Czynnościowy & Bioelektryczność
- Pełna implementacja modelu Hodgkina-Huxleya z poprawnym numerycznie traktowaniem osobliwości (reguła de l'Hôpitala).
- Tryb 1: **Krzywa Weissa-Lapicque'a i wyznaczanie bodźca progowego:**
  - Interaktywna regulacja czasu trwania bodźca $\Delta t$ i natężenia $I_1$.
  - Przycisk automatycznego wyznaczenia 10 punktów pomiarowych do tabeli protokołu (dla $\Delta t \in [0.1, 20]\text{ ms}$).
  - Wykres hiperboliczny $I_p = f(\Delta t)$ oraz zlinearyzowany $I_p = f(1/\Delta t)$.
  - Automatyczne wyliczenie prostej regresji, współczynnika $u$, reobazy $R$ i chronaksji $CH$.
- Tryb 2: **Zjawiska dwubodźcowe (refrakcja i sumowanie):**
  - Regulacja odstępu czasowego $\Delta \tau$ oraz siły drugiego bodźca.
  - Demonstracja refrakcji bezwzględnej ($\Delta \tau < 2\text{ ms}$), względnej ($2-10\text{ ms}$) oraz sumowania czasowego bodźców podprogowych.
- Tryb 3: **Hiperpolaryzacja i farmakologia:**
  - Wpływ bodźców ujemnych (pobudzenie z wyłączenia / anodal break excitation).
  - Wirtualna lignokaina / tetrodotoksyna (blokada $g_{Na}$) i tetraetyloamon TEA (blokada $g_K$).
- Eksport gotowych danych do CSV.

### Zakładka 2: Hemodynamika & Prawa Przepływu Cieczy
- Model naczynia naczyniowego z dwoma segmentami i opcją synchronizacji promieni ($r_1 = r_2$).
- Zgodność z prawami Poiseuille'a, Bernoulliego i ciągłości strugi:
  - Prawidłowy bilans strat ciśnienia całkowitego i ciśnień statycznych.
  - Wyliczanie oporu $R_N$, ciśnienia dynamicznego $p_d$, prędkości $v$ oraz liczby Reynoldsa $N_R$ dla obu odcinków.
- Dynamiczny wskaźnik reżimu przepływu:
  - Laminarny ($N_R < 2000$), przejściowy ($2000-2300$), turbulentny ($N_R > 2300$) z alertem powstawania szmerów osłuchowych.
- Generator tabeli protokołu (10 punktów pomiarowych $r \in [5, 15]\text{ mm}$) z jednoczesnym wykresem $R_N = f(r)$ (prawo 4. potęgi) oraz $v = f(r)$ (prawo 2. potęgi).
- Odniesienie kliniczne: stenoza miażdżycowa, tętniak (prawo Laplace'a), osłuchiwanie tonów Korotkowa.

### Zakładka 3: Dozymetria & Osłabianie Promieniowania Jonizującego w Tkankach
- Baza izotopów: Cez-137 ($0.662\text{ MeV}$), Kobalt-60 ($1.25\text{ MeV}$), Technet-99m ($140\text{ keV}$ - scyntygrafia), RTG diagnostyczny ($60\text{ keV}$).
- Baza materiałów: Ołów (Pb), Beton, Kość ludzka zwarta, Tkanka miękka / Woda, Aluminium.
- Realistyczny wirtualny licznik:
  - Pomiar promieniowania tła $a_t \pm \Delta a_t$.
  - Czas bramkowania zliczeń $t_{pom}$.
  - Przełącznik: tryb idealny (teoretyczny) vs tryb pomiarowy (fluktuacje kwantowe Poissona z obliczaniem niepewności pomiarowych $\Delta a$ i $\Delta \ln a$).
- Tabela 10 grubości absorbentu dokładnie odwzorowująca protokół laboratoryjny.
- Podwójny wykres:
  1. $a = f(x)$ ze wskazaniem warstwy połowiącej $HVL = d_{1/2}$.
  2. $\ln(a) = f(x)$ z dopasowaną prostą regresji liniowej, wyznaczonym doświadczalnym $\mu$ oraz porównaniem z wartością tablicową NIST.
- Zastosowania medyczne: zasada ALARA, ochrona personelu, skala Hounsfielda w Tomografii Komputerowej (CT).
