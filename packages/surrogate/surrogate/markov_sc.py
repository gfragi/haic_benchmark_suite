"""
markov_sc.py

MarkovSurrogateSC: a probabilistic surrogate operator for the Smart City
(Novoville permit-review) pilot, fitted from real pilot data by
scripts/fit_markov_sc.py (see data/sc_markov_model.json).

Generates synthetic sessions in the same haic.decisions_artifact.v1 shape
real pilot logs use, so they pass through the existing ingest -> evaluate
-> dashboard pipeline unmodified.
"""
from __future__ import annotations

import json
import time
import uuid
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import truncnorm

# Reverse mapping: canonical action -> original string, for the payload
# fields real partner logs use. Note "Fixed & accepted" uses an ampersand,
# not "and" - matches the real data, not the "and" spelling that appears
# in this dataset's own (stale) derive_correct_rules.
AI_ORIGINAL = {
    "ai_accept": "Accepted",
    "ai_reject": "Rejected",
    "ai_flag": "Flagged for verification",
}
OP_ORIGINAL = {
    "op_accept": "Accepted",
    "op_reject": "Rejected",
    "op_accept_verified": "Accepted after verification",
    "op_reject_verified": "Rejected after verification",
    "op_fix_accept": "Fixed & accepted",
}
OP_STATES = ["op_accept", "op_reject", "op_accept_verified", "op_reject_verified", "op_fix_accept"]
CORRECT_OP_ACTIONS = {"op_accept", "op_accept_verified", "op_fix_accept"}

_MIN_PERSONA_SAMPLES = 10
_DURATION_MIN_S = 5.0


