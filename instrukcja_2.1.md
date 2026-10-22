.**Instrukcja dla agenta kodującego Antigravity**

### **Cel zadania**

Przebuduj istniejącą aplikację symulującą potencjał czynnościowy z wersji 2.0 do wersji 2.1. Zachowaj rozdzielenie silnika numerycznego `hh_model.py` od interfejsu `app.py`, wykorzystującego Streamlit i Plotly.

Celem jest uzyskanie aplikacji:

* zgodnej terminologicznie i dydaktycznie z Rozdziałem 21 podręcznika;  
* ograniczającej wiedzę wykraczającą poza podręcznik do niezbędnego minimum;  
* umożliwiającej samodzielne projektowanie eksperymentów, wykonywanie pomiarów, dobór reprezentacji graficznej i wnioskowanie;  
* zachowującej poprawność numeryczną oraz uczciwie przedstawiającej ograniczenia modelu.

**Wykonaj zmiany w repozytorium, uruchom testy i przedstaw raport. Nie ograniczaj się do propozycji zmian. Nie deklaruj wykonania testów, których nie uruchomiono.**

---

### **1\. Najpierw przeprowadź audyt repozytorium i materiałów**

1. Przeczytaj istniejące:

   * `hh_model.py`;  
   * `app.py`;  
   * pliki zależności;  
   * testy;  
   * instrukcje i protokoły studenckie;  
   * dokumentację projektu.  
2. Sprawdź, czy w repozytorium znajduje się Rozdział 21 podręcznika lub jego wiarygodny eksport.

3. Jeśli podręcznik jest dostępny, zweryfikuj:

   * wartości napięć;  
   * nazewnictwo;  
   * opisy doświadczeń;  
   * ryciny 1, 3, 5, 6 i 7;  
   * polecenia dotyczące akomodacji, hiperpolaryzacji i refrakcji;  
   * definicje reobazy i chronaksji.  
4. Jeśli podręcznika nie ma:

   * traktuj wartości i wymagania z niniejszej instrukcji jako założenia przekazane przez zamawiającego;  
   * nie przedstawiaj ich jako niezależnie zweryfikowanych;  
   * nie twórz fikcyjnych cytowań ani numerów stron;  
   * wykonaj pozostałe prace, a brak weryfikacji źródłowej odnotuj w raporcie.  
5. Przed zmianami uruchom dostępne testy i zanotuj stan wyjściowy.

**Nie zastępuj brakującego podręcznika przypadkowymi materiałami internetowymi.**

---

### **2\. Zachowaj architekturę i rozdzielenie odpowiedzialności**

#### **`hh_model.py`**

Silnik odpowiada za:

* generowanie przebiegu bodźca;  
* całkowanie modelu;  
* obliczanie napięcia i przewodności;  
* przechowywanie wewnętrznych zmiennych modelu;  
* pomocnicze funkcje analizy odpowiedzi;  
* walidację parametrów.

Silnik nie może importować Streamlit ani tworzyć wykresów.

#### **`app.py`**

Interfejs odpowiada za:

* kontrolki stymulatora;  
* uruchamianie symulacji;  
* oscyloskop;  
* kursor pomiarowy;  
* Tryb Ducha;  
* dziennik pomiarowy;  
* kreator wykresu;  
* instrukcje dla studenta.

Dopuszczalne jest wydzielenie dodatkowych modułów pomocniczych, jeżeli uprości to testowanie. Nie przenoś obliczeń modelu do interfejsu.

---

### **3\. Skoryguj napięcia bez fałszowania działania modelu**

#### **Docelowe wartości dydaktyczne**

Zgodnie z przekazaną analizą aplikacja powinna dążyć do:

* potencjału spoczynkowego około **−90 mV**;  
* pomocniczego poziomu progu **−60 mV**;  
* szczytu potencjału czynnościowego około **\+30 mV**.

Wartości potencjałów równowagowych wskazane w analizie:

* `E_Na = +66 mV`;  
* `E_K = −97 mV`;  
* `E_Cl = −90 mV`.

#### **Obowiązkowe rozstrzygnięcie sprzeczności**

Nie wdrażaj automatycznie przesunięcia wszystkich napięć o −20 mV jako rozwiązania całego problemu.

Dla wartości przytoczonych w analizie takie przesunięcie daje:

* −70 → −90 mV;  
* −55 → −75 mV, **nie −60 mV**;  
* \+45 → \+25 mV;  
* −82 → −102 mV;  
* −59,4 → −79,4 mV.

