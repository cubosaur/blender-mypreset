# Preferences

Diffed against `--factory-startup` on Blender 5.1.2. 15 applicable changes, plus 2
on the keyconfig and 1 on an add-on.

Everything here is applied by
[`extensions/ez_preset/profile.py`](../extensions/ez_preset/profile.py), which
records the factory value alongside the chosen one so Restore has something to go
back to.

## Interface

| Setting | Mine | Factory | Note |
| --- | --- | --- | --- |
| `view.ui_scale` | `1.15` | `1.0` | Larger UI for a 4K display |
| `view.gizmo_size` | `100` | `75` | Bigger transform gizmo, easier to grab |
| `view.mini_axis_type` | `MINIMAL` | `GIZMO` | Plain axis cross, not the navigation ball |
| `view.mini_axis_brightness` | `10` | `8` | |
| `view.color_picker_type` | `CIRCLE_HSL` | `CIRCLE_HSV` | HSL wheel |
| `view.show_splash` | `False` | `True` | No splash on launch |
| `view.show_tooltips_python` | `True` | `False` | Shows the Python path in tooltips |
| `view.show_addons_enabled_only` | `True` | `False` | Preferences lists only enabled add-ons |
| `view.show_area_handle` | `True` | `False` | Visible corner handles for splitting areas |
| `view.show_number_arrows` | `True` | `False` | Step arrows on number fields |
| `view.use_text_render_subpixelaa` | `True` | `False` | Subpixel text antialiasing |

`show_tooltips_python` is the load-bearing one: it is what makes it possible to
hover a setting, read its RNA path, and script the change instead of clicking it.
This whole repo is downstream of that checkbox.

## Editing

| Setting | Mine | Factory | Note |
| --- | --- | --- | --- |
| `edit.undo_steps` | `128` | `32` | Deeper undo stack, costs memory |

## Navigation

| Setting | Mine | Factory | Note |
| --- | --- | --- | --- |
| `inputs.navigation_mode` | `FLY` | `WALK` | Fly rather than walk |

## System

| Setting | Mine | Factory | Note |
| --- | --- | --- | --- |
| `system.gpu_backend` | `VULKAN` | `OPENGL` | Needs a restart to take effect |
| `system.use_online_access` | `True` | `False` | Required by the extensions repository |

## Keyconfig preferences

These live on the `Blender` keyconfig rather than on Preferences, which is why they
are easy to miss in a naive diff — the keyconfig is itself a Python add-on and is
absent under `--factory-startup`.

| Setting | Mine | Factory | Note |
| --- | --- | --- | --- |
| `spacebar_action` | `SEARCH` | `PLAY` | Spacebar opens search |
| `use_v3d_shade_ex_pie` | `True` | `False` | Extended shading pie on `Z` |

Everything else on the keyconfig is stock, including `select_mouse = LEFT`,
`rmb_action = TWEAK` and `use_alt_navigation = True` — all already the defaults.

## Add-on preferences

| Add-on | Setting | Mine | Factory | Note |
| --- | --- | --- | --- | --- |
| Cycles | `compute_device_type` | `CUDA` | `NONE` | 3 devices enumerated on this machine |

Applied inside a `try`, since a machine with no CUDA device will reject it. The
add-on reports the skip rather than failing the run.

## Deliberately not applied

These show up in the raw diff but are not portable settings, so `profile.py` lists
them in `SKIPPED_PREFERENCES` rather than applying them:

| Setting | Value here | Why skipped |
| --- | --- | --- |
| `system.dpi` | `124` | Computed from `view.ui_scale` and the monitor |
| `system.ui_scale` | `1.722222` | Same — a derived value, not an input |
| `system.register_all_users` | `True` | Windows file-association state, needs admin |

Also excluded: file paths, recent files, bookmarks, and the enumerated Cycles
device list — all machine-local.

## Raw diff

[`reference/preferences-diff.txt`](../reference/preferences-diff.txt), regenerate
with:

```bash
blender --background --python tools/dump_config.py
```
