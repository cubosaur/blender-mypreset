# Blender — My Preset

Every change I have made to a stock Blender install, written down, and packaged as
an add-on so a fresh machine is one click away from my setup.

Two things live here:

1. **The catalogue** — a complete, honest list of what differs from factory Blender.
   Extracted from `userpref.blend` and `startup.blend` by diffing against a
   `--factory-startup` run, not from memory.
2. **[`extensions/ez_preset/`](extensions/ez_preset)** — an add-on that applies all
   of it. Enable it and it writes the preferences, edits the keymap, loads the
   theme, and adds one thing Blender lacks: `Ctrl+1` isolating the selection in
   Edit Mode.

Captured from **Blender 5.1.2** on Windows 11. The tables say *what*.
[docs/why.md](docs/why.md) is where the *why* goes, one section per change.

---

## Contents

| Document | What is in it |
| --- | --- |
| [docs/keymap.md](docs/keymap.md) | Every hotkey change, and who owns it |
| [docs/preferences.md](docs/preferences.md) | Every preference change |
| [docs/startup-file.md](docs/startup-file.md) | The saved startup `.blend` |
| [docs/extensions.md](docs/extensions.md) | Add-ons, including three of my own |
| [docs/theme.md](docs/theme.md) | Theme, and one migration artifact |
| [docs/edit-mode-isolate.md](docs/edit-mode-isolate.md) | Design notes on the new `Ctrl+1` |
| [docs/why.md](docs/why.md) | **The reasoning behind each change** |
| [startup-files/](startup-files) | Saved startup `.blend` files |
| [reference/](reference) | Raw generated diffs, for grepping |

---

## The shape of it

The setup is a **Maya-shaped Blender**. Almost every deliberate change traces back
to one of four ideas:

- **`W`/`E`/`R` are move, rotate, scale**, and `Q` is select — the Maya home row.
- **`F` frames the selection**, everywhere, in every mode.
- **`Ctrl+1` isolates**, and now does so in Edit Mode too.
- **Right mouse acts on click, not on press**, so an RMB *drag* is free to mean
  something else.

The last two of those are not preferences at all — they are add-ons I wrote,
because the keymap alone could not express them.

---

## Hotkeys, at a glance

Changes I made by hand. `~` marks a binding moved off its default key.

### Global (Window keymap — works in every editor)

| Key | Does | Note |
| --- | --- | --- |
| `D` | Toggle Affect Only Origins | Added |
| `Ctrl+2` | Toggle wireframe overlay | Added |
| `4` | Viewport colour-type menu | Added |

### 3D View (any mode)

| Key | Does | Default was |
| --- | --- | --- |
| `F` | Frame Selected | ~ `Numpad .` |
| `Ctrl+1` | Isolate / Local View, without reframing | ~ `Numpad /` |
| `Ctrl+3` | Toggle X-Ray | Added |

### Object Mode

| Key | Does | Default was |
| --- | --- | --- |
| `Q` | X-Ray box select tool | Added |
| `1` | Subdivision preview off | ~ `Ctrl+0` |
| `3` | Subdivision preview on | ~ `Ctrl+2` |
| `X` | Delete, no confirmation popup | `X` with popup |
| `W` `E` `R` | Move / Rotate / Scale | via add-on |

Subdivision is a two-state preview, not a level ladder. `2` is unbound on purpose.

### Edit Mode and UV Editor

The same keys, in both the Mesh and UV Editor keymaps.

| Key | Does | Default was |
| --- | --- | --- |
| `Ctrl+1` | **Isolate selection + unsync UVs** | ~ `mesh.select_mode` expand |
| `Alt+1/2/3` | Expand select mode to vert / edge / face | ~ `Ctrl+1/2/3` |
| `Q` | X-Ray box select tool (Mesh only) | Added |
| `Ctrl+E` | Extrude along normals (Mesh only) | ~ `E` |
| `Shift+E` | Edge menu (Mesh only) | ~ `Ctrl+E` |
| `W` `E` `R` | Move / Rotate / Scale | via add-on |

