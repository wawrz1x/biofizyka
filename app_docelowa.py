import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from scipy import stats

# -----------------------------------------------------------------------------
# KONFIGURACJA STRONY STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Wirtualna Pracownia Biofizyki Medycznej",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estetyczne style CSS
st.markdown("""
<style>
    .main-title {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E3A8A;
        margin-bottom: 0.2rem;
    }
    .sub-title {
        font-size: 1.1rem;
        color: #4B5563;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background-color: #F3F4F6;
        border-radius: 8px;
        padding: 12px;
        border-left: 4px solid #2563EB;
        margin-bottom: 10px;
    }
    .clinical-box {
        background-color: #EFF6FF;
        border-left: 5px solid #3B82F6;
        padding: 14px;
        border-radius: 6px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .warning-box {
        background-color: #FEF3C7;
        border-left: 5px solid #F59E0B;
        padding: 14px;
        border-radius: 6px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
    .success-box {
        background-color: #ECFDF5;
        border-left: 5px solid #10B981;
        padding: 14px;
        border-radius: 6px;
        margin-top: 15px;
        margin-bottom: 15px;
    }
</style>
""", unsafe_allow_html=True)


# =============================================================================
# MODUŁ 1: POTENCJAŁ CZYNNOŚCIOWY (MODEL HODGKINA-HUXLEYA I PRAWO WEISSA)
# =============================================================================

def alpha_n(v):
    x = -v - 60.0
    return 0.1 if abs(x) < 1e-6 else 0.01 * x / (np.exp(x / 10.0) - 1.0)

def beta_n(v):
    return 0.125 * np.exp((-v - 70.0) / 80.0)

def alpha_m(v):
    x = -v - 45.0
    return 1.0 if abs(x) < 1e-6 else 0.1 * x / (np.exp(x / 10.0) - 1.0)

def beta_m(v):
    return 4.0 * np.exp((-v - 70.0) / 18.0)

def alpha_h(v):
    return 0.07 * np.exp((-v - 70.0) / 20.0)

def beta_h(v):
    return 1.0 / (np.exp((-v - 40.0) / 10.0) + 1.0)


def symuluj_hh(
    stim1_amp=50.0, stim1_dur=1.0, stim1_start=2.0,
    use_stim2=False, stim2_amp=50.0, stim2_dur=1.0, interval=5.0,
    block_na=0.0, block_k=0.0,
    t_max=30.0, dt=0.01
):
    """
    Numeryczne rozwiązanie układu równań Hodgkina-Huxleya (1952) metodą Eulera.
    Zwraca tablice czasów, napięć, prądów bodźca, przewodności i stanów bramek.
    """
    steps = int(t_max / dt)
    times = np.linspace(0, t_max, steps)
    
    voltages = np.zeros(steps)
    i_stim = np.zeros(steps)
    g_na_arr = np.zeros(steps)
    g_k_arr = np.zeros(steps)
    m_arr = np.zeros(steps)
    h_arr = np.zeros(steps)
    n_arr = np.zeros(steps)
    
    # Warunki spoczynkowe dla V = -70 mV
    mv = -70.0
    an, bn = alpha_n(mv), beta_n(mv)
    am, bm = alpha_m(mv), beta_m(mv)
    ah, bh = alpha_h(mv), beta_h(mv)
    
    n = an / (an + bn)
    m = am / (am + bm)
    h = ah / (ah + bh)
    
    # Maksymalne przewodności z uwzględnieniem blokerów farmakologicznych
    gna_max = 120.0 * (1.0 - block_na / 100.0)
    gk_max = 36.0 * (1.0 - block_k / 100.0)
    gl = 0.3
    
    stim2_start = stim1_start + stim1_dur + interval
    
    for i, t in enumerate(times):
        # Kinetyka bramek
        an, bn = alpha_n(mv), beta_n(mv)
        am, bm = alpha_m(mv), beta_m(mv)
        ah, bh = alpha_h(mv), beta_h(mv)
        
        n += (an * (1.0 - n) - bn * n) * dt
        m += (am * (1.0 - m) - bm * m) * dt
        h += (ah * (1.0 - h) - bh * h) * dt
        
        gk = gk_max * (n ** 4)
        gna = gna_max * (m ** 3) * h
        
        # Prądy jonowe (wg konwencji ac.py: I = g*(E - V))
        ik = gk * (-mv - 82.0)
        ina = gna * (-mv + 45.0)
        ilk = gl * (-mv - 59.4)
        
        ia = 0.0
        if stim1_start <= t < stim1_start + stim1_dur:
            ia += stim1_amp
        if use_stim2 and (stim2_start <= t < stim2_start + stim2_dur):
            ia += stim2_amp
            
        mv += (ina + ik + ilk + ia) * dt
        
        voltages[i] = mv
        i_stim[i] = ia
        g_na_arr[i] = gna
        g_k_arr[i] = gk
        m_arr[i] = m
        h_arr[i] = h
        n_arr[i] = n
        
    return {
        "t": times,
        "V": voltages,
        "I_stim": i_stim,
        "g_Na": g_na_arr,
        "g_K": g_k_arr,
        "m": m_arr,
        "h": h_arr,
        "n": n_arr,
        "max_v": np.max(voltages),
        "min_v": np.min(voltages)
    }


@st.cache_data
def znajdz_prog_hh(stim_dur, low=0.1, high=200.0, tol=0.05):
    """
    Wyznacza natężenie bodźca progowego Ip dla zadanego czasu trwania stim_dur metodą bisekcji.
    Potencjał czynnościowy uznaje się za wyzwolony, gdy maksymalne napięcie przekroczy 0 mV.
    Wynik jest buforowany w pamięci (@st.cache_data), co eliminuje opóźnienia.
    """
    for _ in range(20):
        mid = (low + high) / 2.0
        res = symuluj_hh(stim1_amp=mid, stim1_dur=stim_dur, stim1_start=2.0, t_max=25.0)
        if res["max_v"] > 0.0:
            high = mid
        else:
            low = mid
        if (high - low) < tol:
            break
    return round((low + high) / 2.0, 2)


@st.cache_data
def get_weiss_reference_data():
    """Oblicza wzorcową serię Weissa raz i buforuje w pamięci."""
    durs = np.array([0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 2.0, 5.0, 10.0, 20.0])
    ips = np.array([znajdz_prog_hh(d) for d in durs])
    inv_durs = 1.0 / durs
    charges = durs * ips
    slope, intercept, r_value, p_value, std_err = stats.linregress(inv_durs, ips)
    return {
        "durs": durs,
        "ips": ips,
        "inv_durs": inv_durs,
        "charges": charges,
        "slope": slope,
        "intercept": intercept,
        "r_value": r_value,
        "reobaza": intercept,
        "u_coef": slope,
        "chronaksja": slope / intercept
    }


