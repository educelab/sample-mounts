import tomllib

import pytest

from scrollcase.cli import defaults_toml
from scrollcase.config import CaseConfig, Layout, config_from_dict, load_config


def test_defaults_toml_round_trips():
    assert config_from_dict(tomllib.loads(defaults_toml())) == CaseConfig()


def test_unknown_keys_are_rejected():
    with pytest.raises(ValueError, match="wall_thicknes"):
        config_from_dict({"wall_thicknes": 3})
    with pytest.raises(ValueError, match="colour"):
        config_from_dict({"label": {"colour": "red"}})


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
