<<<<<<< Updated upstream
import tkinter as tk
from tkinter import messagebox, ttk
from datetime import datetime
import os
import sys
import json

# ---------------------------
# Dynamic Config Path (.exe & .py)
# ---------------------------

if getattr(sys, 'frozen', False):
    APP_DIR = os.path.dirname(sys.executable)
else:
    APP_DIR = os.path.dirname(os.path.abspath(__file__))

CONFIG_FILE = os.path.join(APP_DIR, "app_config.json")

# Default dynamic configuration structure
DEFAULT_CONFIG = {
    "categories": {
        "Zenput Options": [
            "Bill of Lading [1]", "Bill of Lading [2]", "Bill of Lading [3]", 
            "Veeder Root", "Payout", "Coupon", "Lottery", "Titan Series", 
            "Change Order", "QSR Safe Drops"
        ],
        "CNG Options": [
            "Department Sales", "Fuel Tier", "EMR", "NCR", "NPR", 
            "Loyalty", "Pop Discount", "Drive Off", "MOP", 
            "Adjusted Fuel Deposit", "KKC"
        ]
    },
    "multi_popups": {
        "Titan Series": ["Safe EOD Report", "Safe Summary Report"],
        "NCR": ["Fleetwide", "Fuelman", "PumpPASS", "Exxon Mobil G", "Shell"],
        "NPR": ["E85", "Diesel", "Racing Fuel", "Kerosene"],
        "Loyalty": ["600", "888", "800", "211"]
    },
    "entry_popups": {
        "Bill of Lading [1]": "BOL#",
        "Bill of Lading [2]": "BOL#",
        "Bill of Lading [3]": "BOL#"
    }
}

# Dynamic selection state
multi_selections = {}
entry_values = {}

# ---------------------------
# Config Storage & Migration
# ---------------------------

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                data = json.load(f)
                
            if "categories" not in data:
                categories = {}
                if "zenput_options" in data:
                    categories["Zenput Options"] = data["zenput_options"]
                if "cng_options" in data:
                    categories["CNG Options"] = data["cng_options"]
                data["categories"] = categories

            if "multi_popups" not in data:
                data["multi_popups"] = DEFAULT_CONFIG["multi_popups"].copy()

            if "entry_popups" not in data:
                data["entry_popups"] = DEFAULT_CONFIG["entry_popups"].copy()

            save_config(data)
            return data
        except Exception:
            return DEFAULT_CONFIG.copy()
    else:
        save_config(DEFAULT_CONFIG)
        return DEFAULT_CONFIG.copy()

def save_config(config_data):
    try:
        with open(CONFIG_FILE, "w") as f:
            json.dump(config_data, f, indent=4)
    except Exception as e:
        messagebox.showerror("Error", f"Failed to save configuration: {e}")

# ---------------------------
# Icon Path & Focus Helpers
# ---------------------------

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def restore_focus(prev_widget):
    try:
        if prev_widget and prev_widget.winfo_exists():
            prev_widget.focus_set()
            return
    except Exception:
        pass
    if all_checkbuttons:
        all_checkbuttons[0].focus_set()

# ---------------------------
# Core Logic Functions
# ---------------------------

def update_result():
    selected_items = []
    timestamp_str = "" 
    entry_popups = config.get("entry_popups", {})
    
    for name, var in all_options.items():
        if var.get():
            if name == "Timestamp":
                now = datetime.now().strftime("%m/%d/%Y")
                timestamp_str = f" - {user_name}(DE) {now}"
            elif name in entry_popups:
                val = entry_values.get(name, tk.StringVar()).get().strip()
                if val:
                    prefix = entry_popups[name]
                    if prefix:
                        selected_items.append(f"{prefix}{val}")
                    else:
                        selected_items.append(f"{name}#{val}")
            else:
                sel_list = multi_selections.get(name, [])
                if sel_list:
                    selected_items.append(f"{name}(" + ", ".join(sel_list) + ")")
                else:
                    selected_items.append(name)

    result.config(state="normal")
    result.delete("1.0", tk.END)
    
    if selected_items or timestamp_str:
        items_joined = ", ".join(selected_items)
        final_text = f"Data Entered: {items_joined}{timestamp_str}"
        result.insert(tk.END, final_text.strip())
        
    result.config(state="disabled")

def copy_to_clipboard(event=None):
    content = result.get("1.0", tk.END).strip()
    if content:
        if not all_options.get("Timestamp", tk.BooleanVar()).get():
            content = content.replace("Data Entered: ", "")
        
        root.clipboard_clear()
        root.clipboard_append(content)
        root.update()
    return "break"

def clear_all(event=None):
    for name, var in all_options.items():
        var.set(False)
    for var in entry_values.values():
        var.set("")
    for key in multi_selections:
        multi_selections[key].clear()
    update_result()
    if all_checkbuttons:
        all_checkbuttons[0].focus_set()
    return "break"

# ---------------------------
# Navigation Logic
# ---------------------------

def navigate_widgets(widget_list, direction, container):
    current = container.focus_get()
    visible_widgets = [cb for cb in widget_list if cb.winfo_viewable()]
    
    if current in visible_widgets:
        idx = visible_widgets.index(current)
        if direction == "up":
            next_idx = (idx - 1) % len(visible_widgets)
        else:
            next_idx = (idx + 1) % len(visible_widgets)
        visible_widgets[next_idx].focus_set()
    elif visible_widgets:
        visible_widgets[0].focus_set()
    return "break"

def next_tab(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    tabs = notebook.tabs()
    if not tabs: return
    current = notebook.index(notebook.select())
    next_idx = (current + 1) % len(tabs)
    notebook.select(next_idx)
    return "break"

def prev_tab(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    tabs = notebook.tabs()
    if not tabs: return
    current = notebook.index(notebook.select())
    prev_idx = (current - 1) % len(tabs)
    notebook.select(prev_idx)
    return "break"

# ---------------------------
# Window Positioning Helpers
# ---------------------------

def position_left_of_root(popup, popup_width, popup_height):
    root.update_idletasks()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    new_x = root_x - popup_width - 10
    new_y = root_y
    popup.geometry(f"{popup_width}x{popup_height}+{new_x}+{new_y}")

def position_center_of_root(popup, popup_width, popup_height):
    root.update_idletasks()
    root_width = root.winfo_width()
    root_height = root.winfo_height()
    root_x = root.winfo_x()
    root_y = root.winfo_y()
    new_x = root_x + (root_width - popup_width) // 2
    new_y = root_y + (root_height - popup_height) // 2
    popup.geometry(f"{popup_width}x{popup_height}+{new_x}+{new_y}")

# ---------------------------
# Hotkey Triggers
# ---------------------------

def toggle_timestamp(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    if "Timestamp" not in all_options:
        all_options["Timestamp"] = tk.BooleanVar(value=False)
    all_options["Timestamp"].set(not all_options["Timestamp"].get())
    update_result()
    return "break"

def press_f1(event=None):
    if "Veeder Root" in all_options and "Titan Series" in all_options:
        titan_sel = multi_selections.setdefault("Titan Series", [])
        if not all_options["Veeder Root"].get():
            all_options["Veeder Root"].set(True)
            all_options["Titan Series"].set(True)
            opts = config.get("multi_popups", {}).get("Titan Series", ["Safe EOD Report", "Safe Summary Report"])
            open_multi_checkbox_popup("Titan Series", opts, titan_sel)
        else:
            all_options["Veeder Root"].set(False)
            all_options["Titan Series"].set(False)
            titan_sel.clear()
            update_result()
    return "break"

def press_f2(event=None):
    if "Veeder Root" in all_options and "Titan Series" in all_options and "Lottery" in all_options:
        titan_sel = multi_selections.setdefault("Titan Series", [])
        if not all_options["Veeder Root"].get():
            all_options["Veeder Root"].set(True)
            all_options["Titan Series"].set(True)
            all_options["Lottery"].set(True)
            opts = config.get("multi_popups", {}).get("Titan Series", ["Safe EOD Report", "Safe Summary Report"])
            open_multi_checkbox_popup("Titan Series", opts, titan_sel)
        else:
            all_options["Veeder Root"].set(False)
            all_options["Titan Series"].set(False)
            all_options["Lottery"].set(False)
            titan_sel.clear()
            update_result()
    return "break"

def trigger_add_option(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    open_add_option_popup()
    return "break"

def trigger_remove_option(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    open_remove_option_popup()
    return "break"

def trigger_add_category(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    open_add_category_popup()
    return "break"

def trigger_rename_category(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    open_rename_category_popup()
    return "break"

def trigger_quick_search(event=None):
    if isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)):
        return
    open_quick_search_popup()
    return "break"

def trigger_reorder_options(event=None):
    focused = root.focus_get()
    if isinstance(focused, (tk.Entry, tk.Text, ttk.Entry)):
        return
    open_reorder_options_popup()
    return "break"

# ---------------------------
# Dynamic UI Rendering
# ---------------------------

def make_entry_cmd(n, p):
    return lambda: open_single_entry_popup(n, p) if all_options[n].get() else update_result()

def make_multi_cmd(n, opts, sel):
    return lambda: open_multi_checkbox_popup(n, opts, sel) if all_options[n].get() else (sel.clear(), update_result())

def render_checkboxes():
    global all_checkbuttons, option_cb_map, tab_frames
    
    for tab in notebook.tabs():
        notebook.forget(tab)
        
    all_checkbuttons = []
    option_cb_map = {}
    tab_frames = {}

    categories = config.get("categories", {})
    multi_popups_config = config.get("multi_popups", {})
    entry_popups_config = config.get("entry_popups", {})

    for cat_name, opts in categories.items():
        tab_frame = ttk.Frame(notebook)
        notebook.add(tab_frame, text=f" {cat_name} ")
        tab_frames[cat_name] = tab_frame

        for name in opts:
            if name not in all_options:
                all_options[name] = tk.BooleanVar()

            if name in entry_popups_config:
                prefix = entry_popups_config[name]
                entry_values.setdefault(name, tk.StringVar())
                cmd = make_entry_cmd(name, prefix)
            elif name in multi_popups_config:
                sub_opts = multi_popups_config[name]
                multi_selections.setdefault(name, [])
                cmd = make_multi_cmd(name, sub_opts, multi_selections[name])
            else:
                cmd = update_result

            cb = tk.Checkbutton(tab_frame, text=name, variable=all_options[name], command=cmd)
            cb.pack(anchor="w", padx=10, pady=2)
            all_checkbuttons.append(cb)
            option_cb_map[name] = cb

    update_result()

# ---------------------------
# Category Management Windows
# ---------------------------

def open_add_category_popup():
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Add New Category")
    position_center_of_root(popup, 280, 140)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    tk.Label(popup, text="Category Name:", font=("Arial", 9, "bold")).pack(pady=8)
    cat_var = tk.StringVar()
    entry = tk.Entry(popup, textvariable=cat_var)
    entry.pack(pady=2); entry.focus_set()

    def confirm():
        new_cat = cat_var.get().strip()
        if not new_cat:
            messagebox.showwarning("Warning", "Category name cannot be empty!", parent=popup)
            return

        if new_cat in config["categories"]:
            messagebox.showwarning("Warning", "Category already exists!", parent=popup)
            return

        config["categories"][new_cat] = []
        save_config(config)
        render_checkboxes()
        popup.destroy()
        restore_focus(prev_focus)

    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: (popup.destroy(), restore_focus(prev_focus)))
    
    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=12)
    tk.Button(btn_frame, text="Add Category", command=confirm).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", command=lambda: (popup.destroy(), restore_focus(prev_focus))).pack(side="left", padx=5)

def open_rename_category_popup():
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Rename Category")
    position_center_of_root(popup, 300, 200)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    cats = list(config.get("categories", {}).keys())
    if not cats:
        messagebox.showinfo("Info", "No categories available to rename.", parent=popup)
        popup.destroy()
        return

    try:
        current_idx = notebook.index(notebook.select())
        default_cat = cats[current_idx] if current_idx < len(cats) else cats[0]
    except Exception:
        default_cat = cats[0]

    tk.Label(popup, text="Select Category:", font=("Arial", 9, "bold")).pack(pady=(10, 2))
    cat_var = tk.StringVar(value=default_cat)
    dropdown = ttk.Combobox(popup, textvariable=cat_var, values=cats, state="readonly")
    dropdown.pack(pady=2)

    tk.Label(popup, text="New Category Name:", font=("Arial", 9, "bold")).pack(pady=(10, 2))
    new_name_var = tk.StringVar(value=default_cat)
    entry = tk.Entry(popup, textvariable=new_name_var)
    entry.pack(pady=2)
    entry.focus_set()

    def update_entry_field(event=None):
        new_name_var.set(cat_var.get())

    dropdown.bind("<<ComboboxSelected>>", update_entry_field)

    def confirm():
        old_cat = cat_var.get()
        new_cat = new_name_var.get().strip()

        if not new_cat:
            messagebox.showwarning("Warning", "Category name cannot be empty!", parent=popup)
            return

        if new_cat == old_cat:
            popup.destroy()
            restore_focus(prev_focus)
            return

        if new_cat in config["categories"]:
            messagebox.showwarning("Warning", "A category with this name already exists!", parent=popup)
            return

        new_categories = {}
        for k, v in config["categories"].items():
            if k == old_cat:
                new_categories[new_cat] = v
            else:
                new_categories[k] = v

        config["categories"] = new_categories
        save_config(config)
        render_checkboxes()
        popup.destroy()
        restore_focus(prev_focus)

    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: (popup.destroy(), restore_focus(prev_focus)))

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="Rename", width=8, command=confirm).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", width=8, command=lambda: (popup.destroy(), restore_focus(prev_focus))).pack(side="left", padx=5)

def open_remove_category_popup():
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Remove Category")
    position_center_of_root(popup, 300, 160)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    cats = list(config.get("categories", {}).keys())
    if not cats:
        messagebox.showinfo("Info", "No categories available to remove.", parent=popup)
        popup.destroy()
        return

    tk.Label(popup, text="Select Category to Remove:", font=("Arial", 9, "bold")).pack(pady=10)
    cat_var = tk.StringVar(value=cats[0])
    dropdown = ttk.Combobox(popup, textvariable=cat_var, values=cats, state="readonly")
    dropdown.pack(pady=5)
    dropdown.focus_set()

    def confirm():
        target = cat_var.get()
        if target in config["categories"]:
            for opt in config["categories"][target]:
                if opt in all_options: del all_options[opt]
                if opt in config.get("multi_popups", {}): del config["multi_popups"][opt]
                if opt in config.get("entry_popups", {}): del config["entry_popups"][opt]
                if opt in multi_selections: del multi_selections[opt]
                if opt in entry_values: del entry_values[opt]
            
            del config["categories"][target]
            save_config(config)
            render_checkboxes()

        popup.destroy()
        restore_focus(prev_focus)

    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: (popup.destroy(), restore_focus(prev_focus)))

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=12)
    tk.Button(btn_frame, text="Remove", width=8, command=confirm).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", width=8, command=lambda: (popup.destroy(), restore_focus(prev_focus))).pack(side="left", padx=5)

