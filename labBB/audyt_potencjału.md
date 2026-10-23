## **3\. Co warto wdrożyć do przebudowywanego programu? (Rekomendacje UX i funkcjonalne)**

Skoro macie pełną kontrolę nad kodem symulatora, niewielkim nakładem pracy programistycznej możecie zamienić go z prostego kalkulatora w potężne narzędzie dydaktyczne:

1. **Tryb „Duch” (Ghost Trace / Porównanie dwóch przebiegów):**  
   * Skoro widok odświeża się po każdej zmianie parametrów, studentowi trudno zauważyć subtelną różnicę między tym, co było przed chwilą, a tym, co jest teraz.  
   * **Funkcja:** Przycisk *„Zatrzymaj przebieg w tle (Zapamiętaj jako krzywą referencyjną)”*. Stary przebieg zostaje na ekranie jako wyszarzona linia przerywana, a nowy rysuje się w kolorze na wierzchu. Student od razu widzi na jednym ekranie, jak zmiana czasu trwania, dodanie pre-stymulacji czy zmiana odstępu przesuwa krzywą potencjału i przewodności\!  
2. **Generator serii impulsów (Pulse Train) do sumowania czasowego:**  
   * W podręczniku na Ryc. 6 pokazane jest sumowanie **trzech** kolejnych bodźców podprogowych, podczas gdy stary program i protokół pozwalały tylko na dwa bodźce. Przy dwóch bodźcach sumowanie czasowe bywa mało spektakularne.  
   * **Funkcja:** Zamiast sztywnego „Bodziec 1 i Bodziec 2”, dodajcie zakładkę/tryb *„Seria impulsów (Sumowanie)”*, gdzie student ustawia: natężenie pojedynczego impulsu $J$, czas trwania $\Delta t$, liczbę impulsów $N$ (np. od 2 do 10\) oraz częstotliwość / odstęp między nimi. To idealnie pokaże bezwładność pojemnościową błony.  
3. **Bodziec o narastającym zboczu (Rampa / Trójkąt) w module Akomodacji:**  
   * Obecnie podręcznik każe badać akomodację dwoma bodźcami prostokątnymi (długi podprogowy \+ krótki testujący), co dla studentów bywa mało intuicyjne i łatwo to pomylić ze zwykłym sumowaniem.  
   * **Funkcja:** Oprócz układu dwóch bodźców prostokątnych, dodajcie możliwość wyboru kształtu bodźca: **Prostokąt vs Rampa (liniowo narastający prąd)**. Student ustawia prąd końcowy np. na \$30\\text{ }\\mu\\text{A/cm}^2\$ (dużo powyżej progu). Przy bodźcu prostokątnym – jest iglica. Przy powolnej rampie dochodzącej do tych samych \$30\\text{ }\\mu\\text{A/cm}^2\$ – brak potencjału czynnościowego, a na wykresie poniżej widać, że kanały sodowe uległy inaktywacji\! To daje natychmiastowy efekt „Aha\!”.  
4. **Interaktywny kursor pomiarowy (Oscilloscope Crosshair) \+ Wskaźnik inaktywacji $N{a}^{+}$:**  
   * W modelu Hodgkina-Huxleya za akomodację i refrakcję bezwzględną odpowiada zmienna bramkowania $h$ (inaktywacja kanałów sodowych). Jeśli program pokazuje tylko wypadkową przewodność ${g}_{Na}$ (która w spoczynku i w inaktywacji wynosi blisko zera), student nie widzi różnicy między kanałem *zamkniętym-gotowym* a *zainaktywowanym*.  
   * **Funkcja:** Dodanie na wykresie (lub na pasku bocznym jako pasek postępu) wskaźnika **„Dostępność (gotowość) kanałów $N{a}^{+}$ (współczynnik $h$ w modelu H-H)”** oraz kursora myszy, którym student może najechać na dowolną milisekundę wykresu i odczytać dokładne wartości: $t$, $U(t)$, ${g}_{Na}(t)$, ${g}_{K}(t)$.

### **1\. Audyt zgodności z podręcznikiem (Co jest w tekście, a co musimy odrzucić?)**

