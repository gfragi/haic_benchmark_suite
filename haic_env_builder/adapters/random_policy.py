import random
import time
from typing import Any, Dict, Optional
from .model_runtime import AgentRuntime
from .overcooked_hcai import DISCRETE_ACTIONS

class RandomDiscretePolicy(AgentRuntime):
    def act(self, obs: Dict[str, Any], state: Optional[Any] = None) -> Dict[str, Any]:
        t0 = time.time()
        action = random.choice(DISCRETE_ACTIONS)
        latency_ms = (time.time() - t0) * 1000.0
        return {"action": action, "latency_ms": latency_ms, "probs": None}
