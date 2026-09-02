"""
markov.py

MarkovSurrogate: a domain-agnostic first-order Markov surrogate operator,
fitted from real pilot data (see e.g. data/sc_markov_model.json, produced by
scripts/fit_markov.py). All domain-specific action vocabulary - the AI/
operator action sets, which op actions count as "accepted", and the
original display strings for each - lives in the model JSON file (schema
"haic.markov_model.v1"); this class holds none of it.

Generates synthetic sessions in the same haic.decisions_artifact.v1 shape
real pilot logs use, so they pass through the existing ingest -> evaluate ->
dashboard pipeline unmodified.
"""
from __future__ import annotations

import json
import logging
import time
import uuid
from pathlib import Path
from typing import Any

import numpy as np
from scipy.stats import truncnorm

logger = logging.getLogger(__name__)

_MODEL_SCHEMA = "haic.markov_model.v1"
_MIN_DURATION_S = 5.0

# packages/surrogate/surrogate/markov.py -> project root is 3 parents up.
_ONTOLOGY_PATH = Path(__file__).resolve().parents[3] / "data" / "haic_ontology.json"


class MarkovSurrogate:
    """A first-order Markov surrogate for AI-evaluated -> operator-verified
    interactions, fitted from real pilot data for any domain."""

    def __init__(
        self,
        model_path: str,
        persona: str = "aggregate",
        seed: int = 42,
        smooth_epsilon: float = 0.05,
    ):
        """
        Load the fitted Markov model and configure the surrogate persona.

        persona:
          - "aggregate" - the fitted aggregate transition matrix, as-is.
          - an id present in model["by_operator"] - that operator's own fit.
          - an archetype id from haic_ontology.json's persona_archetypes
            (e.g. "high_trust", "skeptic", "expert", "novice", "from_data") -
            the aggregate matrix with that archetype's accept_bias/
            rt_multiplier applied. Falls back to "aggregate" (with a logged
            warning) if the id isn't found anywhere, or if the ontology file
            itself is missing.
        smooth_epsilon: Laplace smoothing added to each op_action cell in
            every non-null transition row before renormalizing, so sparse
            rows aren't degenerate. Archetype bias is applied on top of the
            already-smoothed aggregate matrix, not before, so it isn't
            diluted twice.
        """
        self.model_path = model_path
        self.seed = seed
        self.smooth_epsilon = smooth_epsilon
        self.rt_multiplier = 1.0

        model = json.loads(Path(model_path).read_text(encoding="utf-8"))
        if model.get("schema") != _MODEL_SCHEMA:
            raise ValueError(
                f"Unsupported model schema {model.get('schema')!r} in {model_path} "
                f"- expected {_MODEL_SCHEMA!r}"
            )

        self.domain = model["domain"]
        self.ai_actions: list[str] = model["ai_actions"]
        self.op_actions: list[str] = model["op_actions"]
        self.accept_actions: set[str] = set(model["accept_actions"])
        self.ai_action_original_strings: dict[str, str] = model["ai_action_original_strings"]
        self.op_action_original_strings: dict[str, str] = model["op_action_original_strings"]
        self.ai_freq: dict[str, float] = model["ai_action_frequency"]

        by_operator = model.get("by_operator", {})
        self.matrix = (
            by_operator[persona]
            if persona not in ("aggregate",) and persona in by_operator
            else model["aggregate"]
        )

        self.duration_stats: dict[str, dict | None] = self.matrix["duration_stats"]
        self.transition_matrix: dict[str, dict[str, float] | None] = {
            ai_action: self._smooth_row(row)
            for ai_action, row in self.matrix["transition_matrix"].items()
        }

        if persona == "aggregate":
            self.persona = "aggregate"
        elif persona in by_operator:
            self.persona = str(persona)
        else:
            self._apply_archetype(str(persona))

        np.random.seed(self.seed)

    def _apply_archetype(self, persona: str) -> None:
        """
        Resolve a persona_archetypes id (from haic_ontology.json) into a
        biased variant of the (already-smoothed) aggregate transition
        matrix. Sets self.persona and, when the archetype defines them,
        overrides self.transition_matrix / self.rt_multiplier. Falls back to
        self.persona = "aggregate" (with a logged warning) if the id can't
        be resolved.
        """
        archetype = self._load_persona_archetype(persona)
        if archetype is None:
            logger.warning(
                "Unknown persona '%s' (not 'aggregate', not an operator id in "
                "the model's by_operator, not a persona_archetypes id in %s) - "
                "falling back to aggregate.", persona, _ONTOLOGY_PATH,
            )
            self.persona = "aggregate"
            return

        # Report the archetype id even when it carries no bias (e.g.
        # "from_data", whose accept_bias/rt_multiplier are both null in the
        # ontology) - the point is to never silently relabel a recognized,
        # deliberate persona choice as "aggregate".
        self.persona = persona

        if archetype.get("accept_bias") is not None:
            self.transition_matrix = {
                ai_action: self._apply_accept_bias(row, archetype["accept_bias"])
                for ai_action, row in self.transition_matrix.items()
            }
        if archetype.get("rt_multiplier") is not None:
            self.rt_multiplier = archetype["rt_multiplier"]

    def _load_persona_archetype(self, persona_id: str) -> dict | None:
        """Look up one persona_archetypes entry by id in haic_ontology.json."""
        if not _ONTOLOGY_PATH.exists():
            logger.warning("Ontology file not found at %s - cannot resolve persona '%s'.",
                            _ONTOLOGY_PATH, persona_id)
            return None
        ontology = json.loads(_ONTOLOGY_PATH.read_text(encoding="utf-8"))
        for p in ontology.get("persona_archetypes", []):
            if p["id"] == persona_id:
                return p
        return None

    def _apply_accept_bias(self, row: dict[str, float] | None, target_accept_mass: float) -> dict[str, float] | None:
        """
        Rescale one (already-smoothed) transition row so its accept-family
        mass (sum over self.accept_actions) matches target_accept_mass,
        redistributing the rest proportionally across the remaining states,
        then renormalizing.
        """
        if row is None:
            return None

        current_accept_mass = sum(row[k] for k in self.accept_actions)
        if current_accept_mass <= 0:
            return row  # nothing to scale from - leave the row as-is

        reject_mass = 1.0 - current_accept_mass
        remaining = 1.0 - target_accept_mass
        scale = target_accept_mass / current_accept_mass

        new_probs = {}
        for k, v in row.items():
            if k in self.accept_actions:
                new_probs[k] = v * scale
            else:
                new_probs[k] = v * (remaining / reject_mass) if reject_mass > 0 else v

        total = sum(new_probs.values())
        return {k: v / total for k, v in new_probs.items()}

    def _smooth_row(self, row: dict[str, float] | None) -> dict[str, float] | None:
        """Apply Laplace smoothing to one transition row and renormalize."""
        if row is None:
            return None
        smoothed = {op: row.get(op, 0.0) + self.smooth_epsilon for op in self.op_actions}
        total = sum(smoothed.values())
        return {op: v / total for op, v in smoothed.items()}

    def _sample_ai_action(self) -> str:
        """Sample an AI action from the model's empirical frequency
        distribution. Actions with zero frequency are never drawn."""
        actions = [a for a, p in self.ai_freq.items() if p > 0]
        weights = [self.ai_freq[a] for a in actions]
        weights = np.array(weights) / sum(weights)
        return str(np.random.choice(actions, p=weights))

    def _sample_op_action(self, ai_action: str) -> tuple[str, dict[str, float]]:
        """
        Sample an operator action given the AI action.

        Returns (sampled_op_action, full_probability_dict_over_all_op_actions) -
        the full dict is what gets attached as surrogate_probs on the
        generated event.
        """
        row = self.transition_matrix.get(ai_action)
        if row is None:
            # No fitted data for this ai_action (shouldn't happen since
            # _sample_ai_action never draws a zero-frequency action, but
            # fall back to a uniform distribution rather than crashing).
            row = {op: 1.0 / len(self.op_actions) for op in self.op_actions}
        sampled = str(np.random.choice(self.op_actions, p=[row[op] for op in self.op_actions]))
        return sampled, row

    def _sample_duration(self, ai_action: str, rt_max_s: float = 300.0) -> float:
        """Sample a response time from a truncated normal fitted to this
        ai_action's real duration_s stats, bounded to [_MIN_DURATION_S, rt_max_s].
        The mean is scaled by self.rt_multiplier (1.0 unless an archetype
        persona set a different value) - std is left unscaled, per spec."""
        stats = self.duration_stats.get(ai_action)
        if stats is None:
            # No fitted duration data - fall back to the midpoint of the bounds.
            return (_MIN_DURATION_S + rt_max_s) / 2.0

        mean, std = stats["mean"] * self.rt_multiplier, stats["std"]
        if not std:
            return float(np.clip(mean, _MIN_DURATION_S, rt_max_s))

        a = (_MIN_DURATION_S - mean) / std
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
        (haic.decisions_artifact.v1) - n_items interactions, each producing
        an AI event followed by a human (operator) event."""
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
                    "ai_decision": self.ai_action_original_strings[ai_action],
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
                "correct": op_action in self.accept_actions,
                "surrogate_action": op_action,
                "surrogate_probs": probs,
                "payload": {
                    "op_decision": self.op_action_original_strings[op_action],
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
            "run_id": f"markov_{self.domain}_{self.persona}_{self.seed}_{n_items}",
            "meta": {
                "pilot_tag": f"surrogate_markov_{self.domain}",
                "application": {"name": "MarkovSurrogate", "version": "1.0.0"},
                "ai_system": {"model_name": f"markov_chain_{self.domain}", "model_type": "surrogate"},
                "task": {"name": self.domain, "domain": self.domain, "unit_of_work": "item"},
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

    def generate_batch(self, n_sessions: int = 10, n_items: int = 10, **kwargs) -> list[dict[str, Any]]:
        """
        Generate n_sessions surrogate sessions, each with an incrementing
        seed for reproducibility.
        """
        base_seed = self.seed
        sessions = []
        for i in range(n_sessions):
            self.seed = base_seed + i
            sessions.append(self.generate_session(n_items=n_items, **kwargs))
        self.seed = base_seed
        return sessions
