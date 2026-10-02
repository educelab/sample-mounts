"""End-to-end case generation."""

import dataclasses
import json
import logging
import subprocess
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path

from . import lining
from .config import CaseConfig, ConfigError, Layout, validate, validate_layout

logger = logging.getLogger(__name__)

ALL_PARTS = ("left", "right", "stand")
_SUFFIX = {"left": "L", "right": "R", "stand": "Stand", "scroll": "Scroll"}


@dataclass
class BuildResult:
    layout: Layout
    outputs: dict[str, Path]


def _write_job(path: Path, cfg: CaseConfig, layout: Layout, part: str, out: Path, tolerance: float):
    job = {
        "config": dataclasses.asdict(cfg),
        "layout": dataclasses.asdict(layout),
        "part": part,
        "out": str(out),
        "tolerance": tolerance,
    }
    path.write_text(json.dumps(job))


def _render_bodies(
    cfg: CaseConfig, layout: Layout, parts, work: Path, tolerance: float
) -> dict[str, Path]:
    """Build B-rep parts in parallel worker processes."""
    procs = {}
    for part in parts:
        job, out = work / f"{part}.json", work / f"{part}-body.stl"
        _write_job(job, cfg, layout, part, out, tolerance)
        cmd = [sys.executable, "-m", "scrollcase.brep_worker", str(job)]
        procs[part] = (subprocess.Popen(cmd, stderr=subprocess.PIPE, text=True), out)

    bodies = {}
    for part, (proc, out) in procs.items():
        _, err = proc.communicate()
        if proc.returncode != 0 or not out.exists():
            logger.info("B-rep worker output for %s:\n%s", part, err)
            last = err.strip().splitlines()[-1] if err.strip() else f"exit code {proc.returncode}"
            raise RuntimeError(f"B-rep stage failed for {part}: {last}")
        bodies[part] = out
    return bodies


def default_parts(cfg: CaseConfig) -> tuple[str, ...]:
    return ("left", "right", "stand") if cfg.stand.enabled else ("left", "right")


def build(
    cfg: CaseConfig,
    out_dir: str | Path,
    parts=None,
    tolerance: float = 0.01,
) -> BuildResult:
    """Generate case STLs into `out_dir`, named `<cfg.name>-<L|R|Stand|Scroll>.stl`.

    `parts` defaults to both halves, plus the stand if `stand.enabled`.
    """
    validate(cfg)
    parts = default_parts(cfg) if parts is None else tuple(parts)
    unknown = set(parts) - set(ALL_PARTS)
    if unknown:
        raise ConfigError(f"Unknown parts: {sorted(unknown)}; available: {sorted(ALL_PARTS)}")
    if "stand" in parts and not cfg.stand.enabled:
        raise ConfigError("stand requested but stand.enabled = false")
    if cfg.scroll.mesh and not Path(cfg.scroll.mesh).is_file():
        raise ConfigError(f"Scroll mesh not found: {cfg.scroll.mesh}")
    out_dir = Path(out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    scroll, radius, height = lining.prepare_scroll(cfg)
    layout = Layout.from_config(cfg, radius, height)
    validate_layout(cfg, layout)
    logger.info("Case outer diameter %.2f, height %.2f", layout.outer_diameter, layout.outer_height)

    def path(key: str) -> Path:
        return out_dir / f"{cfg.name}-{_SUFFIX[key]}.stl"

    outputs = {"scroll": path("scroll")}
    lining.save(lining.place_scroll(scroll, layout), outputs["scroll"])

    with tempfile.TemporaryDirectory() as tmp:
        bodies = _render_bodies(cfg, layout, parts, Path(tmp), tolerance)
        halves_needed = [p for p in parts if p in lining.SIDES]
        halves = lining.build_lining(scroll, cfg, layout) if halves_needed else {}

        for part in parts:
            outputs[part] = path(part)
            mesh = lining.load_brep_export(bodies[part])
            if part in halves:
                logger.info("Assembling %s half", part)
                mesh = lining.assemble(mesh, halves[part])
            lining.save(mesh, outputs[part])

    return BuildResult(layout=layout, outputs=outputs)
