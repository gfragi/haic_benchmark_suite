"""
Adapter management endpoints — /api/v1/adapters/...

  GET  /adapters/{pilot_tag}  — fetch the saved config for one adapter
  POST /adapters/register     — register (or overwrite) an adapter config
  POST /adapters/test         — test a mapping against a single sample event
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# --------------------------------------------------------------------------- #
# Request / response models                                                   #
# --------------------------------------------------------------------------- #

class AdapterConfig(BaseModel):
    pilot_tag: str
    actor_type_field: str = "actor_type"
    human_value: str = "human"
    ai_value: str = "ai"
    latency_field: str = "latency_ms"
    latency_unit: str = "ms"       # "ms" | "s"
    duration_field: str = "duration_s"
    duration_unit: str = "s"       # "s"  | "ms"
    correct_field: str = "correct"
    correct_value: str = "true"
    incorrect_value: str = "false"
    ai_action_names: list[str] = ["ai_evaluated"]
    human_action_names: list[str] = ["application_created", "operator_verified"]
    package_format: str = "single_json"   # "single_json" | "zip" | "folder"


class TestMappingRequest(BaseModel):
    pilot_tag: str
    sample_event: dict[str, Any]


# --------------------------------------------------------------------------- #
# Routes                                                                       #
# --------------------------------------------------------------------------- #

@router.get("/{pilot_tag}")
def get_adapter_config(pilot_tag: str):
    """Return the saved JSON config for *pilot_tag*, or 404."""
    from metrics_core.adapters.config_adapter import get_config
    cfg = get_config(pilot_tag)
    if cfg is None:
        raise HTTPException(
            status_code=404,
            detail=f"No saved config for adapter '{pilot_tag.lower()}'",
        )
    return cfg


@router.post("/register", status_code=201)
def register_adapter(cfg: AdapterConfig):
    """
    Register (or overwrite) an adapter from the supplied field-mapping config.
    Persists the config to adapters/configs/{pilot_tag}.json and activates it
    immediately — no restart required.
    """
    try:
        from metrics_core.adapters.config_adapter import register_from_config
        register_from_config(cfg.model_dump())
        return {"pilot_tag": cfg.pilot_tag.lower(), "status": "registered"}
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@router.post("/test")
def test_mapping(req: TestMappingRequest):
    """
    Run the adapter for *pilot_tag* on a single sample event dict.
    Returns the mapped fields and, if valid, a DecisionEvent representation.
    Useful for verifying field-name configuration before uploading real logs.
    """
    from metrics_core.adapters import config_adapter as ca
    from metrics_core.adapters.registry import AdapterRegistry

    # Refresh in case a config was just registered in this request cycle.
    ca.load_all_configs()

    tag = req.pilot_tag.lower()
    fake_sessions = [{"session_id": "test", "decisions": [req.sample_event]}]
    adapted = AdapterRegistry.adapt(tag, fake_sessions)

    if not adapted or not adapted[0].get("decisions"):
        return {"mapped": {}, "decision_event": None, "warning": "Adapter returned no decisions."}

    mapped_event = adapted[0]["decisions"][0]

    # Attempt DecisionEvent validation for richer feedback.
    try:
        from metrics_core.schema import DecisionEvent
        de = DecisionEvent.model_validate(mapped_event)
        return {
            "mapped": mapped_event,
            "decision_event": de.model_dump(exclude_none=True),
            "warning": None,
        }
    except Exception as exc:
        return {
            "mapped": mapped_event,
            "decision_event": None,
            "warning": f"Mapped successfully but DecisionEvent validation note: {exc}",
        }