def render_tab_potencjal():
    st.markdown('<div class="main-title">⚡ Potencjał Czynnościowy & Pobudliwość Komórkowa</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Model Hodgkina-Huxleya (1952), Prawo Weissa-Lapicque\'a, Refrakcja i Reobaza/Chronaksja</div>', unsafe_allow_html=True)
    
    with st.expander("📘 Informacje teoretyczne i cele ćwiczenia (zgodnie z protokołem L09b)"):
        st.markdown(r"""
        **Cel ćwiczenia:**
        1. Zbadanie zależności natężenia bodźca progowego $I_p$ od czasu jego trwania $\Delta t$ (krzywa Weissa-Lapicque'a).
        2. Linearyzacja zależności $I_p = f(1/\Delta t)$ i wyznaczenie parametrów pobudliwości: **reobazy ($R$)** oraz **chronaksji ($CH$)**.
        3. Obserwacja zjawisk elektrofizjologicznych:
           - **Sumowanie podprogowe** (temporal summation),
           - **Okres refrakcji bezwzględnej i względnej**,
           - **Hiperpolaryzacja i pobudzenie z wyłączenia** (*anodal break excitation* / rebound spike).
        
        **Kluczowe równania:**
        - **Prawo Weissa:** $I_p = R + \frac{u}{\Delta t}$, gdzie $u = R \cdot CH$ (minimalny ładunek progowy $Q_0$).
        - **Model Hodgkina-Huxleya:**
          $$C_m \frac{dV}{dt} = I_{bodźca} - \left(\bar{g}_{Na}m^3h(V-E_{Na}) + \bar{g}_K n^4(V-E_K) + g_L(V-E_L)\right)$$
        """)

    col_ctrl, col_plot = st.columns([1, 2])
    
    with col_ctrl:
        st.subheader("🎛️ Parametry Stymulacji")
        tryb_badania = st.selectbox(
            "Wybierz tryb eksperymentu:",
            [
                "1. Wirtualny stymulator & Szukanie progu Ip (do protokołu)",
                "2. Dwa bodźce: Refrakcja i Sumowanie czasowe",
                "3. Hiperpolaryzacja i Zjawisko Odbicia (Anodal Break)",
                "4. Wpływ Farmakologii (Znieczulenie miejscowe / Toksyny)"
            ]
        )
        
        if tryb_badania.startswith("1."):
            st.markdown("**Wyznaczanie progu pobudliwości $I_p$:**")
            czas_opcja = st.selectbox(
                "Wybierz czas trwania bodźca Δt z protokołu [ms]:",
                [0.1, 0.2, 0.3, 0.5, 0.8, 1.0, 2.0, 5.0, 10.0, 15.0, 20.0, "Inna wartość (suwak)"],
                index=5 # 1.0 ms
            )
            if czas_opcja == "Inna wartość (suwak)":
                stim1_dur = st.slider("Czas trwania bodźca Δt [ms]:", min_value=0.1, max_value=25.0, value=1.0, step=0.1)
            else:
                stim1_dur = float(czas_opcja)
                
            stim1_amp = st.slider(
                "Natężenie bodźca I₁ [µA/cm²]:", 
                min_value=0.0, max_value=80.0, value=5.0, step=0.2,
                help="Stopniowo zwiększaj natężenie pokrętłem/suwakiem, aż komórka wygeneruje potencjał czynnościowy (iglicę powyżej 0 mV)."
            )
            use_stim2 = False
            stim2_amp, stim2_dur, interval = 0.0, 1.0, 5.0
            block_na, block_k = 0.0, 0.0
            t_max = max(25.0, stim1_dur + 10.0)
            
            with st.expander("💡 Pokaż teoretyczny próg (podpowiedź dla studenta)"):
                prog_auto = znajdz_prog_hh(stim1_dur)
                st.caption(f"Dla Δt = {stim1_dur:.1f} ms dokładny próg wynosi: **{prog_auto:.2f} µA/cm²**")

        elif tryb_badania.startswith("2."):
            st.markdown("Badanie odpowiedzi błony na dwa kolejne bodźce w zmiennym odstępie czasu $\\Delta\\tau$.")
            typ_dwa_bodzce = st.radio("Scenariusz:", ["Badanie Refrakcji (bodziec 1 ponadprogowy)", "Sumowanie Podprogowe (dwa słabe bodźce)"])
            
            if typ_dwa_bodzce == "Badanie Refrakcji (bodziec 1 ponadprogowy)":
                stim1_amp = st.slider("Bodziec 1 I₁ [µA/cm²]:", min_value=20.0, max_value=100.0, value=50.0, step=5.0)
                stim1_dur = st.slider("Czas bodźca 1 Δt₁ [ms]:", 0.5, 3.0, 1.0, 0.1)
                interval = st.slider("Odstęp między bodźcami Δτ [ms]:", min_value=0.5, max_value=15.0, value=4.0, step=0.2)
                stim2_amp = st.slider("Bodziec 2 I₂ [µA/cm²]:", min_value=5.0, max_value=150.0, value=50.0, step=5.0)
                stim2_dur = 1.0
                use_stim2 = True
            else:
                stim1_amp = st.slider("Bodziec 1 (podprogowy) I₁ [µA/cm²]:", min_value=1.0, max_value=10.0, value=5.0, step=0.2)
                stim1_dur = 1.0
                interval = st.slider("Odstęp między bodźcami Δτ [ms]:", min_value=0.2, max_value=5.0, value=0.8, step=0.1)
                stim2_amp = st.slider("Bodziec 2 (podprogowy) I₂ [µA/cm²]:", min_value=1.0, max_value=10.0, value=5.0, step=0.2)
                stim2_dur = 1.0
                use_stim2 = True
                
            block_na, block_k = 0.0, 0.0
            t_max = 35.0

        elif tryb_badania.startswith("3."):
            st.markdown("Badanie skutków podania impulsu hiperpolaryzującego (ujemnego).")
            stim1_amp = st.slider("Amplituda prądu hiperpolaryzującego [µA/cm²]:", min_value=-40.0, max_value=-2.0, value=-15.0, step=1.0)
            stim1_dur = st.slider("Czas trwania impulsu [ms]:", min_value=1.0, max_value=15.0, value=5.0, step=0.5)
            use_stim2 = False
            stim2_amp, stim2_dur, interval = 0.0, 1.0, 5.0
            block_na, block_k = 0.0, 0.0
            t_max = 30.0

        else: # Farmakologia
            st.markdown("Wpływ leków znieczulających miejscowo (blokada $Na_v$) i leków przeciwarytmicznych.")
            stim1_amp = st.slider("Natężenie bodźca I₁ [µA/cm²]:", 5.0, 50.0, 25.0, 1.0)
            stim1_dur = 1.0
            block_na = st.slider("Blokada kanałów Na⁺ (np. Lignokaina, TTX) [%]:", 0.0, 100.0, 50.0, 5.0)
            block_k = st.slider("Blokada kanałów K⁺ (np. TEA) [%]:", 0.0, 100.0, 0.0, 5.0)
            use_stim2 = False
            stim2_amp, stim2_dur, interval = 0.0, 1.0, 5.0
            t_max = 25.0

    # Symulacja standardowa
    sim = symuluj_hh(
        stim1_amp=stim1_amp, stim1_dur=stim1_dur, stim1_start=2.0,
        use_stim2=use_stim2, stim2_amp=stim2_amp, stim2_dur=stim2_dur, interval=interval,
        block_na=block_na, block_k=block_k, t_max=t_max
    )
    
    # Detekcja iglic potencjału czynnościowego (szczyty powyżej 0 mV)
    v_trace = sim["V"]
    t_trace = sim["t"]
    peaks_idx = [k for k in range(1, len(v_trace)-1) 
                 if v_trace[k] > 0.0 and v_trace[k] > v_trace[k-1] and v_trace[k] > v_trace[k+1]]
    num_peaks = len(peaks_idx)
    peak_times = [t_trace[k] for k in peaks_idx]
    
    with col_plot:
        # Status pobudzenia i wyjaśnienie liczby iglic
        if num_peaks == 0:
            st.warning(f"⚠️ **ODPOWIEDŹ PODPROGOWA / BRAK PEŁNEGO AP.** Maksymalna depolaryzacja: **{sim['max_v']:.1f} mV** (nie przekroczyła 0 mV). Zwiększaj natężenie bodźca I₁!")
        elif num_peaks == 1:
            st.success(f"✅ **POTENCJAŁ CZYNNOŚCIOWY WYGENEROWANY (pojedyncza iglica)!** Szczyt: **+{sim['max_v']:.1f} mV** w chwili t = {peak_times[0]:.1f} ms. **👉 Zapisz próg Ip = {stim1_amp:.2f} µA/cm² w Tabeli 1 protokołu dla Δt = {stim1_dur:.1f} ms!**")
        else:
            st.info(f"💡 **POBUDZENIE CIĄGŁE / WYŁADOWANIE SERYJNE!** Wygenerowano **{num_peaks} potencjały czynnościowe** (szczyty w chwilach: {', '.join([f'{p:.1f}' for p in peak_times])} ms).")
            st.markdown(r"""
            > 🧠 **Fizjologia wyładowań seryjnych (*Repetitive Firing*):**  
            > **Czy to prawidłowe, że długi bodziec wywołuje 2 potencjały?**  
            > **TAK, w 100% fizjologicznie prawidłowe!** Po pierwszym potencjale następuje repolaryzacja i refrakcja. Ponieważ bodziec prądowy jest długi i nadal trwa, to po wyjściu z okresu refrakcji błona zostaje **ponownie zdepolaryzowana do progu**, wyzwalając kolejny impuls! Tak neurony kodują siłę bodźca częstotliwością impulsów (*rate coding*).  
            > **Wskazówka do protokołu:** Przy wyznaczaniu progu $I_p$ (prawo Weissa) poszukujesz najmniejszego natężenia wywołującego **pierwsze pojedyncze pobudzenie**.
            """)
            
        fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
        
        # Panel 1: Napięcie błonowe
        axs[0].plot(sim["t"], sim["V"], color="#D97706", linewidth=2.2, label="Napięcie błony Vm")
        axs[0].axhline(y=-70, color="gray", linestyle=":", alpha=0.7, label="Potencjał spoczynkowy (-70 mV)")
        axs[0].axhline(y=0, color="red", linestyle="--", alpha=0.5, label="Próg odwrócenia (0 mV)")
        axs[0].set_ylabel("Napięcie [mV]", fontsize=11, fontweight="bold")
        axs[0].set_ylim(-95, 55)
        axs[0].grid(True, alpha=0.3)
        axs[0].legend(loc="upper right", fontsize=9)
        axs[0].set_title("Potencjał błonowy w czasie", fontsize=12, fontweight="bold")
        
        # Panel 2: Prąd bodźca
        axs[1].plot(sim["t"], sim["I_stim"], color="#4B5563", linewidth=2.0, label="Prąd bodźca I_stim")
        axs[1].set_ylabel("Prąd [µA/cm²]", fontsize=11, fontweight="bold")
        axs[1].grid(True, alpha=0.3)
        axs[1].legend(loc="upper right", fontsize=9)
        
        # Panel 3: Przewodności jonowe
        axs[2].plot(sim["t"], sim["g_Na"], color="#2563EB", linewidth=2.0, label="Przewodność sodowa (gNa)")
        axs[2].plot(sim["t"], sim["g_K"], color="#DC2626", linewidth=2.0, label="Przewodność potasowa (gK)")
        axs[2].set_ylabel("Przewodność [mS/cm²]", fontsize=11, fontweight="bold")
        axs[2].set_xlabel("Czas [ms]", fontsize=11, fontweight="bold")
        axs[2].grid(True, alpha=0.3)
        axs[2].legend(loc="upper right", fontsize=9)
        
        plt.tight_layout()
        st.pyplot(fig)

    # -------------------------------------------------------------------------
    # WIRTUALNY NOTATNIK POMIAROWY STUDENTA
    # -------------------------------------------------------------------------
    if "notatnik_potencjal" not in st.session_state:
        st.session_state["notatnik_potencjal"] = []
        
    st.markdown("---")
    st.subheader("📓 Wirtualny Notatnik Pomiarowy Studenta")
    st.caption("Poniższy notatnik służy jako brudnopis podczas pracy w laboratorium. Zapisuj tu odczytane wartości progowe, które przepisujesz do papierowego protokołu.")
    
    col_n1, col_n2, col_n3 = st.columns([1.2, 1, 2])
    with col_n1:
        if st.button("➕ Zapisz punkt (Δt, Ip) do Notatnika"):
            st.session_state["notatnik_potencjal"].append({
                "Czas trwania Δt [ms]": stim1_dur,
                "Odwrotność 1/Δt [1/ms]": round(1.0 / stim1_dur, 3),
                "Odczytany próg Ip [µA/cm²]": stim1_amp,
                "Czy wyzwolono AP?": "TAK" if num_peaks >= 1 else "NIE",
                "Liczba iglic": num_peaks,
                "Vmax [mV]": round(sim["max_v"], 1)
            })
    with col_n2:
        if st.button("🗑️ Wyczyść notatnik"):
            st.session_state["notatnik_potencjal"] = []
            
    if len(st.session_state["notatnik_potencjal"]) > 0:
        df_notes = pd.DataFrame(st.session_state["notatnik_potencjal"])
        st.dataframe(df_notes, use_container_width=True)
        csv_n = df_notes.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Pobierz swoje pomiary (CSV)", data=csv_n, file_name="moje_pomiary_potencjal.csv", mime="text/csv")

    # -------------------------------------------------------------------------
    # SEKCJA WERYFIKACJI I WZORCOWEJ KRZYWEJ WEISSA
    # -------------------------------------------------------------------------
    with st.expander("📐 Sprawdź swoje obliczenia i wykresy z papierowego protokołu (Klucz odpowiedzi)"):
        st.markdown(r"""
        Gdy uzupełnisz tabelę w papierowym protokole, narysujesz wykresy $I_p = f(\Delta t)$ oraz $I_p = f(1/\Delta t)$ na papierze milimetrowym i wyznaczysz reobazę ($R$) oraz chronaksję ($CH$), możesz poniżej sprawdzić wzorcowe wyniki modelu teoretycznego:
        """)
        
        ref = get_weiss_reference_data()
        durs = ref["durs"]
        ips = ref["ips"]
        inv_durs = ref["inv_durs"]
        charges = ref["charges"]
        slope = ref["slope"]
        intercept = ref["intercept"]
        r_value = ref["r_value"]
        reobaza = ref["reobaza"]
        u_coef = ref["u_coef"]
        chronaksja = ref["chronaksja"]
        
        df_weiss = pd.DataFrame({
            "Lp.": range(1, len(durs) + 1),
            "Czas trwania Δt [ms]": durs,
            "Odwrotność 1/Δt [1/ms]": np.round(inv_durs, 3),
            "Bodziec progowy Ip [µA/cm²]": ips,
            "Ładunek progowy Q = Ip*Δt [nC/cm²]": np.round(charges, 2)
        })
        
        col_tab, col_w_plot = st.columns([1, 1.2])
        
        with col_tab:
            st.dataframe(df_weiss, use_container_width=True, hide_index=True)
            
            st.markdown(f"""
            <div class="metric-card">
                <b>Wzorcowe wyniki dopasowania równania Weissa (punkty 4, 5, 6 protokołu):</b><br>
                • <b>Współczynnik kierunkowy u:</b> <code>{u_coef:.3f} µA·ms/cm²</code> (ładunek progowy)<br>
                • <b>Reobaza R (asymptota pozioma):</b> <code>{reobaza:.2f} µA/cm²</code><br>
                • <b>Chronaksja CH = u / R:</b> <code>{chronaksja:.2f} ms</code><br>
                • <b>Współczynnik korelacji R²:</b> <code>{r_value**2:.4f}</code>
            </div>
            """, unsafe_allow_html=True)
            
        with col_w_plot:
            fig_w, (ax_w1, ax_w2) = plt.subplots(1, 2, figsize=(11, 4.5))
            
            # Wykres 1: Krzywa siła-czas
            dense_t = np.linspace(0.1, 20.0, 200)
            dense_ip = reobaza + u_coef / dense_t
            
            ax_w1.scatter(durs, ips, color="darkblue", zorder=5, label="Pomiary Ip (symulacja)")
            ax_w1.plot(dense_t, dense_ip, color="crimson", linewidth=2, label="Dopasowanie Weissa")
            ax_w1.axhline(y=reobaza, color="green", linestyle="--", label=f"Reobaza R = {reobaza:.1f}")
            ax_w1.axhline(y=2*reobaza, color="orange", linestyle=":", label=f"2R = {2*reobaza:.1f}")
            ax_w1.axvline(x=chronaksja, color="purple", linestyle="--", label=f"Chronaksja = {chronaksja:.2f} ms")
            ax_w1.set_xlabel("Czas trwania bodźca Δt [ms]", fontweight="bold")
            ax_w1.set_ylabel("Bodziec progowy Ip [µA/cm²]", fontweight="bold")
            ax_w1.set_title("Wzorcowa krzywa siła-czas", fontweight="bold")
            ax_w1.grid(True, alpha=0.3)
            ax_w1.legend(fontsize=8)
            
            # Wykres 2: Linearyzacja
            dense_inv = np.linspace(0, 10.5, 200)
            ax_w2.scatter(inv_durs, ips, color="darkblue", zorder=5, label="Punkty pomiarowe")
            ax_w2.plot(dense_inv, intercept + slope * dense_inv, color="indigo", linewidth=2, label=f"y = {slope:.2f}x + {intercept:.2f}")
            ax_w2.set_xlabel("Odwrotność czasu 1/Δt [1/ms]", fontweight="bold")
            ax_w2.set_ylabel("Bodziec progowy Ip [µA/cm²]", fontweight="bold")
            ax_w2.set_title("Wzorcowa prosta Weissa", fontweight="bold")
            ax_w2.grid(True, alpha=0.3)
            ax_w2.legend(fontsize=8)
            
            plt.tight_layout()
            st.pyplot(fig_w)

    # Kontekst medyczny
    with st.expander("🩺 Zastosowania Kliniczne i Wnioski do Protokołu"):
        st.markdown("""
        1. **Elektrostymulacja serca i optymalizacja energii:**
           - Nowoczesne kardiostymulatory ustawiają czas trwania impulsu równy w przybliżeniu **chronaksji mięśnia sercowego** (ok. 0.4–1.0 ms). 
           - Skrócenie czasu impulsu poniżej chronaksji drastycznie zwiększa wymagane natężenie prądu ($I_p$), a wydłużenie ponad chronaksję marnuje energię baterii bez obniżenia progu (asymptota reobazy).
        2. **Refrakcja a zaburzenia rytmu serca:**
           - W okresie **refrakcji bezwzględnej** inaktywacja kanałów sodowych (bramki $h$) jest całkowita – komórka jest niewrażliwa na żadne bodźce. Chroni to serce przed skurczem tężcowym.
           - W okresie **refrakcji względnej** bodziec może wywołać niepełny, wolno przewodzony potencjał czynnościowy, co stanowi podłoże groźnych arytmii komorowych w mechanizmie *reentry*.
        3. **Znieczulenie miejscowe (Lignokaina, Bupiwakaina):**
           - Leki te wiążą się od wewnątrz z kanałami $Na_v$, uniemożliwiając ich otwarcie (spadek $g_{Na}$). Po przekroczeniu krytycznej blokady (ok. 60–70%), depolaryzacja nie osiąga progu generacji AP i przewodzenie bólu zostaje przerwane.
        """)


