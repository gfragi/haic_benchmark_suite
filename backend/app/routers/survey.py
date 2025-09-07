# app/routers/survey.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from app.schemas.survey import SurveyCreate
from app.utils.database import get_db
from app.services.survey_service import (
    create_survey,
    aggregate_survey_metrics,
    distinct_app_versions,
    aggregate_for_version,
)

router = APIRouter()

@router.post("", summary="Submit a survey response")
async def submit_survey(survey: SurveyCreate, db: Session = Depends(get_db)):
    try:
        db_survey = create_survey(db, survey)
        return {"status": "success", "message": "Survey response saved", "survey_id": db_survey.survey_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/aggregate", summary="Get aggregated survey metrics")
def get_aggregated_metrics(
    pilot_tag: Optional[str] = Query(None),
    db: Session = Depends(get_db)
):
    return aggregate_survey_metrics(db, pilot_tag=pilot_tag)

@router.get("/versions", response_model=List[str], summary="List app versions that have surveys for a pilot")
def list_versions_for_pilot(
    pilot_tag: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return distinct_app_versions(db, pilot_tag) or []

@router.get("/summary", summary="Aggregated metrics for a single pilot/version")
def version_summary(
    pilot_tag: str = Query(..., min_length=1),
    app_version: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Returns: { pilot_tag, app_version, avg_sus, avg_ethics, count }
    """
    return aggregate_for_version(db, pilot_tag, app_version)

@router.get("/compare", summary="Compare two versions for a pilot")
def compare_versions(
    pilot_tag: str = Query(..., min_length=1),
    version_a: str = Query(..., min_length=1),
    version_b: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
) -> Dict[str, Any]:
    """
    Returns:
    {
      "A": { pilot_tag, app_version, avg_sus, avg_ethics, count },
      "B": { pilot_tag, app_version, avg_sus, avg_ethics, count }
    }
    """
    return {
        "A": aggregate_for_version(db, pilot_tag, version_a),
        "B": aggregate_for_version(db, pilot_tag, version_b),
    }
