# haic_env_builder/adapters/ct_scan_adapter.py
from __future__ import annotations
from typing import Dict, Any, List, Tuple, Optional

# minimal base contract: your BaseAdapter just needs reset/step/action_space/close
try:
    from .base import BaseAdapter
except Exception:
    class BaseAdapter:  # fall back for local runs
        def reset(self, seed: Optional[int] = None): ...
        def step(self, action_map: Dict[str, str]): ...
        def action_space(self, agent_name: str) -> List[str]: ...
        def close(self): ...

# Domain action sets (kept local to avoid cross-coupling)
CT_RADS_ACTIONS = [
    "open_study","select_series","scroll_slice","window_level",
    "mark_finding","add_measurement","compare_priors",
    "dictate_note","finalize_report","request_recon"
]
CT_VOICEBOT_ACTIONS = [
    "speak_prompt","confirm_patient","notify_radiologist",
    "read_checklist","record_finding","handoff_call"
]

def _one_hot(actions: List[str], idx: int) -> Dict[str, float]:
    probs = {a: 0.0 for a in actions}
    if 0 <= idx < len(actions):
        probs[actions[idx]] = 1.0
    return probs

def _bump_on(actions: List[str], anchor: Optional[str], p_anchor: float = 0.7) -> Dict[str, float]:
    """Simple soft distribution: put p_anchor on 'anchor' (if valid), spread the rest uniformly."""
    if not actions:
        return {}
    n = len(actions)
    if anchor in actions and n > 1:
        rest = (1.0 - p_anchor) / (n - 1)
        return {a: (p_anchor if a == anchor else rest) for a in actions}
    # uniform fallback
    u = 1.0 / n
    return {a: u for a in actions}

class CTScanAdapter(BaseAdapter):
    """
    Stateless toy CT task with a checklist-like ground truth, emitting:
      - decisions[...] with: correct, probs (1-hot ground truth), surrogate_probs (soft bump on proposed)
      - events[...] checklist progress markers
    """

    def __init__(self, **env_params: Any):
        self.params = dict(env_params or {})
        # Simple radiologist checklist (customizable via env_params["checklist"])
        self.checklist: List[str] = list(self.params.get("checklist") or [
            "open_study",
            "select_series",
            # allow many scroll_slice; correctness considers phase (see _is_correct)
            "mark_finding",
            "dictate_note",
            "finalize_report",
        ])
        self.allow_multi_scroll = bool(self.params.get("allow_multi_scroll", True))
        self.max_steps = int(self.params.get("steps", 15))
        self.ticks = 0
        self.phase = 0  # index in checklist
        self.done = False

    # --- adapter api ---
    def reset(self, seed: Optional[int] = None):
        self.ticks = 0
        self.phase = 0
        self.done = False
        return {}

    def close(self):
        pass

    def action_space(self, agent_name: str) -> List[str]:
        nm = (agent_name or "").lower()
        if "voice" in nm or "bot" in nm:
            return list(CT_VOICEBOT_ACTIONS)
        return list(CT_RADS_ACTIONS)

    # --- correctness policy ---
    def _expected(self) -> str:
        if 0 <= self.phase < len(self.checklist):
            return self.checklist[self.phase]
        return "finalize_report"

    def _is_correct(self, agent: str, action: str) -> bool:
        nm = (agent or "").lower()
        if "voice" in nm or "bot" in nm:
            # keep voice-bot neutral/assisting in this toy setup
            return True
        exp = self._expected()
        if action == exp:
            return True
        # allow "scroll_slice" freely between select_series and mark_finding if enabled
        if self.allow_multi_scroll and action == "scroll_slice":
            # ok between phases 1..(index of "mark_finding")
            try:
                mark_idx = self.checklist.index("mark_finding")
            except ValueError:
                mark_idx = 2
            return 1 <= self.phase < mark_idx
        return False

    def _advance_if_needed(self, action: str):
        """Advance checklist when the expected step is performed."""
        if self.done:
            return None
        exp = self._expected()
        if action == exp:
            prev = self.phase
            self.phase += 1
            if self.phase >= len(self.checklist):
                self.done = True
            return {"event_type": "checklist_progress", "from": prev, "to": self.phase}
        return None

    def step(self, action_map: Dict[str, str]) -> Tuple[Dict[str, Any], bool]:
        if self.done:
            return {"decisions": [], "events": [], "info": {}}, True

        self.ticks += 1
        decisions: List[Dict[str, Any]] = []
        events: List[Dict[str, Any]] = []

        # Radiologist ground-truth distribution = one-hot at expected
        # Voice-bot is neutral (we won’t compute probs for it)
        expected = self._expected()

        for agent, action in (action_map or {}).items():
            space = self.action_space(agent)
            # correctness
            correct = self._is_correct(agent, action)

            # probs: one-hot at expected (only for radiologist-like agents)
            probs = _one_hot(space, space.index(expected)) if expected in space else {}

            # surrogate_probs: soft bump on the *proposed* action (runner will attach proposed_action;
            # we can still emit a soft prior here around the final action as a reasonable surrogate)
            surrogate_probs = _bump_on(space, action, p_anchor=0.7)

            # decision row (runner will add t/proposed_action/etc.)
            decisions.append({
                "agent": agent,
                "action": action,
                "correct": bool(correct),
                "probs": probs,                     # P_human (ground-truth intent)
                "surrogate_probs": surrogate_probs, # P_surrogate (policy-ish)
            })

            # progress event if checklist advanced
            ev = self._advance_if_needed(action)
            if ev:
                events.append({"event_type": "checklist_progress", **ev})

        # horizon
        if self.ticks >= self.max_steps or self.done:
            self.done = True

        return {"decisions": decisions, "events": events, "info": {}}, self.done
