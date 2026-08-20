# Startup files

Saved startup `.blend` files. One is active at a time — whichever sits at
Blender's `config/startup.blend` is what **File ▸ New** gives you.

| File | Contents | Size |
| --- | --- | --- |
| [`default.blend`](default.blend) | UE mannequin scale reference, three-collection workflow, Cycles on GPU, CAD-style snapping | 3.3 MB |

`default.blend` is the live one, copied from Blender 5.1 on 2026-08-20. What is
inside it, and why, is in [`docs/startup-file.md`](../docs/startup-file.md).

The folder is set up to hold alternatives — a lighter one for quick modelling, a
heavier one for archviz, a sculpting one. Add the file, add a row above, and say
what it is for.

## Install one

`ez_preset` deliberately does **not** install these. An add-on replacing the
startup file on enable would overwrite user data silently, which is not something
an add-on should do. So this is a manual copy.

**The safe way, inside Blender:**

1. **File ▸ Open**, pick the file from this folder.
2. **File ▸ Defaults ▸ Save Startup File**.

That writes Blender's own `startup.blend` for you, in the running version's
format.

**The direct way**, replacing the file on disk:

```bash
cp startup-files/default.blend "$APPDATA/Blender Foundation/Blender/5.1/config/startup.blend"
```

Back up the existing one first, and close Blender before you do it — Blender
writes `startup.blend` on **File ▸ Defaults ▸ Save Startup File** and can
overwrite your copy.

## Reverting

**File ▸ Defaults ▸ Load Factory Startup File**, then **File ▸ Defaults ▸ Save
Startup File**. Or just delete `config/startup.blend`; Blender falls back to the
built-in default.

## A note on versions

A `.blend` saved by a newer Blender does not open in an older one. `default.blend`
is a 5.1 file. Blender upgrades these on load and will re-save in the current
format, so after a version jump it is worth re-exporting the file back into this
folder rather than leaving a stale one here.
