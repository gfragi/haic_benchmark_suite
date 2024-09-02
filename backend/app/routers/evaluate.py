import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry
from app.services.metrics import Metrics
from app.utils.generic_functions import get_config_by_id
from fastapi import BackgroundTasks

from app.models.configuration import EvaluationConfig
from app.services.evaluate import run_evaluation
from app.services.metrics import Metrics
from app.utils.generic_functions import get_config_by_id


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

@router.get("/metrics", response_model=dict)
def get_metrics():
    metrics = Metrics.get_available_metrics()
    return {"metrics": list(metrics)}
