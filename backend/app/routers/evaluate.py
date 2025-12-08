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
    - load per-session derived metrics from MinIO
    - aggregate them
    - store EvaluationResult
    - mark config as STATUS_COMPLETED
    """
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

        # 3) Load per-session derived metrics from MinIO
        session_metrics: List[Dict[str, Any]] = []
        for log_entry in logs:
            if not log_entry.derived_filename:
                # if you have older logs without derived, you could recompute here
                continue

            # IMPORTANT:
            # - configuration_id: int
            # - derived_filename: e.g. "uploads/session.20251128T...derived.json"
            derived = get_json(configuration_id, log_entry.derived_filename)
            session_metrics.append(derived)

        # 4) Aggregate across sessions
        summary = aggregate_session_metrics(session_metrics, config)

        # 5) Create and store an EvaluationResult
        result = EvaluationResult(
            configuration_id=configuration_id,
            created_at=datetime.now(timezone.utc),
            summary=summary,  # JSON column
        )
        db.add(result)

        # 6) Update config status
        config.evaluation_status = EvaluationConfig.STATUS_COMPLETED
        db.add(config)

        db.commit()

    finally:
        db.close()
