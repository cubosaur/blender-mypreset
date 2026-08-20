"""The profile: every hand-made change to this Blender setup, as data.

This module is the single source of truth. The apply modules are dumb engines
that walk these tables; nothing about *which* settings are personal lives
anywhere else, so adding a preference means adding one line here and nothing
more.

Two rules keep the tables honest:

**Only hand-made changes belong here.** A large share of the keymap edits in this
setup are produced by other add-ons: Easy Transform Axis Switch switches off the
plain W/E/R bindings it takes over, and Remember Last Used Axis flips 19 right
mouse bindings from Press to Click. Those add-ons re-apply their own edits on
every load, so duplicating them here would mean two owners for one binding and a
restore that fights whichever ran last. They are documented in the repo instead.

**Every entry carries its factory value.** Restore means "put Blender back", so
the default is written down rather than read at runtime, where by definition it
has already been overwritten.
"""

# ---------------------------------------------------------------------------
# Preferences
# ---------------------------------------------------------------------------
# (path, value, factory, note)
PREFERENCES = (
    ("view.ui_scale", 1.15, 1.0,
     "Slightly larger UI for a 4K display"),
    ("view.gizmo_size", 100, 75,
     "Bigger transform gizmo, easier to grab"),
    ("view.mini_axis_type", "MINIMAL", "GIZMO",
     "Simple axis cross instead of the navigation gizmo ball"),
    ("view.mini_axis_brightness", 10, 8,
     "Brighter mini axis"),
    ("view.color_picker_type", "CIRCLE_HSL", "CIRCLE_HSV",
     "HSL colour wheel"),
    ("view.show_splash", False, True,
     "No splash screen on launch"),
    ("view.show_tooltips_python", True, False,
     "Show the Python name in tooltips, needed to script config changes"),
    ("view.show_addons_enabled_only", True, False,
     "Preferences lists only enabled add-ons"),
    ("view.show_area_handle", True, False,
     "Visible corner handles for splitting areas"),
    ("view.show_number_arrows", True, False,
     "Step arrows on number fields"),
    ("view.use_text_render_subpixelaa", True, False,
     "Subpixel text antialiasing"),
    ("edit.undo_steps", 128, 32,
     "Deeper undo stack"),
    ("inputs.navigation_mode", "FLY", "WALK",
     "Fly navigation rather than walk"),
    ("system.gpu_backend", "VULKAN", "OPENGL",
     "Vulkan backend, takes effect after a restart"),
    ("system.use_online_access", True, False,
     "Allow online access, required for the extensions repository"),
)

# Machine-derived values deliberately left out of PREFERENCES.
SKIPPED_PREFERENCES = (
    ("system.dpi", "Derived from view.ui_scale and the display"),
    ("system.ui_scale", "Derived from view.ui_scale and the display"),
    ("system.register_all_users", "Windows install state, needs admin, not portable"),
)

# Preferences that live on the "Blender" keyconfig rather than on Preferences.
# (attribute, value, factory, note)
KEYCONFIG_PREFERENCES = (
    ("spacebar_action", "SEARCH", "PLAY",
     "Spacebar opens search instead of playing the timeline"),
    ("use_v3d_shade_ex_pie", True, False,
     "Extended shading pie on Z"),
)

# Add-on preferences. (module, attribute, value, factory, note)
ADDON_PREFERENCES = (
    ("cycles", "compute_device_type", "CUDA", "NONE",
     "CUDA compute for Cycles, skipped when the machine has no CUDA device"),
)

# ---------------------------------------------------------------------------
# Theme
# ---------------------------------------------------------------------------
# Installed separately as an extension, so the profile only points at it.
# Applying is a no-op when the theme is not present.
THEME = {
    "extension_id": "Professional_theme",
    "xml": "Professional.xml",
    "name": "Professional",
    "author": "kame404",
    "version": "1.0.3",
}

# ---------------------------------------------------------------------------
# Keymap
# ---------------------------------------------------------------------------
# Bindings added from scratch.
KEYMAP_ADD = (
    dict(keymap="Window", idname="wm.context_toggle", type="D",
         properties={"data_path": "scene.tool_settings.use_transform_data_origin"},
         note="D toggles Affect Only Origins"),
    dict(keymap="Window", idname="wm.context_toggle", type="TWO", ctrl=True,
         properties={"data_path": "space_data.overlay.show_wireframes"},
         note="Ctrl+2 toggles the wireframe overlay"),
    dict(keymap="Window", idname="wm.context_menu_enum", type="FOUR",
         properties={"data_path": "space_data.shading.color_type"},
         note="4 opens the viewport colour-type menu"),
    dict(keymap="Object Mode", idname="wm.tool_set_by_id", type="Q",
         properties={"name": "object_tool.select_box_xray"},
         note="Q picks the X-Ray box select tool"),
    dict(keymap="Mesh", idname="wm.tool_set_by_id", type="Q",
         properties={"name": "mesh_tool.select_box_xray"},
         note="Q picks the X-Ray box select tool"),
    # In the 3D View keymap, not Window, so it exists only where it can work:
    # view3d.toggle_xray needs a View3D space. The 3D View keymap also covers
    # every mode at once, which is what "works in Object and Edit Mode" needs.
    # The stock Alt+Z binding is left in place alongside it.
    dict(keymap="3D View", idname="view3d.toggle_xray", type="THREE", ctrl=True,
         note="Ctrl+3 toggles X-ray, in every mode"),
)