**Samo przesunięcie nie zapewnia więc zgodności z podanymi wartościami podręcznikowymi.**

#### **Wymagana procedura**

1. Ustal konwencję napięcia rzeczywiście używaną w aktualnym kodzie.  
2. Sprawdź zależność funkcji kinetycznych od tej konwencji.  
3. Rozróżnij:  
   * zmianę współrzędnej napięcia;  
   * zmianę parametrów fizycznych modelu;  
   * zmianę samej prezentacji.  
4. Preferuj spójną kalibrację modelu, obejmującą parametry i kinetykę, zamiast kosmetycznego przesuwania wykresu.  
5. Jeżeli stosujesz transformację napięcia, zastosuj ją konsekwentnie do wszystkich zależnych wielkości i jawnie opisz w dokumentacji technicznej.  
6. Nie stosuj arbitralnego skalowania amplitudy wyłącznie po to, aby wykres osiągał \+30 mV.  
7. Nie wymuszaj potencjału czynnościowego przez instrukcję typu „po przekroczeniu −60 mV wygeneruj impuls”.  
8. Nie utożsamiaj linii pomocniczej −60 mV z uniwersalnym, stałym progiem dynamicznego modelu.

#### **Warunek odbioru**

Przedstaw wyniki pomiarów z rzeczywistych symulacji:

* napięcie równowagowe bez bodźca;  
* stabilność spoczynku;  
* amplitudę odpowiedzi ponadprogowej;  
* zachowanie odpowiedzi w pobliżu progu;  
* wpływ kroku czasowego na wyniki.

Zaproponuj i uzasadnij tolerancje przed oceną końcową. Jeśli nie da się jednocześnie spełnić wszystkich celów, opisz kompromis zamiast deklarować pozorną zgodność.

#### **Prąd przecieku a chlorki**

**Nie zmieniaj wyłącznie etykiety istniejącego prądu przecieku na prąd chlorkowy.**

* Jeżeli model ma zawierać gałąź chlorkową zgodną z ryciną, zaimplementuj ją jawnie i zweryfikuj jej wpływ na równowagę.  
* Jeśli pozostaje ogólny prąd przecieku, nie przedstawiaj go jako wyłącznie chlorkowego.  
* Parametry techniczne niewymagane dydaktycznie mogą pozostać ukryte przed studentem.

---

### **4\. Usuń z interfejsu treści wykraczające poza przyjęty zakres**

Usuń ze wszystkich elementów widocznych dla studenta:

* wykresy zmiennych `m`, `h`, `n`;  
* pasek dostępności kanałów oparty na `h`;  
* odczyt „stan bramki h w piku”;  
* równania kinetyczne bramek;  
* objaśnienia wymagające znajomości tych zmiennych.

Dotyczy to również:

* podpowiedzi;  
* legend;  
* komunikatów;  
* rozwijanych paneli;  
* opisów zadań;  
* standardowych eksportów studenckich.

Zmienne bramkowania pozostają w silniku i testach technicznych.

Zachowaj prezentację:

* przewodności sodowej;  
* przewodności potasowej;  
* opisowego pojęcia inaktywacji układu sodowego, jeżeli potwierdza je materiał źródłowy.

Zastąp nazwę „Krzywa Weissa-Lapicque’a” określeniem:

**„Zależność natężenia bodźca progowego od czasu trwania: Iₚ \= f(Δt)”**.

Nie dodawaj nowych nazw i mechanizmów tylko dlatego, że występują w implementacji modelu.

---

### **5\. Przebuduj stymulator**

Udostępnij wyłącznie trzy tryby:

1. **Pojedynczy bodziec**.  
2. **Dwa bodźce**.  
3. **Seria 3 bodźców**.

Wszystkie bodźce mają być prostokątne.

Usuń rampę z:

* wyboru trybu;  
* instrukcji;  
* zadań;  
* presetów;  
* aktywnych ścieżek interfejsu.

Nieużywaną implementację rampy usuń albo odizoluj poza zakresem aplikacji studenckiej.

#### **Parametry**

Zapewnij możliwość ustawiania:

* amplitudy;  
* czasu trwania;  
* początku bodźca;  
* odstępu między bodźcami.

Dla dwóch bodźców umożliwiaj niezależne amplitudy i czasy trwania.

Dla serii trzech bodźców umożliwiaj konfigurację potrzebną do samodzielnego badania sumowania.

Amplituda musi dopuszczać:

* wartości dodatnie;  
* zero;  
* wartości ujemne.

