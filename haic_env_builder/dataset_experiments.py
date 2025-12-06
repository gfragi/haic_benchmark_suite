"""
Dataset experiment runner for HAIC simulations.
Based on haic_sim_mvp tools/run_dataset_experiment.py
"""
import json
from pathlib import Path
from typing import Dict, Any, Optional
from datetime import datetime

from .datasets import load_csv, make_script_from_dataset
from .policies import ThresholdPolicy, L2DPolicy


def run_dataset_experiment(
    dataset_csv: str,
    mode: str = "baseline",
    results_dir: str = "results",
    seed: Optional[int] = None
) -> Dict[str, Any]:
    """
    Run an experiment on a dataset with a specified mode.

    Args:
        dataset_csv: Path to CSV dataset file
        mode: "baseline" or "l2d"
        results_dir: Directory to save results
        seed: Random seed for reproducibility

    Returns:
        Dict with log path and summary metrics
    """
    rows = load_csv(dataset_csv)

    # Create basic config
    cfg: Dict[str, Any] = {
        "sim_id": f"exp_{mode}",
        "environment": {
            "id": "HAIC_Exp",
            "class": "base.Environment",
            "attributes": {"task": "classification"}
        },
        "agents": [
            {
                "id": "AI",
                "class": "base.Agent",
                "model": "ai",
                "affordances": ["classify"]
            },
            {
                "id": "H",
                "class": "base.Agent",
                "model": "human",
                "affordances": ["classify"]
            }
        ],
        "objects": [
            {
                "id": f"O{i+1}",
                "class": "base.Object",
                "attributes": {"row": i+1},
                "affordances": ["classify"]
            }
            for i in range(len(rows))
        ],
        "script": []
    }

    # Choose policy based on mode
    policy = ThresholdPolicy() if mode == "baseline" else L2DPolicy()

    # Generate script from dataset
    cfg["script"] = make_script_from_dataset(
        rows, "AI", "H", policy, human_accuracy=0.9
    )

    # Save config for reference
    config_path = Path(results_dir) / f"{cfg['sim_id']}_config.json"
    config_path.parent.mkdir(parents=True, exist_ok=True)
    with open(config_path, 'w') as f:
        json.dump(cfg, f, indent=2)

    # For now, return the config - the actual simulation would be run
    # through the normal simulation pipeline using haic_sim_mvp adapter
    result = {
        "config_path": str(config_path),
        "config": cfg,
        "dataset_rows": len(rows),
        "mode": mode,
        "policy": policy.__class__.__name__
    }

    # Save result
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    result_path = Path(results_dir) / f"dataset_exp_{mode}_{timestamp}.json"
    with open(result_path, 'w') as f:
        json.dump(result, f, indent=2)

    return {
        "result_path": str(result_path),
        "summary": result
    }
