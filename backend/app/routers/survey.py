# app/routers/survey.py
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy.orm import Session
from app.schemas.survey import SurveyCreate, SurveyImportRequest
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
    list_pilots_overview,
    import_surveys,
)

router = APIRouter()

@router.post("", summary="Submit a survey response")
async def submit_survey(survey: SurveyCreate, db: Session = Depends(get_db)):
    try:
        db_survey = create_survey(db, survey)
        return {"status": "success", "message": "Survey response saved", "survey_id": db_survey.survey_id}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get(
    "/pilots",
    summary="Overview of which pilots have survey data",
    description=(
        "One row per distinct pilot_tag - total response count, a "
        "per-app_version breakdown, and first/last submission timestamps. "
        "Every other pilot-scoped endpoint (aggregate/summary/raw/export/...) "
        "requires already knowing the pilot_tag - this is the discovery step "
        "before that."
    ),
)
def list_pilots_overview_route(db: Session = Depends(get_db)):
    return list_pilots_overview(db)

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
        "Feed the result straight into POST /survey/import on the target environment - "
        "the intended use is exporting from one deployment and importing into "
        "another, not display."
    ),
)
def full_survey_export_route(
    pilot_tag: Optional[str] = Query(None, description="Restrict to one pilot; omit for all pilots"),
    db: Session = Depends(get_db),
):
    return full_survey_export(db, pilot_tag)

@router.post(
    "/import",
    summary="Bulk-import survey rows exported from another environment",
    description=(
        "Takes the array GET /survey/export produces (on a source platform, e.g. "
        "dev) and imports it here. Accepts either that array pasted in directly "
        "(exactly what /export returns, no wrapping needed), or the full "
        "{rows, pilot_tag_config_overrides, drop_schema_id, dry_run} object when "
        "you need those extra options. configuration_id is never taken from the "
        "source row - a raw config id isn't portable across environments - it's "
        "resolved by matching each row's pilot_tag against THIS platform's own "
        "configurations. A pilot_tag that matches exactly one configuration "
        "here resolves automatically; one that matches zero or several is left "
        "unlinked (configuration_id null) and reported in unmatched_pilot_tags / "
        "ambiguous_pilot_tags, unless resolved via pilot_tag_config_overrides. "
        "Set use_row_configuration_id=true to instead trust each row's own "
        "configuration_id as-is (for rows where it's non-null) - only for "
        "deliberately testing an import against one specific config, not a real "
        "migration, since a raw configuration_id from elsewhere may not exist "
        "here or may mean something else entirely. "
        "Set dry_run to see how everything would resolve without writing anything."
    ),
    openapi_extra={
        # The handler takes a raw Request (to accept both an array and an
        # object body), so FastAPI can't derive a schema from a parameter
        # type the way it does everywhere else - this fills that back in by
        # hand so Swagger still shows a real schema/example instead of
        # "No parameters" / a bare "string" placeholder.
        "requestBody": {
            "required": True,
            "content": {
                "application/json": {
                    "schema": {
                        "oneOf": [
                            {"type": "array", "items": {"type": "object"}, "title": "Rows array"},
                            SurveyImportRequest.model_json_schema() | {"title": "Full options object"},
                        ]
                    },
                    "examples": {
                        "bare_array": {
                            "summary": "Paste GET /survey/export's output directly",
                            "value": [
                                {
                                    "survey_id": "f5a65a02-74f4-45f0-a9b9-6aba40b5c94d",
                                    "user_id": "anon_9265",
                                    "timestamp": "2026-03-27T12:30:23.944872",
                                    "pilot_tag": "applications",
                                    "app_version": "apps_v2.0.0",
                                    "ai_model_version": "apps-model-v1",
                                    "schema_id": None,
                                    "tam_sus_responses": {
                                        "sus_q1": 4, "sus_q2": 1, "sus_q3": 5, "sus_q4": 1, "sus_q5": 4,
                                        "sus_q6": 1, "sus_q7": 5, "sus_q8": 2, "sus_q9": 4, "sus_q10": 1,
                                    },
                                    "ethics_responses": {
                                        "q_fairness": 5, "q_transparency": 5, "q_privacy": 3,
                                        "q_accountability": 5, "q_trust": 5,
                                    },
                                    "domain_specific": {"user_type": "senior_operator", "experience_months": 35},
                                    "configuration_id": 3,
                                },
                            ],
                        },
                        "full_object": {
                            "summary": "With options (overrides, dry_run, ...)",
                            "value": {
                                "rows": [],
                                "pilot_tag_config_overrides": {"applications": 8},
                                "drop_schema_id": True,
                                "dry_run": True,
                                "use_row_configuration_id": False,
                            },
                        },
                    },
                }
            },
        }
    },
)
async def import_surveys_route(request: Request, db: Session = Depends(get_db)):
    body = await request.json()
    if not isinstance(body, (list, dict)):
        raise HTTPException(status_code=422, detail="Body must be a JSON array of rows, or an object with a 'rows' field.")
    try:
        payload = SurveyImportRequest(rows=body) if isinstance(body, list) else SurveyImportRequest(**body)
    except Exception as e:
        raise HTTPException(status_code=422, detail=str(e))
    return import_surveys(
        db, payload.rows, payload.pilot_tag_config_overrides, payload.drop_schema_id,
        payload.dry_run, payload.use_row_configuration_id,
    )