# ---------------------------
# Option Reordering Window
# ---------------------------

def open_reorder_options_popup():
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Reorder Options")
    position_center_of_root(popup, 320, 360)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    cats = list(config.get("categories", {}).keys())
    if not cats:
        messagebox.showinfo("Info", "No categories available.", parent=popup)
        popup.destroy()
        return

    try:
        current_idx = notebook.index(notebook.select())
        default_cat = cats[current_idx] if current_idx < len(cats) else cats[0]
    except Exception:
        default_cat = cats[0]

    tk.Label(popup, text="Select Category:", font=("Arial", 9, "bold")).pack(pady=(10, 2))
    cat_var = tk.StringVar(value=default_cat)
    cat_dropdown = ttk.Combobox(popup, textvariable=cat_var, values=cats, state="readonly")
    cat_dropdown.pack(pady=2)

    list_frame = tk.Frame(popup)
    list_frame.pack(fill="both", expand=True, padx=15, pady=8)

    listbox = tk.Listbox(list_frame, selectmode="browse", height=8)
    listbox.pack(side="left", fill="both", expand=True)

    scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=listbox.yview)
    scrollbar.pack(side="right", fill="y")
    listbox.config(yscrollcommand=scrollbar.set)

    def populate_list(*args):
        listbox.delete(0, tk.END)
        for opt in config["categories"].get(cat_var.get(), []):
            listbox.insert(tk.END, opt)
        if listbox.size() > 0:
            listbox.select_set(0)

    cat_dropdown.bind("<<ComboboxSelected>>", populate_list)
    populate_list()

    def move_up():
        sel = listbox.curselection()
        if not sel or sel[0] == 0:
            return
        idx = sel[0]
        cat = cat_var.get()
        opts = config["categories"][cat]
        opts[idx], opts[idx-1] = opts[idx-1], opts[idx]
        populate_list()
        listbox.select_set(idx - 1)
        listbox.see(idx - 1)

    def move_down():
        sel = listbox.curselection()
        if not sel or sel[0] == listbox.size() - 1:
            return
        idx = sel[0]
        cat = cat_var.get()
        opts = config["categories"][cat]
        opts[idx], opts[idx+1] = opts[idx+1], opts[idx]
        populate_list()
        listbox.select_set(idx + 1)
        listbox.see(idx + 1)

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=5)

    tk.Button(btn_frame, text="▲ Move Up", command=move_up, width=11).pack(side="left", padx=4)
    tk.Button(btn_frame, text="▼ Move Down", command=move_down, width=11).pack(side="left", padx=4)

    def save_and_close():
        save_config(config)
        render_checkboxes()
        popup.destroy()
        restore_focus(prev_focus)

    tk.Button(popup, text="Done", width=12, command=save_and_close).pack(pady=(5, 10))

    popup.bind('<Escape>', lambda e: save_and_close())
    popup.protocol("WM_DELETE_WINDOW", save_and_close)

# ---------------------------
# Manage Options Windows
# ---------------------------

def open_add_option_popup():
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Add New Option")
    position_center_of_root(popup, 380, 430)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    # --- Section 1: Option Details ---
    details_frame = ttk.LabelFrame(popup, text=" Option Details ", padding=10)
    details_frame.pack(fill="x", padx=15, pady=(10, 5))

    tk.Label(details_frame, text="Option Name:", font=("Arial", 9, "bold")).grid(row=0, column=0, sticky="w", pady=4)
    name_var = tk.StringVar()
    entry = tk.Entry(details_frame, textvariable=name_var)
    entry.grid(row=0, column=1, columnspan=2, sticky="ew", pady=4, padx=(5, 0))
    entry.focus_set()

    tk.Label(details_frame, text="Category Tab:", font=("Arial", 9, "bold")).grid(row=1, column=0, sticky="w", pady=4)

    cat_names = list(config.get("categories", {}).keys())
    if not cat_names:
        config["categories"]["General Options"] = []
        cat_names = ["General Options"]

    category_var = tk.StringVar(value=cat_names[0])
    category_dropdown = ttk.Combobox(
        details_frame, 
        textvariable=category_var, 
        values=cat_names,
        state="readonly",
        width=14
    )
    category_dropdown.grid(row=1, column=1, sticky="w", pady=4, padx=(5, 5))

    def quick_add_cat():
        popup.destroy()
        open_add_category_popup()

    def quick_rename_cat():
        popup.destroy()
        open_rename_category_popup()

    cat_btn_frame = tk.Frame(details_frame)
    cat_btn_frame.grid(row=2, column=0, columnspan=2, sticky="w", pady=(4, 0))

    tk.Button(cat_btn_frame, text="Add category", command=quick_add_cat).pack(side="left", padx=(0, 5))
    tk.Button(cat_btn_frame, text="Rename", command=quick_rename_cat).pack(side="left")

    details_frame.columnconfigure(1, weight=1)

    # --- Section 2: Popup Behavior ---
    behavior_frame = ttk.LabelFrame(popup, text=" Popup Behavior ", padding=10)
    behavior_frame.pack(fill="x", padx=15, pady=5)

    popup_type = tk.StringVar(value="none")

    rb_none = tk.Radiobutton(behavior_frame, text="None (Standard Checkbox)", variable=popup_type, value="none")
    rb_multi = tk.Radiobutton(behavior_frame, text="Multi-Select Checklist", variable=popup_type, value="multi")
    rb_entry = tk.Radiobutton(behavior_frame, text="Text Input Popup", variable=popup_type, value="entry")

    rb_none.pack(anchor="w")
    rb_multi.pack(anchor="w")
    rb_entry.pack(anchor="w")

    # Dynamic Frame for Extra Fields inside behavior frame
    extra_frame = tk.Frame(behavior_frame)
    extra_frame.pack(fill="x", pady=(6, 0))

    sub_opts_var = tk.StringVar()
    prefix_var = tk.StringVar()

    sub_label = tk.Label(extra_frame, text="Sub-options (comma separated):", font=("Arial", 8, "bold"))
    sub_entry = tk.Entry(extra_frame, textvariable=sub_opts_var)
    sub_hint = tk.Label(extra_frame, text="e.g. Option A, Option B, Option C", font=("Arial", 7, "italic"), fg="gray")

    prefix_label = tk.Label(extra_frame, text="Output Prefix (e.g. BOL# or blank for Name#):", font=("Arial", 8, "bold"))
    prefix_entry = tk.Entry(extra_frame, textvariable=prefix_var)
    prefix_hint = tk.Label(extra_frame, text="e.g. BOL# outputs BOL#123", font=("Arial", 7, "italic"), fg="gray")

    def toggle_behavior(*args):
        mode = popup_type.get()
        sub_label.pack_forget()
        sub_entry.pack_forget()
        sub_hint.pack_forget()
        prefix_label.pack_forget()
        prefix_entry.pack_forget()
        prefix_hint.pack_forget()

        if mode == "multi":
            sub_label.pack(anchor="w")
            sub_entry.pack(fill="x", pady=2)
            sub_hint.pack(anchor="w")
        elif mode == "entry":
            prefix_label.pack(anchor="w")
            prefix_entry.pack(fill="x", pady=2)
            prefix_hint.pack(anchor="w")

    popup_type.trace_add("write", toggle_behavior)

    # --- Section 3: Action Buttons ---
    def confirm():
        new_name = name_var.get().strip()
        cat = category_var.get()
        mode = popup_type.get()

        if not new_name:
            messagebox.showwarning("Warning", "Option name cannot be empty!", parent=popup)
            return

        all_existing = [opt for opts in config["categories"].values() for opt in opts]
        if new_name in all_existing or new_name == "Timestamp":
            messagebox.showwarning("Warning", "An option with this name already exists!", parent=popup)
            return

        if mode == "multi":
            raw_sub = sub_opts_var.get().strip()
            if not raw_sub:
                messagebox.showwarning("Warning", "Please enter at least one sub-option!", parent=popup)
                return
            parsed_sub_opts = [s.strip() for s in raw_sub.split(",") if s.strip()]
            if not parsed_sub_opts:
                messagebox.showwarning("Warning", "Invalid sub-option list provided!", parent=popup)
                return
            config.setdefault("multi_popups", {})[new_name] = parsed_sub_opts

        elif mode == "entry":
            pref = prefix_var.get().strip()
            config.setdefault("entry_popups", {})[new_name] = pref
            entry_values[new_name] = tk.StringVar()

        if cat in config["categories"]:
            config["categories"][cat].append(new_name)

        save_config(config)
        render_checkboxes()
        popup.destroy()
        restore_focus(prev_focus)

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=12)
    tk.Button(btn_frame, text="Add Option", width=10, command=confirm).pack(side="left", padx=5)
    tk.Button(btn_frame, text="Cancel", width=10, command=lambda: (popup.destroy(), restore_focus(prev_focus))).pack(side="left", padx=5)

    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: (popup.destroy(), restore_focus(prev_focus)))

