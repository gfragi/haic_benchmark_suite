# haic_env_builder/tests/test_e2e_simulation.py
from __future__ import annotations
from pathlib import Path
import json
import math

import pytest

# If you run pytest from repo root, ensure package is importable:
#   PYTHONPATH=. pytest -q
from haic_env_builder.utils.simulation_runner import simulate_environment
from metrics_core.interaction_metrics import compute_metrics

CONFIG_DIR = Path("haic_env_builder/configs")

# --- helpers -----------------------------------------------------

def _has_metric_keys(m: dict) -> bool:
    want = {"F", "D", "HCL", "Tr", "A", "S", "EL"}
    return want.issubset(set(m.keys()))

def _close(a: float, b: float, tol: float = 1e-6) -> bool:
    return math.isfinite(a) and math.isfinite(b) and abs(a - b) <= tol

# --- tests -------------------------------------------------------

@pytest.mark.parametrize(
    "cfg_name",
    [
        "CT_Scan_Diagnosis_env.yaml",
        "Kitchen_Toy_env.yaml",
    ],
)
def test_e2e_simulate_and_recompute(cfg_name: str):
    cfg_path = CONFIG_DIR / cfg_name
    assert cfg_path.exists(), f"Missing config: {cfg_path}"

    # Run simulation (deterministic with seed)
    result = simulate_environment(str(cfg_path), seed=666)

    # Basic shape
    assert "task" in result and "metrics" in result and "decisions" in result
    assert result.get("status") == "success"
    assert isinstance(result["decisions"], list) and len(result["decisions"]) > 0
    assert _has_metric_keys(result["metrics"])

    # Recompute metrics from raw decisions and compare
    recomputed = compute_metrics(decisions=result["decisions"])
    assert _has_metric_keys(recomputed)

    diffs = {k: abs(recomputed[k] - float(result["metrics"][k])) for k in recomputed.keys()}
    # Allow a tiny numerical wiggle
    for k, d in diffs.items():
        assert d <= 1e-6, f"Metric {k} mismatch: recomputed={recomputed[k]} vs reported={result['metrics'][k]} (diff={d})"


@pytest.mark.parametrize(
    "cfg_name",
    [
        "CT_Scan_Diagnosis_env.yaml",
        "Kitchen_Toy_env.yaml",
    ],
)
def test_seed_reproducibility(cfg_name: str):
    cfg_path = CONFIG_DIR / cfg_name
    assert cfg_path.exists(), f"Missing config: {cfg_path}"

    r1 = simulate_environment(str(cfg_path), seed=42)
    r2 = simulate_environment(str(cfg_path), seed=42)

    # Same metrics & same decisions order
    assert json.dumps(r1["decisions"], sort_keys=True) == json.dumps(r2["decisions"], sort_keys=True)
    assert r1["metrics"] == r2["metrics"]


@pytest.mark.parametrize(
    "cfg_name",
    [
        "CT_Scan_Diagnosis_env.yaml",
        "Kitchen_Toy_env.yaml",
    ],
)
def test_seed_variability(cfg_name: str):
    """
    Different seeds should *usually* lead to different traces/metrics.
    If this ever flaps (identical), it means the generator doesn't use the seed much,
    which is still a useful signal.
    """
    cfg_path = CONFIG_DIR / cfg_name
    assert cfg_path.exists(), f"Missing config: {cfg_path}"

    r1 = simulate_environment(str(cfg_path), seed=1)
    r2 = simulate_environment(str(cfg_path), seed=999)

    # At least one of decisions or metrics should differ
    decisions_equal = json.dumps(r1["decisions"], sort_keys=True) == json.dumps(r2["decisions"], sort_keys=True)
    metrics_equal = r1["metrics"] == r2["metrics"]

    assert not (decisions_equal and metrics_equal), "Different seeds produced identical outputs—check RNG usage."
