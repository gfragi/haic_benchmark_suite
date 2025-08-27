from abc import ABC, abstractmethod
from typing import Any, Dict, Optional

class AgentRuntime(ABC):
    """Wraps a policy/runtime (rule-based, PPO, CREW, LLM)."""

    @abstractmethod
    def act(self, obs: Dict[str, Any], state: Optional[Any] = None) -> Dict[str, Any]:
        """
        Returns {"action": <action>, "latency_ms": float,
                 "probs": Optional[Dict[str, float]]}
        """
        ...

    def reset(self): ...
    def close(self): ...
