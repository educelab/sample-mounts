"""Case configuration and derived layout.

Units are mm. Case coordinates: the case axis is +Z, the shell bottom is Z=0,
and the halves split on the XZ plane (left is -Y, right is +Y).
"""

import dataclasses
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class ScrollConfig:
    """Input mesh and how it is cleaned up and placed in the case.

    With no `mesh`, a cylinder of `generic_diameter` x `generic_height` is used.
    `rotate` (degrees, XYZ) and `translate` are applied after auto-alignment;
    the case is then sized around the result.
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
class HoneycombConfig:
    enabled: bool = True
    hole_edges: int = 6
    columns: int = 12
    spacing: float = 1.5


@dataclass
class NubConfig:
    """Alignment nubs on the left half, with matching sockets on the right.

    `positions` are [x, z] pairs on the split plane, in case coordinates.
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
class CaseConfig:
    name: str = "Scroll Case"
    lining_offset: float = 2.0
    wall_thickness: float = 2.0
    bottom_buffer: float = 5.0
    top_buffer: float = 5.0
    internal_gap: float = 3.0
    outer_cylinder: bool = True
    overhang_removal: bool = True
    marker_rings: bool = True
    mount_disc: str = "112.5"  # "112.5" or "65"
    stand_length_scale: float = 1.0
    voxel_size: float = 0.4
    scroll: ScrollConfig = field(default_factory=ScrollConfig)
    honeycomb: HoneycombConfig = field(default_factory=HoneycombConfig)
    nubs: NubConfig = field(default_factory=NubConfig)
    escape_holes: EscapeHoleConfig = field(default_factory=EscapeHoleConfig)
    label: LabelConfig = field(default_factory=LabelConfig)


def _from_dict(cls: type, data: dict[str, Any]):
    fields = {f.name: f for f in dataclasses.fields(cls)}
    unknown = set(data) - set(fields)
    if unknown:
        raise ValueError(f"Unknown {cls.__name__} keys: {sorted(unknown)}")
    kwargs = {}
    for key, value in data.items():
        ftype = fields[key].type
        if dataclasses.is_dataclass(ftype):
            value = _from_dict(ftype, value)
        kwargs[key] = value
    return cls(**kwargs)


def config_from_dict(data: dict[str, Any]) -> CaseConfig:
    return _from_dict(CaseConfig, data)


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
