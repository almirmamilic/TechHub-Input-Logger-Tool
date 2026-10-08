import tkinter as tk
from datetime import datetime
import sys
import os

# ---------------------------
# Helper for PyInstaller pathing
# ---------------------------
def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ICON_FILE = resource_path("app_icon.ico")

# ---------------------------
# State Management
# ---------------------------
click_order = []

# ---------------------------
# Functions
# ---------------------------

def on_checkbox_toggle(name):
    """Tracks the order of clicks and opens popups"""
    if all_options[name].get():
        if name not in click_order:
            click_order.append(name)
    else:
        if name in click_order:
            click_order.remove(name)
    
    if name == "Bill Of Lading [1]":
        if all_options[name].get(): open_bol_popup(name, bol1_value)
    elif name == "Bill Of Lading [2]":
        if all_options[name].get(): open_bol_popup(name, bol2_value)
    elif name == "Bill Of Lading [3]":
        if all_options[name].get(): open_bol_popup(name, bol3_value)
    elif name == "NCR":
        if all_options[name].get():
            open_multi_checkbox_popup("NCR", ["Fleetwide", "Fuelman", "PumpPass", "ExxonMobilG", "Shell"], ncr_selected)
        else:
            ncr_selected.clear()
    elif name == "NPR":
        if all_options[name].get():
            open_multi_checkbox_popup("NPR", ["E-85", "Diesel", "Racingfuel", "Kerosene"], npr_selected)
        else:
            npr_selected.clear()
    elif name == "Loyalty":
        if all_options[name].get():
            open_multi_checkbox_popup("Loyalty", ["600", "888", "800", "211"], loyalty_selected)
        else:
            loyalty_selected.clear()
    elif name == "Lottery":
        if all_options[name].get():
            open_multi_checkbox_popup("Lottery", ["FL Lottery", "IN Lottery", "IL Lottery"], lottery_selected)
        else:
            lottery_selected.clear()
            
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
        if name == "NCR":
            if ncr_selected:
                selected.append(f"NCR({', '.join(ncr_selected)})")
            else:
                selected.append(name)
        elif name == "NPR":
            if npr_selected:
                selected.append(f"NPR({', '.join(npr_selected)})")
            else:
                selected.append(name)
        elif name == "Loyalty":
            if loyalty_selected:
                selected.append(f"Loyalty({', '.join(loyalty_selected)})")
            else:
                selected.append(name)
        
        # Keeping Lottery as sub-selections only (per previous request)
        elif name == "Lottery":
            if lottery_selected:
                selected.append(", ".join(lottery_selected))
            else:
                selected.append(name)
        
        elif name == "Bill Of Lading [1]":
            val = bol1_value.get().strip()
            selected.append(f"BOL#{val}" if val else "BOL1#")
        elif name == "Bill Of Lading [2]":
            val = bol2_value.get().strip()
            selected.append(f"BOL#{val}" if val else "BOL2#")
        elif name == "Bill Of Lading [3]":
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

# ---------------------------
# Popups Logic
# ---------------------------

def open_bol_popup(bol_name, bol_var):
    popup = tk.Toplevel(root)
    popup.title(f"Enter {bol_name}")
    popup.geometry("250x120")
    try: popup.iconbitmap(ICON_FILE)
    except: pass
    popup.transient(root)
    popup.grab_set()
    tk.Label(popup, text=f"Enter {bol_name} value:").pack(pady=5)
    entry = tk.Entry(popup, textvariable=bol_var)
    entry.pack(pady=5)
    entry.focus_force()

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

def open_multi_checkbox_popup(name, options_list, selected_list):
    popup = tk.Toplevel(root)
    popup.title(f"Select {name}")
    popup.geometry("250x240")
    try: popup.iconbitmap(ICON_FILE)
    except: pass
    popup.transient(root)
    popup.grab_set()
    vars, widgets = [], []
    for opt in options_list:
        var = tk.BooleanVar(value=(opt in selected_list))
        cb = tk.Checkbutton(popup, text=opt, variable=var)
        cb.pack(anchor="w", padx=20)
        vars.append((opt, var))
        widgets.append(cb)

    def focus_next(event): event.widget.tk_focusNext().focus(); return "break"
    def focus_prev(event): event.widget.tk_focusPrev().focus(); return "break"
    def toggle_space(event): event.widget.toggle(); return "break"

    for cb in widgets:
        cb.bind("<Down>", focus_next); cb.bind("<Up>", focus_prev); cb.bind("<space>", toggle_space)

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
    btn.pack(pady=10)
    btn.bind("<Up>", focus_prev)
    if widgets: widgets[0].focus_force()
    popup.bind('<Return>', confirm)
    popup.bind('<Escape>', cancel_esc)

# ---------------------------
# UI Construction
# ---------------------------

root = tk.Tk()
root.title("Input Logger Tool")
root.geometry("320x720") 
try: root.iconbitmap(ICON_FILE)
except: pass

zenput_frame = tk.LabelFrame(root, text="Zenput Options", padx=5, pady=5)
cng_frame = tk.LabelFrame(root, text="CNG Options", padx=5, pady=5)
timestamp_frame = tk.LabelFrame(root, text="Additional Options", padx=5, pady=5)
zenput_frame.pack(fill="both", padx=10, pady=5)
cng_frame.pack(fill="both", padx=10, pady=5)
timestamp_frame.pack(fill="both", padx=10, pady=5)

zenput_options = ["Bill Of Lading [1]", "Bill Of Lading [2]", "Bill Of Lading [3]", "Veeder Root", "Payout", "Coupon", "Lottery", "Titan Series", "Change Order"]
cng_options = ["EMR", "NCR", "NPR", "Loyalty", "Drive Off", "Pop Discount", "Adjusted Fuel Deposit"]
additional_options = ["Timestamp"]

all_options = {}
bol1_value, bol2_value, bol3_value = tk.StringVar(), tk.StringVar(), tk.StringVar()
ncr_selected, npr_selected, loyalty_selected, lottery_selected = [], [], [], []

for name in zenput_options + cng_options + additional_options:
    all_options[name] = tk.BooleanVar()

for name in zenput_options:
    tk.Checkbutton(zenput_frame, text=name, variable=all_options[name], 
                   command=lambda n=name: on_checkbox_toggle(n)).pack(anchor="w")

for name in cng_options:
    tk.Checkbutton(cng_frame, text=name, variable=all_options[name], 
                   command=lambda n=name: on_checkbox_toggle(n)).pack(anchor="w")

for name in additional_options:
    tk.Checkbutton(timestamp_frame, text=name, variable=all_options[name], 
                   command=lambda n=name: on_checkbox_toggle(n)).pack(anchor="w")

result_frame = tk.Frame(root)
result_frame.pack(fill="both", padx=10, pady=10)
result = tk.Text(result_frame, height=5, width=32, state="disabled")
result.pack(pady=5)
btn_frame = tk.Frame(result_frame)
btn_frame.pack()
tk.Button(btn_frame, text="Copy", width=12, command=copy_to_clipboard).pack(side="left", padx=5)
tk.Button(btn_frame, text="Clear", width=12, command=clear_all).pack(side="left", padx=5)

def refresh_timestamp():
    if all_options["Timestamp"].get(): update_result()
    root.after(60000, refresh_timestamp)

refresh_timestamp()
root.bind('<Delete>', lambda e: clear_all())
root.bind('<Control-c>', copy_to_clipboard)
tk.Label(root, text="Credited to Maal", font=("Arial", 7), fg="gray").pack(side="bottom", pady=2)
root.mainloop()