Zdefiniuj jednoznacznie, czy odstęp oznacza czas między końcem pierwszego a początkiem drugiego bodźca. Preferuj tę definicję i opisz ją w interfejsie.

Obsłuż poprawnie zerowy odstęp. Jeżeli dopuszczasz nakładanie impulsów, określ i przetestuj sposób sumowania prądów.

#### **Jednostki**

Podstawowa etykieta amplitudy:

**„Gęstość prądu bodźca J \[µA/cm²\]”**.

W dzienniku możesz stosować oznaczenie `Iₚ`, zgodnie z wymaganiem dydaktycznym, ale wyjaśnij, że w tej aplikacji oznacza ono progową gęstość prądu. Nie mieszaj prądu całkowitego z gęstością prądu.

---

### **6\. Ogranicz presety do dwóch ustawień startowych**

Pozostaw tylko:

1. **Bodziec podprogowy**.  
2. **Bodziec ponadprogowy**.

Zweryfikuj ich działanie po kalibracji modelu.

Usuń presety rozwiązujące zadania dotyczące:

* sumowania;  
* akomodacji;  
* hiperpolaryzacji;  
* refrakcji względnej;  
* refrakcji bezwzględnej.

Nie zastępuj ich przyciskami demonstracyjnymi o innych nazwach, które wykonują tę samą pracę za studenta.

Techniczne scenariusze testowe mogą zawierać gotowe konfiguracje, ale nie mogą być dostępne jako rozwiązania w interfejsie studenckim.

---

### **7\. Zintegruj oscyloskop w jednym widoku**

Zastąp osobną zakładkę z mechanizmem jonowym jednym ekranem zawierającym trzy panele w kolejności:

1. **Potencjał błonowy U(t) \[mV\]**.  
2. **Przewodności sodowa i potasowa**.  
3. **Gęstość prądu bodźca J(t) \[µA/cm²\]**.

Wszystkie panele muszą mieć:

* wspólną oś czasu;  
* zsynchronizowane powiększanie i przesuwanie;  
* wspólny pionowy kursor;  
* zgodne odczyty czasu.

Przewodności opisuj jako `g_Na = 1/R_Na` oraz `g_K = 1/R_K`. Jeśli model używa wielkości odniesionych do powierzchni, zastosuj odpowiednie jednostki i wyjaśnij konwencję w dokumentacji.

#### **Kursor pomiarowy**

Dla wybranego czasu pokaż:

* czas;  
* napięcie;  
* przewodność sodową;  
* przewodność potasową;  
* gęstość prądu bodźca.

Nie pokazuj bramek.

Zweryfikuj rzeczywiste działanie kursora we wszystkich panelach. Sama konfiguracja podpowiedzi nie jest wystarczającym dowodem synchronizacji.

Jeżeli używane wersje bibliotek nie zapewniają wspólnego kursora przy najechaniu, zastosuj działające rozwiązanie zastępcze, np. wspólny wybór czasu sterujący linią i odczytami.

#### **Linie pomocnicze**

Dodaj:

* poziom spoczynkowy −90 mV;  
* podręcznikowy poziom odniesienia −60 mV.

Opis linii nie może sugerować, że model ma niezmienny próg niezależny od historii pobudzenia.

---

### **8\. Zachowaj i rozszerz Tryb Ducha**

Przycisk **„Zamroź ślad”** zapisuje niezależną kopię:

* czasu;  
* napięcia;  
* obu przewodności;  
* bodźca;  
* konfiguracji eksperymentu;  
* identyfikatora konfiguracji modelu.

Zamrożone przebiegi pokaż jako szare lub przerywane na wszystkich trzech panelach.

Zapewnij:

* czytelne odróżnienie aktualnego i zamrożonego przebiegu;  
* możliwość usunięcia śladu;  
* brak nadpisywania zamrożonych danych przy zmianie suwaków;  
* poprawne porównanie przebiegów o różnych siatkach czasu.

Nie przesuwaj automatycznie przebiegów względem siebie. Ewentualne wyrównanie musi być jawną operacją użytkownika.

Po zmianie konfiguracji modelu oznacz niezgodność starego śladu albo go unieważnij z czytelnym komunikatem.

---

### **9\. Przebuduj dziennik pomiarowy i kreator wykresu**

#### **Dziennik**

Dziennik ma gromadzić surowe pomiary, przede wszystkim:

* czas trwania bodźca `Δt [ms]`;  
* progową gęstość prądu `Iₚ [µA/cm²]`.

