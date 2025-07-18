# haic_env_builder/utils/simulation_runner.py
import yaml
from pathlib import Path

def simulate_environment(config_path: str):
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"Config not found: {config_path}")

    with open(path, "r") as f:
        config = yaml.safe_load(f)

    # Extract config parts
    task = config["task"]
    agents = config["agents"]
    profiles = config["profiles"]

    # Simulate interaction (placeholder)
    result = {
        "task_summary": f"{task['name']} executed with {len(agents)} agents and {len(profiles)} user profiles",
        "outputs": ["classification", "summary", "voice_feedback"],
        "status": "success",
        "metrics": {
            "interaction_count": 12,
            "efficiency_score": 0.84,
            "collaboration": "high"
        }
    }

    return result
