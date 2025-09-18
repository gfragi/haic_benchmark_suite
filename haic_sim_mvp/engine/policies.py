
from dataclasses import dataclass
from typing import Any, Dict

@dataclass
class PolicyResult: # Result of a policy prediction
    label: Any
    confidence: float = 1.0
    defer: bool = False

class Policy: # Base class for policies
    def predict(self, sample: Dict[str, Any]) -> PolicyResult: raise NotImplementedError

class ThresholdPolicy(Policy): # Classify based on a probability threshold
    def __init__(self, positive_label="positive", threshold=0.5):
        self.positive_label, self.threshold = positive_label, threshold

    def predict(self, sample: Dict[str, Any]) -> PolicyResult:
        p = float(sample.get("ai_prob", 0.0))
        label = self.positive_label if p >= self.threshold else f"not_{self.positive_label}"
        return PolicyResult(label, p, False)

class L2DPolicy(Policy): # Classify based on a probability distribution
    def __init__(self, positive_label="positive", tau=0.7): # Defer if p in (1-tau, tau)
        self.positive_label, self.tau = positive_label, tau

    def predict(self, sample: Dict[str, Any]) -> PolicyResult: # Classify based on a probability distribution
        p = float(sample.get("ai_prob", 0.0))
        if p < self.tau and p > 1.0 - self.tau:
            return PolicyResult(None, p, True)
        label = self.positive_label if p >= 0.5 else f"not_{self.positive_label}"
        return PolicyResult(label, p, False)
