"""Dry run against the REAL user config. Loads it, applies, verifies, never saves."""

import bpy

MODULE = "bl_ext.user_default.ez_preset"

print("=" * 78)
print("Blender", bpy.app.version_string, "| real user config")
print("=" * 78)

bpy.utils.keyconfig_init()
user = bpy.context.window_manager.keyconfigs.user
print("keymaps:", len(user.keymaps),
      "items:", sum(len(k.keymap_items) for k in user.keymaps))

enabled_before = {a.module for a in bpy.context.preferences.addons}
print("ez_preset already enabled:", MODULE in enabled_before)

print()
print("--- enabling", MODULE, "---")
try:
    bpy.ops.preferences.addon_enable(module=MODULE)
    print("enable OK")
except Exception as exc:
    print("enable FAILED:", exc)
    raise SystemExit(1)

addon = bpy.context.preferences.addons.get(MODULE)
print("preferences object:", addon.preferences if addon else None)

import sys
mod = sys.modules.get(MODULE)
ezprefs = sys.modules.get(MODULE + ".prefs")

print()
print("--- applying profile ---")
notes = ezprefs.apply_profile()
if notes:
    for n in notes:
        print("   note:", n)
else:
    print("   no notes")

print()
print("--- idempotency: apply again ---")
notes2 = ezprefs.apply_profile()
print("   second run notes:", len(notes2))
for n in notes2:
    print("     ", n)

print()
print("=" * 78)
print("VERIFY against real config")
print("=" * 78)
user = bpy.context.window_manager.keyconfigs.user
addon_kc = bpy.context.window_manager.keyconfigs.addon

FAILS = []
def check(label, cond, extra=""):
    print(("  PASS  " if cond else "  FAIL  ") + label + (("  | " + str(extra)) if extra else ""))
    if not cond:
        FAILS.append(label)

mesh = user.keymaps.get("Mesh")
expand = [k for k in mesh.keymap_items
          if k.idname == "mesh.select_mode" and k.ctrl and not k.shift
          and k.type in ("ONE", "TWO", "THREE")]
check("Ctrl+1/2/3 expand disabled in real Mesh keymap",
      expand and all(not k.active for k in expand),
      [(k.type, k.active) for k in expand])

akm = addon_kc.keymaps.get("Mesh") if addon_kc else None
own = list(akm.keymap_items) if akm else []
check("Ctrl+1 -> ez_isolate.toggle in addon keyconfig",
      any(k.idname == "ez_isolate.toggle" and k.type == "ONE" and k.ctrl for k in own))
check("Alt+1/2/3 expand in addon keyconfig",
      len([k for k in own if k.idname == "mesh.select_mode" and k.alt]) == 3)

# The pre-existing hand-made edits must still be exactly as they were.
def find(km_name, idname, **spec):
    km = user.keymaps.get(km_name)
    for kmi in (km.keymap_items if km else []):
        if kmi.idname != idname:
            continue
        ok = True
        for k, v in spec.items():
            if k == "properties":
                for pk, pv in v.items():
                    if not hasattr(kmi.properties, pk) or getattr(kmi.properties, pk) != pv:
                        ok = False
                        break
            elif getattr(kmi, k) != v:
                ok = False
            if not ok:
                break
        if ok:
            return kmi
    return None

check("3D View Ctrl+1 localview intact",
      find("3D View", "view3d.localview", type="ONE", ctrl=True,
           properties={"frame_selected": False}) is not None)
check("3D View F frame-selected intact",
      find("3D View", "view3d.view_selected", type="F") is not None)
check("Mesh Ctrl+E extrude intact",
      find("Mesh", "view3d.edit_mesh_extrude_move_normal", type="E", ctrl=True) is not None)
check("Window Ctrl+2 wireframe intact",
      find("Window", "wm.context_toggle", type="TWO", ctrl=True,
           properties={"data_path": "space_data.overlay.show_wireframes"}) is not None)
check("Mesh Q xray tool intact",
      find("Mesh", "wm.tool_set_by_id", type="Q",
           properties={"name": "mesh_tool.select_box_xray"}) is not None)

# ETAS must still own its W/E/R bindings; the preset must not have fought it.
etas = [k for k in mesh.keymap_items if k.idname == "etas.transform_tool"]
check("ETAS W/E/R still live in Mesh (3)", len(etas) == 3 and all(k.active for k in etas),
      [(k.type, k.active) for k in etas])
obj_km = user.keymaps.get("Object Mode")
etas_o = [k for k in obj_km.keymap_items if k.idname == "etas.transform_tool"]
check("ETAS W/E/R still live in Object Mode (3)",
      len(etas_o) == 3 and all(k.active for k in etas_o))

# RLUA's RMB Click conversions must be untouched.
rmb = find("Mesh", "wm.call_menu", type="RIGHTMOUSE", value="CLICK",
           properties={"name": "VIEW3D_MT_edit_mesh_context_menu"})
check("RLUA RMB-on-click still intact in Mesh", rmb is not None)

P = bpy.context.preferences
check("ui_scale still 1.15", abs(P.view.ui_scale - 1.15) < 1e-4, P.view.ui_scale)
check("undo_steps still 128", P.edit.undo_steps == 128, P.edit.undo_steps)
check("gpu_backend still VULKAN", P.system.gpu_backend == "VULKAN")

print()
print("=" * 78)
print("RESULT: %d failure(s)   (preferences NOT saved)" % len(FAILS))
for f in FAILS:
    print("   FAILED:", f)
print("=" * 78)
