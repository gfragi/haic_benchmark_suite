from __future__ import annotations
from typing import Any, Dict, List, Tuple, Set
from datetime import datetime


def _parse_logs_blob(blob: Any) -> List[Dict[str, Any]]:
    """
    Accepts either:
    - {"logs":[{...}]}  (your current format)
    - [{...}]           (list of sessions)
    - {...}             (single session)
    Returns list of session dicts with "decisions".
    """
    if blob is None:
        return []
    if isinstance(blob, dict) and "logs" in blob and isinstance(blob["logs"], list):
        return [s for s in blob["logs"] if isinstance(s, dict)]
    if isinstance(blob, list):
        return [s for s in blob if isinstance(s, dict)]
    if isinstance(blob, dict):
        return [blob]
    return []


def extract_actions_from_logs(blob: Any) -> Set[str]:
    sessions = _parse_logs_blob(blob)
    actions: Set[str] = set()
    for s in sessions:
        for d in s.get("decisions", []) or []:
            if isinstance(d, dict) and d.get("action"):
                actions.add(str(d["action"]))
    return actions


def validate_logs_against_contract(
    *,
    contract: Dict[str, Any],
    logs_blob: Any,
    action_map: Dict[str, str],
) -> Dict[str, Any]:
    """
    Validates minimal requirements + mapping coverage.
    """
    sessions = _parse_logs_blob(logs_blob)
    affordance_keys = set(a.get("key") for a in (contract.get("affordances") or []) if isinstance(a, dict))

    discovered_actions = sorted(list(extract_actions_from_logs(logs_blob)))
    unmapped_actions: List[str] = []
    mapped_to_unknown_affordance: List[Tuple[str, str]] = []

    # core field checks
    missing_actor_type = 0
    missing_timestamp = 0
    missing_action = 0
    missing_interaction_id = 0
    missing_latency_ms = 0
    missing_duration_s = 0

    total_events = 0
    ai_events = 0
    human_events = 0

    # timestamp parsing warnings
    bad_timestamp = 0

    for s in sessions:
        for d in s.get("decisions", []) or []:
            if not isinstance(d, dict):
                continue
            total_events += 1

            if d.get("interaction_id") is None:
                missing_interaction_id += 1
            if d.get("actor_type") is None:
                missing_actor_type += 1
            if d.get("action") is None:
                missing_action += 1
            if d.get("timestamp") is None:
                missing_timestamp += 1
            else:
                # lightweight parse check
                try:
                    datetime.fromisoformat(str(d["timestamp"]).replace("Z", "+00:00"))
                except Exception:
                    bad_timestamp += 1

            actor_type = str(d.get("actor_type") or "")
            if actor_type == "ai":
                ai_events += 1
                if d.get("latency_ms") is None:
                    missing_latency_ms += 1
            if actor_type == "human":
                human_events += 1
                if d.get("duration_s") is None:
                    missing_duration_s += 1

    # mapping checks
    for act in discovered_actions:
        mapped = action_map.get(act)
        if not mapped:
            # allow direct match if action equals affordance key
            if act not in affordance_keys:
                unmapped_actions.append(act)
        else:
            if mapped not in affordance_keys:
                mapped_to_unknown_affordance.append((act, mapped))

    # coverage hints (very rough)
    coverage = {
        "latency_analytics_possible": ai_events > 0 and (missing_latency_ms < ai_events),
        "human_time_analytics_possible": human_events > 0 and (missing_duration_s < human_events),
        "mapping_complete": len(unmapped_actions) == 0 and len(mapped_to_unknown_affordance) == 0,
        "total_events": total_events,
        "ai_events": ai_events,
        "human_events": human_events,
    }

    return {
        "discovered_actions": discovered_actions,
        "unmapped_actions": unmapped_actions,
        "mapped_to_unknown_affordance": [{"action": a, "mapped_to": m} for a, m in mapped_to_unknown_affordance],
        "missing_fields": {
            "missing_interaction_id": missing_interaction_id,
            "missing_actor_type": missing_actor_type,
            "missing_action": missing_action,
            "missing_timestamp": missing_timestamp,
            "bad_timestamp_format": bad_timestamp,
            "missing_latency_ms_on_ai_events": missing_latency_ms,
            "missing_duration_s_on_human_events": missing_duration_s,
        },
        "coverage": coverage,
        "notes": [
            "Payload fields are opaque and not validated.",
            "Actions may map directly to affordance keys OR via action_map aliases."
        ]
    }