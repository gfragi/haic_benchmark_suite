from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.utils.database import get_db
from app.schemas.survey_schema import SurveyQuestionSetIn, SurveyQuestionSetOut
from app.services.survey_schema_service import (
    create_schema, fetch_schema_by_id, fetch_latest_for_pilot
)

router = APIRouter()

def _to_out(obj) -> SurveyQuestionSetOut:
    return SurveyQuestionSetOut(
        schema_id=str(obj.schema_id),
        name=obj.name,
        pilot_tag=obj.pilot_tag,
        version=obj.version,
        questions=obj.questions,
        question_position=obj.question_position,
        active=obj.active,
        created_by=obj.created_by,
        intro_title=obj.intro_title,
        intro_description=obj.intro_description,
    )

@router.post("", response_model=SurveyQuestionSetOut)
def create_schema_route(payload: SurveyQuestionSetIn, db: Session = Depends(get_db)):
    obj = create_schema(db, payload)
    return _to_out(obj)

@router.get("/{schema_id}", response_model=SurveyQuestionSetOut)
def get_schema(schema_id: str, db: Session = Depends(get_db)):
    obj = fetch_schema_by_id(db, schema_id)
    return _to_out(obj)

@router.get("", response_model=Optional[SurveyQuestionSetOut])
def get_latest_for_pilot(pilot_tag: str = Query(...), db: Session = Depends(get_db)):
    obj = fetch_latest_for_pilot(db, pilot_tag)
    if not obj:
        return None
    return _to_out(obj)
