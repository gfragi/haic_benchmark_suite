from typing import List, Optional
from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from app.utils.database import get_db
from app.models import EvaluationResult
from app.schemas.results import EvaluationResultSchema
from app.services.agg_metrics import calculate_metrics_for_group

router = APIRouter()


# Fetch Evaluation Results grouped by configuration ID
@router.get("/{configuration_id}")
async def get_evaluation_results(configuration_id: int, db: Session = Depends(get_db)):
    results = db.query(EvaluationResult).filter(EvaluationResult.configuration_id == configuration_id).all()
    if not results:
        raise HTTPException(status_code=404, detail="No results found for this configuration")
    return results

# Fetch specific Evaluation Result
@router.get("/{configuration_id}/{result_id}")
async def get_evaluation_result(configuration_id: int, result_id: int, db: Session = Depends(get_db)):
    result = db.query(EvaluationResult).filter(
        EvaluationResult.configuration_id == configuration_id,
        EvaluationResult.id == result_id
    ).first()

    if not result:
        raise HTTPException(status_code=404, detail="No result found for this configuration and result ID")

    return result

# Fetch all Evaluation Results
@router.get("/list", response_model=List[EvaluationResultSchema])
def get_all_evaluation_results(db: Session = Depends(get_db)):
    results = db.query(EvaluationResult).all()
    return results


# Fetch Evaluation Results for a specific group of metrics
@router.get("/{configuration_id}/{group_name}")
async def get_evaluation_results(configuration_id: int, group_name: str, db: Session = Depends(get_db)):
    # Calculate or fetch the metrics for the specified group
    metrics = calculate_metrics_for_group(db, configuration_id, group_name)

    if not metrics:
        raise HTTPException(status_code=404, detail="No results found for this configuration and group")

    return metrics


# @router.get("/{result_id}", response_model=EvaluationResultSchema)
# def get_evaluation_result(result_id: int, db: Session = Depends(get_db)):
#     result = db.query(EvaluationResult).filter(EvaluationResult.id == result_id).first()
#     if not result:
#         raise HTTPException(status_code=404, detail="Evaluation result not found")
#     return result