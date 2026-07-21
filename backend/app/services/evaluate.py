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
import logging
from typing import Iterable, List, Dict, Any
from collections import defaultdict

logger = logging.getLogger(__name__)


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


def _load_all_logs_from_prefix(bucket: str, prefix: str) -> list:
    """Scan all raw JSON files under a MinIO prefix and return combined session entries."""
    entries = []
    objects = _get_client().list_objects(bucket, prefix=prefix, recursive=True)
    for obj in objects:
        name = obj.object_name
        if not name.endswith(".json") or name.endswith(".derived.json"):
            continue
        try:
            entries.extend(_load_logs_from_minio(bucket, name))
        except Exception as e:
            print(f"[evaluate] Skipping {name}: {e}")
    return entries


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

    from app.services.schema_bridge import normalize_log_payload
    sessions, warnings = normalize_log_payload(logs_data)
    if warnings:
        logger.warning("Schema warnings loading %s: %s", minio_path, warnings)
    # Convert back to dicts for compatibility with _compute_derived_metrics()
    return [s.model_dump(mode="json") for s in sessions]


def _normalize_logs_data(logs_data):
    # Deprecated: use normalize_log_payload() from schema_bridge directly.
    # Kept for log_service.py import compatibility.
    from app.services.schema_bridge import normalize_log_payload
    sessions, _ = normalize_log_payload(logs_data)
    return [s.model_dump(mode="json") for s in sessions]

def _session_duration_s(session: dict) -> float | None:
    """
    Estimate one session's duration in seconds.
    Used to build the all_session_times list for P95 baseline derivation.

    Priority: session_started_at / session_ended_at > t-range from decisions.
    """
    def _parse_dt(v: Any):
        if v is None:
            return None
        if isinstance(v, datetime):
            return v
        if isinstance(v, str):
            try:
                return datetime.fromisoformat(v.replace("Z", "+00:00"))
            except Exception:
                pass
        return None

    s_dt = _parse_dt(session.get("session_started_at"))
    e_dt = _parse_dt(session.get("session_ended_at"))
    if s_dt and e_dt:
        dur = (e_dt - s_dt).total_seconds()
        if dur > 0:
            return dur

    # Fall back to t-value range from decisions (preserved by RC1 fix).
    decisions = session.get("decisions") or []
    t_vals = [
        d["t"] for d in decisions
        if isinstance(d.get("t"), (int, float)) and d["t"] is not None
    ]
    if t_vals:
        span = max(t_vals) - min(t_vals)
        if span > 0:
            return span

    return None


def _human_rt_seconds(decision: dict) -> float | None:
    """Prefer explicit duration_s; fall back to latency_ms -> seconds."""
    v = decision.get("duration_s")
    if isinstance(v, (int, float)):
        return float(v)
    ms = decision.get("latency_ms")
    if isinstance(ms, (int, float)):
        return float(ms) / 1000.0
    return None


def _all_session_times(logs: list) -> list | None:
    times = [_session_duration_s(e) for e in logs]
    return [d for d in times if d is not None and d > 0] or None


def _all_human_rts(logs: list) -> list | None:
    return [
        rt
        for entry in logs
        for d in (entry.get("decisions") or [])
        if str(d.get("actor_type", "")).lower() == "human"
        for rt in [_human_rt_seconds(d)]
        if rt is not None and rt > 0
    ] or None


def _compute_derived_metrics(
    logs: list,
    baseline_s: float | None = None,
    all_session_times: list | None = None,
    all_human_rts: list | None = None,
) -> list:
    """
    Compute derived metrics for a list of logs.

    `all_session_times`/`all_human_rts` should be computed ONCE across every
    ai_model_version being evaluated together (see run_evaluation) and passed
    in here, rather than recomputed per version-group from `logs` alone.
    Otherwise each version gets its own P95-derived baseline_s/rt_max ceiling,
    which shrinks as a version's own performance improves - silently
    absorbing genuine gains into a lower denominator instead of showing them
    in EL/HCL, and making the versions not comparable on a common scale. When
    not supplied (e.g. a single-version caller), falls back to deriving from
    just `logs`.
    """
    if all_session_times is None:
        all_session_times = _all_session_times(logs)
    if all_human_rts is None:
        all_human_rts = _all_human_rts(logs)

    derived_list = []
    for entry in logs:
        try:
            derived = compute_from_log(
                entry,
                baseline_s=baseline_s,
                all_session_times=all_session_times,
                all_human_rts=all_human_rts,
            )
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

def _compute_fairness(entries: list) -> dict | None:
    try:
        from app.services.fairness_service import compute_fairness_for_logs
        return compute_fairness_for_logs(entries)
    except Exception as e:
        logger.warning("Fairness computation skipped: %s", repr(e))
        return None


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

