from abc import ABC, abstractmethod
from typing import Dict, Any, List

class ScenarioRunner(ABC):
    """Κοινό interface για όλα τα σενάρια."""
    def __init__(self, config: Dict[str, Any]):
        self.config = config

    @abstractmethod
    def step_loop(self) -> Dict[str, Any]:
        """Εκτελεί τη βασική λογική (π.χ. N steps) και επιστρέφει decisions + raw stats."""
        ...

    @abstractmethod
    def compute_metrics(self, trace: Dict[str, Any]) -> Dict[str, float]:
        """Υπολογίζει μετρικές πάνω στο trace (π.χ. F, D, HCL, Tr, A, S, EL)."""
        ...
