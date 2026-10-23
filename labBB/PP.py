import tkinter as tk
from tkinter import ttk
import math

class LaboratoriumPrawPrzeplywu:
    def __init__(self, root):
        self.root = root
        self.root.title("Prawa Przepływu - Symulator Laboratoryjny")
        self.root.geometry("850x650")
        self.root.configure(bg="#f0f0f0")

        # Stała długość rury (dobrana tak, by opory przypominały te ze zrzutu ekranu)
        self.L = 0.685 
        # Ciśnienie na wylocie (referencyjne)
        self.P_out = 900.0 

        # --- ZMIENNE KONTROLNE ---
        self.r1_var = tk.DoubleVar(value=10.0)
        self.r2_var = tk.DoubleVar(value=10.0)
        self.sync_var = tk.BooleanVar(value=True)
        
        self.Q_var = tk.DoubleVar(value=5.0)     # dm^3/min
        self.eta_var = tk.DoubleVar(value=3.0)   # mPa*s
        self.rho_var = tk.DoubleVar(value=1060.0) # kg/m^3

        # Podpięcie zdarzeń - zmiana suwaka automatycznie przelicza fizykę (POPRAWIONE trace_add)
        self.r1_var.trace_add("write", self.aktualizuj_symulacje)
        self.r2_var.trace_add("write", self.aktualizuj_symulacje)
        self.Q_var.trace_add("write", self.aktualizuj_symulacje)
        self.eta_var.trace_add("write", self.aktualizuj_symulacje)
        self.rho_var.trace_add("write", self.aktualizuj_symulacje)
        self.sync_var.trace_add("write", self.synchronizuj_promienie)

        self.zbuduj_interfejs()
        self.aktualizuj_symulacje()

    def zbuduj_interfejs(self):
        # --- EKRAN WIZUALIZACJI (GÓRA) ---
        wiz_frame = tk.Frame(self.root, bg="white", bd=2, relief="sunken")
        wiz_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.canvas = tk.Canvas(wiz_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

        # --- PANEL STEROWANIA (DÓŁ) ---
        ctrl_frame = ttk.LabelFrame(self.root, text="Panel Sterowania Parametrami", padding=15)
        ctrl_frame.pack(fill="x", padx=20, pady=(0, 20))

        # Lewa kolumna: Promienie
        frame_r = ttk.Frame(ctrl_frame)
        frame_r.grid(row=0, column=0, padx=20, sticky="n")
        
        ttk.Label(frame_r, text="PROMIEŃ 1 [mm]:").pack(anchor="w")
        self.slider_r1 = ttk.Scale(frame_r, from_=5.0, to=20.0, variable=self.r1_var, orient="horizontal", length=150)
        self.slider_r1.pack()
        self.lbl_r1 = ttk.Label(frame_r, text="10.0")
        self.lbl_r1.pack()

        self.cb_sync = ttk.Checkbutton(frame_r, text="synchronicznie", variable=self.sync_var)
        self.cb_sync.pack(pady=5)

        ttk.Label(frame_r, text="PROMIEŃ 2 [mm]:").pack(anchor="w")
        self.slider_r2 = ttk.Scale(frame_r, from_=5.0, to=20.0, variable=self.r2_var, orient="horizontal", length=150)
        self.slider_r2.pack()
        self.lbl_r2 = ttk.Label(frame_r, text="10.0")
        self.lbl_r2.pack()

        # Prawa kolumna: Właściwości płynu
        frame_p = ttk.Frame(ctrl_frame)
        frame_p.grid(row=0, column=1, padx=40, sticky="n")

        ttk.Label(frame_p, text="STRUMIEŃ OBJĘTOŚCI [dm³/min]:").pack(anchor="w")
        ttk.Scale(frame_p, from_=1.0, to=10.0, variable=self.Q_var, orient="horizontal", length=200).pack()
        self.lbl_q = ttk.Label(frame_p, text="5.0")
        self.lbl_q.pack(pady=(0, 10))

        ttk.Label(frame_p, text="LEPKOŚĆ [mPa*s]:").pack(anchor="w")
        ttk.Scale(frame_p, from_=1.0, to=10.0, variable=self.eta_var, orient="horizontal", length=200).pack()
        self.lbl_eta = ttk.Label(frame_p, text="3.0")
        self.lbl_eta.pack(pady=(0, 10))

        ttk.Label(frame_p, text="GĘSTOŚĆ [kg/m³]:").pack(anchor="w")
        ttk.Entry(frame_p, textvariable=self.rho_var, width=10, justify="center").pack()

    def synchronizuj_promienie(self, *args):
        if self.sync_var.get():
            self.r2_var.set(self.r1_var.get())
            self.slider_r2.state(['disabled'])
        else:
            self.slider_r2.state(['!disabled'])

    def aktualizuj_symulacje(self, *args):
        # Aktualizacja etykiet nad suwakami
        if self.sync_var.get() and self.r1_var.get() != self.r2_var.get():
            self.r2_var.set(self.r1_var.get())

        self.lbl_r1.config(text=f"{self.r1_var.get():.1f}")
        self.lbl_r2.config(text=f"{self.r2_var.get():.1f}")
        self.lbl_q.config(text=f"{self.Q_var.get():.1f}")
        self.lbl_eta.config(text=f"{self.eta_var.get():.1f}")

        # Pobranie wartości i konwersja na jednostki SI
        r1_m = self.r1_var.get() / 1000.0
        r2_m = self.r2_var.get() / 1000.0
        Q_m3s = self.Q_var.get() / 60000.0       # dm^3/min na m^3/s
        eta_Pas = self.eta_var.get() / 1000.0    # mPa*s na Pa*s
        
        try:
            rho = self.rho_var.get()
        except tk.TclError:
            rho = 1060.0

        # OBLICZENIA FIZYCZNE DLA SEKCJI 1 (Początek naczynia)
        v1 = Q_m3s / (math.pi * (r1_m ** 2))
        Pd1 = 0.5 * rho * (v1 ** 2)
        NR1 = (rho * v1 * (2 * r1_m)) / eta_Pas
        RN1 = (8 * eta_Pas * (self.L / 2)) / (math.pi * (r1_m ** 4))

        # OBLICZENIA FIZYCZNE DLA SEKCJI 2 (Koniec naczynia)
        v2 = Q_m3s / (math.pi * (r2_m ** 2))
        Pd2 = 0.5 * rho * (v2 ** 2)
        RN2 = (8 * eta_Pas * (self.L / 2)) / (math.pi * (r2_m ** 4))

        # Spadki ciśnień
        Ps2 = self.P_out
        Ps1 = Ps2 + (RN1 + RN2) * Q_m3s
        
        P_calk_1 = Ps1 + Pd1
        P_calk_2 = Ps2 + Pd2

        # RYSOWANIE WIZUALIZACJI
        self.canvas.delete("all")
        w = self.canvas.winfo_width()
        h = self.canvas.winfo_height()
        if w < 10: w = 800
        if h < 10: h = 300

        cy = h / 2
        
        # Grubości rur proporcjonalne do promienia
        grubosc1 = self.r1_var.get() * 3
        grubosc2 = self.r2_var.get() * 3

        # Rysowanie naczynia
        self.canvas.create_rectangle(50, cy - grubosc1, w/2, cy + grubosc1, fill="#87CEEB", outline="black", width=2)
        self.canvas.create_rectangle(w/2, cy - grubosc2, w-50, cy + grubosc2, fill="#87CEEB", outline="black", width=2)

        # Wyświetlanie tekstów (Czujniki)
        self.rysuj_czujnik(w*0.25, cy - grubosc1 - 60, f"Ps1 (statyczne): {Ps1:.1f} Pa", f"p1 (całkowite): {P_calk_1:.1f} Pa")
        self.rysuj_czujnik(w*0.75, cy - grubosc2 - 60, f"Ps2 (statyczne): {Ps2:.1f} Pa", f"p2 (całkowite): {P_calk_2:.1f} Pa")

        # Wyświetlanie Liczby Reynoldsa na dole
        self.canvas.create_text(w/2, cy + max(grubosc1, grubosc2) + 40, 
                                text=f"Liczba Reynoldsa (NR): {int(NR1)}", 
                                font=("Arial", 14, "bold"), fill="darkred")

    def rysuj_czujnik(self, x, y, txt1, txt2):
        self.canvas.create_line(x, y+40, x, y+80, width=3, fill="gray")
        self.canvas.create_rectangle(x-90, y-20, x+90, y+40, fill="#333", outline="black")
        self.canvas.create_text(x, y, text=txt1, fill="#0f0", font=("Consolas", 10, "bold"))
        self.canvas.create_text(x, y+20, text=txt2, fill="#0ff", font=("Consolas", 10, "bold"))

if __name__ == "__main__":
    root = tk.Tk()
    style = ttk.Style()
    if 'clam' in style.theme_names():
        style.theme_use('clam')
    app = LaboratoriumPrawPrzeplywu(root)
    
    # Opóźnienie pierwszego rysowania, żeby canvas znał swoje rozmiary
    root.after(100, app.aktualizuj_symulacje)
    root.mainloop()