Dodaj identyfikator pomiaru i możliwość zapisania notatki. Konfigurację eksperymentu przechowuj jako metadane.

Zapewnij:

* dodawanie pomiarów;  
* usuwanie wybranych rekordów;  
* czyszczenie z zabezpieczeniem przed przypadkową utratą;  
* eksport CSV z jednostkami;  
* zachowanie danych podczas standardowych ponownych uruchomień interfejsu.

Nie zapisuj bieżącej amplitudy jako „progu”, jeśli student nie wykonał procedury jego wyznaczania.

#### **Wyznaczanie progu**

Domyślnie student sam zmienia amplitudę i zawęża przedział między odpowiedzią podprogową a ponadprogową.

Możesz udostępnić pomoc w ręcznej bisekcji, np. obliczenie środka przedziału. Nie uruchamiaj automatycznego wyszukiwania progu po kliknięciu „Zapisz punkt”.

Jeżeli istnieje automatyczna bisekcja:

* zachowaj ją do testów lub jawnego trybu prowadzącego;  
* usuń ją z domyślnej ścieżki studenckiej;  
* nie udostępniaj automatycznego skanowania całej charakterystyki.

#### **Kolumny obliczeniowe**

Przycisk **„Dodaj kolumnę obliczeniową”** pozwala studentowi jawnie dodać:

* `1/Δt [1/ms]`;  
* `ΔQ/S = Iₚ · Δt [nC/cm²]`.

Nie dodawaj tych kolumn automatycznie.

Sprawdź przeliczenie jednostek:

`µA/cm² × ms = nC/cm²`.

Odrzucaj zerowe i ujemne czasy trwania.

#### **Jeden kreator wykresu**

Usuń trzy automatyczne wykresy.

Udostępnij jeden kreator, w którym student wybiera:

**Oś X:**

* `Δt [ms]`;  
* `1/Δt [1/ms]`, jeśli dodano tę kolumnę.

**Oś Y:**

* `Iₚ [µA/cm²]`;  
* `ΔQ/S [nC/cm²]`, jeśli dodano tę kolumnę.

Wykres powstaje po świadomym wyborze osi i użyciu przycisku **„Utwórz / aktualizuj wykres”**.

Nie ustawiaj domyślnie „właściwego” rozwiązania zadania.

#### **Regresja**

Dodaj domyślnie wyłączoną opcję dopasowania prostej dla:

* `X = 1/Δt`;  
* `Y = Iₚ`.

Student sam wybiera punkty lub zakres dopasowania.

Nie wykonuj automatycznie:

* wyboru „najlepszego” zakresu;  
* odrzucania punktów;  
* usuwania obserwacji dla długich czasów;  
* interpretacji odstępstw.

Sprawdź, czy wybrane dane umożliwiają dopasowanie, w tym czy zawierają co najmniej dwie różne wartości X.

Możesz pokazać prostą i jej równanie na żądanie. **Nie podpisuj automatycznie wyrazu wolnego jako gotowej reobazy i nie obliczaj chronaksji za studenta.**

Zapewnij ręczne pola na:

* wyznaczoną reobazę;  
* wyznaczoną chronaksję;  
* opis metody;  
* wnioski.

---

### **10\. Dostosuj zadania i protokół**

Zachowaj schemat:

**zadanie → projekt eksperymentu → pomiar → wybór wykresu → interpretacja → wnioski**.

Zaktualizuj wszystkie odwołania do usuniętych zakładek, rampy i bramek.

#### **Akomodacja**

Zadanie ma umożliwiać porównanie:

* samego krótkiego bodźca testującego;  
* tego samego bodźca poprzedzonego długim bodźcem podprogowym.

Uwzględnij możliwość ustawienia:

* pierwszego bodźca o czasie 3,0 ms;  
* drugiego bodźca o czasie 0,4 ms;  
* zmiennej amplitudy i odstępu.

Student sam wyznacza amplitudę testującą i korzysta z Trybu Ducha.

**Nie traktuj podanego w analizie przykładu 20 µA/cm² jako gwarantowanego progu po przebudowie modelu.**

Pytania mają kierować uwagę na napięcie i przewodności, ale nie podawać gotowego wniosku.

#### **Hiperpolaryzacja**

Umożliwiaj:

* pojedynczy ujemny bodziec, np. o czasie 5 ms;  
* ujemny bodziec poprzedzający dodatni bodziec testujący;  
* porównanie z kontrolą bez bodźca wstępnego.

