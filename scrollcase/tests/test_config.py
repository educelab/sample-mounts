import tomllib
from pathlib import Path

import pytest

from scrollcase.cli import config_toml, defaults_toml
from scrollcase.config import PRESETS, CaseConfig, Layout, config_from_dict, load_config

PRESET_DIR = Path(__file__).parent / "presets"


@pytest.mark.parametrize("style", sorted(PRESETS))
def test_released_presets_are_frozen(style):
    """A preset's resolved values must never change; add a new version instead."""
    golden = PRESET_DIR / f"{style}.toml"
    assert golden.exists(), f"Add {golden.name} (scrollcase defaults --style {style})"
    assert defaults_toml(style) == golden.read_text()


@pytest.mark.parametrize("style", sorted(PRESETS))
def test_defaults_toml_round_trips(style):
    cfg = config_from_dict({"style": style})
    assert config_from_dict(tomllib.loads(config_toml(cfg))) == cfg


def test_default_style_is_educelab_v1():
    assert config_from_dict({}) == config_from_dict({"style": "educelab.v1"})
    assert config_from_dict({}) == CaseConfig()


def test_user_values_override_preset():
    cfg = config_from_dict({"shell": {"type": "solid", "marker_rings": False}})
    assert cfg.shell.type == "solid"
    # Untouched keys in the same section keep the preset's values
    assert cfg.shell.honeycomb.columns == 12


def test_unknown_keys_and_styles_are_rejected():
    with pytest.raises(ValueError, match="wall_thicknes"):
        config_from_dict({"wall_thicknes": 3})
    with pytest.raises(ValueError, match=r"label\.colour"):
        config_from_dict({"label": {"colour": "red"}})
    with pytest.raises(ValueError, match="educelab.v1"):
        config_from_dict({"style": "educelab"})


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"shell": {"type": "lattice"}}, "shell.type"),
        ({"mount": {"type": "generic-100"}}, "mount.type"),
        ({"shell": {"type": "solid"}}, "marker_rings"),
        ({"shell": {"type": "none", "marker_rings": False}}, "floor and lid"),
        ({"style": "villa.2026-10", "escape_holes": {"enabled": True}}, "escape_holes"),
        ({"style": "villa.2026-10", "stand": {"enabled": True}}, "generic mount"),
        ({"ends": {"type": "caps"}, "shell": {"open_top": True}}, "open_top"),
        ({"ends": {"type": "caps"}}, "stand requires ends.type"),
    ],
)
def test_invalid_combinations_are_rejected(data, message):
    with pytest.raises(ValueError, match=message):
        config_from_dict(data)


def test_mesh_path_resolves_relative_to_config(tmp_path):
    (tmp_path / "case.toml").write_text('[scroll]\nmesh = "meshes/s.ply"\n')
    cfg = load_config(tmp_path / "case.toml")
    assert cfg.scroll.mesh == str((tmp_path / "meshes" / "s.ply").resolve())


def test_layout_stacks_up():
    cfg = CaseConfig()
    L = Layout.from_config(cfg, scroll_radius=38, scroll_height=155)
    assert L.cavity_diameter == 80
    assert L.lining_diameter == 84
    assert L.outer_diameter == 84 + 2 * cfg.internal_gap + 2 * cfg.wall_thickness
    # Lid sits above the cavity top by wall + top buffer + lid thickness
    cavity_top = L.cavity_z + L.cavity_height
    assert L.outer_height == pytest.approx(
        cavity_top + cfg.wall_thickness + cfg.top_buffer + cfg.wall_thickness
    )
    assert L.scroll_z == L.cavity_z + cfg.lining_offset


def test_villa_preset_layout_matches_upstream():
    """Upstream's stack-up: 3mm margins, 10mm caps, curve ending at the cavity."""
    cfg = config_from_dict({"style": "villa.2026-10"})
    L = Layout.from_config(cfg, scroll_radius=38, scroll_height=155)
    # Upstream cylinder_height = h + 2 offset + 2 wall + lower + upper margins
    assert L.inner_height == 155 + 4 + 4 + 3 + 3
    assert L.outer_height == L.inner_height + 2 * 10
    assert L.split_span == L.cavity_diameter / 2
    assert L.cap_half_width == 112.5 / 2
