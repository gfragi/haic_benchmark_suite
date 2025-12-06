"""
Policies for HAIC simulation.
Based on haic_sim_mvp engine/policies.py
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from dataclasses import dataclass


@dataclass
class PolicyResult:
    """Result of applying a policy to a sample."""
    label: Optional[str] = None
    defer: bool = False
    confidence: float = 0.0


class Policy(ABC):
    """Base policy class."""

    @abstractmethod
    def predict(self, sample: Dict[str, Any]) -> PolicyResult:
        """Predict based on sample data."""
        pass


class ThresholdPolicy(Policy):
    """Simple threshold policy - classify if prob >= threshold."""

    def __init__(self, threshold: float = 0.5):
        self.threshold = threshold

    def predict(self, sample: Dict[str, Any]) -> PolicyResult:
        p = float(sample.get("ai_prob", 0))
        if p >= self.threshold:
            return PolicyResult(label="positive", confidence=p)
        return PolicyResult(label="not_positive", confidence=p)


class L2DPolicy(Policy):
    """L2D-like policy - defer when uncertain."""

    def __init__(self, tau: float = 0.7):
        self.tau = tau  # uncertainty band threshold

    def predict(self, sample: Dict[str, Any]) -> PolicyResult:
        p = float(sample.get("ai_prob", 0))

        # Uncertainty band: (1-tau, tau)
        if (1 - self.tau) < p < self.tau:
            return PolicyResult(defer=True, confidence=p)

        # Outside band: classify
        label = "positive" if p >= self.tau else "not_positive"
        return PolicyResult(label=label, confidence=p)
