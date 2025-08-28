from typing import Dict, Any, List
from haic_env_builder.registry.task_registry import TASK_ADAPTERS
from haic_env_builder.registry.agent_registry import AGENT_RUNTIMES
from haic_env_builder.adapters.base import EnvAdapter
from haic_env_builder.adapters.model_runtime import AgentRuntime

def build_adapter(task_params: Dict[str, Any]) -> EnvAdapter:
    adapter_key = task_params.get("adapter")
    if not adapter_key:
        raise ValueError("Task parameters must include 'adapter' (e.g., 'overcooked_hcai').")
    cls = TASK_ADAPTERS.get(adapter_key)
    if not cls:
        raise ValueError(f"Unknown adapter '{adapter_key}'. Available: {list(TASK_ADAPTERS)}")
    # Pass all params except 'adapter' to constructor
    kwargs = {k: v for k, v in task_params.items() if k != "adapter"}
    return cls(**kwargs)

def build_runtimes(agent_defs: List[Dict[str, Any]]) -> Dict[str, AgentRuntime]:
    runtimes: Dict[str, AgentRuntime] = {}
    for a in agent_defs:
        name = a["name"]
        runtime_key = a.get("runtime")
        if not runtime_key:
            raise ValueError(f"Agent '{name}' missing 'runtime' (e.g., 'random_discrete').")
        cls = AGENT_RUNTIMES.get(runtime_key)
        if not cls:
            raise ValueError(f"Unknown runtime '{runtime_key}'. Available: {list(AGENT_RUNTIMES)}")
        runtimes[name] = cls()
    return runtimes
