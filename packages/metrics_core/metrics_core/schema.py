"""
metrics_core.schema
-------------------
External / storage-facing Pydantic v2 models.

These define what goes into the database and what the API returns.
They are intentionally separate from models.DecisionEvent (the internal
computation record) — the two serve different contracts:

  schema.DecisionEvent  — what haic_logging stores per-event
                          (has interaction_id, payload, enum actor_type)

  models.DecisionEvent  — what compute_metrics() consumes
                          (has agent, probs, surrogate_probs, off_role_action)

Adapters translate schema.DecisionEvent → models.DecisionEvent before
any metric computation happens.
"""
from __future__ import annotations

import re
from datetime import datetime
from enum import Enum
from typing import Any

from pydantic import BaseModel, Field, field_validator

# ---------------------------------------------------------------------------
# Enumerations
# ---------------------------------------------------------------------------

class ActorType(str, Enum):
    """Who produced a decision event."""
    human  = "human"
    ai     = "ai"
    system = "system"


# ---------------------------------------------------------------------------
# Per-event record (what haic_logging writes)
# ---------------------------------------------------------------------------

class DecisionEvent(BaseModel):
    """
    A single logged decision or action event.

    interaction_id identifies the case / ticket / image being acted on,
    enabling per-case aggregation independent of session boundaries.

    payload is an opaque dict: adapters extract what they need from it.
    """
    interaction_id: str
    timestamp: datetime | None = None
    t: float | None = None  # relative time in seconds (partner/simulator logs; pass-through)
    actor_type: ActorType | None = None
    action: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)
    latency_ms: float | None = Field(None, ge=0)
    duration_s: float | None = Field(None, ge=0)
    correct: bool | None = None

    @field_validator("timestamp", mode="before")
    @classmethod
    def _fix_nanoseconds(cls, v: Any) -> Any:
        """
        Strip sub-microsecond precision before parsing.

        Python's datetime.fromisoformat() chokes on nanosecond strings like
        "2026-02-02T08:00:00.000000729+00:00" (9 fractional digits).
        Truncate to 6 fractional digits (microseconds) so the parse succeeds.
        """
        if isinstance(v, str):
            v = re.sub(r"(\.\d{6})\d+", r"\1", v)
            v = v.replace("Z", "+00:00")
        return v


# ---------------------------------------------------------------------------
# Session record (what the log root contains)
# ---------------------------------------------------------------------------

class SessionLog(BaseModel):
    """
    One session (pilot run / evaluation) with its decision events.

    session_id is the primary key.  sim_id ties back to the simulation
    that produced the data; pilot_tag groups sessions for comparison.
    """
    sim_id: str | None = None
    session_id: str
    pilot_tag: str | None = None
    app_version: str | None = None
    ai_model_version: str | None = None
    decisions: list[DecisionEvent] = Field(default_factory=list)
    session_started_at: datetime | None = None
    session_ended_at: datetime | None = None
    meta: dict[str, Any] = Field(default_factory=dict)   # pass-through metadata (task_parameters etc.)
    extras: dict[str, Any] = Field(default_factory=dict)


# ---------------------------------------------------------------------------
# Metric output (what the API returns per session)
# ---------------------------------------------------------------------------

class MetricResult(BaseModel):
    """
    The computed value of a single named metric.

    value is None (not zero) when there was insufficient data to compute
    the metric — callers must check before plotting or alerting.

    inferred=True flags that a baseline used in the computation was
    auto-derived (e.g., median of the session) rather than explicitly
    configured, so the result should be interpreted with caution.
    """
    metric: str
    value: float | None         # None = insufficient data, not zero
    n_events: int = 0
    warning: str | None = None
    inferred: bool = False      # True if baseline was auto-derived


class SessionMetrics(BaseModel):
    """Metric results for one session, ready for the API response."""
    session_id: str
    pilot_tag: str | None
    metrics: list[MetricResult]
