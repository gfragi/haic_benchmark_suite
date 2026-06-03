from datetime import datetime, timezone
import io
import json
import os
import uuid
from dotenv import load_dotenv
from sqlmodel import Session
# Temporarily comment out metrics_core import
# from metrics_core.outcome_metrics import Metrics
from app.models import EvaluationConfig
from app.models.results import EvaluationResult, MetricGroup
from app.utils.database import SessionLocal
from app.utils.minio_utils import get_minio_client
from app.services.metrics_adapter import compute_from_log
import traceback
from typing import Iterable, List, Dict, Any
from collections import defaultdict


load_dotenv()

_minio_client = None

def _get_client():
    global _minio_client
    if _minio_client is None:
        _minio_client = get_minio_client()
    return _minio_client

def calculate_prediction_accuracy(interaction_data: list[dict]) -> float:
    """Calculate prediction accuracy from interaction data."""
    if not interaction_data:
        return 0.0

    correct_count = 0
    total_count = 0

    for interaction in interaction_data:
        result = interaction.get("result")
        if result in ["true_positive", "true_negative"]:
            correct_count += 1
            total_count += 1
        elif result in ["false_positive", "false_negative"]:
            total_count += 1

    return correct_count / total_count if total_count > 0 else 0.0

def calculate_response_time(interaction_data: list[dict]) -> float:
    """Calculate average response time from interaction data."""
    response_times = []
    for interaction in interaction_data:
        rt = interaction.get("response_time")
        if isinstance(rt, (int, float)):
            response_times.append(rt)

    return sum(response_times) / len(response_times) if response_times else 0.0

def _get(d: dict, path: Iterable[str], default=None):
    cur = d
    for p in path:
        if not isinstance(cur, dict) or p not in cur:
            return default
        cur = cur[p]
    return cur

def _norm_ver(v: Any) -> str:
    """Normalize version values: cast to str, strip, map ''/'None' to 'Unknown'."""
    if v is None:
        return "Unknown"
    if isinstance(v, (int, float)):
        v = str(v)
    v = str(v).strip()
    return v if v else "Unknown"

def _ai_version(entry: dict) -> str:
    # Prefer explicit field; then meta/runMeta fallbacks
    return _norm_ver(
        entry.get("ai_model_version")
        or _get(entry, ["meta", "ai_model_version"])
        or _get(entry, ["runMeta", "ai_model_version"])
        or _get(entry, ["runMeta", "app_version"])   # many logs use app_version as the model build id
    )

def _app_version(entry: dict) -> str:
    return _norm_ver(
        entry.get("app_version")
        or _get(entry, ["runMeta", "app_version"])
        or _get(entry, ["meta", "app_version"])
    )

def _iter_entries(payload: Any) -> List[dict]:
    """
    Return a flat list of session dicts from:
      - a list of dicts
      - a single dict
      - a dict containing 'sessions' | 'logs' | 'entries'
    Ignore anything that isn't a dict.
    """
    if isinstance(payload, list):
        return [x for x in payload if isinstance(x, dict)]

    if isinstance(payload, dict):
        for key in ("sessions", "logs", "entries"):
            if isinstance(payload.get(key), list):
                return [x for x in payload[key] if isinstance(x, dict)]
        return [payload]  # single-session object

    return []

def split_logs_by_ai_model_version(logs_data: list[dict]) -> dict[str, list[dict]]:
    groups = defaultdict(list)
    for entry in logs_data:
        if isinstance(entry, dict):
            groups[_ai_version(entry)].append(entry)  # <-- uses your helper
    return groups


def _mean_map(dicts: list[dict]) -> dict:
    """
    Mean-aggregate numeric values across a list of homogenous dicts.
    Non-numeric / missing values are ignored.
    """
    out: dict = {}
    if not dicts:
        return out
    all_keys = set().union(*(d.keys() for d in dicts))
    for k in all_keys:
        vals = [d.get(k) for d in dicts if isinstance(d.get(k), (int, float))]
        out[k] = (sum(vals) / len(vals)) if vals else None
    return out


def _load_logs_from_minio(bucket: str, minio_path: str) -> list:
    """Load and parse logs from MinIO."""
    try:
        obj = _get_client().get_object(bucket, minio_path)
    except Exception as e:
        raise RuntimeError(f"Failed to get object from MinIO (bucket='{bucket}', path='{minio_path}'): {e}")

    try:
        raw_bytes = obj.read()
    finally:
        try:
            obj.close()
            obj.release_conn()
        except Exception:
            pass

    try:
        text = raw_bytes.decode("utf-8")
    except Exception as e:
        raise ValueError(f"Object at '{minio_path}' is not valid UTF-8: {e}")

    try:
        logs_data = json.loads(text)
    except json.JSONDecodeError as e:
        raise ValueError(f"Object at '{minio_path}' is not valid JSON: {e.msg}")

    return _normalize_logs_data(logs_data)

def _normalize_logs_data(logs_data):
    """Normalize logs data to a list of session entries."""
    # Unwrap common wrappers
    if isinstance(logs_data, dict):
        for key in ("logs", "sessions", "entries"):
            if isinstance(logs_data.get(key), list):
                logs_data = logs_data[key]
                break

    # Normalize to a list of objects
    if isinstance(logs_data, dict):
        logs_data = [logs_data]
    if not isinstance(logs_data, list):
        raise ValueError("Uploaded log must be a JSON object or a list/array of objects")

    # Flatten / validate entries
    entries = _iter_entries(logs_data)
    if not entries:
        raise ValueError("Uploaded log contains no valid session entries.")

    return entries

