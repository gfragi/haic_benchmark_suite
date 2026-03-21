"""
Config-driven adapter — loads JSON configs from adapters/configs/ directory.

Each JSON file registers one pilot_tag adapter at import time and whenever
register_from_config() is called.  The adapter performs best-effort field
mapping using the config's field-name overrides, falling back to the
canonical names when a field is already present.

Config schema (all keys optional except pilot_tag):
{
  "pilot_tag":         string   — primary key; file name = {pilot_tag}.json
  "actor_type_field":  string   — field holding "human" / "ai" label  (default: actor_type)
  "human_value":       string   — value that means human              (default: human)
  "ai_value":          string   — value that means ai                  (default: ai)
  "latency_field":     string   — field for AI response latency        (default: latency_ms)
  "latency_unit":      "ms"|"s" — unit of latency_field               (default: ms)
  "duration_field":    string   — field for human decision time        (default: duration_s)
  "duration_unit":     "s"|"ms" — unit of duration_field              (default: s)
  "correct_field":     string   — field for correct/incorrect outcome  (default: correct)
  "correct_value":     string   — value meaning correct                (default: true)
  "incorrect_value":   string   — value meaning incorrect              (default: false)
  "ai_action_names":   [string] — event types owned by AI actor
  "human_action_names":[string] — event types owned by human actor
  "package_format":    "single_json"|"zip"|"folder"
}
"""
from __future__ import annotations

import json
import logging
import os
from pathlib import Path

from .registry import AdapterRegistry

logger = logging.getLogger(__name__)

# Allow the configs directory to be overridden at runtime (useful in Docker).
_ENV_DIR = os.getenv("ADAPTER_CONFIGS_DIR")
CONFIGS_DIR: Path = Path(_ENV_DIR) if _ENV_DIR else Path(__file__).parent / "configs"


# --------------------------------------------------------------------------- #
# Adapter factory                                                              #
# --------------------------------------------------------------------------- #

def _make_adapter(cfg: dict):
    """Return a session-list adapter function built from *cfg*."""
    actor_field    = cfg.get("actor_type_field", "actor_type")
    human_val      = cfg.get("human_value",  "human").lower()
    ai_val         = cfg.get("ai_value",     "ai").lower()
    latency_field  = cfg.get("latency_field",  "latency_ms")
    latency_unit   = cfg.get("latency_unit",   "ms")
    duration_field = cfg.get("duration_field", "duration_s")
    duration_unit  = cfg.get("duration_unit",  "s")
    correct_field  = cfg.get("correct_field",  "correct")
    correct_val    = str(cfg.get("correct_value",   "true")).lower()
    incorrect_val  = str(cfg.get("incorrect_value", "false")).lower()
    ai_actions     = {a.lower() for a in cfg.get("ai_action_names",    [])}
    human_actions  = {a.lower() for a in cfg.get("human_action_names", [])}

    def adapt(sessions: list[dict]) -> list[dict]:
        adapted = []
        for session in sessions:
            decisions = session.get("decisions") or []
            new_decisions = []

            for d in decisions:
                nd = dict(d)

                # ── actor_type ────────────────────────────────────────────
                if nd.get("actor_type") is None:
                    raw = nd.get(actor_field)
                    if raw is not None:
                        s = str(raw).lower()
                        if s == human_val:
                            nd["actor_type"] = "human"
                        elif s == ai_val:
                            nd["actor_type"] = "ai"
                        else:
                            nd["actor_type"] = s
                    elif ai_actions or human_actions:
                        action = str(nd.get("action") or nd.get("event_type") or "").lower()
                        if action in ai_actions:
                            nd["actor_type"] = "ai"
                        elif action in human_actions:
                            nd["actor_type"] = "human"

                # ── latency_ms ────────────────────────────────────────────
                if nd.get("latency_ms") is None:
                    raw = nd.get(latency_field)
                    if raw is not None:
                        try:
                            v = float(raw)
                            nd["latency_ms"] = v if latency_unit == "ms" else v * 1000.0
                        except (ValueError, TypeError):
                            pass

                # ── duration_s ────────────────────────────────────────────
                if nd.get("duration_s") is None:
                    raw = nd.get(duration_field)
                    if raw is not None:
                        try:
                            v = float(raw)
                            nd["duration_s"] = v if duration_unit == "s" else v / 1000.0
                        except (ValueError, TypeError):
                            pass

                # ── correct ───────────────────────────────────────────────
                if nd.get("correct") is None:
                    raw = nd.get(correct_field)
                    if raw is not None:
                        s = str(raw).strip().lower()
                        if s in {correct_val, "true", "yes", "1", "correct"}:
                            nd["correct"] = True
                        elif s in {incorrect_val, "false", "no", "0", "incorrect"}:
                            nd["correct"] = False

                new_decisions.append(nd)

            adapted.append({**session, "decisions": new_decisions})
        return adapted

    return adapt


# --------------------------------------------------------------------------- #
# Config file helpers                                                          #
# --------------------------------------------------------------------------- #

def load_all_configs() -> None:
    """Scan CONFIGS_DIR and register adapters for any unregistered pilot_tags."""
    if not CONFIGS_DIR.exists():
        return
    for path in sorted(CONFIGS_DIR.glob("*.json")):
        try:
            cfg = json.loads(path.read_text(encoding="utf-8"))
            tag = cfg.get("pilot_tag", path.stem).lower()
            # Always (re-)register so that updated configs take effect.
            AdapterRegistry._adapters[tag] = _make_adapter(cfg)
        except Exception as exc:
            logger.warning("config_adapter: skipping %s — %s", path.name, exc)


def register_from_config(cfg: dict) -> None:
    """
    Register (or overwrite) an adapter from a config dict, and persist it.

    Raises ValueError if pilot_tag is missing.
    """
    tag = cfg.get("pilot_tag", "").strip().lower()
    if not tag:
        raise ValueError("pilot_tag is required")

    CONFIGS_DIR.mkdir(parents=True, exist_ok=True)
    path = CONFIGS_DIR / f"{tag}.json"
    path.write_text(json.dumps(cfg, indent=2, ensure_ascii=False), encoding="utf-8")

    AdapterRegistry._adapters[tag] = _make_adapter(cfg)
    logger.info("config_adapter: registered adapter for pilot_tag=%r", tag)


def config_exists(pilot_tag: str) -> bool:
    """Return True if a saved config file exists for *pilot_tag*."""
    return (CONFIGS_DIR / f"{pilot_tag.lower()}.json").exists()


def get_config(pilot_tag: str) -> dict | None:
    """Load and return the saved config dict, or None if not found."""
    path = CONFIGS_DIR / f"{pilot_tag.lower()}.json"
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


# Load existing configs at import time.
load_all_configs()
