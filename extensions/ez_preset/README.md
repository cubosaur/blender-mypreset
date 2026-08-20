# EZ Preset

This Blender setup as an add-on. Enable it and it applies the whole personal
profile — preferences, keymap edits, theme — plus one feature Blender does not
have: `Ctrl+1` isolating the selection in Edit Mode.

Requires Blender 4.2 or newer. Captured and tested on 5.1.2.

## Install

**Edit ▸ Preferences ▸ Add-ons ▸ Install from Disk**, point it at this folder, and
enable it. It applies on first enable.

Or drop the folder into:

```
%APPDATA%\Blender Foundation\Blender\<version>\extensions\user_default\
```

## What it does

| | |
| --- | --- |
| **Preferences** | 15 values, plus 2 keyconfig preferences and 1 add-on preference |
| **Keymap** | 6 bindings added, 7 moved, 13 switched off, plus 6 expand bindings relocated to Alt |
| **Theme** | Loads Professional, if that theme extension is installed |
| **Feature** | `Ctrl+1` isolate in Edit Mode and the UV Editor; expand moves to `Alt+1/2/3` in both |

Everything it changes is one table in [`profile.py`](profile.py). Adding a
preference to the profile is one line there and nothing anywhere else.

## Layout

| File | Role |
| --- | --- |
| `profile.py` | **The data.** Every change, with its factory value. |
| `apply_prefs.py` | Preferences, keyconfig preferences, add-on preferences, theme |
| `apply_keymaps.py` | All keymap work, both keyconfigs |
| `ops_isolate.py` | The `ez_isolate.toggle` operator |
| `prefs.py` | Apply / Restore buttons and the status panel |

## Apply and Restore

**Edit ▸ Preferences ▸ Add-ons ▸ EZ Preset** has both, plus a report of anything
that could not be done on this machine and a list of missing companion add-ons.

- **Apply** is idempotent. Running it twice changes nothing the second time.
- **Restore** puts every setting the profile touches back to the Blender factory
  value. It is driven by the profile, not by a log of what was applied, so it
  cleans up a setup that was configured by hand before this add-on existed.

**Disabling the add-on does not revert anything.** It withdraws only its own
`Ctrl+1` and `Alt+1/2/3` bindings, which live in the add-on keyconfig. The
preference and keymap edits are your settings by then, and silently rolling them
back on a disable would be a nasty surprise. Use Restore for that.

`Apply on First Enable` can be turned off if you want the isolate hotkey without
adopting the preferences and theme.

## Two things worth knowing

**Applying writes to saved Preferences.** The keymap edits go into the *user*
keyconfig, because that is the only place Blender persists a keymap diff and shows
it in the UI. That is a real change to `userpref.blend`, which is why Restore
exists and why the panel reports what it did.

**Keymap ordering is not negotiable.** Blender merges the add-on keyconfig into the
active keymap only for keymaps the user keyconfig has not modified. Touching a
keymap marks it user-modified, after which add-on bindings for it never fire. So
the add-on bindings go in first, the merge is flushed with `keyconfigs.update()`,
and only then are the user-keyconfig edits applied. `apply_keymaps.py` documents
this at the top; do not reorder those calls.

## Tests

```bash
blender --background --factory-startup --python ../../tools/test_ez_preset.py
```

64 assertions: profile apply, every keymap edit in both the Mesh and UV Editor
keymaps, the isolate round trip including preservation of hand-hidden geometry,
the empty-selection refusal, and a full restore back to factory.

## Notes

- `Ctrl+Shift+1/2/3` (extend and expand) is left on `Ctrl` in both keymaps, since
  it collides with nothing. Expand therefore sits on `Alt` while extend-and-expand
  sits on `Ctrl+Shift` — deliberate, not an oversight.
- `Ctrl+2` and `Ctrl+3` over the UV Editor do nothing. `Ctrl+2` falls through to
  the Window wireframe toggle, whose data path does not resolve on an Image Editor
  space, so it returns `PASS_THROUGH` with no error. `Ctrl+3` is unbound.
- `system.gpu_backend = VULKAN` needs a Blender restart to take effect.
- Use `tools/diag_hotkey.py` to see which keymap actually wins a key.
