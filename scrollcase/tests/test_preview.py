import base64
import io
import json
import re

import trimesh

from scrollcase.preview import write_preview


def _page_data(path):
    match = re.search(r'<script id="data" type="application/json">(.*?)</script>', path.read_text())
    return json.loads(match.group(1))


def test_preview_embeds_every_part(tmp_path):
    outputs = {}
    for i, key in enumerate(("scroll", "right", "left")):
        outputs[key] = tmp_path / f"{key}.stl"
        trimesh.creation.box(extents=(10, 10, 10 + i)).export(outputs[key])

    page = write_preview(outputs, tmp_path / "p.html", title="A</script><b>")
    data = _page_data(page)

    # Listed in display order, each as a named GLB node with its mesh intact
    assert [p["key"] for p in data["parts"]] == ["left", "right", "scroll"]
    glb = io.BytesIO(base64.b64decode(data["glb"]))
    scene = trimesh.load(glb, file_type="glb")
    assert set(scene.graph.nodes_geometry) == {"left", "right", "scroll"}
    assert scene.geometry["left"].extents[2] == 12

    assert data["title"] == "A</script><b>"
    assert "<title>A&lt;/script&gt;&lt;b&gt;</title>" in page.read_text()
