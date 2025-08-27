from abc import ABC, abstractmethod
from typing import Any, Dict, Optional, Tuple, List

class EnvAdapter(ABC):
    """Wraps a task/environment (e.g., Overcooked)."""

    @abstractmethod
    def reset(self, seed: Optional[int] = None) -> Dict[str, Any]:
        """Return initial observation/info dict."""
        ...

    @abstractmethod
    def step(self, actions: Dict[str, Any]) -> Tuple[Dict[str, Any], bool, Dict[str, Any]]:
        """
        actions: per-agent action (str/int/etc)
        returns: (event_log, done, info)
        - event_log: list of decision dicts (Decision schema)
        - done: episode finished
        - info: extra env info (scores, deliveries, etc.)
        """
        ...

    @abstractmethod
    def close(self): ...
