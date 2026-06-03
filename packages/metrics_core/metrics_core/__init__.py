# expose core metrics functions and data models

from .outcome_metrics import Metrics as OutcomeMetrics
from .interaction_metrics import (
    compute_metrics,
    compute_metrics_by_agent,
    compute_metrics_with_results,
)
from .latency import latency_percentiles_by
from .human_rt import human_response_percentiles_by

# schema.DecisionEvent  — external / storage-facing (has interaction_id, payload)
# models.DecisionEvent  — internal computation record (has agent, probs, …);
#                         exported as ComputationDecisionEvent to avoid collision
from .schema import DecisionEvent, MetricResult, SessionLog, SessionMetrics
from .models import DecisionEvent as ComputationDecisionEvent

__all__ = [
    # metrics functions
    "compute_metrics",
    "compute_metrics_by_agent",
    "compute_metrics_with_results",
    "latency_percentiles_by",
    "human_response_percentiles_by",
    "OutcomeMetrics",
    # data models
    "DecisionEvent",            # schema.DecisionEvent — storage / API
    "ComputationDecisionEvent", # models.DecisionEvent — adapter output / compute input
    "MetricResult",
    "SessionLog",
    "SessionMetrics",
]
__version__ = "0.2.0"