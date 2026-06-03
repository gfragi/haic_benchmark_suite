from __future__ import annotations
from typing import Dict, Any, List


def make_pilot_contract(
    *,
    sim_id: str,
    pilot_tag: str,
    domain: str,
    task: str,
    actors: List[Dict[str, Any]],
    objects: List[Dict[str, Any]],
    affordances: List[Dict[str, Any]],
    action_map: Dict[str, str],
    derive_correct_rules: List[Dict[str, Any]] | None,
    rt_limits: Dict[str, Any] | None,
) -> Dict[str, Any]:
    """
    Pilot Environment Contract (semantic contract for evaluation).
    """
    out: Dict[str, Any] = {
        "sim_id": sim_id,
        "pilot_tag": pilot_tag,
        "environment": {
            "domain": domain,
            "task": task,
        },
        "actors": actors,
        "objects": objects,
        "affordances": affordances,
        "action_map": action_map or {},
    }
    if derive_correct_rules:
        out["derive_correct_rules"] = derive_correct_rules
    if rt_limits:
        out["rt_limits"] = rt_limits
    return out


def make_sample_log_template(
    *,
    sim_id: str,
    pilot_tag: str,
    app_version: str | None = None,
    ai_model_version: str | None = None,
    session_id: str = "session_001",
    interaction_id: str = "interaction_001",
    example_actions: List[str] | None = None,
) -> Dict[str, Any]:
    """
    Minimal log skeleton pilots can fill.
    """
    if example_actions is None:
        example_actions = ["application_created", "ai_evaluated", "operator_verified"]

    decisions = []
    # event 1
    decisions.append({
        "interaction_id": interaction_id,
        "timestamp": "2026-01-01T10:00:00+00:00",
        "actor_type": "human",
        "action": example_actions[0],
        "payload": {"note": "example payload"},
    })
    # event 2
    decisions.append({
        "interaction_id": interaction_id,
        "timestamp": "2026-01-01T10:00:05+00:00",
        "actor_type": "ai",
        "action": example_actions[1],
        "latency_ms": 1500,
        "payload": {"ai_decision": "Accepted"},
    })
    # event 3
    decisions.append({
        "interaction_id": interaction_id,
        "timestamp": "2026-01-01T10:01:00+00:00",
        "actor_type": "human",
        "action": example_actions[2],
        "duration_s": 32.5,
        "payload": {"op_decision": "Accepted"},
    })

    log = {
        "logs": [{
            "sim_id": sim_id,
            "session_id": session_id,
            "pilot_tag": pilot_tag,
            "decisions": decisions
        }]
    }

    if app_version:
        log["logs"][0]["app_version"] = app_version
    if ai_model_version:
        log["logs"][0]["ai_model_version"] = ai_model_version

    return log

FIELD_HELP = {
    "pilot_tag": "Short pilot identifier used for grouping and dashboard filters (e.g., applications, manufacturing, health).",
    "sim_id": "Stable ID for the pilot scenario/application. Keep constant across runs for comparability.",
    "domain": "Domain label (e.g., smart-cities, manufacturing, healthcare).",
    "task": "High-level task name (e.g., application_review, module_assignment).",
    "actor_type": "Who produced the event: human | ai | system.",
    "action": "Pilot-specific event name (e.g., ai_evaluated). You will map it to a canonical affordance.",
    "timestamp": "ISO timestamp of the event. Used to order events and compute time windows.",
    "latency_ms": "AI/system execution time for the action (milliseconds). Enables latency percentiles (p50/p90/p95).",
    "duration_s": "Human time spent on an action (seconds). Enables human-effort analytics.",
    "interaction_id": "ID for the item within a session (e.g., ticket_id, image_id, application_id).",
    "session_id": "ID for the overall work session/batch/run. Can be a day, a shift, or a batch identifier.",
    "payload": "Pilot-owned domain fields. Stored and passed-through; not required for core metrics.",
    "action_map": "Mapping from pilot action strings to canonical affordance keys.",
    "derive_correct_rules": "Optional rules for deriving agreement (correct) from AI and human decisions.",
    "app_version": "Version of the application producing the logs.",
    "ai_model_version": "Version of the AI model used in the pilot.",
    "rt_max_ai_ms": "Maximum allowed AI response time (milliseconds) for real-time constraints.",
    "rt_max_human_s": "Maximum allowed human response time (seconds) for real-time constraints.",
    "actor_id": "Unique identifier for the human or AI actor.",
    "role": "Role of the actor in the process (e.g., reviewer, approver).",
    "object_id": "Unique identifier for the object being acted upon (e.g., application ID).",
    "object_kind": "Type or category of the object (e.g., loan_application, image).",
}