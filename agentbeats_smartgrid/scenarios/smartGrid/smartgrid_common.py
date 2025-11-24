from dataclasses import dataclass
from typing import Any, Dict, List, Tuple

from haic_sim_mvp.engine.smartgrid_env import (
    SmartGridCoreEnv,
)

from . import some_metric_helpers  # ή από packages/metrics_core



@dataclass
class InteractionLogEntry:
    timestep: int
    state: Dict[str, Any]
    action: Dict[str, Any]
    next_state: Dict[str, Any]
    info: Dict[str, Any]

class SmartGridEnv:
    def __init__(self, difficulty: str, seed: int):
        self.core = SmartGridCoreEnv(difficulty=difficulty, seed=seed)

    def reset(self) -> Dict[str, Any]:
        state = self.core.reset()
        return state

    def step(
        self,
        state: Dict[str, Any],
        action: Dict[str, Any],
    ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        next_state, info = self.core.step(action)
        return next_state, info

    def serialize_state(self, state: Dict[str, Any]) -> Dict[str, Any]:
        # εδώ φροντίζεις το state να είναι "LLM-friendly" JSON
        return self.core.to_dict(state)

    def summarize_episode(
        self, interactions: List[InteractionLogEntry]
    ) -> Dict[str, Any]:
        return self.core.summarize(interactions)



def compute_task_metrics(
    episode_summary: Dict[str, Any],
    interactions: List[InteractionLogEntry],
) -> Dict[str, float]:
    # Παράδειγμα: πάρ’το ως έχει από τα δικά σου
    return {
        "incidents_avoided": episode_summary["incidents_avoided"],
        "total_penalty": episode_summary["total_penalty"],
        "stability_index": episode_summary["stability_index"],
        "normalized_task_score": episode_summary["normalized_task_score"],
    }

def compute_haic_metrics(
    episode_summary: Dict[str, Any],
    interactions: List[InteractionLogEntry],
) -> Dict[str, float]:
    # Εδώ τυλίγεις τα F, D, HCL, Trust, EL κ.λπ.
    # Αν ήδη τα υπολογίζεις σε άλλο module, απλά κάνε import εκείνες τις functions.
    F = ...   # interactions/min
    D = ...   # avg human duration
    HCL = ...
    Tr = ...
    EL = ...

    normalized_collab_score = some_metric_helpers.combine_haic(
        F=F, D=D, HCL=HCL, Tr=Tr, EL=EL
    )

    return {
        "F": F,
        "D": D,
        "HCL": HCL,
        "Tr": Tr,
        "EL": EL,
        "normalized_collab_score": normalized_collab_score,
    }