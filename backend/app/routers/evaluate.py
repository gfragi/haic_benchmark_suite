# app/routers/evaluate.py

from fastapi import APIRouter, HTTPException, Depends, BackgroundTasks
from sqlalchemy.orm import Session

from app.models import LogEntry
from app.models.configuration import EvaluationConfig
from app.services.evaluate import run_evaluation as execute_evaluation
from app.utils.database import get_db

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

    # Run evaluation in background using the full evaluation pipeline
    background_tasks.add_task(execute_evaluation, configuration_id)

    message = f"Evaluation started for configuration {configuration_id}"
    return {
        "detail": message,
        "message": message,  # backward compatibility for older clients
        "status": "running",
        "log_count": log_count,
    }
