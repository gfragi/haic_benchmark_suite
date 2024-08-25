from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry, EvaluationConfig
from app.schemas.results import EvaluationResultSchema
from app.services.evaluate import evaluate_logs_and_save_results

router = APIRouter()

@router.post("/", response_model=EvaluationResultSchema)
def create_evaluation_result(result: EvaluationResultSchema, db: Session = Depends(get_db)):
    # Ensure the configuration exists
    config = db.query(EvaluationConfig).filter(EvaluationConfig.id == result.configuration_id).first()
    if not config:
        raise HTTPException(status_code=404, detail="Configuration not found")

    # Perform the evaluation
    metrics = evaluate_logs_and_save_results(result.configuration_id, db)

    # Create the evaluation result
    db_result = EvaluationResult(
        configuration_id=result.configuration_id,
        accuracy=metrics.get("Prediction Accuracy"),
        precision=metrics.get("Precision"),
        recall=metrics.get("Recall"),
        human_ai_agreement_rate=metrics.get("Human-AI Agreement Rate"),
        time_to_resolution=metrics.get("Time to Resolution"),
        human_effort_saved=metrics.get("Human Effort Saved"),
        ai_assistance_rate=metrics.get("AI Assistance Rate"),
        learning_efficiency=metrics.get("Learning Efficiency"),
        correction_efficiency=metrics.get("Correction Efficiency"),
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
    query = db.query(EvaluationResult).join(EvaluationConfig)

    if start_date:
        query = query.filter(EvaluationResult.evaluation_date >= start_date)
    if end_date:
        query = query.filter(EvaluationResult.evaluation_date <= end_date)
    if ai_model_name:
        query = query.filter(EvaluationConfig.ai_model_name == ai_model_name)
    if min_accuracy:
        query = query.filter(EvaluationResult.accuracy >= min_accuracy)
    if max_accuracy:
        query = query.filter(EvaluationResult.accuracy <= max_accuracy)

    results = query.all()
    return results
