from __future__ import annotations
from pathlib import Path
from typing import Any, Dict, List, Optional
import yaml
import random

from haic_env_builder.components.task import Task
from haic_env_builder.components.profile import Profile
from haic_env_builder.components.agent import Agent
from haic_env_builder.utils.random_seed import set_global_seed
from haic_env_builder.utils.config_hash import stable_config_hash
from haic_env_builder.utils.metrics_logger import log_run_artifacts
from haic_env_builder.utils.metrics import compute_metrics

def _infer_total_time(steps: int, dt: float) -> float:
    # If steps timestamps are 0, dt, 2dt, ..., (steps-1)dt -> total_time = (steps-1)*dt
    if steps <= 1:
        return 0.0
    return (steps - 1) * dt

def simulate_environment(config_path: str, seed: Optional[int] = None) -> Dict[str, Any]:
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    # 1) Seed all RNGs for reproducibility
    set_global_seed(seed)

    # 2) Parse components
    task = Task(**config["task"])
    agents = [Agent(**a) for a in config["agents"]]
    profiles = [Profile(**p) for p in config["profiles"]]

    # 3) Deterministic sim loop params
    steps: int = int(config.get("sim", {}).get("steps", 5))
    dt: float = float(config.get("sim", {}).get("dt", 0.5))   # seconds per step

    # 4) Decisions (deterministic timestamps; stable latencies from seeded RNG)
    decisions: List[Dict[str, Any]] = []
    t = 0.0
    cumulative_reward = 0.0

    for step in range(steps):
        for agent in agents:
            # deterministic latency draw (seeded)
            base_lat = 0.2 if agent.modality == "text" else 0.35
            jitter = random.uniform(-0.05, 0.05)  # stable under fixed seed
            latency = max(0.01, base_lat + jitter)

            # dummy accepted flag for ai actors (if your agent semantics demand)
            accepted = None
            if "suggest" in agent.capabilities or "classify" in agent.capabilities:
                # simulate a “human accepted AI suggestion” ~ 70% (seeded)
                accepted = random.random() < 0.7

            # update reward deterministically (toy)
            reward_delta = 0.05 if accepted or accepted is None else -0.02
            cumulative_reward += reward_delta

            decisions.append({
                "t": round(t, 6),
                "actor": "ai" if agent.name.lower().endswith("assistant") else "human",
                "action": agent.act(task),
                "latency": round(latency, 6),
                "accepted": accepted,
                "reward": round(cumulative_reward, 6),
            })
        t += dt

    # 5) Compute metrics (deterministic given seed+config)
    total_time = _infer_total_time(steps, dt)
    metrics = compute_metrics(
    decisions,
    total_time=total_time,
    steps=steps,
    num_agents=len(agents),
    dt=dt,
)

    # 6) Build full result payload with provenance
    cfg_hash = stable_config_hash(config)
    full_result = {
        "task": task.to_dict(),
        "agents": [a.to_dict() for a in agents],
        "profiles": [p.to_dict() for p in profiles],
        "sim": {"steps": steps, "dt": dt, "total_time": total_time},
        "provenance": {
            "seed": seed,
            "config_hash": cfg_hash,
            "config_path": str(path),
        },
        "decisions": decisions,
        "metrics": metrics,
        "status": "success",
    }

    # 7) Write artifacts (runs/ + metrics/)
    paths = log_run_artifacts(task.name, seed, cfg_hash, full_result, metrics)
    full_result["artifact_paths"] = paths
    return full_result
