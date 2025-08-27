from typing import Dict, Type
from haic_env_builder.adapters.model_runtime import AgentRuntime
from haic_env_builder.adapters.random_policy import RandomDiscretePolicy

AGENT_RUNTIMES: Dict[str, Type[AgentRuntime]] = {
    "random_discrete": RandomDiscretePolicy,
    # "ppo": PPOAdapter, "crew": CrewRuntime, ...
}
