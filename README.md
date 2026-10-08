# TechHub Input Logger Tool

A desktop application for organizing and copying inputs from store paperwork submitted to PDI.

## Features

- Select and arrange input options using category tabs.
- Compose an entry, then use **Copy** to copy it or **Clear** to reset selections.
- Add, remove, rename, and reorder categories and options.
- Create options as standard checkboxes, text-entry fields, or multiple-choice checkboxes with a custom choice list.
- Toggle **Timestamp** and switch between light and dark themes.
- Save custom categories, options, labels, ordering, and theme preference between launches.

### Custom option types

When adding an option, choose one of these types:

- **Standard** — adds the option name when selected.
- **Text Entry** — prompts for a value and adds it as `Option#value`.
- **Multiple Choices** — enter one choice per line. The popup lets you select multiple choices, which are added as `Option(choice 1, choice 2)`.

In a multiple-choice popup, use **Up** and **Down** to move between choices, **Space** to toggle the focused choice, **Left Arrow** to select it, and **Right Arrow** to clear it.

## Keyboard shortcuts

| Key | Action |
| --- | --- |
| `+` | Choose **Add New Category** or **Add New Option** |
| `-` | Choose a category or option to remove |
| `*` | Choose categories or options to rename or reorder |
| `` ` `` | Toggle Timestamp |
| `A` or `←` | Go to the previous tab (when a choice popup is not active) |
| `D` or `→` | Go to the next tab (when a choice popup is not active) |

Use the **Dark Mode** checkbox in **Additional Options** to change the theme. Your theme preference and category and option customizations are saved for the current Windows user.
