"""EZ Preset - this Blender setup, as an add-on.

Enable it on a fresh install and it applies the whole personal profile: the
preference changes, the keymap edits, the theme, and one feature Blender does not
have -- ``Ctrl+1`` isolating the selection in Edit Mode the way it isolates
objects in Object Mode.

Registration happens in two passes. The first runs inside ``register()`` and
catches the normal case of enabling the add-on from Preferences. The second runs
from a timer a fraction of a second later, because when Blender enables add-ons
during startup the user keyconfig is still empty at ``register()`` time and there
is nothing there to edit yet.
"""

import bpy

from . import apply_keymaps, apply_prefs, ops_isolate, prefs, profile

_registered = False
_applied_this_session = False


def _apply_profile_once():
    """Do the full apply the first time only. Returns True if it ran.

    Applying writes to saved Preferences, so doing it on every load would
    silently undo any later hand tweak. ``applied`` lives in the add-on
    preferences, so it persists per install and the first launch on a new
    machine is what triggers the apply.
    """
    global _applied_this_session
    addon_prefs = prefs.get_prefs()
    if addon_prefs is None:
        return False
    if _applied_this_session:
        return False
    if not (addon_prefs.apply_on_enable and not addon_prefs.applied):
        return False
    _applied_this_session = True
    prefs.apply_profile()
    addon_prefs.applied = True
    return True


def _sync():
    """Put our keymap state in place. Idempotent, and safe to call twice.

    Must stay callable more than once per launch. When Blender enables add-ons
    during startup the user keyconfig can still be empty at ``register()`` time,
    and a keymap edit against an empty keyconfig silently does nothing. The
    timer below calls this again once the UI is up, which is the pass that
    actually lands the edits on a normal launch.
    """
    if _apply_profile_once():
        return
    apply_keymaps.apply_keymaps()


def _deferred(*_args):
    if _registered:
        _sync()
    return None


classes = ops_isolate.classes + prefs.classes


def register():
    global _registered, _applied_this_session
    for cls in classes:
        bpy.utils.register_class(cls)
    _registered = True
    _applied_this_session = False

    _sync()

    if not bpy.app.background:
        bpy.app.timers.register(_deferred, first_interval=0.25)


def unregister():
    global _registered
    _registered = False
    if bpy.app.timers.is_registered(_deferred):
        bpy.app.timers.unregister(_deferred)

    # Only this add-on's own bindings are withdrawn. The profile's preference
    # and keymap edits are left in place: they are the user's settings now, and
    # silently reverting them on a disable would be a nasty surprise. The
    # Restore Defaults button in the add-on preferences is the way back.
    apply_keymaps._clear_addon_items()

    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
