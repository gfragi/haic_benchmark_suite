# app/services/core_metrics.py
from __future__ import annotations
from asyncio import events
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import io, json

from metrics_core.interaction_metrics import (
    compute_metrics,
    compute_metrics_with_results,
    compute_metrics_by_agent,
)
from metrics_core.schema import MetricResult
from metrics_core.adapters.registry import AdapterRegistry

# IMPORTANT: import the module, not names (avoids ImportError)
try:
    import app.utils.minio_utils as minio_utils  # type: ignore
except Exception:
    minio_utils = None  # running without MinIO utils

# ---------- storage helpers (MinIO if available, else local) ----------

def _minio_read_json(key: str) -> dict | list:
    """
    Try a few common helper names from your minio_utils.
    Falls back to raw client usage if present.
    """
    if minio_utils is None:
        raise RuntimeError("minio_utils not available")

    # 1) Direct helpers your project might already have
    for fn_name in (
        "read_json_from_minio", "get_json", "download_json",
        "minio_read_json", "minio_get_json"
    ):
        fn = getattr(minio_utils, fn_name, None)
        if callable(fn):
            return fn(key)

    # 2) Raw client fallback (adjust bucket name getter to your codebase)
    get_client = getattr(minio_utils, "get_minio_client", None)
    get_bucket = getattr(minio_utils, "get_minio_bucket", None)
    bucket_name = getattr(minio_utils, "MINIO_BUCKET", None)
    if callable(get_client) and (callable(get_bucket) or bucket_name):
        client = get_client()
        bucket = bucket_name or get_bucket()
        obj = client.get_object(bucket, key)
        try:
            data = obj.read()
            return json.loads(data)
        finally:
            obj.close()
    raise RuntimeError("No suitable MinIO read helper found in minio_utils")

def _minio_write_json(key: str, payload: dict | list) -> None:
    if minio_utils is None:
        raise RuntimeError("minio_utils not available")

    for fn_name in (
        "write_json_to_minio", "put_json", "upload_json",
        "minio_write_json", "minio_put_json"
    ):
        fn = getattr(minio_utils, fn_name, None)
        if callable(fn):
            fn(key, payload)
            return

    get_client = getattr(minio_utils, "get_minio_client", None)
    get_bucket = getattr(minio_utils, "get_minio_bucket", None)
    bucket_name = getattr(minio_utils, "MINIO_BUCKET", None)
    if callable(get_client) and (callable(get_bucket) or bucket_name):
        client = get_client()
        bucket = bucket_name or get_bucket()
        data = json.dumps(payload).encode("utf-8")
        stream = io.BytesIO(data)
        client.put_object(bucket, key, stream, length=len(data), content_type="application/json")
        return
    raise RuntimeError("No suitable MinIO write helper found in minio_utils")

def _local_read_json(path: Path) -> dict | list:
    with path.open("r") as f:
        return json.load(f)

def _local_write_json(path: Path, payload: dict | list) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2))

# Choose where to read events from and where to write results if MinIO is absent
LOGS_DIR = Path("logs")              # e.g., logs/<run_id>/events.json
RESULTS_DIR = Path("metrics")        # fallback: metrics/<run_id>/core_v1.json

# ---------- domain helpers ----------

def _load_events_for_run(run_id: str) -> list[dict]:
    """
    Load raw events for a run. Prefer MinIO if utils exist; otherwise read local file.
    Adjust keys/paths to your project’s conventions.
    """
    key = f"logs/{run_id}/events.json"
    if minio_utils is not None:
        try:
            return _minio_read_json(key)  # type: ignore[return-value]
        except Exception:
            pass  # fall back to local file

    local = LOGS_DIR / run_id / "events.json"
    if local.exists():
        return _local_read_json(local)  # type: ignore[return-value]
    raise FileNotFoundError(f"Could not find events for run_id={run_id} (tried MinIO key '{key}' and '{local}')")

def _write_core_artifact(run_id: str, artifact: dict) -> str:
    """
    Save artifact. Prefer MinIO; else local. Returns a string path/key for UI.
    """
    key = f"results/{run_id}/metrics/core_v1.json"
    if minio_utils is not None:
        try:
            _minio_write_json(key, artifact)
            return key  # MinIO key
        except Exception:
            pass
    local = RESULTS_DIR / run_id / "core_v1.json"
    _local_write_json(local, artifact)
    return str(local)

# Optional: if your backend logs aren't already in the generic schema,
# replace this with a tiny custom adapter mapping -> decisions.
def _to_decisions(events: list[dict], pilot_tag: str = "generic") -> list[dict]:
    return AdapterRegistry.adapt(pilot_tag, events)


def extract_session_durations(sessions: list[dict]) -> list[float]:
    """
    Extract total duration per session from a list of session dicts.
    Used to infer baseline_s via P95 when not explicitly configured.
    """
    import re
    from datetime import datetime

    def _clean(ts: Any) -> str:
        return re.sub(r"(\.\d{6})\d+", r"\1", str(ts).replace("Z", "+00:00"))

    durations = []
    for s in sessions:
        start = s.get("session_started_at")
        end = s.get("session_ended_at")
        if start and end:
            try:
                t0 = datetime.fromisoformat(_clean(start))
                t1 = datetime.fromisoformat(_clean(end))
                d = (t1 - t0).total_seconds()
                if d > 0:
                    durations.append(d)
            except Exception:
                pass
    return durations


# ---------- public API ----------

def compute_core_v1_for_run(
    run_id: str,
    *,
    rt_max: float = 5.0,
    baseline_s: Optional[float] = None,
    all_session_times: Optional[list[float]] = None,
) -> Tuple[Dict[str, Any], str]:
    events = _load_events_for_run(run_id)
    pilot_tag = events[0].get("pilot_tag", "generic") if events else "generic"
    decisions = _to_decisions(events, pilot_tag=pilot_tag)

    # Use new rich results
    rich_results: Dict[str, MetricResult] = compute_metrics_with_results(
        decisions=decisions,
        rt_max=rt_max,
        basel3ine_s=baseline_s,
        all_session_times=all_session_times,
    )
    by_agent = compute_metrics_by_agent(
        decisions, rt_max=rt_max, baseline_s=baseline_s
    )

    # Flatten for backward compat (value or None)
    metrics_flat = {k: v.value for k, v in rich_results.items()}

    # Collect warnings — only non-None
    warnings = [
        {"metric": k, "warning": v.warning}
        for k, v in rich_results.items()
        if v.warning is not None
    ]

    artifact = {
        "run_id": run_id,
        "metrics_suite": "core_v1",
        "params": {"rt_max": rt_max, "baseline_s": baseline_s},
        "metrics": metrics_flat,        # dict[str, float|None]
        "warnings": warnings,           # NEW: surfaces all metric warnings
        "by_agent": by_agent,
        "counts": {"events": len(events), "decisions": len(decisions)},
    }
    out_ref = _write_core_artifact(run_id, artifact)
    return artifact, out_ref
