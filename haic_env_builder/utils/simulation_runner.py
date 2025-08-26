from __future__ import annotations
import yaml, json, random, time
from pathlib import Path
from datetime import datetime

from haic_env_builder.components.agent import Agent
from haic_env_builder.components.profile import Profile
from haic_env_builder.components.task import Task
from haic_env_builder.utils.metrics_logger import log_simulation_metrics
from haic_env_builder.utils.metrics import compute_metrics

METRICS_DIR = Path("metrics")

def _timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")

def simulate_environment(config_path: str, seed: int | None = None):
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    if seed is not None:
        random.seed(seed)

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    task = Task(**config["task"])
    agents = [Agent(**a) for a in config["agents"]]
    profiles = [Profile(**p) for p in config["profiles"]]

    # --- Simple interaction loop (mock) -------------------------------------
    steps = 5
    decisions = []
    last_source = "human"
    for step in range(steps):
        for agent in agents:
            # Alternate source to let fluency/adaptability have signal
            source = "ai" if last_source == "human" else "human"
            last_source = source

            latency_ms = random.randint(500, 2300) if source == "ai" else random.randint(800, 2800)
            time.sleep(0.0)  # no real wait, keep 0 for speed

            action = "classify" if "classify" in agent.capabilities else (agent.capabilities[0] if agent.capabilities else "idle")
            accepted = None
            override = None
            error = random.random() < 0.05
            correction = random.random() < 0.02
            risk = random.uniform(0.0, 0.9)

            if source == "ai":
                accepted = random.random() > 0.2  # human usually accepts
            else:
                override = random.random() < 0.1   # human sometimes overrides AI

            decisions.append({
                "step": step,
                "agent": agent.name,
                "source": source,
                "action": action,
                "latency_ms": latency_ms,
                "accepted": accepted,
                "override": override,
                "error": error,
                "correction": correction,
                "risk": risk,
            })

    # --- Real metrics --------------------------------------------------------
    hc_metrics = compute_metrics(decisions)

    result = {
        "task": task.to_dict(),
        "agents": [a.to_dict() for a in agents],
        "profiles": [p.to_dict() for p in profiles],
        "metrics": hc_metrics,
        "decisions": decisions,
        "status": "success",
        "seed": seed,
    }

    # Save full run + summary under /metrics with consistent naming
    METRICS_DIR.mkdir(parents=True, exist_ok=True)
    base = task.name.replace(" ", "_")
    ts = _timestamp()

    full_path = METRICS_DIR / f"{base}_full_{ts}.json"
    with open(full_path, "w") as f:
        json.dump(result, f, indent=2)

    summary = {
        "task": task.name,
        "timestamp": ts,
        "metrics": hc_metrics,
        "agents": [a.name for a in agents],
        "profiles": [p.profile_id for p in profiles],
        "seed": seed,
        "file": full_path.name,
    }
    summary_path = METRICS_DIR / f"{base}_summary_{ts}.json"
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)

    # Keep the existing “metrics logger” file for backward compatibility
    result["log_path"] = log_simulation_metrics(result)

    return result
