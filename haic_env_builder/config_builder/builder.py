import yaml

class ConfigBuilder:
    def __init__(self, task_schema, agent_schema, profile_schema):
        self.task_schema = task_schema
        self.agent_schema = agent_schema
        self.profile_schema = profile_schema

    def build_config(self, user_choices: dict, output_path="configs/{task_name}_env.yaml"):
        config = {
            "task": {
                "name": user_choices["task_name"],
                "description": "Auto-generated task",
                "parameters": user_choices["task_params"]
            },
            "agents": user_choices["agents"],
            "profiles": user_choices["profiles"]
        }

        with open(output_path, "w") as f:
            yaml.dump(config, f)

        print(f"[✔] Config written to {output_path}")
