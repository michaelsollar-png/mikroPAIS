# 💡 Start of file
# 💡 basic functions_tested 01.11 with OK, all working
# 💡 Start of file
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

def remove_control_chars(text):
        # Removes all characters with ASCII < 32 except common ones like \n, \t
        return ''.join(c for c in text if ord(c) >= 32 or c in '\n\t')

class ComparisonApp:
    def __init__(self, root):
        self.root = root
        self.root.title("MIKRO_PAIS v1.0")
        self.root.configure(bg="#f4f4f4")
        self.image_dir = ""

        style = ttk.Style()
        style.theme_use('clam')  # 'clam' allows background colors

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
        self.navigation_panel = ttk.Frame(self.root)
        self.navigation_panel.pack(side="top", fill="x", pady=20)

        self.run_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.run_frame, text="📊 Results")
        self.run_box = tk.Text(self.run_frame, width=100, height=25, font=("Segoe UI", 10), bg="#f9f9f9", state="disabled")
        self.run_box.pack(fill="both", expand=True)

        self.run_box.tag_configure("OK", foreground="green", font=("Segoe UI", 10, "bold"))
        self.run_box.tag_configure("FAIL", foreground="red", font=("Segoe UI", 10, "bold"))
        self.run_box.tag_configure("ERROR", foreground="orange", font=("Segoe UI", 10, "bold"))


        files_frame = ttk.LabelFrame(self.main_frame, text="📂 Files")
        files_frame.pack(fill="x", padx=10, pady=5)

        btn_load_csv = ttk.Button(files_frame, text="📂 Load CSV + measurements", command=self.load_files, style="My.TButton")
        btn_load_csv.grid(row=0, column=0, padx=5, pady=5)
        self.add_hint(btn_load_csv, "Load CSV file and measurement data")

        btn_load_json = ttk.Button(files_frame, text="📂Load JSON", command=self.load_json, style="My.TButton")
        btn_load_json.grid(row=0, column=1, padx=5, pady=5)
        self.add_hint(btn_load_json, "Load previously saved JSON results")

        btn_load_scans = ttk.Button(files_frame, text="📂 Load scans", command=self.choose_image_directory, style="My.TButton")
        btn_load_scans.grid(row=0, column=2, padx=5)
        self.add_hint(btn_load_scans, "Select folder with scan images")

        btn_save = ttk.Button(files_frame, text="Save results", command=self.save_results, style="My.TButton")
        btn_save.grid(row=0, column=3, padx=5, pady=5)
        self.add_hint(btn_save, "Save current results to JSON")

        btn_export_fail = ttk.Button(files_frame, text="📤 Export FAIL scans", command=self.export_fail_images, style="My.TButton")
        btn_export_fail.grid(row=0, column=5, padx=5)
        self.add_hint(btn_export_fail, "Export images marked as FAIL in current measurement")

        controls_frame = ttk.LabelFrame(self.main_frame, text="🎛️ Controls")
        controls_frame.pack(fill="x", padx=10, pady=5)

        ttk.Label(controls_frame, text="Filter:").grid(row=0, column=0, padx=5)
        self.filter_type = tk.StringVar(value="ALL")
        self.filter_options = ["ALL", "OK", "FAIL", "ERROR"]
        self.filter_menu = ttk.OptionMenu(controls_frame, self.filter_type, self.filter_options[0], *self.filter_options, command=self.refresh_output)
        self.filter_menu.grid(row=0, column=1, padx=5)

        ttk.Label(controls_frame, text="Change min/max (%):").grid(row=0, column=2, padx=5)
        self.percentage = tk.StringVar(value="10")
        ttk.OptionMenu(controls_frame, self.percentage, "5", "10", "15", "20").grid(row=0, column=3, padx=5)
        ttk.Button(controls_frame, text="Change CSV.csv", command=self.edit_ec_file).grid(row=0, column=4, padx=5)

        navigation_frame = ttk.LabelFrame(self.main_frame, text="📊 Measurement")
        navigation_frame.pack(fill="x", padx=10, pady=5)

        btn_prev = ttk.Button(navigation_frame, text="⬅️ Prev", command=self.prev_measurement)
        btn_prev.pack(side=tk.LEFT, padx=5)
        self.add_hint(btn_prev, "previous pallet measurement")

        btn_next = ttk.Button(navigation_frame, text="➡️ Next", command=self.next_measurement)
        btn_next.pack(side=tk.LEFT, padx=5)
        self.add_hint(btn_next, "next pallet measurement")

        btn_run = ttk.Button(navigation_frame, text="Run", command=self.run_analysis)
        btn_run.pack(side=tk.LEFT, padx=5)
        self.add_hint(btn_run, "Start analysis of the all pallets measurements")

        btn_begin = ttk.Button(navigation_frame, text="⏮️ Begin", command=self.jump_to_start)
        btn_begin.pack(side=tk.LEFT, padx=5)
        self.add_hint(btn_begin, "to the first pallet measurement")

        btn_end = ttk.Button(navigation_frame, text="⏭️ End", command=self.jump_to_end)
        btn_end.pack(side=tk.LEFT, padx=5)
        self.add_hint(btn_end, "to the last pallet measurement")

        btn_scuts = ttk.Button(navigation_frame, text="🧭 Shortcuts", command=self.show_shortcuts)
        btn_scuts.pack(side=tk.LEFT, padx=5)
        self.add_hint(btn_scuts, "show keyboard shortcuts")

        self.only_fail = tk.BooleanVar(value=False)
        ttk.Checkbutton(navigation_frame, text="Only FAIL", variable=self.only_fail).pack(side=tk.LEFT, padx=5)

        self.measurement_label = tk.Label(navigation_frame, text="Measurement #1", font=("Segoe UI", 14, "bold"), foreground="blue")
        self.measurement_label.pack(side=tk.LEFT, padx=10)

        btn_allfail = ttk.Button(navigation_frame, text="📤 All fail export", command=self.export_all_fail_images)
        btn_allfail.pack(side=tk.LEFT, padx=5)
        self.add_hint(btn_allfail, "run all measurements and export all FAIL scans")

        # ✅ Main vertical PanedWindow
        main_paned = tk.PanedWindow(self.main_frame, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        main_paned.pack(fill="both", expand=True, padx=10, pady=10)

        # ✅ Top section: output + summary
        output_paned = tk.PanedWindow(main_paned, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        main_paned.add(output_paned)

        self.output = scrolledtext.ScrolledText(output_paned, width=80, height=20, font=("Consolas", 10))
        output_paned.add(self.output, minsize=300)

        summary_frame = ttk.LabelFrame(output_paned, text="📊 Summary", width=300, height=150)
        output_paned.add(summary_frame)

        # self.summary_box = tk.Text(summary_frame, width=40, height=20, font=("Segoe UI", 10), bg="#f9f9f9", state="disabled")
        # self.summary_box.pack(fill="both", expand=True)

        self.status_banner = tk.Label(
            summary_frame,
            text="",
            font=("Segoe UI", 20, "bold"),
            fg="white",
            bg="gray",
            anchor="center",
            relief="ridge",
            padx=10,
            pady=50
        )

        self.status_banner.pack(fill="x", pady=10)

        # ✅ Bottom section: visualization
        self.paned_viz = tk.PanedWindow(main_paned, orient=tk.VERTICAL, sashrelief=tk.RAISED)
        main_paned.add(self.paned_viz)

        viz_controls = ttk.LabelFrame(self.paned_viz, text="📦 Visualization")
        self.paned_viz.add(viz_controls)

        self.aggregate_status = tk.BooleanVar(value=True)
        ttk.Checkbutton(viz_controls, text="Agregate", variable=self.aggregate_status,
                        command=lambda: self.draw_json(self.last_json)).pack(side=tk.LEFT, padx=5)

        ttk.Label(viz_controls, text="Scale:").pack(side=tk.LEFT)
        self.scale_value = tk.DoubleVar(value=0.2)
        tk.Scale(viz_controls, from_=0.05, to=0.5, resolution=0.01, orient=tk.HORIZONTAL,
                variable=self.scale_value, command=lambda _: self.draw_json(self.last_json),
                length=200).pack(side=tk.LEFT)

        self.summary_label = ttk.Label(viz_controls, text="", foreground="blue")
        self.summary_label.pack(pady=5)

        self.canvas_json = tk.Canvas(self.paned_viz, width=1200, height=600, bg="white")
        self.paned_viz.add(self.canvas_json)

        # ✅ Bottom horizontal paned for chart and statistics
        self.paned_chart = tk.PanedWindow(self.paned_viz, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.paned_viz.add(self.paned_chart)

        # Initialize data structures
        self.tooltip = None
        self.ec_file = ""
        self.data_rows = {}
        self.measurement_index = 0
        self.results = []
        self.results_map = {}
        self.aggregation_status = {}
        self.last_json = {}
        # store EC header row (if present) so we can preserve it when writing
        self.ec_header = None

        self.create_trends_tab()
        self.preview_window = None
        self.preview_canvas = None

        # Keyboard shortcuts
        self.root.bind("<Home>", lambda e: self.jump_to_start())
        self.root.bind("<End>", lambda e: self.jump_to_end())
        self.root.bind("<Left>", lambda e: self.prev_measurement())
        self.root.bind("<Right>", lambda e: self.next_measurement())
        self.root.bind("<Control-e>", lambda e: self.export_fail_images())
        self.root.bind("<Control-R>", lambda e: self.run_analysis())
        self.root.bind("<Control-E>", lambda e: self.export_all_fail_images())


    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import matplotlib.pyplot as plt

    def choose_image_directory(self):
        path = filedialog.askdirectory(title="Choose scans directory")
        if path:
            self.image_dir = path
            messagebox.showinfo("Directory chosen", f"directory: {path}")


    def insert_output(self, text):
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
       

    def run_analysis(self):
        text = "📊 summary\n\n"

        if not self.ec_file or not self.data_rows:
            messagebox.showwarning("missing data", "Load attr.config file and measurement files first.")
            return

        try:
                with open(self.ec_file, encoding='utf-8') as f:
                    csvreader = csv.reader(f, delimiter=';')
                    # read and store header (if present)
                    header = next(csvreader, None)
                    self.ec_header = header
                    ec_rows = list(csvreader)
        except Exception as e:
            messagebox.showerror("Error", f"cannot load attr.config file {e}")
            return

        # Determine the maximum number of measurements across files
        lengths = [len(rows) for rows in self.data_rows.values()]
        measurement_count = min(lengths) if lengths else 0

        fail_counter = {}
        file_errors = {}
        ok_count = 0
        fail_count = 0

        for idx in range(measurement_count):
            measurement_status = "OK"
            for row in ec_rows:
                try:
                    layer, object_id, error_type = row[0], row[1], row[2]
                    min_val = self.parse_decimal(row[3])
                    max_val = self.parse_decimal(row[4])
                    file_id = row[5]
                    index = int(row[6]) - 1
                    rows = self.data_rows.get(file_id, [])
                    if idx >= len(rows):
                        continue
                    value = self.parse_decimal(rows[idx][index])
                    if min_val <= value <= max_val:
                        continue
                    measurement_status = "FAIL"
                    label = f"{layer} {object_id} {error_type}"
                    fail_counter[label] = fail_counter.get(label, 0) + 1
                    file_errors[file_id] = file_errors.get(file_id, 0) + 1
                except Exception:
                    measurement_status = "FAIL"
                    continue
            if measurement_status == "OK":
                ok_count += 1
            else:
                fail_count += 1


        # Output to summary box
        text = f"🔍 Done {measurement_count} all measurements\n\n"

        if fail_counter:
            top_20 = sorted(fail_counter.items(), key=lambda x: x[1], reverse=True)[:20]
            text += "TOP 20 FAIL elements:\n"
            for label, count in top_20:
                text += f"• {label}: {count}× FAIL\n"
            most_common_obj = top_20[0]
            text += f"\n🔁 Most frequent FAIL element: {most_common_obj[0]} ({most_common_obj[1]}×)\n"
        else:
            text += "No FAIL founded.\n"

        if file_errors:
            text += "\n📁 Fail count by cameras\n"
            for sid, count in sorted(file_errors.items()):
                text += f"• file {sid}: {count}× FAIL\n"
            worst_file = max(file_errors.items(), key=lambda x: x[1])
            text += f"\n📊 Most FAIL camera {worst_file[0]} ({worst_file[1]}×)\n"
        else:
            text += "\nNone of cameras contains FAIL measurements.\n"

        text += f"\n📈 Measurement summary:\n"
        text += f"✅ OK measurement: {ok_count}\n"
        text += f"❌ FAIL measurement: {fail_count}\n"

        #self.aktualizuj_souhrn(text)

        self.run_box.config(state="normal")
        #self.run_box.insert(tk.END, text + "\n")
        self.insert_output(text)

        self.run_box.config(state="disabled")

               # 📤 Output to the "Summary Analysis" tab
        self.run_box.config(state="normal")
        self.run_box.delete("1.0", "end")
        self.run_box.insert("1.0", text)
        self.run_box.config(state="disabled")


    def handle_click(self, event=None, file_id=None, first_value=None):
        import os
        from PIL import Image, ImageTk

        if not self.image_dir:
            messagebox.showwarning("Directory not found", "choose directory with scans please.")
            return

        search_code = f"C{file_id}"
        search_value = str(first_value).zfill(5)

        for filename in os.listdir(self.image_dir):
            if filename.lower().endswith(".png") and search_code in filename and search_value in filename:
                path = os.path.join(self.image_dir, filename)
                self.show_image_in_window(path)
                return

        messagebox.showwarning("Image not found", f"No existing file '{search_code}' and '{search_value}' in name.")


    def show_image_in_window(self, file_path):
        import os
        from PIL import Image, ImageTk, ImageOps, ImageEnhance

        # 🧠 If the window already exists, reuse it
        if self.preview_window and self.preview_window.winfo_exists():
            window = self.preview_window
            for widget in window.winfo_children():
                widget.destroy()
        else:
            window = tk.Toplevel(self.root)
            self.preview_window = window

        canvas = tk.Canvas(window, bg="black")
        self.preview_canvas = canvas


        window.title("Scan preview")

        # 🏷️ File name
        file_name = os.path.basename(file_path)
        ttk.Label(window, text=file_name, font=("Segoe UI", 10, "bold")).pack(pady=(5, 0))

        # 🎛️ Filter selection
        filters = {
            "Default": lambda img: img,
            "Inverted": lambda img: ImageOps.invert(img.convert("RGB")),
            "Relax": lambda img: ImageOps.colorize(img.convert("L"), black="navy", white="gold"),
            "Bright": lambda img: ImageEnhance.Brightness(img).enhance(1.5),
            "Weak": lambda img: ImageEnhance.Contrast(img.convert("RGB")).enhance(0.6),
            "Pastell": lambda img: ImageOps.colorize(img.convert("L"), black="#ffffffff", white="#5945aab0"),
        }

        selected_filter = tk.StringVar(value="Pastell")

        ttk.Label(window, text="Filter:").pack()
        combo_filtr = ttk.Combobox(window, textvariable=selected_filter, values=list(filters.keys()), state="readonly")
        combo_filtr.pack(pady=(0, 5))

        canvas.pack(fill="both", expand=True)

        # 🖼️ Load and crop the top third
        img = Image.open(file_path)
        w, h = img.size
        top_third = img.crop((0, 0, w, h // 3))

        # 🧠 Set maximum size
        max_width = 1600
        max_height = 1000
        scale_w = max_width / w
        scale_h = max_height / (h // 3)
        scale = min(scale_w, scale_h, 1.0)

        canvas.original_image = top_third
        canvas.zoom = scale

        window.geometry(f"{int(w * scale)}x{int(h // 3 * scale) + 100}")

        def update_image(*args):
            filter_func = filters.get(selected_filter.get(), lambda img: img)
            modified = filter_func(canvas.original_image)

            zoomed = modified.resize(
                (int(w * canvas.zoom), int(h // 3 * canvas.zoom)),
                Image.LANCZOS
            )
            canvas.tk_img = ImageTk.PhotoImage(zoomed)
            canvas.delete("all")
            canvas.create_image(canvas.winfo_width() // 2, canvas.winfo_height() // 2, image=canvas.tk_img, anchor="center")

        def zoom(event):
            canvas.zoom *= 1.1 if event.delta > 0 else 0.9
            canvas.zoom = max(0.2, min(canvas.zoom, 5.0))
            update_image()

        def start_drag(event):
            canvas.scan_mark(event.x, event.y)

        def drag(event):
            canvas.scan_dragto(event.x, event.y, gain=1)

        combo_filtr.bind("<<ComboboxSelected>>", update_image)
        canvas.bind("<MouseWheel>", zoom)
        canvas.bind("<ButtonPress-1>", start_drag)
        canvas.bind("<B1-Motion>", drag)

        window.update_idletasks()
        update_image()


    def create_trends_tab(self):
        self.trend_frame = ttk.Frame(self.notebook)
        self.notebook.add(self.trend_frame, text="📈 Trends")

        # Top control section
        ovladani = ttk.LabelFrame(self.trend_frame, text="Objects")
        ovladani.pack(fill="x", padx=10, pady=5)

        self.objects_listbox = tk.Listbox(ovladani, selectmode=tk.MULTIPLE, height=12, exportselection=False)
        self.objects_listbox.pack(side=tk.LEFT, padx=10, pady=5, fill="x", expand=True)

        ttk.Button(ovladani, text="Show graph", command=self.draw_trends).pack(side=tk.LEFT, padx=10)

        self.show_trim_avg = tk.BooleanVar(value=False)
        tk.Checkbutton(self.trend_frame, text="Trim average", variable=self.show_trim_avg).pack(anchor="w", pady=5)

        self.trim_ratio = tk.DoubleVar(value=0.1)
        ttk.Label(self.trend_frame, text="Trim (%)").pack(anchor="w", padx=10)
        tk.Spinbox(self.trend_frame, from_=0.0, to=0.4, increment=0.05, textvariable=self.trim_ratio, format="%.2f", width=5).pack(anchor="w", padx=10)

        self.average_type = tk.StringVar(value="trim")
        ttk.Label(self.trend_frame, text="Average type:").pack(anchor="w", padx=10)
        ttk.OptionMenu(self.trend_frame, self.average_type, "trim", "mean", "robust", "median").pack(anchor="w", padx=10)

        # Filter states
        self.filter_frame = ttk.LabelFrame(self.trend_frame, text="Filter states")
        self.filter_frame.pack(fill="x", padx=10, pady=5)

        self.filter_ok = tk.BooleanVar(value=True)
        self.filter_fail = tk.BooleanVar(value=True)
        self.filter_error = tk.BooleanVar(value=False)

        ttk.Checkbutton(self.filter_frame, text="OK", variable=self.filter_ok).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(self.filter_frame, text="FAIL", variable=self.filter_fail).pack(side=tk.LEFT, padx=5)
        ttk.Checkbutton(self.filter_frame, text="ERROR", variable=self.filter_error).pack(side=tk.LEFT, padx=5)

        # ✅ Bottom horizontal paned for chart and statistics
        self.trend_paned = tk.PanedWindow(self.trend_frame, orient=tk.HORIZONTAL, sashrelief=tk.RAISED)
        self.trend_paned.pack(fill="both", expand=True, padx=10, pady=10)

        # Panel pro graf
        self.trend_canvas_frame = tk.Frame(self.trend_paned, width=600)  
        self.trend_paned.add(self.trend_canvas_frame, minsize=400)

        # Panel pro statistiky
        self.statistics_frame = ttk.LabelFrame(self.trend_paned, text="📊 Statistics")
        self.trend_paned.add(self.statistics_frame)

        self.statistics_text = tk.Text(self.statistics_frame, wrap="word", height=20, width=40, font=("Segoe UI", 10))
        self.statistics_text.pack(fill="both", expand=True)
        self.statistics_text.config(state="disabled")
        self.statistics_text.tag_configure("bold", font=("Segoe UI", 10, "bold"))


    def robust_average(self, values, percentile=0.05):
        if not values:
            return None
        values_sorted = sorted(values)
        n = len(values_sorted)
        lower = int(n * percentile)
        upper = int(n * (1 - percentile))
        if upper <= lower:
            return None
        trimmed = values_sorted[lower:upper]
        return sum(trimmed) / len(trimmed)


    def update_objects_dropdown(self):
        try:
            with open(self.ec_file, encoding='utf-8') as f:
                reader = csv.reader(f, delimiter=';')
                # read & store header
                header = next(reader, None)
                self.ec_header = header
                objects = sorted(set(f"{r[0]}|{r[1]}|{r[2]}" for r in reader))
            self.objects_listbox.delete(0, tk.END)
            for obj in objects:
                self.objects_listbox.insert(tk.END, obj)
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


    def draw_trends(self):
        selected_indices = self.objects_listbox.curselection()
        if not selected_indices:
            messagebox.showwarning("Selection", "Choose at least one object.")
            return

        selected_objects = [self.objects_listbox.get(i) for i in selected_indices]
        fig, ax = plt.subplots(figsize=(10, 5))
        statistics_data = []

        try:
            with open(self.ec_file, encoding='utf-8') as f:
                csvreader = csv.reader(f, delimiter=';')
                # read & store header
                header = next(csvreader, None)
                self.ec_header = header
                reader = list(csvreader)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot load attribute config file: {e}")
            return

        max_measurements = max(len(r) for r in self.data_rows.values())
        visible_states = []
        if self.filter_ok.get(): visible_states.append("OK")
        if self.filter_fail.get(): visible_states.append("FAIL")
        if self.filter_error.get(): visible_states.append("ERROR")

        for object_text in selected_objects:
            try:
                layerName, objectId, errorType = object_text.split("|")
            except ValueError:
                continue

            ec_rows_for_obj = [r for r in reader if r[0] == layerName and r[1] == objectId and r[2] == errorType]
            values = []
            statuses = []
            for i in range(max_measurements):
                status = "ERROR"
                value = None
                for r in ec_rows_for_obj:
                    try:
                        file_id = r[5]
                        index = int(r[6]) - 1
                        rows = self.data_rows.get(file_id, [])
                        if i >= len(rows):
                            continue
                        try:
                            value = self.parse_decimal(rows[i][index])
                        except Exception:
                            continue
                        min_val = self.parse_decimal(r[3])
                        max_val = self.parse_decimal(r[4])
                        status = "OK" if min_val <= value <= max_val else "FAIL"
                        break
                    except Exception:
                        continue
                values.append(value)
                statuses.append(status)

            x_filtered = [i for i, s in zip(range(1, len(values)+1), statuses) if s in visible_states and values[i-1] is not None]
            y_filtered = [h for h, s in zip(values, statuses) if s in visible_states and h is not None]

            if not y_filtered:
                continue

            ax.plot(x_filtered, y_filtered, label=f"{layerName} {objectId} ({errorType})", linewidth=2)

            # Average calculation
            avg_type = self.average_type.get()
            avg = None
            if avg_type == "mean":
                avg = sum(y_filtered)/len(y_filtered)
            elif avg_type == "trim":
                avg = self.trimmed_average(y_filtered, self.trim_ratio.get())
            elif avg_type == "robust":
                avg = self.robust_average(y_filtered, percentil=0.05)
            elif avg_type == "median":
                avg = statistics.median(y_filtered)

            avg_text = f"{avg:.2f}" if avg is not None else "n/a"
            statistics_data.append(
                f"🔹 {layerName} {objectId} ({errorType}) → min: {min(y_filtered):.2f}, max: {max(y_filtered):.2f}, avg ({avg_type}): {avg_text}, count: {len(y_filtered)}"
            )

            # Moving average as a curve
            window = 5
            if avg is not None and len(y_filtered) >= window:
                y_moving_avg = np.convolve(y_filtered, np.ones(window)/window, mode='valid')
                x_moving_avg = x_filtered[window - 1:]
                ax.plot(x_moving_avg, y_moving_avg, linestyle="--", color="orange",
                        label=f"{avg_type.capitalize()} trend ({layerName} {objectId})")

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

        # ✅ Toolbar for zoom/pan/save
        toolbar = NavigationToolbar2Tk(canvas, self.trend_canvas_frame)
        toolbar.update()
        toolbar.pack(side="bottom", fill="x")

        # Display statistics with bold avg
        self.statistics_text.config(state="normal")
        self.statistics_text.delete("1.0", tk.END)

        for row in statistics_data:
            if "avg" in row:
                start_pos = self.statistics_text.index("end-1c")
                self.statistics_text.insert("end", row + "\n")
                end_pos = self.statistics_text.index("end-1c")
                match = re.search(r"avg \(\w+\): (\d+\.\d+|n/a)", row)
                if match:
                    number = match.group(1)
                    offset = row.index(number)
                    start_offset = f"{start_pos}+{offset}c"
                    end_offset = f"{start_offset}+{len(number)}c"
                    self.statistics_text.tag_add("bold", start_offset, end_offset)
            else:
                self.statistics_text.insert("end", row + "\n")

        self.statistics_text.config(state="disabled")


    def load_files(self):
        self.ec_file = filedialog.askopenfilename(
            title="Choose Atr.config file.csv",
            filetypes=[("Atr files", "*.csv")]
        )

        files = filedialog.askopenfilenames(
            title="Choose measurement files",
            filetypes=[("Data files", "*.csv *.log"), ("All files", "*.*")]
        )

        self.data_rows.clear()

        for path in files:
            name = os.path.splitext(os.path.basename(path))[0]
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
                cleaned_lines = [remove_control_chars(p) for p in parts]

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
                            cleaned_lines_alt = [remove_control_chars(p) for p in alt_parts]
                            reader_alt = csv.reader(cleaned_lines_alt, delimiter=';')
                            rows_alt = list(reader_alt)
                            if len(rows_alt) > 1:
                                print(f"Debug: aggressive split yielded {len(rows_alt)} rows for {jmeno}")
                                rows = rows_alt
                    except Exception as e:
                        print(f"Debug: aggressive split failed for {jmeno}: {e}")
                if rows:
                    self.data_rows[name] = rows
                    # Debug: report how many logical rows (measurements) were loaded for this file
                    try:
                        cnt = len(rows)
                        print(f"Loaded {cnt} records from {name}")
                    except Exception:
                        pass
                else:
                    print(f"⚠️ File {name} is empty or unreadable.")

            except Exception as e:
                messagebox.showerror("Error", f"Cannot load file {name}: {e}")

        self.measurement_index = 0
        self.run_check()


    def run_check(self):
        import re

        self.results.clear()
        self.results_map.clear()
        self.aggregation_status.clear()
        self.ec_rows = []

        try:
            with open(self.ec_file, encoding='utf-8') as f:
                csvreader = csv.reader(f, delimiter=';')
                # read and store header (if present) then iterate remaining rows
                header = next(csvreader, None)
                self.ec_header = header
                for row_index, row in enumerate(csvreader):
                    self.ec_rows.append(row)
                    try:
                        min_val = self.parse_decimal(row[3])
                        max_val = self.parse_decimal(row[4])
                        file_id = row[5]
                        index = int(row[6]) - 1
                        rows = self.data_rows.get(file_id, [])
                        if self.measurement_index >= len(rows):
                            raise IndexError("Measurement does not exist")

                        measurement_row = rows[self.measurement_index]
                        value = self.parse_decimal(measurement_row[index])
                        first_value = str(measurement_row[0]).replace(',', '.')

                        file_number = re.findall(r'\d+', file_id)
                        file_number = file_number[0] if file_number else file_id

                        label = f"{row[0]} {row[1]} {row[2]}"
                        key = (row[0], str(row[1]))

                        if min_val <= value <= max_val:
                            status = "OK"
                            icon = "✅"
                        else:
                            status = "FAIL"
                            icon = "❌"

                        text = f"[camera {file_number} | image number: {first_value}] {icon} {label}: {value} ({min_val}–{max_val})"
                        self.results.append((status, text, row_index))

                        self.results_map.setdefault(key, []).append({
                            "status": status,
                            "value": value,
                            "min": min_val,
                            "max": max_val,
                            "label": label,
                            "objectId": str(row[1]),
                            "file_id": file_id,
                            "first_value": first_value
                        })

                        prev = self.aggregation_status.get(key, "OK")
                        if prev == "OK" and status != "OK":
                            self.aggregation_status[key] = "NOK"
                        elif prev not in ["NOK", "ERROR"]:
                            self.aggregation_status[key] = status

                    except Exception as e:
                        import traceback
                        tb = traceback.format_exc()
                        label = f"{row[0]} {row[1]} {row[2]}"
                        key = (row[0], str(row[1]))
                        # Try to collect contextual info to help debugging
                        ctx = {}
                        try:
                            ctx['file_id'] = file_id
                            ctx['index_field'] = row[6] if len(row) > 6 else None
                            ctx['data_rows_for_file'] = len(self.data_rows.get(file_id, []))
                        except Exception:
                            pass
                        detail_msg = f"⚠️ {label}: {type(e).__name__}: {e} | ctx={ctx}"
                        # Append the short message to GUI results
                        self.results.append(("ERROR", detail_msg, row_index))
                        # Store more detailed trace in the map for developer inspection
                        self.results_map.setdefault(key, []).append({
                            "status": "ERROR", "value": None, "min": None, "max": None, "label": label,
                            "traceback": tb
                        })
                        self.aggregation_status[key] = "ERROR"
                        # Also print full traceback to console/log for debugging
                        print(f"Error while processing EC row {row_index} ({label}): {e}\n{tb}")

        except Exception as e:
            messagebox.showerror("Error", f"Cannot load attr.config file: {e}")
            return

        self.refresh_output()
        self.draw_json(self.last_json)
        self.update_objects_dropdown()

        # ✅ Update statuses in existing JSON
        for layer in self.last_json.get("layers", []):
            layer_name = layer.get("layerName", "")
            for group in layer.get("layerObjects", []):
                for obj in group:
                    key = (layer_name, str(obj.get("objectId")))
                    status = self.aggregation_status.get(key, "OK")
                    obj["status"] = status

                    entries = self.results_map.get(key, [])
                    for entry in entries:
                        if entry.get("value") is not None:
                            obj["file_id"] = entry.get("file_id", "")
                            obj["first_value"] = entry.get("first_value", "")
                            break

        self.draw_json(self.last_json)


    def create_objects_for_json(self):
        groups = {}
        for (layerName, objectId), entries in self.results_map.items():
            status = self.aggregation_status.get((layerName, objectId), "OK")
            for entry in entries:
                if entry.get("value") is not None:
                    obj = {
                        "objectId": objectId,
                        "width": 20,
                        "height": 100,
                        "status": status,
                        "layerName": layerName,
                        "file_id": entry.get("file_id", ""),
                        "first_value": entry.get("first_value", "")
                    }
                    groups.setdefault(objectId, []).append(obj)
                    break
        return list(groups.values())  # ✅ list of groups


    def refresh_output(self, *_):
        self.output.delete(1.0, tk.END)
        filter_val = self.filter_type.get()

        for i, result_item in enumerate(self.results):
            status, text, row_index = result_item
            if filter_val == "ALL" or filter_val == status:
                tag = f"row_{i}"
                color_pair = {"OK": ("green", "#eaffea"), "FAIL": ("red", "#ffeaea"), "ERROR": ("orange", "#fff5cc")}.get(status, ("black", "white"))
                self.output.insert(tk.END, text + "\n", tag)
                self.output.tag_config(tag, foreground=color_pair[0], background=color_pair[1])
                self.output.tag_bind(tag, "<Button-1>", lambda e, idx=row_index: self.open_min_max_editor(idx))

        self.show_summary()


    def open_min_max_editor(self, row_index):
        row = self.ec_rows[row_index]
        dialog = tk.Toplevel(self.root)
        dialog.title("Settings min/max")
        dialog.geometry("300x150")
        dialog.resizable(False, False)

        tk.Label(dialog, text="Min:").pack(pady=5)
        min_entry = tk.Entry(dialog)
        min_entry.insert(0, row[3])
        min_entry.pack()

        tk.Label(dialog, text="Max:").pack(pady=5)
        max_entry = tk.Entry(dialog)
        max_entry.insert(0, row[4])
        max_entry.pack()

        def save():
            row[3] = min_entry.get()
            row[4] = max_entry.get()
            try:
                # create a backup before overwriting EC.csv
                try:
                    shutil.copy(self.ec_file, self.ec_file + '.bak')
                except Exception:
                    # non-fatal: continue to attempt write
                    pass
                with open(self.ec_file, 'w', encoding='utf-8', newline='') as f:
                    writer = csv.writer(f, delimiter=';')
                    # preserve header if we stored it when reading
                    if getattr(self, 'ec_header', None):
                        writer.writerow(self.ec_header)
                    writer.writerows(self.ec_rows)
                dialog.destroy()
                self.run_check()
            except Exception as e:
                messagebox.showerror("Error", f"cannot save Attr file: {e}")

        tk.Button(dialog, text="Save changes", command=save).pack(pady=10)


    def show_summary(self):
        # Top label
        ok = sum(1 for v in self.results if v[0] == "OK")
        fail = sum(1 for v in self.results if v[0] == "FAIL")
        error = sum(1 for v in self.results if v[0] == "ERROR")
        total = len(self.results)

        color = "green" if ok / total >= 0.8 else "red" if fail / total >= 0.4 or error / total >= 0.3 else "orange"
        text = f"Total: {total} | ✅ OK: {ok} | ❌ FAIL: {fail} | ⚠️ ERROR: {error}"

        self.summary_label.config(text=text, foreground=color)
        self.measurement_label.config(text=f"Measurement #{self.measurement_index + 1}")

        # 🎯 Measurement status banner
        if all(v[0] == "OK" for v in self.results):
            self.status_banner.config(text="✅ OK", bg="#2ecc71", fg="white")
        elif any(v[0] == "FAIL" for v in self.results):
            self.status_banner.config(text="❌ FAIL", bg="#e74c3c", fg="white")
        elif any(v[0] == "ERROR" for v in self.results):
            self.status_banner.config(text="⚠️ ERROR", bg="#f39c12", fg="black")
        else:
            self.status_banner.config(text="—", bg="gray", fg="white")


    def save_results(self):
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
            if not path:
                return
            with open(path, "w", encoding="utf-8", newline='') as f:
                writer = csv.writer(f, delimiter=';')
                for row in self.results:
                    writer.writerow(row[:2])


    def edit_ec_file(self):
        pct = float(self.percentage.get()) / 100.0
        new_rows = []
        # Read EC and adjust min/max for selected params; backup before writing
        try:
            with open(self.ec_file, encoding='utf-8', newline='') as f:
                csvreader = csv.reader(f, delimiter=';')
                # preserve header
                header = next(csvreader, None)
                if header:
                    new_rows.append(header)
                for row in csvreader:
                    try:
                        # check the third column (index 2)
                        if row[2].strip() in ["areaL", "areaR", "area"]:
                            file_id = row[5]
                            index = int(row[6]) - 1
                            value = self.parse_decimal(self.data_rows[file_id][self.measurement_index][index])
                            row[3] = str(round(value * (1 - pct), 3)).replace('.', ',')
                            row[4] = str(round(value * (1 + pct), 3)).replace('.', ',')
                            print(f"Done: {row[0]} {row[1]} {row[2]} → min={row[3]}, max={row[4]}")
                    except Exception as e:
                        print(f"Error while editing a row {row}: {e}")
                    new_rows.append(row)
        except Exception as e:
            messagebox.showerror("Error", f"cannot load attr. config file: {e}")
            return

        try:
            try:
                shutil.copy(self.ec_file, self.ec_file + '.bak')
            except Exception:
                pass
            with open(self.ec_file, 'w', encoding='utf-8', newline='') as f:
                writer = csv.writer(f, delimiter=';')
                writer.writerows(new_rows)
        except Exception as e:
            messagebox.showerror("Error", f"Cannot be written to attr. config file: {e}")
            return
        self.run_check()
        messagebox.showinfo("Done", "The Attr. config file has been modified only for parameters 'areaL', 'areaR' a 'area'.")


    def trimmed_average(self, values, trim_ratio):
        values = [h for h in values if h is not None]
        values = sorted(values)
        n = len(values)
        k = int(n * trim_ratio)
        if n < 2 * k + 1:
            return None
        trimmed = values[k:n - k]
        return round(sum(trimmed) / len(trimmed), 3)


    def load_json(self):
            path = filedialog.askopenfilename(title="Select JSON file", filetypes=[("JSON files", "*.json")])
            if not path:
                return
            try:
                with open(path, encoding="utf-8") as f:
                    data = json.load(f)
                self.last_json = data
                self.draw_json(data)
            except Exception as e:
                messagebox.showerror("Error", f"cannot load json file: {e}")

    def draw_json(self, data):
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
                    status = self.aggregation_status.get(key, "OK") if self.aggregate_status.get() else self.results_map.get(key, [{}])[0].get("status", "OK")
                    fill_color = "#ff4d4d" if status == "NOK" else "#ffcc66" if status == "ERROR" else color

                    rect = self.canvas_json.create_rectangle(
                        x_inner, y_inner, x_inner + w, y_inner + h,
                        fill=fill_color, outline="black"
                    )

                    # ✅ Bind click on each element if it has file_id and first_value
                    sid = obj.get("file_id")
                    ph = obj.get("first_value")
                    if sid and ph:
                        self.canvas_json.tag_bind(
                            rect,
                            "<Button-1>",
                            lambda e, sid=sid, ph=ph: self.handle_click(event=e, file_id=sid, first_value=ph)
                        )

                    self.canvas_json.create_text(
                        x_inner + w / 2, y_inner + h / 2,
                        text=obj["objectId"], font=("Consolas", 8)
                    )
                    self.canvas_json.tag_bind(rect, "<Enter>", lambda e, k=key: self.show_tooltip(e, k))
                    self.canvas_json.tag_bind(rect, "<Leave>", self.hide_tooltip)

                    if vertical:
                        y_inner += h + 10
                        max_w = max(max_w, w)
                    else:
                        x_inner += w + 10
                        max_h = max(max_h, h)

                x_offset += max_w + 20 if vertical else x_inner - group_x + 20


    def show_tooltip(self, event, key):
            fail_texts = [entry for entry in self.results_map.get(key, []) if entry["status"] == "FAIL"]
            if not fail_texts:
                return

            text = f"{key[0]} {key[1]}\n"
            for entry in fail_texts:
                text += f"{entry['label']}: {entry['value']} out of range ({entry['min']}–{entry['max']})\n"

            if self.tooltip:
                self.tooltip.destroy()
            self.tooltip = tk.Toplevel(self.canvas_json)
            self.tooltip.wm_overrideredirect(True)
            self.tooltip.wm_geometry(f"+{event.x_root + 10}+{event.y_root + 10}")
            label = tk.Label(self.tooltip, text=text.strip(), background="#ffffe0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
            label.pack()

    def hide_tooltip(self, event):
            if self.tooltip:
                self.tooltip.destroy()
                self.tooltip = None

    def next_measurement(self):
        # use the minimum length across all data files so the chosen index exists in every file
        try:
            max_index = min(len(r) for r in self.data_rows.values()) - 1
        except Exception:
            max_index = len(next(iter(self.data_rows.values()), [])) - 1
        i = self.measurement_index + 1

        while i <= max_index:
            self.measurement_index = i
            self.run_check()

            # ✅ Check if there is at least one FAIL or ERROR in the measurement
            fail_detected = any(s in ("FAIL", "ERROR") for s, _, _ in self.results)

            self.measurement_label.config(text=f"Measurement #{self.measurement_index + 1}")
            self.refresh_output()

            if not self.only_fail.get() or fail_detected:
                break
            i += 1

    def jump_to_start(self):
        self.measurement_index = 0
        self.run_check()
        self.measurement_label.config(text=f"Measurement #{self.measurement_index + 1}")
        self.refresh_output()


    def jump_to_end(self):
        try:
            self.measurement_index = min(len(r) for r in self.data_rows.values()) - 1
        except Exception:
            self.measurement_index = len(next(iter(self.data_rows.values()), [])) - 1
        self.run_check()
        self.measurement_label.config(text=f"Measurement #{self.measurement_index + 1}")
        self.refresh_output()


    def export_fail_images(self):
        if not self.image_dir:
            messagebox.showwarning("Directory not set", "First, select the directory with images.")
            return

        target_dir = filedialog.askdirectory(title="Select the destination directory for export")
        if not target_dir:
            return

        exported_paths = set()
        not_found = 0

        for (layerName, objectId), entries in self.results_map.items():
            for entry in entries:
                if entry.get("status") != "FAIL":
                    continue

                file_id = entry.get("file_id", "")
                first_value = str(entry.get("first_value", "")).zfill(5)
                search_code = f"C{file_id}"

                for filename in os.listdir(self.image_dir):
                    if filename.lower().endswith(".png") and search_code in filename and first_value in filename:
                        src_path = os.path.join(self.image_dir, filename)
                        if src_path in exported_paths:
                            break  # already exported

                        dst_path = os.path.join(target_dir, filename)
                        try:
                            shutil.copy2(src_path, dst_path)
                            exported_paths.add(src_path)
                        except Exception:
                            not_found += 1
                        break
                else:
                    not_found += 1

        messagebox.showinfo("Export finished",
            f"✅ Images exported: {len(exported_paths)}\n❌ Not found: {not_found}")


    def export_all_fail_images(self):
        if not self.image_dir:
            messagebox.showwarning("Directory not set", "First, select the directory with images.")
            return

        target_dir = filedialog.askdirectory(title="Select the destination directory for exporting all FAIL images")
        if not target_dir:
            return

        max_index = len(next(iter(self.data_rows.values()), []))
        exported_paths = set()
        not_found = 0

        for i in range(max_index):
            self.measurement_index = i
            self.run_check()

            for (layerName, objectId), entries in self.results_map.items():
                for entry in entries:
                    if entry.get("status") != "FAIL":
                        continue

                    file_id = entry.get("file_id", "")
                    first_value = str(entry.get("first_value", "")).zfill(5)
                    search_code = f"C{file_id}"

                    for filename in os.listdir(self.image_dir):
                        if filename.lower().endswith(".png") and search_code in filename and first_value in filename:
                            src_path = os.path.join(self.image_dir, filename)
                            if src_path in exported_paths:
                                break  # already exported

                            dst_path = os.path.join(target_dir, filename)
                            try:
                                shutil.copy2(src_path, dst_path)
                                exported_paths.add(src_path)
                            except Exception:
                                not_found += 1
                            break
                    else:
                        not_found += 1

        messagebox.showinfo("Export finished",
            f"✅ Total images exported: {len(exported_paths)}\n❌ Not found: {not_found}")


    def prev_measurement(self):
        i = self.measurement_index - 1

        while i >= 0:
            self.measurement_index = i
            self.run_check()

            fail_detected = any(s in ("FAIL", "ERROR") for s, _, _ in self.results)

            self.measurement_label.config(text=f"Measurement #{self.measurement_index + 1}")
            self.refresh_output()

            if not self.only_fail.get() or fail_detected:
                break
            i -= 1

    def add_hint(self, widget, text):
        def show_hint(event):
            self.hint_window = tk.Toplevel(widget)
            self.hint_window.wm_overrideredirect(True)
            x = event.x_root + 10
            y = event.y_root + 10
            self.hint_window.wm_geometry(f"+{x}+{y}")
            label = tk.Label(self.hint_window, text=text, background="#ffffe0", relief="solid", borderwidth=1, font=("Segoe UI", 9))
            label.pack()

        def hide_hint(event):
            if hasattr(self, "hint_window") and self.hint_window:
                self.hint_window.destroy()
                self.hint_window = None

        widget.bind("<Enter>", show_hint)
        widget.bind("<Leave>", hide_hint)

    def show_shortcuts(self):
        window = tk.Toplevel(self.root)
        window.title("🧭 Shortcuts")
        window.geometry("400x300")
        window.resizable(False, False)

        text = (
            "📋 Shortcuts:\n\n"
            "• Home → Jump to first measurement\n"
            "• End → Jump to last measurement\n"
            "• ← / → → Prev / next measurement\n"
            "• Ctrl + E → Export FAIL images (actual)\n"
            "• Ctrl + Shift + E → Export all FAIL images\n"
            "• Ctrl + R → Run analysis\n"
        )

        tk.Label(window, text=text, justify="left", font=("Segoe UI", 10), padx=10, pady=10).pack()


if __name__ == "__main__":
    root = tk.Tk()
    app = ComparisonApp(root)
    root.mainloop()
