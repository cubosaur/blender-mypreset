# Startup file

`startup.blend` — what **File ▸ New** gives you. Saved via **File ▸ Defaults ▸ Save
Startup File**, so it is a real `.blend`, not a preference.

`ez_preset` does **not** install this. An add-on cannot replace the startup file
without writing over user data on enable, which is not a thing an add-on should do
silently. Rebuild it by hand, or commit the `.blend` here later and copy it in.

Location: `%APPDATA%\Blender Foundation\Blender\5.1\config\startup.blend`

## Scene contents

| | Mine | Factory |
| --- | --- | --- |
| Objects | `SM_Mannequin` (mesh) | Camera, Cube, Light |
| Collections | `Working`, `Final`, `Scale Reference` | `Collection` |

The default cube, camera and light are gone. In their place a UE4/UE5 mannequin as
a permanent human scale reference — which, with the Revit architectural imports
this setup is usually pointed at, is the thing you actually need on screen.

The three collections are a workflow, not decoration: `Working` for live geometry,
`Final` for what ships, `Scale Reference` for the mannequin.

## Render

| Setting | Mine | Factory |
| --- | --- | --- |
| Engine | **Cycles** | EEVEE |
| Device | GPU | CPU |
| Samples (render) | 512 | 4096 |
| Samples (viewport) | 128 | 1024 |
| Denoiser | **OptiX** | OpenImageDenoise |
| Viewport denoiser | OptiX | Auto |
| Viewport denoising | On | Off |
| Denoise start sample | 16 | 1 |
| Denoise input passses | RGB + Albedo + Normal | RGB + Albedo |
| Sampling pattern | Blue Noise | Tabulated Sobol |
| FPS | **30** | 24 |
| Motion blur | On | Off |

Samples are cut hard in both directions — 512 rather than 4096 — which with OptiX
denoising is the trade of noise floor for iteration speed. 30 fps is a video
delivery default rather than a film one.

## Snapping

The most consequential block for day-to-day modelling.

| Setting | Mine | Factory |
| --- | --- | --- |
| Snap elements | **Vertex, Edge, Grid** | Increment |
| Snap target | **Center** | Closest |
| Angle increment | **15°** | 5° |

Vertex + Edge + Grid with a Center target is CAD-style snapping, and it is on by
default in every new file. 15° rotation increments match the 15/30/45/90 muscle
memory rather than Blender's 5°.

## Viewport

Only the Layout workspace's 3D view differs from factory; Modeling and UV Editing
are stock.

| Setting | Mine | Factory |
| --- | --- | --- |
| 3D cursor | **Hidden** | Shown |
| Statistics overlay | **Shown** | Hidden |
| Cavity type | Both (screen + world) | Screen |
| Sidebar (`N`) | Open | Closed |

Hiding the 3D cursor is a Maya tell — there is no equivalent, so it is visual noise.

## Workspaces

Same 11 as factory, with two layout edits:

| Workspace | Change |
| --- | --- |
| Layout | Timeline removed — Properties, Outliner, 3D View only |
| Compositing | Outliner instead of the Image Editor |

Dropping the Timeline from Layout buys vertical viewport space, which for
architectural work matters more than scrubbing.

## Not changed

Units are stock (metric, metres). Colour management, world, and the remaining nine
workspaces are all factory.

## Rebuilding it from scratch

Only needed if the committed `.blend` is unusable, for example after a Blender
version jump that will not open it. Otherwise just install
[`startup-files/default.blend`](../startup-files/default.blend).

1. Start Blender, delete the default cube, camera and light.
2. Add the collections `Working`, `Final`, `Scale Reference`.
3. Import the UE mannequin into `Scale Reference`.
4. Set the render, snapping and viewport values above.
5. In Layout, close the Timeline area and open the sidebar.
6. **File ▸ Defaults ▸ Save Startup File**.