def open_remove_option_popup():
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Remove Option")
    position_center_of_root(popup, 340, 180)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    all_current_opts = [opt for opts in config.get("categories", {}).values() for opt in opts]
    
    if not all_current_opts:
        messagebox.showinfo("Info", "No options available to remove.", parent=popup)
        popup.destroy()
        return

    tk.Label(popup, text="Select Option to Remove:", font=("Arial", 9, "bold")).pack(pady=10)
    remove_var = tk.StringVar(value=all_current_opts[0])
    dropdown = ttk.Combobox(popup, textvariable=remove_var, values=all_current_opts, state="readonly")
    dropdown.pack(pady=5)
    dropdown.focus_set()

    def confirm():
        target = remove_var.get()
        for cat_opts in config.get("categories", {}).values():
            if target in cat_opts:
                cat_opts.remove(target)

        if target in all_options: del all_options[target]
        if target in config.get("multi_popups", {}): del config["multi_popups"][target]
        if target in config.get("entry_popups", {}): del config["entry_popups"][target]
        if target in multi_selections: del multi_selections[target]
        if target in entry_values: del entry_values[target]

        save_config(config)
        render_checkboxes()
        popup.destroy()
        restore_focus(prev_focus)

    def quick_rem_cat():
        popup.destroy()
        open_remove_category_popup()

    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: (popup.destroy(), restore_focus(prev_focus)))

    btn_frame = tk.Frame(popup)
    btn_frame.pack(pady=15)
    tk.Button(btn_frame, text="Remove Option", command=confirm).pack(side="left", padx=3)
    tk.Button(btn_frame, text="- Category", command=quick_rem_cat).pack(side="left", padx=3)
    tk.Button(btn_frame, text="Cancel", command=lambda: (popup.destroy(), restore_focus(prev_focus))).pack(side="left", padx=3)

# ---------------------------
# Quick Search / Palette
# ---------------------------

def open_quick_search_popup():
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Quick Search")
    position_center_of_root(popup, 280, 260)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    tk.Label(popup, text="Search Option:", font=("Arial", 9, "bold")).pack(pady=(8, 2))
    
    search_var = tk.StringVar()
    search_entry = tk.Entry(popup, textvariable=search_var)
    search_entry.pack(fill="x", padx=15, pady=2)
    search_entry.focus_set()

    listbox = tk.Listbox(popup, selectmode="browse", height=8)
    listbox.pack(fill="both", expand=True, padx=15, pady=5)

    all_opts = [opt for opts in config.get("categories", {}).values() for opt in opts]

    def filter_list(event=None):
        if event and event.keysym in ["Up", "Down"]:
            return
        query = search_var.get().strip().lower()
        listbox.delete(0, tk.END)
        for opt in all_opts:
            if query in opt.lower():
                status = "[✓] " if all_options.get(opt, tk.BooleanVar()).get() else "[  ] "
                listbox.insert(tk.END, status + opt)
        if listbox.size() > 0:
            listbox.select_set(0)

    filter_list()
    search_entry.bind('<KeyRelease>', filter_list)

    def trigger_selection():
        sel = listbox.curselection()
        if not sel:
            if listbox.size() > 0: sel = (0,)
            else: return
        selected_text = listbox.get(sel[0])
        opt_name = selected_text.replace("[✓] ", "").replace("[  ] ", "")
        
        if opt_name in option_cb_map:
            popup.destroy()
            cb = option_cb_map[opt_name]
            cb.invoke()

    def on_key_down(event):
        if listbox.size() > 0:
            current = listbox.curselection()
            idx = current[0] if current else 0
            if idx < listbox.size() - 1:
                listbox.select_clear(0, tk.END)
                listbox.select_set(idx + 1)
                listbox.see(idx + 1)
        return "break"

    def on_key_up(event):
        if listbox.size() > 0:
            current = listbox.curselection()
            idx = current[0] if current else 0
            if idx > 0:
                listbox.select_clear(0, tk.END)
                listbox.select_set(idx - 1)
                listbox.see(idx - 1)
        return "break"

    search_entry.bind('<Down>', on_key_down)
    search_entry.bind('<Up>', on_key_up)
    search_entry.bind('<Return>', lambda e: trigger_selection())
    listbox.bind('<Double-Button-1>', lambda e: trigger_selection())
    
    popup.bind('<Escape>', lambda e: (popup.destroy(), restore_focus(prev_focus)))
    popup.protocol("WM_DELETE_WINDOW", lambda: (popup.destroy(), restore_focus(prev_focus)))

# ---------------------------
# Dynamic Dialog Popups
# ---------------------------

def ask_username():
    global user_name
    popup = tk.Toplevel()
    popup.title("Enter Username")
    position_center_of_root(popup, 300, 120)
    popup.resizable(False, False)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    tk.Label(popup, text="Enter your name:").pack(pady=10)
    username_var = tk.StringVar()
    entry = tk.Entry(popup, textvariable=username_var)
    entry.pack(pady=5); entry.focus_force()

    def confirm():
        global user_name
        name = username_var.get().strip()
        if name:
            user_name = name
            popup.destroy()
        else:
            messagebox.showwarning("Invalid Input", "Please enter a name!")

    popup.protocol("WM_DELETE_WINDOW", lambda: (root.destroy(), os._exit(0)))
    tk.Button(popup, text="Confirm", width=10, command=confirm).pack(pady=5)
    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: (root.destroy(), os._exit(0)))
    popup.wait_window()

def open_single_entry_popup(name, prefix):
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root)
    popup.title("Value")
    position_left_of_root(popup, 250, 120)
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()

    tk.Label(popup, text=f"Enter {name}:").pack(pady=5)
    var = entry_values.setdefault(name, tk.StringVar())
    entry = tk.Entry(popup, textvariable=var)
    entry.pack(pady=5); entry.focus_set()

    def confirm():
        if not var.get().strip():
            all_options[name].set(False)
        popup.destroy()
        update_result()
        restore_focus(prev_focus)

    def cancel():
        all_options[name].set(False)
        var.set("")
        popup.destroy()
        update_result()
        restore_focus(prev_focus)

    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: cancel())
    popup.protocol("WM_DELETE_WINDOW", cancel)
    tk.Button(popup, text="Confirm", command=confirm).pack(pady=5)

def open_multi_checkbox_popup(name, options_list, selected_list):
    prev_focus = root.focus_get()
    popup = tk.Toplevel(root); popup.title(name)
    position_left_of_root(popup, 250, max(220, len(options_list) * 30 + 100))
    try: popup.iconbitmap(resource_path("icon.ico"))
    except: pass
    popup.transient(root); popup.grab_set()
    
    popup_cbs = []
    vars_map = []
    
    tk.Label(popup, text=f"Select {name}:", font=("Arial", 10, "bold")).pack(pady=5)

    for opt in options_list:
        v = tk.BooleanVar(value=(opt in selected_list))
        cb = tk.Checkbutton(popup, text=opt, variable=v)
        cb.pack(anchor="w", padx=20)
        popup_cbs.append(cb)
        vars_map.append((opt, v))

    def confirm():
        selected_list.clear()
        selected_list.extend([opt for opt, v in vars_map if v.get()])
        popup.destroy(); update_result()
        restore_focus(prev_focus)

    def cancel():
        all_options[name].set(False)
        selected_list.clear()
        popup.destroy(); update_result()
        restore_focus(prev_focus)

    popup.bind('w', lambda e: navigate_widgets(popup_cbs, "up", popup))
    popup.bind('W', lambda e: navigate_widgets(popup_cbs, "up", popup))
    popup.bind('s', lambda e: navigate_widgets(popup_cbs, "down", popup))
    popup.bind('S', lambda e: navigate_widgets(popup_cbs, "down", popup))
    popup.bind('<Return>', lambda e: confirm())
    popup.bind('<Escape>', lambda e: cancel())
    popup.protocol("WM_DELETE_WINDOW", cancel)
    
    tk.Button(popup, text="Confirm", command=confirm).pack(pady=10)
    if popup_cbs: popup_cbs[0].focus_set()

# ---------------------------
# Main Application Layout
# ---------------------------

root = tk.Tk()
root.title("Data Entry Tool")
root.geometry("360x510") 

try: root.iconbitmap(resource_path("icon.ico"))
except: pass

config = load_config()

user_name = ""
ask_username()

# Notebook (Tabbed Layout)
notebook = ttk.Notebook(root)
notebook.pack(fill="both", expand=True, padx=10, pady=(5, 0))

result_frame = tk.Frame(root)
result_frame.pack(fill="x", padx=10, pady=5)

all_options = {
    "Timestamp": tk.BooleanVar(value=False)
}
all_checkbuttons = []
option_cb_map = {}
tab_frames = {}

# Result text box
result = tk.Text(result_frame, height=4, width=32, wrap="word", state="disabled")
result.pack(pady=2)

button_frame = tk.Frame(result_frame)
button_frame.pack(pady=2)

# Copy, Clear, and Reorder Buttons
tk.Button(button_frame, text="Copy", width=6, command=copy_to_clipboard).pack(side="left", padx=2)
tk.Button(button_frame, text="Clear", width=6, command=clear_all).pack(side="left", padx=2)
tk.Button(button_frame, text="Reorder", width=6, command=open_reorder_options_popup).pack(side="left", padx=2)

# Dedicated Timestamp Checkbutton Indicator
timestamp_cb = tk.Checkbutton(
    button_frame, 
    text="Timestamp", 
    variable=all_options["Timestamp"], 
    command=update_result
)
timestamp_cb.pack(side="left", padx=5)

# Render checkboxes safely
render_checkboxes()

# ---------------------------
# Key Bindings
# ---------------------------

for k in ['+', '<plus>', '<KP_Add>']:
    root.bind_class('Checkbutton', k, trigger_add_option)

for k in ['-', '<minus>', '<KP_Subtract>']:
    root.bind_class('Checkbutton', k, trigger_remove_option)

for k in ['*', '<asterisk>', '<KP_Multiply>']:
    root.bind_class('Checkbutton', k, trigger_add_category)

for k in ['r', 'R']:
    root.bind_class('Checkbutton', k, trigger_rename_category)

for k in ['/', '<slash>', '<KP_Divide>']:
    root.bind_class('Checkbutton', k, trigger_quick_search)

for key_spec in ['o', 'O', '<Key-o>', '<Key-O>', '<Control-o>', '<Control-O>']:
    root.bind_class('Checkbutton', key_spec, trigger_reorder_options)
    root.bind_all(key_spec, trigger_reorder_options)

# Global Bindings
root.bind('<Control-c>', copy_to_clipboard)
root.bind('<Control-C>', copy_to_clipboard)

# Arrow key & A/D tab navigation
root.bind_all('<Right>', next_tab)
root.bind_all('<Left>', prev_tab)
root.bind_all('d', lambda e: next_tab(e) if not isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)) else None)
root.bind_all('a', lambda e: prev_tab(e) if not isinstance(root.focus_get(), (tk.Entry, tk.Text, ttk.Entry)) else None)

# Global Hotkeys
root.bind_all('+', trigger_add_option)
root.bind_all('<KP_Add>', trigger_add_option)
root.bind_all('-', trigger_remove_option)
root.bind_all('<KP_Subtract>', trigger_remove_option)

root.bind_all('*', trigger_add_category)
root.bind_all('r', trigger_rename_category)
root.bind_all('R', trigger_rename_category)
root.bind_all('/', trigger_quick_search)

root.bind_all('<Delete>', clear_all)
root.bind_all('<F1>', press_f1)
root.bind_all('<F2>', press_f2)
root.bind_all('`', toggle_timestamp)
root.bind_all('w', lambda e: navigate_widgets(all_checkbuttons, "up", root))
root.bind_all('W', lambda e: navigate_widgets(all_checkbuttons, "up", root))
root.bind_all('s', lambda e: navigate_widgets(all_checkbuttons, "down", root))
root.bind_all('S', lambda e: navigate_widgets(all_checkbuttons, "down", root))

# Start focus loop safely
if all_checkbuttons:
    all_checkbuttons[0].focus_set()

=======
import tkinter as tk
from tkinter import messagebox, simpledialog, ttk
from datetime import datetime
import json
import sys
import os

# ---------------------------
# Helper for PyInstaller pathing
# ---------------------------
def resource_path(relative_path):
    base_path = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)

ICON_FILE = resource_path("app_icon.ico")
LIGHT_COLORS = {
    "background": "#F3F6FB",
    "surface": "#FFFFFF",
    "surface_alt": "#EAF0F8",
    "text": "#182A43",
    "muted": "#65758B",
    "accent": "#2563EB",
    "accent_active": "#1D4ED8",
    "border": "#D8E1ED",
}
DARK_COLORS = {
    "background": "#151A23",
    "surface": "#202938",
    "surface_alt": "#2B3749",
    "text": "#E7EDF7",
    "muted": "#A2B0C3",
    "accent": "#82AFFF",
    "accent_active": "#A0C0FF",
    "border": "#3A485C",
}
COLORS = dict(LIGHT_COLORS)
dark_mode_enabled = False

