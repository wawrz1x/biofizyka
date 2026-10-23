Porównam warianty pod kątem dydaktyki, interaktywnych wykresów, modelu Hodgkina-Huxleya i późniejszego utrzymania przez zespół uczelni. Najważniejsze będzie rozdzielenie pytania „czy Streamlit wystarczy?” od „jaka architektura będzie najlepsza docelowo?”.Tak, istnieją rozwiązania dające większą swobodę niż Streamlit, ale **na obecnym etapie nie zmieniałbym języka ani nie przepisywał całego programu**. Dla Waszego symulatora najlepszy stosunek nakładu pracy do efektu daje nadal:

> **Python \+ Streamlit \+ Plotly**, z porządnym oddzieleniem modelu Hodgkina-Huxleya od interfejsu.

Zmianę na aplikację React/TypeScript rozważyłbym dopiero wtedy, gdy symulator ma stać się dopracowanym, publicznym „wirtualnym laboratorium”, a nie tylko aplikacją wspierającą ćwiczenia.

## **Krótka rekomendacja**

### **Teraz**

**Zostać przy Pythonie i Streamlit**, ponieważ:

* obliczenia modelu Hodgkina-Huxleya są naturalne w Pythonie,  
* można wykorzystać NumPy i SciPy,  
* wszystkie wymienione funkcje da się wdrożyć,  
* prowadzący łatwo sprawdzi i zmodyfikuje model,  
* nie trzeba utrzymywać dwóch języków,  
* koszty przebudowy będą wyraźnie niższe.

### **Docelowo, jeśli projekt mocno się rozwinie**

Najlepszą architekturą będzie:

* **Python** jako silnik obliczeniowy i referencyjna implementacja modelu,  
* **React \+ TypeScript** jako interfejs,  
* **Plotly.js** lub Apache ECharts jako warstwa wykresów,  
* ewentualnie **FastAPI** jako połączenie interfejsu z modelem.

Nie zmieniałbym natomiast całego projektu na C++, Javę czy MATLAB tylko ze względu na wydajność. Model pojedynczej błony Hodgkina-Huxleya jest zbyt mały obliczeniowo, aby uzasadniało to taką migrację.

---

# **Czy Streamlit obsłuży wskazane funkcje?**

## **1\. Tryb „Duch”**

**Tak, bez większych problemów.**

Po kliknięciu „Zapamiętaj jako przebieg referencyjny” zapisujecie w `st.session_state`:

st.session\_state\["reference\_trace"\] \= {  
	"t": result.t.copy(),  
	"V": result.V.copy(),  
	"g\_Na": result.g\_Na.copy(),  
	"g\_K": result.g\_K.copy(),  
	"stimulus": result.stimulus.copy(),  
	"parameters": current\_parameters.copy()  
}

Następnie w Plotly rysujecie:

* przebieg referencyjny: szary, przerywany, częściowo przezroczysty,  
* aktualny przebieg: kolorowy, ciągły,  
* bodziec referencyjny opcjonalnie jako cienką szarą linię.

To wręcz podręcznikowe zastosowanie `session_state`.

Warto dodać nie tylko „Zapisz przebieg”, lecz także:

* „Usuń przebieg referencyjny”,  
* „Zamień aktualny z referencyjnym”,  
* krótką etykietę parametrów referencji,  
* obliczenie różnicy, np. `ΔV = V_aktualne − V_referencyjne`.

## **2\. Generator serii impulsów**

**Streamlit spokojnie wystarczy.**

Panel może zawierać:

* amplitudę JJ,  
* czas trwania impulsu Δt\\Delta t,  
* liczbę impulsów N=2–10N \= 2–10,  
* odstęp lub częstotliwość,  
* początek serii,  
* opcjonalnie polaryzację bodźca.

Sam bodziec najlepiej generować jako tablicę niezależną od modelu:

def generate\_pulse\_train(t, amplitude, duration, interval, n\_pulses, start):  
	stimulus \= np.zeros\_like(t)  
	for i in range(n\_pulses):  
    	pulse\_start \= start \+ i \* interval  
    	pulse\_end \= pulse\_start \+ duration  
    	mask \= (t \>= pulse\_start) & (t \< pulse\_end)  
    	stimulus\[mask\] \= amplitude  
	return stimulus

