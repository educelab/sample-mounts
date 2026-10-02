"""Case configuration, style presets, and derived layout.

Units are mm. Case coordinates: the case axis is +Z, the shell bottom is Z=0,
and the halves split on the XZ plane (left is -Y, right is +Y).

A config is resolved as: dataclass defaults, then the `style` preset, then
the user's values. Released presets never change; see `PRESETS`.
"""

import copy
import dataclasses
import math
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from types import UnionType
from typing import Any, get_args, get_origin


class ConfigError(ValueError):
    """A config the user can fix: bad keys, values, or combinations."""


@dataclass
class ScrollConfig:
    """Input mesh and how it is cleaned up and placed in the case.

    With no `mesh`, a cylinder of `generic_diameter` x `generic_height` is used.
    `rotate` (degrees, XYZ) is applied after auto-alignment, then the scroll is
    re-centered on the case axis. `translate` is applied last; the case is
    sized around the result.
    """

    mesh: str | None = None
    scale: float = 1.0
    auto_align: bool = True
    rotate: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    translate: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    decimate_max_error: float = 0.05
    smoothing: str = "none"  # "none", "denoise", or "shrink_expand"
    smoothing_amount: float = 2.0
    generic_diameter: float = 76.0
    generic_height: float = 155.0


@dataclass
class SplitConfig:
    """Surface the halves separate along, as a profile y = f(x) extruded in Z.

    "curve" is villa's S-shaped split spanning the whole case. `amplitude`
    defaults to 0.2 x (span + wall_thickness), as upstream; `flip` mirrors it.
    """

    type: str = "plane"
    amplitude: float | None = None
    flip: bool = False


@dataclass
class HoneycombConfig:
    hole_edges: int = 6
    columns: int = 12
    spacing: float = 1.5


@dataclass
class ShellConfig:
    """Outer cylinder around the lining. `open_top` cuts away its upper part."""

    type: str = "honeycomb"  # "honeycomb", "solid", or "none"
    open_top: bool = False
    marker_rings: bool = True
    honeycomb: HoneycombConfig = field(default_factory=HoneycombConfig)


@dataclass
class EndsConfig:
    """What closes the case top and bottom.

    "shell" is the shell's own floor and lid. "caps" are villa's square end
    caps, with bolt tabs that clamp the halves together (M4 by default) and
    counterbored holes in the bottom cap for mounting (M6 by default). The
    remaining keys only apply to caps.
    """

    type: str = "shell"
    cap_height: float = 10.0
    corner_fillet: float = 6.25
    bolt_hole_diameter: float = 5.0
    bolt_counterbore_diameter: float = 8.0
    bolt_counterbore_depth: float = 2.0
    nut_diameter: float = 9.0
    nut_depth: float = 3.5
    mount_hole_spacing: float = 50.0
    mount_hole_diameter: float = 6.8
    mount_counterbore_diameter: float = 10.5
    mount_counterbore_depth: float = 5.0


@dataclass
class MountConfig:
    type: str = "generic-112.5"  # "generic-112.5", "generic-65", "kinematic", or "none"


@dataclass
class NubConfig:
    """Alignment nubs on the left half, with matching sockets on the right.

    `positions` are [x, z] pairs on the split surface, in case coordinates.
    """

    positions: list[list[float]] = field(default_factory=list)
    size: float = 4.0
    depth: float = 1.5
    margin: float = 0.5


@dataclass
class EscapeHoleConfig:
    enabled: bool = False
    offset: float = 1.5
    diameter: float = 4.0
    angle: float = 15.0


@dataclass
class LabelConfig:
    line1: str = ""
    line2: str = ""
    height: float = 5.0
    depth: float = 0.5
    font: str = "Arial Rounded MT Bold"


@dataclass
class StandConfig:
    enabled: bool = True
    length_scale: float = 1.0