# ---------------------------
# State Management
# ---------------------------
click_order = []
option_action_names = {}
category_action_names = {}
custom_option_types = {}
custom_option_choices = {}
custom_text_values = {}
custom_multi_selected = {}

# ---------------------------
# Functions
# ---------------------------

def on_checkbox_toggle(name):
    """Tracks the order of clicks and opens popups"""
    action_name = option_action_names.get(name, name)
    if all_options[name].get():
        if name not in click_order:
            click_order.append(name)
    else:
        if name in click_order:
            click_order.remove(name)
    
    if action_name == "Bill Of Lading [1]":
        if all_options[name].get(): open_bol_popup(name, bol1_value)
    elif action_name == "Bill Of Lading [2]":
        if all_options[name].get(): open_bol_popup(name, bol2_value)
    elif action_name == "Bill Of Lading [3]":
        if all_options[name].get(): open_bol_popup(name, bol3_value)
    elif action_name == "NCR":
        if all_options[name].get():
            open_multi_checkbox_popup(name, ["Fleetwide", "Fuelman", "PumpPass", "ExxonMobilG", "Shell"], ncr_selected)
        else:
            ncr_selected.clear()
    elif action_name == "NPR":
        if all_options[name].get():
            open_multi_checkbox_popup(name, ["E-85", "Diesel", "Racingfuel", "Kerosene"], npr_selected)
        else:
            npr_selected.clear()
    elif action_name == "Loyalty":
        if all_options[name].get():
            open_multi_checkbox_popup(name, ["600", "888", "800", "211"], loyalty_selected)
        else:
            loyalty_selected.clear()
    elif action_name == "Lottery":
        if all_options[name].get():
            open_multi_checkbox_popup(name, ["FL Lottery", "IN Lottery", "IL Lottery"], lottery_selected)
        else:
            lottery_selected.clear()
    elif name in custom_option_types:
        option_type = custom_option_types[name]
        if all_options[name].get() and option_type == "text":
            open_custom_text_popup(name)
        elif all_options[name].get() and option_type == "multi":
            open_multi_checkbox_popup(
                name,
                custom_option_choices[name],
                custom_multi_selected.setdefault(name, []),
            )
        elif not all_options[name].get():
            if option_type == "text":
                custom_text_values[name].set("")
            elif option_type == "multi":
                custom_multi_selected[name].clear()
            
    update_result()

def update_result():
    selected = []
    timestamp_str = ""

    for name in click_order:
        if name == "Timestamp":
            now = datetime.now().strftime("%m/%d/%Y")
            timestamp_str = f" -Ric(DE) {now}"
            continue
            
        # Reverted Logic for NCR, NPR, Loyalty
        action_name = option_action_names.get(name, name)
        custom_type = custom_option_types.get(name, "checkbox")
        if custom_type == "text" and name in custom_text_values:
            selected.append(f"{name}#{custom_text_values[name].get().strip()}")
        elif custom_type == "multi" and name in custom_multi_selected:
            choices = custom_multi_selected[name]
            selected.append(f"{name}({', '.join(choices)})" if choices else name)
        elif action_name == "NCR":
            if ncr_selected:
                selected.append(f"{name}({', '.join(ncr_selected)})")
            else:
                selected.append(name)
        elif action_name == "NPR":
            if npr_selected:
                selected.append(f"{name}({', '.join(npr_selected)})")
            else:
                selected.append(name)
        elif action_name == "Loyalty":
            if loyalty_selected:
                selected.append(f"{name}({', '.join(loyalty_selected)})")
            else:
                selected.append(name)
        
        # Keeping Lottery as sub-selections only (per previous request)
        elif action_name == "Lottery":
            if lottery_selected:
                selected.append(", ".join(lottery_selected))
            else:
                selected.append(name)
        
        elif action_name == "Bill Of Lading [1]":
            val = bol1_value.get().strip()
            selected.append(f"BOL#{val}" if val else "BOL1#")
        elif action_name == "Bill Of Lading [2]":
            val = bol2_value.get().strip()
            selected.append(f"BOL#{val}" if val else "BOL2#")
        elif action_name == "Bill Of Lading [3]":
            val = bol3_value.get().strip()
            selected.append(f"BOL#{val}" if val else "BOL3#")
        else:
            selected.append(name)

    final_text = ", ".join(selected) + timestamp_str
    
    result.config(state="normal")
    result.delete("1.0", tk.END)
    result.insert(tk.END, final_text.strip())
    result.config(state="disabled")

def copy_to_clipboard(event=None):
    root.clipboard_clear()
    root.clipboard_append(result.get("1.0", tk.END).strip())
    root.update()

def clear_all():
    for name, var in all_options.items():
        var.set(False)
    for value in custom_text_values.values():
        value.set("")
    for selected in custom_multi_selected.values():
        selected.clear()
    click_order.clear()
    bol1_value.set("")
    bol2_value.set("")
    bol3_value.set("")
    ncr_selected.clear()
    npr_selected.clear()
    loyalty_selected.clear()
    lottery_selected.clear()
    update_result()
    root.focus_set()


def activate_popup(window, initial_focus=None):
    window.configure(background=COLORS["background"])
    window.iconbitmap(ICON_FILE)
    root.update_idletasks()
    window.update_idletasks()
    x = root.winfo_rootx() + (root.winfo_width() - window.winfo_width()) // 2
    y = root.winfo_rooty() + (root.winfo_height() - window.winfo_height()) // 2
    window.geometry(f"+{x}+{y}")
    window.lift()
    window.grab_set()
    window.focus_force()
    if initial_focus is not None:
        initial_focus.focus_force()


def save_customizations(
    categories,
    options,
    removed_category_names=None,
    removed_option_names=None,
    saved_category_labels=None,
    saved_option_labels=None,
    saved_category_order=None,
    saved_option_order=None,
    saved_option_types=None,
    saved_option_choices=None,
):
    config_dir = os.path.join(
        os.environ.get("APPDATA", os.path.expanduser("~")),
        "TechHub Input Logger Tool",
    )
    config_path = os.path.join(config_dir, "customizations.json")
    try:
        os.makedirs(config_dir, exist_ok=True)
        with open(config_path, "w", encoding="utf-8") as config_file:
            json.dump(
                {
                    "categories": categories,
                    "options": options,
                    "removed_categories": sorted(
                        hidden_categories if removed_category_names is None else removed_category_names
                    ),
                    "removed_options": sorted(
                        hidden_options if removed_option_names is None else removed_option_names
                    ),
                    "category_labels": (
                        category_labels if saved_category_labels is None else saved_category_labels
                    ),
                    "option_labels": (
                        option_labels if saved_option_labels is None else saved_option_labels
                    ),
                    "category_order": (
                        list(category_options)
                        if saved_category_order is None
                        else saved_category_order
                    ),
                    "option_order": {
                        name: list(option_names)
                        for name, option_names in category_options.items()
                    }
                    if saved_option_order is None
                    else saved_option_order,
                    "dark_mode": dark_mode_enabled,
                    "option_types": (
                        custom_option_types
                        if saved_option_types is None
                        else saved_option_types
                    ),
                    "option_choices": (
                        custom_option_choices
                        if saved_option_choices is None
                        else saved_option_choices
                    ),
                },
                config_file,
                indent=2,
            )
    except OSError as error:
        messagebox.showerror("Save Failed", f"Could not save changes:\n{error}", parent=root)
        return False
    return True


def add_option_checkbox(category_name, option_name):
    if option_name not in all_options:
        all_options[option_name] = tk.BooleanVar()
    checkbox = ttk.Checkbutton(
        category_frames[category_name],
        text=option_name,
        variable=all_options[option_name],
        command=lambda n=option_name: on_checkbox_toggle(n),
    )
    checkbox.pack(anchor="w", fill="x", pady=4)
    option_widgets[option_name] = checkbox


def add_category_tab(category_name):
    frame = tk.Frame(
        options_notebook,
        padx=14,
        pady=12,
        background=COLORS["surface"],
    )
    category_frames[category_name] = frame
    options_notebook.add(frame, text=category_name)
    for option_name in category_options[category_name]:
        add_option_checkbox(category_name, option_name)
    return frame


def add_new_category():
    category_name = simpledialog.askstring(
        "Add New Category",
        "Enter a name for the new category:",
        parent=root,
    )
    if category_name is None:
        return

    category_name = category_name.strip()
    if not category_name:
        messagebox.showwarning("Invalid Category", "Category name cannot be empty.", parent=root)
        return
    reserved_categories = {
        name.casefold()
        for name in (*default_category_options, *category_labels.values())
    }
    if category_name.casefold() in reserved_categories:
        messagebox.showwarning("Duplicate Category", "That category name is reserved.", parent=root)
        return
    if any(name.casefold() == category_name.casefold() for name in category_frames):
        messagebox.showwarning("Duplicate Category", "That category already exists.", parent=root)
        return

    new_categories = {**custom_categories, category_name: []}
    new_category_order = [*category_options, category_name]
    new_option_order = {
        name: list(option_names)
        for name, option_names in category_options.items()
    }
    new_option_order[category_name] = []
    if not save_customizations(
        new_categories,
        custom_options,
        saved_category_order=new_category_order,
        saved_option_order=new_option_order,
    ):
        return

    custom_categories[category_name] = []
    category_options[category_name] = []
    category_action_names[category_name] = category_name
    options_notebook.select(add_category_tab(category_name))


