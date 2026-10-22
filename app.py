"""
app.py
======
Wirtualna Pracownia Biofizyki Medycznej — Wersja 2.1
Ćwiczenie: Potencjał Czynnościowy Neuronu i Pobudliwość Błony Komórkowej
Zgodne z Rozdziałem 21 podręcznika biofizyki i elektrycznym modelem zastępczym (Ryc. 7).
"""

import streamlit as st
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

import hh_model

# -----------------------------------------------------------------------------
# KONFIGURACJA STRONY STREAMLIT
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="Potencjał Czynnościowy — Biofizyka 2.1",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estetyczne style CSS dla laboratoryjnego stanowiska pomiarowego
st.markdown("""
<style>
    .app-header {
        background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%);
        border: 1px solid #334155;
        border-radius: 8px;
        padding: 14px 22px;
        margin-bottom: 14px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.3);
    }
    .app-header h1 {
        color: #F8FAFC;
        font-size: 1.75rem;
        font-weight: 700;
        margin: 0;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .app-header p {
        color: #94A3B8;
        font-size: 0.92rem;
        margin: 4px 0 0 0;
    }
    .status-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 9999px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .badge-spike {
        background-color: rgba(16, 185, 129, 0.2);
        color: #34D399;
        border: 1px solid #059669;
    }
    .badge-sub {
        background-color: rgba(239, 68, 68, 0.2);
        color: #F87171;
        border: 1px solid #DC2626;
    }
    .badge-ghost {
        background-color: rgba(148, 163, 184, 0.2);
        color: #CBD5E1;
        border: 1px solid #64748B;
        padding: 4px 10px;
        border-radius: 6px;
        font-size: 0.82rem;
        margin: 6px 0;
    }
    .kpi-card {
        background-color: #0F172A;
        border: 1px solid #334155;
        border-radius: 6px;
        padding: 8px 12px;
        text-align: center;
        margin-bottom: 6px;
    }
    .kpi-val {
        font-family: 'Consolas', 'Courier New', monospace;
        font-size: 1.25rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .kpi-lbl {
        font-size: 0.72rem;
        color: #94A3B8;
        text-transform: uppercase;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    .info-box {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 12px 16px;
        border-radius: 4px;
        margin: 12px 0;
        font-size: 0.92rem;
        line-height: 1.5;
        color: #1E293B;
    }
    .info-box h4 {
        margin-top: 0;
        color: #1E3A8A;
        margin-bottom: 6px;
    }
</style>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# INICJALIZACJA STANU SESJI
# -----------------------------------------------------------------------------
if "ghost_traces" not in st.session_state:
    st.session_state["ghost_traces"] = []
    if "ghost_trace" in st.session_state and st.session_state["ghost_trace"] is not None:
        st.session_state["ghost_traces"].append(st.session_state["ghost_trace"])

GHOST_COLORS = [
    "#94A3B8",  # Szary (ślad 1)
    "#A78BFA",  # Fioletowy (ślad 2)
    "#2DD4BF",  # Morski / Turkusowy (ślad 3)
    "#FB7185",  # Koralowy / Różowy (ślad 4)
    "#FCD34D",  # Złoty / Żółty (ślad 5)
]
MAX_GHOSTS = 5

if "raw_measurements" not in st.session_state:
    # Surowe pomiary studenta: lista słowników
    st.session_state["raw_measurements"] = []

if "calc_columns" not in st.session_state:
    # Włączone kolumny obliczeniowe
    st.session_state["calc_columns"] = {
        "inv_t": False,    # 1/Δt [1/ms]
        "charge": False    # ΔQ/S = Ip · Δt [nC/cm²]
    }

if "student_analysis" not in st.session_state:
    st.session_state["student_analysis"] = {
        "rheobase": "",
        "chronaxy": "",
        "method_desc": "",
        "charge_concl": ""
    }


# -----------------------------------------------------------------------------
# WERYFIKACJA HASŁA DOSTĘPU (STREAMLIT SECRETS)
# -----------------------------------------------------------------------------
def check_password() -> bool:
    """Zwraca True, jeśli użytkownik podał prawidłowe hasło dostępu."""
    if "APP_PASSWORD" not in st.secrets:
        st.error("⚠️ Brak konfiguracji `APP_PASSWORD` w pliku `.streamlit/secrets.toml` lub panelu Streamlit Cloud Settings.")
        st.info("Dodaj wpis `APP_PASSWORD = \"twoje_haslo\"` do konfiguracji.")
        return False

    def password_entered():
        """Weryfikuje hasło wprowadzone przez użytkownika."""
        if st.session_state.get("password_input", "") == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            if "password_input" in st.session_state:
                del st.session_state["password_input"]  # Nie przechowujemy hasła w stanie sesji
        else:
            st.session_state["password_correct"] = False

    # Jeśli użytkownik już został pomyślnie uwierzytelniony w bieżącej sesji:
    if st.session_state.get("password_correct", False):
        return True

    # Wycentrowany panel logowania
    _, col_center, _ = st.columns([1, 1.3, 1])
    with col_center:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background: linear-gradient(135deg, #0F172A 0%, #1E293B 100%); border: 1px solid #334155; border-radius: 12px; padding: 26px 28px; text-align: center; box-shadow: 0 10px 25px -5px rgba(0,0,0,0.5);">
            <div style="font-size: 2.2rem; margin-bottom: 8px;">🔒</div>
            <h2 style="color: #F8FAFC; margin: 0 0 6px 0; font-size: 1.35rem;">Wirtualna Pracownia Biofizyki</h2>
            <p style="color: #94A3B8; font-size: 0.90rem; margin: 0;">Rozdział 21: Potencjał Czynnościowy Neuronu</p>
        </div>
        """, unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        st.text_input(
            "Wprowadź hasło dostępu do stanowiska:",
            type="password",
            on_change=password_entered,
            key="password_input",
            placeholder="Wpisz hasło i wciśnij Enter..."
        )

        if st.button("🔓 Zaloguj do stanowiska", use_container_width=True):
            password_entered()
            st.rerun()

        if "password_correct" in st.session_state and not st.session_state["password_correct"]:
            st.error("❌ Nieprawidłowe hasło dostępu. Spróbuj ponownie.")

    return False


if not check_password():
    st.stop()


# -----------------------------------------------------------------------------
# NAGŁÓWEK GŁÓWNY
# -----------------------------------------------------------------------------
st.markdown("""
<div class="app-header">
    <h1>⚡ Wirtualna Pracownia Biofizyki: Potencjał Czynnościowy Neuronu <span style="font-size:0.85rem; font-weight:normal; background:#1E3A8A; padding:2px 8px; border-radius:4px;">Wersja 2.1</span></h1>
    <p>Trzykanałowy oscyloskop laboratoryjny i generator bodźców elektrycznych w oparciu o model biofizyczny (Rozdział 21 podręcznika)</p>
</div>
""", unsafe_allow_html=True)


# -----------------------------------------------------------------------------
# UKŁAD DWUKOLUMNOWY
# -----------------------------------------------------------------------------
col_ctrl, col_main = st.columns([1.05, 2.95])


# =============================================================================
# LEWA KOLUMNA: WIRTUALNY STYMULATOR LABORATORYJNY
# =============================================================================
with col_ctrl:
    st.markdown("### 🎛️ Wirtualny Stymulator")
    
    # Dokładnie trzy tryby stymulatora (zgodnie z Pkt 5 wytycznych)
    mode = st.radio(
        "Tryb stymulatora:",
        [
            "1️⃣ Pojedynczy bodziec",
            "2️⃣ Dwa bodźce",
            "3️⃣ Seria 3 bodźców"
        ],
        index=0,
        key="stim_mode"
    )
    
    st.markdown("---")
    
    dt = 0.01  # stały krok całkowania [ms]
    
    # -------------------------------------------------------------------------
    # PARAMETRY W ZALEŻNOŚCI OD WYBRANEGO TRYBU (MANUALNA NASTAWA)
    # -------------------------------------------------------------------------
    if "1️⃣" in mode:
        st.markdown("##### 📍 Pojedynczy bodziec prostokątny")
        
        dur1 = st.number_input(
            "Czas trwania bodźca Δt [ms]:",
            min_value=0.1, max_value=30.0, value=1.0, step=0.1, format="%.2f",
            key="p1_dur"
        )
        amp1 = st.number_input(
            "Gęstość prądu bodźca J [µA/cm²]:",
            min_value=-60.0, max_value=120.0, value=20.0, step=0.5, format="%.2f",
            help="Wartości dodatnie depolaryzują błonę; wartości ujemne (J < 0) służą do badania hiperpolaryzacji.",
            key="p1_amp"
        )
        start1 = st.number_input(
            "Początek bodźca [ms]:",
            min_value=0.5, max_value=10.0, value=2.0, step=0.5,
            key="p1_start"
        )
        
        t_max_default = max(25.0, start1 + dur1 + 15.0)
        t_max = st.number_input("Podstawa czasu oscyloskopu [ms]:", min_value=15.0, max_value=80.0, value=float(t_max_default), step=5.0)
        
        times = np.linspace(0, t_max, int(t_max / dt) + 1)
        stimulus = hh_model.generate_single_pulse(times, amp1, dur1, start=start1)
        current_cfg_str = f"Pojedynczy: J = {amp1:.1f} µA/cm², Δt = {dur1:.2f} ms"

    elif "2️⃣" in mode:
        st.markdown("##### 📍 Dwa bodźce prostokątne")
        st.caption("Do badania zjawisk refrakcji, akomodacji i wpływu hiperpolaryzacji wstępnej")
        
        col_b1, col_b2 = st.columns(2)
        with col_b1:
            st.markdown("**Bodziec 1**")
            amp1 = st.number_input("J₁ [µA/cm²]:", min_value=-60.0, max_value=120.0, value=25.0, step=0.5, key="d_amp1")
            dur1 = st.number_input("Δt₁ [ms]:", min_value=0.1, max_value=25.0, value=1.0, step=0.1, key="d_dur1")
        with col_b2:
            st.markdown("**Bodziec 2**")
            amp2 = st.number_input("J₂ [µA/cm²]:", min_value=-60.0, max_value=120.0, value=30.0, step=0.5, key="d_amp2")
            dur2 = st.number_input("Δt₂ [ms]:", min_value=0.1, max_value=25.0, value=1.0, step=0.1, key="d_dur2")
            
        start1 = st.number_input("Początek 1. bodźca [ms]:", min_value=0.5, max_value=10.0, value=2.0, step=0.5, key="d_start1")
        interval = st.number_input(
            "Odstęp między bodźcami Δτ [ms]:",
            min_value=-5.0, max_value=30.0, value=5.0, step=0.2,
            help="Czas od zakończenia pierwszego bodźca do rozpoczęcia drugiego. Wartość 0 oznacza bezpośrednie sąsiedztwo; wartości ujemne oznaczają nakładanie się impulsów.",
            key="d_interval"
        )
        
        t_max_default = max(30.0, start1 + dur1 + max(0.0, interval) + dur2 + 15.0)
        t_max = st.number_input("Podstawa czasu oscyloskopu [ms]:", min_value=20.0, max_value=90.0, value=float(t_max_default), step=5.0)
        
        times = np.linspace(0, t_max, int(t_max / dt) + 1)
        stimulus = hh_model.generate_dual_pulses(times, amp1, dur1, amp2, dur2, interval, start1=start1)
        current_cfg_str = f"Dwa bodźce: J₁={amp1:.1f}, J₂={amp2:.1f}, Δτ={interval:.1f} ms"

    else:
        st.markdown("##### 📍 Seria 3 bodźców prostokątnych")
        st.caption("Do badania sumowania bodźców podprogowych w czasie (Ryc. 6 z podręcznika)")
        
        amp_train = st.number_input(
            "Gęstość prądu każdego bodźca J [µA/cm²]:",
            min_value=-40.0, max_value=80.0, value=11.5, step=0.2,
            key="tr_amp"
        )
        dur_train = st.number_input(
            "Czas trwania każdego bodźca Δt [ms]:",
            min_value=0.1, max_value=5.0, value=0.8, step=0.1,
            key="tr_dur"
        )
        interval_train = st.number_input(
            "Odstęp między bodźcami Δτ [ms]:",
            min_value=0.1, max_value=20.0, value=1.0, step=0.2,
            help="Czas od zakończenia danego bodźca do rozpoczęcia następnego.",
            key="tr_interval"
        )
        start1 = st.number_input("Początek pierwszego bodźca [ms]:", min_value=0.5, max_value=10.0, value=2.0, step=0.5, key="tr_start1")
        
        t_max_default = max(30.0, start1 + 3 * (dur_train + interval_train) + 15.0)
        t_max = st.number_input("Podstawa czasu oscyloskopu [ms]:", min_value=20.0, max_value=90.0, value=float(t_max_default), step=5.0)
        
        times = np.linspace(0, t_max, int(t_max / dt) + 1)
        stimulus = hh_model.generate_pulse_train(times, amp_train, dur_train, interval_train, n_pulses=3, start=start1)
        current_cfg_str = f"Seria 3 bodźców: J={amp_train:.1f} µA/cm², Δt={dur_train:.1f} ms, Δτ={interval_train:.1f} ms"

    # Wykonanie symulacji numerycznej
    res = hh_model.simulate_hh(stimulus, times)
    
    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # TRYB DUCHA (GHOST TRACES - MAX 5)
    # -------------------------------------------------------------------------
    st.markdown("##### 👻 Tryb Ducha (Ślady Referencyjne, max 5)")
    st.caption("Zapamiętaj do 5 krzywych, aby nałożyć je na siebie i porównać na oscyloskopie.")
    
    num_ghosts = len(st.session_state["ghost_traces"])
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        if st.button(f"📌 Zamroź ({num_ghosts}/5)", use_container_width=True, disabled=(num_ghosts >= MAX_GHOSTS)):
            color = GHOST_COLORS[num_ghosts % len(GHOST_COLORS)]
            st.session_state["ghost_traces"].append({
                "id": num_ghosts + 1,
                "t": res.t.copy(),
                "V": res.V.copy(),
                "g_Na": res.g_Na.copy(),
                "g_K": res.g_K.copy(),
                "I_stim": res.I_stim.copy(),
                "cfg": current_cfg_str,
                "color": color
            })
            st.rerun()
            
    with col_g2:
        if st.button("🗑️ Wyczyść", use_container_width=True, disabled=(num_ghosts == 0)):
            st.session_state["ghost_traces"] = []
            st.rerun()
            
    if num_ghosts > 0:
        for i, g in enumerate(st.session_state["ghost_traces"]):
            st.markdown(
                f'<div style="font-size: 0.80rem; margin-bottom: 3px; padding: 3px 8px; border-radius: 4px; '
                f'background: rgba(15, 23, 42, 0.7); border-left: 3px solid {g["color"]}; color: #E2E8F0;">'
                f'<strong style="color: {g["color"]}">#{i+1}:</strong> {g["cfg"]}'
                f'</div>',
                unsafe_allow_html=True
            )
        if st.button("↩ Cofnij ostatni ślad", use_container_width=True):
            st.session_state["ghost_traces"].pop()
            st.rerun()

    st.markdown("---")
    
    # -------------------------------------------------------------------------
    # ODCZYTY CHWILOWE KOMÓRKI (KPI)
    # -------------------------------------------------------------------------
    st.markdown("##### 📊 Chwilowy stan błony")
    status_html = (
        '<span class="status-badge badge-spike">⚡ Potencjał czynnościowy wygenerowany</span>'
        if res.has_spike else
        '<span class="status-badge badge-sub">💤 Stan podprogowy (brak potencjału czynnościowego)</span>'
    )
    st.markdown(f"**Reakcja komórki:** {status_html}", unsafe_allow_html=True)
    
    kpi_col1, kpi_col2 = st.columns(2)
    with kpi_col1:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val">{res.v_max:+.1f} mV</div>
            <div class="kpi-lbl">Szczyt (U_max)</div>
        </div>
        """, unsafe_allow_html=True)
    with kpi_col2:
        st.markdown(f"""
        <div class="kpi-card">
            <div class="kpi-val">{res.v_min:+.1f} mV</div>
            <div class="kpi-lbl">Min. (U_min)</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("---")
    if st.button("🚪 Wyloguj ze stanowiska", use_container_width=True):
        st.session_state["password_correct"] = False
        st.rerun()


# =============================================================================
# PRAWA KOLUMNA: OSCYLOSKOP, DZIENNIK I PRZEWODNIK
# =============================================================================
with col_main:
    tab_scope, tab_journal, tab_guide = st.tabs([
        "📺 Trzykanałowy Oscyloskop Laboratoryjny",
        "📊 Dziennik Pomiarowy & Kreator Wykresu",
        "📖 Przewodnik Laboratoryjny (Zadania 1–4)"
    ])
    
    # -------------------------------------------------------------------------
    # ZAKŁADKA 1: ZINTEGROWANY TRZYKANAŁOWY OSCYLOSKOP (PLOTLY)
    # -------------------------------------------------------------------------
    with tab_scope:
        # Utworzenie zintegrowanego wykresu 3-panelowego ze wspólną osią czasu
        fig_scope = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.07,
            row_heights=[0.46, 0.32, 0.22],
            subplot_titles=(
                "<b>KANAŁ 1: Potencjał błonowy U(t) [mV]</b>",
                "<b>KANAŁ 2: Przewodności elektryczne błony: g<sub>Na</sub> = 1/R<sub>Na</sub> i g<sub>K</sub> = 1/R<sub>K</sub> [mS/cm²]</b>",
                "<b>KANAŁ 3: Gęstość prądu bodźca J(t) [µA/cm²]</b>"
            )
        )
        
        ghost_traces = st.session_state.get("ghost_traces", [])
        
        # --- ŚLADY REFERENCYJNE (DUCHY, MAX 5) NA WSZYSTKICH TRZECH PANELACH ---
        for i, g in enumerate(ghost_traces):
            g_color = g.get("color", GHOST_COLORS[i % len(GHOST_COLORS)])
            group_name = f"ghost_{i+1}"
            
            # Panel 1: Potencjał U
            fig_scope.add_trace(
                go.Scatter(
                    x=g["t"], y=g["V"],
                    mode="lines",
                    name=f"#{i+1}",
                    line=dict(color=g_color, width=1.6, dash="dash"),
                    hovertemplate=f"U [#{i+1}]: %{{y:.2f}} mV<extra></extra>",
                    legendgroup=group_name,
                    legend="legend",
                    showlegend=True
                ),
                row=1, col=1
            )
            # Panel 2: Przewodności Na i K
            fig_scope.add_trace(
                go.Scatter(
                    x=g["t"], y=g["g_Na"],
                    mode="lines",
                    name=f"g_Na #{i+1}",
                    line=dict(color=g_color, width=1.3, dash="dot"),
                    hoverinfo="skip",
                    legendgroup=group_name,
                    legend="legend2",
                    showlegend=False
                ),
                row=2, col=1
            )
            fig_scope.add_trace(
                go.Scatter(
                    x=g["t"], y=g["g_K"],
                    mode="lines",
                    name=f"g_K #{i+1}",
                    line=dict(color=g_color, width=1.3, dash="dash"),
                    hoverinfo="skip",
                    legendgroup=group_name,
                    legend="legend2",
                    showlegend=False
                ),
                row=2, col=1
            )
            # Panel 3: Gęstość prądu J
            fig_scope.add_trace(
                go.Scatter(
                    x=g["t"], y=g["I_stim"],
                    mode="lines",
                    name=f"J #{i+1}",
                    line=dict(color=g_color, width=1.3, dash="dash"),
                    hoverinfo="skip",
                    legendgroup=group_name,
                    legend="legend3",
                    showlegend=False
                ),
                row=3, col=1
            )

        # --- PANEL 1: POTENCJAŁ BŁONOWY U(t) ---
        fig_scope.add_trace(
            go.Scatter(
                x=res.t, y=res.V,
                mode="lines",
                name="U(t) [mV]",
                line=dict(color="#38BDF8", width=2.8),
                hovertemplate="U: %{y:.2f} mV<extra></extra>",
                legend="legend",
                showlegend=True
            ),
            row=1, col=1
        )
        
        # Linie odniesienia dla panelu 1 (w 100% zgodne z Ryc. 1 i Ryc. 7 podręcznika)
        fig_scope.add_hline(
            y=0.0, line_dash="dash", line_color="#EF4444", line_width=1.0, opacity=0.8,
            annotation_text="0 mV (linia zerowa)", annotation_position="top right",
            annotation_font=dict(color="#FCA5A5", size=10),
            row=1, col=1
        )
        fig_scope.add_hline(
            y=-60.0, line_dash="dot", line_color="#F59E0B", line_width=1.3, opacity=0.9,
            annotation_text="Próg pobudliwości w spoczynku (-60 mV)", annotation_position="top right",
            annotation_font=dict(color="#FDE68A", size=10),
            row=1, col=1
        )
        fig_scope.add_hline(
            y=-90.0, line_dash="dash", line_color="#94A3B8", line_width=1.2, opacity=0.9,
            annotation_text="Potencjał spoczynkowy (-90 mV)", annotation_position="bottom right",
            annotation_font=dict(color="#F1F5F9", size=10),
            row=1, col=1
        )

        # --- PANEL 2: PRZEWODNOŚCI SODOWA I POTASOWA ---
        fig_scope.add_trace(
            go.Scatter(
                x=res.t, y=res.g_Na,
                mode="lines",
                name="g_Na = 1/R_Na (Sód)",
                line=dict(color="#3B82F6", width=2.4),
                hovertemplate="g_Na: %{y:.2f} mS/cm²<extra></extra>",
                legend="legend2",
                showlegend=True
            ),
            row=2, col=1
        )
        fig_scope.add_trace(
            go.Scatter(
                x=res.t, y=res.g_K,
                mode="lines",
                name="g_K = 1/R_K (Potas)",
                line=dict(color="#EF4444", width=2.4),
                hovertemplate="g_K: %{y:.2f} mS/cm²<extra></extra>",
                legend="legend2",
                showlegend=True
            ),
            row=2, col=1
        )

        # --- PANEL 3: GĘSTOŚĆ PRĄDU BODŹCA J(t) ---
        fig_scope.add_trace(
            go.Scatter(
                x=res.t, y=res.I_stim,
                mode="lines",
                name="J(t) (Bodziec)",
                line=dict(color="#F59E0B", width=2.2),
                hovertemplate="J: %{y:.2f} µA/cm²<extra></extra>",
                legend="legend3",
                showlegend=True
            ),
            row=3, col=1
        )

        # Konfiguracja ciemnego motywu, 3 odrębnych białych legend dla każdego kanału i zsynchronizowanego kursora
        common_legend_style = dict(
            orientation="h",
            x=1.0,
            xanchor="right",
            yanchor="bottom",
            bgcolor="rgba(15, 23, 42, 0.95)",
            bordercolor="#475569",
            borderwidth=1.2,
            font=dict(color="#FFFFFF", size=11, family="sans-serif")
        )

        fig_scope.update_layout(
            template="plotly_dark",
            height=710,
            margin=dict(l=60, r=25, t=50, b=35),
            paper_bgcolor="#0A0F1D",
            plot_bgcolor="#030712",
            hovermode="x unified",
            font=dict(color="#F8FAFC", family="sans-serif"),
            showlegend=True,
            legend=dict(**common_legend_style, y=1.015),
            legend2=dict(**common_legend_style, y=0.545),
            legend3=dict(**common_legend_style, y=0.200)
        )

        # Wyraźne białe nagłówki podwykresów wyrównane do lewej strony paska
        for ann in fig_scope['layout']['annotations']:
            ann['x'] = 0.0
            ann['xanchor'] = 'left'
            ann['font'] = dict(color="#F8FAFC", size=12, family="sans-serif")

        # Osie X z czytelnymi etykietami
        fig_scope.update_xaxes(
            title_text="Czas t [ms]",
            title_font=dict(color="#F8FAFC", size=12),
            tickfont=dict(color="#E2E8F0", size=11),
            gridcolor="#1E293B",
            row=3, col=1
        )
        fig_scope.update_xaxes(
            tickfont=dict(color="#E2E8F0", size=11),
            gridcolor="#1E293B",
            row=1, col=1
        )
        fig_scope.update_xaxes(
            tickfont=dict(color="#E2E8F0", size=11),
            gridcolor="#1E293B",
            row=2, col=1
        )

        # Osie Y z czytelnymi etykietami
        fig_scope.update_yaxes(
            title_text="U [mV]",
            title_font=dict(color="#F8FAFC", size=12),
            tickfont=dict(color="#E2E8F0", size=11),
            range=[-105, 55],
            gridcolor="#1E293B",
            row=1, col=1
        )
        fig_scope.update_yaxes(
            title_text="g [mS/cm²]",
            title_font=dict(color="#F8FAFC", size=12),
            tickfont=dict(color="#E2E8F0", size=11),
            gridcolor="#1E293B",
            row=2, col=1
        )
        
        j_min = min(-10.0, float(np.min(res.I_stim)) * 1.25)
        j_max = max(20.0, float(np.max(res.I_stim)) * 1.25)
        fig_scope.update_yaxes(
            title_text="J [µA/cm²]",
            title_font=dict(color="#F8FAFC", size=12),
            tickfont=dict(color="#E2E8F0", size=11),
            range=[j_min, j_max],
            gridcolor="#1E293B",
            row=3, col=1
        )

        st.plotly_chart(fig_scope, use_container_width=True)
        
        # Pasek pomocniczy pod oscyloskopem
        c_sub1, c_sub2, c_sub3 = st.columns(3)
        with c_sub1:
            st.info(f"📍 **Czas szczytu potencjału czynnościowego:** `{res.spike_peak_time:.2f} ms`" if res.spike_peak_time else "📍 **Czas szczytu potencjału czynnościowego:** `Brak (stan podprogowy)`")
        with c_sub2:
            st.info(f"📍 **Szczyt przewodności sodowej:** `{np.max(res.g_Na):.1f} mS/cm²`")
        with c_sub3:
            st.info(f"📍 **Szczyt przewodności potasowej:** `{np.max(res.g_K):.1f} mS/cm²`")

    # -------------------------------------------------------------------------
    # ZAKŁADKA 2: DZIENNIK POMIAROWY & KREATOR WYKRESU (ZADANIE 2)
    # -------------------------------------------------------------------------
    with tab_journal:
        st.markdown("#### 📝 Dziennik Pomiarowy Studenta")
        st.caption("Samodzielne gromadzenie punktów progowych, obliczanie wielkości pochodnych i tworzenie wykresu zależności: Iₚ = f(Δt).")

        col_ent1, col_ent2 = st.columns([1.1, 1.9])
        
        with col_ent1:
            st.markdown("##### ✍️ Wprowadź wyznaczony punkt progowy")
            # Domyślny czas z nastawy stymulatora
            init_dur = dur1 if "1️⃣" in mode else 1.0
            
            ent_dur = st.number_input("Czas trwania bodźca Δt [ms]:", min_value=0.1, max_value=30.0, value=float(init_dur), step=0.1, key="ent_d")
            ent_ip = st.number_input(
                "Wyznaczona progowa gęstość prądu Iₚ [µA/cm²]:",
                min_value=0.1, max_value=150.0, value=13.2, step=0.2, key="ent_i",
                help="Wartość progowa wyznaczona metodą kolejnych przybliżeń (bisekcji)."
            )
            ent_note = st.text_input("Notatka / Identyfikator pomiaru:", value=f"Pomiar {len(st.session_state['raw_measurements']) + 1}", key="ent_n")
            
            if st.button("➕ Zapisz punkt pomiarowy do dziennika", use_container_width=True):
                st.session_state["raw_measurements"].append({
                    "Nr": len(st.session_state["raw_measurements"]) + 1,
                    "Δt [ms]": float(ent_dur),
                    "Ip [µA/cm²]": float(ent_ip),
                    "Notatka": ent_note
                })
                st.success("Zapisano punkt do dziennika pomiarowego!")
                st.rerun()

        with col_ent2:
            st.markdown("##### 🧮 Pomocnik bisekcji (manualny kalkulator środka przedziału)")
            st.caption("Pkt 1 ze str. 180 podręcznika: zawężanie przedziału [A, B] między odpowiedzią podprogową a ponadprogową.")
            col_bis1, col_bis2, col_bis3 = st.columns(3)
            with col_bis1:
                val_a = st.number_input("Wartość A (podprogowa) [µA/cm²]:", value=10.0, step=0.5, key="bis_a")
            with col_bis2:
                val_b = st.number_input("Wartość B (ponadprogowa) [µA/cm²]:", value=20.0, step=0.5, key="bis_b")
            with col_bis3:
                mid_val = (val_a + val_b) / 2.0
                st.metric("Kolejna próba: (A+B)/2", f"{mid_val:.2f} µA/cm²")

        st.markdown("---")
        
        # ---------------------------------------------------------------------
        # TABELA POMIARÓW STUDENCKICH
        # ---------------------------------------------------------------------
        if st.session_state["raw_measurements"]:
            df_raw = pd.DataFrame(st.session_state["raw_measurements"])
            
            # Obsługa kolumn obliczeniowych (dodawanych jawnie na żądanie studenta)
            df_display = df_raw.copy()
            
            if st.session_state["calc_columns"]["inv_t"]:
                df_display["1/Δt [1/ms]"] = np.round(1.0 / df_display["Δt [ms]"], 4)
                
            if st.session_state["calc_columns"]["charge"]:
                # µA/cm² * ms = nC/cm²
                df_display["ΔQ/S [nC/cm²]"] = np.round(df_display["Ip [µA/cm²]"] * df_display["Δt [ms]"], 3)
                
            st.dataframe(df_display, hide_index=True, use_container_width=True)
            
            # Narzędzia zarządzania tabelą
            col_act1, col_act2, col_act3 = st.columns([1.2, 1.0, 1.2])
            with col_act1:
                st.markdown("**Dodaj kolumny obliczeniowe:**")
                if not st.session_state["calc_columns"]["inv_t"]:
                    if st.button("➕ Oblicz i dodaj: 1/Δt [1/ms]", use_container_width=True):
                        st.session_state["calc_columns"]["inv_t"] = True
                        st.rerun()
                else:
                    if st.button("➖ Ukryj kolumnę: 1/Δt", use_container_width=True):
                        st.session_state["calc_columns"]["inv_t"] = False
                        st.rerun()
                        
                if not st.session_state["calc_columns"]["charge"]:
                    if st.button("➕ Oblicz i dodaj: ΔQ/S = Ip · Δt [nC/cm²]", use_container_width=True):
                        st.session_state["calc_columns"]["charge"] = True
                        st.rerun()
                else:
                    if st.button("➖ Ukryj kolumnę: ΔQ/S", use_container_width=True):
                        st.session_state["calc_columns"]["charge"] = False
                        st.rerun()

            with col_act2:
                st.markdown("**Usuwanie pomiaru:**")
                row_to_del = st.selectbox("Wybierz Nr do usunięcia:", df_raw["Nr"].tolist(), key="del_sel")
                if st.button("🗑️ Usuń wybrany pomiar", use_container_width=True):
                    st.session_state["raw_measurements"] = [
                        r for r in st.session_state["raw_measurements"] if r["Nr"] != row_to_del
                    ]
                    # Przenumerowanie
                    for idx, r in enumerate(st.session_state["raw_measurements"]):
                        r["Nr"] = idx + 1
                    st.rerun()

            with col_act3:
                st.markdown("**Zarządzanie dziennikiem:**")
                csv_bytes = df_display.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "📥 Pobierz dziennik (CSV)",
                    csv_bytes,
                    "pomiary_pobudliwosci_potencjal.csv",
                    "text/csv",
                    use_container_width=True
                )
                confirm_clear = st.checkbox("Potwierdzam chęć usunięcia wszystkich pomiarów", key="conf_clr")
                if st.button("⚠️ Wyczyść cały dziennik", use_container_width=True, disabled=not confirm_clear):
                    st.session_state["raw_measurements"] = []
                    st.session_state["calc_columns"] = {"inv_t": False, "charge": False}
                    st.rerun()

            # -----------------------------------------------------------------
            # JEDEN KREATOR WYKRESU (ZGODNIE Z PKT 9 WYTYCZNYCH)
            # -----------------------------------------------------------------
            st.markdown("---")
            st.markdown("### 📈 Kreator Wykresu Pomiarowego")
            st.caption("Wybierz osie współrzędnych i utwórz wykres zgodnie z planowanym etapem analizy.")
            
            # Dostępne opcje osi w zależności od włączonych kolumn
            x_options = ["Δt [ms]"]
            if st.session_state["calc_columns"]["inv_t"]:
                x_options.append("1/Δt [1/ms]")
                
            y_options = ["Ip [µA/cm²]"]
            if st.session_state["calc_columns"]["charge"]:
                y_options.append("ΔQ/S [nC/cm²]")
                
            col_ax1, col_ax2, col_ax3 = st.columns([1, 1, 1])
            with col_ax1:
                sel_x = st.selectbox("Wybierz wielkość na osi X:", x_options, key="sel_x_ax")
            with col_ax2:
                sel_y = st.selectbox("Wybierz wielkość na osi Y:", y_options, key="sel_y_ax")
            with col_ax3:
                st.write("")
                st.write("")
                make_chart = st.button("📊 Utwórz / aktualizuj wykres", use_container_width=True)

            # Rysowanie wykresu
            df_plot = df_display.sort_values(by=sel_x)
            x_data = df_plot[sel_x].values
            y_data = df_plot[sel_y].values
            
            fig_custom = go.Figure()
            
            # Punkty pomiarowe
            fig_custom.add_trace(
                go.Scatter(
                    x=x_data, y=y_data,
                    mode="markers+lines",
                    name="Punkty pomiarowe",
                    marker=dict(size=9, color="#38BDF8"),
                    line=dict(color="#38BDF8", dash="dash")
                )
            )
            
            # Opcjonalne dopasowanie prostej regresji (tylko dla Y = Ip i X = 1/Δt)
            reg_active = False
            if sel_x == "1/Δt [1/ms]" and sel_y == "Ip [µA/cm²]":
                enable_reg = st.checkbox("Dopasuj prostą regresji liniowej: Iₚ = a · (1/Δt) + b", value=False, key="en_reg")
                if enable_reg and len(np.unique(x_data)) >= 2:
                    reg_active = True
                    p_fit = np.polyfit(x_data, y_data, 1)
                    slope_a, intercept_b = p_fit[0], p_fit[1]
                    
                    # R^2
                    y_pred = slope_a * x_data + intercept_b
                    ss_tot = np.sum((y_data - np.mean(y_data))**2)
                    ss_res = np.sum((y_data - y_pred)**2)
                    r_sq = 1.0 - (ss_res / ss_tot) if ss_tot > 0 else 1.0
                    
                    x_line = np.linspace(0.0, float(np.max(x_data)) * 1.15, 100)
                    y_line = slope_a * x_line + intercept_b
                    
                    fig_custom.add_trace(
                        go.Scatter(
                            x=x_line, y=y_line,
                            mode="lines",
                            name=f"Prosta regresji: Iₚ = {slope_a:.2f} · (1/Δt) + {intercept_b:.2f} (R² = {r_sq:.3f})",
                            line=dict(color="#EF4444", width=2.0)
                        )
                    )
                    st.info(f"📐 **Równanie prostej dopasowanej:** `Iₚ = {slope_a:.2f} · (1/Δt) + {intercept_b:.2f}` (współczynnik determinacji R² = {r_sq:.4f})")

            # Tytuł wykresu zgodny z wytycznymi
            chart_title = "Zależność natężenia bodźca progowego od czasu trwania: Iₚ = f(Δt)" if sel_x == "Δt [ms]" and sel_y == "Ip [µA/cm²]" else f"Wykres pomiarowy: {sel_y} = f({sel_x})"
            
            fig_custom.update_layout(
                title=dict(text=f"<b>{chart_title}</b>", font=dict(color="#F8FAFC", size=13)),
                template="plotly_dark",
                height=450,
                paper_bgcolor="#0A0F1D",
                plot_bgcolor="#030712",
                margin=dict(l=50, r=30, t=50, b=40),
                font=dict(color="#F8FAFC", family="sans-serif"),
                legend=dict(
                    bgcolor="rgba(15, 23, 42, 0.95)",
                    bordercolor="#475569",
                    borderwidth=1.5,
                    font=dict(color="#FFFFFF", size=11, family="sans-serif")
                )
            )
            fig_custom.update_xaxes(
                title_text=sel_x,
                title_font=dict(color="#F8FAFC", size=12),
                tickfont=dict(color="#E2E8F0", size=11),
                gridcolor="#1E293B"
            )
            fig_custom.update_yaxes(
                title_text=sel_y,
                title_font=dict(color="#F8FAFC", size=12),
                tickfont=dict(color="#E2E8F0", size=11),
                gridcolor="#1E293B"
            )
            
            st.plotly_chart(fig_custom, use_container_width=True)

            # Pola na wnioski i obliczenia studenta (brak automatycznego gotowca)
            if reg_active:
                st.markdown("##### 📝 Twoje wyznaczone parametry i interpretacja")
                st.caption("Pkt 4–6 ze str. 181 podręcznika: na podstawie dopasowanego równania prostej oblicz reobazę R oraz chronaksję CH.")
                
                col_inp1, col_inp2 = st.columns(2)
                with col_inp1:
                    usr_rheo = st.text_input("Twoja wyznaczona reobaza R [µA/cm²] (wyraz b prostej):", value=st.session_state["student_analysis"]["rheobase"], key="u_rh")
                with col_inp2:
                    usr_chron = st.text_input("Twoja obliczona chronaksja CH [ms] (ze wzoru CH = a / R):", value=st.session_state["student_analysis"]["chronaxy"], key="u_ch")
                    
                usr_desc = st.text_area(
                    "Uzasadnienie metody i interpretacja fizyczna wyznaczonych parametrów:",
                    value=st.session_state["student_analysis"]["method_desc"],
                    key="u_desc"
                )
                usr_concl = st.text_area(
                    "Ocena stałości ładunku progowego ΔQ/S i przyczyn odstępstw dla długich czasów:",
                    value=st.session_state["student_analysis"]["charge_concl"],
                    key="u_concl"
                )
                
                if st.button("💾 Zapisz opracowanie i wnioski"):
                    st.session_state["student_analysis"]["rheobase"] = usr_rheo
                    st.session_state["student_analysis"]["chronaxy"] = usr_chron
                    st.session_state["student_analysis"]["method_desc"] = usr_desc
                    st.session_state["student_analysis"]["charge_concl"] = usr_concl
                    st.success("Zapisano opracowanie do sesji!")

        else:
            st.info("ℹ️ Dziennik pomiarowy jest pusty. Wprowadź wyznaczone punkty progowe w formularzu po lewej stronie, aby rozpocząć tworzenie tabeli i wykresu.")

    # -------------------------------------------------------------------------
    # ZAKŁADKA 3: PRZEWODNIK LABORATORYJNY (ZADANIA 1–4 Z PODRĘCZNIKA)
    # -------------------------------------------------------------------------
    with tab_guide:
        st.markdown("### 📋 Program Ćwiczenia Laboratoryjnego (Rozdział 21)")
        st.markdown("""
        Wirtualne stanowisko laboratoryjne służy do realizacji czterech kluczowych zadań badawczych opisanych w podręczniku.
        
        ---
        #### 🔹 Zadanie 1: Anatomia potencjału i model Hodgkina-Huxleya (Rozdz. 1–3)
        1. W lewym panelu wybierz `1️⃣ Pojedynczy bodziec`.
        2. Ustaw czas trwania $\\Delta t = 1.0\\text{ ms}$.
        3. Sprawdź odpowiedź błony na bodziec podprogowy (wpisz ręcznie $J = 5.0\\ \\mu\\text{A/cm}^2$) oraz ponadprogowy (wpisz $J = 20.0\\ \\mu\\text{A/cm}^2$).
        4. Za pomocą przycisku *„📌 Zamroź ślad”* nałóż oba przebiegi na siebie.
        5. Na oscyloskopie zidentyfikuj:
           - **wykładnicze narastanie i opadanie potencjału podprogowego** (wynikające z ładowania i rozładowania pojemności elektrycznej błony $C$ – porównaj z Ryc. 3b i Ryc. 7 w podręczniku),
           - **gwałtowny wzrost przewodności sodowej $1/R_{Na}$** odpowiadający za fazę depolaryzacji i szczyt przepolaryzowania ($U_{max} \\approx +30\\text{ mV}$ do $+35\\text{ mV}$) po przekroczeniu progu $-60\\text{ mV}$,
           - **opóźniony wzrost przewodności potasowej $1/R_K$** odpowiadający za repolaryzację oraz następczy potencjał hiperpolaryzacyjny ($U_{min} \\approx -96\\text{ mV}$ do $-97\\text{ mV}$).
           
        ---
        #### 🔹 Zadanie 2: Zależność natężenia bodźca progowego od czasu trwania: Iₚ = f(Δt) (Pkt 1–4)
        1. Dla czasów trwania bodźca $\\Delta t$ w zakresie od $0.3\\text{ ms}$ do $10.0\\text{ ms}$ wyznacz metodą kolejnych przybliżeń (bisekcji) minimalną progową gęstość prądu $I_p$, która wyzwala potencjał czynnościowy.
        2. Zapisz każdy punkt w zakładce *Dziennik Pomiarowy*.
        3. Włącz kolumnę obliczeniową $1/\\Delta t$ oraz $\\Delta Q/S = I_p \\cdot \\Delta t$.
        4. W Kreatorze Wykresu sporządź:
           - wykres $I_p = f(\\Delta t)$,
           - wykres linearyzacji $I_p = f(1/\\Delta t)$ z dopasowaną prostą regresji,
           - wykres ładunku $\\Delta Q/S = f(\\Delta t)$.
        5. Z dopasowanego równania prostej $I_p = a \\cdot (1/\\Delta t) + b$ odczytaj reobazę $R = b$ oraz oblicz chronaksję $CH = a / R$.
        6. Zinterpretuj stałość ładunku progowego $\\Delta Q/S$ dla krótkich czasów i wyjaśnij przyczyny jego wzrostu dla bodźców długich (działanie pomp i inaktywacja sodowa).
        
        ---
        #### 🔹 Zadanie 3: Sumowanie bodźców w czasie (Ryc. 6) vs Hiperpolaryzacja (Pkt 6)
        1. **Sumowanie w czasie:** Wybierz tryb `3️⃣ Seria 3 bodźców`.
           - Ustaw parametry bodźca podprogowego (np. $J = 11.5\\ \\mu\\text{A/cm}^2, \\Delta t = 0.8\\text{ ms}$).
           - Zbadaj odpowiedź dla małego odstępu ($\\Delta \\tau = 1.0\\text{ ms}$) oraz dużego odstępu ($\\Delta \\tau = 5.0\\text{ ms}$).
           - Porównaj przebiegi za pomocą Trybu Ducha.
        2. **Hiperpolaryzacja:** W trybie pojedynczego bodźca zbadaj reakcję na prądy ujemne ($J < 0$, czas $5\\text{ ms}$). Zaobserwuj zachowanie błony po ustaniu bodźca.
        
        ---
        #### 🔹 Zadanie 4: Dwa mechanizmy wzrostu progu — Akomodacja vs Refrakcja (Pkt 5 i 7)
        1. **Akomodacja:** W trybie `2️⃣ Dwa impulsy` zbadaj próg pobudzenia dla krótkiego bodźca testującego ($\\Delta t_2 = 0.4\\text{ ms}$) podawanego samodzielnie oraz poprzedzonego długim bodźcem podprogowym ($\\Delta t_1 = 3.0\\text{ ms}$). Zauważ, jak wstępna podprogowa depolaryzacja inaktywuje układ sodowy i zwiększa próg $I_p$.
        2. **Refrakcja:** Ustaw pierwszy bodziec ponadprogowy ($J_1 = 25\\ \\mu\\text{A/cm}^2, \\Delta t_1 = 1.0\\text{ ms}$). Podając drugi bodziec silny ($J_2 = 30\\ \\mu\\text{A/cm}^2, \\Delta t_2 = 1.0\\text{ ms}$) w zmiennym odstępie $\\Delta \\tau$, zbadaj granicę refrakcji bezwzględnej (potencjał czynnościowy nie zostaje wygenerowany) oraz refrakcji względnej (kolejny potencjał czynnościowy o obniżonej amplitudzie).
        """)