| Element / Zjawisko | Status w podręczniku (Dowód w tekście) | Decyzja dydaktyczna |
| :---- | :---- | :---- |
| **Elektryczny model zastępczy H-H i śledzenie przewodności $N{a}^{+}$ oraz ${K}^{+}$** | **100% w tekście:** Ryc. 7 przedstawia kondensator $C$, ogniwa ${E}_{Na},{E}_{K},{E}_{Cl}$ oraz zmienne oporniki ${R}_{Na},{R}_{K}$ i stały ${R}_{Cl}$. Autor wprost pisze, że odwrotności oporów to przewodności elektryczne odzwierciedlające przepuszczalność błony, a program umożliwia śledzenie czasowych zmian *„przewodnictwa elektrycznego błony dla jonów sodowych i potasowych”*. | **Zostaje w pełni.** Pytanie studentów o wykresy przewodności z symulatora to nie nowa wiedza, lecz egzekwowanie tego, co autor sam napisał na str. 180\. |
| **Mechanizm hiperpolaryzacji następczej (bezczynność zamknięcia kanałów ${K}^{+}$)** | **100% w tekście:** Str. 174: *„Pojawia się on wtedy, gdy po osiągnięciu przez błonę potencjału spoczynkowego kanały potasowe nie zostaną jeszcze zamknięte. Zanika on wraz z ustaniem ich działania”*. | **Zostaje w pełni.** Student po prostu zobaczy to zdanie z podręcznika na żywo na wykresie przewodności potasowej w programie. |
| **Koncepcja stałego ładunku progowego ($\Delta Q/S=J\cdot \Delta t$) i przyczyny odchyleń dla długich bodźców** | **100% w tekście:** Str. 175 wprowadza wzór (1) $J\cdot \Delta t=\frac{\Delta Q}{S}$ i utożsamia go z polem prostokąta pod wykresem bodźca. Str. 177 tłumaczy, że dla krótkich stymulacji ładunek potrzebny do pobudzenia jest stały, a dla długich rośnie z powodu działania pompy sodowo-potasowej oraz akomodacji (str. 178). | **Zostaje w pełni.** Zamiast ślepego liczenia równania prostej, student może badać sam iloczyn ${I}_{p}\cdot \Delta t$ (ładunek) dokładnie na bazie wzoru (1) z podręcznika. |
| **Akomodacja i wpływ hiperpolaryzacji poprzez inaktywację/aktywację kanałów $N{a}^{+}$** | **100% w tekście:** Str. 178: *„Długotrwała depolaryzacja inaktywuje układ $N{a}^{+}$, a hiperpolaryzacja ułatwia jego aktywację”*. Ponadto punkt 6 przebiegu ćwiczenia (str. 181\) wprost nakazuje zbadać reakcję na hiperpolaryzację (czas 5 ms, ujemne wartości prądu). | **Zostaje w pełni.** Przywracamy punkt 6 z podręcznika, który ktoś wcześniej usunął z protokołu\! |
| **Sumowanie więcej niż dwóch bodźców podprogowych w czasie** | **100% w tekście:** Ryc. 6 na str. 179 pokazuje sumowanie **trzech** prostokątnych bodźców podprogowych, tłumacząc to pojemnością elektryczną („bezwładnością”) błony. | **Zostaje w pełni.** Rozbudowa programu z 2 do np. 3–5 bodźców w serii to dokładne odwzorowanie Ryc. 6 z podręcznika. |
| **Odróżnienie refrakcji względnej od akomodacji za pomocą dwóch bodźców** | **100% w tekście:** Str. 178–179 opisuje badanie akomodacji i refrakcji względnej układem dwóch następujących po sobie bodźców (pre-stymulacja \+ bodziec testujący) i wyraźnie zaznacza: *„to dwa zupełnie różne zjawiska i nie należy ich mylić”*. | **Zostaje w pełni.** |

### **2\. Gdzie wykorzystamy nasze „dozwolone 10%” poza podręcznikiem?**

Zamiast dokładać studentom nową teorię biofizyczną, której nie ma w skrypcie, wykorzystajmy te 10% na **pomost wizualizacyjno-analityczny zaszyty bezpośrednio w instrukcji protokołu** (tzw. *scaffolding* – student nie musi tego wiedzieć przed przyjściem na zajęcia, dowiaduje się tego z krótkiej wskazówki w zadaniu):

1. **Wizualna reprezentacja ładunku jako pola prostokąta ($\Delta Q/S={I}_{p}\cdot \Delta t$):** Podręcznik podaje ten wzór na str. 175, ale w przebiegu ćwiczenia (str. 181\) każe rysować tylko wykresy ${I}_{p}=f(\Delta t)$ oraz ${I}_{p}=f(1/\Delta t)$. Nasze 5% nowości to poproszenie studenta, by w tabeli obok czasu $\Delta t$ i prądu progowego ${I}_{p}$ pomnożył te dwie liczby przez siebie (obliczając ładunek progowy z Równania 1\) i zobaczył na wykresie, jak dla krótkich czasów ładunek ten jest stały, a dla długich drastycznie rośnie przez ucieczkę jonów (pompy) i akomodację.  
2. **Wyjaśnienie inaktywacji na bazie obserwowanego wykresu ${g}_{Na}$:** Skoro nie wprowadzamy zmiennej $h$, wykorzystujemy drugie 5% na krótką wskazówkę w protokole przy badaniu akomodacji: „Zwróć uwagę, że choć podczas długiego bodźca podprogowego przewodność ${g}_{Na}$ wynosi blisko zera, układ kanałów sodowych uległ częściowej inaktywacji (str. 178). Zobaczysz to w momencie podania drugiego, silnego bodźca – szczyt przewodności ${g}_{Na}$ będzie znacznie niższy niż w warunkach kontrolnych”.

