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


def activate_popup(window, initial_focus=None):
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


def save_customizations(categories, options, removed_category_names=None, removed_option_names=None):
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
    tk.Checkbutton(
        category_frames[category_name],
        text=option_name,
        variable=all_options[option_name],
        command=lambda n=option_name: on_checkbox_toggle(n),
    ).pack(anchor="w")


def add_category_tab(category_name):
    frame = tk.Frame(options_notebook, padx=5, pady=5)
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
    if any(name.casefold() == category_name.casefold() for name in default_category_options):
        messagebox.showwarning("Duplicate Category", "That category name is reserved.", parent=root)
        return
    if any(name.casefold() == category_name.casefold() for name in category_frames):
        messagebox.showwarning("Duplicate Category", "That category already exists.", parent=root)
        return

    new_categories = {**custom_categories, category_name: []}
    if not save_customizations(new_categories, custom_options):
        return

    custom_categories[category_name] = []
    category_options[category_name] = []
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
    dialog.geometry("300x150")
    dialog.transient(root)

    tk.Label(dialog, text="Option name:").pack(anchor="w", padx=10, pady=(10, 2))
    name_entry = tk.Entry(dialog)
    name_entry.pack(fill="x", padx=10)
    tk.Label(dialog, text="Category:").pack(anchor="w", padx=10, pady=(8, 2))
    category_choice = ttk.Combobox(
        dialog,
        values=list(category_frames),
        state="readonly",
    )
    category_choice.pack(fill="x", padx=10)
    category_choice.current(0)

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

        new_custom_options = {
            name: list(option_names)
            for name, option_names in custom_options.items()
        }
        new_custom_options.setdefault(category_name, []).append(option_name)
        if not save_customizations(custom_categories, new_custom_options):
            return

        custom_options[category_name] = new_custom_options[category_name]
        category_options[category_name].append(option_name)
        add_option_checkbox(category_name, option_name)
        dialog.destroy()

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
    all_options.pop(option_name, None)
    if option_name in click_order:
        click_order.remove(option_name)
    if option_name == "NCR":
        ncr_selected.clear()
    elif option_name == "NPR":
        npr_selected.clear()
    elif option_name == "Loyalty":
        loyalty_selected.clear()
    elif option_name == "Lottery":
        lottery_selected.clear()
    elif option_name == "Bill Of Lading [1]":
        bol1_value.set("")
    elif option_name == "Bill Of Lading [2]":
        bol2_value.set("")
    elif option_name == "Bill Of Lading [3]":
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
    new_hidden_categories = set(hidden_categories)
    if category_name in default_category_options:
        new_hidden_categories.add(category_name)
    if not save_customizations(
        new_custom_categories,
        new_custom_options,
        new_hidden_categories,
        hidden_options,
    ):
        return

    removed_options = list(category_options[category_name])
    hidden_categories.clear()
    hidden_categories.update(new_hidden_categories)
    custom_categories.clear()
    custom_categories.update(new_custom_categories)
    custom_options.clear()
    custom_options.update(new_custom_options)
    options_notebook.forget(category_frames[category_name])
    category_frames.pop(category_name).destroy()
    category_options.pop(category_name)
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
    new_hidden_options = set(hidden_options)
    if option_name in new_custom_options.get(category_name, []):
        new_custom_options[category_name].remove(option_name)
        if not new_custom_options[category_name]:
            new_custom_options.pop(category_name)
    else:
        new_hidden_options.add(option_name)
    if not save_customizations(
        custom_categories,
        new_custom_options,
        hidden_categories,
        new_hidden_options,
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

def open_multi_checkbox_popup(name, options_list, selected_list):
    popup = tk.Toplevel(root)
    popup.title(f"Select {name}")
    popup.geometry("250x240")
    popup.transient(root)
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
    popup.bind('<Return>', confirm)
    popup.bind('<Escape>', cancel_esc)
    activate_popup(popup, widgets[0] if widgets else btn)

# ---------------------------
# UI Construction
# ---------------------------

root = tk.Tk()
root.title("Input Logger Tool")
root.geometry("320x720") 
root.iconbitmap(ICON_FILE)
root.iconbitmap(default=ICON_FILE)

options_notebook = ttk.Notebook(root)
timestamp_frame = tk.LabelFrame(root, text="Additional Options", padx=5, pady=5)
options_notebook.pack(fill="both", padx=10, pady=5)
timestamp_frame.pack(fill="both", padx=10, pady=5)

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
bol1_value, bol2_value, bol3_value = tk.StringVar(), tk.StringVar(), tk.StringVar()
ncr_selected, npr_selected, loyalty_selected, lottery_selected = [], [], [], []
category_frames = {}
custom_categories = {}
custom_options = {}
hidden_categories = set()
hidden_options = set()

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
    if (
        not isinstance(saved_categories, dict)
        or not isinstance(saved_options, dict)
        or not isinstance(saved_removed_categories, list)
        or any(not isinstance(name, str) or not name.strip() for name in saved_removed_categories)
        or not isinstance(saved_removed_options, list)
        or any(not isinstance(name, str) or not name.strip() for name in saved_removed_options)
    ):
        raise ValueError("Customization categories and options must be JSON objects.")

    hidden_categories.update(saved_removed_categories)
    hidden_options.update(saved_removed_options)
    category_options = {
        category_name: [
            option_name
            for option_name in option_names
            if option_name not in hidden_options
        ]
        for category_name, option_names in default_category_options.items()
        if category_name not in hidden_categories
    }
    used_category_names = {name.casefold() for name in default_category_options}
    used_option_names = {
        name.casefold()
        for option_names in default_category_options.values()
        for name in option_names
    }
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
                for option_name in option_names
            )
        ):
            raise ValueError("Customization file contains an invalid or duplicate category.")
        custom_categories[category_name] = option_names
        category_options[category_name] = list(option_names)
        used_category_names.add(category_name.casefold())
        used_option_names.update(option_name.casefold() for option_name in option_names)
    for category_name, option_names in saved_options.items():
        if (
            category_name not in category_options
            or not isinstance(option_names, list)
            or any(
                not isinstance(option_name, str)
                or not option_name.strip()
                or option_name.casefold() in used_option_names
                for option_name in option_names
            )
        ):
            raise ValueError("Customization file contains an invalid or duplicate option.")
        custom_options[category_name] = list(option_names)
        category_options[category_name].extend(option_names)
        used_option_names.update(option_name.casefold() for option_name in option_names)
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
    category_options = {
        name: list(option_names)
        for name, option_names in default_category_options.items()
    }

for option_names in category_options.values():
    for name in option_names:
        all_options[name] = tk.BooleanVar()
for name in additional_options:
    all_options[name] = tk.BooleanVar()

for category_name in category_options:
    add_category_tab(category_name)

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
root.bind_all("<KeyPress-plus>", show_add_choices)
root.bind_all("<KP_Add>", show_add_choices)
root.bind_all("<KeyPress-minus>", show_remove_choices)
root.bind_all("<KP_Subtract>", show_remove_choices)
tk.Label(root, text="Credited to Maal", font=("Arial", 7), fg="gray").pack(side="bottom", pady=2)
root.mainloop()