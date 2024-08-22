import datetime
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry
from app.services.evaluate import evaluate_log
from app.services.evaluate import get_available_metrics

router = APIRouter()

@router.post("/{log_id}", response_model=dict)
def evaluate_log(log_id: int, db: Session = Depends(get_db)):
    log = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log not found")

    config = log.evaluation_config
    if not config:
        raise HTTPException(status_code=404, detail="Associated evaluation config not found")

    # Perform evaluation
    result = evaluate_log(log, config)

    # Save result
    db_result = EvaluationResult(
        log_id=log.id,
        metrics=result,
        evaluation_date=str(datetime.utcnow())
    )
    db.add(db_result)
    db.commit()
    db.refresh(db_result)

    return db_result

@router.get("/metrics", response_model=dict)
def get_metrics():
    metrics = get_available_metrics()
    return {"metrics": list(metrics)}