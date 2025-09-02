from typing import Optional
from sqlalchemy.orm import Session
from app.schemas.survey import SurveyCreate
from app.models.survey import Survey
import uuid
from math import sqrt
from statistics import mean, pstdev

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

    groups = {}  # key -> {"sus": [], "ethics": []}

    for s in raw:
        if pilot_tag and s.pilot_tag != pilot_tag:
            continue
        key = (s.app_version or "Unknown") if pilot_tag else (s.pilot_tag or "Unknown")

        sus_score = calculate_sus_score(s.tam_sus_responses)   # already in your file
        ethics_vals = list(s.ethics_responses.values())
        ethics_score = ((sum(ethics_vals) / len(ethics_vals)) - 1) * 25 if ethics_vals else 0

        groups.setdefault(key, {"sus": [], "ethics": []})
        groups[key]["sus"].append(sus_score)
        groups[key]["ethics"].append(ethics_score)

    out = {}
    for k, v in groups.items():
        n = len(v["sus"])
        sus_mean = mean(v["sus"])
        ethics_mean = mean(v["ethics"])
        sus_std = pstdev(v["sus"]) if n > 1 else 0.0
        ethics_std = pstdev(v["ethics"]) if n > 1 else 0.0
        sus_se = sus_std / sqrt(n) if n > 1 else 0.0
        ethics_se = ethics_std / sqrt(n) if n > 1 else 0.0
        # 95% CI with normal approx; good enough for dashboarding
        out[k] = {
            "count": n,
            "avg_sus": sus_mean,
            "avg_ethics": ethics_mean,
            "sus_std": sus_std,
            "ethics_std": ethics_std,
            "sus_ci95": 1.96 * sus_se,
            "ethics_ci95": 1.96 * ethics_se,
            "sus_values": v["sus"],          # optional for box/violin
            "ethics_values": v["ethics"]
        }
    return out
