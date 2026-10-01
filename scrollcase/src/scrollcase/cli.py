"""Command line interface.

scrollcase build [MESH] [-c case.toml] [-o OUT_DIR] [--parts left,right,stand]
scrollcase defaults [--style STYLE] > case.toml
"""

import argparse
import dataclasses
import logging
import sys

from .config import PRESETS, CaseConfig, config_from_dict, load_config


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    return repr(value)


# Example values shown for keys that are unset by default
_UNSET_HINTS = {
    "mesh": '"path/to/mesh.ply"',
    "amplitude": "10.0  # default: 0.2 x (span + wall_thickness)",
}


def config_toml(cfg: CaseConfig) -> str:
    """A fully resolved config as TOML. Unset optional values are commented out."""
    lines: list[str] = []

    def table(data: dict, prefix: str) -> None:
        nested = []
        for key, value in data.items():
            if isinstance(value, dict):
                nested.append((key, value))
            elif value is None:
                lines.append(f"# {key} = {_UNSET_HINTS.get(key, '...')}")
            else:
                lines.append(f"{key} = {_toml_value(value)}")
        for key, value in nested:
            lines.append(f"\n[{prefix}{key}]")
            table(value, f"{prefix}{key}.")

    table(dataclasses.asdict(cfg), "")
    return "\n".join(lines) + "\n"


def defaults_toml(style: str = CaseConfig.style) -> str:
    return config_toml(config_from_dict({"style": style}))


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="scrollcase", description=__doc__.split("\n")[0])
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="generate case STLs")
    build.add_argument("mesh", nargs="?", help="scroll mesh (overrides scroll.mesh)")
    build.add_argument("-c", "--config", help="TOML config file")
    build.add_argument("-o", "--out", default=".", help="output directory")
    build.add_argument("--name", help="output file prefix (overrides name)")
    build.add_argument(
        "--parts", help="comma-separated parts (default: left,right, plus stand if enabled)"
    )

    defaults = sub.add_parser("defaults", help="print a style's full config as TOML")
    defaults.add_argument("--style", default=CaseConfig.style, choices=sorted(PRESETS))

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(name)s: %(message)s",
    )

    if args.command == "defaults":
        sys.stdout.write(defaults_toml(args.style))
        return 0

    cfg = load_config(args.config) if args.config else config_from_dict({})
    if args.mesh:
        cfg.scroll.mesh = args.mesh
    if args.name:
        cfg.name = args.name

    # Imported here so `defaults` works without loading meshlib
    from .pipeline import build as run_build

    parts = [p.strip() for p in args.parts.split(",") if p.strip()] if args.parts else None
    result = run_build(cfg, args.out, parts=parts)
    L = result.layout
    print(f"Scroll: {2 * L.scroll_radius:.2f} D x {L.scroll_height:.2f} H mm")
    print(f"Lining: {L.lining_diameter:.2f} D (outer) mm")
    if cfg.shell.type != "none":
        print(f"Shell:  {L.inner_diameter:.2f} D (inner), {L.outer_diameter:.2f} D (outer) mm")
    if cfg.ends.type == "caps":
        side = 2 * L.cap_half_width
        print(f"Caps:   {side:.2f} x {side:.2f} mm, plus bolt tabs")
    print(f"Height: {L.outer_height:.2f} mm")
    for path in result.outputs.values():
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