def add_new_option():
    if not category_frames:
        messagebox.showinfo(
            "Add New Option",
            "Add a category before adding an option.",
            parent=root,
        )
        return

    dialog = tk.Toplevel(root)
    dialog.title("Add New Option")
    dialog.geometry("340x390")
    dialog.transient(root)

    tk.Label(dialog, text="Option name:").pack(anchor="w", padx=10, pady=(10, 2))
    name_entry = tk.Entry(dialog)
    name_entry.pack(fill="x", padx=10)
    tk.Label(dialog, text="Category:").pack(anchor="w", padx=10, pady=(6, 2))
    category_choice = ttk.Combobox(
        dialog,
        values=list(category_frames),
        state="readonly",
    )
    category_choice.pack(fill="x", padx=10)
    category_choice.current(0)
    tk.Label(dialog, text="Option type:").pack(anchor="w", padx=10, pady=(6, 2))
    option_type_choice = ttk.Combobox(
        dialog,
        values=[
            "Standard",
            "Text Entry",
            "Multiple Choices",
        ],
        state="readonly",
    )
    option_type_choice.pack(fill="x", padx=10)
    option_type_choice.current(0)

    choices_frame = tk.Frame(dialog)
    tk.Label(
        choices_frame,
        text="Choices (one per line):",
    ).pack(anchor="w", pady=(6, 2))
    choices_text = tk.Text(
        choices_frame,
        height=6,
        wrap="word",
        bg=COLORS["surface"],
        fg=COLORS["text"],
        insertbackground=COLORS["text"],
        relief="flat",
        highlightthickness=1,
        highlightbackground=COLORS["border"],
        highlightcolor=COLORS["accent"],
    )
    choices_text.pack(fill="both", expand=True)

    def insert_choice_newline(event):
        choices_text.insert("insert", "\n")
        return "break"

    choices_text.bind("<Return>", insert_choice_newline)

    def update_type_fields(event=None):
        if option_type_choice.current() == 2:
            choices_frame.pack(fill="both", expand=True, padx=10, before=buttons)
        else:
            choices_frame.pack_forget()

    option_type_choice.bind("<<ComboboxSelected>>", update_type_fields)

    def confirm(event=None):
        option_name = name_entry.get().strip()
        category_name = category_choice.get()
        if not option_name:
            messagebox.showwarning("Invalid Option", "Option name cannot be empty.", parent=dialog)
            name_entry.focus_set()
            return
        reserved_options = {
            name.casefold()
            for option_names in default_category_options.values()
            for name in option_names
        }
        if (
            option_name.casefold() == "timestamp"
            or option_name.casefold() in reserved_options
            or any(name.casefold() == option_name.casefold() for name in all_options)
        ):
            messagebox.showwarning("Duplicate Option", "That option already exists.", parent=dialog)
            name_entry.focus_set()
            return

        option_type = ("checkbox", "text", "multi")[option_type_choice.current()]
        choices = []
        if option_type == "multi":
            choices = [
                choice.strip()
                for choice in choices_text.get("1.0", "end").splitlines()
                if choice.strip()
            ]
            if not choices:
                messagebox.showwarning(
                    "Invalid Choices",
                    "Enter at least one choice for a multiple-choice option.",
                    parent=dialog,
                )
                choices_text.focus_set()
                return
            if len({choice.casefold() for choice in choices}) != len(choices):
                messagebox.showwarning(
                    "Duplicate Choices",
                    "Each choice must be unique.",
                    parent=dialog,
                )
                choices_text.focus_set()
                return

        new_custom_options = {
            name: list(option_names)
            for name, option_names in custom_options.items()
        }
        new_custom_options.setdefault(category_name, []).append(option_name)
        new_option_types = dict(custom_option_types)
        new_option_types[option_name] = option_type
        new_option_choices = {
            name: list(option_names)
            for name, option_names in custom_option_choices.items()
        }
        if option_type == "multi":
            new_option_choices[option_name] = choices
        new_option_order = {
            name: list(option_names)
            for name, option_names in category_options.items()
        }
        new_option_order[category_name].append(option_name)
        if not save_customizations(
            custom_categories,
            new_custom_options,
            saved_option_order=new_option_order,
            saved_option_types=new_option_types,
            saved_option_choices=new_option_choices,
        ):
            return

        custom_options[category_name] = new_custom_options[category_name]
        custom_option_types.clear()
        custom_option_types.update(new_option_types)
        custom_option_choices.clear()
        custom_option_choices.update(new_option_choices)
        category_options[category_name].append(option_name)
        option_action_names[option_name] = option_name
        if option_type == "text":
            custom_text_values[option_name] = tk.StringVar()
        elif option_type == "multi":
            custom_multi_selected[option_name] = []
        add_option_checkbox(category_name, option_name)
        dialog.destroy()

    update_type_fields()
    buttons = tk.Frame(dialog)
    buttons.pack(pady=10)
    tk.Button(buttons, text="Add", width=10, command=confirm).pack(side="left", padx=5)
    tk.Button(buttons, text="Cancel", width=10, command=dialog.destroy).pack(side="left", padx=5)
    dialog.bind("<Return>", confirm)
    dialog.bind("<Escape>", lambda event: dialog.destroy())
    activate_popup(dialog, name_entry)


def show_add_choices(event=None):
    if event is not None and event.widget.winfo_toplevel() is not root:
        return

    popup = tk.Toplevel(root)
    popup.title("Input Logger Tool")
    popup.geometry("280x90")
    popup.transient(root)

    def choose(action):
        popup.destroy()
        action()

    buttons = tk.Frame(popup)
    buttons.pack(expand=True)
    add_category_button = tk.Button(
        buttons,
        text="Add New Category",
        command=lambda: choose(add_new_category),
    )
    add_category_button.pack(side="left", padx=5)
    tk.Button(
        buttons,
        text="Add New Option",
        command=lambda: choose(add_new_option),
    ).pack(side="left", padx=5)
    popup.bind("<Escape>", lambda key_event: popup.destroy())
    activate_popup(popup, add_category_button)


def remove_option_state(option_name):
    action_name = option_action_names.pop(option_name, option_name)
    option_widgets.pop(option_name, None)
    all_options.pop(option_name, None)
    custom_option_types.pop(option_name, None)
    custom_option_choices.pop(option_name, None)
    custom_text_values.pop(option_name, None)
    custom_multi_selected.pop(option_name, None)
    if option_name in click_order:
        click_order.remove(option_name)
    if action_name == "NCR":
        ncr_selected.clear()
    elif action_name == "NPR":
        npr_selected.clear()
    elif action_name == "Loyalty":
        loyalty_selected.clear()
    elif action_name == "Lottery":
        lottery_selected.clear()
    elif action_name == "Bill Of Lading [1]":
        bol1_value.set("")
    elif action_name == "Bill Of Lading [2]":
        bol2_value.set("")
    elif action_name == "Bill Of Lading [3]":
        bol3_value.set("")


def remove_category(category_name):
    if not messagebox.askyesno(
        "Remove Category",
        f"Remove the '{category_name}' category and all its options?",
        parent=root,
    ):
        return

    new_custom_categories = {
        name: list(option_names)
        for name, option_names in custom_categories.items()
        if name != category_name
    }
    new_custom_options = {
        name: list(option_names)
        for name, option_names in custom_options.items()
        if name != category_name
    }
    removed_options = list(category_options[category_name])
    new_option_types = {
        name: option_type
        for name, option_type in custom_option_types.items()
        if name not in removed_options
    }
    new_option_choices = {
        name: list(choices)
        for name, choices in custom_option_choices.items()
        if name not in removed_options
    }
    new_category_order = [
        name for name in category_options if name != category_name
    ]
    new_option_order = {
        name: list(option_names)
        for name, option_names in category_options.items()
        if name != category_name
    }
    new_hidden_categories = set(hidden_categories)
    action_name = category_action_names.get(category_name, category_name)
    if action_name in default_category_options:
        new_hidden_categories.add(action_name)
    if not save_customizations(
        new_custom_categories,
        new_custom_options,
        new_hidden_categories,
        hidden_options,
        saved_category_order=new_category_order,
        saved_option_order=new_option_order,
        saved_option_types=new_option_types,
        saved_option_choices=new_option_choices,
    ):
        return

    hidden_categories.clear()
    hidden_categories.update(new_hidden_categories)
    custom_categories.clear()
    custom_categories.update(new_custom_categories)
    custom_options.clear()
    custom_options.update(new_custom_options)
    options_notebook.forget(category_frames[category_name])
    category_frames.pop(category_name).destroy()
    category_options.pop(category_name)
    category_action_names.pop(category_name, None)
    for option_name in removed_options:
        remove_option_state(option_name)
    update_result()


def remove_option(category_name, option_name):
    if not messagebox.askyesno(
        "Remove Option",
        f"Remove '{option_name}' from '{category_name}'?",
        parent=root,
    ):
        return

    new_custom_options = {
        name: list(option_names)
        for name, option_names in custom_options.items()
    }
    new_option_types = dict(custom_option_types)
    new_option_types.pop(option_name, None)
    new_option_choices = {
        name: list(choices)
        for name, choices in custom_option_choices.items()
        if name != option_name
    }
    new_hidden_options = set(hidden_options)
    action_name = option_action_names.get(option_name, option_name)
    new_option_order = {
        name: [
            current for current in option_names
            if current != option_name
        ] if name == category_name else list(option_names)
        for name, option_names in category_options.items()
    }
    if option_name in new_custom_options.get(category_name, []):
        new_custom_options[category_name].remove(option_name)
        if not new_custom_options[category_name]:
            new_custom_options.pop(category_name)
    else:
        new_hidden_options.add(action_name)
    if not save_customizations(
        custom_categories,
        new_custom_options,
        hidden_categories,
        new_hidden_options,
        saved_option_order=new_option_order,
        saved_option_types=new_option_types,
        saved_option_choices=new_option_choices,
    ):
        return

    custom_options.clear()
    custom_options.update(new_custom_options)
    hidden_options.clear()
    hidden_options.update(new_hidden_options)
    category_options[category_name].remove(option_name)
    for widget in category_frames[category_name].winfo_children():
        if widget.cget("text") == option_name:
            widget.destroy()
            break
    remove_option_state(option_name)
    update_result()


def choose_category_to_remove():
    if not category_frames:
        messagebox.showinfo("Remove Category", "There are no categories to remove.", parent=root)
        return

    popup = tk.Toplevel(root)
    popup.title("Remove Category")
    popup.geometry("300x120")
    popup.transient(root)
    tk.Label(popup, text="Choose a category to remove:").pack(padx=10, pady=(12, 4))
    category_choice = ttk.Combobox(
        popup,
        values=list(category_frames),
        state="readonly",
    )
    category_choice.pack(fill="x", padx=10)
    category_choice.current(0)

    def confirm(event=None):
        category_name = category_choice.get()
        popup.destroy()
        remove_category(category_name)

    buttons = tk.Frame(popup)
    buttons.pack(pady=10)
    tk.Button(buttons, text="Remove", width=10, command=confirm).pack(side="left", padx=5)
    tk.Button(buttons, text="Cancel", width=10, command=popup.destroy).pack(side="left", padx=5)
    popup.bind("<Return>", confirm)
    popup.bind("<Escape>", lambda event: popup.destroy())
    activate_popup(popup, category_choice)


def choose_option_to_remove():
    available_categories = [
        name for name, option_names in category_options.items() if option_names
    ]
    if not available_categories:
        messagebox.showinfo("Remove Option", "There are no options to remove.", parent=root)
        return

    popup = tk.Toplevel(root)
    popup.title("Remove Option")
    popup.geometry("300x180")
    popup.transient(root)
    tk.Label(popup, text="Choose a category and option to remove:").pack(
        anchor="w",
        padx=10,
        pady=(10, 4),
    )
    category_choice = ttk.Combobox(
        popup,
        values=available_categories,
        state="readonly",
    )
    category_choice.pack(fill="x", padx=10)
    category_choice.current(0)
    option_choice = ttk.Combobox(popup, state="readonly")
    option_choice.pack(fill="x", padx=10, pady=(8, 0))

    def update_option_choices(event=None):
        option_choice["values"] = category_options[category_choice.get()]
        option_choice.current(0)

    category_choice.bind("<<ComboboxSelected>>", update_option_choices)
    update_option_choices()

    def confirm(event=None):
        category_name = category_choice.get()
        option_name = option_choice.get()
        popup.destroy()
        remove_option(category_name, option_name)

    buttons = tk.Frame(popup)
    buttons.pack(pady=10)
    tk.Button(buttons, text="Remove", width=10, command=confirm).pack(side="left", padx=5)
    tk.Button(buttons, text="Cancel", width=10, command=popup.destroy).pack(side="left", padx=5)
    popup.bind("<Return>", confirm)
    popup.bind("<Escape>", lambda event: popup.destroy())
    activate_popup(popup, category_choice)


def show_remove_choices(event=None):
    if event is not None and event.widget.winfo_toplevel() is not root:
        return

    popup = tk.Toplevel(root)
    popup.title("Remove")
    popup.geometry("280x90")
    popup.transient(root)

    def choose(action):
        popup.destroy()
        action()

    buttons = tk.Frame(popup)
    buttons.pack(expand=True)
    remove_category_button = tk.Button(
        buttons,
        text="Remove Category",
        command=lambda: choose(choose_category_to_remove),
    )
    remove_category_button.pack(side="left", padx=5)
    tk.Button(
        buttons,
        text="Remove Option",
        command=lambda: choose(choose_option_to_remove),
    ).pack(side="left", padx=5)
    popup.bind("<Escape>", lambda key_event: popup.destroy())
    activate_popup(popup, remove_category_button)