def _save_result_to_db(session, config_id: int, bucket: str, result_file_path: str, app_version_str: str, ai_model_version: str):
    """
    Save evaluation result to database, replacing any prior result for the
    same (config, ai_model_version) rather than accumulating a new row every
    time evaluation is re-triggered - re-running evaluation should update a
    version's result in place, not multiply its tabs on the dashboard.
    """
    stale = (
        session.query(EvaluationResult)
        .filter(
            EvaluationResult.configuration_id == config_id,
            EvaluationResult.ai_model_version == ai_model_version,
        )
        .all()
    )
    for old in stale:
        try:
            _get_client().remove_object(bucket, old.result_minio_path)
        except Exception as e:
            logger.warning("Could not remove stale result object %s: %s", old.result_minio_path, repr(e))
        session.delete(old)

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

        # Load and normalize logs — folder prefix (ends with /) → scan all files
        if config.minio_path.endswith("/"):
            entries = _load_all_logs_from_prefix(bucket, config.minio_path)
        else:
            entries = _load_logs_from_minio(bucket, config.minio_path)

        # Group by AI model version
        logs_by_ai_version = split_logs_by_ai_model_version(entries)

        # Clean up results for versions that no longer exist under this
        # config - not just versions being re-evaluated this run. Without
        # this, a version whose grouping key changes (e.g. a metadata-
        # extraction fix that turns "Unknown" into a real model name, or
        # logs simply being removed) leaves its old row behind forever,
        # since _save_result_to_db only replaces a row when the same label
        # re-evaluates, not when it disappears entirely.
        current_versions = set(logs_by_ai_version.keys())
        stale_query = new_session.query(EvaluationResult).filter(
            EvaluationResult.configuration_id == config.id,
        )
        if current_versions:
            stale_query = stale_query.filter(~EvaluationResult.ai_model_version.in_(current_versions))
        stale_results = stale_query.all()
        for old in stale_results:
            try:
                _get_client().remove_object(bucket, old.result_minio_path)
            except Exception as e:
                logger.warning("Could not remove stale result object %s: %s", old.result_minio_path, repr(e))
            new_session.delete(old)
        if stale_results:
            new_session.commit()

        # Computed ONCE across all versions being compared in this run, not
        # per version-group - see _compute_derived_metrics docstring for why
        # a shared ceiling/baseline is required for cross-version comparability.
        global_session_times = _all_session_times(entries)
        global_human_rts = _all_human_rts(entries)

        wrote_any_result = False

        for ai_model_version, logs in logs_by_ai_version.items():
            if not logs:
                continue

            # Collect app versions
            app_versions = sorted({_app_version(e) for e in logs})
            app_version_str = ",".join(app_versions)

            # Compute and aggregate metrics
            derived_list = _compute_derived_metrics(
                logs,
                baseline_s=config.baseline_s,
                all_session_times=global_session_times,
                all_human_rts=global_human_rts,
            )
            agg_by_metric, agg_by_pillar, agg_interaction = _aggregate_metrics(derived_list)
            results_by_group = _group_metrics_by_category(agg_by_metric)

            all_warnings = []
            for d in derived_list:
                all_warnings.extend(d.get("warnings", []))

            # Per-session values needed to recompute EL/EfficiencyScore live
            # for a different baseline_s (e.g. a "what if" slider) without
            # re-running the full pipeline. Not aggregated by simple mean
            # like the rest of `interaction` - EL clamps at 0 per session,
            # so the aggregate must be mean(per-session EL), not
            # EL(mean(total_time)) - pop them out of the naive-mean aggregate
            # and keep the raw per-session pairs instead.
            agg_interaction.pop("_TotalTimeS", None)
            agg_interaction.pop("_EffShapingFactor", None)
            el_recompute_sessions = [
                {
                    "total_time_s": d["interaction"]["_TotalTimeS"],
                    "shaping_factor": d["interaction"]["_EffShapingFactor"],
                }
                for d in derived_list
                if d.get("interaction", {}).get("_TotalTimeS") is not None
                and d.get("interaction", {}).get("_EffShapingFactor") is not None
            ]

            # Per-session metric values with a timestamp, for plotting any
            # metric against time (e.g. is Adaptability trending up across
            # sessions, not just within one) - the aggregates above collapse
            # sessions into a single mean, which hides that entirely.
            # session_started_at falls back to the session's earliest
            # decision timestamp when not set, so this still works for logs
            # that never provide an explicit session start/end.
            metric_timeseries = []
            for log_entry, d in zip(logs, derived_list):
                ts = log_entry.get("session_started_at")
                if not ts:
                    decision_ts = [
                        ts_ for dec in (log_entry.get("decisions") or [])
                        if (ts_ := dec.get("timestamp"))
                    ]
                    ts = min(decision_ts) if decision_ts else None
                if not ts:
                    continue
                metrics = {k: v for k, v in d.get("interaction", {}).items() if not k.startswith("_")}
                metric_timeseries.append({
                    "timestamp": ts,
                    "session_id": log_entry.get("session_id"),
                    **metrics,
                })
            metric_timeseries.sort(key=lambda r: r["timestamp"])

            # Compose result data
            result_data = {
                "configuration_id": config.id,
                "ai_model_version": ai_model_version,
                "app_versions": app_versions,
                "generated_at": datetime.now(timezone.utc).isoformat(),
                "source_log_path": config.minio_path,
                "warnings": all_warnings,
                "aggregates": {
                    "by_metric": agg_by_metric,
                    "by_pillar": agg_by_pillar,
                    "by_group": results_by_group,
                    "interaction": agg_interaction,
                },
                "fairness": _compute_fairness(logs),
                "el_recompute_sessions": el_recompute_sessions,
                "metric_timeseries": metric_timeseries,
            }

            # Save to MinIO and DB
            result_file_path = _save_result_to_minio(bucket, config.id, result_data)
            _save_result_to_db(new_session, config.id, bucket, result_file_path, app_version_str, ai_model_version)

            wrote_any_result = True

        config.evaluation_status = (
            EvaluationConfig.STATUS_COMPLETED if wrote_any_result
            else EvaluationConfig.STATUS_FAILED
        )

    except Exception as e:
        logger.error(
            "Evaluation failed for config %s: %s",
            config_id, repr(e), exc_info=True,
        )
        if 'config' in locals() and config:
            config.evaluation_status = EvaluationConfig.STATUS_FAILED
    finally:
        new_session.commit()
        new_session.close()