# Default bindings moved to another key, or given different properties.
# "match" locates the factory item, "to" is the wanted end state.
KEYMAP_REBIND = (
    dict(keymap="3D View", idname="view3d.view_selected",
         match=dict(type="NUMPAD_PERIOD"),
         to=dict(type="F"),
         note="Maya muscle memory: F frames the selection"),
    # The factory value of every property in "to" has to appear in "match" as
    # well, or Restore puts the key back but leaves the property changed.
    dict(keymap="3D View", idname="view3d.localview",
         match=dict(type="NUMPAD_SLASH", properties={"frame_selected": True}),
         to=dict(type="ONE", ctrl=True, properties={"frame_selected": False}),
         note="Ctrl+1 isolates, without reframing the view"),
    dict(keymap="Mesh", idname="view3d.edit_mesh_extrude_move_normal",
         match=dict(type="E"),
         to=dict(type="E", ctrl=True),
         note="Extrude moves to Ctrl+E, freeing E for the rotate tool"),
    dict(keymap="Mesh", idname="wm.call_menu",
         match=dict(type="E", ctrl=True,
                    properties={"name": "VIEW3D_MT_edit_mesh_edges"}),
         to=dict(type="E", shift=True),
         note="Edge menu moves to Shift+E to make room for extrude"),
    # Two subdivision keys on purpose, not five. 1 is the un-subdivided cage and
    # 3 is the subdivided preview -- a two-state preview toggle rather than a
    # level ladder. Level 1 is deliberately unbound; do not "complete" this row.
    dict(keymap="Object Mode", idname="object.subdivision_set",
         match=dict(type="ZERO", ctrl=True, properties={"level": 0}),
         to=dict(type="ONE"),
         note="Subdivision preview off, on plain 1"),
    dict(keymap="Object Mode", idname="object.subdivision_set",
         match=dict(type="TWO", ctrl=True, properties={"level": 2}),
         to=dict(type="THREE"),
         note="Subdivision preview on, on plain 3"),
    dict(keymap="Object Mode", idname="object.delete",
         match=dict(type="X", properties={"confirm": True}),
         to=dict(type="X", properties={"confirm": False}),
         note="X deletes without the confirmation popup"),
)

# Default bindings switched off. Mode keymaps such as Mesh, Object Mode and
# Sculpt outrank the 3D View and Window keymaps, so anything left live here
# would shadow a binding above it.
KEYMAP_DISABLE = (
    dict(keymap="Mesh", idname="mesh.edge_face_add", type="F",
         note="F is Frame Selected everywhere; gives up Make Edge/Face on F"),
    dict(keymap="Object Mode", idname="object.subdivision_set", type="ONE",
         ctrl=True, properties={"level": 1},
         note="Frees Ctrl+1 for Isolate"),
    dict(keymap="Object Mode", idname="object.subdivision_set", type="THREE",
         ctrl=True, properties={"level": 3},
         note="Redundant once subdivision moved to plain 1 and 3"),
    dict(keymap="Object Mode", idname="object.subdivision_set", type="FOUR",
         ctrl=True, properties={"level": 4},
         note="Redundant once subdivision moved to plain 1 and 3"),
    dict(keymap="Object Mode", idname="object.subdivision_set", type="FIVE",
         ctrl=True, properties={"level": 5},
         note="Redundant once subdivision moved to plain 1 and 3"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="ZERO",
         ctrl=True, properties={"level": 0},
         note="Sculpt subdivision row switched off"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="ONE",
         ctrl=True, properties={"level": 1},
         note="Frees Ctrl+1 for Isolate in Sculpt Mode"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="TWO",
         ctrl=True, properties={"level": 2},
         note="Frees Ctrl+2 for the wireframe overlay toggle"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="THREE",
         ctrl=True, properties={"level": 3},
         note="Sculpt subdivision row switched off"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="FOUR",
         ctrl=True, properties={"level": 4},
         note="Sculpt subdivision row switched off"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="FIVE",
         ctrl=True, properties={"level": 5},
         note="Sculpt subdivision row switched off"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="ONE",
         alt=True, properties={"level": -1, "relative": True},
         note="Sculpt relative subdivision switched off"),
    dict(keymap="Sculpt", idname="object.subdivision_set", type="TWO",
         alt=True, properties={"level": 1, "relative": True},
         note="Sculpt relative subdivision switched off"),
)

# ---------------------------------------------------------------------------
# Companion add-ons
# ---------------------------------------------------------------------------
# Not installed by this add-on, but the setup is incomplete without them, and
# several keymap edits documented in the repo are theirs rather than ours.
# (module, label, source, what it does)
COMPANIONS = (
    ("bl_ext.user_default.easy_transform_axis_switch",
     "Easy Transform Axis Switch", "own", "Maya W/E/R transform hotkeys"),
    ("bl_ext.user_default.remember_last_used_axis",
     "Remember Last Used Axis", "own", "RMB-drag transform on the last gizmo axis"),
    ("bl_ext.user_default.ez_uv_editor",
     "EZ UV Editor", "own", "Maya-style UV workflow"),
    ("bl_ext.blender_org.xray_selection_tools",
     "X-Ray Selection Tools", "store", "Box, lasso and circle select with X-ray"),
    ("node_wrangler", "Node Wrangler", "bundled", "Shader node shortcuts"),
)
