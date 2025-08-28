# haic_env_builder/adapters/ct_scan_adapter.py
from __future__ import annotations
from typing import Dict, Any, Sequence, Tuple, Optional, List
from dataclasses import dataclass
from .base import EnvAdapter, StepOutput

# Radiologist verbs
_RAD_ACTIONS: Tuple[str, ...] = (
    "open_study","select_series","scroll_slice","window_level",
    "mark_finding","add_measurement","compare_priors",
    "dictate_note","finalize_report","request_recon"
)

# Voice/ops assistant verbs
_VOICE_ACTIONS: Tuple[str, ...] = (
    "speak_prompt","confirm_patient","notify_radiologist",
    "read_checklist","record_finding","handoff_call"
)

def _space_for(name: str) -> Tuple[str, ...]:
    n = (name or "").lower()
    # Only classify as voice if it clearly says 'voice' or 'bot'
    if ("voice" in n) or ("bot" in n):
        return _VOICE_ACTIONS
    return _RAD_ACTIONS

@dataclass
class CTScanAdapter(EnvAdapter):
    name: str = "ct_scan"
    version: str = "1.1.1"

    def __init__(self, steps: int = 12, dt: float = 0.1, **_):
        self.steps = int(steps)
        self.dt = float(dt)
        self._t = 0.0
        self._k = 0

    def reset(self, *, seed: Optional[int] = None) -> Dict[str, Any]:
        self._t = 0.0
        self._k = 0
        return {"env": self.name, "version": self.version, "dt": self.dt, "seed": seed}

    def action_space(self, agent_name: str) -> Sequence[str]:
        return _space_for(agent_name)

    def step(self, action_map: Dict[str, str]) -> Tuple[StepOutput, bool]:
        decisions: List[Dict[str, Any]] = []
        events: List[Dict[str, Any]] = []

        # Clamp to each agent's allowed verbs; ensure duration_s is non-null
        for name, act in action_map.items():
            space = set(self.action_space(name))
            action = act if act in space else (next(iter(space)) if space else None)
            decisions.append({
                "t": self._t,
                "agent": name,
                "action": action,
                "duration_s": 0.0,
            })

        # Illustrative progress event every 5 ticks
        if self._k % 5 == 0:
            events.append({
                "t": self._t,
                "event_type": "checklist_progress",
                "k": self._k,
            })

        info = {"tick": self._k, "dt": self.dt, "env": self.name}

        # advance time
        self._t += self.dt
        self._k += 1
        done = (self._k >= self.steps)

        return StepOutput(decisions=decisions, events=events, info=info), done

    def close(self) -> None:
        pass
