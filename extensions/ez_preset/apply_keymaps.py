"""All keymap work: this add-on's own bindings, and the profile's edits.

Two different mechanisms are in play here and they are not interchangeable.

*Add-on keyconfig.* Bindings this add-on owns outright -- the Edit Mode isolate
on Ctrl+1, and the select-mode expand row relocated to Alt+1/2/3 -- go into
``keyconfigs.addon``. Blender merges that into the active keymap and, crucially,
throws it away again on unregister, so uninstalling leaves no trace.

Both the **Mesh** and **UV Editor** keymaps get these bindings. The two keymaps
carry the same three Ctrl+1/2/3 expand defaults, so treating only one of them
leaves the hotkeys meaning different things depending on which editor the pointer
happens to be over.

*User keyconfig.* The profile's own edits (moving F to Frame Selected, switching
off the Sculpt subdivision row, and so on) have to be written into
``keyconfigs.user``, because that is where Blender keeps a keymap diff and where
the Preferences UI shows it. Those writes are real changes to saved Preferences,
so each one records enough to be undone and Restore puts the factory value back.

Ordering constraint, learned the hard way: Blender merges the add-on keyconfig
into the active one only for keymaps the user keyconfig has not modified.
Touching a keymap marks it user-modified, after which add-on bindings for that
keymap sit in the add-on keyconfig and never fire. So the add-on bindings go in
first, the merge is flushed with ``keyconfigs.update()``, and only then are the
user-keyconfig edits applied.
"""

import bpy

from . import profile
from .ops_isolate import EZISO_OT_toggle

ISOLATE_KEY = "ONE"

# Keymaps this add-on owns bindings in. Both get the same treatment, because the
# same three Ctrl+1/2/3 expand bindings exist in both and the hotkeys must mean
# the same thing whichever editor the pointer is over.
OWNED_KEYMAPS = ("Mesh", "UV Editor")

# (key, select-mode) for the expand bindings the isolate hotkey displaces.
EXPAND_BINDINGS = (
    ("ONE", "VERT"),
    ("TWO", "EDGE"),
    ("THREE", "FACE"),
)
_EXPAND_KEYS = {key for key, _mode in EXPAND_BINDINGS}

_MODIFIERS = ("ctrl", "alt", "shift", "oskey")

_addon_keymaps = []


def _keyconfigs():
    wm = getattr(bpy.context, "window_manager", None)
    return getattr(wm, "keyconfigs", None) if wm else None


def _user_keymap(name):
    keyconfigs = _keyconfigs()
    if keyconfigs is None or keyconfigs.user is None:
        return None
    return keyconfigs.user.keymaps.get(name)


def _properties_match(kmi, wanted):
    props = kmi.properties
    if props is None:
        return not wanted
    for key, value in wanted.items():
        if not hasattr(props, key):
            return False
        current = getattr(props, key)
        if isinstance(value, bool):
            if bool(current) != value:
                return False
        elif isinstance(value, (int, float)) and not isinstance(value, bool):
            if abs(float(current) - float(value)) > 1e-6:
                return False
        elif current != value:
            return False
    return True


def _matches(kmi, spec, idname):
    if kmi.idname != idname:
        return False
    if kmi.type != spec.get("type", kmi.type):
        return False
    if kmi.value != spec.get("value", "PRESS"):
        return False
    for modifier in _MODIFIERS:
        if bool(getattr(kmi, modifier)) != bool(spec.get(modifier, False)):
            return False
    return _properties_match(kmi, spec.get("properties", {}))


def _find(km, spec, idname, require_active=None):
    for kmi in km.keymap_items:
        if require_active is not None and kmi.active != require_active:
            continue
        if _matches(kmi, spec, idname):
            return kmi
    return None


def _write(kmi, spec):
    kmi.type = spec.get("type", kmi.type)
    for modifier in _MODIFIERS:
        setattr(kmi, modifier, bool(spec.get(modifier, False)))
    for key, value in spec.get("properties", {}).items():
        if hasattr(kmi.properties, key):
            setattr(kmi.properties, key, value)


# ---------------------------------------------------------------------------
# This add-on's own bindings, in the add-on keyconfig
# ---------------------------------------------------------------------------

def _owned(kmi):
    if kmi.idname == EZISO_OT_toggle.bl_idname:
        return True
    return (kmi.idname == "mesh.select_mode" and kmi.alt
            and kmi.type in _EXPAND_KEYS)


def _clear_addon_items():
    for km, kmi in _addon_keymaps:
        try:
            km.keymap_items.remove(kmi)
        except (RuntimeError, ReferenceError):
            pass
    _addon_keymaps.clear()

    # Sweep strays left behind by a script reload.
    keyconfigs = _keyconfigs()
    addon_kc = keyconfigs.addon if keyconfigs else None
    if addon_kc is None:
        return
    for km_name in OWNED_KEYMAPS:
        km = addon_kc.keymaps.get(km_name)
        if km is None:
            continue
        for kmi in [i for i in km.keymap_items if _owned(i)]:
            km.keymap_items.remove(kmi)


def _add_addon_items():
    keyconfigs = _keyconfigs()
    addon_kc = keyconfigs.addon if keyconfigs else None
    if addon_kc is None:
        return
    for km_name in OWNED_KEYMAPS:
        km = addon_kc.keymaps.new(name=km_name, space_type="EMPTY",
                                  region_type="WINDOW")

        kmi = km.keymap_items.new(EZISO_OT_toggle.bl_idname, ISOLATE_KEY,
                                  "PRESS", ctrl=True)
        _addon_keymaps.append((km, kmi))

        for key, mode in EXPAND_BINDINGS:
            kmi = km.keymap_items.new("mesh.select_mode", key, "PRESS",
                                      alt=True)
            kmi.properties.type = mode
            kmi.properties.use_expand = True
            _addon_keymaps.append((km, kmi))