### **3\. Zaktualizowany kształt 4 zadań w protokole (100% zgodności z podręcznikiem)**

Zachowujemy Twój schemat: **Zadanie $\rightarrow$ Eksperyment w symulatorze $\rightarrow$ Wybór reprezentacji graficznej / Tabela $\rightarrow$ Wniosek oparty na podręczniku**.

#### **Zadanie 1: Elektryczny model zastępczy i anatomia potencjału (Wstęp \+ Rozdz. 3 podręcznika)**

* **Eksperyment:** Student ustawia pojedynczy bodziec (np. $\Delta t=0,5ms$) i bada zachowanie błony dla bodźca podprogowego (Ryc. 3b) oraz ponadprogowego (Ryc. 1), obserwując jednocześnie przebieg potencjału błonowego $U$ oraz przewodności błony dla jonów $N{a}^{+}$ i ${K}^{+}$ (odwrotności oporów ${R}_{Na}$ i ${R}_{K}$ z Ryc. 7).  
* **Zadanie graficzne / pomiarowe:** Odczytanie za pomocą kursora na wykresie symulatora (lub zaznaczenie na schemacie czasowym) dokładnych momentów czasowych ($t$) dla trzech zdarzeń: 1\) szczytu przepolaryzowania (+30 mV), 2\) maksymalnej przewodności dla $N{a}^{+}$, 3\) maksymalnej przewodności dla ${K}^{+}$ oraz odczytanie wartości przewodności potasowej w chwili wystąpienia następczego potencjału hiperpolaryzacyjnego.  
* **Wniosek dla studenta:** Powiązanie kształtu potencjału czynnościowego z modelem zastępczym Hodgkina-Huxleya: zrozumienie, dlaczego potencjał podprogowy narasta i opada wykładniczo (ładowanie kondensatora $C$) oraz dlaczego po repolaryzacji napięcie spada poniżej $-90mV$ (otwarte wciąż kanały potasowe – niski opór ${R}_{K}$ dążący do potencjału równowagowego potasu ${E}_{K}=-97mV$ z Ryc. 7).

#### **Zadanie 2: Krzywa pobudliwości, reobaza, chronaksja i bilans ładunku (Pkt 1–4 przebiegu ćwiczenia)**

* **Eksperyment:** Wyznaczenie metodą kolejnych przybliżeń (bisekcji) natężenia progowego ${I}_{p}$ dla kilku czasów trwania bodźca $\Delta t$ (w zakresie od $0,3ms$ do $4,0ms$, plus jeden bardzo długi bodziec np. $8–10ms$).  
* **Zadanie graficzne / pomiarowe:**  
  * Zamiast dwóch osobnych tabel jak w starym protokole (pkt 1 i pkt 2), **jedna zbiorcza tabela**: $\Delta t$, $1/\Delta t$, wyznaczone ${I}_{p}$ oraz obliczony ze wzoru (1) ładunek progowy $\Delta Q/S={I}_{p}\cdot \Delta t$.  
  * Student rysuje wykresy i wyznacza reobazę $R$ oraz chronaksję $CH$, ale staje przed problemem badawczym: *Na którym wykresie – ${I}_{p}=f(\Delta t)$, ${I}_{p}=f(1/\Delta t)$ czy $\Delta Q/S=f(\Delta t)$ – najłatwiej zauważyć i wytłumaczyć moment, w którym komórka zaczyna aktywnie bronić swojej homeostazy?*  
* **Wniosek dla studenta:** Wyjaśnienie (na bazie str. 177–178), dlaczego dla długich czasów stymulacji punkty uciekają z linii prostej, a potrzebny ładunek rośnie (rola pompy sodowo-potasowej wypompowującej ładunek w trakcie trwania długiego bodźca oraz narastającej akomodacji).

#### **Zadanie 3: Pojemność błony i kierunek polaryzacji – Sumowanie w czasie vs Hiperpolaryzacja (Ryc. 6 oraz Pkt 6 przebiegu ćwiczenia)**

