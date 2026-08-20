# Theme

**Professional** 1.0.3 by [kame404](https://github.com/kame404/Blender-Themes),
installed from extensions.blender.org.

Not hand-edited. Diffing the saved theme against a fresh load of the shipped
`Professional.xml` gives **10** differences, and none of them are colour choices —
see below.

`ez_preset` applies it by loading the XML preset from whichever extension
repository has the theme installed. If the theme is not installed the step is
skipped with a note rather than failing, so the rest of the profile still applies.

## The 10 differences

Seven are one setting each across RGB channels, so really three settings plus a
path:

| Field | Theme XML says | Saved value | |
| --- | --- | --- | --- |
| `view_3d.grid_major` | `#3a3a3a` | `#545454` | Blender factory value |
| `view_3d.gp_wire_edit` | `#7a7a7a` | `#999999` | Blender factory value |
| `preferences.match` | `#0c4a6e` | `#4772b3` | Blender factory value |
| `filepath` | — | points at the **5.0** extensions folder | stale path |

All three colours match **Blender's factory defaults**, not anything chosen by
hand. The theme was applied while this machine was on Blender 5.0; the 5.0 → 5.1
preference migration reset those three fields to factory while leaving the other
747 alone. The `filepath` still pointing at `…/Blender/5.0/extensions/…` is the
fingerprint — even though the 5.0 and 5.1 copies of `Professional.xml` are
byte-identical (`md5 35c9647c…`).

So: cosmetic drift from a version upgrade, not customisation. Re-applying the theme
in 5.1 would close all four gaps. Worth doing, but nothing is visibly wrong.

## Also installed, not active

| Theme | Version | Author |
| --- | --- | --- |
| Dark Pro | 2.0.3 | Mahdi Shalchian |
| DarkPurpleGreen | 1.0.1 | MSBH |
| Shadow | 5.0.2 | Shadow |

All four are dark themes, which is the only real preference on display here.

## Reproducing the comparison

The check is worth keeping, because "did I actually customise this theme, or is it
stock?" is not answerable by looking at it:

```bash
# 1. dump the saved theme
blender --background --python tools/dump_config.py

# 2. dump a clean load of the theme XML on factory settings
blender --background --factory-startup --python tools/dump_theme_xml.py
```

Then diff the two flattened trees. Anything left is either a real edit or, as here,
migration drift.
