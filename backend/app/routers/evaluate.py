import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry
from app.services.evaluate import evaluate_logs
from app.services.metrics import get_available_metrics
from app.utils.generic_functions import get_config_by_id

router = APIRouter()


# Trigger Evaluation Endpoint
@router.post("/{configuration_id}")
async def evaluate_config(configuration_id: int, db: Session = Depends(get_db)):
    # Fetch the configuration by ID
    config = get_config_by_id(configuration_id, db)
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Fetch the associated logs
    logs = db.query(LogEntry).filter(LogEntry.configuration_id == configuration_id).all()
    if not logs:
        raise HTTPException(status_code=404, detail="No logs found for this configuration")

    # Run the evaluation
    results = evaluate_logs(config, logs)

    # Save the results in the database
    for metric_name, value in results.items():
        db_result = EvaluationResult(
            configuration_id=configuration_id,
            evaluation_date=datetime.datetime.utcnow(),
            **{metric_name: value}
        )
        db.add(db_result)
    db.commit()

    return {"detail": "Evaluation completed successfully", "results": results}

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