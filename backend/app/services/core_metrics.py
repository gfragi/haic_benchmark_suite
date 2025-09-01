# app/services/core_metrics.py
from __future__ import annotations
from typing import Optional, Dict, Any, Tuple
from pathlib import Path
import io, json

from metrics_core.interaction_metrics import compute_metrics, compute_metrics_by_agent
from metrics_core.adapters.generic_json import to_decisions as generic_to_decisions

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
def _to_decisions(events: list[dict]) -> list[dict]:
    return generic_to_decisions(events)

# ---------- public API ----------

def compute_core_v1_for_run(
    run_id: str,
    *,
    rt_max: float = 5.0,
    baseline_s: Optional[float] = None,
) -> Tuple[Dict[str, Any], str]:
    events = _load_events_for_run(run_id)
    decisions = _to_decisions(events)

    summary = compute_metrics(decisions=decisions, rt_max=rt_max, baseline_s=baseline_s)
    by_agent = compute_metrics_by_agent(decisions, rt_max=rt_max, baseline_s=baseline_s)

    artifact = {
        "run_id": run_id,
        "metrics_suite": "core_v1",
        "params": {"rt_max": rt_max, "baseline_s": baseline_s},
        "metrics": summary,
        "by_agent": by_agent,
        "counts": {"events": len(events), "decisions": len(decisions)},
    }
    out_ref = _write_core_artifact(run_id, artifact)
    return artifact, out_ref