# ---------------------------------------------------------------------------
# The expand row Ctrl+1/2/3 that the isolate hotkey has to displace
# ---------------------------------------------------------------------------

def _is_expand_conflict(kmi):
    """True for the three Ctrl+1/2/3 expand bindings, and nothing else.

    Guards on ``shift`` so the Ctrl+Shift extend-and-expand row survives, and on
    ``any`` so a wildcard binding is never silently swallowed.
    """
    if kmi.idname != "mesh.select_mode":
        return False
    if kmi.type not in _EXPAND_KEYS or kmi.value != "PRESS":
        return False
    if kmi.key_modifier != "NONE" or kmi.any:
        return False
    if not _properties_match(kmi, {"use_expand": True}):
        return False
    return kmi.ctrl and not (kmi.shift or kmi.alt or kmi.oskey)


def _disable_expand_conflicts(record):
    for km_name in OWNED_KEYMAPS:
        km = _user_keymap(km_name)
        if km is None:
            continue
        for kmi in km.keymap_items:
            if kmi.active and _is_expand_conflict(kmi):
                kmi.active = False
                record.append((km_name, kmi.id))


# ---------------------------------------------------------------------------
# The profile's edits, in the user keyconfig
# ---------------------------------------------------------------------------

def apply_profile_keymaps(record):
    """Apply KEYMAP_ADD, KEYMAP_REBIND and KEYMAP_DISABLE. Idempotent."""
    problems = []

    for entry in profile.KEYMAP_ADD:
        km = _user_keymap(entry["keymap"])
        if km is None:
            problems.append("keymap %r missing" % entry["keymap"])
            continue
        if _find(km, entry, entry["idname"]) is not None:
            continue
        kmi = km.keymap_items.new(entry["idname"], entry["type"], "PRESS",
                                  ctrl=entry.get("ctrl", False),
                                  alt=entry.get("alt", False),
                                  shift=entry.get("shift", False))
        for key, value in entry.get("properties", {}).items():
            if hasattr(kmi.properties, key):
                setattr(kmi.properties, key, value)
        record.append(("added", entry["keymap"], kmi.id))

    for entry in profile.KEYMAP_REBIND:
        km = _user_keymap(entry["keymap"])
        if km is None:
            problems.append("keymap %r missing" % entry["keymap"])
            continue
        # Already in the wanted state, so there is nothing to move.
        if _find(km, entry["to"], entry["idname"]) is not None:
            continue
        kmi = _find(km, entry["match"], entry["idname"])
        if kmi is None:
            problems.append("%s: no %s on %s to rebind"
                            % (entry["keymap"], entry["idname"],
                               entry["match"].get("type")))
            continue
        record.append(("rebound", entry["keymap"], kmi.id))
        _write(kmi, entry["to"])

    for entry in profile.KEYMAP_DISABLE:
        km = _user_keymap(entry["keymap"])
        if km is None:
            problems.append("keymap %r missing" % entry["keymap"])
            continue
        kmi = _find(km, entry, entry["idname"], require_active=True)
        if kmi is None:
            continue
        kmi.active = False
        record.append(("disabled", entry["keymap"], kmi.id))

    return problems


def restore_profile_keymaps():
    """Put every profile edit back to its factory state.

    Driven by the profile rather than by the record of what was applied, so a
    setup that was configured by hand before this add-on existed is cleaned up
    just as well as one this add-on wrote.
    """
    problems = []

    for entry in profile.KEYMAP_ADD:
        km = _user_keymap(entry["keymap"])
        if km is None:
            continue
        kmi = _find(km, entry, entry["idname"])
        if kmi is not None:
            km.keymap_items.remove(kmi)

    for entry in profile.KEYMAP_REBIND:
        km = _user_keymap(entry["keymap"])
        if km is None:
            continue
        kmi = _find(km, entry["to"], entry["idname"])
        if kmi is None:
            continue
        target = dict(entry["match"])
        _write(kmi, target)

    for entry in profile.KEYMAP_DISABLE:
        km = _user_keymap(entry["keymap"])
        if km is None:
            continue
        kmi = _find(km, entry, entry["idname"], require_active=False)
        if kmi is not None:
            kmi.active = True

    for km_name in OWNED_KEYMAPS:
        km = _user_keymap(km_name)
        if km is None:
            continue
        for kmi in km.keymap_items:
            if not kmi.active and _is_expand_conflict(kmi):
                kmi.active = True

    return problems


# ---------------------------------------------------------------------------
# Entry points
# ---------------------------------------------------------------------------

def apply_keymaps():
    """Install our bindings, flush the merge, then edit the user keyconfig.

    Safe to call repeatedly. Existing add-on bindings are left in place rather
    than removed and re-added, because re-adding into an already user-modified
    keymap hits the merge problem described in the module docstring.
    """
    keyconfigs = _keyconfigs()
    if keyconfigs is None:
        return ["window manager not ready"]

    if not _addon_keymaps:
        _clear_addon_items()
        _add_addon_items()
        keyconfigs.update()

    record = []
    problems = apply_profile_keymaps(record)
    _disable_expand_conflicts(record)
    return problems


def restore_keymaps():
    _clear_addon_items()
    return restore_profile_keymaps()
