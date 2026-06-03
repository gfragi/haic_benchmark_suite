"""Adapter protocol: contract that every adapter module must satisfy."""
from __future__ import annotations

from typing import Any, List, Protocol

from metrics_core.models import DecisionEvent


class Adapter(Protocol):
    """
    Contract every adapter module must satisfy.

    Adapters own field mapping (pilot-specific aliases → canonical names)
    and type coercion.  They must NOT do timestamp→t derivation; that is
    _normalize_decisions()'s responsibility.
    """

    def to_decisions(
        self,
        events: List[dict[str, Any]],
    ) -> List[DecisionEvent]:
        """Map raw pilot events to canonical DecisionEvent records."""
        ...
