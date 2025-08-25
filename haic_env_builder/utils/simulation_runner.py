import json
import yaml
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any, Optional
import random

from haic_env_builder.components.agent import Agent
from haic_env_builder.components.profile import Profile
from haic_env_builder.components.task import Task
from haic_env_builder.utils.metrics_logger import compute_metrics_from_log


def _now_ts() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def simulate_environment(config_path: str, seed: Optional[int] = None) -> Dict[str, Any]:
    """
    Runs a lightweight, deterministic (if seed set) simulation based on a YAML config.
    Produces ONE timestamped file in metrics/ with both raw decisions and computed metrics.
    """
    if seed is not None:
        random.seed(seed)

    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    # ---- Parse components
    task = Task(**config["task"])
    agents: List[Agent] = [Agent(**a) for a in config["agents"]]
    profiles: List[Profile] = [Profile(**p) for p in config["profiles"]]

    # ---- Simple simulation loop
    steps = 5
    # action pool derived from agent capabilities (fallback to generic verbs)
    default_actions = ["classify", "highlight", "summarize", "speak", "respond", "move", "deliver"]
    decisions: List[Dict[str, Any]] = []

    for step in range(steps):
        for agent in agents:
            # pick an action from agent capabilities if possible
            pool = agent.capabilities if agent.capabilities else default_actions
            chosen = "classify" if "classify" in pool else random.choice(pool)

            # create interaction attributes used by metrics
            # (toy logic but reproducible with seed)
            ai_suggested = (random.random() < 0.8)  # most actions come from AI suggestion
            human_accepted = ai_suggested and (random.random() < 0.75)
            success = human_accepted or (random.random() < 0.6)
            latency_ms = int(300 + 400 * random.random())  # 300–700ms

            decisions.append({
                "step": step,
                "agent": agent.name,
                "action": chosen,
                "ai_suggested": ai_suggested,
                "human_accepted": human_accepted,
                "success": success,
                "latency_ms": latency_ms
            })

    # ---- Compute metrics FROM raw decisions
    metrics = compute_metrics_from_log(
        task_name=task.name,
        agents=[a.name for a in agents],
        decisions=decisions
    )

    # ---- Assemble single result object
    result = {
        "task": task.to_dict(),
        "agents": [a.to_dict() for a in agents],
        "profiles": [p.to_dict() for p in profiles],
        "decisions": decisions,
        "metrics": metrics,
        "status": "success",
    }

    # ---- Persist ONE timestamped file under metrics/
    out_dir = Path("metrics")
    out_dir.mkdir(parents=True, exist_ok=True)
    fname = f"{task.name.replace(' ', '_')}_metrics_{_now_ts()}.json"
    save_path = out_dir / fname
    with open(save_path, "w") as f:
        json.dump(result, f, indent=2)

    # also return path for the API / UI
    result["log_path"] = str(save_path)
    return result
