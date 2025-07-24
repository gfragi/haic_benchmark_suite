from unittest import result
import yaml
import json
from pathlib import Path
from datetime import datetime
from haic_env_builder.components.agent import Agent
from haic_env_builder.components.profile import Profile
from haic_env_builder.components.task import Task
from haic_env_builder.utils.metrics_logger import log_simulation_metrics


def simulate_environment(config_path: str):
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    # Parse components using classes
    task = Task(**config["task"])
    agents = [Agent(**agent) for agent in config["agents"]]
    profiles = [Profile(**profile) for profile in config["profiles"]]

    # Simulation loop (mocked)
    steps = 5
    decisions = []
    for step in range(steps):
        for agent in agents:
            action = agent.act(task)
            decisions.append({
                "step": step,
                "agent": agent.name,
                "action": action
            })

    # Generate metrics (mock)
    metrics = {
        "steps": steps,
        "total_actions": len(decisions),
        "collaboration_score": round(0.6 + 0.4 * len(agents) / (len(profiles) + 1), 2),
        "efficiency_score": 0.82,
    }

    result = {
        "task": task.to_dict(),
        "agents": [agent.name for agent in agents],
        "profiles": [profile.profile_id for profile in profiles],
        "metrics": metrics,
        "decisions": decisions,
        "status": "success"
    }

    # Save result
    save_path = Path("metrics") / f"{task.name.replace(' ', '_')}_metrics.json"
    save_path.parent.mkdir(exist_ok=True)
    
    with open(save_path, "w") as f:
        json.dump(result, f, indent=2)

    log_path = log_simulation_metrics(result)
    result["log_path"] = log_path
    print(f"[✔] Simulation completed. Metrics saved to {log_path}")
    
    return result