def rename_category(category_name, new_name):
    new_name = new_name.strip()
    if not new_name:
        messagebox.showwarning("Invalid Category", "Category name cannot be empty.", parent=root)
        return
    if any(name.casefold() == new_name.casefold() for name in category_frames if name != category_name):
        messagebox.showwarning("Duplicate Category", "That category already exists.", parent=root)
        return

    action_name = category_action_names.get(category_name, category_name)
    allowed_category_names = {
        action_name.casefold(),
        category_labels.get(action_name, action_name).casefold(),
    }
    reserved_categories = {
        name.casefold()
        for name in (*default_category_options, *category_labels.values())
        if name.casefold() not in allowed_category_names
    }
    if new_name.casefold() in reserved_categories:
        messagebox.showwarning("Duplicate Category", "That category name is reserved.", parent=root)
        return
    new_categories = dict(custom_categories)
    new_options = {
        name: list(option_names)
        for name, option_names in custom_options.items()
    }
    new_category_labels = dict(category_labels)
    new_category_order = [new_name if name == category_name else name for name in category_options]
    new_option_order = {
        (new_name if name == category_name else name): list(option_names)
        for name, option_names in category_options.items()
    }
    if category_name in new_categories:
        new_categories[new_name] = new_categories.pop(category_name)
    if category_name in new_options:
        new_options[new_name] = new_options.pop(category_name)
    if action_name in default_category_options:
        new_category_labels[action_name] = new_name
    if not save_customizations(
        new_categories,
        new_options,
        saved_category_labels=new_category_labels,
        saved_category_order=new_category_order,
        saved_option_order=new_option_order,
    ):
        return

    renamed_category_options = {
        (new_name if name == category_name else name): option_names
        for name, option_names in category_options.items()
    }
    renamed_category_frames = {
        (new_name if name == category_name else name): frame
        for name, frame in category_frames.items()
    }
    renamed_category_actions = {
        (new_name if name == category_name else name): action
        for name, action in category_action_names.items()
    }
    category_options.clear()
    category_options.update(renamed_category_options)
    category_frames.clear()
    category_frames.update(renamed_category_frames)
    category_action_names.clear()
    category_action_names.update(renamed_category_actions)
    custom_categories.clear()
    custom_categories.update(new_categories)
    custom_options.clear()
    custom_options.update(new_options)
    category_labels.clear()
    category_labels.update(new_category_labels)
    options_notebook.tab(category_frames[new_name], text=new_name)


def rename_option(category_name, option_name, new_name):
    new_name = new_name.strip()
    if not new_name:
        messagebox.showwarning("Invalid Option", "Option name cannot be empty.", parent=root)
        return
    if any(name.casefold() == new_name.casefold() for name in all_options if name != option_name):
        messagebox.showwarning("Duplicate Option", "That option already exists.", parent=root)
        return
    if new_name.casefold() == "timestamp":
        messagebox.showwarning("Reserved Option", "Timestamp is a reserved option name.", parent=root)
        return

    action_name = option_action_names.get(option_name, option_name)
    reserved_options = {
        name.casefold()
        for option_names in default_category_options.values()
        for name in option_names
    }
    reserved_options.update(name.casefold() for name in option_labels.values())
    allowed_option_names = {
        action_name.casefold(),
        option_labels.get(action_name, action_name).casefold(),
    }
    if (
        new_name.casefold() in reserved_options
        and new_name.casefold() not in allowed_option_names
    ):
        messagebox.showwarning("Reserved Option", "That option name is reserved.", parent=root)
        return
    new_categories = {
        name: list(option_names)
        for name, option_names in custom_categories.items()
    }
    new_options = {
        name: list(option_names)
        for name, option_names in custom_options.items()
    }
    new_option_labels = dict(option_labels)
    new_option_names = [
        new_name if name == option_name else name
        for name in category_options[category_name]
    ]
    new_option_order = {
        name: (
            new_option_names
            if name == category_name
            else list(option_names)
        )
        for name, option_names in category_options.items()
    }
    new_option_types = dict(custom_option_types)
    if option_name in new_option_types:
        new_option_types[new_name] = new_option_types.pop(option_name)
    new_option_choices = {
        name: list(choices)
        for name, choices in custom_option_choices.items()
    }
    if option_name in new_option_choices:
        new_option_choices[new_name] = new_option_choices.pop(option_name)
    if option_name in new_options.get(category_name, []):
        new_options[category_name] = [
            new_name if name == option_name else name
            for name in new_options[category_name]
        ]
    if action_name in {
        name
        for option_names in default_category_options.values()
        for name in option_names
    }:
        new_option_labels[action_name] = new_name
    if not save_customizations(
        new_categories,
        new_options,
        saved_option_labels=new_option_labels,
        saved_option_order=new_option_order,
        saved_option_types=new_option_types,
        saved_option_choices=new_option_choices,
    ):
        return

    category_options[category_name] = new_option_names
    if option_name in custom_options.get(category_name, []):
        custom_options[category_name] = new_options[category_name]
    custom_option_types.clear()
    custom_option_types.update(new_option_types)
    custom_option_choices.clear()
    custom_option_choices.update(new_option_choices)
    option_labels.clear()
    option_labels.update(new_option_labels)
    option_action_names[new_name] = option_action_names.pop(option_name, option_name)
    all_options[new_name] = all_options.pop(option_name)
    if option_name in custom_text_values:
        custom_text_values[new_name] = custom_text_values.pop(option_name)
    if option_name in custom_multi_selected:
        custom_multi_selected[new_name] = custom_multi_selected.pop(option_name)
    if option_name in click_order:
        click_order[click_order.index(option_name)] = new_name
    option_widget = option_widgets.pop(option_name)
    option_widget.configure(text=new_name)
    option_widgets[new_name] = option_widget
    update_result()


def open_rename_option_dialog():
    categories_with_options = [
        name for name, option_names in category_options.items() if option_names
    ]
    if not categories_with_options:
        messagebox.showinfo("Rename Option", "There are no options to rename.", parent=root)
        return

    popup = tk.Toplevel(root)
    popup.title("Rename Option")
    popup.geometry("320x190")
    popup.transient(root)
    tk.Label(popup, text="Category:").pack(anchor="w", padx=10, pady=(10, 2))
    category_choice = ttk.Combobox(
        popup,
        values=categories_with_options,
        state="readonly",
    )
    category_choice.pack(fill="x", padx=10)
    category_choice.current(0)
    tk.Label(popup, text="Option:").pack(anchor="w", padx=10, pady=(6, 2))
    option_choice = ttk.Combobox(popup, state="readonly")
    option_choice.pack(fill="x", padx=10)
    tk.Label(popup, text="New name:").pack(anchor="w", padx=10, pady=(6, 2))
    name_entry = tk.Entry(popup)
    name_entry.pack(fill="x", padx=10)

    def update_options(event=None):
        option_choice["values"] = category_options[category_choice.get()]
        option_choice.current(0)

    category_choice.bind("<<ComboboxSelected>>", update_options)
    update_options()

    def confirm(event=None):
        selected_category = category_choice.get()
        selected_option = option_choice.get()
        popup.destroy()
        rename_option(selected_category, selected_option, name_entry.get())

    buttons = tk.Frame(popup)
    buttons.pack(pady=8)
    tk.Button(buttons, text="Rename", width=10, command=confirm).pack(side="left", padx=5)
    tk.Button(buttons, text="Cancel", width=10, command=popup.destroy).pack(side="left", padx=5)
    popup.bind("<Return>", confirm)
    popup.bind("<Escape>", lambda event: popup.destroy())
    activate_popup(popup, name_entry)


def open_rename_category_dialog():
    if not category_options:
        messagebox.showinfo("Rename Category", "There are no categories to rename.", parent=root)
        return

    popup = tk.Toplevel(root)
    popup.title("Rename Category")
    popup.geometry("300x170")
    popup.transient(root)
    tk.Label(popup, text="Category:").pack(anchor="w", padx=10, pady=(10, 2))
    category_choice = ttk.Combobox(
        popup,
        values=list(category_options),
        state="readonly",
    )
    category_choice.pack(fill="x", padx=10)
    category_choice.current(0)
    tk.Label(popup, text="New name:").pack(anchor="w", padx=10, pady=(6, 2))
    name_entry = tk.Entry(popup)
    name_entry.pack(fill="x", padx=10)

    def confirm(event=None):
        selected_category = category_choice.get()
        new_name = name_entry.get()
        popup.destroy()
        rename_category(selected_category, new_name)

    buttons = tk.Frame(popup)
    buttons.pack(pady=8)
    tk.Button(buttons, text="Rename", width=10, command=confirm).pack(side="left", padx=5)
    tk.Button(buttons, text="Cancel", width=10, command=popup.destroy).pack(side="left", padx=5)
    popup.bind("<Return>", confirm)
    popup.bind("<Escape>", lambda event: popup.destroy())
    activate_popup(popup, name_entry)


def open_reorder_dialog(title, item_names, on_reorder):
    popup = tk.Toplevel(root)
    popup.title(title)
    popup.geometry("300x300")
    popup.transient(root)
    listbox = tk.Listbox(popup, exportselection=False)
    listbox.pack(fill="both", expand=True, padx=10, pady=(10, 5))
    for name in item_names:
        listbox.insert(tk.END, name)
    if item_names:
        listbox.selection_set(0)

    def move_selected(offset):
        selection = listbox.curselection()
        if not selection:
            return
        old_index = selection[0]
        new_index = old_index + offset
        if not 0 <= new_index < listbox.size():
            return
        item = listbox.get(old_index)
        listbox.delete(old_index)
        listbox.insert(new_index, item)
        listbox.selection_set(new_index)
        listbox.activate(new_index)

    controls = tk.Frame(popup)
    controls.pack(pady=5)
    tk.Button(controls, text="Move Up", command=lambda: move_selected(-1)).pack(
        side="left",
        padx=5,
    )
    tk.Button(controls, text="Move Down", command=lambda: move_selected(1)).pack(
        side="left",
        padx=5,
    )

    def confirm(event=None):
        on_reorder(listbox.get(0, tk.END))
        popup.destroy()

    tk.Button(popup, text="Save Order", command=confirm).pack(pady=(0, 10))
    popup.bind("<Return>", confirm)
    popup.bind("<Escape>", lambda event: popup.destroy())
    activate_popup(popup, listbox)


def reorder_categories(new_order):
    new_option_order = {
        name: list(category_options[name])
        for name in new_order
    }
    if not save_customizations(
        custom_categories,
        custom_options,
        saved_category_order=new_order,
        saved_option_order=new_option_order,
    ):
        return
    reordered_options = {name: category_options[name] for name in new_order}
    reordered_frames = {name: category_frames[name] for name in new_order}
    category_options.clear()
    category_options.update(reordered_options)
    category_frames.clear()
    category_frames.update(reordered_frames)
    for index, name in enumerate(new_order):
        options_notebook.insert(index, category_frames[name])


def reorder_options(category_name, new_order):
    new_option_order = {
        name: (new_order if name == category_name else list(option_names))
        for name, option_names in category_options.items()
    }
    if not save_customizations(
        custom_categories,
        custom_options,
        saved_option_order=new_option_order,
    ):
        return
    category_options[category_name] = list(new_order)
    for option_name in new_order:
        option_widgets[option_name].pack_forget()
    for option_name in new_order:
        option_widgets[option_name].pack(anchor="w")


def open_reorder_options_dialog():
    if not category_options:
        messagebox.showinfo("Reorder Options", "There are no categories.", parent=root)
        return

    popup = tk.Toplevel(root)
    popup.title("Choose Category")
    popup.geometry("300x120")
    popup.transient(root)
    tk.Label(popup, text="Choose a category whose options to reorder:").pack(
        padx=10,
        pady=(12, 4),
    )
    category_choice = ttk.Combobox(
        popup,
        values=list(category_options),
        state="readonly",
    )
    category_choice.pack(fill="x", padx=10)
    category_choice.current(0)

    def confirm(event=None):
        category_name = category_choice.get()
        popup.destroy()
        open_reorder_dialog(
            "Reorder Options",
            category_options[category_name],
            lambda order: reorder_options(category_name, order),
        )

    buttons = tk.Frame(popup)
    buttons.pack(pady=8)
    tk.Button(buttons, text="Continue", width=10, command=confirm).pack(side="left", padx=5)
    tk.Button(buttons, text="Cancel", width=10, command=popup.destroy).pack(side="left", padx=5)
    popup.bind("<Return>", confirm)
    popup.bind("<Escape>", lambda event: popup.destroy())
    activate_popup(popup, category_choice)


