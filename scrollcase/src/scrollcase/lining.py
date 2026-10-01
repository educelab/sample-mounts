"""Mesh stage: scroll alignment, lining construction, and final assembly.

Uses meshlib only. meshlib bundles its own OpenCASCADE, which conflicts with
build123d's in the same process, so the B-rep stage runs in a subprocess.
"""

import logging
from dataclasses import dataclass
from pathlib import Path

import meshlib.mrmeshnumpy as mn
import meshlib.mrmeshpy as mm
import numpy as np
from scipy.spatial.transform import Rotation

from . import alignment
from .config import CaseConfig, Layout, ScrollConfig

logger = logging.getLogger(__name__)

# Large enough to contain any case; used for half-space clipping boxes
_BIG = 5000.0
# The lining wall stops this far short of the split plane so its cut face
# doesn't coincide with the case body's. The divider wall covers the gap.
_SPLIT_INSET = 0.05
# The cavity extends this far past the split plane so it cuts cleanly through
_SPLIT_OVERCUT = 1.0
# Voxel offsets are very dense; decimate them to within this fraction of a voxel
_DECIMATE_VOXEL_FRACTION = 0.1

SIDES = ("left", "right")


@dataclass
class LiningHalf:
    """Solid cavity (scroll + clearance) and the solid wall grown around it."""

    cavity: mm.Mesh
    wall: mm.Mesh


def _copy(mesh: mm.Mesh) -> mm.Mesh:
    out = mm.Mesh()
    out.addMesh(mesh)
    return out


def _transform(mesh: mm.Mesh, rotation: np.ndarray, translation) -> None:
    rows = [mm.Vector3f(*map(float, r)) for r in rotation]
    xf = mm.AffineXf3f(mm.Matrix3f(*rows), mm.Vector3f(*map(float, translation)))
    mesh.transform(xf)


def _translate(mesh: mm.Mesh, offset) -> None:
    _transform(mesh, np.eye(3), offset)


def _vertices(mesh: mm.Mesh) -> np.ndarray:
    return mn.getNumpyVerts(mesh).astype(float)


def _offset(mesh: mm.Mesh, amount: float, voxel_size: float) -> mm.Mesh:
    params = mm.OffsetParameters()
    params.voxelSize = voxel_size
    return mm.offsetMesh(mesh, amount, params)


def _decimate(mesh: mm.Mesh, max_error: float) -> None:
    settings = mm.DecimateSettings()
    settings.maxError = max_error
    settings.packMesh = True
    mm.decimateMesh(mesh, settings)


def _boolean(a: mm.Mesh, b: mm.Mesh, op) -> mm.Mesh:
    result = mm.boolean(a, b, op)
    if not result.valid():
        raise RuntimeError(f"Mesh boolean failed: {result.errorString}")
    return result.mesh


def _half_space(side: str, y_offset: float = 0.0) -> mm.Mesh:
    """Box covering one side of the XZ split plane, shifted by `y_offset` in +Y."""
    y0 = -_BIG + y_offset if side == "left" else y_offset
    return mm.makeCube(mm.Vector3f(2 * _BIG, _BIG, 2 * _BIG), mm.Vector3f(-_BIG, y0, -_BIG))


def _toward_split(side: str) -> float:
    return 1.0 if side == "left" else -1.0


def _clip(mesh: mm.Mesh, side: str, y_offset: float = 0.0) -> mm.Mesh:
    return _boolean(mesh, _half_space(side, y_offset), mm.BooleanOperation.Intersection)


def _smooth(mesh: mm.Mesh, cfg: ScrollConfig, voxel_size: float) -> mm.Mesh:
    if cfg.smoothing == "none":
        return mesh
    if cfg.smoothing == "denoise":
        smoothed = _copy(mesh)
        settings = mm.DenoiseViaNormalsSettings()
        settings.gamma = cfg.smoothing_amount
        mm.meshDenoiseViaNormals(smoothed, settings)
    elif cfg.smoothing == "shrink_expand":
        # Shrinking then expanding rounds off convex details
        smoothed = _offset(mesh, -cfg.smoothing_amount, voxel_size)
        smoothed = _offset(smoothed, cfg.smoothing_amount, voxel_size)
    else:
        raise ValueError(f"Unknown smoothing mode: {cfg.smoothing!r}")
    # Unite with the original so smoothing never cuts into the scroll
    return mm.voxelBooleanUnite(mesh, smoothed, voxel_size)


def _align_wide_axis_to_x(mesh: mm.Mesh) -> None:
    """Rotate about Z so the scroll's wide direction lies in the split plane."""
    xy = _vertices(mesh)[:, :2]
    eigenvalues, eigenvectors = np.linalg.eigh(np.cov(xy - xy.mean(axis=0), rowvar=False))
    wide = eigenvectors[:, np.argmax(eigenvalues)]
    angle = -np.arctan2(wide[1], wide[0])
    rotation = Rotation.from_euler("z", angle).as_matrix()
    _transform(mesh, rotation, [0, 0, 0])


