import json
import subprocess
import sys
import textwrap

import meshlib.mrmeshpy as mm
import pytest


def run_brep(code: str):
    """Run build123d code in a subprocess and return the JSON it prints.

    meshlib is loaded in the test process and conflicts with build123d.
    """
    result = subprocess.run(
        [sys.executable, "-c", textwrap.dedent(code)], capture_output=True, text=True
    )
    assert result.returncode == 0, result.stderr
    return json.loads(result.stdout.strip().splitlines()[-1])


def is_closed(mesh: mm.Mesh) -> bool:
    return mesh.topology.findHoleRepresentiveEdges().size() == 0


def inside(mesh: mm.Mesh, point) -> bool:
    return mm.findSignedDistance(mm.Vector3f(*map(float, point)), mesh).dist < 0


@pytest.fixture(scope="session")
def undercut_scroll(tmp_path_factory):
    """A tilted, off-center I-beam. Its flanges overhang both sides of the split."""
    from scipy.spatial.transform import Rotation

    def box(size, corner):
        return mm.makeCube(mm.Vector3f(*size), mm.Vector3f(*corner))

    flange, web, height = (40, 6), (6, 12), 60
    mesh = box((*flange, height), (-20, -12, 0))
    for part in (box((*flange, height), (-20, 6, 0)), box((*web, height), (-3, -6, 0))):
        mesh = mm.boolean(mesh, part, mm.BooleanOperation.Union).mesh
    rot = Rotation.from_euler("xyz", [20, -10, 35], degrees=True).as_matrix()
    rows = [mm.Vector3f(*map(float, row)) for row in rot]
    mesh.transform(mm.AffineXf3f(mm.Matrix3f(*rows), mm.Vector3f(9, -4, 15)))
    path = tmp_path_factory.mktemp("scroll") / "undercut.stl"
    mm.saveMesh(mesh, path)
    return path
