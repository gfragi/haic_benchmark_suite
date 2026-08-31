"""
sim_bridge.py

Translates the output of haic_env_builder.utils.simulation_runner
.simulate_environment() into the adapter-ready session shape (a plain dict
matching metrics_core.schema.SessionLog) that process_uploaded_log() /
normalize_log_payload() already consume for every real pilot's uploaded
logs. Going through the same pipeline as real data means a simulated
config's results show up in the same Results Dashboard, survey linking,
etc. as any other config, with a single source of truth for metric
computation - simulate_environment() computes its own metrics too, but
those are a separate, standalone artifact (see /simulator/runs), not
wired into EvaluationConfig/EvaluationResult.

simulate_environment()'s decision rows already use metrics_core's own
row shape (actor_type as "human"/"ai"/"system", t, correct, latency_ms,
duration_s all at the top level) - richer than what real partners
usually send. Everything not part of the canonical DecisionEvent fields
(probs, surrogate_probs, ai_suggested, human_accepted, successful_outcome,
unsafe_event, manual_intervention, off_role_action, profile,
proposed_action) is preserved under payload, matching how the app already
reads extended-metrics inputs from payload elsewhere
(metrics_adapter.py's _payload_confidence() etc.).
"""
from __future__ import annotations

import uuid
from typing import Any

_TOP_LEVEL_FIELDS = {
    "agent", "action", "t", "actor_type", "correct", "latency_ms", "duration_s",
}


def translate_sim_run(
    run: dict[str, Any],
    *,
    pilot_tag: str,
    app_version: str,
    ai_model_version: str,
) -> dict[str, Any]:
    """One simulate_environment() result -> one adapter-ready session dict."""
    task_name = run.get("task") or "sim"
    session_id = f"{task_name}_{run.get('config_hash', '')}_{uuid.uuid4().hex[:8]}"

    decisions = []
    for i, d in enumerate(run.get("decisions") or []):
        payload = {k: v for k, v in d.items() if k not in _TOP_LEVEL_FIELDS}
        decisions.append({
            # simulate_environment()'s rows have no per-case identifier (it's
            # a tick/turn-based rollout, not a per-case review workflow) -
            # agent+index is a stable, unique-enough stand-in.
            "interaction_id": f"{d.get('agent', 'agent')}_{i}",
            "t": d.get("t"),
            "actor_type": d.get("actor_type"),
            "action": d.get("action"),
            "payload": payload,
            "correct": d.get("correct"),
            "latency_ms": d.get("latency_ms"),
            "duration_s": d.get("duration_s"),
        })

    return {
        "session_id": session_id,
        "pilot_tag": pilot_tag,
        "app_version": app_version,
        "ai_model_version": ai_model_version,
        "decisions": decisions,
    }
