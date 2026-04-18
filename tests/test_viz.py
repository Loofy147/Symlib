import os
import json
from symlib.kernel.construction import ConstructionEngine
from symlib.search.viz import export_to_dot, export_to_json, save_viz

def test_export_to_dot():
    engine = ConstructionEngine(m=3, k=3)
    sigma = engine.construct()
    dot = export_to_dot(sigma, m=3)
    assert "digraph G {" in dot
    assert "v_0_0_0" in dot
    assert "color=\"red\"" in dot

def test_export_to_json():
    engine = ConstructionEngine(m=3, k=3)
    sigma = engine.construct()
    js_str = export_to_json(sigma, m=3)
    data = json.loads(js_str)
    assert "nodes" in data
    assert "links" in data
    assert len(data["nodes"]) == 27
    assert len(data["links"]) == 27 * 3

def test_save_viz_dot(tmp_path):
    engine = ConstructionEngine(m=3, k=3)
    sigma = engine.construct()
    path = str(tmp_path / "test.dot")
    save_viz(sigma, 3, path)
    assert os.path.exists(path)
    with open(path, "r") as f:
        assert "digraph" in f.read()

def test_save_viz_json(tmp_path):
    engine = ConstructionEngine(m=3, k=3)
    sigma = engine.construct()
    path = str(tmp_path / "test.json")
    save_viz(sigma, 3, path)
    assert os.path.exists(path)
    with open(path, "r") as f:
        data = json.load(f)
        assert "nodes" in data
