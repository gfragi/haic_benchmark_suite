import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any

def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def log_run_artifacts(
    run_payload: Dict[str, Any],
    out_dir: str = "metrics",
    basename_hint: str | None = None,
    write_summary: bool = True,
    write_full: bool = True,
) -> Dict[str, str]:
    """
    Persist artifacts for a single run in ONE folder.
    - write_summary: small JSON with task & metrics
    - write_full: full run payload (incl. decisions)
    Returns paths that were written.
    """
    Path(out_dir).mkdir(parents=True, exist_ok=True)

    task_name = run_payload.get("task", {}).get("name", "task").replace(" ", "_")
    base = basename_hint or task_name
    ts = _timestamp()

    paths = {}

    if write_summary:
        summary = {
            "task": run_payload.get("task"),
            "metrics": run_payload.get("metrics"),
            "num_decisions": len(run_payload.get("decisions", [])),
            "status": run_payload.get("status"),
        }
        p = Path(out_dir) / f"{base}_summary_{ts}.json"
        with open(p, "w") as f:
            json.dump(summary, f, indent=2)
        paths["summary_path"] = str(p)

    if write_full:
        p = Path(out_dir) / f"{base}_full_{ts}.json"
        with open(p, "w") as f:
            json.dump(run_payload, f, indent=2)
        paths["full_path"] = str(p)

    return paths

def log_simulation_metrics(result_dict: Dict, output_dir: str = "metrics") -> str:
    """
    Writes a metrics JSON file for a single simulation result into `output_dir`.
    File name is timestamped to avoid overwrites.

    Expected `result_dict` shape (minimum):
      {
        "task": { "name": str, ... },
        "agents": [...],
        "profiles": [...],
        "metrics": {...},
        "decisions": [...],
        ...
      }
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    task_name = (
        (result_dict.get("task", {}) or {}).get("name", "UnknownTask")
        .replace(" ", "_")
        .strip()
    ) or "UnknownTask"

    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"{task_name}_metrics_{ts}.json"
    fpath = Path(output_dir) / fname

    with open(fpath, "w") as f:
        json.dump(result_dict, f, indent=2)

    print(f"[✔] Metrics logged to {fpath}")
    return str(fpath)