# =============================================================================
# MODUŁ 2: PRAWA PRZEPŁYWU CIECZY I HEMODYNAMIKA (POISEUILLE, BERNOULLI, REYNOLDS)
# =============================================================================

def render_tab_przeplyw():
    st.markdown('<div class="main-title">🩸 Prawa Przepływu Cieczy & Hemodynamika</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Prawo Hagena-Poiseuille\'a, Równanie Ciągłości, Równanie Bernoulliego i Liczba Reynoldsa</div>', unsafe_allow_html=True)
    
    with st.expander("📘 Informacje teoretyczne i wzory (zgodnie z protokołem 'Prawa Przepływu')"):
        st.markdown("""
        **Prawa hydrodynamiczne w układzie naczyniowym:**
        1. **Równanie ciągłości strugi:** $Q = S_1 v_1 = S_2 v_2 = \\text{const} \\implies v = \\frac{Q}{\\pi r^2}$
        2. **Prawo Hagena-Poiseuille'a (opór naczyniowy):** $R_N = \\frac{8 \\eta L}{\\pi r^4}$
        3. **Spadek ciśnienia z prawa Poiseuille'a:** $\\Delta p = R_N \\cdot Q = \\frac{8 \\eta L}{\\pi r^4} Q$
        4. **Ciśnienie dynamiczne:** $p_d = \\frac{1}{2} \\rho v^2$
        5. **Ciśnienie całkowite:** $p = p_s + p_d$
        6. **Liczba Reynoldsa:** $N_R = \\frac{\\rho v d}{\\eta} = \\frac{2 \\rho v r}{\\eta} = \\frac{2 \\rho Q}{\\pi \\eta r}$
           - $N_R < 2000$: Przepływ **laminarny** (warstwowy, cichy osłuchowo).
           - $2000 \\le N_R \\le 2300$: Strefa **przejściowa**.
           - $N_R > 2300$: Przepływ **burzliwy (turbulentny)** – powstawanie szmerów naczyniowych/sercowych!
        """)

    col_ctrl, col_view = st.columns([1, 1.8])
    
    with col_ctrl:
        st.subheader("⚙️ Panel Sterowania Parametrami")
        
        sync_radii = st.checkbox("Synchronizuj promienie (r₁ = r₂ - rura jednorodna)", value=True)
        
        r1 = st.slider("Promień sekcji 1 (r₁) [mm]:", min_value=4.0, max_value=20.0, value=10.0, step=0.5)
        
        if sync_radii:
            r2 = r1
            st.info(f"Promień sekcji 2: r₂ = {r2:.1f} mm (zsynchronizowany)")
        else:
            r2 = st.slider("Promień sekcji 2 (r₂ - np. zwężenie/stenoza) [mm]:", min_value=3.0, max_value=20.0, value=6.0, step=0.5)
            
        st.markdown("---")
        Q_lmin = st.slider("Strumień objętości Q (rzut serca) [dm³/min]:", min_value=1.0, max_value=12.0, value=5.0, step=0.5)
        
        preset_eta = st.selectbox(
            "Wybierz profil płynu / krwi (lepkość η):",
            [
                "Krew prawidłowa (η = 3.5 mPa·s)",
                "Woda / Osocze (η = 1.2 mPa·s)",
                "Niedokrwistość / Anemia (η = 2.2 mPa·s)",
                "Czerwienica / Odwodnienie (η = 6.0 mPa·s)",
                "Własna wartość lepkości"
            ]
        )
        
        if preset_eta == "Krew prawidłowa (η = 3.5 mPa·s)":
            eta_val = 3.5
        elif preset_eta == "Woda / Osocze (η = 1.2 mPa·s)":
            eta_val = 1.2
        elif preset_eta == "Niedokrwistość / Anemia (η = 2.2 mPa·s)":
            eta_val = 2.2
        elif preset_eta == "Czerwienica / Odwodnienie (η = 6.0 mPa·s)":
            eta_val = 6.0
        else:
            eta_val = st.slider("Własna lepkość [mPa·s]:", 1.0, 10.0, 3.0, 0.1)
            
        rho = st.number_input("Gęstość krwi/cieczy ρ [kg/m³]:", min_value=900.0, max_value=1200.0, value=1060.0, step=10.0)
        L = st.number_input("Długość całego naczynia L [m]:", min_value=0.1, max_value=2.0, value=0.685, step=0.05)
        P_out = 900.0 # Stałe referencyjne ciśnienie na wylocie [Pa]

    # Obliczenia fizyczne w jednostkach SI
    r1_m = r1 / 1000.0
    r2_m = r2 / 1000.0
    Q_m3s = Q_lmin / 60000.0
    eta_Pas = eta_val / 1000.0
    L_half = L / 2.0
    
    # Sekcja 1
    v1 = Q_m3s / (np.pi * (r1_m ** 2))
    pd1 = 0.5 * rho * (v1 ** 2)
    RN1 = (8.0 * eta_Pas * L_half) / (np.pi * (r1_m ** 4))
    NR1 = (2.0 * rho * v1 * r1_m) / eta_Pas
    
    # Sekcja 2
    v2 = Q_m3s / (np.pi * (r2_m ** 2))
    pd2 = 0.5 * rho * (v2 ** 2)
    RN2 = (8.0 * eta_Pas * L_half) / (np.pi * (r2_m ** 4))
    NR2 = (2.0 * rho * v2 * r2_m) / eta_Pas
    
    RN_tot = RN1 + RN2
    
    # Spadki ciśnień
    # Na wylocie sekcji 2 ciśnienie statyczne referencyjne Ps_out = 900 Pa
    Ps2 = P_out
    P_calk_2 = Ps2 + pd2
    
    # Ciśnienie całkowite na wlocie: traci energię na opór RN_tot * Q
    P_calk_1 = P_calk_2 + RN_tot * Q_m3s
    Ps1 = P_calk_1 - pd1
    delta_p = P_calk_1 - P_calk_2

    with col_view:
        st.subheader("🔬 Wizualizacja Naczynia & Sensory Laboratoryjne")
        
        # Wykres schematu naczynia
        fig_pipe, ax_pipe = plt.subplots(figsize=(10, 3.5))
        
        # Geometria naczynia
        h1 = r1 * 2.5
        h2 = r2 * 2.5
        
        # Segment 1 i Segment 2
        ax_pipe.fill_between([0, 5], [-h1, -h1], [h1, h1], color="#93C5FD", alpha=0.7, edgecolor="black", linewidth=2)
        ax_pipe.fill_between([5, 10], [-h2, -h2], [h2, h2], color="#60A5FA" if r2 < r1 else "#93C5FD", alpha=0.7, edgecolor="black", linewidth=2)
        
        # Profile prędkości (paraboliczne strzałki)
        y_pts1 = np.linspace(-h1*0.8, h1*0.8, 7)
        v_profile1 = v1 * (1.0 - (y_pts1 / h1)**2)
        for y, vp in zip(y_pts1, v_profile1):
            ax_pipe.arrow(1.5, y, vp * 3.0 / max(v1, 0.01), 0, head_width=1.5, head_length=0.2, fc="navy", ec="navy")
            
        y_pts2 = np.linspace(-h2*0.8, h2*0.8, 7)
        v_profile2 = v2 * (1.0 - (y_pts2 / h2)**2)
        for y, vp in zip(y_pts2, v_profile2):
            ax_pipe.arrow(6.5, y, vp * 3.0 / max(v2, 0.01), 0, head_width=1.5, head_length=0.2, fc="darkred" if NR2 > 2000 else "navy", ec="darkred" if NR2 > 2000 else "navy")
            
        # Manometry / Czujniki
        ax_pipe.plot([2.5, 2.5], [h1, h1+15], color="gray", linewidth=3)
        ax_pipe.plot([7.5, 7.5], [h2, h2+15], color="gray", linewidth=3)
        
        ax_pipe.text(2.5, h1+20, f"Czujnik 1 (wlot)\nPs1: {Ps1:.1f} Pa\np1: {P_calk_1:.1f} Pa\nv1: {v1:.2f} m/s", 
                     ha="center", va="bottom", bbox=dict(boxstyle="round,pad=0.4", fc="#FEF3C7", ec="goldenrod"))
        ax_pipe.text(7.5, h2+20, f"Czujnik 2 (wylot)\nPs2: {Ps2:.1f} Pa\np2: {P_calk_2:.1f} Pa\nv2: {v2:.2f} m/s", 
                     ha="center", va="bottom", bbox=dict(boxstyle="round,pad=0.4", fc="#FEF3C7", ec="goldenrod"))
        
        ax_pipe.set_xlim(-0.5, 10.5)
        ax_pipe.set_ylim(-max(h1, h2)*1.4, max(h1, h2)*1.4 + 40)
        ax_pipe.axis("off")
        ax_pipe.set_title(f"Przekrój naczynia krwionośnego (r₁={r1:.1f} mm, r₂={r2:.1f} mm)", fontweight="bold")
        st.pyplot(fig_pipe)
        
        # Karty wyników
        col_m1, col_m2, col_m3 = st.columns(3)
        col_m1.metric("Opór całkowity RN", f"{RN_tot/1e6:.3f} MPa·s/m³")
        col_m2.metric("Spadek ciśnienia Δp = p₁ - p₂", f"{delta_p:.1f} Pa", f"{delta_p/133.322:.2f} mmHg")
        col_m3.metric("Prędkość w zwężeniu v₂", f"{v2:.2f} m/s", f"{v2/v1:.2f}x wzrost" if v2 > v1 else "1.0x")
        
        # Alert liczby Reynoldsa
        if NR2 < 2000:
            st.markdown(f'<div class="success-box">🟢 <b>PRZEPŁYW LAMINARNY</b> (NR₁ = {int(NR1)}, NR₂ = {int(NR2)}). Brak szmerów, przepływ cichy osłuchowo.</div>', unsafe_allow_html=True)
        elif 2000 <= NR2 <= 2300:
            st.markdown(f'<div class="warning-box">🟡 <b>STREFA PRZEJŚCIOWA</b> (NR₂ = {int(NR2)}). Niestabilność przepływu, lokalne zawirowania przyścienne.</div>', unsafe_allow_html=True)
        else:
            st.markdown(f'<div class="clinical-box" style="border-left-color: #DC2626; background-color: #FEF2F2;">🔴 <b>PRZEPŁYW BURZLIWY / TURBULENTNY!</b> (NR₂ = <b>{int(NR2)}</b> &gt; 2300). Powstają słyszalne stetoskopem <b>szmery naczyniowe (bruit)</b>! Ryzyko uszkodzenia śródbłonka i aktywacji płytek krwi.</div>', unsafe_allow_html=True)

        # Panel odczytowy do Tabeli 1 papierowego protokołu
        st.markdown(f"""
        <div class="metric-card" style="border-left: 5px solid #10B981; background-color: #F0FDF4;">
            <b style="font-size: 1.05rem; color: #065F46;">📝 Odczyt do wpisania w Tabeli 1 papierowego protokołu (dla r = {r1:.1f} mm):</b><br>
            • <b>Ciśnienie statyczne pS1:</b> <code>{Ps1:.1f} Pa</code><br>
            • <b>Ciśnienie całkowite p1:</b> <code>{P_calk_1:.1f} Pa</code><br>
            • <b>Ciśnienie całkowite p2:</b> <code>{P_calk_2:.1f} Pa</code><br>
            • <b>Różnica ciśnień Δp = p1 - p2:</b> <code>{delta_p:.1f} Pa</code><br>
            • <b>Liczba Reynoldsa NR (odczytana):</b> <code>{int(NR1)}</code><br>
            <span style="font-size: 0.85rem; color: #374151;">👉 <b>Zadanie:</b> Przepisz powyższe 5 wartości do wiersza r = {r1:.1f} mm w Tabeli 1. Wartości w Tabeli 2 oblicz samodzielnie na kalkulatorze zgodnie ze wzorami w protokole!</span>
        </div>
        """, unsafe_allow_html=True)

    # -------------------------------------------------------------------------
    # NOTATNIK POMIAROWY STUDENTA DLA PRZEPŁYWÓW
    # -------------------------------------------------------------------------
    if "notatnik_przeplyw" not in st.session_state:
        st.session_state["notatnik_przeplyw"] = []
        
    st.markdown("---")
    st.subheader("📓 Wirtualny Notatnik Pomiarowy do Tabeli 1")
    st.caption("Możesz tutaj gromadzić odczyty dla kolejnych wartości promienia r, które przepisujesz do papierowego protokołu.")
    
    col_fn1, col_fn2, col_fn3 = st.columns([1.2, 1, 2])
    with col_fn1:
        if st.button("➕ Zapisz odczyt do Notatnika"):
            st.session_state["notatnik_przeplyw"].append({
                "Promień r [mm]": r1,
                "Ciśnienie stat. Ps1 [Pa]": round(Ps1, 1),
                "Ciśnienie całk. p1 [Pa]": round(P_calk_1, 1),
                "Ciśnienie całk. p2 [Pa]": round(P_calk_2, 1),
                "Różnica Δp [Pa]": round(delta_p, 1),
                "Liczba Reynoldsa NR (odczytana)": int(NR1)
            })
    with col_fn2:
        if st.button("🗑️ Wyczyść notatnik przepływów"):
            st.session_state["notatnik_przeplyw"] = []
            
    if len(st.session_state["notatnik_przeplyw"]) > 0:
        df_fn = pd.DataFrame(st.session_state["notatnik_przeplyw"])
        st.dataframe(df_fn, use_container_width=True)
        csv_fn = df_fn.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Pobierz swoje pomiary przepływów (CSV)", data=csv_fn, file_name="moje_pomiary_przeplyw.csv", mime="text/csv")

    # -------------------------------------------------------------------------
    # SEKCJA WERYFIKACJI I WZORCOWYCH TABEL DLA STUDENTA
    # -------------------------------------------------------------------------
    with st.expander("📐 Sprawdź swoje obliczenia i wykresy z papierowego protokołu (Klucz odpowiedzi)"):
        st.markdown(r"""
        Gdy uzupełnisz Tabelę 1 (odczyty z manometrów) oraz samodzielnie obliczysz wartości w Tabeli 2 ($R_N$, $p_d$, $v$, $N_R$) i narysujesz wykresy $R_N = f(r)$ oraz $v = f(r)$ na papierze milimetrowym, możesz poniżej sprawdzić wzorcowe wyniki modelu teoretycznego:
        """)
        
        r_series = np.array([5.0, 6.0, 7.0, 8.0, 9.0, 10.0, 11.0, 12.0, 12.6, 15.0]) # Zgodnie z protokołem
        r_series_m = r_series / 1000.0
        
        v_ser = Q_m3s / (np.pi * (r_series_m ** 2))
        pd_ser = 0.5 * rho * (v_ser ** 2)
        RN_ser = (8.0 * eta_Pas * L) / (np.pi * (r_series_m ** 4))
        dp_ser = RN_ser * Q_m3s
        p2_ser = np.full_like(r_series, P_out + pd_ser)
        p1_ser = p2_ser + dp_ser
        ps1_ser = p1_ser - pd_ser
        NR_ser = (2.0 * rho * v_ser * r_series_m) / eta_Pas
        
        df_protokol1 = pd.DataFrame({
            "Lp.": range(1, 11),
            "Promień r [mm]": r_series,
            "Ciśnienie stat. Ps1 [Pa]": np.round(ps1_ser, 1),
            "Ciśnienie całk. p1 [Pa]": np.round(p1_ser, 1),
            "Ciśnienie całk. p2 [Pa]": np.round(p2_ser, 1),
            "Różnica Δp [Pa]": np.round(dp_ser, 1),
            "Liczba Reynoldsa NR (odczytana)": np.round(NR_ser).astype(int)
        })
        
        df_protokol2 = pd.DataFrame({
            "Lp.": range(1, 11),
            "Promień r [mm]": r_series,
            "Opór RN [MPa·s/m³]": np.round(RN_ser / 1e6, 3),
            "Ciśnienie dyn. pd [Pa]": np.round(pd_ser, 1),
            "Prędkość v [m/s]": np.round(v_ser, 3),
            "Liczba Reynoldsa NR (obliczona)": np.round(NR_ser).astype(int)
        })
        
        tab_prot1, tab_prot2 = st.tabs(["Wzorcowa Tabela 1 (Pomiary Ciśnień)", "Wzorcowa Tabela 2 (Obliczenia Opory i Reynolds)"])
        with tab_prot1:
            st.dataframe(df_protokol1, use_container_width=True, hide_index=True)
        with tab_prot2:
            st.dataframe(df_protokol2, use_container_width=True, hide_index=True)

        # Wykresy zależności RN(r) oraz v(r)
        st.markdown("**Wzorcowe wykresy do porównania z Twoimi rysunkami na papierze milimetrowym:**")
        
        fig_pp, (ax_r1, ax_r2, ax_r3) = plt.subplots(1, 3, figsize=(14, 4.2))
        
        # Wykres RN(r)
        dense_r = np.linspace(4.5, 16.0, 200) / 1000.0
        dense_RN = (8.0 * eta_Pas * L) / (np.pi * (dense_r ** 4)) / 1e6
        ax_r1.plot(dense_r * 1000, dense_RN, color="crimson", linewidth=2.5, label="RN ~ 1/r⁴")
        ax_r1.scatter(r_series, RN_ser / 1e6, color="black", zorder=5)
        ax_r1.set_xlabel("Promień naczynia r [mm]", fontweight="bold")
        ax_r1.set_ylabel("Opór naczyniowy RN [MPa·s/m³]", fontweight="bold")
        ax_r1.set_title("Prawo Poiseuille'a: RN = f(r)", fontweight="bold")
        ax_r1.grid(True, alpha=0.3)
        ax_r1.legend()
        
        # Wykres v(r)
        dense_v = Q_m3s / (np.pi * (dense_r ** 2))
        ax_r2.plot(dense_r * 1000, dense_v, color="navy", linewidth=2.5, label="v ~ 1/r²")
        ax_r2.scatter(r_series, v_ser, color="black", zorder=5)
        ax_r2.set_xlabel("Promień naczynia r [mm]", fontweight="bold")
        ax_r2.set_ylabel("Prędkość przepływu v [m/s]", fontweight="bold")
        ax_r2.set_title("Równanie ciągłości: v = f(r)", fontweight="bold")
        ax_r2.grid(True, alpha=0.3)
        ax_r2.legend()
        
        # Wykres NR(r)
        dense_NR = (2.0 * rho * dense_v * dense_r) / eta_Pas
        ax_r3.plot(dense_r * 1000, dense_NR, color="darkgreen", linewidth=2.5, label="NR ~ 1/r")
        ax_r3.axhline(y=2000, color="red", linestyle="--", label="Próg turbulencji (NR=2000)")
        ax_r3.scatter(r_series, NR_ser, color="black", zorder=5)
        ax_r3.set_xlabel("Promień naczynia r [mm]", fontweight="bold")
        ax_r3.set_ylabel("Liczba Reynoldsa NR", fontweight="bold")
        ax_r3.set_title("Liczba Reynoldsa: NR = f(r)", fontweight="bold")
        ax_r3.grid(True, alpha=0.3)
        ax_r3.legend()
        
        plt.tight_layout()
        st.pyplot(fig_pp)

    # Kontekst medyczny
    with st.expander("🩺 Kliniczne Znaczenie Praw Przepływu Cieczy w Medycynie"):
        st.markdown("""
        1. **Znaczenie prawa Poiseuille'a ($R_N \\propto 1/r^4$):**
           - Naczynia oporowe (arteriole) dzięki mięśniówce gładkiej kontrolują średnicę naczynia. Zmniejszenie promienia naczynia o zaledwie **16% skutkuje podwojeniem oporu**, a skurcz o 50% zwiększa opór aż **16-krotnie**! To główny mechanizm regulacji ciśnienia tętniczego.
        2. **Stenoza aortalna i szmery sercowe:**
           - Przy zwężeniu zastawki lub naczynia prędkość krwi $v$ rośnie gwałtownie ($v \\sim 1/r^2$). Powoduje to przekroczenie krytycznej liczby Reynoldsa ($N_R > 2300$) i przejście w przepływ burzliwy. Wiry generują drgania akustyczne odbierane stetoskopem jako **szmer skurczowy**.
        3. **Paradoks Bernoulliego w tętniakach i stenozach:**
           - W miejscu tętniaka (poszerzenie $r$) prędkość maleje, a ciśnienie statyczne na ścianę naczynia rośnie ($p_s = p_{calk} - \\frac{1}{2}\\rho v^2$), co w połączeniu z prawem Laplace'a sprzyja dalszemu rozszerzaniu i pęknięciu tętniaka.
        4. **Pomiar ciśnienia metodą Korotkowa:**
           - Ucisk mankietu powyżej ciśnienia skurczowego zamyka tętnicę. Gdy mankiet opada poniżej ciśnienia skurczowego, krew przeciska się przez wąską szczelinę z ogromną prędkością ($N_R \\gg 2000$). Powstający przepływ turbulentny generuje **tony Korotkowa**.
        """)


