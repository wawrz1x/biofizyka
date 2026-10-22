"""
test_hh_model.py
================
Zestaw testów jednostkowych i walidacji biofizycznej dla hh_model.py (Wersja 2.1).
Weryfikuje stabilność spoczynkową, zachowanie podprogowe/ponadprogowe,
odporność na osobliwości numeryczne oraz scenariusze dydaktyczne.
"""

import unittest
import numpy as np
import hh_model


class TestHodgkinHuxleyModel(unittest.TestCase):

    def test_kinetic_singularities(self):
        """Test odporności na dzielenie przez zero w punktach osobliwych."""
        # Punkt V = V_M0 (-55.0 mV) w alpha_m
        val_m_sing = hh_model.alpha_m(hh_model.V_M0)
        self.assertFalse(np.isnan(val_m_sing))
        self.assertFalse(np.isinf(val_m_sing))
        self.assertAlmostEqual(val_m_sing, 1.0, places=4)

        # Punkt V = V_N0 (-65.0 mV) w alpha_n
        val_n_sing = hh_model.alpha_n(hh_model.V_N0)
        self.assertFalse(np.isnan(val_n_sing))
        self.assertFalse(np.isinf(val_n_sing))
        self.assertAlmostEqual(val_n_sing, 0.1, places=4)

    def test_resting_equilibrium_stability(self):
        """Weryfikacja idealnej stabilności stanu spoczynkowego U = -90.0 mV bez bodźca."""
        times = np.linspace(0, 35, 3500)
        stim = np.zeros_like(times)
        res = hh_model.simulate_hh(stim, times)

        self.assertFalse(res.has_spike)
        self.assertAlmostEqual(res.v_rest, -90.0, places=4)
        self.assertAlmostEqual(res.v_min, -90.0, places=4)
        self.assertAlmostEqual(res.v_max, -90.0, places=4)
        # Napięcie w każdym punkcie czasowym nie może odbiegać od -90.0 mV o więcej niż 1e-4 mV
        np.testing.assert_allclose(res.V, -90.0, atol=1e-4)

    def test_subthreshold_and_suprathreshold_responses(self):
        """Weryfikacja odpowiedzi podprogowej (biernej) oraz ponadprogowej (potencjał czynnościowy)."""
        times = np.linspace(0, 30, 3000)

        # 1. Bodziec podprogowy: J = 5.0 µA/cm², Δt = 1.0 ms
        stim_sub = hh_model.generate_single_pulse(times, 5.0, 1.0, start=2.0)
        res_sub = hh_model.simulate_hh(stim_sub, times)
        self.assertFalse(res_sub.has_spike)
        self.assertLess(res_sub.v_max, -70.0)  # Nie przekracza progu
        self.assertAlmostEqual(res_sub.V[-1], -90.0, delta=0.5)  # Wraca do spoczynku

        # 2. Bodziec ponadprogowy: J = 20.0 µA/cm², Δt = 1.0 ms
        stim_sup = hh_model.generate_single_pulse(times, 20.0, 1.0, start=2.0)
        res_sup = hh_model.simulate_hh(stim_sup, times)
        self.assertTrue(res_sup.has_spike)
        self.assertGreater(res_sup.v_max, 30.0)  # Szczyt > +30 mV (przepolaryzowanie)
        self.assertLess(res_sup.v_min, -96.0)   # Następcza hiperpolaryzacja zbliża się do E_K = -97 mV

    def test_hyperpolarization_negative_current(self):
        """Weryfikacja odpowiedzi na prąd ujemny J < 0 (Pkt 6 ze str. 181 podręcznika)."""
        times = np.linspace(0, 30, 3000)
        stim_hyp = hh_model.generate_single_pulse(times, -15.0, 5.0, start=2.0)
        res_hyp = hh_model.simulate_hh(stim_hyp, times)

        self.assertFalse(res_hyp.has_spike)
        self.assertLess(res_hyp.v_min, -110.0)  # Błona ulega silnej hiperpolaryzacji
        # Odzyskanie gotowości sodowej (bramka h rośnie z 0.37 w spoczynku do > 0.85)
        self.assertGreater(np.max(res_hyp.h), 0.80)
        # Po ustaniu bodźca napięcie wraca do spoczynku
        self.assertAlmostEqual(res_hyp.V[-1], -90.0, delta=1.0)

    def test_dual_pulses_overlapping_and_zero_interval(self):
        """Test generatora dwóch impulsów z zerowym odstępem i sumowaniem prądów."""
        times = np.linspace(0, 20, 2001)

        # Zerowy odstęp
        stim_zero = hh_model.generate_dual_pulses(times, 10.0, 1.0, 15.0, 1.0, interval=0.0, start1=2.0)
        # Sprawdzamy ciągłość od t=2.0 do t=4.0
        idx_2_5 = np.argmin(np.abs(times - 2.5))
        idx_3_5 = np.argmin(np.abs(times - 3.5))
        self.assertAlmostEqual(stim_zero[idx_2_5], 10.0)
        self.assertAlmostEqual(stim_zero[idx_3_5], 15.0)

        # Ujemny odstęp (nakładanie się)
        stim_ovlp = hh_model.generate_dual_pulses(times, 10.0, 2.0, 10.0, 2.0, interval=-1.0, start1=2.0)
        # W obszarze nakładania (t od 3.0 do 4.0) prąd powinien wynosić 10 + 10 = 20
        self.assertAlmostEqual(stim_ovlp[idx_3_5], 20.0)

    def test_temporal_summation_three_pulses(self):
        """Weryfikacja sumowania w czasie serii 3 bodźców (Ryc. 6 z podręcznika)."""
        times = np.linspace(0, 35, 3500)

        # Pojedynczy impuls 11.5 µA/cm² przez 0.8 ms jest podprogowy
        stim1 = hh_model.generate_single_pulse(times, 11.5, 0.8, start=2.0)
        res1 = hh_model.simulate_hh(stim1, times)
        self.assertFalse(res1.has_spike)

        # Seria 3 impulsów o małym odstępie (1.0 ms) wyzwala potencjał czynnościowy!
        stim3_short = hh_model.generate_pulse_train(times, 11.5, 0.8, interval=1.0, n_pulses=3, start=2.0)
        res3_short = hh_model.simulate_hh(stim3_short, times)
        self.assertTrue(res3_short.has_spike)

        # Seria 3 impulsów o dużym odstępie (5.0 ms) NIE wyzwala potencjału czynnościowego
        stim3_long = hh_model.generate_pulse_train(times, 11.5, 0.8, interval=5.0, n_pulses=3, start=2.0)
        res3_long = hh_model.simulate_hh(stim3_long, times)
        self.assertFalse(res3_long.has_spike)

    def test_timestep_convergence(self):
        """Weryfikacja zbieżności numerycznej dla dt = 0.02, 0.01, 0.005 ms."""
        peaks = []
        for dt_val in [0.02, 0.01, 0.005]:
            times = np.linspace(0, 20, int(20 / dt_val))
            stim = hh_model.generate_single_pulse(times, 15.0, 1.0, start=2.0)
            res = hh_model.simulate_hh(stim, times)
            peaks.append(res.v_max)

        # Różnica szczytu między dt=0.01 a dt=0.005 nie przekracza 1.0 mV
        self.assertLess(abs(peaks[1] - peaks[2]), 1.0)


if __name__ == "__main__":
    unittest.main()
