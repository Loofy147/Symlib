import sys
import os
import json
import pytest
from unittest.mock import patch, MagicMock
from symlib.search.cli import main

def test_cli_help():
    with patch("sys.argv", ["symlib-search", "--help"]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 0

def test_cli_basic_run():
    # Mock run_equivariant_sa to return immediately
    with patch("symlib.search.cli.run_equivariant_sa") as mock_sa:
        mock_sa.return_value = (None, {"best": 10, "iters": 100})
        with patch("sys.argv", ["symlib-search", "--m", "3", "--iters", "100"]):
            main()
        mock_sa.assert_called_once()

def test_cli_checkpoint_loading(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.json"
    cp_data = {
        "m": 3,
        "k": 3,
        "sigma_list": [0] * 27,
        "stats": {"best": 5, "iters": 1000}
    }
    with open(checkpoint_path, "w") as f:
        json.dump(cp_data, f)

    with patch("symlib.search.cli.run_equivariant_sa") as mock_sa:
        mock_sa.return_value = (None, {"best": 5, "iters": 1100})
        with patch("sys.argv", ["symlib-search", "--m", "3", "--checkpoint", str(checkpoint_path)]):
            main()
        # Verify it was called with initial_sigma from checkpoint
        args, kwargs = mock_sa.call_args
        assert kwargs["initial_sigma"] == [0] * 27

def test_cli_mismatch_m(tmp_path):
    checkpoint_path = tmp_path / "checkpoint.json"
    cp_data = {"m": 4, "k": 3, "sigma_list": [], "stats": {"best": 5}}
    with open(checkpoint_path, "w") as f:
        json.dump(cp_data, f)

    with patch("sys.argv", ["symlib-search", "--m", "3", "--checkpoint", str(checkpoint_path)]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1

def test_cli_export_viz(tmp_path):
    viz_path = tmp_path / "out.json"
    engine = MagicMock() # ConstructionEngine mock not needed, we mock run_equivariant_sa

    with patch("symlib.search.cli.run_equivariant_sa") as mock_sa:
        # Simulate finding a solution
        from symlib.kernel.construction import ConstructionEngine
        engine = ConstructionEngine(m=3, k=3)
        sol = engine.construct()

        mock_sa.return_value = (sol, {"best": 0, "iters": 10})
        with patch("sys.argv", ["symlib-search", "--m", "3", "--export-viz", str(viz_path)]):
            main()

    assert os.path.exists(viz_path)

def test_cli_mismatch_k(tmp_path):
    checkpoint_path = tmp_path / "checkpoint_k.json"
    cp_data = {"m": 3, "k": 4, "sigma_list": [], "stats": {"best": 5}}
    with open(checkpoint_path, "w") as f:
        json.dump(cp_data, f)

    with patch("sys.argv", ["symlib-search", "--m", "3", "--k", "3", "--checkpoint", str(checkpoint_path)]):
        with pytest.raises(SystemExit) as e:
            main()
        assert e.value.code == 1
