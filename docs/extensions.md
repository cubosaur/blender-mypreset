# Extensions and add-ons

13 add-ons enabled, nothing disabled that ships on by default.

## My own

Three of the four non-stock add-ons are ones I wrote, which is the clearest signal
of where Blender's keymap stops being expressive enough. All under
[github.com/cubosaur](https://github.com/cubosaur).

### Easy Transform Axis Switch — 1.0.0

> Maya-style W/E/R hotkeys with Global/Local orientation toggle

`W`/`E`/`R` → move / rotate / scale via one `etas.transform_tool` operator, bound
across ten mode keymaps. Repeating a key toggles the orientation between Global and
Local instead of restarting the transform, which is the part a plain keymap change
cannot do.

Owns **18** keymap deactivations — everything that previously held a plain `W`, `E`
or `R` press. Recorded in its own `overrides` preference so it can hand them back.

| Preference | Value |
| --- | --- |
| `orientation` | `GLOBAL` |
| `keep_custom_orientations` | `True` |
| `repeat_timeout` | `0.0` (no timeout) |

### Remember Last Used Axis — 1.7.0

> Transform along the last used gizmo axis with an RMB drag

Watches which gizmo axis you last dragged, then lets an RMB drag repeat that
transform on that axis. To free the RMB drag it flips the context menu from
**Press** to **Click** in **19** keymaps, keeping a `keymap_backup` in its own
preferences to undo it.

| Preference | Value |
| --- | --- |
| `enable_rmb_transform` | `True` |
| `transform_source` | `LAST_USED` |
| `retime_context_menu` | `True` |
| `legacy_mmb_repaired` | `True` |

### EZ UV Editor — 0.3.0

> Simplified Maya-style UV workflow

Five numbered steps in an **EZ UV** sidebar tab in the UV Editor: project, seam,
unwrap, gridify, lay out. Drives Blender's own UV operators; what it adds is the
ordering and pixel-accurate padding maths.

Registers **no keymaps**, so it never collides with anything here. Relevant to the
isolate work because it also reads `use_uv_select_sync`.

Notable defaults: conformal unwrap, 1024 px map size, 4 px shell / 2 px tile
padding, exact-shape packing, 90° island rotation.

## From extensions.blender.org

| Add-on | Version | Author | Note |
| --- | --- | --- | --- |
| X-Ray Selection Tools | 4.10.2 | MarshmallowCirno | Box / lasso / circle select with X-ray. Bound to `Q` in Object Mode and Mesh. |

## Bundled with Blender

| Add-on | Note |
| --- | --- |
| Node Wrangler | Enabled. 87 Node Editor bindings, all stock. |
| Cycles | `compute_device_type = CUDA` |
| Pose Library, FBX, glTF 2.0, BVH, SVG, UV Layout | Stock defaults |
| Extensions framework (`bl_pkg`) | Stock |

## Themes installed

Four are installed, one is active. See [theme.md](theme.md).

| Theme | Version | Author | Active |
| --- | --- | --- | --- |
| Professional | 1.0.3 | kame404 | **yes** |
| Dark Pro | 2.0.3 | Mahdi Shalchian | no |
| DarkPurpleGreen | 1.0.1 | MSBH | no |
| Shadow | 5.0.2 | Shadow | no |

## Repositories

| Name | Module | Remote |
| --- | --- | --- |
| extensions.blender.org | `blender_org` | yes |
| User Default | `user_default` | no — local, holds my three add-ons |
| System | `system` | no — ships with Blender |

## Installing on a fresh machine

`ez_preset` cannot install these; Blender gives an add-on no supported way to
install another. It does check which are enabled and lists the missing ones in its
preferences panel.

1. Enable **online access** in Preferences ▸ System, then install X-Ray Selection
   Tools from Preferences ▸ Get Extensions.
2. Clone the three `cubosaur` repos and install each with **Install from Disk**, or
   drop them straight into:
   `%APPDATA%\Blender Foundation\Blender\<version>\extensions\user_default\`
3. Enable Node Wrangler in Preferences ▸ Add-ons.

Order matters slightly: install Easy Transform Axis Switch before `ez_preset` so
its `W`/`E`/`R` deactivations are already in place when the profile is applied.
