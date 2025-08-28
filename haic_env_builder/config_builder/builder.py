from __future__ import annotations
from pathlib import Path
from typing import Any, Dict
import re
import yaml

from haic_env_builder.schemas.config import ConfigSchema

def _slug(s: str) -> str:
    s = s or "task"
    s = re.sub(r"[^A-Za-z0-9_.-]+", "_", s).strip("_")
    return s or "task"

class ConfigBuilder:
    def __init__(self) -> None:
        pass

    def build_config(self, user_choices: dict, output_path: str = "configs/{task_name}_env.yaml") -> str:
        """
        Rely on ConfigSchema for all normalization (legacy -> canonical).
        We just validate, dump, and write YAML.
        """
        validated = ConfigSchema(**(user_choices or {}))

        # Let pydantic render a plain dict (canonical, normalized)
        config: Dict[str, Any] = validated.model_dump(
            by_alias=False,      # keep 'profile_id' not 'id'
            exclude_none=True,   # cleaner YAML
        )

        task_name = config["task"]["name"]
        out_path = Path(output_path.format(task_name=_slug(task_name)))
        out_path.parent.mkdir(parents=True, exist_ok=True)

        with open(out_path, "w") as f:
            yaml.safe_dump(config, f, sort_keys=False, allow_unicode=True)

        print(f"[✔] Config written to {out_path}")
        return str(out_path)
