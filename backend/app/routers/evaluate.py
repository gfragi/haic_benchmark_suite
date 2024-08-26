import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import SessionLocal, get_db
from app.models import EvaluationResult, LogEntry
from app.services.evaluate import evaluate_logs
from app.services.metrics import get_available_metrics
from app.utils.generic_functions import get_config_by_id
from fastapi import BackgroundTasks

from app.models.configuration import EvaluationConfig


router = APIRouter()

def run_evaluation(config_id: int):
    # Create a new session for the background task
    new_session = SessionLocal()

    try:
        # Re-fetch the configuration within the new session using the configuration ID
        config = new_session.query(EvaluationConfig).get(config_id)
        if not config:
            raise ValueError("Configuration not found")

        # Fetch the associated logs within the new session
        logs = new_session.query(LogEntry).filter(LogEntry.configuration_id == config.id).all()
        if not logs:
            raise ValueError("No logs found for this configuration")

        # Run the evaluation
        results = evaluate_logs(config, logs)

        # Initialize the EvaluationResult with all calculated metrics
        db_result = EvaluationResult(
            configuration_id=config.id,
            evaluation_date=datetime.datetime.utcnow(),
            **results  # Unpack the results dictionary to match column names in the EvaluationResult model
        )

        # Add and commit the single instance with all metrics
        new_session.add(db_result)
        config.evaluation_status = EvaluationConfig.STATUS_COMPLETED
    except Exception as e:
        # Update the status to failed if there was an error
        config.evaluation_status = EvaluationConfig.STATUS_FAILED
        print(f"Error during evaluation: {e}")
    finally:
        new_session.commit()
        new_session.close()  # Close the session when done

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
