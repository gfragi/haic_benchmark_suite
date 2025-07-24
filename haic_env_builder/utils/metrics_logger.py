import json
from datetime import datetime
from pathlib import Path

def log_simulation_metrics(env_dict: dict, output_dir="metrics"):
    """
    Logs interaction metrics based on env_dict structure.
    """

    Path(output_dir).mkdir(parents=True, exist_ok=True)

    task_data = env_dict.get("task")

    # ✅ Ensure it's already a dict (safe for downstream access)
    if not isinstance(task_data, dict):
        task_data = {"name": str(task_data), "description": "", "parameters": {}}

    task_name = task_data["name"].replace(" ", "_")
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{task_name}_metrics_{timestamp}.json"
    path = Path(output_dir) / filename

    metrics = {
        "task": task_data,
        "num_agents": len(env_dict.get("agents", [])),
        "num_profiles": len(env_dict.get("profiles", [])),
        "result": env_dict.get("result", "N/A")
    }

    with open(path, "w") as f:
        json.dump(metrics, f, indent=2)

    print(f"[✔] Metrics logged to {path}")
    return str(path)
