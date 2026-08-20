"""Add-on preferences: the Apply and Restore buttons, and what the profile did.

The panel is a status report first and a control surface second. Applying a
profile writes to saved Preferences, which is invasive enough that it should
always be visible what was changed, what could not be changed on this machine,
and which companion add-ons are missing.
"""

import bpy
from bpy.props import BoolProperty, StringProperty
from bpy.types import AddonPreferences, Operator

from . import apply_keymaps, apply_prefs, profile

_LAST_REPORT = []


def get_prefs():
    addon = bpy.context.preferences.addons.get(__package__)
    return addon.preferences if addon else None


def _run(apply_it):
    """Apply or restore everything, returning a flat list of problems."""
    steps = (
        (apply_prefs.apply_preferences if apply_it
         else apply_prefs.restore_preferences),
        (apply_prefs.apply_keyconfig_preferences if apply_it
         else apply_prefs.restore_keyconfig_preferences),
        (apply_prefs.apply_addon_preferences if apply_it
         else apply_prefs.restore_addon_preferences),
        (apply_prefs.apply_theme if apply_it else apply_prefs.restore_theme),
        (apply_keymaps.apply_keymaps if apply_it
         else apply_keymaps.restore_keymaps),
    )
    problems = []
    for step in steps:
        try:
            problems.extend(step() or [])
        except Exception as exc:
            problems.append("%s crashed (%s)" % (step.__name__, exc))
    return problems


def apply_profile():
    global _LAST_REPORT
    _LAST_REPORT = _run(True)
    return _LAST_REPORT


def restore_profile():
    global _LAST_REPORT
    _LAST_REPORT = _run(False)
    return _LAST_REPORT


class EZPRESET_OT_apply(Operator):
    """Apply every preference, keymap and theme change in the profile"""

    bl_idname = "ez_preset.apply"
    bl_label = "Apply Profile"
    bl_options = {"REGISTER"}

    def execute(self, context):
        problems = apply_profile()
        prefs = get_prefs()
        if prefs is not None:
            prefs.applied = True
        if problems:
            self.report({"WARNING"},
                        "Profile applied with %d note(s)" % len(problems))
        else:
            self.report({"INFO"}, "Profile applied")
        return {"FINISHED"}


class EZPRESET_OT_restore(Operator):
    """Put every setting the profile touches back to the Blender default"""

    bl_idname = "ez_preset.restore"
    bl_label = "Restore Defaults"
    bl_options = {"REGISTER"}

    def execute(self, context):
        problems = restore_profile()
        prefs = get_prefs()
        if prefs is not None:
            prefs.applied = False
        if problems:
            self.report({"WARNING"},
                        "Defaults restored with %d note(s)" % len(problems))
        else:
            self.report({"INFO"}, "Defaults restored")
        return {"FINISHED"}


class EZPresetPreferences(AddonPreferences):
    bl_idname = __package__

    applied: BoolProperty(
        name="Applied",
        description="Whether the profile has been applied in this install",
        default=False,
    )
    apply_on_enable: BoolProperty(
        name="Apply on First Enable",
        description=(
            "Apply the whole profile the first time the add-on is enabled on "
            "this machine. Turn this off to keep the add-on's own hotkeys "
            "without adopting the preference and theme changes"
        ),
        default=True,
    )
    overrides: StringProperty(name="Displaced Bindings", default="")

    def draw(self, context):
        layout = self.layout

        row = layout.row(align=True)
        row.scale_y = 1.3
        row.operator(EZPRESET_OT_apply.bl_idname, icon="FILE_REFRESH")
        row.operator(EZPRESET_OT_restore.bl_idname, icon="LOOP_BACK")
        layout.prop(self, "apply_on_enable")

        box = layout.box()
        box.label(
            text="Profile: %d preferences, %d keymap edits, theme %r"
            % (len(profile.PREFERENCES) + len(profile.KEYCONFIG_PREFERENCES),
               len(profile.KEYMAP_ADD) + len(profile.KEYMAP_REBIND)
               + len(profile.KEYMAP_DISABLE),
               profile.THEME["name"]),
            icon="PRESET",
        )
        box.label(text="Ctrl+1 isolates in Edit Mode; expand moved to Alt+1/2/3",
                  icon="EVENT_CTRL")

        if _LAST_REPORT:
            box = layout.box()
            box.label(text="Last run reported:", icon="INFO")
            for line in _LAST_REPORT[:12]:
                box.label(text=line)
            if len(_LAST_REPORT) > 12:
                box.label(text="... and %d more" % (len(_LAST_REPORT) - 12))

        missing = apply_prefs.missing_companions()
        if missing:
            box = layout.box()
            box.label(text="Companion add-ons not enabled:", icon="ERROR")
            for _module, label, source, what in missing:
                box.label(text="%s  (%s) - %s" % (label, source, what))


classes = (
    EZPRESET_OT_apply,
    EZPRESET_OT_restore,
    EZPresetPreferences,
)