Ważna uwaga dydaktyczna: dobrze byłoby umożliwić ustawienie zarówno:

* **odstępu między początkami impulsów**, jak i  
* **przerwy między końcem jednego a początkiem następnego**.

Studenci często mylą te dwie wartości. Interfejs powinien jasno pokazywać, która definicja jest używana.

## **3\. Rampa i bodziec trójkątny**

**Również do wykonania w obecnym systemie.**

Generator bodźców powinien mieć wspólny interfejs:

stimulus \= generate\_stimulus(  
	t=t,  
	shape="ramp",  
	amplitude=30.0,  
	start=10.0,  
	duration=80.0  
)

Kształty bodźca:

* prostokąt,  
* rampa narastająca,  
* trójkąt,  
* seria impulsów,  
* dwa impulsy,  
* impuls kondycjonujący i testujący.

W module akomodacji proponowałbym jednak nie używać wyłącznie „prądu końcowego”. Bardziej dydaktyczne będą jednocześnie dwa parametry:

* prąd końcowy J\_max⁡J\\\_{\\max},  
* szybkość narastania dJ/dtdJ/dt.

To przecież właśnie **szybkość narastania**, a nie sama wartość końcowa, rozstrzyga o odpowiedzi błony.

## **4\. Kursor pomiarowy**

To funkcja, przy której ujawnia się największa różnica między Streamlit a Reactem.

