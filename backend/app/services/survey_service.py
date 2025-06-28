from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.survey import SurveyCreate
from app.models.survey import Survey
import uuid
from collections import defaultdict

def create_survey(db: Session, survey_data: SurveyCreate):
    db_survey = Survey(
        survey_id=uuid.UUID(survey_data.survey_id),
        user_id=survey_data.user_id,
        timestamp=survey_data.timestamp,
        pilot_tag=survey_data.pilot_tag,
        app_version=survey_data.app_version,
        ai_model_version=survey_data.ai_model_version,
        tam_sus_responses=survey_data.tam_sus_responses.dict(),
        ethics_responses=survey_data.ethics_responses.dict(),
        domain_specific=survey_data.domain_specific
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


def calculate_sus_score(sus: dict) -> float:
    total = 0
    for i in range(1, 11):
        key = f'sus_q{i}'
        value = sus.get(key, 0)
        if i % 2 == 1:
            total += value - 1
        else:
            total += 5 - value
    return total * 2.5

def aggregate_survey_metrics(db: Session, pilot_tag: Optional[str] = None):
    query = db.query(Survey)
    raw = query.all()

    grouped = {}

    for s in raw:
        # determine key based on mode
        if pilot_tag:
            if s.pilot_tag != pilot_tag:
                continue
            key = s.app_version or "Unknown"
        else:
            key = s.pilot_tag or "Unknown"

        sus_score = calculate_sus_score(s.tam_sus_responses)
        vals = list(s.ethics_responses.values())
        ethics_score = ((sum(vals) / len(vals)) - 1) * 25 if vals else 0

        if key not in grouped:
            grouped[key] = {
                "count": 0,
                "sus_total": 0,
                "ethics_total": 0
            }

        grouped[key]["count"] += 1
        grouped[key]["sus_total"] += sus_score
        grouped[key]["ethics_total"] += ethics_score

    return {
        k: {
            "avg_sus": v["sus_total"] / v["count"],
            "avg_ethics": v["ethics_total"] / v["count"],
            "count": v["count"]
        }
        for k, v in grouped.items()
    }
