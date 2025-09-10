from datetime import datetime, timezone
import io
import json
import os
import uuid
from dotenv import load_dotenv
from sqlmodel import Session
from metrics_core.outcome_metrics import Metrics
from app.models import EvaluationConfig, LogEntry
from app.models.results import EvaluationResult, MetricGroup
from app.utils.database import SessionLocal
from app.utils.minio_utils import get_minio_client
from app.services.metrics_adapter import compute_from_log
import traceback

load_dotenv()

minio_client = get_minio_client()



def split_logs_by_ai_model_version(logs_data: list):
    # Create a dictionary to hold logs by AI model version
    logs_by_ai_version = {}

    # Iterate through the logs and separate them by AI model version
    for entry in logs_data:
        ai_model_version = entry.get('ai_model_version', "Unknown")

        if ai_model_version not in logs_by_ai_version:
            logs_by_ai_version[ai_model_version] = []

        # Append the log entry to the corresponding version list
        logs_by_ai_version[ai_model_version].append(entry)

    return logs_by_ai_version


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

        # Read the uploaded logs JSON from MinIO
        try:
            obj = minio_client.get_object(bucket, config.minio_path)
        except Exception as e:
            raise RuntimeError(
                f"Failed to get object from MinIO (bucket='{bucket}', path='{config.minio_path}'): {e}"
            )

        try:
            raw_bytes = obj.read()
        finally:
            # ensure connection is always released
            try:
                obj.close()
                obj.release_conn()
            except Exception:
                pass

        try:
            logs_data = json.loads(raw_bytes.decode("utf-8"))
        except Exception as e:
            raise ValueError(f"Object at '{config.minio_path}' is not valid JSON: {e}")

        if isinstance(logs_data, dict):
            logs_data = [logs_data]
        if not isinstance(logs_data, list):
            raise ValueError("Uploaded log must be a JSON object or a list of objects")

        # Group by AI model version
        logs_by_ai_version = split_logs_by_ai_model_version(logs_data)

        wrote_any_result = False

        for ai_model_version, logs in logs_by_ai_version.items():
            if not logs:
                continue

            # Collect app versions for this subset (nice to store in DB row)
            app_versions = sorted({e.get("app_version", "Unknown") for e in logs})
            app_version_str = ",".join(app_versions)

            # Compute derived metrics per session (adapter is forgiving to missing fields)
            derived_list = []
            for entry in logs:
                try:
                    derived = compute_from_log(entry)  # -> {"by_metric","by_pillar","interaction"}
                except Exception as e:
                    print(f"[evaluate] compute_from_log failed for entry: {repr(e)}")
                    derived = {"by_metric": {}, "by_pillar": {}, "interaction": {}}
                derived_list.append(derived)

            # Aggregate across sessions for this AI model version
            agg_by_metric   = _mean_map([d.get("by_metric", {})   for d in derived_list])
            agg_by_pillar   = _mean_map([d.get("by_pillar", {})   for d in derived_list])
            agg_interaction = _mean_map([d.get("interaction", {}) for d in derived_list])

            # Transform by-metric into your grouped layout (keeps compatibility with your UI)
            results_by_group = {
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

            # Compose the result payload we store to MinIO
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

            # Persist results JSON to MinIO
            result_file_path = f"{config.id}/results/{uuid.uuid4()}.json"
            encoded = json.dumps(result_data, ensure_ascii=False, indent=2).encode("utf-8")
            minio_client.put_object(
                bucket_name=bucket,
                object_name=result_file_path,
                data=io.BytesIO(encoded),
                length=len(encoded),
                content_type="application/json",
            )

            # Save EvaluationResult row
            db_result = EvaluationResult(
                configuration_id = config.id,
                evaluation_date  = datetime.now(timezone.utc),
                result_minio_path= result_file_path,
                app_version      = app_version_str,
                ai_model_version = ai_model_version,
            )
            new_session.add(db_result)
            new_session.commit()

            wrote_any_result = True

        config.evaluation_status = (
            EvaluationConfig.STATUS_COMPLETED if wrote_any_result
            else EvaluationConfig.STATUS_FAILED
        )

    except Exception as e:
        # rich error reporting
        print(f"[evaluate] Error during evaluation: {repr(e)}")
        print(traceback.format_exc())
        if 'config' in locals() and config:
            config.evaluation_status = EvaluationConfig.STATUS_FAILED
    finally:
        new_session.commit()
        new_session.close()