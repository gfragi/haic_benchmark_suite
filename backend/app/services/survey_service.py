#survey_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.schemas.survey import SurveyCreate
from app.models.survey import Survey
import uuid
from math import sqrt
from statistics import mean, pstdev
from app.services.survey_schema_service import fetch_schema_by_id, validate_answers_against_schema


def create_survey(db: Session, survey_data: SurveyCreate):
    if survey_data.schema_id:
        schema = fetch_schema_by_id(db, survey_data.schema_id)
        validate_answers_against_schema(schema, survey_data.domain_specific or {})
        
    db_survey = Survey(
        survey_id=uuid.UUID(survey_data.survey_id),
        user_id=survey_data.user_id,
        timestamp=survey_data.timestamp,
        pilot_tag=survey_data.pilot_tag,
        app_version=survey_data.app_version,
        ai_model_version=survey_data.ai_model_version,
        schema_id=uuid.UUID(survey_data.schema_id) if survey_data.schema_id else None,
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


def distinct_app_versions(session: Session, pilot_tag: str) -> List[str]:
    # Postgres: pull distinct app versions for a pilot from the *surveys* table
    stmt = text("""
        SELECT DISTINCT app_version
        FROM surveys
        WHERE pilot_tag = :pilot
          AND app_version IS NOT NULL
        ORDER BY app_version
    """)
    rows = session.execute(stmt, {"pilot": pilot_tag}).all()
    # rows are tuples when using text(); first column is app_version
    return [r[0] for r in rows]



def aggregate_for_version(db: Session, pilot_tag: str, app_version: str) -> Dict[str, Any]:
    """
    Return a simple payload for one (pilot, version) with the fields the UI expects.
    Falls back to zeros if the version has no data.
    """
    all_stats: Dict[str, Dict[str, Any]] = aggregate_survey_metrics(db, pilot_tag=pilot_tag) or {}
    row: Optional[Dict[str, Any]] = all_stats.get(app_version)

    if not row:
        return {"pilot_tag": pilot_tag, "app_version": app_version,
                "avg_sus": 0.0, "avg_ethics": 0.0, "count": 0}

    # Map/normalize keys from your aggregator to what the UI expects.
    # If your aggregator already uses these names, this is a straight pass-through.
    return {
        "pilot_tag": pilot_tag,
        "app_version": app_version,
        "avg_sus": float(row.get("avg_sus", 0.0)),
        "avg_ethics": float(row.get("avg_ethics", 0.0)),
        "count": int(row.get("count", 0)),
    }
    
def question_averages(session: Session, pilot_tag: str, app_version: str):
    """
    Returns:
      {
        "sus": { "sus_q1": 3.9, ..., "sus_q10": 3.2 },
        "ethics": { "q_fairness": 4.2, ... }
      }
    Averages are on the 1..5 scale.
    This version uses JSON functions so it works if columns are JSON (not JSONB).
    """
    stmt = text("""
      WITH base AS (
        SELECT tam_sus_responses, ethics_responses
        FROM surveys
        WHERE pilot_tag = :pilot AND app_version = :ver
      )
      SELECT
        (
          SELECT json_object_agg(key, avg_val ORDER BY key)
          FROM (
            SELECT key, AVG( (value)::numeric ) AS avg_val
            FROM base, json_each_text(tam_sus_responses)
            GROUP BY key
          ) s
        ) AS sus,
        (
          SELECT json_object_agg(key, avg_val ORDER BY key)
          FROM (
            SELECT key, AVG( (value)::numeric ) AS avg_val
            FROM base, json_each_text(ethics_responses)
            GROUP BY key
          ) e
        ) AS ethics
      ;
    """)
    row = session.execute(stmt, {"pilot": pilot_tag, "ver": app_version}).first()
    # row[0] and row[1] can be None if no data
    return {"sus": row[0] or {}, "ethics": row[1] or {}} if row else {"sus": {}, "ethics": {}}