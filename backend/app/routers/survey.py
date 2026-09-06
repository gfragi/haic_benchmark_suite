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
    question_averages,
    domain_specific_averages,
    list_comments,
    raw_survey_responses,
    full_survey_export,
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

@router.get("/question-averages")
def question_averages_route(
    pilot_tag: str = Query(..., min_length=1),
    app_version: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return question_averages(db, pilot_tag, app_version)

@router.get("/domain-specific-averages", summary="Aggregate domain-specific question responses, grouped by schema")
def domain_specific_averages_route(
    pilot_tag: str = Query(..., min_length=1),
    app_version: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return domain_specific_averages(db, pilot_tag, app_version)

@router.get("/comments", summary="List free-text comments for a pilot (optionally filtered by app version)")
def list_comments_route(
    pilot_tag: str = Query(..., min_length=1),
    app_version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return list_comments(db, pilot_tag, app_version)

@router.get("/raw", summary="One row per survey submission, for an analytic (non-aggregated) CSV export")
def raw_survey_responses_route(
    pilot_tag: str = Query(..., min_length=1),
    app_version: Optional[str] = Query(None),
    db: Session = Depends(get_db),
):
    return raw_survey_responses(db, pilot_tag, app_version)

@router.get(
    "/export",
    summary="Full-fidelity survey export for migrating data between environments",
    description=(
        "One row per survey submission, including survey_id/configuration_id/schema_id "
        "(GET /survey/raw deliberately drops those for its flattened analytics shape). "
        "Each row is shaped to be POSTed back as-is to POST /survey on another "
        "environment - the intended use is exporting from one deployment and "
        "importing into another, not display."
    ),
)
def full_survey_export_route(
    pilot_tag: Optional[str] = Query(None, description="Restrict to one pilot; omit for all pilots"),
    db: Session = Depends(get_db),
):
    return full_survey_export(db, pilot_tag)