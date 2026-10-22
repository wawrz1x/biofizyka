"""
hh_model.py
===========
Silnik numeryczny modelu biofizycznego komórki nerwowej dla Wersji 2.1
Wirtualnej Pracowni Biofizyki Medycznej.

Model bazuje na klasycznych równaniach Hodgkina-Huxleya (1952) skalibrowanych
do parametrów elektrycznego obwodu zastępczego z Ryciny 7 oraz danych
z Rozdziału 21 podręcznika:
- Potencjał spoczynkowy: U_spocz = -90.0 mV
- Potencjały równowagowe Nernsta: E_Na = +66.0 mV, E_K = -97.0 mV, E_Cl = -90.0 mV
- Pojemność błony komórkowej: C_m = 1.0 µF/cm²
- Przewodności maksymalne: g_Na_max = 120.0 mS/cm², g_Cl = 0.3 mS/cm²
- Przewodność potasowa g_K_max wyliczana analitycznie dla zerowego prądu spoczynkowego.

Silnik jest całkowicie odseparowany od interfejsu (brak importów Streamlit).
"""

from dataclasses import dataclass
from typing import Optional, Tuple, Union
import numpy as np


# -----------------------------------------------------------------------------
# STAŁE FIZYCZNE I BIOFIZYCZNE MODELU (ZGODNE Z RYC. 7 I ROZDZ. 21 PODRĘCZNIKA)
# -----------------------------------------------------------------------------
V_REST: float = -90.0     # Potencjał spoczynkowy [mV] (Ryc. 1 i Ryc. 7)
ENA: float = 66.0         # Potencjał równowagowy sodu [mV] (Ryc. 7)
EK: float = -97.0         # Potencjał równowagowy potasu [mV] (Ryc. 7)
ECL: float = -90.0        # Potencjał równowagowy chloru [mV] (Ryc. 7)
CM: float = 1.0           # Pojemność elektryczna błony [µF/cm²] (Ryc. 7)

GNA_BAR: float = 120.0    # Maksymalna przewodność sodowa [mS/cm²]
GCL_BAR: float = 0.3      # Przewodność przecieku / chlorkowa [mS/cm²] (Ryc. 7)

# Parametry napięciowe kinetyki bramek (kalibracja dla U_rest = -90 mV i progu ~ -60 mV)
V_M0: float = -55.0       # Punkt środkowy aktywacji sodu [mV]
V_H0: float = -70.0       # Punkt inaktywacji sodu [mV]
V_N0: float = -65.0       # Punkt środkowy aktywacji potasu [mV]


@dataclass
class SimulationResult:
    """Kontener na wyniki symulacji numerycznej modelu Hodgkina-Huxleya."""
    t: np.ndarray             # Czas [ms]
    V: np.ndarray             # Potencjał błonowy U [mV]
    I_stim: np.ndarray        # Gęstość prądu stymulującego J [µA/cm²]
    g_Na: np.ndarray          # Przewodność sodowa g_Na = 1/R_Na [mS/cm²]
    g_K: np.ndarray           # Przewodność potasowa g_K = 1/R_K [mS/cm²]
    g_Cl: float               # Przewodność stała chlorkowa g_Cl = 1/R_Cl [mS/cm²]
    m: np.ndarray             # Zmienna bramkowania m (wewnętrzna)
    h: np.ndarray             # Zmienna bramkowania h (wewnętrzna)
    n: np.ndarray             # Zmienna bramkowania n (wewnętrzna)
    v_max: float              # Maksymalne osiągnięte napięcie U_max [mV]
    v_min: float              # Minimalne osiągnięte napięcie U_min [mV]
    v_rest: float             # Napięcie początkowe / spoczynkowe [mV]
    has_spike: bool           # Flaga wyzwolenia pełnego potencjału czynnościowego
    spike_peak_time: Optional[float]  # Czas wystąpienia szczytu potencjału czynnościowego [ms]


# -----------------------------------------------------------------------------
# WSPÓŁCZYNNIKI SZYBKOŚCI BRAMEK (RÓWNANIA KINETYCZNE)
# Zabezpieczone analitycznie przed dzieleniem przez zero w punktach osobliwych
# -----------------------------------------------------------------------------

