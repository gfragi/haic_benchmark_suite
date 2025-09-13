from __future__ import annotations

from datetime import datetime, timedelta, timezone
import random
import uuid


# -------------------------------
# helpers
# -------------------------------
def _uid(prefix: str) -> str:
    return f"{prefix}-{uuid.uuid4().hex[:8]}"

def _iso_utc(dt: datetime) -> str:
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=timezone.utc)
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")

def random_dt(start: datetime, end: datetime) -> datetime:
    """Uniform random datetime in [start, end]."""
    start_ts = start.timestamp()
    end_ts = end.timestamp()
    return datetime.fromtimestamp(random.uniform(start_ts, end_ts), tz=timezone.utc)

def _bounded_norm(mu: float, sigma: float, lo: float, hi: float) -> float:
    x = random.normalvariate(mu, sigma)
    return float(max(lo, min(hi, x)))

def _rand_choice_prob(p_true=0.5) -> bool:
    return random.random() < p_true

def _maybe(n):
    """Return n or None with small probability for realism."""
    return n if random.random() > 0.05 else None


# -------------------------------
# schema builders (match adapter)
# -------------------------------
def build_core_like_session(
    *,
    session_prefix: str,
    user_id: str,
    app_version: str,
    ai_model_version: str,
    start: datetime,
    end: datetime,
    rt_max: float = 5.0,
    baseline_s: float = 0.0,
) -> dict:
    """Generic session compatible with your compute_from_log adapter."""
    # times
    st = random_dt(start, end - timedelta(minutes=2))
    et = random_dt(st + timedelta(seconds=30), end)

    # “system” validation summary (optional but useful)
    acc = _maybe(_bounded_norm(0.84, 0.06, 0.0, 1.0))
    prec = _maybe(_bounded_norm(0.82, 0.08, 0.0, 1.0))
    rec = _maybe(_bounded_norm(0.80, 0.08, 0.0, 1.0))

    # review outcomes
    fp = int(max(0, random.gauss(2, 1)))
    fn = int(max(0, random.gauss(1, 1)))
    det = int(max(1, random.gauss(10, 3)))
    human_confirm = _bounded_norm(0.8, 0.1, 0.0, 1.0)
    corr_time = max(5, int(random.gauss(40, 20)))

    # decisions timeline (very light; adapter only needs a few fields)
    decisions = []
    t_cursor = 0.0
    for k in range(random.randint(2, 5)):
        dur = max(0.2, random.gauss(2.0, 1.0))
        decisions.append({
            "t": round(t_cursor, 2),
            "agent": user_id,
            "actor_type": "human",
            "action": random.choice(["inspect", "adjust", "confirm", "assist"]),
            "duration_s": round(dur, 2),
            "correct": _rand_choice_prob(0.85),
        })
        t_cursor += dur + random.uniform(0.2, 2.0)

    # performance log (for “Human Effort Saved” surrogate etc.)
    human_effort = {user_id: int(random.gauss(45, 15))}

    return {
        "session_id": _uid(session_prefix),
        "user_id": user_id,
        "ai_model_version": ai_model_version,
        "app_version": app_version,
        "start_time": _iso_utc(st),
        "end_time": _iso_utc(et),

        "interaction_data": {
            "validation_data": {
                "system_metrics": {
                    "accuracy": acc,
                    "precision": prec,
                    "recall": rec,
                },
                "processing_time_seconds": round(max(0.2, random.gauss(4.5, 1.0)), 2),
                "confidence_level": _maybe(_bounded_norm(0.75, 0.1, 0.0, 1.0)),
            },
            "review_data": {
                "false_positives": fp,
                "false_negatives": fn,
                "detections_confirmed": det,
                "human_confirmation_rate": human_confirm,
                "time_spent_on_corrections_seconds": corr_time,
            },
            "alert_data": None,
        },

        "performance_logs": {
            "human_effort_seconds": human_effort
        },

        "decisions": decisions,

        # meta carries rt_max & baseline_s for minimal metrics
        "meta": {
            "schema_version": "1.0",
            "task_name": session_prefix,
            "task_parameters": {"environment": session_prefix, "rt_max": rt_max, "baseline_s": baseline_s},
        },
    }


def build_hmi_xr_session(
    *,
    user_id: str,
    app_version: str,
    ai_model_version: str,
    start: datetime,
    end: datetime,
    rt_max: float = 5.0,
    baseline_s: float = 0.0,
) -> dict:
    """HMI/XR flavored session (names match your partner’s domain)."""
    base = build_core_like_session(
        session_prefix="hmi_xr_evaluation",
        user_id=user_id,
        app_version=app_version,
        ai_model_version=ai_model_version,
        start=start,
        end=end,
        rt_max=rt_max,
        baseline_s=baseline_s,
    )
    # small XR twist: make “assist” actions include an AI latency
    for d in base["decisions"]:
        if d["action"] == "assist":
            d["latency_ms"] = int(max(120, random.gauss(600, 150)))
    return base


# -------------------------------
# public factory
# -------------------------------
def generate_log(
    app_type: str,
    start_datetime: str,
    end_datetime: str,
    ai_model_version_range: str,
    *,
    rt_max: float = 5.0,
    baseline_s: float = 0.0,
    app_version: str = "1.0.0",
) -> dict:
    """
    Create ONE session log in the adapter-ready schema.

    app_type ∈ {"radiologist", "hmi_xr"} for now.
    ai_model_version_range: e.g. "1.0.0-3.2.0"
    """
    # parse times
    start = datetime.fromisoformat(start_datetime.replace("Z", "+00:00"))
    end   = datetime.fromisoformat(end_datetime.replace("Z", "+00:00"))

    # pick an AI model version within range
    def _parse(v): return [int(p) for p in v.strip().split(".")]
    vstart, vend = [_parse(x) for x in ai_model_version_range.split("-")]
    maj = random.randint(vstart[0], vend[0])
    minr = random.randint(vstart[1], vend[1])
    pat = random.randint(vstart[2], vend[2])
    ai_version = f"{maj}.{minr}.{pat}"

    user_id = _uid("user")

    if app_type.lower() in {"radiologist", "radiology"}:
        # Radiology also uses the generic core builder; you can add domain quirks later
        return build_core_like_session(
            session_prefix="radiology_assist",
            user_id=user_id,
            app_version=app_version,
            ai_model_version=ai_version,
            start=start,
            end=end,
            rt_max=rt_max,
            baseline_s=baseline_s,
        )

    if app_type.lower() in {"hmi_xr", "xr", "hmi"}:
        return build_hmi_xr_session(
            user_id=user_id,
            app_version=app_version,
            ai_model_version=ai_version,
            start=start,
            end=end,
            rt_max=rt_max,
            baseline_s=baseline_s,
        )

    # fallback: generic
    return build_core_like_session(
        session_prefix=app_type,
        user_id=user_id,
        app_version=app_version,
        ai_model_version=ai_version,
        start=start,
        end=end,
        rt_max=rt_max,
        baseline_s=baseline_s,
    )
