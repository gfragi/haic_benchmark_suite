import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry
from app.services.metrics import get_available_metrics
from app.utils.generic_functions import get_config_by_id
from fastapi import BackgroundTasks

from app.models.configuration import EvaluationConfig
from app.services.evaluate import run_evaluation


router = APIRouter()

# Trigger Evaluation Endpoint
@router.post("/{configuration_id}")
async def evaluate_config(configuration_id: int, background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    # Fetch the configuration by ID
    config = get_config_by_id(configuration_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Update the status to running
    config.evaluation_status = EvaluationConfig.STATUS_RUNNING
    db.commit()

    # Run the evaluation in the background, passing the config ID
    background_tasks.add_task(run_evaluation, configuration_id)

    return {"detail": "Evaluation started successfully"}

# Fetch Evaluation Results
@router.get("/{configuration_id}/results")
async def get_evaluation_results(configuration_id: int, db: Session = Depends(get_db)):
    results = db.query(EvaluationResult).filter(EvaluationResult.configuration_id == configuration_id).all()
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this configuration")
    return results

@router.get("/metrics", response_model=dict)
def get_metrics():
    metrics = get_available_metrics()
    return {"metrics": list(metrics)}