* **Eksperyment A (Sumowanie w czasie – Ryc. 6):** Student ustawia dwa (lub trzy, jeśli rozbudujemy program zgodnie z Ryc. 6\) bodźce podprogowe o stałym natężeniu (np. $0,8\cdot {I}_{p}$). Zmienia wyłącznie czas przerwy między nimi, szukając granicznego odstępu czasu, poniżej którego bodźce wywołują potencjał czynnościowy.  
* **Eksperyment B (Hiperpolaryzacja – Pkt 6 ze str. 181):** Student podaje bodziec hiperpolaryzujący (ujemna gęstość prądu, czas trwania $5ms$, dokładnie jak w pkt 6 podręcznika) i sprawdza próg pobudliwości dla bodźca testującego podanego tuż po nim (lub obserwuje zachowanie błony po wyłączeniu silnej hiperpolaryzacji).  
* **Zadanie graficzne / pomiarowe:** Zestawienie wpływu wstępnej polaryzacji błony (krótka depolaryzacja vs długa hiperpolaryzacja) na wartość natężenia progowego drugiego bodźca (${I}_{p}'$ względem ${I}_{p}$).  
* **Wniosek dla studenta:** Zrozumienie roli pojemności elektrycznej błony w sumowaniu bodźców (drugi bodziec musi trafić w fazę wykładniczego opadania potencjału zanim ten wróci do spoczynku) oraz potwierdzenie tezy ze str. 178, że wstępna hiperpolaryzacja obniża próg pobudliwości poprzez ułatwienie aktywacji układu $N{a}^{+}$.

#### **Zadanie 4: Dwa mechanizmy wzrostu progu – Akomodacja vs Refrakcja względna (Pkt 5 i 7 przebiegu ćwiczenia)**

* **Eksperyment:** Każdy student bada i porównuje oba zjawiska (zamiast losowego wyboru jednego jak w starym protokole), używając układu dwóch bodźców:  
  1. **Akomodacja (wg Pkt 5 ze str. 181):** Pierwszy bodziec długi i podprogowy ($\Delta {t}_{1}=3,0ms$, natężenie stopniowo zwiększane podprogowo), po nim drugi bodziec testujący ($\Delta {t}_{2}=0,4ms$). Student wyznacza, jak bardzo wzrósł próg ${I}_{p}'$ dla drugiego bodźca.  
  2. **Refrakcja względna (wg Pkt 7 ze str. 181):** Pierwszy bodziec ponadprogowy (wywołuje pełny potencjał czynnościowy), drugi bodziec testujący ($\Delta {t}_{2}=0,4ms$) podany w fazie repolaryzacji/hiperpolaryzacji następczej (np. $3–6ms$ po pierwszym). Student wyznacza nowy próg ${I}_{p}'$ oraz notuje amplitudę powstałego drugiego potencjału czynnościowego.  
* **Zadanie graficzne / pomiarowe:** Porównawcza tabela lub wykres słupkowy pokazujący stosunek ${I}_{p}'/{I}_{p}$ w obu zjawiskach wraz z odczytanym z wykresów symulatora stanem przewodności ${g}_{Na}$ i ${g}_{K}$ w momencie startu drugiego bodźca.  
* **Wniosek dla studenta:** Odpowiedź na kluczowe zastrzeżenie autora podręcznika ze str. 179 (*„zmiany progu pobudliwości w okresie refrakcji względnej i wywołane zmianami potencjału błonowego to dwa zupełnie różne zjawiska”*) – wskazanie, że w akomodacji wzrost progu wynika z powolnej inaktywacji kanałów $N{a}^{+}$ przez długotrwałą depolaryzację podprogową, natomiast w refrakcji względnej nakłada się na to wysoka przewodność wciąż otwartych kanałów potasowych po poprzednim impulsie (co skutkuje też mniejszą amplitudą drugiego potencjału czynnościowego, o czym mówi str. 174).

### **4\. Podsumowanie zmian w przebudowywanym programie (100% zgodności z podręcznikiem)**

Aby program idealnie wspierał ten scenariusz i nie wprowadzał żadnych obcych pojęć:

1. **Zostawiamy wyłącznie bodźce prostokątne**, ale dodajemy opcję przełączenia z „2 bodźców” na „Serię 3 bodźców podprogowych” (dokładna realizacja Ryc. 6 ze str. 179).  
2. **Umożliwiamy wprowadzenie ujemnych wartości gęstości prądu $J$** dla pierwszego bodźca (wymóg konieczny do realizacji punktu 6 ze str. 181 – badanie hiperpolaryzacji).  
3. **Dodajemy kursor pomiarowy (odczyt wartości z wykresu po najechaniu myszką)** oraz przycisk **„Zatrzymaj przebieg w tle (Porównaj)”**, aby student po zmianie parametru widział na ekranie poprzedni przebieg linią przerywaną, a nowy linią ciągłą.  
4. **Podpisujemy osie wykresów przewodności terminologią z podręcznika:** np. *„Przewodność elektryczna błony dla $N{a}^{+}$ ($1/{R}_{Na}$)”* oraz *„Przewodność elektryczna błony dla ${K}^{+}$ ($1/{R}_{K}$)”* (nawiązanie wprost do Ryc. 7 i opisu ze str. 180).

