"""Case configuration, style presets, and derived layout.

Units are mm. Case coordinates: the case axis is +Z, the shell bottom is Z=0,
and the halves split on the XZ plane (left is -Y, right is +Y).

A config is resolved as: dataclass defaults, then the `style` preset, then
the user's values. Released presets never change; see `PRESETS`.
"""

import copy
import dataclasses
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


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
    """Surface the halves separate along, as a profile y = f(x) extruded in Z."""

    type: str = "plane"


@dataclass
class HoneycombConfig:
    hole_edges: int = 6
    columns: int = 12
    spacing: float = 1.5


@dataclass
class ShellConfig:
    """Outer cylinder around the lining. `open_top` cuts away its upper part."""

    type: str = "honeycomb"  # "honeycomb" or "solid"
    open_top: bool = False
    marker_rings: bool = True
    honeycomb: HoneycombConfig = field(default_factory=HoneycombConfig)


@dataclass
class EndsConfig:
    """What closes the case top and bottom. "shell" is the shell's floor and lid."""

    type: str = "shell"


@dataclass
class MountConfig:
    type: str = "generic-112.5"  # "generic-112.5" or "generic-65"


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
# add a new version instead. educelab.v1 is the dataclass defaults.
PRESETS: dict[str, dict[str, Any]] = {
    "educelab.v1": {},
}

_CHOICES = {
    ("split", "type"): ("plane",),
    ("shell", "type"): ("honeycomb", "solid"),
    ("ends", "type"): ("shell",),
    ("mount", "type"): ("generic-112.5", "generic-65"),
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


def _from_dict(cls: type, data: dict[str, Any], where: str = ""):
    fields = {f.name: f for f in dataclasses.fields(cls)}
    unknown = set(data) - set(fields)
    if unknown:
        keys = ", ".join(where + k for k in sorted(unknown))
        raise ValueError(f"Unknown config keys: {keys}")
    kwargs = {}
    for key, value in data.items():
        ftype = fields[key].type
        if dataclasses.is_dataclass(ftype):
            value = _from_dict(ftype, value, f"{where}{key}.")
        kwargs[key] = value
    return cls(**kwargs)


def validate(cfg: CaseConfig) -> None:
    """Reject unknown component types and combinations that can't be built."""
    for (section, key), choices in _CHOICES.items():
        value = getattr(getattr(cfg, section), key)
        if value not in choices:
            raise ValueError(f"{section}.{key} = {value!r} is not one of {list(choices)}")

    def require(ok: bool, message: str):
        if not ok:
            raise ValueError(message)

    require(
        not cfg.shell.marker_rings or cfg.shell.type == "honeycomb",
        f'shell.marker_rings requires shell.type = "honeycomb" (got {cfg.shell.type!r})',
    )
    require(
        not cfg.shell.open_top or cfg.ends.type == "shell",
        f'shell.open_top requires ends.type = "shell" (got {cfg.ends.type!r})',
    )
    require(
        not cfg.stand.enabled or cfg.mount.type.startswith("generic-"),
        f"stand requires a generic mount disc (mount.type = {cfg.mount.type!r})",
    )


def config_from_dict(data: dict[str, Any]) -> CaseConfig:
    """Resolve a config dict against its style preset and validate it."""
    style = data.get("style", CaseConfig.style)
    if style not in PRESETS:
        raise ValueError(f"Unknown style {style!r}; available: {sorted(PRESETS)}")
    merged = _merge(_merge(dataclasses.asdict(CaseConfig()), PRESETS[style]), data)
    merged["style"] = style
    cfg = _from_dict(CaseConfig, merged)
    validate(cfg)
    return cfg


def load_config(path: str | Path) -> CaseConfig:
    """Load a TOML config. Relative mesh paths resolve against the file."""
    path = Path(path)
    cfg = config_from_dict(tomllib.loads(path.read_text()))
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
    bottom_wall: float
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

    @classmethod
    def from_config(cls, cfg: CaseConfig, scroll_radius: float, scroll_height: float):
        wall = cfg.wall_thickness
        bottom_wall = max(2.0, wall)
        cavity_diameter = 2 * (scroll_radius + cfg.lining_offset)
        cavity_height = scroll_height + 2 * cfg.lining_offset
        lining_diameter = cavity_diameter + 2 * wall
        inner_diameter = lining_diameter + 2 * cfg.internal_gap
        inner_height = cfg.bottom_buffer + cavity_height + 2 * wall + cfg.top_buffer
        cavity_z = bottom_wall + cfg.bottom_buffer + wall
        return cls(
            scroll_radius=scroll_radius,
            scroll_height=scroll_height,
            lining_offset=cfg.lining_offset,
            wall=wall,
            bottom_wall=bottom_wall,
            cavity_diameter=cavity_diameter,
            cavity_height=cavity_height,
            lining_diameter=lining_diameter,
            inner_diameter=inner_diameter,
            inner_z=bottom_wall,
            inner_height=inner_height,
            outer_diameter=inner_diameter + 2 * wall,
            outer_height=inner_height + bottom_wall + wall,
            cavity_z=cavity_z,
            scroll_z=cavity_z + cfg.lining_offset,
        )
