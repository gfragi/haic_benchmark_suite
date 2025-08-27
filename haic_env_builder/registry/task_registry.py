from typing import Dict, Type
from haic_env_builder.adapters.base import EnvAdapter
from haic_env_builder.adapters.overcooked_hcai import OvercookedHCAdapter

TASK_ADAPTERS: Dict[str, Type[EnvAdapter]] = {
    "overcooked_hcai": OvercookedHCAdapter,
    # "toy": ToyAdapter, etc.
}
