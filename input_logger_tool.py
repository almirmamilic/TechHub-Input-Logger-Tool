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
option_action_names = {}
category_action_names = {}

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
        if action_name == "NCR":
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


def save_customizations(
    categories,
    options,
    removed_category_names=None,
    removed_option_names=None,
    saved_category_labels=None,
    saved_option_labels=None,
    saved_category_order=None,
    saved_option_order=None,
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
    checkbox = tk.Checkbutton(
        category_frames[category_name],
        text=option_name,
        variable=all_options[option_name],
        command=lambda n=option_name: on_checkbox_toggle(n),
    )
    checkbox.pack(anchor="w")
    option_widgets[option_name] = checkbox


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
        new_option_order = {
            name: list(option_names)
            for name, option_names in category_options.items()
        }
        new_option_order[category_name].append(option_name)
        if not save_customizations(
            custom_categories,
            new_custom_options,
            saved_option_order=new_option_order,
        ):
            return

        custom_options[category_name] = new_custom_options[category_name]
        category_options[category_name].append(option_name)
        option_action_names[option_name] = option_name
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
    action_name = option_action_names.pop(option_name, option_name)
    option_widgets.pop(option_name, None)
    all_options.pop(option_name, None)
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
    ):
        return

    category_options[category_name] = new_option_names
    if option_name in custom_options.get(category_name, []):
        custom_options[category_name] = new_options[category_name]
    option_labels.clear()
    option_labels.update(new_option_labels)
    option_action_names[new_name] = option_action_names.pop(option_name, option_name)
    all_options[new_name] = all_options.pop(option_name)
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
    popup.geometry("300x140")
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
        popup.destroy()
        rename_category(selected_category, name_entry.get())

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
options_notebook.pack(fill="both", expand=True, padx=10, pady=5)
timestamp_frame.pack(fill="x", padx=10, pady=5)

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
    if (
        not isinstance(saved_categories, dict)
        or not isinstance(saved_options, dict)
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
    category_labels.clear()
    option_labels.clear()
    category_action_names.clear()
    option_action_names.clear()
    category_options = {
        name: list(option_names)
        for name, option_names in default_category_options.items()
    }
    category_action_names.update(
        {name: name for name in default_category_options}
    )
    for option_names in default_category_options.values():
        option_action_names.update({name: name for name in option_names})

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
result_frame.pack(fill="x", padx=10, pady=5)
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
root.bind_all("<KeyPress-asterisk>", show_organize_choices)
root.bind_all("<KP_Multiply>", show_organize_choices)
root.bind_all("<KeyPress-grave>", toggle_timestamp)
root.bind_all("<KeyPress-a>", navigate_tabs)
root.bind_all("<KeyPress-A>", navigate_tabs)
root.bind_all("<KeyPress-d>", navigate_tabs)
root.bind_all("<KeyPress-D>", navigate_tabs)
root.bind_all("<Left>", navigate_tabs)
root.bind_all("<Right>", navigate_tabs)
tk.Label(root, text="Credited to Maal", font=("Arial", 7), fg="gray").pack(side="bottom", pady=2)
root.update_idletasks()
root.minsize(320, root.winfo_reqheight())
root.mainloop()