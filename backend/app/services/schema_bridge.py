from __future__ import annotations
import re
from typing import Any
from metrics_core.schema import SessionLog, DecisionEvent

def _clean_ts(v: Any) -> Any:
    """Strip sub-microsecond precision before Pydantic parses datetime."""
    if isinstance(v, str):
        v = re.sub(r'(\.\d{6})\d+', r'\1', v)
        v = v.replace("Z", "+00:00")
    return v

def log_schema_to_session_log(raw: dict) -> tuple[SessionLog, list[str]]:
    """
    Maps a LogSchema-shaped dict to a validated SessionLog.
    Returns (session_log, warnings) where warnings is a list of
    human-readable strings for fields that failed validation.

    Does NOT raise on partial failure — collects warnings and
    continues with valid fields. This allows a log with some
    malformed decisions to still compute metrics on the good ones.
    """
    warnings: list[str] = []

    # Map LogSchema field names → SessionLog field names
    mapped = {
        "session_id":        raw.get("session_id"),
        "pilot_tag":         raw.get("pilot_tag") or raw.get("app_version"),
        "app_version":       raw.get("app_version"),
        "ai_model_version":  raw.get("ai_model_version"),
        "meta":              raw.get("meta", {}),
        "extras":            raw.get("extras", {}),
    }

    # Timestamps: LogSchema uses start_time/end_time (str),
    # SessionLog uses session_started_at/session_ended_at (datetime)
    for src, dst in [("start_time", "session_started_at"),
                     ("end_time",   "session_ended_at")]:
        raw_ts = raw.get(src)
        if raw_ts is not None:
            mapped[dst] = _clean_ts(raw_ts)
        else:
            mapped[dst] = None

    # Decisions: validate each individually, collect warnings for bad ones
    raw_decisions = raw.get("decisions") or []
    valid_decisions = []
    for i, d in enumerate(raw_decisions):
        if not isinstance(d, dict):
            warnings.append(f"decisions[{i}]: not a dict, skipped")
            continue
        # Shallow-copy and clean timestamp; always preserve boolean fields
        nd = {**d}
        if "timestamp" in nd:
            nd["timestamp"] = _clean_ts(nd["timestamp"])
        # Explicit bool coercion: Pydantic may drop False as falsy default
        if "correct" in nd:
            nd["correct"] = bool(nd["correct"]) if nd["correct"] is not None else None
        try:
            valid_decisions.append(DecisionEvent.model_validate(nd))
        except Exception as e:
            warnings.append(
                f"decisions[{i}] (id={d.get('interaction_id','?')}): "
                f"validation failed — {e}"
            )
    mapped["decisions"] = valid_decisions

    # Validate the session envelope itself
    try:
        session_log = SessionLog.model_validate(mapped)
    except Exception as e:
        warnings.append(f"session envelope validation: {e}")
        # Return minimal valid object so caller can still proceed
        session_log = SessionLog(
            session_id=str(raw.get("session_id", "unknown")),
            decisions=valid_decisions,
        )

    return session_log, warnings


def normalize_log_payload(payload: Any) -> tuple[list[SessionLog], list[str]]:
    """
    Accepts anything _normalize_logs_data() accepted:
      - a single session dict
      - a list of session dicts
      - a dict with a 'logs'/'sessions'/'entries' key
    Returns (list[SessionLog], all_warnings).
    Replaces evaluate._normalize_logs_data() entirely.
    """
    all_warnings: list[str] = []

    # Unwrap envelope
    if isinstance(payload, dict):
        for key in ("logs", "sessions", "entries"):
            if isinstance(payload.get(key), list):
                payload = payload[key]
                break

    if isinstance(payload, dict):
        payload = [payload]

    if not isinstance(payload, list):
        raise ValueError(
            "Log must be a JSON object or array of session objects."
        )

    raw_sessions = [x for x in payload if isinstance(x, dict)]

    # Unwrap any {"logs": [...]} envelope entries that appear inside the list.
    # Some partners send mixed arrays where some entries are bare sessions and
    # others are {"logs": [session, ...]} wrappers.
    unwrapped = []
    for entry in raw_sessions:
        if (
            "decisions" not in entry
            and isinstance(entry.get("logs"), list)
        ):
            unwrapped.extend(x for x in entry["logs"] if isinstance(x, dict))
        else:
            unwrapped.append(entry)
    raw_sessions = unwrapped

    if not raw_sessions:
        raise ValueError("Log contains no valid session objects.")

    from metrics_core.adapters.registry import AdapterRegistry
    # Detect pilot_tag from first session
    pilot_tag = raw_sessions[0].get("pilot_tag", "generic") if raw_sessions else "generic"
    # Run pilot-specific adapter
    raw_sessions = AdapterRegistry.adapt(pilot_tag, raw_sessions)

    sessions: list[SessionLog] = []
    for i, raw in enumerate(raw_sessions):
        session_log, warns = log_schema_to_session_log(raw)
        for w in warns:
            all_warnings.append(f"session[{i}] {raw.get('session_id','?')}: {w}")
        sessions.append(session_log)

    return sessions, all_warnings
