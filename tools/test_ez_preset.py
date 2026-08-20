"""Headless test for ez_preset. Run with --factory-startup so nothing real is touched."""

import os
import sys

import bmesh
import bpy

REPO = os.environ.get("EZ_PRESET_PARENT", r"D:/Vibes/08_BLENDER_MYPRESET/extensions")
sys.path.insert(0, REPO)

FAILS = []
def check(label, cond, extra=""):
    print(("  PASS  " if cond else "  FAIL  ") + label + (("  | " + str(extra)) if extra else ""))
    if not cond:
        FAILS.append(label)

print("=" * 78)
print("1. keyconfig init + import + register")
print("=" * 78)
bpy.utils.keyconfig_init()

import ez_preset
from ez_preset import apply_keymaps, apply_prefs, profile, prefs as ezprefs

ez_preset.register()
check("register() completed", True)

print()
print("=" * 78)
print("2. apply_profile()")
print("=" * 78)
problems = ezprefs.apply_profile()
for p in problems:
    print("     note:", p)

P = bpy.context.preferences
check("view.ui_scale == 1.15", abs(P.view.ui_scale - 1.15) < 1e-5, P.view.ui_scale)
check("view.mini_axis_type == MINIMAL", P.view.mini_axis_type == "MINIMAL", P.view.mini_axis_type)
check("edit.undo_steps == 128", P.edit.undo_steps == 128, P.edit.undo_steps)
check("inputs.navigation_mode == FLY", P.inputs.navigation_mode == "FLY", P.inputs.navigation_mode)
check("view.show_splash is False", P.view.show_splash is False)
check("system.gpu_backend == VULKAN", P.system.gpu_backend == "VULKAN", P.system.gpu_backend)

kc = bpy.context.window_manager.keyconfigs.get("Blender")
kcp = getattr(kc, "preferences", None)
if kcp is None:
    check("keyconfig prefs present", False, "no Blender keyconfig preferences")
else:
    check("spacebar_action == SEARCH", kcp.spacebar_action == "SEARCH", kcp.spacebar_action)
    check("use_v3d_shade_ex_pie is True", kcp.use_v3d_shade_ex_pie is True)

print()
print("=" * 78)
print("3. keymap edits landed")
print("=" * 78)
user = bpy.context.window_manager.keyconfigs.user

def find(km_name, idname, **spec):
    km = user.keymaps.get(km_name)
    if km is None:
        return None
    for kmi in km.keymap_items:
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

check("3D View  F -> view3d.view_selected",
      find("3D View", "view3d.view_selected", type="F", ctrl=False, alt=False, shift=False) is not None)
check("3D View  Ctrl+1 -> view3d.localview (frame_selected off)",
      find("3D View", "view3d.localview", type="ONE", ctrl=True,
           properties={"frame_selected": False}) is not None)
check("Mesh  Ctrl+E -> extrude",
      find("Mesh", "view3d.edit_mesh_extrude_move_normal", type="E", ctrl=True) is not None)
check("Mesh  Shift+E -> edge menu",
      find("Mesh", "wm.call_menu", type="E", shift=True,
           properties={"name": "VIEW3D_MT_edit_mesh_edges"}) is not None)
check("Object Mode  1 -> subdivision level 0",
      find("Object Mode", "object.subdivision_set", type="ONE", ctrl=False,
           properties={"level": 0}) is not None)
check("Object Mode  3 -> subdivision level 2",
      find("Object Mode", "object.subdivision_set", type="THREE", ctrl=False,
           properties={"level": 2}) is not None)
check("Object Mode  X -> delete, confirm off",
      find("Object Mode", "object.delete", type="X", properties={"confirm": False}) is not None)
check("Window  Ctrl+2 -> wireframe overlay toggle",
      find("Window", "wm.context_toggle", type="TWO", ctrl=True,
           properties={"data_path": "space_data.overlay.show_wireframes"}) is not None)
check("Window  D -> affect only origins",
      find("Window", "wm.context_toggle", type="D",
           properties={"data_path": "scene.tool_settings.use_transform_data_origin"}) is not None)
check("Mesh  Q -> xray box select",
      find("Mesh", "wm.tool_set_by_id", type="Q",
           properties={"name": "mesh_tool.select_box_xray"}) is not None)
check("3D View  Ctrl+3 -> toggle_xray",
      find("3D View", "view3d.toggle_xray", type="THREE", ctrl=True,
           alt=False, shift=False) is not None)
check("3D View  Alt+Z toggle_xray still present",
      find("3D View", "view3d.toggle_xray", type="Z", alt=True) is not None)
# Ctrl+3 must not be shadowed by a mode keymap in either mode.
for km_name in ("Mesh", "Object Mode", "Sculpt"):
    km = user.keymaps.get(km_name)
    live = [k for k in km.keymap_items
            if k.type == "THREE" and k.ctrl and not (k.alt or k.shift)
            and k.active]
    check("%s has no live Ctrl+3 to shadow X-ray" % km_name, not live,
          [k.idname for k in live])

