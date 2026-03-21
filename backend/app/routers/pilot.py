"""
Pilot onboarding endpoint — /api/v1/pilot/...

  POST /pilot/onboard — full onboarding payload; registers adapter + persists pilot env config
"""
from __future__ import annotations

from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel

router = APIRouter()


# --------------------------------------------------------------------------- #
# Request models                                                               #
# --------------------------------------------------------------------------- #

class ActionDef(BaseModel):
    action_name: str
    label: str = ""


class CorrectnessRule(BaseModel):
    strategy: str = "add_field"   # "add_field" | "existing_field" | "derived"
    field_name: str = "correct"
    correct_value: str = "true"
    incorrect_value: str = "false"
    derive_condition: str = ""
    description: str = ""


class PilotOnboardRequest(BaseModel):
    pilot_tag: str
    pilot_domain: str = ""
    task_description: str = ""
    human_roles: list[str] = []
    human_actions: list[ActionDef] = []
    ai_actions: list[ActionDef] = []
    baseline_duration_s: float | None = None
    max_reaction_time_s: float | None = None
    correctness_rule: CorrectnessRule = CorrectnessRule()
    adapter_config: dict[str, Any] = {}


# --------------------------------------------------------------------------- #
# Endpoint                                                                     #
# --------------------------------------------------------------------------- #

@router.post("/onboard", status_code=201)
def onboard_pilot(req: PilotOnboardRequest):
    """
    Register a new pilot environment:
      1. Derive the adapter config from the onboarding form answers.
      2. Register the adapter immediately (no restart required).
      3. Persist the full pilot env config alongside the adapter config.

    Returns the activated adapter config + pilot_tag.
    """
    try:
        from metrics_core.adapters.config_adapter import register_from_config

        tag = req.pilot_tag.strip().lower()
        if not tag:
            raise HTTPException(status_code=422, detail="pilot_tag is required")

        # Build the adapter config
        cfg: dict[str, Any] = {
            "pilot_tag": tag,
            "ai_action_names":    [a.action_name for a in req.ai_actions],
            "human_action_names": [a.action_name for a in req.human_actions],
        }

        rule = req.correctness_rule
        if rule.strategy == "existing_field":
            cfg["correct_field"]   = rule.field_name
            cfg["correct_value"]   = rule.correct_value
            cfg["incorrect_value"] = rule.incorrect_value

        if req.baseline_duration_s is not None:
            cfg["baseline_s"] = req.baseline_duration_s

        if req.max_reaction_time_s is not None:
            cfg["max_reaction_time_s"] = req.max_reaction_time_s

        # Merge any explicit overrides supplied by the client
        cfg.update(req.adapter_config)
        cfg["pilot_tag"] = tag  # prevent overwrite

        register_from_config(cfg)
        _persist_pilot_env(tag, req)

        return {
            "pilot_tag":      tag,
            "status":         "activated",
            "adapter_config": cfg,
        }

    except HTTPException:
        raise
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


# --------------------------------------------------------------------------- #
# Helpers                                                                      #
# --------------------------------------------------------------------------- #

def _persist_pilot_env(tag: str, req: PilotOnboardRequest) -> None:
    """Persist the full pilot env config as {tag}.env.json next to adapter configs."""
    import json
    from metrics_core.adapters.config_adapter import CONFIGS_DIR

    env_data = req.model_dump()
    env_data["pilot_tag"] = tag

    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    path = CONFIGS_DIR / f"{tag}.env.json"
    path.write_text(json.dumps(env_data, indent=2, ensure_ascii=False), encoding="utf-8")
