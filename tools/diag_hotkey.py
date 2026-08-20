"""Show every keymap that claims a key, in priority order, and mark the winner.

Blender resolves a keypress through the most specific keymap first, and nothing in
the Preferences UI shows that ordering. So a binding can look correct, sit in the
keymap editor exactly as you left it, and still never fire because a
higher-priority keymap claims the same key. This prints the whole chain.

Run it against the real config, with the add-on enabled, to see what actually
happens:

    blender --background --python tools/diag_hotkey.py

Set EZ_DIAG_KEYS to a comma-separated list of key types to check other keys, and
EZ_DIAG_MODS to the modifier set:

    EZ_DIAG_KEYS=F,ONE,TWO EZ_DIAG_MODS=ctrl blender --background --python tools/diag_hotkey.py
"""

import os
import sys

import bpy

MODULE = "bl_ext.user_default.ez_preset"

KEYS = os.environ.get("EZ_DIAG_KEYS", "ONE,TWO,THREE").split(",")
MODS = [m for m in os.environ.get("EZ_DIAG_MODS", "ctrl").split(",") if m]
ALL_MODS = ("ctrl", "alt", "shift", "oskey")

# Rough priority order, highest first. Tool keymaps sit above all of these; they
# rarely matter for modified keys, which is why they are left out.
CONTEXTS = {
    "3D VIEWPORT, MESH EDIT MODE": [
        "Mesh", "Object Non-modal", "Frames",
        "3D View Generic", "3D View", "Screen", "Window",
    ],
    "3D VIEWPORT, OBJECT MODE": [
        "Object Mode", "Object Non-modal", "Frames",
        "3D View Generic", "3D View", "Screen", "Window",
    ],
    "UV EDITOR": [
        "UV Editor", "Image", "Image Generic", "Frames", "Screen", "Window",
    ],
}


def enable_addon():
    """Enable the add-on, then apply, so the diagnosis matches the GUI.

    The apply has to run *after* ``keyconfig_init()`` and it has to run even when
    the add-on is already enabled. In background mode Blender enables add-ons
    before the keymaps exist, so the add-on's own startup pass finds an empty
    user keyconfig and lands nothing. Skipping the apply here reports bindings as
    missing when they are merely not applied yet.
    """
    bpy.utils.keyconfig_init()
    try:
        if MODULE not in {a.module for a in bpy.context.preferences.addons}:
            bpy.ops.preferences.addon_enable(module=MODULE)
        ezprefs = sys.modules.get(MODULE + ".prefs")
        if ezprefs is None:
            print("%s enabled but its prefs module is missing" % MODULE)
            return
        notes = ezprefs.apply_profile()
        print("apply notes:", notes or "none")
    except Exception as exc:
        print("could not apply %s (%s); showing unmodified state" % (MODULE, exc))


def describe_properties(kmi):
    if not kmi.properties:
        return ""
    bits = []
    for prop in kmi.properties.bl_rna.properties:
        if prop.identifier == "rna_type":
            continue
        if kmi.properties.is_property_set(prop.identifier):
            bits.append("%s=%r" % (prop.identifier,
                                   getattr(kmi.properties, prop.identifier)))
    return (" {" + ", ".join(bits) + "}") if bits else ""


def combo(key):
    return "+".join([m.capitalize() for m in MODS] + [key])


def report(user, label, order):
    print()
    print("=" * 78)
    print(label)
    print("=" * 78)
    for key in KEYS:
        print()
        print("--- %s ---" % combo(key))
        winner = None
        for km_name in order:
            km = user.keymaps.get(km_name)
            if km is None:
                continue
            for kmi in km.keymap_items:
                if kmi.type != key:
                    continue
                if any(bool(getattr(kmi, m)) != (m in MODS) for m in ALL_MODS):
                    continue
                mark = ""
                if kmi.active and winner is None:
                    winner = (km_name, kmi.idname)
                    mark = "   <== WINS"
                print("   %s %-22s %-34s%s%s"
                      % ("ACTIVE " if kmi.active else "off    ",
                         km_name, kmi.idname, describe_properties(kmi), mark))
        print("   RESULT:", winner or "nothing bound -> falls through")


enable_addon()
user = bpy.context.window_manager.keyconfigs.user
print("keymaps:", len(user.keymaps),
      "items:", sum(len(k.keymap_items) for k in user.keymaps))
for label, order in CONTEXTS.items():
    report(user, label, order)
print()
print("Preferences were not saved.")