def show_organize_choices(event=None):
    if event is not None and event.widget.winfo_toplevel() is not root:
        return

    popup = tk.Toplevel(root)
    popup.title("Input Logger Tool")
    popup.geometry("300x130")
    popup.transient(root)

    def choose(action):
        popup.destroy()
        action()

    buttons = tk.Frame(popup)
    buttons.pack(fill="both", expand=True, padx=8, pady=8)
    buttons.grid_columnconfigure((0, 1), weight=1, uniform="organize")
    rename_category_button = tk.Button(
        buttons,
        text="Rename Category",
        command=lambda: choose(open_rename_category_dialog),
    )
    rename_category_button.grid(row=0, column=0, sticky="ew", padx=4, pady=4)
    tk.Button(
        buttons,
        text="Rename Option",
        command=lambda: choose(open_rename_option_dialog),
    ).grid(row=0, column=1, sticky="ew", padx=4, pady=4)
    tk.Button(
        buttons,
        text="Reorder Tabs",
        command=lambda: choose(
            lambda: open_reorder_dialog(
                "Reorder Tabs",
                list(category_options),
                reorder_categories,
            )
        ),
    ).grid(row=1, column=0, sticky="ew", padx=4, pady=4)
    tk.Button(
        buttons,
        text="Reorder Options",
        command=lambda: choose(open_reorder_options_dialog),
    ).grid(row=1, column=1, sticky="ew", padx=4, pady=4)
    popup.bind("<Escape>", lambda key_event: popup.destroy())
    activate_popup(popup, rename_category_button)


def toggle_timestamp(event=None):
    if event is not None and event.widget.winfo_toplevel() is not root:
        return
    all_options["Timestamp"].set(not all_options["Timestamp"].get())
    on_checkbox_toggle("Timestamp")
    return "break"


def navigate_tabs(event):
    if event.widget.winfo_toplevel() is not root:
        return
    if event.widget.winfo_class() in ("Entry", "Text", "TEntry", "TCombobox"):
        return

    tabs = options_notebook.tabs()
    if not tabs:
        return "break"

    current_index = options_notebook.index(options_notebook.select())
    if event.keysym.lower() in ("a", "left"):
        options_notebook.select(tabs[max(0, current_index - 1)])
    elif event.keysym.lower() in ("d", "right"):
        options_notebook.select(tabs[min(len(tabs) - 1, current_index + 1)])
    return "break"


# ---------------------------
# Popups Logic
# ---------------------------

def open_bol_popup(bol_name, bol_var):
    popup = tk.Toplevel(root)
    popup.title(f"Enter {bol_name}")
    popup.geometry("250x120")
    popup.transient(root)
    tk.Label(popup, text=f"Enter {bol_name} value:").pack(pady=5)
    entry = tk.Entry(popup, textvariable=bol_var)
    entry.pack(pady=5)
    def confirm(event=None):
        popup.destroy()
        update_result()

    def cancel_esc(event=None):
        all_options[bol_name].set(False)
        if bol_name in click_order: click_order.remove(bol_name)
        bol_var.set("") 
        popup.destroy()
        update_result()

    tk.Button(popup, text="Confirm", command=confirm).pack(pady=5)
    popup.bind('<Return>', confirm)
    popup.bind('<Escape>', cancel_esc)
    activate_popup(popup, entry)


def open_custom_text_popup(option_name):
    popup = tk.Toplevel(root)
    popup.title(f"Enter {option_name}")
    popup.geometry("280x130")
    popup.transient(root)
    tk.Label(popup, text=f"Enter {option_name} value:").pack(pady=5)
    entry = tk.Entry(popup, textvariable=custom_text_values[option_name])
    entry.pack(fill="x", padx=12, pady=5)

    def confirm(event=None):
        popup.destroy()
        update_result()

    def cancel(event=None):
        all_options[option_name].set(False)
        if option_name in click_order:
            click_order.remove(option_name)
        custom_text_values[option_name].set("")
        popup.destroy()
        update_result()

    tk.Button(popup, text="Confirm", command=confirm).pack(pady=5)
    popup.bind("<Return>", confirm)
    popup.bind("<Escape>", cancel)
    activate_popup(popup, entry)


def open_multi_checkbox_popup(name, options_list, selected_list):
    popup = tk.Toplevel(root)
    popup.title(f"Select {name}")
    popup.geometry(f"250x{min(240, max(125, 70 + len(options_list) * 28))}")
    popup.transient(root)
    vars, widgets = [], []
    for opt in options_list:
        var = tk.BooleanVar(value=(opt in selected_list))
        cb = ttk.Checkbutton(
            popup,
            text=opt,
            variable=var,
            style="MultiChoice.TCheckbutton",
        )
        cb.pack(anchor="w", padx=12, pady=1)
        vars.append((opt, var))
        widgets.append(cb)

    def focus_next(event): event.widget.tk_focusNext().focus(); return "break"
    def focus_prev(event): event.widget.tk_focusPrev().focus(); return "break"
    def toggle_space(event): event.widget.toggle(); return "break"

    def set_choice(event, choice_var, selected):
        choice_var.set(selected)
        return "break"

    for cb, (_, choice_var) in zip(widgets, vars):
        cb.bind("<Down>", focus_next)
        cb.bind("<Up>", focus_prev)
        cb.bind("<space>", toggle_space)
        cb.bind(
            "<Left>",
            lambda event, var=choice_var: set_choice(event, var, True),
        )
        cb.bind(
            "<Right>",
            lambda event, var=choice_var: set_choice(event, var, False),
        )

    def confirm(event=None):
        selected_list.clear()
        for opt, var in vars:
            if var.get(): selected_list.append(opt)
        popup.destroy()
        update_result()

    def cancel_esc(event=None):
        all_options[name].set(False)
        if name in click_order: click_order.remove(name)
        selected_list.clear()
        popup.destroy()
        update_result()

    btn = tk.Button(popup, text="Confirm", command=confirm)
    btn.pack(pady=(6, 8))
    btn.bind("<Up>", focus_prev)
    popup.bind('<Return>', confirm)
    popup.bind('<Escape>', cancel_esc)
    activate_popup(popup, widgets[0] if widgets else btn)

# ---------------------------
# UI Construction
# ---------------------------

root = tk.Tk()
root.title("Input Logger Tool")
root.geometry("360x750")
root.resizable(True, True)
root.configure(background=COLORS["background"])
root.iconbitmap(ICON_FILE)
root.iconbitmap(default=ICON_FILE)

root.option_add("*Font", ("Segoe UI", 10))
root.option_add("*Label.background", COLORS["background"])
root.option_add("*Label.foreground", COLORS["text"])
root.option_add("*Button.font", ("Segoe UI", 9, "bold"))
root.option_add("*Button.background", COLORS["surface_alt"])
root.option_add("*Button.foreground", COLORS["text"])
root.option_add("*Button.activeBackground", "#DCE7F5")
root.option_add("*Button.activeForeground", COLORS["text"])
root.option_add("*Button.borderWidth", 0)
root.option_add("*Frame.background", COLORS["background"])
root.option_add("*Checkbutton.background", COLORS["surface"])
root.option_add("*Checkbutton.foreground", COLORS["text"])
root.option_add("*Checkbutton.activeBackground", COLORS["surface"])
root.option_add("*Checkbutton.activeForeground", COLORS["text"])
root.option_add("*Entry.background", COLORS["surface"])
root.option_add("*Entry.foreground", COLORS["text"])
root.option_add("*Entry.insertBackground", COLORS["text"])
root.option_add("*Entry.relief", "flat")

style = ttk.Style(root)
style.theme_use("clam")


def apply_theme_styles():
    root.configure(background=COLORS["background"])
    root.option_add("*Label.background", COLORS["background"])
    root.option_add("*Label.foreground", COLORS["text"])
    root.option_add("*Button.background", COLORS["surface_alt"])
    root.option_add("*Button.foreground", COLORS["text"])
    root.option_add("*Button.activeBackground", COLORS["surface"])
    root.option_add("*Button.activeForeground", COLORS["text"])
    root.option_add("*Frame.background", COLORS["background"])
    root.option_add("*Checkbutton.background", COLORS["surface"])
    root.option_add("*Checkbutton.foreground", COLORS["text"])
    root.option_add("*Checkbutton.activeBackground", COLORS["surface"])
    root.option_add("*Checkbutton.activeForeground", COLORS["text"])
    root.option_add("*Entry.background", COLORS["surface"])
    root.option_add("*Entry.foreground", COLORS["text"])
    root.option_add("*Entry.insertBackground", COLORS["text"])

    style.configure("TFrame", background=COLORS["background"])
    style.configure("TLabel", background=COLORS["background"], foreground=COLORS["text"])
    style.configure("Header.TFrame", background=COLORS["text"])
    style.configure(
        "HeaderTitle.TLabel",
        background=COLORS["text"],
        foreground=COLORS["surface"],
        font=("Segoe UI", 17, "bold"),
    )
    style.configure(
        "HeaderSubtitle.TLabel",
        background=COLORS["text"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 9),
    )
    style.configure(
        "TNotebook",
        background=COLORS["background"],
        borderwidth=0,
        tabmargins=(0, 0, 0, 0),
    )
    style.configure(
        "TNotebook.Tab",
        background=COLORS["surface_alt"],
        foreground=COLORS["muted"],
        padding=(10, 5),
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TNotebook.Tab",
        background=[("selected", COLORS["surface"])],
        foreground=[("selected", COLORS["accent"])],
        padding=[("selected", (10, 5)), ("!selected", (10, 5))],
        borderwidth=[("selected", 0), ("!selected", 0)],
    )
    style.configure(
        "TCheckbutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        padding=(4, 3),
    )
    style.map(
        "TCheckbutton",
        foreground=[("active", COLORS["accent"])],
        background=[("active", COLORS["surface"])],
    )
    style.configure(
        "MultiChoice.TCheckbutton",
        background=COLORS["surface"],
        foreground=COLORS["text"],
        padding=(4, 3),
    )
    style.map(
        "MultiChoice.TCheckbutton",
        foreground=[("active", COLORS["accent"])],
        background=[("active", COLORS["surface"])],
        indicatorcolor=[
            ("selected", COLORS["accent"]),
            ("!selected", COLORS["border"]),
        ],
    )
    style.configure(
        "TLabelframe",
        background=COLORS["surface"],
        bordercolor=COLORS["border"],
        relief="solid",
    )
    style.configure(
        "TLabelframe.Label",
        background=COLORS["surface"],
        foreground=COLORS["muted"],
        font=("Segoe UI", 9, "bold"),
    )
    style.configure(
        "TButton",
        background=COLORS["surface_alt"],
        foreground=COLORS["text"],
        padding=(14, 8),
        borderwidth=0,
        font=("Segoe UI", 9, "bold"),
    )
    style.map(
        "TButton",
        background=[
            ("active", COLORS["surface"]),
            ("pressed", COLORS["border"]),
        ],
        foreground=[("active", COLORS["text"])],
    )
    style.configure(
        "Accent.TButton",
        background=COLORS["accent"],
        foreground="#FFFFFF",
    )
    style.map(
        "Accent.TButton",
        background=[
            ("active", COLORS["accent_active"]),
            ("pressed", COLORS["accent_active"]),
        ],
        foreground=[("active", "#FFFFFF")],
    )
    style.configure(
        "TCombobox",
        fieldbackground=COLORS["surface"],
        background=COLORS["surface"],
        foreground=COLORS["text"],
        padding=5,
    )
    style.map(
        "TCombobox",
        fieldbackground=[("readonly", COLORS["surface"])],
        foreground=[("readonly", COLORS["text"])],
    )
    style.configure(
        "TEntry",
        fieldbackground=COLORS["surface"],
        foreground=COLORS["text"],
        padding=5,
    )


apply_theme_styles()


def apply_theme():
    COLORS.clear()
    COLORS.update(DARK_COLORS if dark_mode_enabled else LIGHT_COLORS)
    apply_theme_styles()
    for frame in category_frames.values():
        frame.configure(background=COLORS["surface"])
    if "result_frame" in globals():
        result_frame.configure(background=COLORS["background"])
        btn_frame.configure(background=COLORS["background"])
    if "result" in globals():
        result.configure(
            bg=COLORS["surface"],
            fg=COLORS["text"],
            insertbackground=COLORS["text"],
            highlightbackground=COLORS["border"],
            highlightcolor=COLORS["accent"],
        )


def toggle_dark_mode():
    global dark_mode_enabled
    dark_mode_enabled = dark_mode_var.get()
    apply_theme()
    if not save_customizations(custom_categories, custom_options):
        dark_mode_enabled = not dark_mode_enabled
        dark_mode_var.set(dark_mode_enabled)
        apply_theme()

options_notebook = ttk.Notebook(root, height=0)
options_notebook.pack(fill="both", expand=True, padx=16, pady=(8, 8))
timestamp_frame = ttk.LabelFrame(
    root,
    text="  Additional Options  ",
    padding=(12, 8),
)
timestamp_frame.pack(fill="x", padx=16, pady=6)

