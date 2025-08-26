# haic_env_builder/utils/simulation_runner.py
from __future__ import annotations
from typing import Dict, Any, List, Optional
from pathlib import Path
import json
from datetime import datetime, timezone

from haic_env_builder.components.task import Task
from haic_env_builder.components.agent import Agent
from haic_env_builder.components.profile import Profile
from haic_env_builder.utils.metrics import compute_metrics
from haic_env_builder.utils.config_hash import compute_config_hash  # helper to hash config
from haic_env_builder.utils.random_seed import set_global_seed
from haic_env_builder.schemas.run_artifact import RunArtifact, Metrics as MetricsModel
import yaml

SIM_VERSION = "sim-0.1.0"
METRICS_DIR = Path("metrics")

def _load_yaml_config(path: str) -> Dict[str, Any]:
    with open(path, "r") as f:
        return yaml.safe_load(f)

def _artifact_path(task_name: str) -> Path:
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
    safe = task_name.replace(" ", "_")
    return METRICS_DIR / f"{safe}_full_{ts}.json"

def simulate_environment(config_path: str, seed: Optional[int] = None) -> Dict[str, Any]:
    cfg = _load_yaml_config(config_path)

    # Optional seed
    set_global_seed(seed)

    # Build components
    task = Task(**cfg["task"])
    agents = [Agent(**a) for a in cfg["agents"]]
    profiles = [Profile(**p) for p in cfg["profiles"]]

    # --- MOCKED decision generation (replace with your real sim loop) ---
    decisions: List[Dict[str, Any]] = []
    t = 0.0
    for step in range(10):  # toy steps
        for a in agents:
            action = a.act(task)
            decisions.append({
                "t": round(t, 3),
                "agent": a.name,
                "actor_type": "ai",          # or "human" if applicable
                "action": action,
                "latency_ms": 400 + step * 10,
                "duration_s": 0.9,
                "correct": True
            })
            t += 1.0
    # -------------------------------------------------------------------

    # Pull baseline if provided
    baseline_s = cfg["task"]["parameters"].get("baseline_s")

    # Compute metrics
    metrics_dict = compute_metrics(
        decisions=decisions,
        T=None,                     # derive from timestamps by default
        baseline_s=baseline_s,
    )
    metrics = MetricsModel(**metrics_dict)

    artifact = RunArtifact(
        version=SIM_VERSION,
        task=task.name,
        seed=seed,
        config_hash=compute_config_hash(cfg),
        T=None,  # derived
        baseline_s=baseline_s,
        agents=[a.name for a in agents],
        profiles=[p.profile_id for p in profiles],
        decisions=decisions,
        metrics=metrics,
        status="success",
    )

    path = _artifact_path(task.name)
    with open(path, "w") as f:
        f.write(artifact.model_dump_json(indent=2))

    return artifact.model_dump()  # what your API returns