### Switched off on purpose

| Key | Was | Why |
| --- | --- | --- |
| `F` (Edit Mode) | Make Edge/Face | `F` is Frame Selected everywhere. A real trade-off — see [docs/keymap.md](docs/keymap.md). |
| `Ctrl+1/2/3` (Mesh, UV Editor) | Select-mode expand | Moved to `Alt+1/2/3` to free `Ctrl+1` for Isolate |
| `Ctrl+1/3/4/5` (Object Mode) | Subdivision levels | `Ctrl+1` is Isolate; the ladder is unwanted |
| `Ctrl+0…5`, `Alt+1/2` (Sculpt) | Subdivision levels | Frees `Ctrl+1` and `Ctrl+2` in Sculpt Mode |

**Why disabling matters:** mode keymaps (`Mesh`, `Object Mode`, `Sculpt`) outrank
the `3D View` keymap, which outranks `Window`. A live binding in a higher-priority
keymap silently shadows a lower one. Every entry above exists because of that
ordering, not out of tidiness — `Ctrl+2` for the wireframe overlay genuinely did
not fire in Edit Mode until the `Ctrl+2` expand binding moved to `Alt+2`.

Priority is invisible in the Preferences UI, so there is a tool for it:

```bash
blender --background --python tools/diag_hotkey.py
```

It prints every keymap that claims a key, in priority order, and marks the winner.

Full tables, including the 37 bindings my add-ons rewrite rather than me:
**[docs/keymap.md](docs/keymap.md)**.

---

## Preferences, at a glance

15 changes. Full table with factory values in
[docs/preferences.md](docs/preferences.md).

| | |
| --- | --- |
| **Interface** | UI scale 1.15 · gizmo size 100 · minimal mini-axis · HSL colour picker · no splash · Python tooltips on · area handles and number arrows shown · subpixel AA |
| **Editing** | Undo steps 128 |
| **Navigation** | Fly, not Walk |
| **System** | Vulkan backend · online access on · Cycles on CUDA |
| **Keymap** | Spacebar opens Search · extended shading pie on `Z` |

---

## Install on a fresh machine

```bash
git clone https://github.com/cubosaur/blender-mypreset.git
```

Then in Blender: **Edit ▸ Preferences ▸ Add-ons ▸ Install from Disk**, point it at
`extensions/ez_preset`, and enable it. It applies the whole profile on first
enable. **Edit ▸ Preferences ▸ Add-ons ▸ EZ Preset** has an Apply / Restore pair
and reports anything it could not do on this machine.

Two things the add-on does not install. The four companion extensions in
[docs/extensions.md](docs/extensions.md), because an add-on cannot install other
add-ons — it lists whichever are missing so it is obvious what is left. And the
startup file in [startup-files/](startup-files), because replacing it on enable
would overwrite user data silently.

---

## Reproducing the catalogue

Everything in `docs/` came out of these, not out of clicking through Preferences:

```bash
blender --background --python tools/dump_config.py
```

`tools/gen_why.py` refreshes [docs/why.md](docs/why.md) from the profile, keeping
whatever reasoning is already written and adding stubs for new entries:

```bash
python tools/gen_why.py
```

`tools/` also holds `diff_keymap.py`, `diff_prefs.py`, `diag_hotkey.py`, and
`test_ez_preset.py` — 64 assertions covering the profile round-trip and the
isolate toggle:

```bash
blender --background --factory-startup --python tools/test_ez_preset.py
```

Two details worth knowing if you run these yourself:

- `--background` does **not** populate the default keymaps, so a keymap dump looks
  almost empty until you call `bpy.utils.keyconfig_init()` first. That one line is
  the difference between seeing 137 keymap items and seeing 3296.
- `keyconfigs.user.keymaps` contains **duplicate names** across space types. Key a
  dict on the keymap name and you will silently lose bindings.