def alpha_m(v: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Współczynnik aktywacji bramki m (otwieranie poru sodowego)."""
    x = v - V_M0
    # Osobliwość w x = 0 (v = V_M0): lim_{x->0} 0.1*x / (1 - exp(-x/10)) = 1.0
    if isinstance(v, np.ndarray):
        with np.errstate(divide='ignore', invalid='ignore'):
            res = 0.1 * x / (1.0 - np.exp(-x / 10.0))
            res[np.abs(x) < 1e-6] = 1.0
        return res
    return 1.0 if abs(x) < 1e-6 else 0.1 * x / (1.0 - np.exp(-x / 10.0))


def beta_m(v: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Współczynnik deaktywacji bramki m."""
    return 4.0 * np.exp(-(v - V_REST) / 18.0)


def alpha_h(v: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Współczynnik usuwania inaktywacji bramki h (wzrost gotowości sodu)."""
    return 0.07 * np.exp(-(v - V_REST) / 20.0)


def beta_h(v: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Współczynnik inaktywacji bramki h (zamykanie układu sodowego)."""
    x = v - V_H0
    return 1.0 / (np.exp(-x / 10.0) + 1.0)


def alpha_n(v: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Współczynnik aktywacji bramki n (otwieranie kanałów potasowych)."""
    x = v - V_N0
    # Osobliwość w x = 0 (v = V_N0): lim_{x->0} 0.01*x / (1 - exp(-x/10)) = 0.1
    if isinstance(v, np.ndarray):
        with np.errstate(divide='ignore', invalid='ignore'):
            res = 0.01 * x / (1.0 - np.exp(-x / 10.0))
            res[np.abs(x) < 1e-6] = 0.1
        return res
    return 0.1 if abs(x) < 1e-6 else 0.01 * x / (1.0 - np.exp(-x / 10.0))


def beta_n(v: Union[float, np.ndarray]) -> Union[float, np.ndarray]:
    """Współczynnik deaktywacji bramki n."""
    return 0.125 * np.exp(-(v - V_REST) / 80.0)


# -----------------------------------------------------------------------------
# ANILITYCZNE WYZNACZENIE GK_BAR DLA IDEALNEJ RÓWNOWAGI SPOCZYNKOWEJ
# -----------------------------------------------------------------------------
def get_calibrated_conductances() -> Tuple[float, float, float, float, float, float]:
    """
    Oblicza wartości początkowe bramek m0, h0, n0 oraz kalibruje GK_BAR,
    aby w punkcie V = V_REST = -90.0 mV pochodna dV/dt wynosiła dokładnie 0.0.
    
    Z bilansu Kirchhoffa w spoczynku:
    - I_Cl = g_Cl * (V_REST - ECL) = g_Cl * (-90 - (-90)) = 0
    - I_Na = g_Na0 * (V_REST - ENA) = g_Na0 * (-90 - 66) = -156 * g_Na0
    - I_K = g_K0 * (V_REST - EK) = g_K0 * (-90 - (-97)) = +7 * g_K0
    - 0 = I_Na + I_K => 7 * g_K0 = 156 * g_Na0 => g_K0 = (156 / 7) * g_Na0.
    Stosunek R_Na / R_K = 156 / 7 ≈ 22.29, co znakomicie odpowiada
    podręcznikowej proporcji 25 z Ryciny 7.
    """
    am0, bm0 = float(alpha_m(V_REST)), float(beta_m(V_REST))
    ah0, bh0 = float(alpha_h(V_REST)), float(beta_h(V_REST))
    an0, bn0 = float(alpha_n(V_REST)), float(beta_n(V_REST))
    
    m0 = am0 / (am0 + bm0)
    h0 = ah0 / (ah0 + bh0)
    n0 = an0 / (an0 + bn0)
    
    gna0 = GNA_BAR * (m0 ** 3) * h0
    gk0_req = gna0 * 156.0 / 7.0
    gk_bar_calibrated = gk0_req / (n0 ** 4)
    
    return m0, h0, n0, gna0, gk0_req, gk_bar_calibrated


# Wylicz stałe przy imporcie
M0, H0, N0, GNA0, GK0, GK_BAR = get_calibrated_conductances()


# -----------------------------------------------------------------------------
# GENERATORY PRZEBIEGÓW BODŹCÓW PROSTOKĄTNYCH (WYŁĄCZNIE 3 TRYBY)
# -----------------------------------------------------------------------------

def generate_single_pulse(
    t: np.ndarray,
    amp: float,
    dur: float,
    start: float = 2.0
) -> np.ndarray:
    """
    Generuje pojedynczy prostokątny impuls gęstości prądu.
    amp: gęstość prądu J [µA/cm²] (wartość dodatnia, zero lub ujemna).
    dur: czas trwania Δt [ms].
    start: czas rozpoczęcia stymulacji [ms].
    """
    stim = np.zeros_like(t, dtype=np.float64)
    if dur > 0.0:
        mask = (t >= start) & (t < start + dur)
        stim[mask] = amp
    return stim


def generate_dual_pulses(
    t: np.ndarray,
    amp1: float,
    dur1: float,
    amp2: float,
    dur2: float,
    interval: float,
    start1: float = 2.0
) -> np.ndarray:
    """
    Generuje układ dwóch impulsów prostokątnych.
    interval: odstęp czasowy Δτ [ms] zdefiniowany jako czas od KOŃCA
              pierwszego impulsu do POCZĄTKU drugiego impulsu.
              start2 = start1 + dur1 + interval.
              Gdy interval < 0, impulsy nakładają się, a prądy sumują się liniowo.
    """
    stim = np.zeros_like(t, dtype=np.float64)
    if dur1 > 0.0:
        mask1 = (t >= start1) & (t < start1 + dur1)
        stim[mask1] += amp1
        
    start2 = start1 + dur1 + interval
    if dur2 > 0.0:
        mask2 = (t >= start2) & (t < start2 + dur2)
        stim[mask2] += amp2
        
    return stim


def generate_pulse_train(
    t: np.ndarray,
    amp: float,
    dur: float,
    interval: float,
    n_pulses: int = 3,
    start: float = 2.0
) -> np.ndarray:
    """
    Generuje serię 3 impulsów prostokątnych do badania sumowania w czasie (Ryc. 6).
    interval: odstęp czasowy Δτ [ms] między końcem jednego impulsu a początkiem następnego.
    n_pulses: dokładnie 3 impulsy (domyślnie i zgodnie z metodyką).
    """
    stim = np.zeros_like(t, dtype=np.float64)
    count = max(1, int(n_pulses))
    for i in range(count):
        p_start = start + i * (dur + interval)
        p_end = p_start + dur
        if dur > 0.0:
            mask = (t >= p_start) & (t < p_end)
            stim[mask] += amp
    return stim


# -----------------------------------------------------------------------------
# NUMERYCZNE ROZWIĄZYWANIE RÓWNAŃ MODELU HODGKINA-HUXLEYA
# -----------------------------------------------------------------------------

def simulate_hh(
    stimulus: np.ndarray,
    times: np.ndarray,
    v_init: float = V_REST
) -> SimulationResult:
    """
    Całkowanie numeryczne nieliniowego układu równań różniczkowych zwyczajnych.
    Metoda różnicowa pierwszego rzędu (Forward Euler o stałym kroku dt <= 0.01 ms).
    
    Równanie bilansu potencjału błonowego:
    C_m * dU/dt = - [ g_Na*(U - E_Na) + g_K*(U - E_K) + g_Cl*(U - E_Cl) ] + J_stim(t)
    """
    n_steps = len(times)
    if n_steps < 2:
        raise ValueError("Tablica czasów musi zawierać co najmniej 2 punkty.")
    dt = float(times[1] - times[0])
    
    voltages = np.zeros(n_steps, dtype=np.float64)
    g_na_arr = np.zeros(n_steps, dtype=np.float64)
    g_k_arr = np.zeros(n_steps, dtype=np.float64)
    m_arr = np.zeros(n_steps, dtype=np.float64)
    h_arr = np.zeros(n_steps, dtype=np.float64)
    n_arr = np.zeros(n_steps, dtype=np.float64)
    dv_arr = np.zeros(n_steps, dtype=np.float64)
    
    # Warunki początkowe
    mv = float(v_init)
    curr_m = float(M0)
    curr_h = float(H0)
    curr_n = float(N0)
    
    v_max = mv
    v_min = mv
    
    for i in range(n_steps):
        t = times[i]
        ia = float(stimulus[i])
        
        # Wartości kinetyczne w bieżącym napięciu
        am, bm = float(alpha_m(mv)), float(beta_m(mv))
        ah, bh = float(alpha_h(mv)), float(beta_h(mv))
        an, bn = float(alpha_n(mv)), float(beta_n(mv))
        
        # Przewodności jonowe zgodne z Ryc. 7
        gna = GNA_BAR * (curr_m ** 3) * curr_h
        gk = GK_BAR * (curr_n ** 4)
        
        # Prądy jonowe (I = g * (V - E))
        ina = gna * (mv - ENA)
        ik = gk * (mv - EK)
        icl = GCL_BAR * (mv - ECL)
        
        # Pochodna dU/dt [mV/ms]
        dv_dt = (-ina - ik - icl + ia) / CM
        
        # Zapis do tablic
        voltages[i] = mv
        g_na_arr[i] = gna
        g_k_arr[i] = gk
        m_arr[i] = curr_m
        h_arr[i] = curr_h
        n_arr[i] = curr_n
        dv_arr[i] = dv_dt
        
        if mv > v_max:
            v_max = mv
        if mv < v_min:
            v_min = mv
            
        # Aktualizacja zmiennych metodą Eulera
        curr_m += (am * (1.0 - curr_m) - bm * curr_m) * dt
        curr_h += (ah * (1.0 - curr_h) - bh * curr_h) * dt
        curr_n += (an * (1.0 - curr_n) - bn * curr_n) * dt
        mv += dv_dt * dt

    # -------------------------------------------------------------------------
    # KRYTERIUM DETEKCJI POTENCJAŁU CZYNNOŚCIOWEGO
    # -------------------------------------------------------------------------
    # Potencjał czynnościowy to nie samo przekroczenie arbitralnej linii -60 mV.
    # Wymagamy:
    # 1. Regeneracyjnej fazy wznoszącej: dU/dt > 10.0 mV/ms (prawo "wszystko albo nic")
    # 2. Osiągnięcia przepolaryzowania (U_max > 0.0 mV, typowo +30 do +38 mV).
    has_spike = bool((v_max > 0.0) and (np.max(dv_arr) > 10.0))
    spike_peak_time = float(times[int(np.argmax(voltages))]) if has_spike else None
    
    return SimulationResult(
        t=times,
        V=voltages,
        I_stim=stimulus,
        g_Na=g_na_arr,
        g_K=g_k_arr,
        g_Cl=GCL_BAR,
        m=m_arr,
        h=h_arr,
        n=n_arr,
        v_max=float(v_max),
        v_min=float(v_min),
        v_rest=float(v_init),
        has_spike=has_spike,
        spike_peak_time=spike_peak_time
    )


# -----------------------------------------------------------------------------
# AUTOMATYCZNA BISEKCJA (WYŁĄCZNIE DO TESTÓW TECHNICZNYCH / WEWNĘTRZNYCH)
# -----------------------------------------------------------------------------

def find_threshold_bisection(
    dur: float,
    start: float = 2.0,
    t_max: float = 30.0,
    dt: float = 0.01,
    tolerance: float = 0.02,
    max_iter: int = 25
) -> float:
    """
    Wewnętrzna funkcja do technicznych testów modelu.
    NIE jest eksponowana w interfejsie studenckim jako automatyczny gotowiec.
    """
    times = np.linspace(0, t_max, int(t_max / dt))
    
    def test_amp(amp: float) -> bool:
        stim = generate_single_pulse(times, amp, dur, start=start)
        res = simulate_hh(stim, times)
        return res.has_spike
        
    low = 0.0
    high = 80.0
    if not test_amp(high):
        high = 150.0
        
    for _ in range(max_iter):
        mid = (low + high) / 2.0
        if test_amp(mid):
            high = mid
        else:
            low = mid
        if (high - low) < tolerance:
            break
            
    return float((low + high) / 2.0)
