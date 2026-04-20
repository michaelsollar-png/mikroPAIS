# 💡 Začátek souboru
# 💡 basic functions_tested 01.11 with OK, all working
# 💡 Začátek souboru
import tkinter as tk
from tkinter import filedialog, messagebox, scrolledtext, ttk
import csv
import json
import os
import re
import shutil
import matplotlib.pyplot as plt
import numpy as np
import statistics
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from functools import partial
from PIL import Image, ImageTk

def odstranit_ridici_znaky(text):
        # Odstraní všechny znaky s ASCII < 32 kromě běžných jako \n, \t
        return ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')

class PorovnaniApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MIKRO_PAIS v1.0")
        self.root.configure(bg="#f4f4f4")
        self.adresar_obrazku = ""

        style = ttk.Style()
        style.theme_use('clam')  # 'clam' umožňuje barvy pozadí

        style.configure("My.TButton",
            foreground="white",
            background="#245F61",
            font=("Segoe UI", 10, "bold"),
            padding=6,
            borderwidth=2,
            relief="raised"
        )

        style.map("My.TButton",
            foreground=[('pressed', 'yellow'), ('active', 'orange')],
            background=[('pressed', "#2F648E"), ('active', "#1B629D")],
            relief=[('pressed', 'sunken'), ('active', 'groove')]
        )

        style = ttk.Style()
        style.configure("TLabelframe", background="#f4f4f4")
        style.configure("TLabel", background="#f4f4f4", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TCheckbutton", background="#f4f4f4", font=("Segoe UI", 10))

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True)

        self.main_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.main_frame, text="🧪 Measurement")
        self.panel_navigace = ttk.Frame(self.root)
        self.panel_navigace.pack(side="top", fill="x", pady=20)

        self.run_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.run_frame, text="📊 Results")
        self.run_box = tk.Text(self.run_frame, width=100, height=25, font=("Segoe UI", 10), bg="#f9f9f9", state="disabled")
        self.run_box.pack(fill="both", expand=True)

        self.run_box.tag_configure("OK", foreground="green", font=("Segoe UI", 10, "bold"))
        self.run_box.tag_configure("FAIL", foreground="red", font=("Segoe UI", 10, "bold"))
        self.run_box.tag_configure("ERROR", foreground="orange", font=("Segoe UI", 10, "bold"))


        soubory_frame = ttk.LabelFrame(self.main_frame, text="📂 Files")
        soubory_frame.pack(fill="x", padx=10, pady=5)

        btn_load_csv = ttk.Button(soubory_frame, text="📂 Load CSV + measurements", command=self.nacist_soubory, style="My.TButton")
        btn_load_csv.grid(row=0, column=0, padx=5, pady=5)
        self.pridej_hint(btn_load_csv, "Load CSV file and measurement data")

        btn_load_json = ttk.Button(soubory_frame, text="📂Load JSON", command=self.nacist_json, style="My.TButton")
        btn_load_json.grid(row=0, column=1, padx=5, pady=5)
        self.pridej_hint(btn_load_json, "Load previously saved JSON results")

        btn_load_scans = ttk.Button(soubory_frame, text="📂 Load scans", command=self.zvol_adresar_obrazku, style="My.TButton")
        btn_load_scans.grid(row=0, column=2, padx=5)
        self.pridej_hint(btn_load_scans, "Select folder with scan images")

        btn_save = ttk.Button(soubory_frame, text="Save results", command=self.ulozit_vysledky, style="My.TButton")
        btn_save.grid(row=0, column=3, padx=5, pady=5)
        self.pridej_hint(btn_save, "Save current results to JSON")

        btn_export_fail = ttk.Button(soubory_frame, text="📤 Export FAIL scans", command=self.exportuj_fail_obrazky, style="My.TButton")
        btn_export_fail.grid(row=0, column=5, padx=5)
        self.pridej_hint(btn_export_fail, "Export images marked as FAIL in current measurement")

        ovladani_frame = ttk.LabelFrame(self.main_frame, text="🎛️ controlls")
        ovladani_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(ovladani_frame, text="Filtr:").grid(row=0, column=0, padx=5)
        self.filtr_typ = tk.StringVar(value="ALL")
        self.filtr_options = ["ALL", "OK", "FAIL", "ERROR"]
        self.filtr_menu = ttk.OptionMenu(ovladani_frame, self.filtr_typ, self.filtr_options[0], *self.filtr_options, command=self.obnovit_vystup)
        self.filtr_menu.grid(row=0, column=1, padx=5)

        ttk.Label(ovladani_frame, text="Change min/max (%):").grid(row=0, column=2, padx=5)
        self.procento = tk.StringVar(value="10")
        ttk.OptionMenu(ovladani_frame, self.procento, "5", "10", "15", "20").grid(row=0, column=3, padx=5)
        ttk.Button(ovladani_frame, text="Change CSV.csv", command=self.uprav_soubor_ec).grid(row=0, column=4, padx=5)

        navigace_frame = ttk.LabelFrame(self.main_frame, text="📊 Measurement")
        navigace_frame.pack(fill="x", padx=10, pady=5)

        btn_prev = ttk.Button(navigace_frame, text="⬅️ Prev", command=self.predchozi_mereni)
        btn_prev.pack(side=tk.LEFT, padx=5)
        self.pridej_hint(btn_prev, "previous pallet measurement")

        btn_next = ttk.Button(navigace_frame, text="➡️ Next", command=self.dalsi_mereni)
        btn_next.pack(side=tk.LEFT, padx=5)
        self.pridej_hint(btn_next, "next pallet measurement")

        btn_run = ttk.Button(navigace_frame, text="Run", command=self.spustit_analyzu)
        btn_run.pack(side=tk.LEFT, padx=5)
        self.pridej_hint(btn_run, "Start analysis of the all pallets measurements")

        btn_begin = ttk.Button(navigace_frame, text="⏮️ Begin", command=self.skok_na_zacatek)
        btn_begin.pack(side=tk.LEFT, padx=5)
        self.pridej_hint(btn_begin, "to the first pallet measurement")

        btn_end = ttk.Button(navigace_frame, text="⏭️ End", command=self.skok_na_konec)
        btn_end.pack(side=tk.LEFT, padx=5)
        self.pridej_hint(btn_end, "to the last pallet measurement")

        btn_scuts = ttk.Button(navigace_frame, text="🧭 Shortcuts", command=self.zobraz_zkratky)
        btn_scuts.pack(side=tk.LEFT, padx=5)
        self.pridej_hint(btn_scuts, "show keyboard shortcuts")

        self.pouze_fail = tk.BooleanVar(value=False)
        ttk.Checkbutton(navigace_frame, text="Only FAIL", variable=self.pouze_fail).pack(side=tk.LEFT, padx=5)

        self.mereni_label = tk.Label(navigace_frame, text="Pallet #1", font=("Segoe UI", 14, "bold"), foreground="blue")
        self.mereni_label.pack(side=tk.LEFT, padx=10)

        btn_allfail = ttk.Button(navigace_frame, text="📤 All fail export", command=self.exportuj_vsechny_fail_obrazky)
        btn_allfail.pack(side=tk.LEFT, padx=5)
        self.pridej_hint(btn_allfail, "run all measurements and export all FAIL scans")

        # ✅ Hlavní vertikální PanedWindow
        hlavni_paned = tk.PanedWindow(self.main_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        hlavni_paned.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Horní část: výstup + summary
        vystup_paned = tk.PanedWindow(hlavni_paned, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        hlavni_paned.add(vystup_paned)

        self.vystup = scrolledtext.ScrolledText(vystup_paned, width=80, height=20, font=("Consolas", 10))
        vystup_paned.add(self.vystup, minsize=300)

        souhrn_frame = ttk.LabelFrame(vystup_paned, text="📊 Summary", width=300, height=150)
        vystup_paned.add(souhrn_frame)

        # self.souhrn_box = tk.Text(souhrn_frame, width=40, height=20, font=("Segoe UI", 10), bg="#f9f9f9", state="disabled")
        # self.souhrn_box.pack(fill="both", expand=True)

        self.banner_stav = tk.Label(
            souhrn_frame,
            text="",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="gray",
            anchor="center",
            relief="ridge",
            padx=10,
            pady=50
        )

        self.banner_stav.pack(fill="x", pady=10)

        # ✅ Spodní část: vizualizace
        self.paned_vizu = tk.PanedWindow(hlavni_paned, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        hlavni_paned.add(self.paned_vizu)

        viz_controls = ttk.LabelFrame(self.paned_vizu, text="📦 Vizu")
        self.paned_vizu.add(viz_controls)

        self.agregovat_stav = tk.BooleanVar(value=True)
        ttk.Checkbutton(viz_controls, text="Agregate", variable=self.agregovat_stav,
                        command=lambda: self.vykresli_json(self.last_json)).pack(side=tk.LEFT, padx=5)

        ttk.Label(viz_controls, text="Scale:").pack(side=tk.LEFT)
        self.scale_value = tk.DoubleVar(value=0.2)
        tk.Scale(viz_controls, from_=0.05, to=0.5, resolution=0.01, orient=tk.HORIZONTAL,
                variable=self.scale_value, command=lambda _: self.vykresli_json(self.last_json),
                length=200).pack(side=tk.LEFT)

        self.souhrn_label = ttk.Label(viz_controls, text="", foreground="blue")
        self.souhrn_label.pack(pady=5)

        self.canvas_json = tk.Canvas(self.paned_vizu, width=1200, height=600, bg="white")
        self.paned_vizu.add(self.canvas_json)

        # ✅ Spodní horizontální paned pro graf a statistiky
        self.paned_graf = tk.PanedWindow(self.paned_vizu, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned_vizu.add(self.paned_graf)

        # Inicializace datových struktur
        self.tooltip = None
        self.soubor_ec = ""
        self.data_radky = {}
        self.index_mereni = 0
        self.vysledky = []
        self.vysledky_map = {}
        self.status_agregace = {}
        self.last_json = {}
        # store EC header row (if present) so we can preserve it when writing
        self.ec_header = None

        self.vytvor_trend_zalozku()
        self.okno_nahledu = None
        self.canvas_nahledu = None

        # Klávesové zkratky
        self.root.bind("<Home>", lambda e: self.skok_na_zacatek())
        self.root.bind("<End>", lambda e: self.skok_na_konec())
        self.root.bind("<Left>", lambda e: self.predchozi_mereni())
        self.root.bind("<Right>", lambda e: self.dalsi_mereni())
        self.root.bind("<Control-e>", lambda e: self.exportuj_fail_obrazky())
        self.root.bind("<Control-R>", lambda e: self.spustit_analyzu())
        self.root.bind("<Control-E>", lambda e: self.exportuj_vsechny_fail_obrazky())


    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt

    def zvol_adresar_obrazku(self):
        path = filedialog.askdirectory(title="Choose scans directory")
        if path:
            self.adresar_obrazku = path
            messagebox.showinfo("Directory choosen", f"directory: {path}")


    def vloz_vystup(self, text):
        self.run_box.config(state="normal")
        start = self.run_box.index("end-1c")
        self.run_box.insert(tk.END, text + "\n")
        end = self.run_box.index("end-1c")

        for keyword, tag in [("OK", "OK"), ("FAIL", "FAIL"), ("ERROR", "ERROR")]:
            idx = start
            while True:
                idx = self.run_box.search(keyword, idx, stopindex=end)
                if not idx:
                    break
                lastidx = f"{idx}+{len(keyword)}c"
                self.run_box.tag_add(tag, idx, lastidx)
                idx = lastidx

        self.run_box.config(state="disabled")
        self.run_box.see("end")
       

    def spustit_analyzu(self):
        text = "📊 summary\n\n"

        if not self.soubor_ec or not self.data_radky:
            messagebox.showwarning("missing data", "Load attr.config file and measurement files first.")
            return

        try:
                with open(self.soubor_ec, encoding='utf-8') as f:
                    csvreader = csv.reader(f, delimiter=';')
                    # read and store header (if present)
                    header = next(csvreader, None)
                    self.ec_header = header
                    ec_radky = list(csvreader)
        except Exception as e:
            messagebox.showerror("Error", f"cannot load attr.config file {e}")
            return

        # Zjisti maximální počet měření napříč soubory
        delky = [len(radky) for radky in self.data_radky.values()]
        pocet_mereni = min(delky) if delky else 0

        fail_counter = {}
        soubor_chyby = {}
        pocet_ok_mereni = 0
        pocet_fail_mereni = 0

        for idx in range(pocet_mereni):
            stav_mereni = "OK"
            for radek in ec_radky:
                try:
                    layer, object_id, typ = radek[0], radek[1], radek[2]
                    min_val = self.parse_decimal(radek[3])
                    max_val = self.parse_decimal(radek[4])
                    soubor_id = radek[5]
                    index = int(radek[6]) - 1
                    radky = self.data_radky.get(soubor_id, [])
                    if idx >= len(radky):
                        continue
                    hodnota = self.parse_decimal(radky[idx][index])
                    if min_val <= hodnota <= max_val:
                        continue
                    stav_mereni = "FAIL"
                    label = f"{layer} {object_id} {typ}"
                    fail_counter[label] = fail_counter.get(label, 0) + 1
                    soubor_chyby[soubor_id] = soubor_chyby.get(soubor_id, 0) + 1
                except Exception:
                    stav_mereni = "FAIL"
                    continue
            if stav_mereni == "OK":
                pocet_ok_mereni += 1
            else:
                pocet_fail_mereni += 1


        # Výstup do souhrn_box
        text = f"🔍 Done {pocet_mereni} all measurements\n\n"

        if fail_counter:
            top_20 = sorted(fail_counter.items(), key=lambda x: x[1], reverse=True)[:20]
            text += "TOP 20 FAIL elements:\n"
            for label, count in top_20:
                text += f"• {label}: {count}× FAIL\n"
            nejcastejsi_obj = top_20[0]
            text += f"\n🔁 Most frequent FAIL element: {nejcastejsi_obj[0]} ({nejcastejsi_obj[1]}×)\n"
        else:
            text += "No FAIL founded.\n"

        if soubor_chyby:
            text += "\n📁 Fail count by cameras\n"
            for sid, count in sorted(soubor_chyby.items()):
                text += f"• file {sid}: {count}× FAIL\n"
            nejhorsi_soubor = max(soubor_chyby.items(), key=lambda x: x[1])
            text += f"\n📊 Most FAIL camera {nejhorsi_soubor[0]} ({nejhorsi_soubor[1]}×)\n"
        else:
            text += "\nNone of cameras contains FAIL measurements.\n"

        text += f"\n📈 Measurement summary:\n"
        text += f"✅ OK measurement: {pocet_ok_mereni}\n"
        text += f"❌ FAIL measurement: {pocet_fail_mereni}\n"

        #self.aktualizuj_souhrn(text)

        self.run_box.config(state="normal")
        #self.run_box.insert(tk.END, text + "\n")
        self.vloz_vystup(text)

        self.run_box.config(state="disabled")

        # 📤 Výstup do záložky „Souhrnná analýza“
        self.run_box.config(state="normal")
        self.run_box.delete("1.0", "end")
        self.run_box.insert("1.0", text)
        self.run_box.config(state="disabled")


    def zpracuj_klik(self, event=None, soubor_id=None, prvni_hodnota=None):
        import os
        from PIL import Image, ImageTk

        if not self.adresar_obrazku:
            messagebox.showwarning("Directory not found", "choose directory with scans please.")
            return

        hledany_kod = f"C{soubor_id}"
        hledana_hodnota = str(prvni_hodnota).zfill(5)

        for filename in os.listdir(self.adresar_obrazku):
            if filename.lower().endswith(".png") and hledany_kod in filename and hledana_hodnota in filename:
                cesta = os.path.join(self.adresar_obrazku, filename)
                self.zobraz_obrazek_v_okne(cesta)
                return

        messagebox.showwarning("Image not found", f"No existing file '{hledany_kod}' a '{hledana_hodnota}' in name.")


    def zobraz_obrazek_v_okne(self, cesta):
        import os
        from PIL import Image, ImageTk, ImageOps, ImageEnhance

        # 🧠 Pokud okno už existuje, použij ho
        if self.okno_nahledu and self.okno_nahledu.winfo_exists():
            okno = self.okno_nahledu
            for widget in okno.winfo_children():
                widget.destroy()
        else:
            okno = tk.Toplevel(self.root)
            self.okno_nahledu = okno

        canvas = tk.Canvas(okno, bg="black")
        self.canvas_nahledu = canvas


        okno.title("Scan preview")

        # 🏷️ Název souboru
        nazev = os.path.basename(cesta)
        ttk.Label(okno, text=nazev, font=("Segoe UI", 10, "bold")).pack(pady=(5, 0))

        # 🎛️ Výběr filtru
        filtry = {
            "Default": lambda img: img,
            "Inverted": lambda img: ImageOps.invert(img.convert("RGB")),
            "Relax": lambda img: ImageOps.colorize(img.convert("L"), black="navy", white="gold"),
            "Bright": lambda img: ImageEnhance.Brightness(img).enhance(1.5),
            "Weak": lambda img: ImageEnhance.Contrast(img.convert("RGB")).enhance(0.6),
            "Pastell": lambda img: ImageOps.colorize(img.convert("L"), black="#ffffffff", white="#5945aab0"),
        }

        vybrany_filtr = tk.StringVar(value="Pastell")

        ttk.Label(okno, text="Filtr:").pack()
        combo_filtr = ttk.Combobox(okno, textvariable=vybrany_filtr, values=list(filtry.keys()), state="readonly")
        combo_filtr.pack(pady=(0, 5))

        canvas.pack(fill="both", expand=True)

        # 🖼️ Načti a ořízni horní třetinu
        img = Image.open(cesta)
        w, h = img.size
        horni_tretina = img.crop((0, 0, w, h // 3))

        # 🧠 Nastav maximální velikost
        max_width = 1600
        max_height = 1000
        scale_w = max_width / w
        scale_h = max_height / (h // 3)
        scale = min(scale_w, scale_h, 1.0)

        canvas.original_image = horni_tretina
        canvas.zoom = scale

        okno.geometry(f"{int(w * scale)}x{int(h // 3 * scale) + 100}")

        def aktualizuj_obrazek(*args):
            filtr_funkce = filtry.get(vybrany_filtr.get(), lambda img: img)
            upraveny = filtr_funkce(canvas.original_image)

            zoomed = upraveny.resize(
                (int(w * canvas.zoom), int(h // 3 * canvas.zoom)),
                Image.LANCZOS
            )
            canvas.tk_img = ImageTk.PhotoImage(zoomed)
            canvas.delete("all")
            canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=canvas.tk_img, anchor="center")

        def zoomuj(event):
            canvas.zoom *= 1.1 if event.delta > 0 else 0.9
            canvas.zoom = max(0.2, min(canvas.zoom, 5.0))
            aktualizuj_obrazek()

        def start_drag(event):
            canvas.scan_mark(event.x, event.y)

        def draguj(event):
            canvas.scan_dragto(event.x, event.y, gain=1)

        combo_filtr.bind("<<ComboboxSelected>>", aktualizuj_obrazek)
        canvas.bind("<MouseWheel>", zoomuj)
        canvas.bind("<ButtonPress-1>", start_drag)
        canvas.bind("<B1-Motion>", draguj)

        okno.update_idletasks()
        aktualizuj_obrazek()


    def vytvor_trend_zalozku(self):
        self.trend_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trend_frame, text="📈 Trends")

        # Horní ovládací část
        ovladani = ttk.LabelFrame(self.trend_frame, text="Objects")
        ovladani.pack(fill="x", padx=10, pady=5)

        self.objekty_listbox = tk.Listbox(ovladani, selectmode=tk.MULTIPLE, height=12, exportselection=False)
        self.objekty_listbox.pack(side=tk.LEFT, padx=10, pady=5, fill="x", expand=True)

        ttk.Button(ovladani, text="Show graph", command=self.vykresli_trendy).pack(side=tk.LEFT, padx=10)

        self.zobrazit_trim_avg = tk.BooleanVar(value=False)
        tk.Checkbutton(self.trend_frame, text="Trim average", variable=self.zobrazit_trim_avg).pack(anchor="w", pady=5)

        self.trim_ratio = tk.DoubleVar(value=0.1)
        ttk.Label(self.trend_frame, text="Trim (%)").pack(anchor="w", padx=10)
        tk.Spinbox(self.trend_frame, from_=0.0, to=0.4, increment=0.05, textvariable=self.trim_ratio, format="%.2f", width=5).pack(anchor="w", padx=10)

        self.typ_prumeru = tk.StringVar(value="trim")
        ttk.Label(self.trend_frame, text="Average type:").pack(anchor="w", padx=10)
        ttk.OptionMenu(self.trend_frame, self.typ_prumeru, "trim", "mean", "robust", "median").pack(anchor="w", padx=10)

        # Filtr stavů
        self.filtr_frame = ttk.LabelFrame(self.trend_frame, text="Filter states")
        self.filtr_frame.pack(fill="x", padx=10, pady=5)

        self.filtr_ok = tk.BooleanVar(value=True)
        self.filtr_fail = tk.BooleanVar(value=True)
        self.filtr_error = tk.BooleanVar(value=False)

        ttk.Checkbutton(self.filtr_frame, text="OK", variable=self.filtr_ok).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(self.filtr_frame, text="FAIL", variable=self.filtr_fail).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(self.filtr_frame, text="ERROR", variable=self.filtr_error).pack(side=tk.LEFT, padx=5)

        # ✅ Spodní horizontální PanedWindow pro graf a statistiky
        self.trend_paned = tk.PanedWindow(self.trend_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.trend_paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel pro graf
        self.trend_canvas_frame = tk.Frame(self.trend_paned, width=600)  
        self.trend_paned.add(self.trend_canvas_frame, minsize=400)

        # Panel pro statistiky
        self.statistiky_frame = ttk.LabelFrame(self.trend_paned, text="📊 Statistiky")
        self.trend_paned.add(self.statistiky_frame)

        self.statistika_text = tk.Text(self.statistiky_frame, wrap="word", height=20, width=40, font=("Segoe UI", 10))
        self.statistika_text.pack(fill="both", expand=True)
        self.statistika_text.config(state="disabled")
        self.statistika_text.tag_configure("bold", font=("Segoe UI", 10, "bold"))


    def robustni_prumer(self, hodnoty, percentil=0.05):
        if not hodnoty:
            return None
        hodnoty_sorted = sorted(hodnoty)
        n = len(hodnoty_sorted)
        dolni = int(n * percentil)
        horni = int(n * (1 - percentil))
        if horni <= dolni:
            return None
        vycistene = hodnoty_sorted[dolni:horni]
        return sum(vycistene) / len(vycistene)


    def aktualizuj_objekty_dropdown(self):
        try:
            with open(self.soubor_ec, encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                # read & store header
                header = next(reader, None)
                self.ec_header = header
                objekty = sorted(set(f"{r[0]}|{r[1]}|{r[2]}" for r in reader))
            self.objekty_listbox.delete(0, tk.END)
            for obj in objekty:
                self.objekty_listbox.insert(tk.END, obj)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load attribute config file: {e}")

    def parse_decimal(self, s):
        """Parse a number that may use a comma as decimal separator.

        Raises ValueError on empty or invalid input.
        """
        if s is None:
            raise ValueError("Empty value")
        s_str = str(s).strip()
        if s_str == "":
            raise ValueError("Empty value")
        try:
            return float(s_str.replace(',', '.'))
        except Exception as e:
            raise ValueError(f"Cannot be switch '{s_str}' to number: {e}")


    def vykresli_trendy(self):
        vybrane_indexy = self.objekty_listbox.curselection()
        if not vybrane_indexy:
            messagebox.showwarning("Selection", "Choose at least one object.")
            return

        vybrane_objekty = [self.objekty_listbox.get(i) for i in vybrane_indexy]
        fig, ax = plt.subplots(figsize=(10, 5))
        statistiky = []

        try:
            with open(self.soubor_ec, encoding='utf-8') as f:
                csvreader = csv.reader(f, delimiter=';')
                # read & store header
                header = next(csvreader, None)
                self.ec_header = header
                reader = list(csvreader)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load attribute config file: {e}")
            return

        max_mereni = max(len(r) for r in self.data_radky.values())
        zobrazene_stavy = []
        if self.filtr_ok.get(): zobrazene_stavy.append("OK")
        if self.filtr_fail.get(): zobrazene_stavy.append("FAIL")
        if self.filtr_error.get(): zobrazene_stavy.append("ERROR")

        for objekt_text in vybrane_objekty:
            try:
                layerName, objectId, errorType = objekt_text.split("|")
            except ValueError:
                continue

            radky_ec = [r for r in reader if r[0] == layerName and r[1] == objectId and r[2] == errorType]
            hodnoty = []
            stavy = []
            for i in range(max_mereni):
                stav = "ERROR"
                hodnota = None
                for r in radky_ec:
                    try:
                        soubor_id = r[5]
                        index = int(r[6]) - 1
                        radky = self.data_radky.get(soubor_id, [])
                        if i >= len(radky):
                            continue
                        try:
                            hodnota = self.parse_decimal(radky[i][index])
                        except Exception:
                            continue
                        min_val = self.parse_decimal(r[3])
                        max_val = self.parse_decimal(r[4])
                        stav = "OK" if min_val <= hodnota <= max_val else "FAIL"
                        break
                    except Exception:
                        continue
                hodnoty.append(hodnota)
                stavy.append(stav)

            x_filtered = [i for i, s in zip(range(1, len(hodnoty)+1), stavy) if s in zobrazene_stavy and hodnoty[i-1] is not None]
            y_filtered = [h for h, s in zip(hodnoty, stavy) if s in zobrazene_stavy and h is not None]

            if not y_filtered:
                continue

            ax.plot(x_filtered, y_filtered, label=f"{layerName} {objectId} ({errorType})", linewidth=2)

            # Výpočet průměru
            typ = self.typ_prumeru.get()
            avg = None
            if typ == "mean":
                avg = sum(y_filtered)/len(y_filtered)
            elif typ == "trim":
                avg = self.trimovany_prumer(y_filtered, self.trim_ratio.get())
            elif typ == "robust":
                avg = self.robustni_prumer(y_filtered, percentil=0.05)
            elif typ == "median":
                avg = statistics.median(y_filtered)

            avg_text = f"{avg:.2f}" if avg is not None else "n/a"
            statistiky.append(
                f"🔹 {layerName} {objectId} ({errorType}) → min: {min(y_filtered):.2f}, max: {max(y_filtered):.2f}, avg ({typ}): {avg_text}, count: {len(y_filtered)}"
            )

            # Klouzavý průměr jako křivka
            window = 5
            if avg is not None and len(y_filtered) >= window:
                y_moving_avg = np.convolve(y_filtered, np.ones(window)/window, mode='valid')
                x_moving_avg = x_filtered[window - 1:]
                ax.plot(x_moving_avg, y_moving_avg, linestyle="--", color="orange",
                        label=f"{typ.capitalize()} trend ({layerName} {objectId})")

        ax.set_title("Trends of selected objects")
        ax.set_xlabel("Measurement index")
        ax.set_ylabel("Value")
        ax.grid(True)
        ax.legend()

        for widget in self.trend_canvas_frame.winfo_children():
            widget.destroy()

        canvas = FigureCanvasTkAgg(fig, master=self.trend_canvas_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

        # ✅ Toolbar pro zoom/pan/save
        toolbar = NavigationToolbar2Tk(canvas, self.trend_canvas_frame)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")

        # Výpis statistik s tučným avg
        self.statistika_text.config(state="normal")
        self.statistika_text.delete("1.0", tk.END)

        for radek in statistiky:
            if "avg" in radek:
                zacatek = self.statistika_text.index("end-1c")
                self.statistika_text.insert("end", radek + "\n")
                konec = self.statistika_text.index("end-1c")
                match = re.search(r"avg \(\w+\): (\d+\.\d+|n/a)", radek)
                if match:
                    cislo = match.group(1)
                    offset = radek.index(cislo)
                    start_offset = f"{zacatek}+{offset}c"
                    end_offset = f"{start_offset}+{len(cislo)}c"
                    self.statistika_text.tag_add("bold", start_offset, end_offset)
            else:
                self.statistika_text.insert("end", radek + "\n")

        self.statistika_text.config(state="disabled")


    def nacist_soubory(self):
        self.soubor_ec = filedialog.askopenfilename(
            title="Choose Atr.config file.csv",
            filetypes=[("Atr files", "*.csv")]
        )

        soubory = filedialog.askopenfilenames(
            title="Choose measurement files",
            filetypes=[("Data files", "*.csv *.log"), ("All files", "*.*")]
        )

        self.data_radky.clear()

        for path in soubory:
            jmeno = os.path.splitext(os.path.basename(path))[0]
            try:
                with open(path, encoding='utf-8') as f:
                    content = f.read()

                # If the file uses STX (start-of-text, \x02) as a row separator
                # (some measurement exports concatenate rows without newline),
                # split accordingly. Some exports also include ETX (end-of-text, \x03)
                # as a terminator for a record; remove it if present.
                if '\n' in content:
                    parts = content.splitlines()
                else:
                    # Try splitting on common control-frame separators: STX (\x02), ETX (\x03),
                    # RS (record separator \x1E) and GS (group separator \x1D).
                    import re
                    parts = [p.strip().replace('\x03', '') for p in re.split(r'[\x02\x03\x1E\x1D]+', content) if p.strip()]
                    if not parts:
                        # If that didn't find anything, try splitting on CR only
                        if '\r' in content:
                            parts = [p.strip() for p in content.split('\r') if p.strip()]
                        else:
                            # fallback: treat whole file as single line
                            parts = [content]

                # Clean control characters for every logical line
                cleaned_lines = [odstranit_ridici_znaky(p) for p in parts]

                reader = csv.reader(cleaned_lines, delimiter=';')
                rows = list(reader)
                # If we parsed only a single logical row but the file looks large,
                # try a more aggressive split on any control character (0x01-0x1F)
                # — this helps when the file uses an uncommon framing character.
                if len(rows) <= 1 and len(content) > 200:
                    import collections
                    ctrl_counts = collections.Counter(ch for ch in content if ord(ch) < 32)
                    print(f"Debug: control char counts for {jmeno}: {dict(ctrl_counts)}")
                    try:
                        alt_parts = [p.strip().replace('\x03', '') for p in __import__('re').split(r'[\x01-\x1F]+', content) if p.strip()]
                        if len(alt_parts) > 1:
                            cleaned_lines_alt = [odstranit_ridici_znaky(p) for p in alt_parts]
                            reader_alt = csv.reader(cleaned_lines_alt, delimiter=';')
                            rows_alt = list(reader_alt)
                            if len(rows_alt) > 1:
                                print(f"Debug: aggressive split yielded {len(rows_alt)} rows for {jmeno}")
                                rows = rows_alt
                    except Exception as e:
                        print(f"Debug: aggressive split failed for {jmeno}: {e}")
                if rows:
                    self.data_radky[jmeno] = rows
                    # Debug: report how many logical rows (measurements) were loaded for this file
                    try:
                        cnt = len(rows)
                        print(f"Loaded {cnt} records from {jmeno}")
                    except Exception:
                        pass
                else:
                    print(f"⚠️ File {jmeno} is empty or unreadeble.")

            except Exception as e:
                messagebox.showerror("Error", f"Cannot load file {jmeno}: {e}")

        self.index_mereni = 0
        self.spustit_kontrolu()


    def spustit_kontrolu(self):
        import re

        self.vysledky.clear()
        self.vysledky_map.clear()
        self.status_agregace.clear()
        self.ec_radky = []

        try:
            with open(self.soubor_ec, encoding='utf-8') as f:
                csvreader = csv.reader(f, delimiter=';')
                # read and store header (if present) then iterate remaining rows
                header = next(csvreader, None)
                self.ec_header = header
                for index_radku, radek in enumerate(csvreader):
                    self.ec_radky.append(radek)
                    try:
                        min_val = self.parse_decimal(radek[3])
                        max_val = self.parse_decimal(radek[4])
                        soubor_id = radek[5]
                        index = int(radek[6]) - 1
                        radky = self.data_radky.get(soubor_id, [])
                        if self.index_mereni >= len(radky):
                            raise IndexError("Measurement does not exist")

                        radek_mereni = radky[self.index_mereni]
                        hodnota = self.parse_decimal(radek_mereni[index])
                        prvni_hodnota = str(radek_mereni[0]).replace(',', '.')

                        cislo_souboru = re.findall(r'\d+', soubor_id)
                        cislo_souboru = cislo_souboru[0] if cislo_souboru else soubor_id

                        label = f"{radek[0]} {radek[1]} {radek[2]}"
                        key = (radek[0], str(radek[1]))

                        if min_val <= hodnota <= max_val:
                            status = "OK"
                            ikona = "✅"
                        else:
                            status = "FAIL"
                            ikona = "❌"

                        text = f"[camera {cislo_souboru} | image number: {prvni_hodnota}] {ikona} {label}: {hodnota} ({min_val}–{max_val})"
                        self.vysledky.append((status, text, index_radku))

                        self.vysledky_map.setdefault(key, []).append({
                            "status": status,
                            "value": hodnota,
                            "min": min_val,
                            "max": max_val,
                            "label": label,
                            "objectId": str(radek[1]),
                            "souborId": soubor_id,
                            "prvniHodnota": prvni_hodnota
                        })

                        prev = self.status_agregace.get(key, "OK")
                        if prev == "OK" and status != "OK":
                            self.status_agregace[key] = "NOK"
                        elif prev not in ["NOK", "ERROR"]:
                            self.status_agregace[key] = status

                    except Exception as e:
                        import traceback
                        tb = traceback.format_exc()
                        label = f"{radek[0]} {radek[1]} {radek[2]}"
                        key = (radek[0], str(radek[1]))
                        # Try to collect contextual info to help debugging
                        ctx = {}
                        try:
                            ctx['soubor_id'] = soubor_id
                            ctx['index_field'] = radek[6] if len(radek) > 6 else None
                            ctx['data_rows_for_file'] = len(self.data_radky.get(soubor_id, []))
                        except Exception:
                            pass
                        detail_msg = f"⚠️ {label}: {type(e).__name__}: {e} | ctx={ctx}"
                        # Append the short message to GUI results
                        self.vysledky.append(("ERROR", detail_msg, index_radku))
                        # Store more detailed trace in the map for developer inspection
                        self.vysledky_map.setdefault(key, []).append({
                            "status": "ERROR", "value": None, "min": None, "max": None, "label": label,
                            "traceback": tb
                        })
                        self.status_agregace[key] = "ERROR"
                        # Also print full traceback to console/log for debugging
                        print(f"Error while processing EC row {index_radku} ({label}): {e}\n{tb}")

        except Exception as e:
            messagebox.showerror("Error", f"Cannot load attr.config file: {e}")
            return

        self.obnovit_vystup()
        self.vykresli_json(self.last_json)
        self.aktualizuj_objekty_dropdown()

        # ✅ Aktualizace stavů v existujícím JSON
        for layer in self.last_json.get("layers", []):
            layer_name = layer.get("layerName", "")
            for group in layer.get("layerObjects", []):
                for obj in group:
                    key = (layer_name, str(obj.get("objectId")))
                    stav = self.status_agregace.get(key, "OK")
                    obj["stav"] = stav

                    entries = self.vysledky_map.get(key, [])
                    for entry in entries:
                        if entry.get("value") is not None:
                            obj["souborId"] = entry.get("souborId", "")
                            obj["prvniHodnota"] = entry.get("prvniHodnota", "")
                            break

        self.vykresli_json(self.last_json)


    def vytvor_objekty_pro_json(self):
        skupiny = {}
        for (layerName, objectId), entries in self.vysledky_map.items():
            stav = self.status_agregace.get((layerName, objectId), "OK")
            for entry in entries:
                if entry.get("value") is not None:
                    obj = {
                        "objectId": objectId,
                        "width": 20,
                        "height": 100,
                        "stav": stav,
                        "layerName": layerName,
                        "souborId": entry.get("souborId", ""),
                        "prvniHodnota": entry.get("prvniHodnota", "")
                    }
                    skupiny.setdefault(objectId, []).append(obj)
                    break
        return list(skupiny.values())  # ✅ seznam skupin


    def obnovit_vystup(self, *_):
        self.vystup.delete(1.0, tk.END)
        typ = self.filtr_typ.get()

        for i, vysledek in enumerate(self.vysledky):
            status, text, index_radku = vysledek
            if typ == "ALL" or typ == status:
                tag = f"radek_{i}"
                barva = {"OK": ("green", "#eaffea"), "FAIL": ("red", "#ffeaea"), "ERROR": ("orange", "#fff5cc")}.get(status, ("black", "white"))
                self.vystup.insert(tk.END, text + "\n", tag)
                self.vystup.tag_config(tag, foreground=barva[0], background=barva[1])
                self.vystup.tag_bind(tag, "<Button-1>", lambda e, idx=index_radku: self.otevri_editor_min_max(idx))

        self.zobraz_souhrn()


    def otevri_editor_min_max(self, index_radku):
        radek = self.ec_radky[index_radku]
        top = tk.Toplevel(self.root)
        top.title("Settings min/max")
        top.geometry("300x150")
        top.resizable(False, False)

        tk.Label(top, text="Min:").pack(pady=5)
        min_entry = tk.Entry(top)
        min_entry.insert(0, radek[3])
        min_entry.pack()

        tk.Label(top, text="Max:").pack(pady=5)
        max_entry = tk.Entry(top)
        max_entry.insert(0, radek[4])
        max_entry.pack()

        def ulozit():
            radek[3] = min_entry.get()
            radek[4] = max_entry.get()
            try:
                # create a backup before overwriting EC.csv
                try:
                    shutil.copy(self.soubor_ec, self.soubor_ec + '.bak')
                except Exception:
                    # non-fatal: continue to attempt write
                    pass
                with open(self.soubor_ec, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f, delimiter=';')
                    # preserve header if we stored it when reading
                    if getattr(self, 'ec_header', None):
                        writer.writerow(self.ec_header)
                    writer.writerows(self.ec_radky)
                top.destroy()
                self.spustit_kontrolu()
            except Exception as e:
                messagebox.showerror("Error", f"cannot save Attr file: {e}")

        tk.Button(top, text="Save changes", command=ulozit).pack(pady=10)


    def zobraz_souhrn(self):
        # Horní štítek
        ok = sum(1 for v in self.vysledky if v[0] == "OK")
        fail = sum(1 for v in self.vysledky if v[0] == "FAIL")
        error = sum(1 for v in self.vysledky if v[0] == "ERROR")
        total = len(self.vysledky)

        barva = "green" if ok / total >= 0.8 else "red" if fail / total >= 0.4 or error / total >= 0.3 else "orange"
        text = f"Total: {total} | ✅ OK: {ok} | ❌ FAIL: {fail} | ⚠️ ERROR: {error}"

        self.souhrn_label.config(text=text, foreground=barva)
        self.mereni_label.config(text=f"Measurement #{self.index_mereni + 1}")

        # 🎯 Banner stavu měření
        if all(v[0] == "OK" for v in self.vysledky):
            self.banner_stav.config(text="✅ OK", bg="#2ecc71", fg="white")
        elif any(v[0] == "FAIL" for v in self.vysledky):
            self.banner_stav.config(text="❌ FAIL", bg="#e74c3c", fg="white")
        elif any(v[0] == "ERROR" for v in self.vysledky):
            self.banner_stav.config(text="⚠️ ERROR", bg="#f39c12", fg="black")
        else:
            self.banner_stav.config(text="—", bg="gray", fg="white")


    def ulozit_vysledky(self):
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV soubory", "*.csv")])
            if not path:
                return
            with open(path, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f, delimiter=';')
                for row in self.vysledky:
                    writer.writerow(row[:2])


    def uprav_soubor_ec(self):
        procento = float(self.procento.get()) / 100.0
        nove_radky = []
        # Read EC and adjust min/max for selected params; backup before writing
        try:
            with open(self.soubor_ec, encoding='utf-8', newline='') as f:
                csvreader = csv.reader(f, delimiter=';')
                # preserve header
                header = next(csvreader, None)
                if header:
                    nove_radky.append(header)
                for radek in csvreader:
                    try:
                        # kontrolujeme třetí sloupec (index 2)
                        if radek[2].strip() in ["areaL", "areaR", "area"]:
                            soubor_id = radek[5]
                            index = int(radek[6]) - 1
                            hodnota = self.parse_decimal(self.data_radky[soubor_id][self.index_mereni][index])
                            radek[3] = str(round(hodnota * (1 - procento), 3)).replace('.', ',')
                            radek[4] = str(round(hodnota * (1 + procento), 3)).replace('.', ',')
                            print(f"Done: {radek[0]} {radek[1]} {radek[2]} → min={radek[3]}, max={radek[4]}")
                    except Exception as e:
                        print(f"Error while editing a row {radek}: {e}")
                    nove_radky.append(radek)
        except Exception as e:
            messagebox.showerror("Error", f"cannot load attr. config file: {e}")
            return

        try:
            try:
                shutil.copy(self.soubor_ec, self.soubor_ec + '.bak')
            except Exception:
                pass
            with open(self.soubor_ec, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(nove_radky)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot be written to attr. config file: {e}")
            return
        self.spustit_kontrolu()
        messagebox.showinfo("Done", "The Attr. config file has been modified only for parameters 'areaL', 'areaR' a 'area'.")


    def trimovany_prumer(self, hodnoty, trim_ratio):
        hodnoty = [h for h in hodnoty if h is not None]
        hodnoty = sorted(hodnoty)
        n = len(hodnoty)
        k = int(n * trim_ratio)
        if n < 2 * k + 1:
            return None
        orezane = hodnoty[k:n - k]
        return round(sum(orezane) / len(orezane), 3)


    def nacist_json(self):
            path = filedialog.askopenfilename(title="Select JSON file", filetypes=[("JSON files", "*.json")])
            if not path:
                return
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                self.last_json = data
                self.vykresli_json(data)
            except Exception as e:
                messagebox.showerror("Error", f"cannot load json file: {e}")

    def vykresli_json(self, data):
        self.canvas_json.delete("all")
        scale = self.scale_value.get()
        layer_spacing = 30
        x_offset = 20

        for layer in data.get("layers", []):
            color = layer.get("color", "#cccccc")
            vertical = layer.get("vertical", False)
            layer_name = layer.get("layerName", "Layer")

            for i, group in enumerate(layer.get("layerObjects", [])):
                group_x = x_offset
                y_inner = 30
                x_inner = group_x
                max_w = 0
                max_h = 0

                self.canvas_json.create_text(group_x, 10, anchor="nw", text=f"{layer_name} {i+1}", font=("Segoe UI", 10, "bold"))

                for obj in group:
                    w = obj["width"] * scale
                    h = obj["height"] * scale
                    if vertical:
                        w, h = h, w

                    key = (layer_name, str(obj["objectId"]))
                    status = self.status_agregace.get(key, "OK") if self.agregovat_stav.get() else self.vysledky_map.get(key, [{}])[0].get("status", "OK")
                    fill_color = "#ff4d4d" if status == "NOK" else "#ffcc66" if status == "ERROR" else color

                    rect = self.canvas_json.create_rectangle(
                        x_inner, y_inner, x_inner + w, y_inner + h,
                        fill=fill_color, outline="black"
                    )

                    # ✅ Vázání kliknutí na každý prvek, pokud má souborId a prvniHodnota
                    sid = obj.get("souborId")
                    ph = obj.get("prvniHodnota")
                    if sid and ph:
                        self.canvas_json.tag_bind(
                            rect,
                            "<Button-1>",
                            lambda e, sid=sid, ph=ph: self.zpracuj_klik(event=e, soubor_id=sid, prvni_hodnota=ph)
                        )

                    self.canvas_json.create_text(
                        x_inner + w / 2, y_inner + h / 2,
                        text=obj["objectId"], font=("Consolas", 8)
                    )
                    self.canvas_json.tag_bind(rect, "<Enter>", lambda e, k=key: self.zobraz_tooltip(e, k))
                    self.canvas_json.tag_bind(rect, "<Leave>", self.skryt_tooltip)

                    if vertical:
                        y_inner += h + 10
                        max_w = max(max_w, w)
                    else:
                        x_inner += w + 10
                        max_h = max(max_h, h)

                x_offset += max_w + 20 if vertical else x_inner - group_x + 20


    def zobraz_tooltip(self, event, key):
            fail_texts = [entry for entry in self.vysledky_map.get(key, []) if entry["status"] == "FAIL"]
            if not fail_texts:
                return

            text = f"{key[0]} {key[1]}\n"
            for entry in fail_texts:
                text += f"{entry['label']}: {entry['value']} MIMO rozsah ({entry['min']}–{entry['max']})\n"

            if self.tooltip:
                self.tooltip.destroy()
            self.tooltip = tk.Toplevel(self.canvas_json)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(self.tooltip, text=text.strip(), background="#ffffe0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
            label.pack()

    def skryt_tooltip(self, event):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

    def dalsi_mereni(self):
        # use the minimum length across all data files so the chosen index exists in every file
        try:
            max_index = min(len(r) for r in self.data_radky.values()) - 1
        except Exception:
            max_index = len(next(iter(self.data_radky.values()), [])) - 1
        i = self.index_mereni + 1

        while i <= max_index:
            self.index_mereni = i
            self.spustit_kontrolu()

            # ✅ Zjisti, zda je v měření alespoň jeden FAIL nebo ERROR
            fail_detected = any(status in ("FAIL", "ERROR") for status, _, _ in self.vysledky)

            self.mereni_label.config(text=f"Měření #{self.index_mereni + 1}")
            self.obnovit_vystup()

            if not self.pouze_fail.get() or fail_detected:
                break
            i += 1

    def skok_na_zacatek(self):
        self.index_mereni = 0
        self.spustit_kontrolu()
        self.mereni_label.config(text=f"Měření #{self.index_mereni + 1}")
        self.obnovit_vystup()


    def skok_na_konec(self):
        try:
            self.index_mereni = min(len(r) for r in self.data_radky.values()) - 1
        except Exception:
            self.index_mereni = len(next(iter(self.data_radky.values()), [])) - 1
        self.spustit_kontrolu()
        self.mereni_label.config(text=f"Měření #{self.index_mereni + 1}")
        self.obnovit_vystup()


    def exportuj_fail_obrazky(self):
        if not self.adresar_obrazku:
            messagebox.showwarning("Directory not set", "First, select the directory with images.")
            return

        cilovy_adresar = filedialog.askdirectory(title="Select the destination directory for export")
        if not cilovy_adresar:
            return

        exportovane_cesty = set()
        nenalezeno = 0

        for (layerName, objectId), entries in self.vysledky_map.items():
            for entry in entries:
                if entry.get("status") != "FAIL":
                    continue

                soubor_id = entry.get("souborId", "")
                prvni_hodnota = str(entry.get("prvniHodnota", "")).zfill(5)
                hledany_kod = f"C{soubor_id}"

                for filename in os.listdir(self.adresar_obrazku):
                    if filename.lower().endswith(".png") and hledany_kod in filename and prvni_hodnota in filename:
                        src_path = os.path.join(self.adresar_obrazku, filename)
                        if src_path in exportovane_cesty:
                            break  # už exportováno

                        dst_path = os.path.join(cilovy_adresar, filename)
                        try:
                            shutil.copy2(src_path, dst_path)
                            exportovane_cesty.add(src_path)
                        except Exception:
                            nenalezeno += 1
                        break
                else:
                    nenalezeno += 1

        messagebox.showinfo("Export finished",
            f"✅ Images exported: {len(exportovane_cesty)}\n❌ Not found: {nenalezeno}")


    def exportuj_vsechny_fail_obrazky(self):
        if not self.adresar_obrazku:
            messagebox.showwarning("Directory not set", "First, select the directory with images.")
            return

        cilovy_adresar = filedialog.askdirectory(title="Select the destination directory for exporting all FAIL images")
        if not cilovy_adresar:
            return

        max_index = len(next(iter(self.data_radky.values()), []))
        exportovane_cesty = set()
        nenalezeno = 0

        for i in range(max_index):
            self.index_mereni = i
            self.spustit_kontrolu()

            for (layerName, objectId), entries in self.vysledky_map.items():
                for entry in entries:
                    if entry.get("status") != "FAIL":
                        continue

                    soubor_id = entry.get("souborId", "")
                    prvni_hodnota = str(entry.get("prvniHodnota", "")).zfill(5)
                    hledany_kod = f"C{soubor_id}"

                    for filename in os.listdir(self.adresar_obrazku):
                        if filename.lower().endswith(".png") and hledany_kod in filename and prvni_hodnota in filename:
                            src_path = os.path.join(self.adresar_obrazku, filename)
                            if src_path in exportovane_cesty:
                                break  # už exportováno

                            dst_path = os.path.join(cilovy_adresar, filename)
                            try:
                                shutil.copy2(src_path, dst_path)
                                exportovane_cesty.add(src_path)
                            except Exception:
                                nenalezeno += 1
                            break
                    else:
                        nenalezeno += 1

        messagebox.showinfo("Export finished",
            f"✅ Total images exported: {len(exportovane_cesty)}\n❌ Not found: {nenalezeno}")


    def predchozi_mereni(self):
        i = self.index_mereni - 1

        while i >= 0:
            self.index_mereni = i
            self.spustit_kontrolu()

            fail_detected = any(status in ("FAIL", "ERROR") for status, _, _ in self.vysledky)

            self.mereni_label.config(text=f"Measurement #{self.index_mereni + 1}")
            self.obnovit_vystup()

            if not self.pouze_fail.get() or fail_detected:
                break
            i -= 1

    def pridej_hint(self, widget, text):
        def zobraz_hint(event):
            self.hint_okno = tk.Toplevel(widget)
            self.hint_okno.wm_overrideredirect(True)
            x = event.x_root + 10
            y = event.y_root + 10
            self.hint_okno.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.hint_okno, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
            label.pack()

        def skryt_hint(event):
            if hasattr(self, "hint_okno") and self.hint_okno:
                self.hint_okno.destroy()
                self.hint_okno = None

        widget.bind("<Enter>", zobraz_hint)
        widget.bind("<Leave>", skryt_hint)

    def zobraz_zkratky(self):
        okno = tk.Toplevel(self.root)
        okno.title("🧭 Shortcuts")
        okno.geometry("400x300")
        okno.resizable(False, False)

        text = (
            "📋 Shortcuts:\n\n"
            "• Home → Jump to first measurement\n"
            "• End → Jump to last measurement\n"
            "• ← / → → Prev / next measurement\n"
            "• Ctrl + E → Export FAIL images (actual)\n"
            "• Ctrl + Shift + E → Export all FAIL images\n"
            "• Ctrl + R → Run analysis\n"
        )

        tk.Label(okno, text=text, justify="left", font=("Segoe UI", 10), padx=10, pady=10).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = PorovnaniApp(root)
    root.mainloop()
