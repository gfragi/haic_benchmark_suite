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

def calculate_ethics_score(ethics: dict) -> float:
    total = sum(ethics.values())
    count = len(ethics)
    if count == 0:
        return 0.0
    avg = total / count
    return avg * 20  # Rescale average to 0-100

def aggregate_survey_metrics(db_session: Session) -> dict:
    surveys = db_session.query(Survey).all()
    pilot_results = defaultdict(list)

    for survey in surveys:
        tam_data = survey.tam_sus_responses   # dict containing SUS responses
        ethics_data = survey.ethics_responses   # dict containing ethics responses

        sus_score = calculate_sus_score(tam_data)
        ethics_score = calculate_ethics_score(ethics_data)

        pilot_results[survey.pilot_tag].append((sus_score, ethics_score))

    aggregated_results = {}
    for pilot, scores in pilot_results.items():
        count = len(scores)
        avg_sus = sum(s[0] for s in scores) / count
        avg_ethics = sum(s[1] for s in scores) / count
        aggregated_results[pilot] = {
            'avg_sus': avg_sus,
            'avg_ethics': avg_ethics,
            'count': count
        }
    return aggregated_results
