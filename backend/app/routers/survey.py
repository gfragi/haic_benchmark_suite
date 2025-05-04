from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.schemas.survey import SurveyCreate
from app.services.survey_service import create_survey
from app.utils.database import get_db
from app.services.survey_service import aggregate_survey_metrics


router = APIRouter(prefix="", tags=["Survey"])


@router.post("", summary="Submit a survey response")
async def submit_survey(survey: SurveyCreate, db: Session = Depends(get_db)):
    try:
        db_survey = create_survey(db, survey)
        return {
            "status": "success",
            "message": "Survey response saved",
            "survey_id": db_survey.survey_id
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/aggregate", summary="Get aggregated survey metrics")
def get_aggregated_metrics(db: Session = Depends(get_db)):
    """
    Returns aggregated survey metrics grouped by pilot tag.
    For each pilot, it returns:
      - average SUS score
      - average Ethics score
      - number of responses collected
    """
    results = aggregate_survey_metrics(db)
    return results