class MarkovSurrogateSC:
    """A first-order Markov surrogate for AI-evaluated -> operator-verified
    interactions, fitted from real Smart City pilot data."""

    def __init__(
        self,
        model_path: str,
        persona: str = "aggregate",
        seed: int = 42,
        smooth_epsilon: float = 0.05,
    ):
        """
        Load the fitted Markov model and configure the surrogate persona.

        persona: "aggregate" or an operator id "1".."5". Falls back to
            "aggregate" if the requested operator has fewer than
            _MIN_PERSONA_SAMPLES records.
        smooth_epsilon: Laplace smoothing added to each of the 5 op-state
            cells in every non-null transition row before renormalizing,
            so sparse rows (ai_flag in particular, n=32) aren't degenerate.
        """
        self.model_path = model_path
        self.seed = seed
        self.smooth_epsilon = smooth_epsilon

        model = json.loads(Path(model_path).read_text(encoding="utf-8"))
        group = self._select_group(model, persona)
        self.persona = group["_persona_used"]

        self.ai_action_frequency: dict[str, float] = group["ai_action_frequency"]
        self.duration_stats: dict[str, dict | None] = group["duration_stats"]
        self.transition_matrix: dict[str, dict[str, float] | None] = {
            ai_action: self._smooth_row(row)
            for ai_action, row in group["transition_matrix"].items()
        }

        np.random.seed(self.seed)

    def _select_group(self, model: dict, persona: str) -> dict:
        """Pick the aggregate or per-operator fit, falling back to aggregate
        when the requested persona doesn't have enough samples."""
        if persona == "aggregate":
            out = dict(model["aggregate"])
            out["_persona_used"] = "aggregate"
            return out

        by_operator = model.get("by_operator", {})
        group = by_operator.get(str(persona))
        if group is None or group.get("n", 0) < _MIN_PERSONA_SAMPLES:
            out = dict(model["aggregate"])
            out["_persona_used"] = "aggregate"
            return out

        out = dict(group)
        out["_persona_used"] = str(persona)
        return out

    def _smooth_row(self, row: dict[str, float] | None) -> dict[str, float] | None:
        """Apply Laplace smoothing to one transition row and renormalize."""
        if row is None:
            return None
        smoothed = {op: row.get(op, 0.0) + self.smooth_epsilon for op in OP_STATES}
        total = sum(smoothed.values())
        return {op: v / total for op, v in smoothed.items()}

    def _sample_ai_action(self) -> str:
        """Sample an AI action from the model's empirical frequency
        distribution. Actions with zero frequency (ai_accept - never
        reaches operator review, see fit_markov_sc.py) are never drawn."""
        actions = [a for a, p in self.ai_action_frequency.items() if p > 0]
        weights = [self.ai_action_frequency[a] for a in actions]
        weights = np.array(weights) / sum(weights)
        return str(np.random.choice(actions, p=weights))

    def _sample_op_action(self, ai_action: str) -> tuple[str, dict[str, float]]:
        """
        Sample an operator action given the AI action.

        Returns (sampled_op_action, full_probability_dict_over_all_op_states) -
        the full dict is what gets attached as surrogate_probs on the
        generated event.
        """
        row = self.transition_matrix.get(ai_action)
        if row is None:
            # No fitted data for this ai_action (shouldn't happen since
            # _sample_ai_action never draws a zero-frequency action, but
            # fall back to a uniform distribution rather than crashing).
            row = {op: 1.0 / len(OP_STATES) for op in OP_STATES}
        sampled = str(np.random.choice(OP_STATES, p=[row[op] for op in OP_STATES]))
        return sampled, row

    def _sample_duration(self, ai_action: str, rt_max_s: float) -> float:
        """Sample a response time from a truncated normal fitted to this
        ai_action's real duration_s stats, bounded to [_DURATION_MIN_S, rt_max_s]."""
        stats = self.duration_stats.get(ai_action)
        if stats is None:
            # No fitted duration data - fall back to the midpoint of the bounds.
            return (_DURATION_MIN_S + rt_max_s) / 2.0

        mean, std = stats["mean"], stats["std"]
        if not std:
            return float(np.clip(mean, _DURATION_MIN_S, rt_max_s))

        a = (_DURATION_MIN_S - mean) / std
        b = (rt_max_s - mean) / std
        return float(truncnorm.rvs(a, b, loc=mean, scale=std))

    def generate_session(
        self,
        n_items: int = 10,
        rt_max_s: float = 300.0,
        baseline_s: float | None = None,
        ai_latency_ms: float = 45000.0,
    ) -> dict[str, Any]:
        """Generate one complete surrogate session as a decisions artifact
        (haic.decisions_artifact.v1) - n_items permit applications, each
        producing an AI event followed by a human (operator) event."""
        np.random.seed(self.seed)

        decisions: list[dict[str, Any]] = []
        total_duration_s = 0.0

        for i in range(n_items):
            interaction_id = f"SIM_{i + 1:04d}"

            ai_action = self._sample_ai_action()
            decisions.append({
                "interaction_id": interaction_id,
                "actor_type": "ai",
                "action": "ai_evaluated",
                "latency_ms": ai_latency_ms,
                "correct": None,
                "duration_s": None,
                "payload": {
                    "ai_decision": AI_ORIGINAL[ai_action],
                    "ai_fields_with_error": [],
                    "ai_comment": "",
                },
            })

            op_action, probs = self._sample_op_action(ai_action)
            duration_s = self._sample_duration(ai_action, rt_max_s)
            total_duration_s += duration_s

            decisions.append({
                "interaction_id": interaction_id,
                "actor_type": "human",
                "action": "operator_verified",
                "duration_s": duration_s,
                "latency_ms": None,
                "correct": op_action in CORRECT_OP_ACTIONS,
                "surrogate_action": op_action,
                "surrogate_probs": probs,
                "payload": {
                    "op_decision": OP_ORIGINAL[op_action],
                    "op_id": self.persona,
                    "role": "operator",
                },
            })

        start_time = time.time()
        end_time = start_time + total_duration_s

        return {
            "artifact_schema": "haic.decisions_artifact.v1",
            "schema_version": "haic.decisions.v1",
            "session_id": f"surrogate_{uuid.uuid4().hex[:8]}",
            "run_id": f"markov_sc_{self.persona}_{self.seed}_{n_items}",
            "meta": {
                "pilot_tag": "surrogate_sc_markov",
                "application": {"name": "MarkovSurrogateSC", "version": "1.0.0"},
                "ai_system": {"model_name": "markov_chain_sc", "model_type": "surrogate"},
                "task": {"name": "permit_review", "domain": "smart_city", "unit_of_work": "application"},
                "human": {"actor_id": self.persona, "role": "operator", "expertise": "unknown"},
                "sim": {
                    "persona": self.persona,
                    "seed": self.seed,
                    "n_items": n_items,
                    "smooth_epsilon": self.smooth_epsilon,
                    "model_source": self.model_path,
                },
                "timestamps": {"start_time": start_time, "end_time": end_time},
            },
            "decisions": decisions,
        }

    def generate_batch(self, n_sessions: int = 10, n_items: int = 164, **kwargs) -> list[dict[str, Any]]:
        """
        Generate n_sessions surrogate sessions, each with an incrementing
        seed for reproducibility. Default n_items=164 matches the real
        pilot's operator-reviewed count (see sc_markov_model.json meta.n_valid).
        """
        base_seed = self.seed
        sessions = []
        for i in range(n_sessions):
            self.seed = base_seed + i
            sessions.append(self.generate_session(n_items=n_items, **kwargs))
        self.seed = base_seed
        return sessions


if __name__ == "__main__":
    surrogate = MarkovSurrogateSC(model_path="data/sc_markov_model.json", persona="aggregate", seed=42)
    session = surrogate.generate_session(n_items=5)

    print(json.dumps(session, indent=2))
    print()

    decisions = session["decisions"]
    for d in decisions:
        assert d["actor_type"] in ("ai", "human"), f"unexpected actor_type: {d}"

    human_events = [d for d in decisions if d["actor_type"] == "human"]
    for d in human_events:
        probs = d["surrogate_probs"]
        assert set(probs.keys()) == set(OP_STATES), f"surrogate_probs missing keys: {probs}"
        assert abs(sum(probs.values()) - 1.0) < 1e-9, f"surrogate_probs doesn't sum to 1.0: {probs}"
        assert isinstance(d["correct"], bool), f"correct is not a bool: {d}"
        assert 5.0 <= d["duration_s"] <= 300.0, f"duration_s out of bounds: {d}"

    print("Smoke test passed")
