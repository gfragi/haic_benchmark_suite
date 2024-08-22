from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry
from app.schemas.results import EvaluationResultSchema

router = APIRouter()

@router.post("/", response_model=EvaluationResultSchema)
def create_evaluation_result(result: EvaluationResultSchema, db: Session = Depends(get_db)):
    # Ensure the log entry exists
    log = db.query(LogEntry).filter(LogEntry.id == result.log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log entry not found")

    # Create the evaluation result
    db_result = EvaluationResult(
        log_id=result.log_id,
        metrics=result.metrics,
        evaluation_date=result.evaluation_date
    )

    db.add(db_result)
    db.commit()
    db.refresh(db_result)
    return db_result

@router.get("/{result_id}", response_model=EvaluationResultSchema)
def get_evaluation_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")
    return result

@router.get("/list", response_model=List[EvaluationResultSchema])
def get_all_evaluation_results(db: Session = Depends(get_db)):
    results = db.query(EvaluationResult).all()
    return results


@router.get("/search", response_model=List[EvaluationResultSchema])
def query_evaluation_results(
    start_date: Optional[str] = Query(None),
    end_date: Optional[str] = Query(None),
    ai_model_name: Optional[str] = Query(None),
    min_accuracy: Optional[float] = Query(None),
    max_accuracy: Optional[float] = Query(None),
    db: Session = Depends(get_db)
):
    query = db.query(EvaluationResult)

    if start_date:
        query = query.filter(EvaluationResult.evaluation_date >= start_date)
    if end_date:
        query = query.filter(EvaluationResult.evaluation_date <= end_date)
    if ai_model_name:
        query = query.filter(EvaluationResult.ai_model_name == ai_model_name)
    if min_accuracy:
        query = query.filter(EvaluationResult.metrics['Prediction Accuracy'].as_float() >= min_accuracy)
    if max_accuracy:
        query = query.filter(EvaluationResult.metrics['Prediction Accuracy'].as_float() <= max_accuracy)

    results = query.all()
    return results