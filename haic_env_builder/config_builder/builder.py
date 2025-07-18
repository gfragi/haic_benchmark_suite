# haic_env_builder/config_builder/builder.py
from haic_env_builder.schemas.config import ConfigSchema
import yaml

class ConfigBuilder:
    def __init__(self):
        pass

    def build_config(self, user_choices: dict, output_path="configs/{task_name}_env.yaml"):
        validated = ConfigSchema(**user_choices)

        config = {
            "task": {
                "name": validated.task.name,
                "description": validated.task.description,
                "parameters": validated.task.parameters
            },
            "agents": [agent.dict() for agent in validated.agents],
            "profiles": [profile.dict() for profile in validated.profiles]
        }

        with open(output_path, "w") as f:
            yaml.dump(config, f)

        print(f"[✔] Config written to {output_path}")
        return output_path
