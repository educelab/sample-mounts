import tomllib
from pathlib import Path

import pytest

from scrollcase.cli import config_toml, defaults_toml, main
from scrollcase.config import (
    PRESETS,
    CaseConfig,
    ConfigError,
    Layout,
    config_from_dict,
    load_config,
    validate_layout,
)

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
    cfg = config_from_dict({"shell": {"type": "solid"}})
    assert cfg.shell.type == "solid"
    assert cfg.shell.marker_rings
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


def test_marker_rings_are_ignored_without_a_shell():
    cfg = config_from_dict({"style": "villa.2026-10", "shell": {"marker_rings": True}})
    assert cfg.shell.type == "none"


def test_caps_clear_the_shell():
    """Caps around a shell wider than the mount leave a margin, avoiding tangent faces."""
    cfg = config_from_dict(
        {"ends": {"type": "caps"}, "mount": {"type": "none"}, "stand": {"enabled": False}}
    )
    L = Layout.from_config(cfg, scroll_radius=38, scroll_height=155)
    assert L.cap_half_width == L.outer_diameter / 2 + cfg.wall_thickness


def test_mount_holes_must_fit_on_caps():
    cfg = config_from_dict({"style": "villa.2026-10", "mount": {"type": "none"}})
    L = Layout.from_config(cfg, scroll_radius=20, scroll_height=100)
    with pytest.raises(ConfigError, match="mount_hole_spacing"):
        validate_layout(cfg, L)
    cfg.ends.mount_hole_spacing = L.cap_half_width - cfg.ends.mount_counterbore_diameter / 2
    validate_layout(cfg, L)


@pytest.mark.parametrize(
    ("data", "message"),
    [
        ({"wall_thickness": "2"}, "wall_thickness = '2' must be a number"),
        ({"shell": {"open_top": 1}}, "must be a boolean"),
        ({"shell": "none"}, r"shell must be a table"),
        ({"nubs": {"positions": [[1, "a"]]}}, "a list of lists of numbers"),
        ({"label": {"line1": 5}}, "label.line1 = 5 must be a string"),
    ],
)
def test_wrong_value_types_are_rejected(data, message):
    with pytest.raises(ConfigError, match=message):
        config_from_dict(data)


def test_cli_reports_config_errors_without_traceback(tmp_path, capsys):
    (tmp_path / "bad.toml").write_text("wall_thickness = \n")
    assert main(["build", "-c", str(tmp_path / "bad.toml")]) == 2
    assert main(["build", "-c", str(tmp_path / "missing.toml")]) == 2
    assert main(["build", str(tmp_path / "missing.ply")]) == 2
    err = capsys.readouterr().err.splitlines()
    assert len(err) == 3
    assert "invalid TOML" in err[0]
    assert "Config file not found" in err[1]
    assert "Scroll mesh not found" in err[2]


@pytest.mark.parametrize(
    "path", sorted((Path(__file__).parents[1] / "examples").glob("*.toml")), ids=lambda p: p.name
)
def test_examples_load(path):
    load_config(path)
