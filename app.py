import customtkinter as ctk
from tkinter import messagebox
import baza # Uvozimo naš modul za bazu

ctk.set_appearance_mode("Dark")
ctk.set_default_color_theme("blue")

class ExpenseApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Menadžment Troškova 2025")
        self.geometry("1100x700")
        
        # Varijable stanja
        self.selected_expense_id = None
        self.is_editing = False # Da li smo u modu izmjene? 

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.setup_ui()
        self.osvjezi_listu() # Učitaj podatke odmah

    def setup_ui(self):
        # LIJEVI PANEL (UNOS) 
        self.sidebar = ctk.CTkFrame(self, width=320, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        
        ctk.CTkLabel(self.sidebar, text="Unos Podataka", font=("Arial", 20, "bold")).pack(pady=20)

        # Naziv 
        ctk.CTkLabel(self.sidebar, text="Naziv (5-50 karaktera):").pack(anchor="w", padx=20)
        self.ent_naziv = ctk.CTkEntry(self.sidebar, placeholder_text="npr. Kupovina opreme")
        self.ent_naziv.pack(fill="x", padx=20, pady=5)

        # Iznos 
        ctk.CTkLabel(self.sidebar, text="Iznos (€):").pack(anchor="w", padx=20)
        self.ent_iznos = ctk.CTkEntry(self.sidebar, placeholder_text="0.00")
        self.ent_iznos.pack(fill="x", padx=20, pady=5)

        # Tip troška (Segmented Button kao Radio) 
        ctk.CTkLabel(self.sidebar, text="Tip troška:").pack(anchor="w", padx=20, pady=(10,0))
        self.var_tip = ctk.StringVar(value="fiksni")
        self.seg_tip = ctk.CTkSegmentedButton(self.sidebar, values=["fiksni", "rekreacija", "drugo"], variable=self.var_tip)
        self.seg_tip.pack(fill="x", padx=20, pady=5)

        # Namjena (Dropdown) 
        ctk.CTkLabel(self.sidebar, text="Namjena:").pack(anchor="w", padx=20, pady=(10,0))
        self.opt_namjena = ctk.CTkOptionMenu(self.sidebar, values=["kirija", "hrana", "odjeća", "kafa", "obuća", "trening", "drugo"])
        self.opt_namjena.pack(fill="x", padx=20, pady=5)

        # Lokacija 
        ctk.CTkLabel(self.sidebar, text="Lokacija (Grad):").pack(anchor="w", padx=20)
        self.ent_lokacija = ctk.CTkEntry(self.sidebar, placeholder_text="npr. Podgorica")
        self.ent_lokacija.pack(fill="x", padx=20, pady=(5, 20))

        # Glavno dugme (Mijenja tekst Dodaj/Potvrdi) 
        self.btn_main = ctk.CTkButton(self.sidebar, text="Dodaj trošak", command=self.glavna_akcija)
        self.btn_main.pack(fill="x", padx=20, pady=10)

        self.btn_otkazi = ctk.CTkButton(self.sidebar, text="Otkaži izmjenu", fg_color="transparent", border_width=1, command=self.reset_form)
        
        # DESNI PANEL (LISTA I DUGMAD)
        self.main_panel = ctk.CTkFrame(self, fg_color="transparent")
        self.main_panel.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.main_panel.grid_rowconfigure(0, weight=1)
        self.main_panel.grid_columnconfigure(0, weight=1)

        # Scrollable Frame kao Listbox
        self.lista_frame = ctk.CTkScrollableFrame(self.main_panel, label_text="Lista troškova")
        self.lista_frame.grid(row=0, column=0, sticky="nsew", columnspan=3)

        # Donja dugmad
        btn_frame = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        btn_frame.grid(row=1, column=0, sticky="ew", pady=10, columnspan=3)

        ctk.CTkButton(btn_frame, text="Izmijeni trošak", fg_color="#F39C12", command=self.pripremi_izmjenu).pack(side="left", padx=5, expand=True, fill="x")
        ctk.CTkButton(btn_frame, text="Obriši trošak", fg_color="#C0392B", command=self.brisi_trosak).pack(side="left", padx=5, expand=True, fill="x") # [cite: 44]
        
        # Statistička dugmad 
        stats_frame = ctk.CTkFrame(self.main_panel, fg_color="transparent")
        stats_frame.grid(row=2, column=0, sticky="ew", pady=5, columnspan=3)
        
        ctk.CTkButton(stats_frame, text="Filtriraj (Tip/Namjena)", command=self.otvori_filter_prozor).pack(side="left", padx=2, expand=True) # [cite: 47]
        ctk.CTkButton(stats_frame, text="Top 5 Lokacija", command=self.prikazi_top_5).pack(side="left", padx=2, expand=True) # [cite: 50]
        ctk.CTkButton(stats_frame, text="Česte Lokacije (>4)", command=self.prikazi_ceste_lokacije).pack(side="left", padx=2, expand=True) # [cite: 52]

    def osvjezi_listu(self, podaci=None):
        # Čišćenje liste
        for widget in self.lista_frame.winfo_children():
            widget.destroy()

        if podaci is None:
            podaci = baza.dobavi_sve_troskove()

        self.radio_var_list = ctk.IntVar(value=-1) # Za selekciju jednog reda

        for row in podaci:
            id_t, naziv, iznos, tip, namjena, grad = row
            prikaz = f"{naziv} | {iznos}€ | {tip} | {namjena} | {grad}"
            
            rb = ctk.CTkRadioButton(self.lista_frame, text=prikaz, variable=self.radio_var_list, value=id_t)
            rb.pack(anchor="w", pady=2, padx=5)

    def glavna_akcija(self):
        try:
            naziv = self.ent_naziv.get()
            iznos = self.ent_iznos.get()
            tip = self.var_tip.get()
            namjena = self.opt_namjena.get()
            lokacija = self.ent_lokacija.get()

            if not naziv or not iznos or not lokacija:
                messagebox.showerror("Greška", "Sva polja su obavezna!")
                return

            if self.is_editing:
                # Ažuriranje
                baza.azuriraj_trosak_db(self.selected_expense_id, naziv, iznos, tip, namjena, lokacija)
                messagebox.showinfo("Uspjeh", "Trošak uspješno ažuriran!")
                self.reset_form()
            else:
                # Dodavanje
                baza.dodaj_trosak_db(naziv, iznos, tip, namjena, lokacija)
                messagebox.showinfo("Uspjeh", "Trošak uspješno dodat!")
                self.reset_form() # Čisti polja
            
            self.osvjezi_listu()

        except ValueError as e:
            messagebox.showerror("Greška", str(e))
        except Exception as e:
            messagebox.showerror("Greška", f"Došlo je do greške: {e}")

    def pripremi_izmjenu(self):
        id_select = self.radio_var_list.get()
        if id_select == -1:
            messagebox.showwarning("Pažnja", "Morate odabrati trošak iz liste!")
            return

        # Nađi podatke za taj ID
        svi = baza.dobavi_sve_troskove()
        trosak = next((x for x in svi if x[0] == id_select), None)
        
        if trosak:
            self.is_editing = True
            self.selected_expense_id = id_select
            
            # Popuni polja
            self.ent_naziv.delete(0, "end")
            self.ent_naziv.insert(0, trosak[1])
            self.ent_iznos.delete(0, "end")
            self.ent_iznos.insert(0, str(trosak[2]))
            self.var_tip.set(trosak[3])
            self.opt_namjena.set(trosak[4])
            self.ent_lokacija.delete(0, "end"); self.ent_lokacija.insert(0, trosak[5])
            
            # Promijeni dugme 
            self.btn_main.configure(text="Potvrdi izmjenu", fg_color="#F39C12")
            self.btn_otkazi.pack(fill="x", padx=20, pady=5) # Pokaži dugme za otkazivanje

    def reset_form(self):
        # Vraća formu u početno stanje (Dodaj trošak) [cite: 42]
        self.is_editing = False
        self.selected_expense_id = None
        self.ent_naziv.delete(0, "end")
        self.ent_iznos.delete(0, "end")
        self.ent_lokacija.delete(0, "end")
        self.btn_main.configure(text="Dodaj trošak", fg_color=["#3B8ED0", "#1F6AA5"])
        self.btn_otkazi.pack_forget()

    def brisi_trosak(self):
        # [cite: 43, 44]
        id_select = self.radio_var_list.get()
        if id_select == -1:
            messagebox.showwarning("Pažnja", "Morate odabrati trošak!")
            return
            
        # Potvrda brisanja 
        odgovor = messagebox.askyesno("Brisanje", "Da li ste sigurni da želite obrisati trošak?")
        if odgovor:
            baza.obrisi_trosak_db(id_select)
            self.osvjezi_listu() 

    def otvori_filter_prozor(self):
        top = ctk.CTkToplevel(self)
        top.title("Izdvajanje")
        top.geometry("400x300")
        top.attributes("-topmost", True)

        ctk.CTkLabel(top, text="Filtriraj po:").pack(pady=10)
        
        v_tip = ctk.StringVar(value="fiksni")
        ctk.CTkRadioButton(top, text="Fiksni", variable=v_tip, value="fiksni").pack()
        ctk.CTkRadioButton(top, text="Rekreacija", variable=v_tip, value="rekreacija").pack()
        ctk.CTkRadioButton(top, text="Drugo", variable=v_tip, value="drugo").pack()

        ctk.CTkLabel(top, text="ILI Namjena:").pack(pady=5)
        v_namjena = ctk.CTkOptionMenu(top, values=["Sve", "kirija", "hrana", "odjeća", "kafa"])
        v_namjena.pack()

        def potvrdi():
            
            rez = baza.filtriraj_troskove(tip=v_tip.get(), namjena=v_namjena.get())
            self.osvjezi_listu(rez) # Prikaz rezultata u glavnom Listbox-u
            top.destroy()

        ctk.CTkButton(top, text="Potvrdi", command=potvrdi).pack(pady=20)

    def prikazi_top_5(self):
        
        data = baza.top_lokacije(limit=5)
        msg = "\n".join([f"{grad}: {br}" for grad, br in data])
        messagebox.showinfo("Top 5 Lokacija", msg if msg else "Nema podataka")

    def prikazi_ceste_lokacije(self):
        # Lokacije koje su se ponovile više od 4 puta, prikaži Top 3
        data = baza.top_lokacije(limit=3, min_ponavljanja=4)
        msg = "\n".join([f"{grad}: {br}" for grad, br in data])
        messagebox.showinfo("Top 3 (>4 puta)", msg if msg else "Nema lokacija sa >4 ponavljanja")

if __name__ == "__main__":
    app = ExpenseApp()
    app.mainloop()