Nie gwarantuj, że dowolna hiperpolaryzacja obniży próg. Zbadaj zależność od amplitudy, czasu i odstępu.

Ewentualne pobudzenie po zakończeniu ujemnego bodźca traktuj jako możliwy wynik modelu, a nie obowiązkowy efekt. Nie dodawaj angielskiego terminu „rebound spike” do podstawowego interfejsu.

#### **Sumowanie**

Udostępnij trzy bodźce prostokątne, ale pozostaw studentowi dobór amplitud i odstępów.

#### **Refrakcja**

Pozostaw zadanie samodzielnego zaprojektowania doświadczenia.

Nie dodawaj presetów ani automatycznych komunikatów wskazujących, że aktualna konfiguracja jest gotowym przykładem refrakcji względnej lub bezwzględnej.

---

### **11\. Wprowadź kontrolę zakresu „maksymalnie 10% poza podręcznikiem”**

Nie deklaruj matematycznie potwierdzonego spełnienia limitu, jeśli nie zdefiniowano sposobu jego liczenia.

Przygotuj rejestr treści widocznych dla studenta, klasyfikując je jako:

1. potwierdzone w podręczniku;  
2. konieczne objaśnienia obsługi;  
3. rozszerzenia merytoryczne;  
4. treści wymagające weryfikacji.

Dla rozszerzeń podaj uzasadnienie ich niezbędności. Usuń rozszerzenia zbędne.

Wewnętrzna implementacja modelu nie jest sama w sobie treścią dydaktyczną, dopóki nie jest prezentowana studentowi.

---

### **12\. Testy i kryteria odbioru**

#### **Silnik numeryczny**

Przetestuj:

* stabilny spoczynek bez bodźca;  
* odpowiedź podprogową i ponadprogową;  
* hiperpolaryzację;  
* dwa i trzy bodźce;  
* zerową amplitudę;  
* granice czasowe impulsów;  
* brak `NaN` i nieskończoności;  
* odporność funkcji kinetycznych w punktach numerycznie problematycznych;  
* wpływ zmniejszenia kroku czasowego;  
* poprawność jednostek.

Detekcja odpowiedzi używana w testach nie może opierać się wyłącznie na przekroczeniu linii −60 mV. Zdefiniuj i udokumentuj kryterium odróżniające potencjał czynnościowy od biernej depolaryzacji.

#### **Scenariusze dydaktyczne**

Sprawdź, czy model umożliwia znalezienie konfiguracji pokazujących:

* sumowanie;  
* akomodację;  
* refrakcję względną;  
* refrakcję bezwzględną;  
* wpływ poprzedzającej hiperpolaryzacji na odpowiedź testującą.

Zapisz rzeczywiste konfiguracje i wyniki w dokumentacji technicznej, nie jako presety studenckie.

Jeżeli efekt nie występuje, nie fałszuj przebiegów i nie dopisuj oczekiwanego wniosku. Zgłoś ograniczenie oraz proponowaną korektę modelu.

#### **Interfejs**

Sprawdź:

* dokładnie trzy tryby stymulatora;  
* brak rampy i bramek w treściach studenckich;  
* tylko dwa presety startowe;  
* trzy zsynchronizowane panele;  
* działający wspólny kursor;  
* Tryb Ducha na wszystkich panelach;  
* trwałość dziennika;  
* poprawność eksportu;  
* brak automatycznego wyliczania reobazy i chronaksji;  
* brak automatycznego tworzenia trzech wykresów;  
* poprawność polskich etykiet i jednostek.

#### **Dokumentacja końcowa**

Dostarcz:

1. listę zmienionych plików;  
2. opis zmian modelu i konwencji napięcia;  
3. wyniki uruchomionych testów;  
4. instrukcję uruchomienia aplikacji;  
5. checklistę spełnionych wymagań;  
6. listę ograniczeń i elementów wymagających weryfikacji podręcznikowej;  
7. krótką instrukcję ręcznego sprawdzenia aplikacji przez prowadzącego.

**Warunek zakończenia: aplikacja ma wspierać samodzielne badanie zjawisk, a nie generować za studenta eksperyment, analizę i wnioski.**

---

**Najważniejsze doprecyzowania:** instrukcja zachowuje zakres analizy, ale blokuje trzy ryzykowne skróty: pozorną korektę napięć samym offsetem, przemianowanie przecieku na chlorki bez zmiany modelu oraz automatyczne wyznaczanie progu pod pozorem samodzielnego pomiaru.

