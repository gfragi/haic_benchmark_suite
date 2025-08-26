from __future__ import annotations
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def ensure_dirs():
    Path("metrics").mkdir(parents=True, exist_ok=True)
    Path("runs").mkdir(parents=True, exist_ok=True)

def write_json(path: Path, data: Dict[str, Any]) -> str:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    return str(path)

def log_run_artifacts(
    task_name: str,
    seed: int | None,
    cfg_hash: str,
    full_result: Dict[str, Any],
    metrics: Dict[str, float]
) -> Dict[str, str]:
    """
    Writes:
      - runs/{task}_{timestamp}_seed{seed}_{hash}.json      (full run: config, decisions, metrics)
      - metrics/{task}_{timestamp}_seed{seed}_{hash}.json   (metrics only)
    Returns paths.
    """
    ensure_dirs()
    safe_task = task_name.replace(" ", "_")
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    seed_tag = f"seed{seed}" if seed is not None else "seedNA"
    base = f"{safe_task}_{ts}_{seed_tag}_{cfg_hash}"

    run_path = Path("runs") / f"{base}.json"
    metrics_path = Path("metrics") / f"{base}.json"

    write_json(run_path, full_result)
    write_json(metrics_path, {"task": task_name, "seed": seed, "config_hash": cfg_hash, "metrics": metrics})

    return {"run_path": str(run_path), "metrics_path": str(metrics_path)}