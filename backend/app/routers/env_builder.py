from fastapi import APIRouter, Query, HTTPException
from pydantic import BaseModel
from haic_env_builder.config_builder.builder import ConfigBuilder

from pathlib import Path
import yaml

router = APIRouter()

# Define input schema (this is the raw request before validation)
class ConfigRequest(BaseModel):
    task_name: str
    task_parameters: dict
    agent_definitions: list
    profile_definitions: list

@router.post("/generate_config")
def generate_config(request: ConfigRequest):
    builder = ConfigBuilder()

    user_choices = {
        "task": {
            "name": request.task_name,
            "description": "Auto-generated from request",
            "parameters": request.task_parameters
        },
        "agents": request.agent_definitions,
        "profiles": request.profile_definitions
    }

    filename = f"{request.task_name.replace(' ', '_')}_env.yaml"
    path = f"haic_env_builder/configs/{filename}"

    builder.build_config(user_choices=user_choices, output_path=path)

    return {"message": "Environment config generated", "path": path}


@router.get("/list_configs")
def list_configs():
    config_dir = Path("haic_env_builder/configs")
    configs = [f.name for f in config_dir.glob("*.yaml")]
    return {"available_configs": configs}


@router.get("/load_config")
def load_config(name: str = Query(..., description="YAML config filename")):
    path = Path("haic_env_builder/configs") / name
    if not path.exists():
        raise HTTPException(status_code=404, detail="Config not found")

    with open(path, "r") as f:
        data = yaml.safe_load(f)

    return {"config": data}
