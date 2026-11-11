# TechHub Input Logger Tool

A desktop application for organizing and copying inputs from store paperwork submitted to PDI.

## Features

- Select input options using category tabs (**CT**, **CNG**, **FT**, **A** by default).
- Compose an entry, then use **Copy** to copy it or **Clear** to reset selections.
- Output is always ordered by tab and option order, regardless of the order options were clicked.
- Add, remove, rename, and reorder categories and options from the **⚙ settings menu**.
- Create options as standard checkboxes, text-entry fields, or multiple-choice checkboxes with a custom choice list.
- Toggle **Timestamp** via the clock button or keyboard shortcut; the output is prefixed with `Data Entered:` and suffixed with ` - <Agent Name>(DE) MM/DD/YYYY`.
- Set your agent name once — it's remembered between launches and used in the timestamp suffix.
- Switch between light and dark themes; the preference is saved.
- Window size, theme, agent name, and all category/option customizations are saved for the current Windows user.

### Custom option types

When adding an option, choose one of these types:

- **Standard** — adds the option name when selected.
- **Text Entry** — prompts for a value and adds it as `Option#value`.
- **Multiple Choices** — enter one choice per line. The popup lets you select multiple choices, which are added as `Option(choice 1, choice 2)`.

In a multiple-choice popup, use **W/S** or **Up/Down** to move between choices, **Space** to toggle the focused choice, **Left Arrow** to uncheck it, and **Right Arrow** to check it. **Enter** confirms and **Escape** cancels.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `` ` `` | Toggle Timestamp |
| `A` or `←` | Go to the previous tab |
| `D` or `→` | Go to the next tab |
| `W` or `S` | Move focus up/down through the options in the current tab |
| `Delete` | Clear all selections |
| `Ctrl+C` | Copy the output |

Shortcuts do not fire while typing in a text field or while a popup is open.

## Settings

Click the **⚙** button at the top-right of the options area to open the settings menu:

- **Add Category** / **Add Option**
- **Remove Category** / **Remove Option**
- **Rename Category** / **Rename Option**
- **Reorder Tabs** / **Reorder Options**
- **Agent Name...** — set the name used in the timestamp suffix
- **Dark Mode** — toggle the theme

On first launch, a dialog asks for your agent name (the default is `Unknown`).

## Data storage

All preferences are stored in `%APPDATA%\TechHub Input Logger Tool\customizations.json` — a plain JSON file with categories, options, ordering, hidden items, labels, option types/choices, dark mode, agent name, and window size. Selected options themselves are not saved.

## Windows executable

The packaged, single-file application is `dist/TechHub Input Logger Tool.exe`. It opens as a GUI application without a command prompt. The app icon is embedded in the executable and bundled for the Tkinter window and taskbar.

To rebuild on Windows, use the project virtual environment:

```powershell
.venv\Scripts\python.exe -m PyInstaller --noconfirm "TechHub Input Logger Tool.spec"
```
