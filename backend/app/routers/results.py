from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends, Query
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult, LogEntry, EvaluationConfig
from app.schemas.results import EvaluationResultSchema
from app.services.agg_metrics import calculate_metrics_for_group

router = APIRouter()

@router.get("/list", response_model=List[EvaluationResultSchema])
def get_all_evaluation_results(db: Session = Depends(get_db)):
    results = db.query(EvaluationResult).all()
    return results


@router.get("/{result_id}", response_model=EvaluationResultSchema)
def get_evaluation_result(result_id: int, db: Session = Depends(get_db)):
    result = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
    if not result:
        raise HTTPException(status_code=404, detail="Evaluation result not found")
    return result




@router.get("/results/{configuration_id}/{group_name}")
async def get_evaluation_results(configuration_id: int, group_name: str, db: Session = Depends(get_db)):
    # Calculate or fetch the metrics for the specified group
    metrics = calculate_metrics_for_group(db, configuration_id, group_name)

    if not metrics:
        raise HTTPException(status_code=404, detail="No results found for this configuration and group")

    return metrics