mesh_km = user.keymaps.get("Mesh")
expand = [k for k in mesh_km.keymap_items
          if k.idname == "mesh.select_mode" and k.ctrl and not k.shift
          and k.type in ("ONE", "TWO", "THREE")]
check("Ctrl+1/2/3 expand all inactive", expand and all(not k.active for k in expand),
      [(k.type, k.active) for k in expand])
ctrl_shift = [k for k in mesh_km.keymap_items
              if k.idname == "mesh.select_mode" and k.ctrl and k.shift]
check("Ctrl+Shift+1/2/3 left active", ctrl_shift and all(k.active for k in ctrl_shift),
      [(k.type, k.active) for k in ctrl_shift])

mesh_f = [k for k in mesh_km.keymap_items if k.idname == "mesh.edge_face_add" and k.type == "F"]
check("Mesh F (edge_face_add) disabled", mesh_f and all(not k.active for k in mesh_f))

sculpt_km = user.keymaps.get("Sculpt")
sub = [k for k in sculpt_km.keymap_items if k.idname == "object.subdivision_set"]
check("Sculpt subdivision row disabled (%d items)" % len(sub), sub and all(not k.active for k in sub))

addon_kc = bpy.context.window_manager.keyconfigs.addon

# Hotkey parity: Mesh and UV Editor must get identical treatment.
for km_name in ("Mesh", "UV Editor"):
    akm = addon_kc.keymaps.get(km_name) if addon_kc else None
    own = [k for k in akm.keymap_items] if akm else []
    check("%s addon keyconfig: Ctrl+1 isolate present" % km_name,
          any(k.idname == "ez_isolate.toggle" and k.type == "ONE" and k.ctrl
              for k in own))
    alt_expand = [k for k in own if k.idname == "mesh.select_mode" and k.alt]
    check("%s addon keyconfig: Alt+1/2/3 expand present (3)" % km_name,
          len(alt_expand) == 3,
          [(k.type, k.properties.type, k.properties.use_expand)
           for k in alt_expand])

uv_km = user.keymaps.get("UV Editor")
uv_expand = [k for k in uv_km.keymap_items
             if k.idname == "mesh.select_mode" and k.ctrl and not k.shift
             and k.type in ("ONE", "TWO", "THREE")]
check("UV Editor Ctrl+1/2/3 expand all inactive",
      uv_expand and all(not k.active for k in uv_expand),
      [(k.type, k.active) for k in uv_expand])
uv_cs = [k for k in uv_km.keymap_items
         if k.idname == "mesh.select_mode" and k.ctrl and k.shift]
check("UV Editor Ctrl+Shift+1/2/3 left active",
      uv_cs and all(k.active for k in uv_cs))

print()
print("=" * 78)
print("4. Edit Mode isolate operator")
print("=" * 78)
bpy.ops.wm.read_factory_settings(use_empty=True)
bpy.ops.mesh.primitive_cube_add()
obj = bpy.context.active_object
me = obj.data
print("     cube:", len(me.vertices), "verts", len(me.polygons), "faces")

bpy.ops.object.mode_set(mode="EDIT")
bpy.context.tool_settings.mesh_select_mode = (False, False, True)


def select_faces(indices):
    """Select exactly these faces, flushing so Blender's ops agree with us."""
    bpy.ops.mesh.select_all(action="DESELECT")
    bm = bmesh.from_edit_mesh(me)
    bm.faces.ensure_lookup_table()
    for i in indices:
        bm.faces[i].select = True
    bm.select_flush(True)
    bmesh.update_edit_mesh(me)


# Pre-hide face 5 by hand so we can prove the toggle preserves it.
select_faces([5])
bpy.ops.mesh.hide(unselected=False)
print("     pre-hid face 5 by hand")

bm = bmesh.from_edit_mesh(me)
bm.faces.ensure_lookup_table()
prehidden = {i for i, f in enumerate(bm.faces) if f.hide}
print("     hidden before isolate:", sorted(prehidden))

select_faces([0, 1])

ts = bpy.context.scene.tool_settings
ts.use_uv_select_sync = True
print("     uv sync before:", ts.use_uv_select_sync)

res = bpy.ops.ez_isolate.toggle()
check("isolate returned FINISHED", res == {"FINISHED"}, res)

bm = bmesh.from_edit_mesh(me)
bm.faces.ensure_lookup_table()
visible = {i for i, f in enumerate(bm.faces) if not f.hide}
check("only faces 0,1 visible", visible == {0, 1}, sorted(visible))
check("uv sync turned off", ts.use_uv_select_sync is False)
check("mesh carries snapshot", "ez_isolate_counts" in me)

res = bpy.ops.ez_isolate.toggle()
check("restore returned FINISHED", res == {"FINISHED"}, res)

