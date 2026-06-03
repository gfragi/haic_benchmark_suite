"""
metrics_core.models
-------------------
Canonical data contract between adapters and computation functions.

DecisionEvent is the single source of truth for what a normalized decision
looks like.  Adapters produce it; interaction_metrics consumes it.

_parse_ts and _safe_float are shared utilities imported by both adapters
and interaction_metrics — define them here once.
"""
from __future__ import annotations

import math
import re
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from pydantic import BaseModel, ConfigDict, Field, field_validator


# ---------------------------------------------------------------------------
# Shared helpers (used by adapters AND interaction_metrics)
# ---------------------------------------------------------------------------

def _parse_ts(ts: Any) -> Optional[datetime]:
    """
    Parse a timestamp value to a timezone-aware UTC datetime.

    Handles:
      - datetime objects (naive → UTC assumed)
      - numeric epoch: seconds, milliseconds (>1e12), nanoseconds (>1e15)
      - ISO-8601 strings (with or without trailing Z)

    Returns None on any parse failure; never raises.
    """
    if ts is None:
        return None
    if isinstance(ts, datetime):
        return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)
    if isinstance(ts, (int, float)):
        v = float(ts)
        if v > 1e15:        # nanoseconds  (~1.77e18 in 2026)
            v /= 1e9
        elif v > 1e12:      # milliseconds (~1.77e12 in 2026)
            v /= 1e3
        # else: already seconds
        try:
            return datetime.fromtimestamp(v, tz=timezone.utc)
        except (OSError, OverflowError, ValueError):
            return None
    try:
        s = str(ts).replace("Z", "+00:00")
        # Strip sub-microsecond digits: "2026-02-02T08:00:00.000000729+00:00"
        # → "2026-02-02T08:00:00.000000+00:00" so fromisoformat() doesn't choke.
        s = re.sub(r"(\.\d{6})\d+", r"\1", s)
        parsed = datetime.fromisoformat(s)
        return parsed if parsed.tzinfo else parsed.replace(tzinfo=timezone.utc)
    except (ValueError, TypeError):
        return None


def _safe_float(v: Any, default: Optional[float] = None) -> Optional[float]:
    """
    Convert *v* to float without raising.  Returns *default* on failure.

    bool is treated as 1.0 / 0.0 (not 1 / 0 via int conversion).
    """
    if v is None:
        return default
    if isinstance(v, bool):
        return 1.0 if v else 0.0
    try:
        return float(v)
    except (TypeError, ValueError):
        return default


# ---------------------------------------------------------------------------
# Canonical decision record produced by all adapters
# ---------------------------------------------------------------------------

_ACTOR_NORMALISE = {"human": "human", "ai": "ai", "system": "system"}


class DecisionEvent(BaseModel):
    """
    A single decision / event record in canonical form.

    Adapters are responsible for:
      - field mapping  (pilot-specific aliases → canonical names)
      - type coercion  (strings → float / bool)

    _normalize_decisions() is responsible for:
      - deriving numeric *t* from *timestamp* when absent
      - sorting by *t*

    All fields except *agent* are optional so that partial data from any
    pilot schema can be represented without fabricating values.
    """
    model_config = ConfigDict(extra="ignore")

    # Identity
    agent: str
    actor_type: str = "unknown"     # "human" | "ai" | "system" | "unknown"
    action: Optional[str] = None

    # Time — adapters set timestamp; _normalize_decisions derives t
    t: Optional[float] = None           # seconds, monotonic within session
    timestamp: Optional[datetime] = None  # UTC datetime

    # Performance
    duration_s: Optional[float] = Field(None, ge=0)
    latency_ms: Optional[float] = Field(None, ge=0)
    correct: Optional[bool] = None

    # Surrogate similarity
    probs: Optional[Dict[str, float]] = None
    surrogate_probs: Optional[Dict[str, float]] = None
    surrogate_action: Optional[str] = None

    # Event metadata
    event_type: Optional[str] = None
    off_role_action: Optional[bool] = None

    # ------------------------------------------------------------------
    # Validators: coerce at the boundary so downstream never sees bad types
    # ------------------------------------------------------------------

    @field_validator("actor_type", mode="before")
    @classmethod
    def _normalise_actor_type(cls, v: Any) -> str:
        if v is None:
            return "unknown"
        s = str(v).strip().lower()
        return _ACTOR_NORMALISE.get(s, s)

    @field_validator("duration_s", "latency_ms", mode="before")
    @classmethod
    def _coerce_non_negative_float(cls, v: Any) -> Optional[float]:
        if v is None:
            return None
        result = _safe_float(v)
        return None if result is None else max(0.0, result)

    @field_validator("timestamp", mode="before")
    @classmethod
    def _coerce_timestamp(cls, v: Any) -> Optional[datetime]:
        if isinstance(v, datetime):
            return v if v.tzinfo else v.replace(tzinfo=timezone.utc)
        return _parse_ts(v)

    @field_validator("correct", mode="before")
    @classmethod
    def _coerce_correct(cls, v: Any) -> Optional[bool]:
        if v is None:
            return None
        if isinstance(v, bool):
            return v
        s = str(v).strip().lower()
        if s in {"true", "1", "yes", "correct"}:
            return True
        if s in {"false", "0", "no", "incorrect"}:
            return False
        return None

    @field_validator("probs", "surrogate_probs", mode="before")
    @classmethod
    def _coerce_prob_dict(cls, v: Any) -> Optional[Dict[str, float]]:
        if v is None:
            return None
        if not isinstance(v, dict) or not v:
            return None
        out: Dict[str, float] = {}
        for k, val in v.items():
            f = _safe_float(val)
            if f is not None:
                out[str(k)] = f
        return out if out else None


# ---------------------------------------------------------------------------
# Output models
# ---------------------------------------------------------------------------

class MetricResult(BaseModel):
    """Wrapper for a single named metric value — useful for per-metric reporting."""
    metric: str
    value: float
    unit: Optional[str] = None
    ok: bool = True
    note: Optional[str] = None


class ComputeMetricsOutput(BaseModel):
    """Typed output of compute_metrics().  Mirrors the dict keys exactly."""
    F: float = Field(description="Interaction frequency (interactions / min)")
    D: float = Field(description="Mean action duration (s)")
    HCL: float = Field(description="Human cognitive load proxy [0, 1]")
    Tr: float = Field(description="Trust / reliability [0, 1]")
    A: float = Field(description="Adaptability [-1, 1]")
    S: float = Field(description="Surrogate similarity [0, 1]")
    EL: float = Field(description="Effort loss vs baseline [0, ∞)")
    EfficiencyScore: float = Field(description="Composite efficiency score [0, 1]")

    def to_metric_results(self) -> list[MetricResult]:
        units = {"F": "interactions/min", "D": "s", "EL": "ratio"}
        return [
            MetricResult(metric=k, value=v, unit=units.get(k))
            for k, v in self.model_dump().items()
        ]
