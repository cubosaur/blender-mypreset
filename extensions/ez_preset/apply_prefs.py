"""Apply and restore the preference, keyconfig-preference and theme entries.

Everything here walks the tables in ``profile.py``. Each setter is wrapped
because a profile written against one Blender version will meet renamed and
removed properties in the next, and one missing attribute should cost that one
line rather than the whole apply. Failures are collected and handed back so the
caller can report them instead of dying halfway through.
"""

import os

import bpy

from . import profile


def _resolve(root, path):
    """Walk a dotted path, returning (owner, attribute) or (None, None)."""
    parts = path.split(".")
    owner = root
    for part in parts[:-1]:
        owner = getattr(owner, part, None)
        if owner is None:
            return None, None
    return owner, parts[-1]


def _set(root, path, value):
    owner, attr = _resolve(root, path)
    if owner is None or not hasattr(owner, attr):
        return "missing: %s" % path
    try:
        setattr(owner, attr, value)
    except Exception as exc:
        return "%s = %r rejected (%s)" % (path, value, exc)
    return None


def _keyconfig_preferences():
    """Preferences of the active "Blender" keyconfig, or None.

    These live on the keyconfig rather than on Preferences, and the keyconfig is
    a Python add-on: it is absent under ``--factory-startup`` and briefly absent
    while Blender is still starting up.
    """
    wm = getattr(bpy.context, "window_manager", None)
    keyconfigs = getattr(wm, "keyconfigs", None) if wm else None
    if keyconfigs is None:
        return None
    kc = keyconfigs.get("Blender")
    return getattr(kc, "preferences", None) if kc else None


def _addon_preferences(module):
    addon = bpy.context.preferences.addons.get(module)
    return addon.preferences if addon else None


def _theme_xml():
    """Absolute path to the theme XML shipped by the theme extension.

    The theme is a separate extension rather than a file inside this add-on, so
    it is found through the extension repositories instead of relative to here.
    Returns None when the theme is not installed, which is not an error.
    """
    spec = profile.THEME
    for repo in bpy.context.preferences.extensions.repos:
        if not repo.enabled:
            continue
        directory = repo.directory
        if not directory:
            continue
        candidate = os.path.join(directory, spec["extension_id"], spec["xml"])
        if os.path.exists(candidate):
            return candidate
    return None


def apply_preferences():
    problems = []
    prefs = bpy.context.preferences
    for path, value, _factory, _note in profile.PREFERENCES:
        problem = _set(prefs, path, value)
        if problem:
            problems.append(problem)
    return problems


def restore_preferences():
    problems = []
    prefs = bpy.context.preferences
    for path, _value, factory, _note in profile.PREFERENCES:
        problem = _set(prefs, path, factory)
        if problem:
            problems.append(problem)
    return problems


def apply_keyconfig_preferences():
    kc_prefs = _keyconfig_preferences()
    if kc_prefs is None:
        return ["keyconfig preferences unavailable"]
    problems = []
    for attr, value, _factory, _note in profile.KEYCONFIG_PREFERENCES:
        problem = _set(kc_prefs, attr, value)
        if problem:
            problems.append(problem)
    return problems


def restore_keyconfig_preferences():
    kc_prefs = _keyconfig_preferences()
    if kc_prefs is None:
        return []
    problems = []
    for attr, _value, factory, _note in profile.KEYCONFIG_PREFERENCES:
        problem = _set(kc_prefs, attr, factory)
        if problem:
            problems.append(problem)
    return problems


def apply_addon_preferences():
    problems = []
    for module, attr, value, _factory, note in profile.ADDON_PREFERENCES:
        owner = _addon_preferences(module)
        if owner is None:
            problems.append("%s not enabled, skipped %s" % (module, attr))
            continue
        problem = _set(owner, attr, value)
        if problem:
            # A missing CUDA or HIP device is the normal case on another
            # machine, so this is reported rather than treated as a failure.
            problems.append("%s: %s (%s)" % (module, problem, note))
    return problems


def restore_addon_preferences():
    problems = []
    for module, attr, _value, factory, _note in profile.ADDON_PREFERENCES:
        owner = _addon_preferences(module)
        if owner is None:
            continue
        problem = _set(owner, attr, factory)
        if problem:
            problems.append("%s: %s" % (module, problem))
    return problems


def apply_theme():
    """Load the theme preset XML, if the theme extension is installed."""
    path = _theme_xml()
    if path is None:
        return ["theme %r not installed, skipped" % profile.THEME["name"]]
    try:
        bpy.ops.script.execute_preset(
            filepath=path,
            menu_idname="USERPREF_MT_interface_theme_presets",
        )
    except Exception as exc:
        return ["theme failed to load (%s)" % exc]
    return []


def restore_theme():
    try:
        bpy.ops.preferences.reset_default_theme()
    except Exception as exc:
        return ["theme reset failed (%s)" % exc]
    return []


def missing_companions():
    """Companion add-ons from the profile that are not currently enabled."""
    enabled = {a.module for a in bpy.context.preferences.addons}
    return [entry for entry in profile.COMPANIONS if entry[0] not in enabled]
