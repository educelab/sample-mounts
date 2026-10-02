"""Standalone HTML preview of a build's output STLs."""

import base64
import html
import json
from importlib.resources import files
from pathlib import Path

import trimesh

# Display order, label, color, and explode direction. The split is at Y=0
# and the stand cradles the left half from -Y, so it moves out past it.
_PARTS = {
    "left": ("Left half", "#4f8fd6", [0, -1, 0]),
    "right": ("Right half", "#d6894f", [0, 1, 0]),
    "stand": ("Stand", "#8a8f98", [0, -2, 0]),
    "scroll": ("Scroll", "#c9b48a", [0, 0, 0]),
}


def write_preview(outputs: dict[str, Path], path: str | Path, title: str = "Scroll case") -> Path:
    """Write a single HTML file that shows `outputs` (part name -> STL) in 3D.

    The meshes are embedded as one GLB. The page loads three.js from a CDN,
    so viewing it needs a network connection but no local server.
    """
    scene = trimesh.Scene()
    parts = []
    for key in sorted(outputs, key=lambda k: list(_PARTS).index(k) if k in _PARTS else len(_PARTS)):
        label, color, explode = _PARTS.get(key, (key, "#999999", [0, 0, 0]))
        scene.add_geometry(trimesh.load_mesh(outputs[key]), node_name=key, geom_name=key)
        parts.append({"key": key, "label": label, "color": color, "explode": explode})

    data = {
        "title": title,
        "parts": parts,
        "glb": base64.b64encode(scene.export(file_type="glb")).decode("ascii"),
    }
    template = files("scrollcase").joinpath("preview.html").read_text(encoding="utf-8")
    # "</" would end the inline <script> early
    payload = json.dumps(data).replace("</", "<\\/")
    page = template.replace("__TITLE__", html.escape(title)).replace("__DATA__", payload)
    path = Path(path)
    path.write_text(page, encoding="utf-8")
    return path