# =============================================================================
# MODUŁ 3: OSŁABIANIE PROMIENIOWANIA JONIZUJĄCEGO W TKANKACH
# =============================================================================

# Autentyczne dane fizyczne oparte na tablicach NIST XCOM
DANE_IZOTOPOW = {
    "Cez-137 (E = 0.662 MeV)": {
        "E_opis": "0.662 MeV",
        "E_num": 0.662,
        "materialy": {
            "Ołów (Pb)": {"mi_masowe": 0.110, "gestosc": 11.34, "kolor": "navy"},
            "Miedź (Cu)": {"mi_masowe": 0.0714, "gestosc": 8.96, "kolor": "#B87333"},
            "Żelazo / Stal (Fe)": {"mi_masowe": 0.0735, "gestosc": 7.87, "kolor": "#475569"},
            "Aluminium (Al)": {"mi_masowe": 0.075, "gestosc": 2.70, "kolor": "gray"},
            "Beton zwykły": {"mi_masowe": 0.077, "gestosc": 2.35, "kolor": "darkorange"},
            "Kość ludzka (zwarta)": {"mi_masowe": 0.086, "gestosc": 1.85, "kolor": "#8B4513"},
            "Plexiglas / PMMA": {"mi_masowe": 0.0825, "gestosc": 1.19, "kolor": "#10B981"},
            "Tkanka miękka / Woda": {"mi_masowe": 0.086, "gestosc": 1.00, "kolor": "#0284C7"}
        }
    },
    "Kobalt-60 (E = 1.25 MeV)": {
        "E_opis": "1.25 MeV",
        "E_num": 1.25,
        "materialy": {
            "Ołów (Pb)": {"mi_masowe": 0.058, "gestosc": 11.34, "kolor": "navy"},
            "Miedź (Cu)": {"mi_masowe": 0.0518, "gestosc": 8.96, "kolor": "#B87333"},
            "Żelazo / Stal (Fe)": {"mi_masowe": 0.0534, "gestosc": 7.87, "kolor": "#475569"},
            "Aluminium (Al)": {"mi_masowe": 0.053, "gestosc": 2.70, "kolor": "gray"},
            "Beton zwykły": {"mi_masowe": 0.058, "gestosc": 2.35, "kolor": "darkorange"},
            "Kość ludzka (zwarta)": {"mi_masowe": 0.059, "gestosc": 1.85, "kolor": "#8B4513"},
            "Plexiglas / PMMA": {"mi_masowe": 0.0602, "gestosc": 1.19, "kolor": "#10B981"},
            "Tkanka miękka / Woda": {"mi_masowe": 0.063, "gestosc": 1.00, "kolor": "#0284C7"}
        }
    },
    "Technet-99m (E = 140 keV - Medycyna Nuklearna)": {
        "E_opis": "140 keV",
        "E_num": 0.140,
        "materialy": {
            "Ołów (Pb)": {"mi_masowe": 2.05, "gestosc": 11.34, "kolor": "navy"},
            "Miedź (Cu)": {"mi_masowe": 0.495, "gestosc": 8.96, "kolor": "#B87333"},
            "Żelazo / Stal (Fe)": {"mi_masowe": 0.368, "gestosc": 7.87, "kolor": "#475569"},
            "Aluminium (Al)": {"mi_masowe": 0.138, "gestosc": 2.70, "kolor": "gray"},
            "Beton zwykły": {"mi_masowe": 0.145, "gestosc": 2.35, "kolor": "darkorange"},
            "Kość ludzka (zwarta)": {"mi_masowe": 0.175, "gestosc": 1.85, "kolor": "#8B4513"},
            "Plexiglas / PMMA": {"mi_masowe": 0.148, "gestosc": 1.19, "kolor": "#10B981"},
            "Tkanka miękka / Woda": {"mi_masowe": 0.150, "gestosc": 1.00, "kolor": "#0284C7"}
        }
    }
}


