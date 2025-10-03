from typing import Optional, Dict, Any, List
from uuid import UUID
from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.survey_schema import SurveyQuestionSet
from app.schemas.survey_schema import SurveyQuestionSetIn

def fetch_schema_by_id(db: Session, schema_id: str) -> SurveyQuestionSet:
    obj = db.query(SurveyQuestionSet).filter(SurveyQuestionSet.schema_id == UUID(schema_id)).first()
    if not obj:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="schema not found")
    return obj

def fetch_latest_for_pilot(db: Session, pilot_tag: str) -> Optional[SurveyQuestionSet]:
    return (
        db.query(SurveyQuestionSet)
          .filter(SurveyQuestionSet.pilot_tag == pilot_tag, SurveyQuestionSet.active == True)
          .order_by(SurveyQuestionSet.version.desc(), SurveyQuestionSet.created_at.desc())
          .first()
    )

def create_schema(db: Session, payload: SurveyQuestionSetIn) -> SurveyQuestionSet:
    # (Optional) enforce unique (pilot_tag, version) pair
    obj = SurveyQuestionSet(
        name=payload.name,
        pilot_tag=payload.pilot_tag,
        version=payload.version or 1,
        questions=[q.model_dump() for q in payload.questions],
        active=payload.active,
        created_by=payload.created_by,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

# --- Validation of answers ---

def _ensure(cond: bool, msg: str):
    if not cond:
        raise HTTPException(status_code=422, detail=msg)

def validate_answers_against_schema(schema: SurveyQuestionSet, answers: Dict[str, Any]):
    q_index = {q["id"]: q for q in schema.questions}

    # required questions present?
    for q in schema.questions:
        if q.get("required") and q["id"] not in answers:
            raise HTTPException(status_code=422, detail=f"missing required answer: {q['id']}")

    # each provided answer must be known + type-checked
    for key, val in answers.items():
        q = q_index.get(key)
        _ensure(q is not None, f"unknown question id: {key}")

        t = q["type"]
        if t == "likert":
            _ensure(isinstance(val, (int, float)), f"{key} must be numeric")
            scale = q.get("scale") or {"min": 1, "max": 5}
            _ensure(scale["min"] <= float(val) <= scale["max"], f"{key} out of range")
        elif t == "single":
            _ensure(val in (q.get("options") or []), f"{key} not in options")
        elif t == "multi":
            _ensure(isinstance(val, list), f"{key} must be a list")
            opt = set(q.get("options") or [])
            _ensure(set(val).issubset(opt), f"{key} contains invalid options")
        elif t == "text":
            _ensure(isinstance(val, str), f"{key} must be a string")
        elif t == "number":
            _ensure(isinstance(val, (int, float)), f"{key} must be numeric")
        elif t == "boolean":
            _ensure(isinstance(val, bool), f"{key} must be boolean")
        else:
            raise HTTPException(status_code=422, detail=f"unsupported type for {key}: {t}")
