# Scroll case config reference

Scroll cases are configured with a TOML file passed to `scrollcase build -c`.
Every key is optional; anything left out comes from the config's style
preset. Print a style's complete config:

```bash
uv run scrollcase defaults --style educelab.v1 > my-scroll.toml
```

Unknown keys are an error, so typos don't silently fall back to defaults.
Combinations that can't be built are also rejected when the config loads
(see [Valid combinations](#valid-combinations)). Lengths are in millimeters
and angles in degrees.

## Styles

`style` picks a preset of defaults for every key below. Your own values
override the preset key by key, so `[shell] type = "solid"` keeps the rest of
the preset's `[shell]` settings.

| Style | Description |
|---|---|
| `educelab.v1` | The default: honeycomb shell with floor and lid, flat split, Generic Mount Disc, stand. The former OpenSCAD generator's design. |
| `villa.2026-10` | [ScrollPrize/villa's case](https://github.com/ScrollPrize/villa/tree/main/foundation/scrollcase) at commit `7d6a82c` (2026-10-01): no shell, curved split ending in round posts, square bolted caps with upstream's label layout, kinematic mount disc, 3 mm margins, no stand. |

Components mix freely within the [valid combinations](#valid-combinations),
e.g. villa's caps and kinematic disc around a honeycomb shell:

```toml
style = "educelab.v1"
[split]
type = "curve"
[ends]
type = "caps"
[mount]
type = "kinematic"
[stand]
enabled = false
```

Known differences from upstream in `villa.2026-10`: the scroll fit uses a
tighter tolerance (upstream's stops about 1° off-axis and oversizes the
radius by about 1 mm), the wide-axis rotation normalizes its vector before
taking the angle, `voxel_size` is absolute (upstream uses 0.4% of the mesh
diagonal), and `"denoise"` smoothing uses `smoothing_amount` (upstream
ignores its strength setting).

Released styles never change, so a config rebuilds the same case for as
long as it names the same style. A design update becomes a new version
(e.g. `educelab.v2`). Omitting `style` means `educelab.v1`, permanently.

**Case coordinates.** The case axis is +Z and the bottom of the shell is
Z=0; the mount disc sits below it, from Z=-12.5 to 0. The halves split on the
XZ plane: the left half (with the mount disc) is on the -Y side and the right
half is on the +Y side.

## Top level

| Key | Default | Description |
|---|---|---|
| `style` | `"educelab.v1"` | Preset to resolve the rest of the config against. See [Styles](#styles). |
| `name` | `"Scroll Case"` | Output file prefix: `<name>-L.stl`, `-R.stl`, `-Stand.stl`, `-Scroll.stl`. Overridden by `--name`. |
| `lining_offset` | `2.0` | Clearance between the scroll surface and the inside of the lining. Also the gap above and below the scroll. |
| `wall_thickness` | `2.0` | Thickness of the lining wall, shell, lid, and half of the divider. The floor is `max(2, wall_thickness)`. |
| `bottom_buffer` | `5.0` | Gap between the floor and the bottom of the lining. |
| `top_buffer` | `5.0` | Gap between the top of the lining and the lid. |
| `internal_gap` | `3.0` | Radial gap between the lining and the inside of the shell. |
| `overhang_removal` | `true` | Extrudes each half's cavity toward the split so the scroll can be lowered straight in. Turn off only to inspect the raw lining. |
| `voxel_size` | `0.4` | Resolution of the lining offsets and overhang removal. Smaller is more faithful but slower and uses more memory; the PHercParis scrolls peaked at 3.5–5 GB at 0.4. |

## `[scroll]`

The input mesh and how it is prepared and placed.

| Key | Default | Description |
|---|---|---|
| `mesh` | none | Scroll mesh (PLY, STL, or OBJ). A relative path is resolved against the config file. Overridden by the positional `mesh` argument. If unset, a generic cylinder is used. |
| `scale` | `1.0` | Multiplies the mesh coordinates. Use it if the mesh isn't in millimeters. |
| `auto_align` | `true` | Fits the smallest cylinder that encloses the scroll, stands the scroll up along +Z with its bottom at Z=0, and turns its widest direction into the split plane. With `false`, the mesh keeps its own orientation (its Z axis becomes the case axis) but is still centered on the axis with its bottom at Z=0. |
| `rotate` | `[0, 0, 0]` | Extra rotation in degrees about the X, then Y, then Z axes, applied after alignment. The scroll is then re-centered on the case axis, so only the orientation changes. Z spins the scroll about the case axis, e.g. `[0, 0, 90]` puts the widest direction across the split instead of in it. X/Y tilt it; the case grows to enclose the tilted scroll. |
| `translate` | `[0, 0, 0]` | Offset applied after re-centering. An X/Y offset deliberately moves the scroll off the case axis, and the case grows to enclose it. Z has no effect, because the scroll is always placed `lining_offset` above the cavity floor. |
| `decimate_max_error` | `0.05` | How far, at most, the simplified input mesh may deviate from the original. |
| `smoothing` | `"none"` | Simplifies a very detailed lining: `"denoise"` or `"shrink_expand"`. The smoothed result is merged with the original, so smoothing never cuts into the scroll. |
| `smoothing_amount` | `2.0` | For `"denoise"`, the smoothing strength (meshlib `gamma`). For `"shrink_expand"`, the shrink/expand distance in mm; larger values round off more detail. |
| `generic_diameter` | `76.0` | Diameter of the generic cylinder used when `mesh` is unset. |
| `generic_height` | `155.0` | Height of the generic cylinder used when `mesh` is unset. |

## `[split]`

The surface the two halves separate along. Every split is a profile
y = f(x) extruded along Z, so from anywhere in a half the scroll can move
straight along Y to the split; overhang removal relies on this.

| Key | Default | Description |
|---|---|---|
| `type` | `"plane"` | `"plane"`: the XZ plane. `"curve"`: ScrollPrize/villa's S-shaped split, made of two arcs, spanning the whole case out to the middle of the shell wall. A curved seam avoids a flat interface lined up with the beam, which shows up as a streak in CT. |
| `amplitude` | unset | How far the S bulges from the XZ plane. Unset means 0.2 × (span + `wall_thickness`), as upstream, where the span is the radius at the middle of the shell wall. Too large an amplitude is an error. |
| `flip` | `false` | Mirrors the S. |

With a curved split the divider follows the curve at constant thickness,
and nubs move along Y to sit on it.

## `[shell]`

The outer cylinder around the lining, including its floor and lid.

| Key | Default | Description |
|---|---|---|
| `type` | `"honeycomb"` | `"honeycomb"` (hexagonal cutouts), `"solid"`, or `"none"`. With `"none"` the case is just the lining, divider, and ends, as upstream; the divider then ends in round posts at the cavity edge. |
| `open_top` | `false` | Cuts away the upper shell on both sides, leaving an open cradle around the lining. |
| `marker_rings` | `true` | Raised rings at the cavity bottom, scroll bottom, scroll middle, scroll top, and cavity top. |

### `[shell.honeycomb]`

Hexagonal cutouts, used when `shell.type = "honeycomb"`. The floor, lid,
marker ring bands, and divider stay solid.

| Key | Default | Description |
|---|---|---|
| `hole_edges` | `6` | Number of sides on each hole. |
| `columns` | `12` | Holes around the circumference. Alternate rows are offset by half a column. |
| `spacing` | `1.5` | Width of the strips between holes. |

## `[ends]`

What closes the top and bottom of the case.

| Key | Default | Description |
|---|---|---|
| `type` | `"shell"` | `"shell"`: the shell's own floor and lid. `"caps"`: villa's square end caps, sized to the larger of the case and the mount disc. Bolts through tabs on both sides clamp the halves together; the bottom cap has counterbored mounting holes and an engraved arrow; the top cap carries the label. |
| `cap_height` | `10.0` | Cap thickness. Also the width of the bolt tabs. |
| `corner_fillet` | `6.25` | Radius of the caps' corners. |
| `bolt_hole_diameter` | `5.0` | Clamping bolt clearance hole (M4, loose). |
| `bolt_counterbore_diameter` | `8.0` | Bolt head counterbore, on the +Y face of each tab. |
| `bolt_counterbore_depth` | `2.0` | |
| `nut_diameter` | `9.0` | Hex nut pocket, across corners, on the -Y face of each tab. |
| `nut_depth` | `3.5` | |
| `mount_hole_spacing` | `50.0` | Mounting holes in the bottom cap at (±spacing, ±spacing). |
| `mount_hole_diameter` | `6.8` | Mounting bolt clearance hole (M6). |
| `mount_counterbore_diameter` | `10.5` | Counterbored from the inside face of the bottom cap. |
| `mount_counterbore_depth` | `5.0` | |

The `cap_*`, `bolt_*`, `nut_*`, and `mount_*` keys only apply to caps.

## `[mount]`

The mount that attaches the left half to the scanner.

| Key | Default | Description |
|---|---|---|
| `type` | `"generic-112.5"` | `"generic-112.5"` or `"generic-65"`: the Generic Mount Disc of that diameter, matching `OpenSCAD/Generic Mount Disc*.scad`, with an orientation notch on its rim. `"kinematic"`: villa's 112.5 × 10 mm disc with three V-slots for a kinematic mount; the right half's side of its top is lowered 0.5 mm so the right half doesn't bind on it. `"none"`: no mount. |

## `[nubs]`

Alignment nubs on the left half's split face, with matching sockets on the
right half. Place them on the divider, outside the cavity and inside the
case: the build fails, naming the nub, if one isn't. `scrollcase build`
prints the lining and shell diameters. On a curved split each nub sits at
(x, f(x), z), still pointing along Y, with its base sunk into the divider so
it stays attached where the surface slopes.

| Key | Default | Description |
|---|---|---|
| `positions` | `[]` | `[x, z]` pairs, e.g. `[[-44, 20], [44, 150]]`. The nub is placed at X = -x, as in the old OpenSCAD generator. Odd-numbered entries (the 2nd, 4th, …) are rotated 45° into diamonds. |
| `size` | `4.0` | Width and height of each nub. |
| `depth` | `1.5` | How far each nub sticks out from the split face. |
| `margin` | `0.5` | Clearance on every side of the socket. |

## `[escape_holes]`

Four holes per half: two through the floor and two through the lid, placed at
±`angle` from the X axis in the gap between the lining and the shell. On the
left half, the floor holes go through the mount disc as well.

| Key | Default | Description |
|---|---|---|
| `enabled` | `false` | Adds the holes. |
| `offset` | `1.5` | Moves the holes outward from halfway between the lining and the shell. Holes that would be tangent to a shell surface are nudged inward by 0.1 mm. |
| `diameter` | `4.0` | Hole diameter. |
| `angle` | `15.0` | Angle of each hole from the X axis, in degrees. |

## `[label]`

With shell ends, the label is engraved on the bottom of the mount disc (left
half) and the bottom of the shell (right half), mirrored so it reads
correctly from below. It is also engraved on the stand's back plate, on the
face toward the case. With caps it goes on the top cap in upstream's layout:
`line1` once on each half, `line2`, and a generated `<lining D> x <cavity H>`
line.

| Key | Default | Description |
|---|---|---|
| `line1` | `""` | First line. Empty lines are skipped. |
| `line2` | `""` | Second line, placed 1.5 × `height` below the first. |
| `height` | `5.0` | Font size. |
| `depth` | `0.5` | Engraving depth. |
| `font` | `"Arial Rounded MT Bold"` | System font name. If the font isn't installed, Arial is used instead. OpenCASCADE's warning about this is hidden when the build succeeds. |

## `[stand]`

Cradle that holds the left half upright on its mount disc during assembly.

| Key | Default | Description |
|---|---|---|
| `enabled` | `true` | Builds `<name>-Stand.stl`. `--parts` defaults to `left,right`, plus `stand` when this is on. |
| `length_scale` | `1.0` | Stand length as a fraction of the case height. The top cradle moves with it. |

## Valid combinations

These are checked when the config loads, and the error names the keys
involved.

| Rule | Why |
|---|---|
| `ends.type = "shell"` requires a shell | The floor and lid are part of the shell. |
| `shell.marker_rings` requires `shell.type = "honeycomb"` | The rings fill bands of the honeycomb. |
| `shell.open_top` requires `ends.type = "shell"` | It cuts away the shell's lid. |
| `escape_holes` require a shell | They sit in the gap between the lining and the shell. |
| `stand.enabled` requires a `generic-*` mount and `ends.type = "shell"` | The cradle is shaped around the Generic Mount Disc, its notch, and the round shell. |

## How the dimensions stack up

From the fitted scroll radius `r` and height `h`:

```
cavity diameter   = 2 (r + lining_offset)
lining diameter   = cavity diameter + 2 wall_thickness
shell inner diam. = lining diameter + 2 internal_gap
case diameter     = shell inner diam. + 2 wall_thickness

case height = floor + bottom_buffer
            + wall_thickness + (h + 2 lining_offset) + wall_thickness
            + top_buffer + lid
```

The floor is `max(2, wall_thickness)` and the lid is `wall_thickness`; with
caps both are `cap_height`. Without a shell, the case diameter is the
lining diameter.

`scrollcase build` prints the scroll, lining, shell, and case sizes.