default_category_options = {
    "Crunchtime": ["Bill Of Lading [1]", "Bill Of Lading [2]", "Bill Of Lading [3]", "Veeder Root", "Payout", "Coupon", "Lottery", "Titan Series", "Change Order"],
    "CNG": ["EMR", "NCR", "NPR", "Loyalty", "Drive Off", "Pop Discount", "Adjusted Fuel Deposit"],
}
category_options = {
    name: list(option_names)
    for name, option_names in default_category_options.items()
}
additional_options = ["Timestamp"]

all_options = {}
dark_mode_var = tk.BooleanVar(value=dark_mode_enabled)
bol1_value, bol2_value, bol3_value = tk.StringVar(), tk.StringVar(), tk.StringVar()
ncr_selected, npr_selected, loyalty_selected, lottery_selected = [], [], [], []
category_frames = {}
option_widgets = {}
custom_categories = {}
custom_options = {}
hidden_categories = set()
hidden_options = set()
category_labels = {}
option_labels = {}

customization_path = os.path.join(
    os.environ.get("APPDATA", os.path.expanduser("~")),
    "TechHub Input Logger Tool",
    "customizations.json",
)
try:
    with open(customization_path, "r", encoding="utf-8") as config_file:
        saved_customizations = json.load(config_file)
    if not isinstance(saved_customizations, dict):
        raise ValueError("Customization file must contain a JSON object.")

    saved_categories = saved_customizations.get("categories", {})
    saved_options = saved_customizations.get("options", {})
    saved_removed_categories = saved_customizations.get("removed_categories", [])
    saved_removed_options = saved_customizations.get("removed_options", [])
    saved_category_labels = saved_customizations.get("category_labels", {})
    saved_option_labels = saved_customizations.get("option_labels", {})
    saved_category_order = saved_customizations.get("category_order")
    saved_option_order = saved_customizations.get("option_order")
    saved_dark_mode = saved_customizations.get("dark_mode", False)
    saved_option_types = saved_customizations.get("option_types", {})
    saved_option_choices = saved_customizations.get("option_choices", {})
    if (
        not isinstance(saved_categories, dict)
        or not isinstance(saved_options, dict)
        or not isinstance(saved_dark_mode, bool)
        or not isinstance(saved_option_types, dict)
        or any(
            not isinstance(name, str)
            or option_type not in ("checkbox", "text", "multi")
            for name, option_type in saved_option_types.items()
        )
        or not isinstance(saved_option_choices, dict)
        or any(
            not isinstance(name, str)
            or not isinstance(choices, list)
            or any(not isinstance(choice, str) or not choice.strip() for choice in choices)
            or len({choice.casefold() for choice in choices}) != len(choices)
            for name, choices in saved_option_choices.items()
        )
        or not isinstance(saved_category_labels, dict)
        or any(
            not isinstance(old, str)
            or not isinstance(new, str)
            or not old.strip()
            or not new.strip()
            for old, new in saved_category_labels.items()
        )
        or not isinstance(saved_option_labels, dict)
        or any(
            not isinstance(old, str)
            or not isinstance(new, str)
            or not old.strip()
            or not new.strip()
            for old, new in saved_option_labels.items()
        )
        or not isinstance(saved_removed_categories, list)
        or any(not isinstance(name, str) or not name.strip() for name in saved_removed_categories)
        or not isinstance(saved_removed_options, list)
        or any(not isinstance(name, str) or not name.strip() for name in saved_removed_options)
        or (
            saved_category_order is not None
            and (
                not isinstance(saved_category_order, list)
                or any(not isinstance(name, str) for name in saved_category_order)
            )
        )
        or (saved_option_order is not None and not isinstance(saved_option_order, dict))
    ):
        raise ValueError("Customization categories and options must be JSON objects.")

    category_labels.update(saved_category_labels)
    option_labels.update(saved_option_labels)
    hidden_categories.update(saved_removed_categories)
    hidden_options.update(saved_removed_options)
    category_options = {}
    loaded_category_names = set()
    loaded_option_names = set()
    for original_category, original_options in default_category_options.items():
        if original_category in hidden_categories:
            continue
        category_name = category_labels.get(original_category, original_category)
        if category_name.casefold() in loaded_category_names:
            raise ValueError("Customization file contains duplicate category names.")
        loaded_category_names.add(category_name.casefold())
        category_action_names[category_name] = original_category
        visible_options = []
        for original_option in original_options:
            if original_option in hidden_options:
                continue
            option_name = option_labels.get(original_option, original_option)
            if option_name.casefold() in loaded_option_names:
                raise ValueError("Customization file contains duplicate option names.")
            loaded_option_names.add(option_name.casefold())
            option_action_names[option_name] = original_option
            visible_options.append(option_name)
        category_options[category_name] = visible_options
    used_category_names = {
        name.casefold()
        for name in (
            list(default_category_options)
            + list(category_labels.values())
        )
    }
    used_option_names = {
        name.casefold()
        for option_names in default_category_options.values()
        for name in option_names
    }
    used_option_names.update(name.casefold() for name in option_labels.values())
    used_option_names.add("timestamp")
    for category_name, option_names in saved_categories.items():
        if (
            not isinstance(category_name, str)
            or not category_name.strip()
            or category_name.casefold() in used_category_names
            or not isinstance(option_names, list)
            or any(
                not isinstance(option_name, str)
                or not option_name.strip()
                or option_name.casefold() in used_option_names
                or option_name.casefold() in loaded_option_names
                for option_name in option_names
            )
        ):
            raise ValueError("Customization file contains an invalid or duplicate category.")
        custom_categories[category_name] = option_names
        category_options[category_name] = list(option_names)
        category_action_names[category_name] = category_name
        used_category_names.add(category_name.casefold())
        for option_name in option_names:
            loaded_option_names.add(option_name.casefold())
            option_action_names[option_name] = option_name
            used_option_names.add(option_name.casefold())
    for category_name, option_names in saved_options.items():
        if (
            category_name not in category_options
            or not isinstance(option_names, list)
            or any(
                not isinstance(option_name, str)
                or not option_name.strip()
                or option_name.casefold() in used_option_names
                or option_name.casefold() in loaded_option_names
                for option_name in option_names
            )
        ):
            raise ValueError("Customization file contains an invalid or duplicate option.")
        custom_options[category_name] = list(option_names)
        category_options[category_name].extend(option_names)
        for option_name in option_names:
            loaded_option_names.add(option_name.casefold())
            option_action_names[option_name] = option_name
            used_option_names.add(option_name.casefold())
    custom_option_names = {
        option_name
        for option_names in (*custom_categories.values(), *custom_options.values())
        for option_name in option_names
    }
    if (
        not set(saved_option_types).issubset(custom_option_names)
        or not set(saved_option_choices).issubset(custom_option_names)
        or any(
            saved_option_types.get(name, "checkbox") != "multi"
            for name in saved_option_choices
        )
        or any(
            saved_option_types.get(name) == "multi"
            and not saved_option_choices.get(name)
            for name in saved_option_types
        )
    ):
        raise ValueError("Customization file contains invalid custom option types or choices.")
    custom_option_types.update(saved_option_types)
    custom_option_choices.update(
        {name: list(choices) for name, choices in saved_option_choices.items()}
    )
    if saved_category_order is not None:
        if (
            len(saved_category_order) != len(category_options)
            or set(saved_category_order) != set(category_options)
        ):
            raise ValueError("Customization file contains an invalid category order.")
        category_options = {
            name: category_options[name]
            for name in saved_category_order
        }
    if saved_option_order is not None:
        if set(saved_option_order) != set(category_options):
            raise ValueError("Customization file contains an invalid option order.")
        for category_name, saved_order in saved_option_order.items():
            if (
                not isinstance(saved_order, list)
                or any(not isinstance(name, str) for name in saved_order)
                or len(saved_order) != len(category_options[category_name])
                or set(saved_order) != set(category_options[category_name])
            ):
                raise ValueError("Customization file contains an invalid option order.")
            category_options[category_name] = list(saved_order)
    dark_mode_enabled = saved_dark_mode
except FileNotFoundError:
    pass
except (OSError, json.JSONDecodeError, ValueError) as error:
    messagebox.showerror(
        "Customization Load Failed",
        f"Could not load saved categories and options:\n{error}",
        parent=root,
    )
    custom_categories.clear()
    custom_options.clear()
    hidden_categories.clear()
    hidden_options.clear()
    custom_option_types.clear()
    custom_option_choices.clear()
    category_labels.clear()
    option_labels.clear()
    category_action_names.clear()
    option_action_names.clear()
    category_options = {
        name: list(option_names)
        for name, option_names in default_category_options.items()
    }
    dark_mode_enabled = False
    category_action_names.update(
        {name: name for name in default_category_options}
    )
    for option_names in default_category_options.values():
        option_action_names.update({name: name for name in option_names})

dark_mode_var.set(dark_mode_enabled)
apply_theme()

for option_name, option_type in custom_option_types.items():
    if option_type == "text":
        custom_text_values[option_name] = tk.StringVar()
    elif option_type == "multi":
        custom_multi_selected[option_name] = []

for option_names in category_options.values():
    for name in option_names:
        all_options[name] = tk.BooleanVar()
for name in additional_options:
    all_options[name] = tk.BooleanVar()

for category_name in category_options:
    add_category_tab(category_name)

for name in additional_options:
    ttk.Checkbutton(
        timestamp_frame,
        text=name,
        variable=all_options[name],
        command=lambda n=name: on_checkbox_toggle(n),
    ).pack(side="left")
ttk.Checkbutton(
    timestamp_frame,
    text="Dark Mode",
    variable=dark_mode_var,
    command=toggle_dark_mode,
).pack(side="left", padx=(16, 0))

result_frame = tk.Frame(root, background=COLORS["background"])
result_frame.pack(fill="x", padx=16, pady=(8, 12))
result = tk.Text(
    result_frame,
    height=4,
    width=1,
    state="disabled",
    wrap="word",
    font=("Segoe UI", 10),
    bg=COLORS["surface"],
    fg=COLORS["text"],
    insertbackground=COLORS["text"],
    relief="flat",
    highlightthickness=1,
    highlightbackground=COLORS["border"],
    highlightcolor=COLORS["accent"],
    padx=10,
    pady=9,
)
result.pack(fill="x", pady=(0, 10))
btn_frame = tk.Frame(result_frame, background=COLORS["background"])
btn_frame.pack(anchor="center")
ttk.Button(
    btn_frame,
    text="Copy",
    style="Accent.TButton",
    width=12,
    command=copy_to_clipboard,
).pack(side="left")
ttk.Button(
    btn_frame,
    text="Clear",
    width=12,
    command=clear_all,
).pack(side="left", padx=(8, 0))
ttk.Label(
    result_frame,
    text="Credited to Maal",
    font=("Segoe UI", 8),
    foreground=COLORS["muted"],
).pack(anchor="center", pady=(6, 0))

def refresh_timestamp():
    if all_options["Timestamp"].get(): update_result()
    root.after(60000, refresh_timestamp)

refresh_timestamp()
root.bind('<Delete>', lambda e: clear_all())
root.bind('<Control-c>', copy_to_clipboard)
root.bind_all("<KeyPress-plus>", show_add_choices)
root.bind_all("<KP_Add>", show_add_choices)
root.bind_all("<KeyPress-minus>", show_remove_choices)
root.bind_all("<KP_Subtract>", show_remove_choices)
root.bind_all("<KeyPress-asterisk>", show_organize_choices)
root.bind_all("<KP_Multiply>", show_organize_choices)
root.bind_all("<KeyPress-grave>", toggle_timestamp)
root.bind_all("<KeyPress-a>", navigate_tabs)
root.bind_all("<KeyPress-A>", navigate_tabs)
root.bind_all("<KeyPress-d>", navigate_tabs)
root.bind_all("<KeyPress-D>", navigate_tabs)
root.bind_all("<Left>", navigate_tabs)
root.bind_all("<Right>", navigate_tabs)
root.update_idletasks()
root.minsize(btn_frame.winfo_reqwidth() + 32, root.winfo_reqheight())
>>>>>>> Stashed changes
root.mainloop()