def render_tab_promieniowanie():
    st.markdown('<div class="main-title">☢️ Osłabianie Promieniowania Jonizującego w Tkankach</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-title">Prawo Lamberta-Beera, Pomiary Tła, Statystyka Zliczeń Poissona i Warstwa Połowiąca (HVL)</div>', unsafe_allow_html=True)
    
    with st.expander("📘 Informacje teoretyczne i wzory (zgodnie z protokołem L02)"):
        st.markdown("""
        **Fizyka osłabiania promieniowania fotonowego w materii:**
        1. **Prawo osłabiania (Lamberta-Beera):** $I(x) = I_0 e^{-\\mu x}$ lub w szybkości zliczania netto: $a(x) = a_0 e^{-\\mu x}$
        2. **Szybkość zliczania brutto i tło:** $a_{brutto}(x) = a(x) + a_t$
        3. **Postać logarytmiczna (linearyzacja):** $\\ln a(x) = \\ln a_0 - \\mu x$
           - Współczynnik kierunkowy prostej wynosi $-\\mu$.
        4. **Grubość warstwy połowiącej (HVL - Half-Value Layer):**
           $$HVL = d_{1/2} = \\frac{\\ln 2}{\\mu} \\approx \\frac{0.693}{\\mu}$$
        5. **Masowy współczynnik osłabiania:** $\\mu_m = \\frac{\\mu}{\\rho} \\quad [\\text{cm}^2/\\text{g}]$
        6. **Statystyka kwantowa (Rozkład Poissona):**
           Dla $N$ zliczeń w czasie $t_{pom}$, niepewność zliczeń wynosi $\\sigma_N = \\sqrt{N}$, a niepewność szybkości zliczania $\\Delta a = \\frac{\\sqrt{N}}{t_{pom}} = \\sqrt{\\frac{a}{t_{pom}}}$.
        """)

    col_ctrl, col_sim = st.columns([1, 1.8])
    
    with col_ctrl:
        st.subheader("🔬 Stanowisko Dozymetryczne")
        
        izotop_nazwa = st.selectbox("Wybierz źródło promieniowania:", list(DANE_IZOTOPOW.keys()))
        dane_izotopu = DANE_IZOTOPOW[izotop_nazwa]
        
        material_nazwa = st.selectbox("Wybierz badany absorbent / tkankę:", list(dane_izotopu["materialy"].keys()))
        info_mat = dane_izotopu["materialy"][material_nazwa]
        
        st.markdown("---")
        st.markdown("**Parametry pomiarowe licznika:**")
        
        tryb_szumu = st.radio("Tryb pomiaru detektora:", ["Realistyczny (z szumem Poissona i niepewnościami)", "Idealny (czysto teoretyczny)"])
        
        t_pomiaru = st.slider("Czas pomiaru bramki licznika t [s]:", min_value=5, max_value=60, value=15, step=5)
        a0 = st.slider("Aktywność wiązki I₀ (szybkość początkowa) [imp/s]:", min_value=100, max_value=1000, value=500, step=50)
        at_true = st.slider("Promieniowanie tła at [imp/s]:", min_value=1, max_value=20, value=6, step=1)
        
        # Prawdziwe wielkości fizyczne
        mi_masowe_true = info_mat["mi_masowe"]
        gestosc_true = info_mat["gestosc"]
        mu_true = mi_masowe_true * gestosc_true
        hvl_true = np.log(2) / mu_true
        
        st.markdown(f"""
        <div class="metric-card">
            <b>Właściwości materiałowe (tablicowe NIST):</b><br>
            • Gęstość ρ: <code>{gestosc_true:.2f} g/cm³</code><br>
            • Wsp. masowy μ/ρ: <code>{mi_masowe_true:.3f} cm²/g</code><br>
            • Wsp. liniowy μ: <code>{mu_true:.3f} 1/cm</code><br>
            • Teoretyczne HVL: <code>{hvl_true:.2f} cm</code>
        </div>
        """, unsafe_allow_html=True)

    with col_sim:
        st.subheader("🔬 Wirtualne Stanowisko Dozymetryczne – Pomiary do Protokołu L02")
        
        # Zakres grubości dobrany do HVL materiału
        max_x = max(10.0, np.ceil(hvl_true * 4.5))
        if material_nazwa.startswith("Ołów") and "140 keV" in izotop_nazwa:
            max_x = 1.0 # Dla ołowiu przy niskich energiach osłabianie jest ogromne
            
        x_steps = np.linspace(0.0, max_x, 10)
        
        # Krok 1: Pomiar tła
        st.markdown("#### Krok 1: Pomiar promieniowania tła naturalnego ($a_t$)")
        st.caption("Przed włożeniem absorbentu zmierz częstość zliczeń tła naturalnego detektora.")
        
        col_t1, col_t2 = st.columns([1, 1.4])
        with col_t1:
            if st.button("▶️ Zmierz tło licznikiem (czas 15s)"):
                if tryb_szumu.startswith("Realistyczny"):
                    n_t = np.random.poisson(at_true * t_pomiaru)
                    st.session_state['at_meas'] = n_t / t_pomiaru
                    st.session_state['delta_at'] = np.sqrt(n_t) / t_pomiaru
                    st.session_state['nt_raw'] = n_t
                else:
                    st.session_state['at_meas'] = float(at_true)
                    st.session_state['delta_at'] = 0.0
                    st.session_state['nt_raw'] = int(at_true * t_pomiaru)
                    
        at_meas = st.session_state.get('at_meas', float(at_true))
        delta_at = st.session_state.get('delta_at', 0.5)
        nt_raw = st.session_state.get('nt_raw', int(at_true * t_pomiaru))
        
        with col_t2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #F59E0B; background-color: #FFFBEB;">
                <b>Odczyt licznika dla tła (punkt 2 i 7 protokołu):</b><br>
                • Zliczenia Nt w czasie t={t_pomiaru}s: <code>{nt_raw} imp</code><br>
                • <b>Szybkość zliczania tła at:</b> <code>{at_meas:.2f} ± {delta_at:.2f} imp/s</code><br>
                <span style="font-size: 0.85rem; color: #92400E;">👉 <b>Zadanie:</b> Wpisz wartość at w punkcie 2 swojego papierowego protokołu!</span>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("---")
        # Krok 2: Pomiar dla wybranej grubości x
        st.markdown("#### Krok 2: Pomiar dla warstwy absorbentu o grubości $x$")
        st.caption("Wybierz grubość płytki absorbentu i wykonaj zliczenie, aby uzyskać szybkość zliczania brutto.")
        
        col_x1, col_x2 = st.columns([1, 1.4])
        with col_x1:
            x_wybrane = st.selectbox(
                "Wybierz grubość absorbentu x [cm]:",
                [round(val, 2) for val in x_steps],
                index=0
            )
            
            # Przycisk pomiaru
            if st.button(f"▶️ Wykonaj pomiar dla x = {x_wybrane} cm"):
                st.session_state['last_x'] = x_wybrane
                
        last_x = st.session_state.get('last_x', x_wybrane)
        a_net_ideal = a0 * np.exp(-mu_true * last_x)
        lambda_gross = (a_net_ideal + at_true) * t_pomiaru
        if tryb_szumu.startswith("Realistyczny"):
            n_single = np.random.poisson(lambda_gross)
            a_single_brutto = n_single / t_pomiaru
            delta_single = np.sqrt(n_single) / t_pomiaru
        else:
            n_single = int(lambda_gross)
            a_single_brutto = a_net_ideal + at_meas
            delta_single = 0.0
            
        with col_x2:
            st.markdown(f"""
            <div class="metric-card" style="border-left: 4px solid #2563EB; background-color: #EFF6FF;">
                <b>Odczyt licznika dla grubości x = {last_x:.2f} cm:</b><br>
                • Zliczenia N w czasie t={t_pomiaru}s: <code>{n_single} imp</code><br>
                • <b>Szybkość zliczania brutto:</b> <code>{a_single_brutto:.1f} ± {delta_single:.1f} imp/s</code><br>
                <span style="font-size: 0.85rem; color: #1E40AF;">👉 <b>Zadanie:</b> Wpisz wartość <b>{a_single_brutto:.1f}</b> w kolumnie 'Szybkość zliczania a ± Δa' w punkcie 3 protokołu.<br>Następnie na kalkulatorze oblicz szybkość netto: a = a_brutto - at oraz ln(a).</span>
            </div>
            """, unsafe_allow_html=True)

    # Notatnik laboratoryjny do promieniowania
    if "notatnik_prom" not in st.session_state:
        st.session_state["notatnik_prom"] = []
        
    st.markdown("---")
    st.subheader("📓 Wirtualny Notatnik Pomiarowy do Tabeli w Punkcie 3")
    st.caption("Możesz tutaj gromadzić odczyty dla kolejnych grubości x, które przepisujesz do papierowego protokołu.")
    
    col_pn1, col_pn2, col_pn3 = st.columns([1.2, 1, 2])
    with col_pn1:
        if st.button("➕ Zapisz punkt pomiarowy do Notatnika"):
            st.session_state["notatnik_prom"].append({
                "Grubość x [cm]": last_x,
                "Zliczenia N [imp]": n_single,
                "a_brutto [imp/s]": round(a_single_brutto, 1),
                "Niepewność Δa [imp/s]": round(delta_single, 1)
            })
    with col_pn2:
        if st.button("🗑️ Wyczyść notatnik promieniowania"):
            st.session_state["notatnik_prom"] = []
            
    if len(st.session_state["notatnik_prom"]) > 0:
        df_pn = pd.DataFrame(st.session_state["notatnik_prom"])
        st.dataframe(df_pn, use_container_width=True)
        csv_pn = df_pn.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Pobierz swoje pomiary (CSV)", data=csv_pn, file_name="moje_pomiary_promieniowanie.csv", mime="text/csv")

    # -------------------------------------------------------------------------
    # SEKCJA WERYFIKACJI I WZORCOWYCH WYNIKÓW DLA STUDENTA
    # -------------------------------------------------------------------------
    with st.expander("📐 Sprawdź swoje obliczenia i wykresy z papierowego protokołu (Weryfikator)"):
        st.markdown(r"""
        Gdy uzupełnisz tabelę w punkcie 3 protokołu (obliczysz na kalkulatorze $a_{netto} = a_{brutto} - a_t$, $\Delta a$, $\ln a$ oraz $\Delta \ln a$) i narysujesz wykresy $a = f(x)$ oraz $\ln a = f(x)$ na papierze milimetrowym, możesz poniżej sprawdzić wzorcowe wyniki modelu teoretycznego:
        """)
        
        # Symulacja 10 punktów referencyjnych
        pomiary_list = []
        for i, x in enumerate(x_steps):
            a_net_ideal = a0 * np.exp(-mu_true * x)
            lambda_gross = (a_net_ideal + at_true) * t_pomiaru
            if tryb_szumu.startswith("Realistyczny"):
                n_gross = np.random.poisson(lambda_gross)
                a_gross = n_gross / t_pomiaru
                delta_a_gross = np.sqrt(n_gross) / t_pomiaru
                a_net = max(a_gross - at_meas, 0.1)
                delta_a_net = np.sqrt(delta_a_gross**2 + delta_at**2)
            else:
                a_gross = a_net_ideal + at_meas
                delta_a_gross = 0.0
                a_net = a_net_ideal
                delta_a_net = 0.0
                
            ln_a = np.log(a_net)
            delta_ln_a = delta_a_net / a_net if delta_a_net > 0 else 0.0
            
            pomiary_list.append({
                "Lp.": i + 1,
                "Grubość x [cm]": round(x, 2),
                "a_brutto [imp/s]": round(a_gross, 1),
                "Szybkość netto a [imp/s]": round(a_net, 1),
                "Δa [imp/s]": round(delta_a_net, 1),
                "ln(a)": round(ln_a, 3),
                "Δln(a)": round(delta_ln_a, 3)
            })
            
        df_prom = pd.DataFrame(pomiary_list)
        st.dataframe(df_prom, use_container_width=True, hide_index=True)
        
        xs = df_prom["Grubość x [cm]"].values
        ys_a = df_prom["Szybkość netto a [imp/s]"].values
        ys_lna = df_prom["ln(a)"].values
        
        slope_prom, intercept_prom, r_prom, p_prom, se_prom = stats.linregress(xs, ys_lna)
        mu_exp = -slope_prom
        mi_exp = mu_exp / gestosc_true
        hvl_exp = np.log(2) / mu_exp if mu_exp > 0 else 0.0
        
        col_plot1, col_plot2 = st.columns(2)
        
        with col_plot1:
            fig_a, ax_a = plt.subplots(figsize=(6.5, 4.8))
            dense_x = np.linspace(0, max_x, 200)
            dense_a = np.exp(intercept_prom) * np.exp(-mu_exp * dense_x)
            
            ax_a.errorbar(xs, ys_a, yerr=df_prom["Δa [imp/s]"].values, fmt='o', color=info_mat["kolor"], ecolor='black', capsize=4, label="Punkty pomiarowe netto")
            ax_a.plot(dense_x, dense_a, color=info_mat["kolor"], linewidth=2.5, label="Dopasowanie wykładnicze")
            
            if hvl_exp <= max_x and hvl_exp > 0:
                ax_a.axvline(x=hvl_exp, color="red", linestyle="--", label=f"HVL doświadczalne = {hvl_exp:.2f} cm")
                ax_a.axhline(y=np.exp(intercept_prom)/2.0, color="gray", linestyle=":", label="I₀ / 2 (połowa natężenia)")
                
            ax_a.set_xlabel("Grubość warstwy absorbentu x [cm]", fontweight="bold")
            ax_a.set_ylabel("Szybkość zliczania netto a [imp/s]", fontweight="bold")
            ax_a.set_title(f"Zależność a = f(x) dla {material_nazwa}", fontweight="bold")
            ax_a.grid(True, alpha=0.3)
            ax_a.legend(fontsize=9)
            st.pyplot(fig_a)

        with col_plot2:
            fig_ln, ax_ln = plt.subplots(figsize=(6.5, 4.8))
            ax_ln.errorbar(xs, ys_lna, yerr=df_prom["Δln(a)"].values, fmt='s', color="indigo", ecolor='gray', capsize=4, label="Punkty pomiarowe ln(a)")
            ax_ln.plot(dense_x, intercept_prom + slope_prom * dense_x, color="red", linewidth=2.5, label=f"Regresja: y = {slope_prom:.3f}x + {intercept_prom:.2f}")
            ax_ln.set_xlabel("Grubość warstwy absorbentu x [cm]", fontweight="bold")
            ax_ln.set_ylabel("Logarytm naturalny ln(a)", fontweight="bold")
            ax_ln.set_title(f"Linearyzacja ln(a) = f(x) [Nachylenie = -μ]", fontweight="bold")
            ax_ln.grid(True, alpha=0.3)
            ax_ln.legend(fontsize=9)
            st.pyplot(fig_ln)

        # Zestawienie tabelaryczne wyników doświadczalnych vs tablicowych
        st.markdown("**Wzorcowe parametry do Punktu 5 i 10 protokołu:**")
        col_res1, col_res2, col_res3 = st.columns(3)
        col_res1.markdown(f"""
        <div class="metric-card">
            <b>Warstwa Połowiąca (HVL):</b><br>
            • Z wykresu / wzoru: <code>{hvl_exp:.2f} cm</code><br>
            • Wartość teoretyczna: <code>{hvl_true:.2f} cm</code><br>
            • Błąd względny: <code>{abs(hvl_exp - hvl_true)/hvl_true * 100:.1f}%</code>
        </div>
        """, unsafe_allow_html=True)
        
        col_res2.markdown(f"""
        <div class="metric-card">
            <b>Liniowy Współczynnik Osłabiania (μ):</b><br>
            • Z nachylenia regresji: <code>{mu_exp:.3f} cm⁻¹</code><br>
            • Wartość teoretyczna: <code>{mu_true:.3f} cm⁻¹</code><br>
            • Niepewność fitu: <code>±{se_prom:.3f} cm⁻¹</code>
        </div>
        """, unsafe_allow_html=True)
        
        col_res3.markdown(f"""
        <div class="metric-card">
            <b>Masowy Współczynnik Osłabiania (μ_m):</b><br>
            • Wyznaczony μ / ρ: <code>{mi_exp:.3f} cm²/g</code><br>
            • Wartość tablicowa NIST: <code>{mi_masowe_true:.3f} cm²/g</code><br>
            • Współczynnik R² dopasowania: <code>{r_prom**2:.4f}</code>
        </div>
        """, unsafe_allow_html=True)

    # Wykres zbiorczy porównujący wszystkie materiały
    st.markdown("---")
    st.subheader("🌐 Zbiorcze Porównanie Materiałów dla Wybranego Źródła")
    
    fig_all, ax_all = plt.subplots(figsize=(10, 4.5))
    x_common = np.linspace(0, 15.0, 300)
    
    for mat_n, mat_inf in dane_izotopu["materialy"].items():
        mu_m = mat_inf["mi_masowe"] * mat_inf["gestosc"]
        trans = 100.0 * np.exp(-mu_m * x_common)
        ax_all.plot(x_common, trans, label=f"{mat_n} (HVL={np.log(2)/mu_m:.2f} cm)", color=mat_inf["kolor"], linewidth=2.2)
        
    ax_all.set_xlabel("Grubość osłony [cm]", fontweight="bold")
    ax_all.set_ylabel("Transmisja promieniowania [%]", fontweight="bold")
    ax_all.set_title(f"Porównanie skuteczności osłon dla źródła {izotop_nazwa}", fontweight="bold")
    ax_all.set_ylim(0, 105)
    ax_all.grid(True, alpha=0.3)
    ax_all.legend()
    st.pyplot(fig_all)

    # Kontekst medyczny
    with st.expander("🩺 Zastosowania Kliniczne w Radiologii i Ochronie Radiologicznej"):
        st.markdown(r"""
        1. **Zasada ALARA w Ochronie Radiologicznej (As Low As Reasonably Achievable):**
           - **Czas:** minimalizacja czasu ekspozycji personelu i pacjenta.
           - **Odległość:** prawo odwrotnych kwadratów ($I \propto 1/r^2$).
           - **Osłony:** dobór odpowiedniej grubości materiału o wysokim $Z$ i dużej gęstości (np. fartuchy ołowiane o równoważniku ołowiu 0.25–0.5 mm Pb, ściany pracowni z barytobetonu).
        2. **Fizyczne Podstawy Tomografii Komputerowej (Skala Hounsfielda):**
           - Obraz w TK powstaje z rekonstrukcji lokalnych liniowych współczynników osłabiania $\mu$:
             $$HU = 1000 \times \frac{\mu_{tkanki} - \mu_{wody}}{\mu_{wody}}$$
           - Powietrze: $-1000\text{ HU}$ (brak osłabiania), Woda: $0\text{ HU}$, Tkanka tłuszczowa: ok. $-100\text{ HU}$, Tkanka miękka: $+20$ do $+50\text{ HU}$, Kość zbita: $+1000$ do $+2000\text{ HU}$ (bardzo wysokie $\mu$ ze względu na wapń $Z=20$).
        3. **Rola energii fotonów w diagnostyce vs terapii:**
           - Przy niskich energiach ($E < 100\text{ keV}$ – diagnostyka RTG/TK) dominujący jest **efekt fotoelektryczny** ($\sigma_{ph} \propto \frac{Z^3}{E^3}$). Zależność od $Z^3$ daje doskonały kontrast między kością a tkankami miękkimi!
           - Przy energiach megawoltowych ($E > 1\text{ MeV}$ – Kobalt-60, akceleratory liniowe w radioterapii) dominuje **rozpraszanie komptonowskie**, zależne jedynie od gęstości elektronowej $\rho_e$, co pozwala równomiernie deponować dawkę niszczącą w głębi guza nowotworowego.
        """)


