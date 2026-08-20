# Edit Mode Isolate — `Ctrl+1`

In Object Mode, `Ctrl+1` is `view3d.localview`: isolate the selected objects. This
adds the Edit Mode equivalent, so the key means the same thing in both modes.

Press it with faces selected and you get:

1. Only those faces visible in the 3D viewport.
2. UV Sync Selection off, so the UV Editor shows just that island instead of every
   UV in the model.
3. Those UVs selected, ready to grab.

Press it again and all three revert.

Operator: `ez_isolate.toggle`, in
[`ops_isolate.py`](../extensions/ez_preset/ops_isolate.py).

---

## Why it could not be a keymap change

Local View isolates **objects**. There is no object-level equivalent for "these
four faces", so the Edit Mode version has to be hide/reveal, and hide/reveal has no
toggle operator — `mesh.hide` and `mesh.reveal` are one-way. Anything that
remembers which state you were in needs code.

`Ctrl+1` was also not free. Blender's **Mesh** keymap binds it to
`mesh.select_mode` with `use_expand`, and Mesh outranks the `3D View` keymap that
holds Local View, so a new binding on `Ctrl+1` would never have been reached. That
expand row moved to `Alt+1/2/3` — see [keymap.md](keymap.md).

## Reversing exactly, not approximately

The obvious implementation is `mesh.hide(unselected=True)` on the way in and
`mesh.reveal()` on the way out. That is wrong: `reveal` unhides **everything**,
including geometry you had hidden by hand with `H` before you ever pressed
`Ctrl+1`. Isolating and un-isolating would quietly resurrect it.

So the toggle snapshots the hidden state first. Before hiding anything it records,
per mesh, the indices of every hidden vert, edge and face, as ID properties on the
mesh data-block:

```
ez_isolate_counts      [verts, edges, faces]  — staleness guard
ez_isolate_hide_vert   [indices…]
ez_isolate_hide_edge   [indices…]
ez_isolate_hide_face   [indices…]
```

Restoring clears every hide flag and re-applies those three lists directly.

**Why all three domains.** Blender's hide flags are not derivable from one another.
Hide a single face in face mode and its verts stay visible, because neighbouring
faces still use them — so a face-only snapshot would under-restore, and a
vert-only snapshot would over-restore. Recording all three and writing all three
back sidesteps the problem entirely: the snapshot was a consistent state, so
reproducing it verbatim is also consistent. That is why the restore path sets
`elem.hide` directly rather than going through `mesh.hide`, which would try to
propagate and get it wrong.

**Staleness.** Element indices only mean something while the topology holds still.
If you delete or add geometry while isolated, the stored indices point at the wrong
elements. `ez_isolate_counts` catches that: on mismatch the toggle reveals
everything and reports a warning rather than corrupting the visibility state.

## Where the state lives

On the data, not in a module global:

| State | Stored on | Why there |
| --- | --- | --- |
| Hidden-element snapshot | The **mesh** | Per-object, and survives undo and file save |
| Previous UV sync value | The **scene** | It is a scene tool setting |
| "Am I isolated?" | Implied by the snapshot | Cannot disagree with what is on screen |

There is no separate boolean for "isolated". A mesh is isolated exactly when it
carries a snapshot, which removes a whole class of desync bug — no flag can be left
`True` after an undo rolled the hide flags back. It also means the toggle survives
leaving Edit Mode and coming back, and reloading the file.

With multiple objects in Edit Mode the toggle restores only when **every** edit
mesh carries a snapshot; otherwise it treats the press as a fresh isolate.

## UV Sync Selection

Turning sync off is what makes the UV Editor show one island instead of the whole
model. Blender then keeps a **separate** UV selection, which is usually empty or
left over from earlier — so a bare unsync often looks like the isolate failed.

The toggle therefore runs `uv.select_all(action='SELECT')` afterwards. That needs a
UV Editor on screen and a context override to reach it; if no UV Editor is open the
step is skipped, since there is nothing to show. The area search prefers the active
window, so driving the toggle on one monitor does not reach across to a UV Editor
on another.

## Behaviour notes

- **Nothing selected** → refuses with a warning, rather than hiding the entire
  mesh, which is not a state you can get out of with the same key.
- **Object Mode** → `poll` returns `False`; `Ctrl+1` falls through to Local View as
  before.
- **Undo** → the operator is `{'REGISTER', 'UNDO'}` and all its state is on mesh
  and scene data, so one `Ctrl+Z` rolls back the visibility, the snapshot and the
  sync flag together.
- **Selection on restore** → left as you left it. Previously hidden geometry comes
  back deselected, which is how Blender's own reveal behaves.
- **Cost** → snapshotting is three Python passes over the BMesh. Negligible on
  normal meshes; expect a fraction of a second on the million-element imports this
  setup is often pointed at.

## Tests

[`tools/test_ez_preset.py`](../tools/test_ez_preset.py) covers the toggle
headlessly, including the case that motivated the snapshot design — hide a face by
hand, isolate two others, toggle back, and assert the hand-hidden face is still
hidden:

```bash
blender --background --factory-startup --python tools/test_ez_preset.py
```

41 assertions, covering the isolate round trip, the empty-selection refusal, the
Object Mode poll, and the full profile apply/restore cycle.
