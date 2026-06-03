from __future__ import annotations
from dataclasses import dataclass, asdict
from typing import Dict, List
import json
from pathlib import Path

# Where custom affordances are persisted (local quick-win)
CUSTOM_STORE = Path(__file__).resolve().parent / ".pilot_affordances.json"


@dataclass
class Affordance:
    key: str
    label: str
    actor_types: List[str]  # ["human", "ai", "system"]
    timing: str             # "ai_latency_ms" | "human_duration_s" | "none"
    description: str = ""
    group: str = "Custom"   # AI | Human | System | Custom


def get_default_affordances() -> Dict[str, List[Affordance]]:
    return {
        "AI": [
            Affordance("evaluate", "Evaluate / Validate", ["ai"], "ai_latency_ms",
                       "Model evaluates input and returns decision.", "AI"),
            Affordance("classify", "Classify", ["ai"], "ai_latency_ms",
                       "Model predicts class/label.", "AI"),
            Affordance("forecast", "Forecast", ["ai"], "ai_latency_ms",
                       "Model forecasts future state.", "AI"),
            Affordance("propose", "Propose / Recommend", ["ai"], "ai_latency_ms",
                       "Model proposes assignment/solution.", "AI"),
            Affordance("explain", "Explain (XAI)", ["ai"], "ai_latency_ms",
                       "Model provides explanation/rationale.", "AI"),
        ],
        "Human": [
            Affordance("create", "Create / Submit", ["human"], "none",
                       "Human initiates a new case/interaction.", "Human"),
            Affordance("review", "Review", ["human"], "human_duration_s",
                       "Human reviews model output.", "Human"),
            Affordance("verify", "Verify", ["human"], "human_duration_s",
                       "Human verifies/cross-checks outcome.", "Human"),
            Affordance("accept", "Accept", ["human"], "human_duration_s",
                       "Human accepts recommendation/outcome.", "Human"),
            Affordance("reject", "Reject", ["human"], "human_duration_s",
                       "Human rejects recommendation/outcome.", "Human"),
            Affordance("override", "Override", ["human"], "human_duration_s",
                       "Human overrides AI/system decision.", "Human"),
            Affordance("annotate", "Annotate / Label", ["human"], "human_duration_s",
                       "Human labels or annotates data.", "Human"),
        ],
        "System": [
            Affordance("route", "Route / Dispatch", ["system"], "none",
                       "System routes case to next stage/actor.", "System"),
            Affordance("notify", "Notify", ["system"], "none",
                       "System sends notification.", "System"),
            Affordance("start", "Start", ["system"], "none",
                       "System starts process/task.", "System"),
            Affordance("end", "End", ["system"], "none",
                       "System ends process/task.", "System"),
            Affordance("store", "Store / Persist", ["system"], "none",
                       "System stores artifacts/logs.", "System"),
        ],
        "Custom": []
    }


def affordance_to_dict(a: Affordance) -> dict:
    return asdict(a)


def _load_custom() -> List[Affordance]:
    if not CUSTOM_STORE.exists():
        return []
    try:
        data = json.loads(CUSTOM_STORE.read_text(encoding="utf-8"))
        out = []
        for item in data if isinstance(data, list) else []:
            out.append(Affordance(
                key=str(item.get("key")),
                label=str(item.get("label", item.get("key"))),
                actor_types=list(item.get("actor_types") or []),
                timing=str(item.get("timing", "none")),
                description=str(item.get("description", "")),
                group=str(item.get("group", "Custom")),
            ))
        return out
    except Exception:
        return []


def add_custom_affordance(a: Affordance) -> None:
    """
    Persist custom affordance to local store. Deduplicate by key.
    """
    existing = _load_custom()
    by_key = {x.key: x for x in existing}
    by_key[a.key] = a
    CUSTOM_STORE.write_text(
        json.dumps([affordance_to_dict(x) for x in by_key.values()], indent=2, ensure_ascii=False),
        encoding="utf-8"
    )


def reset_custom_affordances() -> None:
    if CUSTOM_STORE.exists():
        CUSTOM_STORE.unlink()


def get_affordances_merged() -> Dict[str, List[Affordance]]:
    base = get_default_affordances()
    custom = _load_custom()
    for c in custom:
        base.setdefault(c.group or "Custom", [])
        base[c.group or "Custom"].append(c)
    return base