# =============================================================================
# GŁÓWNA APLIKACJA I PASEK BOCZNY
# =============================================================================

def main():
    with st.sidebar:
        st.image("https://img.icons8.com/fluency/96/caduceus.png", width=70)
        st.title("Pracownia Biofizyki")
        st.caption("Uniwersytet Medyczny • Laboratorium Komputerowe")
        st.markdown("---")
        
        st.subheader("👤 Dane Studenta")
        st_imie = st.text_input("Imię i Nazwisko:", placeholder="np. Jan Kowalski")
        st_grupa = st.text_input("Grupa dziekańska:", placeholder="np. Lekarski Gr. 3")
        st_data = st.date_input("Data ćwiczenia:")
        
        st.markdown("---")
        st.markdown("""
        **Wybierz ćwiczenie z zakładek u góry:**
        1. ⚡ **Potencjał Czynnościowy** (L09b)
        2. 🩸 **Prawa Przepływu** (Hemodynamika)
        3. ☢️ **Osłabianie Promieniowania** (L02)
        """)
        
        st.markdown("---")
        st.caption("Wersja 2.0 • Zgodna z protokołami sprawozdawczymi")

    tab1, tab2, tab3 = st.tabs([
        "⚡ 1. Potencjał Czynnościowy (Hodgkin-Huxley & Weiss)",
        "🩸 2. Prawa Przepływu Cieczy (Hemodynamika)",
        "☢️ 3. Osłabianie Promieniowania Jonizującego w Tkankach"
    ])

    with tab1:
        render_tab_potencjal()

    with tab2:
        render_tab_przeplyw()

    with tab3:
        render_tab_promieniowanie()


if __name__ == "__main__":
    main()