def prepare_scroll(cfg: CaseConfig) -> tuple[mm.Mesh, float, float]:
    """Load, clean up, and align the scroll.

    Returns the scroll mesh centered on the Z axis with its bottom at Z=0,
    plus its enclosing radius and height.
    """
    sc = cfg.scroll
    if sc.mesh is None:
        logger.info("No scroll mesh given, using a generic cylinder")
        r = sc.generic_diameter / 2
        scroll = mm.makeCylinderAdvanced(r, r, 0.0, 2 * np.pi, sc.generic_height, 128)
        return scroll, sc.generic_diameter / 2, sc.generic_height

    scroll = mm.loadMesh(Path(sc.mesh))
    if sc.scale != 1.0:
        scroll.transform(mm.AffineXf3f.linear(mm.Matrix3f.scale(sc.scale)))
    if scroll.computeBoundingBox().diagonal() < 5:
        logger.warning("Scroll mesh is very small. Is `scale` set correctly?")
    if len(mm.getAllComponents(scroll)) > 1:
        logger.warning("Scroll mesh has multiple components")

    _decimate(scroll, sc.decimate_max_error)
    scroll = _smooth(scroll, sc, cfg.voxel_size)

    if sc.auto_align:
        rotation, translation, _, _ = alignment.fit_cylinder(_vertices(scroll))
        _transform(scroll, rotation, translation)
        _align_wide_axis_to_x(scroll)

    if any(sc.rotate):
        _transform(
            scroll, Rotation.from_euler("xyz", sc.rotate, degrees=True).as_matrix(), [0, 0, 0]
        )
    if any(sc.translate):
        _translate(scroll, sc.translate)

    # Size the case around the final placement
    verts = _vertices(scroll)
    radius = float(np.linalg.norm(verts[:, :2], axis=1).max())
    z_min, z_max = float(verts[:, 2].min()), float(verts[:, 2].max())
    _translate(scroll, [0, 0, -z_min])
    logger.info("Scroll radius %.2f, height %.2f", radius, z_max - z_min)
    return scroll, radius, z_max - z_min


def build_lining(scroll: mm.Mesh, cfg: CaseConfig, layout: Layout) -> dict[str, LiningHalf]:
    """Build each half's cavity and lining wall, in case coordinates.

    The cavity is the scroll offset by `lining_offset`. With overhang removal,
    each half's cavity is extruded toward the split plane so the scroll can be
    lowered straight in, then the wall is grown around that extruded cavity.
    """
    cavity = _offset(place_scroll(scroll, layout), cfg.lining_offset, cfg.voxel_size)
    max_error = cfg.voxel_size * _DECIMATE_VOXEL_FRACTION

    halves = {}
    for side in SIDES:
        toward = _toward_split(side)
        half = _clip(cavity, side, y_offset=toward * _SPLIT_OVERCUT)
        if cfg.overhang_removal:
            # Undercuts are filled in the direction opposite `upDirection`
            params = mm.FixUndercuts.FixParams()
            params.findParameters.upDirection = mm.Vector3f(0, -toward, 0)
            params.voxelSize = cfg.voxel_size
            mm.FixUndercuts.fix(half, params)
            half = _clip(half, side, y_offset=toward * _SPLIT_OVERCUT)
        _decimate(half, max_error)

        wall = _offset(half, cfg.wall_thickness, cfg.voxel_size)
        wall = _clip(wall, side, y_offset=-toward * _SPLIT_INSET)
        _decimate(wall, max_error)
        halves[side] = LiningHalf(cavity=half, wall=wall)
    return halves


def assemble(body: mm.Mesh, half: LiningHalf) -> mm.Mesh:
    """Add the lining wall to a case body, then cut out the cavity.

    Subtracting the cavity last avoids unioning two coincident cavity surfaces.
    """
    walled = _boolean(body, half.wall, mm.BooleanOperation.Union)
    return _boolean(walled, half.cavity, mm.BooleanOperation.DifferenceAB)


def place_scroll(scroll: mm.Mesh, layout: Layout) -> mm.Mesh:
    placed = _copy(scroll)
    _translate(placed, [0, 0, layout.scroll_z])
    return placed


def load(path: str | Path) -> mm.Mesh:
    return mm.loadMesh(Path(path))


def load_brep_export(path: str | Path, max_hole_perimeter: float = 1.0) -> mm.Mesh:
    """Load a B-rep STL, closing the tiny gaps tessellation sometimes leaves."""
    mesh = load(path)
    mm.MeshBuilder.uniteCloseVertices(mesh, 1e-4)
    for edge in mesh.topology.findHoleRepresentiveEdges():
        perimeter = mesh.holePerimeter(edge)
        if perimeter > max_hole_perimeter:
            raise RuntimeError(f"{path}: B-rep export has a {perimeter:.2f} mm hole")
        mm.fillHole(mesh, edge)
    return mesh


def save(mesh: mm.Mesh, path: str | Path) -> None:
    mm.saveMesh(mesh, Path(path))