@dataclass
class CaseConfig:
    style: str = "educelab.v1"
    name: str = "Scroll Case"
    lining_offset: float = 2.0
    wall_thickness: float = 2.0
    bottom_buffer: float = 5.0
    top_buffer: float = 5.0
    internal_gap: float = 3.0
    overhang_removal: bool = True
    voxel_size: float = 0.4
    scroll: ScrollConfig = field(default_factory=ScrollConfig)
    split: SplitConfig = field(default_factory=SplitConfig)
    shell: ShellConfig = field(default_factory=ShellConfig)
    ends: EndsConfig = field(default_factory=EndsConfig)
    mount: MountConfig = field(default_factory=MountConfig)
    nubs: NubConfig = field(default_factory=NubConfig)
    escape_holes: EscapeHoleConfig = field(default_factory=EscapeHoleConfig)
    label: LabelConfig = field(default_factory=LabelConfig)
    stand: StandConfig = field(default_factory=StandConfig)


# Released presets are frozen by tests/presets/<style>.toml. To change one,
# add a new version instead. educelab.v1 is the dataclass defaults, so new
# keys must default to behavior that leaves its geometry unchanged.
PRESETS: dict[str, dict[str, Any]] = {
    "educelab.v1": {},
    # ScrollPrize/villa foundation/scrollcase at 7d6a82c (2026-10-01)
    "villa.2026-10": {
        "bottom_buffer": 3.0,
        "top_buffer": 3.0,
        "scroll": {"decimate_max_error": 0.02},
        "split": {"type": "curve"},
        "shell": {"type": "none", "marker_rings": False},
        "ends": {"type": "caps"},
        "mount": {"type": "kinematic"},
        "label": {"height": 8.0, "font": "Arial"},
        "stand": {"enabled": False},
    },
}

# Mount diameters, for sizing caps. Must match mount_disc.MOUNT_DISCS, which
# can't be imported here because it loads build123d.
MOUNT_DIAMETERS = {"generic-112.5": 112.5, "generic-65": 65.0, "kinematic": 112.5, "none": 0.0}

_CHOICES = {
    ("split", "type"): ("plane", "curve"),
    ("shell", "type"): ("honeycomb", "solid", "none"),
    ("ends", "type"): ("shell", "caps"),
    ("mount", "type"): tuple(MOUNT_DIAMETERS),
    ("scroll", "smoothing"): ("none", "denoise", "shrink_expand"),
}


