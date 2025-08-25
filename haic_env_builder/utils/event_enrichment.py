import random
from typing import Any, Dict, List

def enrich_decisions(
    decisions: List[Dict[str, Any]],
    agents: List[Dict[str, Any]],
    profiles: List[Dict[str, Any]],
    *,
    scenario: str = "generic",
) -> List[Dict[str, Any]]:
    """
    Adds fields needed by metrics: actor_type, latency_ms, ai_suggested, human_accepted,
    successful_outcome, unsafe_event, manual_intervention, profile (dict).
    """
    # map agent name -> type
    agent_type = {}
    for a in agents:
        # If you later want stricter mapping: set modality or a.flag "is_ai"
        agent_type[a["name"]] = "ai" if a.get("modality") in ("text", "audio") and "classify" in a.get("capabilities", []) else "human"

    # simple round-robin profile assignment
    prof_list = profiles if profiles else [{"id": "user0", "skill_level": "unknown", "role": "user"}]
    enriched = []
    for i, d in enumerate(decisions):
        agent_name = d.get("agent")
        p = prof_list[i % len(prof_list)]
        is_ai = agent_type.get(agent_name, "human") == "ai"

        ai_suggested = is_ai and random.random() < 0.8
        human_accepted = ai_suggested and random.random() < 0.7
        successful = random.random() < (0.85 if human_accepted else 0.6)
        unsafe = random.random() < 0.03
        manual = (not is_ai) and random.random() < 0.25
        latency = random.randint(200, 2500) if not is_ai else random.randint(50, 500)

        enriched.append({
            **d,
            "actor_type": "ai" if is_ai else "human",
            "latency_ms": latency,
            "ai_suggested": ai_suggested,
            "human_accepted": human_accepted if not is_ai else False,
            "successful_outcome": successful,
            "unsafe_event": unsafe,
            "manual_intervention": manual,
            "profile": p,  # dict with id/skill_level/role
        })
    return enriched
