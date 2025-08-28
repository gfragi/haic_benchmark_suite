# utils/validation.py
import json
from pathlib import Path
import jsonschema
from schemas.decision import Decision, Event
from typing import Dict, Any

SCHEMA_DIR = Path(__file__).parent.parent / "docs" / "schemas"
SCHEMA_DIR.mkdir(parents=True, exist_ok=True)

def write_json_schemas():
    (SCHEMA_DIR / "decision-1.0.0.json").write_text(json.dumps(Decision.model_json_schema(), indent=2))
    (SCHEMA_DIR / "event-1.0.0.json").write_text(json.dumps(Event.model_json_schema(), indent=2))

def validate_jsonl(jsonl_path: str, schema_path: str):
    schema = json.loads(Path(schema_path).read_text())
    with open(jsonl_path) as f:
        for ln, line in enumerate(f, start=1):
            if not line.strip(): continue
            obj = json.loads(line)
            jsonschema.validate(obj, schema)

def assert_invariants(decisions_path: str, events_path: str):
    # example: monotonic t per sim_id, allowed event types, etc.
    pass



def validate_task_params(task_params: Dict[str, Any]) -> None:
    if "environment" not in task_params and "adapter" not in task_params:
        raise ValueError("task.parameters must include 'environment' (preferred) or legacy 'adapter'.")
    env_name = task_params.get("environment") or task_params.get("adapter")
    if not isinstance(env_name, str) or not env_name:
        raise ValueError("task.parameters.environment must be a non-empty string.")
    if "env_params" in task_params and not isinstance(task_params["env_params"], dict):
        raise ValueError("task.parameters.env_params must be a dict if provided.")