def _merge(base: dict, override: dict) -> dict:
    out = copy.deepcopy(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(out.get(key), dict):
            out[key] = _merge(out[key], value)
        else:
            out[key] = copy.deepcopy(value)
    return out


_TYPE_NAMES = {float: "number", int: "integer", bool: "boolean", str: "string"}


def _type_name(ftype, plural=False) -> str:
    """Plain-English name of a field type, e.g. "a list of numbers"."""
    if isinstance(ftype, UnionType):
        names = [_type_name(t, plural) for t in get_args(ftype) if t is not type(None)]
        return " or ".join(names)
    if get_origin(ftype) is list:
        inner = _type_name(get_args(ftype)[0], plural=True)
        return f"lists of {inner}" if plural else f"a list of {inner}"
    name = _TYPE_NAMES.get(ftype, getattr(ftype, "__name__", str(ftype)))
    if plural:
        return name + "s"
    return ("an " if name[0] in "aeiou" else "a ") + name


def _matches(value, ftype) -> bool:
    if isinstance(ftype, UnionType):
        return any(_matches(value, t) for t in get_args(ftype))
    if get_origin(ftype) is list:
        (item,) = get_args(ftype)
        return isinstance(value, list) and all(_matches(v, item) for v in value)
    if ftype is type(None):
        return value is None
    if isinstance(value, bool):
        return ftype is bool
    if ftype is float:
        return isinstance(value, (int, float))
    return isinstance(value, ftype)


def _from_dict(cls: type, data: dict[str, Any], where: str = ""):
    fields = {f.name: f for f in dataclasses.fields(cls)}
    unknown = set(data) - set(fields)
    if unknown:
        keys = ", ".join(where + k for k in sorted(unknown))
        raise ConfigError(f"Unknown config keys: {keys}")
    kwargs = {}
    for key, value in data.items():
        ftype = fields[key].type
        if dataclasses.is_dataclass(ftype):
            if not isinstance(value, dict):
                raise ConfigError(f"{where}{key} must be a table, e.g. [{where}{key}]")
            value = _from_dict(ftype, value, f"{where}{key}.")
        elif not _matches(value, ftype):
            raise ConfigError(f"{where}{key} = {value!r} must be {_type_name(ftype)}")
        kwargs[key] = value
    return cls(**kwargs)


def validate(cfg: CaseConfig) -> None:
    """Reject unknown component types and combinations that can't be built."""
    for (section, key), choices in _CHOICES.items():
        value = getattr(getattr(cfg, section), key)
        if value not in choices:
            raise ConfigError(f"{section}.{key} = {value!r} is not one of {list(choices)}")

    def require(ok: bool, message: str):
        if not ok:
            raise ConfigError(message)

    require(
        not cfg.shell.marker_rings or cfg.shell.type == "honeycomb",
        f'shell.marker_rings requires shell.type = "honeycomb" (got {cfg.shell.type!r})',
    )
    require(
        not cfg.shell.open_top or cfg.ends.type == "shell",
        f'shell.open_top requires ends.type = "shell" (got {cfg.ends.type!r})',
    )
    require(
        cfg.ends.type != "shell" or cfg.shell.type != "none",
        'ends.type = "shell" needs a shell to provide the floor and lid (shell.type = "none")',
    )
    require(
        not cfg.escape_holes.enabled or cfg.shell.type != "none",
        'escape_holes need a shell; they sit between the lining and shell (shell.type = "none")',
    )
    require(
        not cfg.stand.enabled or cfg.mount.type.startswith("generic-"),
        f"stand requires a generic mount disc (mount.type = {cfg.mount.type!r})",
    )
    require(
        not cfg.stand.enabled or cfg.ends.type == "shell",
        f'stand requires ends.type = "shell" to fit its cradle (got {cfg.ends.type!r})',
    )


def config_from_dict(data: dict[str, Any]) -> CaseConfig:
    """Resolve a config dict against its style preset and validate it."""
    style = data.get("style", CaseConfig.style)
    if style not in PRESETS:
        raise ConfigError(f"Unknown style {style!r}; available: {sorted(PRESETS)}")
    merged = _merge(_merge(dataclasses.asdict(CaseConfig()), PRESETS[style]), data)
    merged["style"] = style
    cfg = _from_dict(CaseConfig, merged)
    validate(cfg)
    return cfg


def load_config(path: str | Path) -> CaseConfig:
    """Load a TOML config. Relative mesh paths resolve against the file."""
    path = Path(path)
    try:
        data = tomllib.loads(path.read_text())
    except FileNotFoundError:
        raise ConfigError(f"Config file not found: {path}") from None
    except tomllib.TOMLDecodeError as e:
        raise ConfigError(f"{path}: invalid TOML: {e}") from None
    try:
        cfg = config_from_dict(data)
    except ConfigError as e:
        raise ConfigError(f"{path}: {e}") from None
    if cfg.scroll.mesh and not Path(cfg.scroll.mesh).is_absolute():
        cfg.scroll.mesh = str((path.parent / cfg.scroll.mesh).resolve())
    return cfg


@dataclass(frozen=True)
class Layout:
    """Case dimensions derived from the config and the aligned scroll size."""

    scroll_radius: float
    scroll_height: float
    lining_offset: float
    wall: float
    # Floor (or bottom cap) and lid (or top cap) thicknesses
    bottom_wall: float
    lid_thickness: float
    cavity_diameter: float
    cavity_height: float
    lining_diameter: float
    inner_diameter: float
    inner_z: float
    inner_height: float
    outer_diameter: float
    outer_height: float
    cavity_z: float
    scroll_z: float
    split_span: float
    # Half the side of the square caps, or 0 without caps
    cap_half_width: float

    @classmethod
    def from_config(cls, cfg: CaseConfig, scroll_radius: float, scroll_height: float):
        """Without a shell, the inner and outer diameters are the lining's."""
        wall = cfg.wall_thickness
        caps = cfg.ends.type == "caps"
        bottom_wall = cfg.ends.cap_height if caps else max(2.0, wall)
        lid = cfg.ends.cap_height if caps else wall
        cavity_diameter = 2 * (scroll_radius + cfg.lining_offset)
        cavity_height = scroll_height + 2 * cfg.lining_offset
        lining_diameter = cavity_diameter + 2 * wall
        if cfg.shell.type == "none":
            inner_diameter = outer_diameter = lining_diameter
            # villa's curve ends at the cavity, where its end posts sit
            split_span = cavity_diameter / 2
        else:
            inner_diameter = lining_diameter + 2 * cfg.internal_gap
            outer_diameter = inner_diameter + 2 * wall
            # The split curve runs to the middle of the shell wall
            split_span = (inner_diameter + outer_diameter) / 4
        cap_half_width = max(MOUNT_DIAMETERS[cfg.mount.type], outer_diameter) / 2 if caps else 0.0
        inner_height = cfg.bottom_buffer + cavity_height + 2 * wall + cfg.top_buffer
        cavity_z = bottom_wall + cfg.bottom_buffer + wall
        return cls(
            scroll_radius=scroll_radius,
            scroll_height=scroll_height,
            lining_offset=cfg.lining_offset,
            wall=wall,
            bottom_wall=bottom_wall,
            lid_thickness=lid,
            cavity_diameter=cavity_diameter,
            cavity_height=cavity_height,
            lining_diameter=lining_diameter,
            inner_diameter=inner_diameter,
            inner_z=bottom_wall,
            inner_height=inner_height,
            outer_diameter=outer_diameter,
            outer_height=inner_height + bottom_wall + lid,
            cavity_z=cavity_z,
            scroll_z=cavity_z + cfg.lining_offset,
            split_span=split_span,
            cap_half_width=cap_half_width,
        )


NUB_ROTATIONS = (0, 45)


def nub_extent(cfg: CaseConfig, index: int) -> float:
    """Half-width of a nub in X: square nubs, then 45-degree diamonds."""
    half = cfg.nubs.size / 2
    return half * math.sqrt(2) if NUB_ROTATIONS[index % 2] else half


def validate_layout(cfg: CaseConfig, L: Layout) -> None:
    """Checks that need the fitted scroll size, run once the layout is known."""
    from .split import profile_for

    profile_for(cfg, L)
    divider = L.outer_diameter / 2 - L.cavity_diameter / 2
    for i, (x, z) in enumerate(cfg.nubs.positions):
        e = nub_extent(cfg, i)
        r = abs(x)
        lo, hi = L.cavity_diameter / 2 + e, L.outer_diameter / 2 - e
        if lo > hi:
            shape = "diamond" if NUB_ROTATIONS[i % 2] else "square"
            raise ConfigError(
                f"nubs.positions[{i}]: a {shape} nub of nubs.size = {cfg.nubs.size} is "
                f"{2 * e:.2f} mm wide, but the divider between the cavity and the outer wall "
                f"is only {divider:.2f} mm wide. Use a smaller nubs.size, or a shell"
                f" or thicker wall_thickness to widen the divider."
            )
        if r < lo or r > hi:
            where = "into the scroll cavity" if r < lo else "past the outside of the case"
            raise ConfigError(
                f"nubs.positions[{i}] = [{x}, {z}]: a nub at x = {x} would stick {where}. "
                f"Nubs sit on the divider between the cavity and the outer wall; for this "
                f"scroll and nubs.size = {cfg.nubs.size}, x must be ±{lo:.2f} to ±{hi:.2f}"
            )
        z_lo, z_hi = L.inner_z + e, L.inner_z + L.inner_height - e
        if not z_lo <= z <= z_hi:
            raise ConfigError(
                f"nubs.positions[{i}] = [{x}, {z}]: z must be {z_lo:.2f} to {z_hi:.2f} "
                f"to keep the nub inside the case"
            )
