from fastapi import APIRouter
from pydantic import BaseModel
from haic_env_builder.config_builder.builder import ConfigBuilder


router = APIRouter()

#  Define the input schema
class ConfigRequest(BaseModel):
    task_name: str
    task_parameters: dict
    agent_definitions: list
    profile_definitions: list

#  Define the endpoint
@router.post("/generate_config")
def generate_config(request: ConfigRequest):
    builder = ConfigBuilder()

    builder.add_task(request.task_name, request.task_parameters)

    for agent in request.agent_definitions:
        builder.add_agent(agent["name"], agent["capabilities"], agent["modality"])

    for profile in request.profile_definitions:
        builder.add_profile(profile["id"], profile["skill_level"], profile["role"])

    config_path = builder.build_config(output_dir="haic_env_builder/configs")

    return {"message": "Environment config generated", "path": config_path}
