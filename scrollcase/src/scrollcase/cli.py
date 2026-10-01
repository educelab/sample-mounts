"""Command line interface.

scrollcase build [MESH] [-c case.toml] [-o OUT_DIR] [--parts left,right,stand]
scrollcase defaults > case.toml
"""

import argparse
import dataclasses
import logging
import sys

from .config import CaseConfig, load_config


def _toml_value(value) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, str):
        return '"' + value.replace("\\", "\\\\").replace('"', '\\"') + '"'
    if isinstance(value, list):
        return "[" + ", ".join(_toml_value(v) for v in value) + "]"
    return repr(value)


def defaults_toml() -> str:
    """Default config as TOML. `scroll.mesh` is left commented out."""
    data = dataclasses.asdict(CaseConfig())
    lines, tables = [], []
    for key, value in data.items():
        if isinstance(value, dict):
            tables.append((key, value))
        else:
            lines.append(f"{key} = {_toml_value(value)}")
    for name, table in tables:
        lines.append(f"\n[{name}]")
        for key, value in table.items():
            if value is None:
                lines.append(f'# {key} = "path/to/mesh.ply"')
            else:
                lines.append(f"{key} = {_toml_value(value)}")
    return "\n".join(lines) + "\n"


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(prog="scrollcase", description=__doc__.split("\n")[0])
    parser.add_argument("-v", "--verbose", action="store_true")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="generate case STLs")
    build.add_argument("mesh", nargs="?", help="scroll mesh (overrides scroll.mesh)")
    build.add_argument("-c", "--config", help="TOML config file")
    build.add_argument("-o", "--out", default=".", help="output directory")
    build.add_argument("--name", help="output file prefix (overrides name)")
    build.add_argument("--parts", default="left,right,stand", help="comma-separated parts")

    sub.add_parser("defaults", help="print the default config as TOML")

    args = parser.parse_args(argv)
    logging.basicConfig(
        level=logging.INFO if args.verbose else logging.WARNING,
        format="%(asctime)s %(name)s: %(message)s",
    )

    if args.command == "defaults":
        sys.stdout.write(defaults_toml())
        return 0

    cfg = load_config(args.config) if args.config else CaseConfig()
    if args.mesh:
        cfg.scroll.mesh = args.mesh
    if args.name:
        cfg.name = args.name

    # Imported here so `defaults` works without loading meshlib
    from .pipeline import build as run_build

    parts = [p.strip() for p in args.parts.split(",") if p.strip()]
    result = run_build(cfg, args.out, parts=parts)
    L = result.layout
    print(f"Scroll: {2 * L.scroll_radius:.2f} D x {L.scroll_height:.2f} H mm")
    print(f"Lining: {L.lining_diameter:.2f} D (outer) mm")
    print(f"Shell:  {L.inner_diameter:.2f} D (inner)")
    print(f"Case:   {L.outer_diameter:.2f} D x {L.outer_height:.2f} H mm")
    for path in result.outputs.values():
        print(f"Wrote {path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