def _compute_derived_metrics(logs: list) -> list:
    """Compute derived metrics for a list of logs."""
    derived_list = []
    for entry in logs:
        try:
            derived = compute_from_log(entry)
        except Exception as e:
            print(f"[evaluate] compute_from_log failed for entry: {repr(e)}")
            derived = {"by_metric": {}, "by_pillar": {}, "interaction": {}}
        derived_list.append(derived)
    return derived_list

def _aggregate_metrics(derived_list: list) -> tuple:
    """Aggregate metrics across sessions."""
    agg_by_metric = _mean_map([d.get("by_metric", {}) for d in derived_list])
    agg_by_pillar = _mean_map([d.get("by_pillar", {}) for d in derived_list])
    agg_interaction = _mean_map([d.get("interaction", {}) for d in derived_list])
    return agg_by_metric, agg_by_pillar, agg_interaction

def _group_metrics_by_category(agg_by_metric: dict) -> dict:
    """Group metrics by category for UI compatibility."""
    return {
        "Effectiveness": {
            k: v for k, v in agg_by_metric.items()
            if k in ("Prediction Accuracy","Precision","Recall","Overall System Accuracy","Model Improvement Rate")
        },
        "Efficiency": {
            k: v for k, v in agg_by_metric.items()
            if k in ("Response Time","Task Completion Time","Error Reduction Rate","Resource Utilization",
                     "Teaching Efficiency","Correction Efficiency","Knowledge Retention")
        },
        "Adaptability and Learning": {
            k: v for k, v in agg_by_metric.items()
            if k in ("Feedback Impact","Adaptability Score","Impact of Corrections","Learning Efficiency",
                     "Objective Fulfillment Rate")
        },
        "Collaboration and Interaction": {
            k: v for k, v in agg_by_metric.items()
            if k in ("AI Assistance Rate","Human-AI Agreement Rate","Decision Effectiveness","Time to Resolution",
                     "Human Effort Saved")
        },
        "Trust and Safety": {
            k: v for k, v in agg_by_metric.items()
            if k in ("Trust Score","Confidence","Safety Incidents","System Reliability")
        },
        "Robustness and Generalization": {
            k: v for k, v in agg_by_metric.items()
            if k in ("Adversarial Robustness","Domain Generalization")
        },
    }

def _save_result_to_minio(bucket: str, config_id: int, result_data: dict) -> str:
    """Save evaluation result to MinIO and return the path."""
    result_file_path = f"{config_id}/results/{uuid.uuid4()}.json"
    encoded = json.dumps(result_data, ensure_ascii=False, indent=2).encode("utf-8")
    _get_client().put_object(
        bucket_name=bucket,
        object_name=result_file_path,
        data=io.BytesIO(encoded),
        length=len(encoded),
        content_type="application/json",
    )
    return result_file_path

def _save_result_to_db(session, config_id: int, result_file_path: str, app_version_str: str, ai_model_version: str):
    """Save evaluation result to database."""
    db_result = EvaluationResult(
        configuration_id=config_id,
        evaluation_date=datetime.now(timezone.utc),
        result_minio_path=result_file_path,
        app_version=app_version_str,
        ai_model_version=ai_model_version,
    )
    session.add(db_result)
    session.commit()

def run_evaluation(config_id: int):
    new_session = SessionLocal()
    bucket = os.getenv("MINIO_BUCKET")

    try:
        if not bucket:
            raise ValueError("MINIO_BUCKET env var is missing.")

        config: EvaluationConfig | None = new_session.query(EvaluationConfig).get(config_id)
        if not config:
            raise ValueError(f"Configuration {config_id} not found")

        if not config.minio_path:
            raise ValueError(
                f"No minio_path set for EvaluationConfig {config_id}. "
                f"Upload or register a log first."
            )

        # Load and normalize logs
        entries = _load_logs_from_minio(bucket, config.minio_path)

        # Group by AI model version
        logs_by_ai_version = split_logs_by_ai_model_version(entries)

        wrote_any_result = False

        for ai_model_version, logs in logs_by_ai_version.items():
            if not logs:
                continue

            # Collect app versions
            app_versions = sorted({_app_version(e) for e in logs})
            app_version_str = ",".join(app_versions)

            # Compute and aggregate metrics
            derived_list = _compute_derived_metrics(logs)
            agg_by_metric, agg_by_pillar, agg_interaction = _aggregate_metrics(derived_list)
            results_by_group = _group_metrics_by_category(agg_by_metric)

            # Compose result data
            result_data = {
                "configuration_id": config.id,
                "ai_model_version": ai_model_version,
                "app_versions": app_versions,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_log_path": config.minio_path,
                "aggregates": {
                    "by_metric": agg_by_metric,
                    "by_pillar": agg_by_pillar,
                    "by_group": results_by_group,
                    "interaction": agg_interaction,
                },
            }

            # Save to MinIO and DB
            result_file_path = _save_result_to_minio(bucket, config.id, result_data)
            _save_result_to_db(new_session, config.id, result_file_path, app_version_str, ai_model_version)

            wrote_any_result = True

        config.evaluation_status = (
            EvaluationConfig.STATUS_COMPLETED if wrote_any_result
            else EvaluationConfig.STATUS_FAILED
        )

    except Exception as e:
        print(f"[evaluate] Error during evaluation: {repr(e)}")
        print(traceback.format_exc())
        if 'config' in locals() and config:
            config.evaluation_status = EvaluationConfig.STATUS_FAILED
    finally:
        new_session.commit()
        new_session.close()
