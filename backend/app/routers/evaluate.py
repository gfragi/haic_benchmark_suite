# app/routers/evaluate.py

from typing import List, Dict, Any
from datetime import datetime, timezone
from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.utils.database import SessionLocal, get_db
from app.utils.minio_utils import get_json
from app.utils.generic_functions import get_config_by_id
from app.models import LogEntry, EvaluationResult
from app.models.configuration import EvaluationConfig

router = APIRouter()

@router.post("/{configuration_id}")
def trigger_evaluation(configuration_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """
    Trigger evaluation for a specific configuration.
    This will run the evaluation process in the background.
    """
    # Check if configuration exists
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Check if configuration has any logs
    log_count = db.query(LogEntry).filter(LogEntry.configuration_id == configuration_id).count()
    if log_count == 0:
        raise HTTPException(status_code=400, detail="No logs found for this configuration")

    # Update status to running
    config.evaluation_status = EvaluationConfig.STATUS_RUNNING
    db.commit()

    # Run evaluation in background
    background_tasks.add_task(run_evaluation, configuration_id)

    return {
        "message": f"Evaluation started for configuration {configuration_id}",
        "status": "running",
        "log_count": log_count
    }


def aggregate_session_metrics(
    session_metrics: List[Dict[str, Any]],
    config: EvaluationConfig
) -> Dict[str, Any]:
    """
    Aggregate per-session derived metrics into a summary.
    Adapt this to your real KPI structure.
    """
    if not session_metrics:
        return {"message": "No session metrics available for this configuration"}

    n = len(session_metrics)
    sums: Dict[str, float] = {}

    # Assume each derived is either {"kpis": {...}} or flat dict of metrics
    for m in session_metrics:
        kpis = m.get("kpis", m)
        for key, value in kpis.items():
            if isinstance(value, (int, float)):
                sums[key] = sums.get(key, 0.0) + float(value)

    averages = {k: v / n for k, v in sums.items()}

    return {
        "num_sessions": n,
        "average_metrics": averages,
    }


def run_evaluation(configuration_id: int) -> None:
    """
    Background evaluation task:
    - open a new DB session
    - load config and all related logs
    - aggregate derived metrics from all logs
    - store aggregated result in MinIO
    - create EvaluationResult record
    - mark config as STATUS_COMPLETED
    """
    from app.utils.minio_utils import put_json

    db: Session = SessionLocal()
    try:
        # 1) Load configuration
        config = get_config_by_id(configuration_id, db)
        if not config:
            # config deleted or missing – nothing to do
            return

        # 2) Get all logs under this configuration
        logs: List[LogEntry] = (
            db.query(LogEntry)
            .filter(LogEntry.configuration_id == configuration_id)
            .all()
        )

        if not logs:
            config.evaluation_status = EvaluationConfig.STATUS_COMPLETED
            db.add(config)
            db.commit()
            return

        # 3) Aggregate metrics from all logs
        # For now, we'll create a simple aggregation
        # In a real implementation, you'd load derived metrics from MinIO
        total_logs = len(logs)
        summary = {
            "total_sessions": total_logs,
            "configuration_id": configuration_id,
            "evaluation_timestamp": datetime.now(timezone.utc).isoformat(),
            "status": "completed"
        }

        # 4) Store aggregated result in MinIO
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        result_filename = f"results/evaluation_{configuration_id}_{ts}.json"
        result_path = f"{configuration_id}/{result_filename}"

        put_json(configuration_id, result_filename, summary)

        # 5) Create EvaluationResult record
        result = EvaluationResult(
            configuration_id=configuration_id,
            evaluation_date=datetime.now(timezone.utc),
            result_minio_path=result_path,
            app_version=config.ai_model_name,  # Use AI model name as app version for now
            ai_model_version=config.ai_model_name
        )
        db.add(result)

        # 6) Update config status
        config.evaluation_status = EvaluationConfig.STATUS_COMPLETED
        db.add(config)

        db.commit()

    finally:
        db.close()
