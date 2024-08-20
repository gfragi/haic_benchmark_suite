from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry
from app.services.evaluate import evaluate_log

router = APIRouter()

@router.post("/{log_id}", response_model=dict)
def evaluate_log_entry(log_id: int, db: Session = Depends(get_db)):
    log = db.query(LogEntry).filter(LogEntry.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")
    
    config = log.evaluation_config
    
    metrics_results = evaluate_log(log, config)
    
    evaluation_result = EvaluationResult(log_id=log_id, metrics=metrics_results, evaluation_date=log.end_time)
    db.add(evaluation_result)
    db.commit()
    db.refresh(evaluation_result)
    
    return metrics_results
