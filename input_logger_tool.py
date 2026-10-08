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

root.mainloop()