Plotly w Streamlit oferuje interaktywne wykresy, wartości przy najechaniu i obsługę wyboru punktów. Oficjalne API `st.plotly_chart` obsługuje zdarzenia wyboru przez `on_select`, a dane wyboru mogą być zapisane w stanie sesji. [\[docs.streamlit.io\]](https://docs.streamlit.io/develop/api-reference/charts/st.plotly_chart), [\[chart-sele...eamlit.app\]](https://chart-selections-demo.streamlit.app/)

### **W Streamlit można łatwo wykonać:**

* jedną pionową linię kursora dla wszystkich paneli,  
* wspólny hover po osi czasu,  
* odczyt:  
  * tt,  
  * V\_mV\\\_m,  
  * I\_stimI\\\_{\\mathrm{stim}},  
  * g\_Nag\\\_{\\mathrm{Na}},  
  * g\_Kg\\\_{\\mathrm{K}},  
  * mm, hh, nn,  
* powiększanie fragmentu wykresu,  
* zaznaczanie punktów,  
* eksport obrazu.

### **Ograniczenie**

Jeśli chcecie, żeby kursor:

* płynnie przesuwał się z myszą,  
* aktualizował osobny panel liczbowy bez ponownego wykonania aplikacji,  
* „przyklejał się” do próbki,  
* działał jak prawdziwy oscyloskop,

to **React \+ Plotly.js daje więcej kontroli**.

W Streamlit zdarzenia przesyłane z wykresu mogą prowadzić do ponownego uruchomienia skryptu. Dla zwykłego kliknięcia jest to akceptowalne, ale przy ciągłym ruchu myszy może być mniej płynne. Dlatego w pierwszej wersji zastosowałbym:

> zsynchronizowany hover Plotly \+ kliknięcie w punkt, które zatrzymuje kursor pomiarowy.

To zapewnia niemal cały efekt dydaktyczny bez zmiany technologii.

---

# **Wykres hh jest bardzo dobrym pomysłem, ale zmieniłbym jego nazwę**

Zamiast:

> „Wskaźnik inaktywacji Na⁺”

lepiej napisać:

> **Dostępność kanałów Na⁺, hh**

albo:

> **Odsetek kanałów Na⁺ dostępnych do aktywacji**

Powód jest istotny. W standardowym modelu Hodgkina-Huxleya:

* h≈1h \\approx 1 oznacza wysoką dostępność kanałów,  
* h≈0h \\approx 0 oznacza silną inaktywację.

Sam napis „inaktywacja hh” może skłonić studenta do błędnego wniosku, że większe hh oznacza większą inaktywację.

Wskaźnik może używać prostych progów dydaktycznych:

* h\>0,75h \> 0{,}75: wysoka dostępność,  
* 0,4≤h≤0,750{,}4 \\le h \\le 0{,}75: częściowa inaktywacja,  
* h\<0,4h \< 0{,}4: mała dostępność.

Trzeba jednak podpisać je jako **orientacyjne**, ponieważ nie są to uniwersalne progi fizjologiczne.

Na wykresie pokazywałbym także:

g\_Na(t)=gˉ\_Nam(t)3h(t)g\\\_{\\mathrm{Na}}(t)=\\bar g\\\_{\\mathrm{Na}}m(t)^3h(t)

Dzięki temu student zobaczy, dlaczego:

* w spoczynku g\_Nag\\\_{\\mathrm{Na}} jest małe, bo małe jest mm, ale hh pozostaje wysokie,  
* podczas akomodacji g\_Nag\\\_{\\mathrm{Na}} również może być małe, lecz tym razem z powodu obniżenia hh.

To dokładnie rozwiązuje problem „kanał zamknięty, ale gotowy” kontra „kanał niedostępny wskutek inaktywacji”.

---

# **Porównanie technologii**

| Rozwiązanie | Model H-H | UX i wykresy | Utrzymanie | Moja ocena |
| ----- | ----- | ----- | ----- | ----- |
| Python \+ Streamlit \+ Plotly | bardzo dobre | dobre | łatwe | **najlepsze teraz** |
| Python \+ Dash | bardzo dobre | bardzo dobre | średnie | dobra alternatywa |
| Python \+ NiceGUI | bardzo dobre | dobre/bardzo dobre | średnie | ciekawa alternatywa |
| React \+ TypeScript \+ Python/FastAPI | bardzo dobre | znakomite | trudniejsze | najlepsze docelowo |
| React \+ TypeScript, wszystko w przeglądarce | dobre | znakomite | średnie/trudne | dobre dla publicznej aplikacji |
| MATLAB App Designer | bardzo dobre | średnie | zależne od licencji | nie polecam do szerokiego wdrożenia |
| Jupyter Notebook/Voilà | bardzo dobre | przeciętne | łatwe | słabsze jako gotowy lab |

## **Plotly Dash**

To rozsądny krok pośredni. Nadal używacie Pythona, ale dostajecie bardziej bezpośredni model reaktywnych komponentów i callbacków.

Wybrałbym Dash zamiast Streamlit, jeśli:

* interakcje pomiędzy kilkoma wykresami stają się bardzo rozbudowane,  
* wiele elementów ma reagować na pojedyncze kliknięcie,  
* chcecie dokładnie kontrolować, co jest przeliczane,  
* rerun całego skryptu zaczyna powodować problemy.

Nie migrowałbym jednak tylko po to, żeby dodać Ghost Trace, rampę i serię impulsów. To nie uzasadnia przebudowy.

## **React \+ TypeScript**

To najlepszy wybór, gdy celem jest produkt przypominający rzeczywiste urządzenie laboratoryjne:

* płynny kursor oscyloskopowy,  
* przeciąganie znaczników bezpośrednio na wykresie,  
* animowane bramki kanałów,  
* synchronizacja kilku paneli,  
* zapis eksperymentów w przeglądarce,  
* responsywność na tabletach,  
* możliwość pracy offline,  
* rozbudowane scenariusze ćwiczeń.

Cena to większa złożoność. Trzeba utrzymywać osobno:

1. model matematyczny,  
2. API,  
3. interfejs,  
4. komunikację między nimi,  
5. testy zgodności wyników.

Dla uczelnianego zespołu oznacza to również większe uzależnienie od osoby znającej frontend.

---

# **A może obliczenia bez serwera?**

Można uruchomić Python bezpośrednio w przeglądarce przez Pyodide/WebAssembly. Istnieje też projekt stlite, który przenosi Streamlit do przeglądarki; udostępnia warianty do integracji z Reactem, aplikacji desktopowych i wdrożeń bez klasycznego serwera. [\[github.com\]](https://github.com/whitphx/stlite), [\[stlite.net\]](https://stlite.net/)

Taki wariant daje:

* brak serwera obliczeniowego,  
* możliwość działania offline,  
* łatwiejszą ochronę danych, bo parametry nie opuszczają urządzenia,  
* potencjalnie łatwe udostępnienie studentom.

Ale nie wybrałbym go jako pierwszej migracji. Środowisko WebAssembly zwiększa rozmiar początkowego ładowania i może mieć ograniczenia zgodności pakietów. Wczesne implementacje wymagały pobrania około 50 MB środowiska i nie obsługiwały wszystkich komponentów Streamlit. [\[discuss.streamlit.io\]](https://discuss.streamlit.io/t/new-library-stlite-a-port-of-streamlit-to-wasm-powered-by-pyodide/25556)

---

# **Architektura, którą wdrożyłbym już teraz**

Największym ryzykiem nie jest wybór języka. Jest nim umieszczenie modelu, generatora bodźców i interfejsu w jednym pliku Streamlit.

Proponowany układ:

action\_potential\_lab/  
│  
├── app.py  
├── model/  
│   ├── hodgkin\_huxley.py  
│   ├── parameters.py  
│   └── solver.py  
│  
├── stimuli/  
│   ├── rectangular.py  
│   ├── pulse\_train.py  
│   ├── ramp.py  
│   └── paired\_pulse.py  
│  
├── experiments/  
│   ├── threshold.py  
│   ├── temporal\_summation.py  
│   ├── accommodation.py  
│   └── refractory\_period.py  
│  
├── visualisation/  
│   ├── membrane\_plot.py  
│   ├── conductance\_plot.py  
│   └── gating\_plot.py  
│  
├── teaching/  
│   ├── hints.py  
│   ├── tasks.py  
│   └── interpretation.py  
│  
└── tests/  
	├── test\_resting\_state.py  
	├── test\_action\_potential.py  
	├── test\_stimuli.py  
	└── test\_refractory\_period.py

Wynik symulacji powinien mieć jedną, stabilną strukturę:

@dataclass  
class SimulationResult:  
	t: np.ndarray  
	V: np.ndarray  
	m: np.ndarray  
	h: np.ndarray  
	n: np.ndarray  
	g\_Na: np.ndarray  
	g\_K: np.ndarray  
	I\_Na: np.ndarray  
	I\_K: np.ndarray  
	I\_stim: np.ndarray  
	parameters: dict

Dzięki temu:

* Streamlit staje się tylko warstwą prezentacji,  
* wdrożenie Ghost Trace jest proste,  
* każdy generator bodźca zwraca taką samą strukturę,  
* późniejsza migracja do React/FastAPI nie wymaga przepisywania modelu,  
* można automatycznie sprawdzać wyniki.

---

# **Ostateczna decyzja**

## **Pozostałbym przy Streamlit, jeżeli:**

* aplikacja jest przeznaczona głównie na zajęcia,  
* obsługuje jednego studenta na sesję,  
* najważniejsze są poprawność modelu i zrozumienie zjawisk,  
* rozwój prowadzą osoby znające przede wszystkim Pythona,  
* nie potrzebujecie animacji działających z częstotliwością interfejsu oscyloskopowego.

## **Wybrałbym React \+ FastAPI, jeżeli:**

* aplikacja ma być publicznym produktem uczelni,  
* ma działać na wielu urządzeniach,  
* planujecie więcej modeli i ćwiczeń,  
* potrzebujecie bardzo płynnej interakcji z wykresami,  
* chcecie logowania, zapisywania wyników i raportów,  
* macie osobę mogącą utrzymywać TypeScript/React.

## **Moja rekomendacja dla Was**

> **Nie zmieniać teraz technologii. Przebudować kod modułowo w Pythonie, pozostać przy Streamlit i zastąpić statyczne wykresy przez Plotly.**

Następnie wdrażać w tej kolejności:

1. zunifikowany generator bodźców,  
2. wyświetlanie V\_mV\\\_m, bodźca, g\_Nag\\\_{\\mathrm{Na}}, g\_Kg\\\_{\\mathrm{K}}, mm, hh, nn,  
3. tryb Ghost Trace,  
4. seria impulsów,  
5. rampa i porównanie rampy z prostokątem,  
6. zsynchronizowany hover i zatrzymywany kliknięciem kursor,  
7. komunikaty dydaktyczne i pytania interpretacyjne.

To da prawie cały oczekiwany efekt bez ponoszenia kosztu migracji. Jednocześnie modułowa architektura pozostawi otwartą drogę do Reacta, jeśli później okaże się, że ograniczeniem jest rzeczywiście interfejs, a nie organizacja obecnego kodu.

