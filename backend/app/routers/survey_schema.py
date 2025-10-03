from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional, List

from app.utils.database import get_db
from app.schemas.survey_schema import SurveyQuestionSetIn, SurveyQuestionSetOut
from app.services.survey_schema_service import (
    create_schema, fetch_schema_by_id, fetch_latest_for_pilot
)

router = APIRouter()

@router.post("", response_model=SurveyQuestionSetOut)
def create_schema_route(payload: SurveyQuestionSetIn, db: Session = Depends(get_db)):
    obj = create_schema(db, payload)
    return SurveyQuestionSetOut(
        schema_id=str(obj.schema_id),
        name=obj.name,
        pilot_tag=obj.pilot_tag,
        version=obj.version,
        questions=obj.questions,
        active=obj.active,
        created_by=obj.created_by,
    )

@router.get("/{schema_id}", response_model=SurveyQuestionSetOut)
def get_schema(schema_id: str, db: Session = Depends(get_db)):
    obj = fetch_schema_by_id(db, schema_id)
    return SurveyQuestionSetOut(
        schema_id=str(obj.schema_id),
        name=obj.name,
        pilot_tag=obj.pilot_tag,
        version=obj.version,
        questions=obj.questions,
        active=obj.active,
        created_by=obj.created_by,
    )

@router.get("", response_model=Optional[SurveyQuestionSetOut])
def get_latest_for_pilot(pilot_tag: str = Query(...), db: Session = Depends(get_db)):
    obj = fetch_latest_for_pilot(db, pilot_tag)
    if not obj:
        return None
    return SurveyQuestionSetOut(
        schema_id=str(obj.schema_id),
        name=obj.name,
        pilot_tag=obj.pilot_tag,
        version=obj.version,
        questions=obj.questions,
        active=obj.active,
        created_by=obj.created_by,
    )
