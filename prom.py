import numpy as np
import matplotlib.pyplot as plt
from ipywidgets import interact, FloatSlider, Dropdown, IntSlider

# --- 1. DANE FIZYCZNE (KOMPLETNA BAZA) ---
baza_izotopow = {
    "Cez-137": {
        "energia_opis": "0.662 MeV",
        "materialy": {
            "Ołów (Pb)": 0.110,
            "Beton zwykły": 0.077,
            "Kość ludzka": 0.086
        }
    },
    "Kobalt-60": {
        "energia_opis": "1.25 MeV",
        "materialy": {
            "Ołów (Pb)": 0.058,
            "Beton zwykły": 0.058,
            "Kość ludzka": 0.059
        }
    }
}

# Właściwości stałe materiałów
MATERIALY_INFO = {
    "Ołów (Pb)":    {"gestosc": 11.34, "kolor": "navy"},
    "Beton zwykły": {"gestosc": 2.35,  "kolor": "darkorange"},
    "Kość ludzka":  {"gestosc": 1.85,  "kolor": "#8B4513"} # Brązowy
}

def symulacja_colab_zoom(wybrany_izotop, aktywny_material, grubosc_sciany_cm, zakres_osi_x):

    # --- PRZYGOTOWANIE DANYCH ---
    dane_izotopu = baza_izotopow[wybrany_izotop]

    # Generujemy oś X dynamicznie na podstawie suwaka "Zoom"
    # Dajemy 400 punktów dla gładkości
    x_range = np.linspace(0, zakres_osi_x, 400)

    plt.figure(figsize=(12, 7))

    # Zmienne pomocnicze do przechowywania danych wybranego materiału
    active_vals = {}

    # --- RYSOWANIE (PĘTLA GHOSTING) ---
    # Rysujemy wszystkie materiały, ale niewybrane są "duchami"
    for nazwa_mat, info in MATERIALY_INFO.items():

        # 1. Fizyka
        gestosc = info["gestosc"]
        mi_masowe = dane_izotopu["materialy"][nazwa_mat]
        mu = mi_masowe * gestosc  # Współczynnik liniowy [1/cm]

        y_values = 100 * np.exp(-mu * x_range)

        # 2. Rysowanie
        if nazwa_mat == aktywny_material:
            # To jest ten wybrany (Kolorowy, gruby)
            plt.plot(x_range, y_values, color=info["kolor"], linewidth=3.5, label=nazwa_mat, zorder=10)
            plt.fill_between(x_range, y_values, color=info["kolor"], alpha=0.1)

            # Zapisujemy dane do późniejszego wykorzystania (kropka, tekst)
            active_vals = {
                "mu": mu, "mi": mi_masowe, "rho": gestosc,
                "y_point": 100 * np.exp(-mu * grubosc_sciany_cm),
                "color": info["kolor"]
            }
        else:
            # To jest tło (Szary, przerywany)
            plt.plot(x_range, y_values, color='gray', alpha=0.3, linewidth=1.5, linestyle='--', label=f'{nazwa_mat} (tło)')

    # --- INTERAKCJA UŻYTKOWNIKA (KROPKA) ---
    # Rysujemy kropkę tylko jeśli mieści się w obecnym zoomie
    if grubosc_sciany_cm <= zakres_osi_x:
        plt.plot(grubosc_sciany_cm, active_vals["y_point"], 'o',
                 color=active_vals["color"], markersize=12, markeredgecolor='black', zorder=11)

        plt.vlines(grubosc_sciany_cm, 0, active_vals["y_point"], colors='black', linestyles=':', alpha=0.5)
        plt.hlines(active_vals["y_point"], 0, grubosc_sciany_cm, colors='black', linestyles=':', alpha=0.5)
    else:
        # Jeśli użytkownik ustawił grubość poza wykresem, wyświetlamy info
        plt.text(zakres_osi_x/2, 50, "PUNKT POZA ZAKRESEM WIDOKU\nZwiększ skalę osi X!",
                 color='red', fontsize=14, ha='center', bbox=dict(facecolor='white', edgecolor='red'))

    # --- HVL (Warstwa Połówkowa) ---
    hvl = np.log(2) / active_vals["mu"]
    if hvl < zakres_osi_x:
        plt.text(hvl, 5, f' HVL={hvl:.1f}cm', color=active_vals["color"], rotation=90, fontweight='bold')
        plt.axvline(x=hvl, color=active_vals["color"], linestyle='--', alpha=0.6)

    # --- OPISY WYKRESU ---
    plt.title(f'Symulacja: {wybrany_izotop} ({dane_izotopu["energia_opis"]})', fontsize=16, fontweight='bold')
    plt.xlabel('Grubość osłony [cm]', fontsize=12)
    plt.ylabel('Transmisja promieniowania [%]', fontsize=12)
    plt.xlim(0, zakres_osi_x) # Tu działa nasz ZOOM
    plt.ylim(0, 105)
    plt.grid(True, linestyle='-', alpha=0.2)

    # Legenda (usuwanie duplikatów)
    handles, labels = plt.gca().get_legend_handles_labels()
    by_label = dict(zip(labels, handles))
    plt.legend(by_label.values(), by_label.keys(), loc='upper right')

    # --- PANEL INFORMACYJNY ---
    info_text = (
        f"MATERIAŁ:   {aktywny_material}\n"
        f"---------------------------\n"
        f"Gęstość:      {active_vals['rho']} g/cm3\n"
        f"Wsp. masowy:  {active_vals['mi']:.3f} cm2/g\n"
        f"--> Wsp. lin: {active_vals['mu']:.3f} 1/cm\n"
        f"---------------------------\n"
        f"USTAWIONA GRUBOŚĆ: {grubosc_sciany_cm:.1f} cm\n"
        f"PRZEPUSZCZALNOŚĆ:  {active_vals['y_point']:.1f} %\n"
    )

    # Pozycjonowanie ramki (zawsze w ok. 70% szerokości wykresu)
    text_x_pos = zakres_osi_x * 0.65
    plt.text(text_x_pos, 45, info_text, fontsize=11, fontfamily='monospace',
             bbox=dict(facecolor='white', alpha=0.92, edgecolor=active_vals["color"], boxstyle='round,pad=0.5', linewidth=2))

    plt.show()

# --- URUCHOMIENIE WIDŻETÓW ---
print("Wskazówka: Użyj suwaka 'Skala osi X', aby przybliżyć (dla Ołowiu) lub oddalić (dla Betonu).")

interact(symulacja_colab_zoom,
         wybrany_izotop=Dropdown(options=['Cez-137', 'Kobalt-60'], description='Źródło:'),
         aktywny_material=Dropdown(options=list(MATERIALY_INFO.keys()), description='Materiał:'),

         # Nowy suwak do Zoomowania (od 5 cm do 50 cm)
         zakres_osi_x=IntSlider(min=5, max=50, step=1, value=15, description='Skala X [cm]:'),

         # Suwak grubości (pozwalamy mu iść aż do 50, żeby pasował do max skali)
         grubosc_sciany_cm=FloatSlider(min=0, max=50, step=0.1, value=2.0, description='Grubość:'));