bm = bmesh.from_edit_mesh(me)
bm.faces.ensure_lookup_table()
hidden_after = {i for i, f in enumerate(bm.faces) if f.hide}
check("pre-existing hidden face preserved", hidden_after == prehidden,
      "before=%s after=%s" % (sorted(prehidden), sorted(hidden_after)))
check("uv sync restored to True", ts.use_uv_select_sync is True)
check("snapshot cleared", "ez_isolate_counts" not in me)

print()
print("     second round trip, nothing pre-hidden")
bpy.ops.mesh.reveal(select=False)
select_faces([3])
bpy.ops.ez_isolate.toggle()
bm = bmesh.from_edit_mesh(me)
visible = {i for i, f in enumerate(bm.faces) if not f.hide}
check("only face 3 visible", visible == {3}, sorted(visible))
bpy.ops.ez_isolate.toggle()
bm = bmesh.from_edit_mesh(me)
check("all faces visible again", not any(f.hide for f in bm.faces))

print()
print("     nothing selected -> refuses")
bpy.ops.mesh.select_all(action="DESELECT")
res = bpy.ops.ez_isolate.toggle()
check("empty selection cancels", res == {"CANCELLED"}, res)

bpy.ops.object.mode_set(mode="OBJECT")
check("poll blocks in Object Mode", not bpy.ops.ez_isolate.toggle.poll())

print()
print("=" * 78)
print("5. restore_profile()")
print("=" * 78)
notes = ezprefs.restore_profile()
for n in notes:
    print("     note:", n)
P = bpy.context.preferences
check("ui_scale back to 1.0", abs(P.view.ui_scale - 1.0) < 1e-5, P.view.ui_scale)
check("undo_steps back to 32", P.edit.undo_steps == 32, P.edit.undo_steps)
check("navigation_mode back to WALK", P.inputs.navigation_mode == "WALK", P.inputs.navigation_mode)
check("show_splash back to True", P.view.show_splash is True)

user = bpy.context.window_manager.keyconfigs.user
check("3D View F rebind reverted",
      find("3D View", "view3d.view_selected", type="NUMPAD_PERIOD") is not None)
check("3D View localview back on NUMPAD_SLASH",
      find("3D View", "view3d.localview", type="NUMPAD_SLASH") is not None)
# Rebinds that changed a property must restore the property, not just the key.
check("localview frame_selected back to True",
      find("3D View", "view3d.localview", type="NUMPAD_SLASH",
           properties={"frame_selected": True}) is not None)
check("object.delete confirm back to True",
      find("Object Mode", "object.delete", type="X",
           properties={"confirm": True}) is not None)
mesh_km = user.keymaps.get("Mesh")
mesh_f = [k for k in mesh_km.keymap_items if k.idname == "mesh.edge_face_add" and k.type == "F"]
check("Mesh F re-enabled", mesh_f and all(k.active for k in mesh_f))
for km_name in ("Mesh", "UV Editor"):
    km = user.keymaps.get(km_name)
    expand = [k for k in km.keymap_items
              if k.idname == "mesh.select_mode" and k.ctrl and not k.shift
              and k.type in ("ONE", "TWO", "THREE")]
    check("%s Ctrl+1/2/3 expand re-enabled" % km_name,
          expand and all(k.active for k in expand))
check("Window Ctrl+2 add removed",
      find("Window", "wm.context_toggle", type="TWO", ctrl=True,
           properties={"data_path": "space_data.overlay.show_wireframes"}) is None)
check("3D View Ctrl+3 xray add removed",
      find("3D View", "view3d.toggle_xray", type="THREE", ctrl=True) is None)
check("3D View Alt+Z xray survived the restore",
      find("3D View", "view3d.toggle_xray", type="Z", alt=True) is not None)

print()
print("=" * 78)
print("6. _sync() stays callable more than once per launch")
print("=" * 78)
# Regression guard. _sync() used to be gated by a once-per-session flag set
# during register(), so the deferred timer pass returned immediately. On a real
# launch the user keyconfig can still be empty at register() time, and that made
# the keymap edits silently never land.
ez_preset._applied_this_session = False
ez_preset._sync()
check("first _sync() applies the profile keymaps",
      find("3D View", "view3d.toggle_xray", type="THREE", ctrl=True) is not None)

ezprefs.restore_profile()
check("restore removed Ctrl+3 again",
      find("3D View", "view3d.toggle_xray", type="THREE", ctrl=True) is None)
ez_preset._sync()
check("_sync() re-applies after a restore, not a no-op",
      find("3D View", "view3d.toggle_xray", type="THREE", ctrl=True) is not None)

ez_preset.unregister()
check("unregister() completed", True)

print()
print("=" * 78)
print("RESULT: %d failure(s)" % len(FAILS))
for f in FAILS:
    print("   FAILED:", f)
print("=" * 78)
