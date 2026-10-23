import numpy as np
import matplotlib.pyplot as plt

# Parametry symulacji
dt = 0.01
t_max = 26.0

# Bodźce
stim0_a = 50.0  # Siła pierwszego bodźca
stim0_d = 1.0   # Czas trwania pierwszego bodźca
stim1_a = 50   # Siła drugiego bodźca
stim1_d = 1   # Czas trwania drugiego bodźca
dly = 20      # Opóźnienie pomiędzy bodźcami

# Warunki początkowe
mv = -70.0
t = -dt / 2.0
n, m, h = 0.318, 0.053, 0.596

# Listy na wyniki
times, voltages, g_K, g_Na, i_stim = [], [], [], [], []

while t <= t_max:
    # Zabezpieczenie przed dzieleniem przez zero
    if abs(mv - (-45.0)) < 1e-5: mv += 0.1
    if abs(mv - (-60.0)) < 1e-5: mv += 0.1

    # Współczynniki kinetyczne
    bn = 0.125 * np.exp((-mv - 70) / 80)
    bm = 4 * np.exp((-mv - 70) / 18)
    bh = 1 / (np.exp((-mv - 40) / 10) + 1)
    an = 0.01 * (-mv - 60) / (np.exp((-mv - 60) / 10) - 1)
    am = 0.1 * (-mv - 45) / (np.exp((-mv - 45) / 10) - 1)
    ah = 0.07 * np.exp((-mv - 70) / 20)

    # Równania różniczkowe (Metoda Eulera)
    if t > dt / 2:
        n += (an * (1 - n) - bn * n) * dt
        m += (am * (1 - m) - bm * m) * dt
        h += (ah * (1 - h) - bh * h) * dt
    else:
        n, m, h = an / (an + bn), am / (am + bm), ah / (ah + bh)

    gk, gna = 36 * (n ** 4), 120 * (m ** 3) * h

    # Prądy jonowe
    ik = gk * (-mv - 82)
    ina = gna * (-mv + 45)
    ilk = 0.3 * (-mv - 59.4)

    # Stymulacja prądem
    ia = 0
    if t + dt / 2 >= 0:
        if t + dt / 2 < stim0_d:
            ia = stim0_a
        if t + dt / 2 > dly and t + dt / 2 < dly + stim1_d:
            ia += stim1_a

    # Zmiana napięcia
    mv += (ina + ik + ilk + ia) * dt

    times.append(t)
    voltages.append(mv)
    i_stim.append(ia)
    g_K.append(gk)
    g_Na.append(gna)
    t += dt

# Rysowanie
fig, axs = plt.subplots(3, 1, figsize=(10, 8), sharex=True)
axs[0].plot(times, i_stim, color='gray', linewidth=2)
axs[0].set_ylabel('Prąd bodźca [µA/cm²]')

axs[1].plot(times, voltages, color='orange', linewidth=2)
axs[1].set_ylabel('Napięcie błony [mV]')

axs[2].plot(times, g_K, color='red', label='Potas (gK)', linewidth=2)
axs[2].plot(times, g_Na, color='blue', label='Sód (gNa)', linewidth=2)
axs[2].set_ylabel('Przewodność [mS/cm²]')
axs[2].set_xlabel('Czas [ms]')
axs[2].legend()

plt.tight_layout()
plt.show()