"""Edit Mode isolate: hide everything but the selection, and unsync the UVs.

``Ctrl+1`` already means isolate in Object Mode (``view3d.localview``). This is
the Edit Mode half of the same muscle memory: the current selection becomes the
only visible geometry and UV Sync Selection switches off, so the UV Editor shows
the isolated island instead of every UV in the model. Press it again and both go
back to how they were.

State lives on the data rather than in a module global, so it survives undo, a
file save and a trip out of Edit Mode: each mesh carries the snapshot needed to
restore its own hide flags, and the scene remembers the UV sync flag. A mesh is
"isolated" precisely when it carries a snapshot, which means the toggle can never
disagree with what is on screen.
"""

import bmesh
import bpy
from bpy.types import Operator

KEY_COUNTS = "ez_isolate_counts"
KEY_HIDE_VERT = "ez_isolate_hide_vert"
KEY_HIDE_EDGE = "ez_isolate_hide_edge"
KEY_HIDE_FACE = "ez_isolate_hide_face"
KEY_PREV_UV_SYNC = "ez_isolate_prev_uv_sync"

_SNAPSHOT_KEYS = (KEY_COUNTS, KEY_HIDE_VERT, KEY_HIDE_EDGE, KEY_HIDE_FACE)


def edit_meshes(context):
    """Meshes currently open in Edit Mode, de-duplicated by data-block."""
    objects = getattr(context, "objects_in_mode_unique_data", None)
    if not objects:
        obj = context.edit_object
        objects = [obj] if obj is not None else []
    return [o for o in objects if o.type == "MESH"]


def is_isolated(mesh):
    return KEY_COUNTS in mesh


def _clear_snapshot(mesh):
    for key in _SNAPSHOT_KEYS:
        if key in mesh:
            del mesh[key]


def _take_snapshot(mesh):
    """Record which elements are hidden *before* the isolate.

    Blender's ``mesh.reveal`` unhides everything, which would throw away
    geometry the user had hidden by hand earlier. Storing the hidden indices
    per domain lets the toggle put back exactly what it found.
    """
    bm = bmesh.from_edit_mesh(mesh)
    mesh[KEY_COUNTS] = [len(bm.verts), len(bm.edges), len(bm.faces)]
    mesh[KEY_HIDE_VERT] = [i for i, v in enumerate(bm.verts) if v.hide]
    mesh[KEY_HIDE_EDGE] = [i for i, e in enumerate(bm.edges) if e.hide]
    mesh[KEY_HIDE_FACE] = [i for i, f in enumerate(bm.faces) if f.hide]


def _restore_snapshot(mesh):
    """Put the hide flags back, and report whether the snapshot still fit.

    All three domains are restored from one snapshot that was itself
    consistent, so there is no need to propagate hiding from verts out to
    faces the way Blender's own hide operator does. If the topology changed
    while isolated the stored indices no longer mean anything, so everything
    is simply revealed and the caller warns.
    """
    bm = bmesh.from_edit_mesh(mesh)
    counts = [len(bm.verts), len(bm.edges), len(bm.faces)]
    stale = list(mesh[KEY_COUNTS]) != counts

    for seq in (bm.verts, bm.edges, bm.faces):
        for elem in seq:
            elem.hide = False

    if not stale:
        for seq, key in ((bm.verts, KEY_HIDE_VERT),
                         (bm.edges, KEY_HIDE_EDGE),
                         (bm.faces, KEY_HIDE_FACE)):
            seq.ensure_lookup_table()
            for index in mesh[key]:
                seq[index].hide = True

    bmesh.update_edit_mesh(mesh)
    _clear_snapshot(mesh)
    return stale


def _find_uv_area(context):
    """Largest UV Editor on screen as (window, area, region), else Nones.

    Areas in the active window win, so driving the toggle from one window does
    not reach across to a UV Editor on another monitor.
    """
    best = (None, None, None)
    best_key = (-1, -1)
    for window in context.window_manager.windows:
        screen = window.screen
        if screen is None:
            continue
        for area in screen.areas:
            if area.type != "IMAGE_EDITOR":
                continue
            space = area.spaces.active
            if space is None or getattr(space, "mode", None) != "UV":
                continue
            region = next((r for r in area.regions if r.type == "WINDOW"), None)
            if region is None:
                continue
            key = (1 if window == context.window else 0, area.width * area.height)
            if key > best_key:
                best_key = key
                best = (window, area, region)
    return best


def _select_all_uvs(context):
    """Select every visible UV so the isolated island is ready to grab.

    Turning sync off hands the UV Editor its own selection, which is usually
    empty or stale from an earlier session. Without this the isolate looks like
    it failed even though the right UVs are the only ones on display. Needs a
    UV Editor to be open, and there is nothing to select if there is not one.
    """
    window, area, region = _find_uv_area(context)
    if area is None:
        return
    with context.temp_override(window=window, area=area, region=region):
        try:
            bpy.ops.uv.select_all(action="SELECT")
        except RuntimeError:
            pass


class EZISO_OT_toggle(Operator):
    """Isolate the selection and unsync the UVs, or undo both"""

    bl_idname = "ez_isolate.toggle"
    bl_label = "Isolate Selection"
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode == "EDIT_MESH"

    def execute(self, context):
        meshes = [o.data for o in edit_meshes(context)]
        if not meshes:
            self.report({"WARNING"}, "No mesh in Edit Mode")
            return {"CANCELLED"}

        if all(is_isolated(m) for m in meshes):
            return self._restore(context, meshes)
        return self._isolate(context, meshes)

    def _isolate(self, context, meshes):
        if not any(m.total_vert_sel for m in meshes):
            self.report({"WARNING"}, "Nothing selected to isolate")
            return {"CANCELLED"}

        # Snapshot every mesh before the operator runs: mesh.hide invalidates
        # the BMesh wrappers, so there is no reading them afterwards.
        for mesh in meshes:
            if not is_isolated(mesh):
                _take_snapshot(mesh)

        bpy.ops.mesh.hide(unselected=True)

        tool_settings = context.scene.tool_settings
        context.scene[KEY_PREV_UV_SYNC] = tool_settings.use_uv_select_sync
        tool_settings.use_uv_select_sync = False
        _select_all_uvs(context)

        return {"FINISHED"}

    def _restore(self, context, meshes):
        stale = [m.name for m in meshes if _restore_snapshot(m)]

        scene = context.scene
        if KEY_PREV_UV_SYNC in scene:
            context.scene.tool_settings.use_uv_select_sync = bool(
                scene[KEY_PREV_UV_SYNC]
            )
            del scene[KEY_PREV_UV_SYNC]

        if stale:
            self.report(
                {"WARNING"},
                "Topology changed while isolated, revealed all: "
                + ", ".join(stale),
            )
        return {"FINISHED"}


classes = (EZISO_OT_toggle,)
