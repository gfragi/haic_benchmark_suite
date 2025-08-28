from __future__ import annotations
import re
from typing import Any, Dict, List, Optional
import random as _random

def enrich_decisions(
    decisions: List[Dict[str, Any]],
    agents: List[Dict[str, Any]],
    profiles: List[Dict[str, Any]],
    *,
    scenario: str = "generic",
    rng: Optional[_random.Random] = None,
    p_ai_suggested: float = 0.8,
    p_human_accept_given_ai: float = 0.7,
    p_success_if_accept: float = 0.85,
    p_success_if_no_accept: float = 0.6,
    p_unsafe: float = 0.03,
    p_manual_human: float = 0.25,
    ai_latency_ms: tuple[int, int] = (50, 500),
    human_latency_ms: tuple[int, int] = (200, 2500),
    force_actor_type: Optional[Dict[str, str]] = None,  # {"agent_name": "ai"|"human"}
) -> List[Dict[str, Any]]:
    R = rng or _random.Random(0)

    # ---- Build name -> actor_type map ----
    agent_type: Dict[str, str] = {}
    bot_re = re.compile(r"(bot|assistant|agent)", re.I)
    for a in (agents or []):
        nm = a.get("name") or ""
        if force_actor_type and nm in force_actor_type:
            t = "ai" if force_actor_type[nm] == "ai" else "human"
        else:
            if bot_re.search(nm):
                t = "ai"
            elif a.get("modality") == "human":
                t = "human"
            else:
                t = a.get("actor_type") or "ai"
        agent_type[nm] = t

    # ---- Build name -> declared action space (optional) ----
    agent_space: Dict[str, set] = {}
    for a in (agents or []):
        nm = a.get("name") or ""
        space = None
        if isinstance(a.get("action_space"), (list, tuple)) and a["action_space"]:
            space = a["action_space"]
        elif isinstance(a.get("runtime_params"), dict):
            rs = a["runtime_params"]
            if isinstance(rs.get("action_space"), (list, tuple)) and rs["action_space"]:
                space = rs["action_space"]
        if space:
            try:
                agent_space[nm] = set(map(str, space))
            except Exception:
                agent_space[nm] = set()

    # ---- Normalize profiles (unique-ish ids) ----
    prof_list = profiles or [{"profile_id": "user0", "skill_level": "unknown", "role": "user"}]
    norm_profiles: List[Dict[str, Any]] = []
    for idx, p in enumerate(prof_list):
        pid = p.get("profile_id") or p.get("id") or p.get("role") or f"profile_{idx}"
        norm_profiles.append({
            "profile_id": pid,
            "skill_level": p.get("skill_level"),
            "role": p.get("role"),
            **({"metadata": p.get("metadata")} if p.get("metadata") is not None else {})
        })

    enriched: List[Dict[str, Any]] = []

    for i, d in enumerate(decisions or []):
        agent_name = d.get("agent") or ""
        # Default to AI when unknown (keeps prior behavior)
        is_ai = ((d.get("actor_type") or agent_type.get(agent_name, "ai")) == "ai")

        # --- latency_ms: keep if present, else synthesize ---
        if d.get("latency_ms") is not None:
            try:
                latency_ms_val = float(d.get("latency_ms"))
            except Exception:
                latency_ms_val = 0.0
        else:
            latency_ms_val = float(R.randint(*(ai_latency_ms if is_ai else human_latency_ms)))

        # --- duration_s: always define; derive small non-zero if missing/zero ---
        try:
            raw_dur = d.get("duration_s", 0.0)
            duration_s_val = float(0.0 if raw_dur is None else raw_dur)
        except Exception:
            duration_s_val = 0.0

        if duration_s_val <= 1e-9:
            # Toy heuristic: ~20% of reaction time, min 20ms action
            try:
                duration_s_val = max(0.02, 0.2 * float(latency_ms_val) / 1000.0)
            except Exception:
                duration_s_val = 0.05

        # --- behavior flags (respect existing if already present) ---
        ai_suggested = bool(d.get("ai_suggested")) if "ai_suggested" in d else (is_ai and (R.random() < p_ai_suggested))
        human_accepted = bool(d.get("human_accepted")) if "human_accepted" in d else ((not is_ai) and ai_suggested and (R.random() < p_human_accept_given_ai))
        success_base = p_success_if_accept if human_accepted else p_success_if_no_accept
        successful = bool(d.get("successful_outcome")) if "successful_outcome" in d else (R.random() < success_base)
        unsafe = bool(d.get("unsafe_event")) if "unsafe_event" in d else (R.random() < p_unsafe)
        manual = bool(d.get("manual_intervention")) if "manual_intervention" in d else ((not is_ai) and (R.random() < p_manual_human))

        # --- off-role: compare proposed_action (or action) against declared space, if any ---
        space = agent_space.get(agent_name, set())
        proposed = d.get("proposed_action") or d.get("action")
        off_role = bool(space) and (proposed not in space)

        # --- profile assignment (round-robin) ---
        prof = norm_profiles[i % len(norm_profiles)]

        row = {
            "actor_type": "ai" if is_ai else "human",
            "latency_ms": latency_ms_val,
            "duration_s": duration_s_val,
            "ai_suggested": ai_suggested,
            "human_accepted": human_accepted,
            "successful_outcome": successful,
            "unsafe_event": unsafe,
            "manual_intervention": manual,
            "off_role_action": bool(d.get("off_role_action", off_role)),
            "correct": bool(d.get("correct", successful)),  # default correctness aligns with success
            "profile": prof,
        }
        merged = {**d, **row}
        enriched.append(merged)

    return enriched
