# Release Notes

## Current release

### TechHub Input Logger Tool

This release brings together the category-based input logger, customization tools, theme switching, and a standalone Windows build.

### Features

- Organize input options in tabs and compose entries from selected options.
- Copy the composed entry or clear the current selections.
- Add, remove, rename, and reorder categories and options.
- Create custom options as standard checkboxes, text-entry prompts, or multiple-choice checkboxes with user-defined choices.
- Preserve custom categories, options, names, ordering, and theme preference between launches.
- Switch between light and dark themes.
- Add a timestamp to the composed entry.
- Use themed multiple-choice popups with keyboard navigation.

### Keyboard shortcuts

| Key | Action |
| --- | --- |
| `+` | Open the add-category or add-option choices |
| `-` | Open the remove-category or remove-option choices |
| `*` | Open category and option rename/reorder choices |
| `` ` `` | Toggle Timestamp |
| `A` or `←` | Move to the previous tab |
| `D` or `→` | Move to the next tab |
| `↑` / `↓` | Move between choices in a multiple-choice popup |
| `Space` | Toggle the focused choice |
| `←` / `→` | Select or clear the focused choice |

### Windows build

- Packaged as a single-file GUI executable using PyInstaller.
- Runs without opening a command prompt.
- Includes the application icon for the executable and Tkinter windows.

### Saved settings

Customizations and the selected theme are saved for the current Windows user and restored when the app is launched again.
