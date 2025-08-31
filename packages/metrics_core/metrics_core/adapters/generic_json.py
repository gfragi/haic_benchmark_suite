
def to_decisions(events):
    out = []
    for e in events:
        out.append({
          "t": e.get("timestamp"),
          "agent": e.get("agent_id") or e.get("user_id"),
          "actor_type": e.get("role"),
          "action": e.get("action"),
          "duration_s": e.get("duration_s"),
          "latency_ms": e.get("response_time_ms"),
          "correct": e.get("is_correct"),
          "probs": e.get("probs") or {},
          "surrogate_probs": e.get("surrogate_probs"),
          "surrogate_action": e.get("surrogate_action"),
          "event_type": e.get("event_type"),
          "off_role_action": e.get("off_role_action"),
        })
    return out
