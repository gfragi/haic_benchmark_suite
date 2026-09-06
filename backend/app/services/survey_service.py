#survey_service.py
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session
from sqlalchemy import text, func
from app.schemas.survey import SurveyCreate
from app.models.survey import Survey
from app.models.configuration import EvaluationConfig
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
        domain_specific=survey_data.domain_specific,
        configuration_id=survey_data.configuration_id,
    )
    db.add(db_survey)
    db.commit()
    db.refresh(db_survey)
    return db_survey


def list_pilots_overview(db: Session) -> List[Dict[str, Any]]:
    """
    One row per distinct pilot_tag: total response count, a per-app_version
    breakdown, and first/last submission timestamps. Every other
    pilot-scoped endpoint (aggregate/summary/raw/export/...) requires
    already knowing the pilot_tag - this is the discovery step before that,
    e.g. to see what's actually there before an export/migration.
    """
    surveys = db.query(Survey).order_by(Survey.timestamp).all()

    by_pilot: Dict[str, List[Survey]] = {}
    for s in surveys:
        by_pilot.setdefault(s.pilot_tag, []).append(s)

    out = []
    for pilot_tag, rows in sorted(by_pilot.items()):
        by_version: Dict[str, int] = {}
        for r in rows:
            key = r.app_version or "Unknown"
            by_version[key] = by_version.get(key, 0) + 1
        timestamps = [r.timestamp for r in rows if r.timestamp]

        out.append({
            "pilot_tag": pilot_tag,
            "response_count": len(rows),
            "versions": [
                {"app_version": v, "response_count": c}
                for v, c in sorted(by_version.items(), key=lambda kv: -kv[1])
            ],
            "first_response_at": min(timestamps).isoformat() if timestamps else None,
            "last_response_at": max(timestamps).isoformat() if timestamps else None,
        })
    return out


def import_surveys(
    db: Session,
    rows: List[Dict[str, Any]],
    pilot_tag_overrides: Optional[Dict[str, int]] = None,
    drop_schema_id: bool = True,
    dry_run: bool = False,
    use_row_configuration_id: bool = False,
) -> Dict[str, Any]:
    """
    Bulk-imports survey rows (the shape full_survey_export() / GET
    /survey/export produces) into THIS platform. By default,
    configuration_id is never taken from the source row - a raw config id
    isn't portable across environments - it's resolved by matching the
    row's pilot_tag against this platform's own `configurations.pilot_tag`.
    pilot_tag isn't unique per configuration in practice, so:
      - exactly one match here -> use it
      - zero or multiple matches -> configuration_id left null, reported in
        unmatched_pilot_tags / ambiguous_pilot_tags, unless the caller
        supplied an explicit override for that pilot_tag.
    use_row_configuration_id skips all of that (for rows where the row's
    own configuration_id is non-null) and uses it as-is - for deliberately
    testing an import against one specific config, not for a real
    cross-environment migration.

    Each row is inserted independently (via create_survey(), so it gets the
    same schema validation POST /survey does) - one bad row is reported and
    skipped rather than aborting the whole batch. dry_run resolves and
    reports without writing anything.
    """
    overrides = pilot_tag_overrides or {}

    configs = (
        db.query(EvaluationConfig.id, EvaluationConfig.pilot_tag)
        .filter(EvaluationConfig.pilot_tag.isnot(None))
        .all()
    )
    by_tag: Dict[str, List[int]] = {}
    for config_id, tag in configs:
        by_tag.setdefault(tag, []).append(config_id)

    imported = 0
    failed: List[Dict[str, Any]] = []
    unmatched_pilot_tags = set()
    ambiguous_pilot_tags: Dict[str, List[int]] = {}

    for row in rows:
        if use_row_configuration_id and row.get("configuration_id") is not None:
            resolved_config_id = row["configuration_id"]
        else:
            tag = row.get("pilot_tag")
            if tag in overrides:
                resolved_config_id = overrides[tag]
            else:
                matches = by_tag.get(tag, [])
                if len(matches) == 1:
                    resolved_config_id = matches[0]
                elif len(matches) == 0:
                    resolved_config_id = None
                    unmatched_pilot_tags.add(tag)
                else:
                    resolved_config_id = None
                    ambiguous_pilot_tags[tag] = matches

        if dry_run:
            imported += 1
            continue

        try:
            payload = SurveyCreate(
                survey_id=row["survey_id"],
                user_id=row["user_id"],
                timestamp=row["timestamp"],
                pilot_tag=row["pilot_tag"],
                app_version=row.get("app_version"),
                ai_model_version=row.get("ai_model_version"),
                tam_sus_responses=row["tam_sus_responses"],
                ethics_responses=row["ethics_responses"],
                domain_specific=row.get("domain_specific"),
                configuration_id=resolved_config_id,
                schema_id=None if drop_schema_id else row.get("schema_id"),
            )
            create_survey(db, payload)
            imported += 1
        except Exception as e:
            db.rollback()
            failed.append({"survey_id": row.get("survey_id"), "error": str(e)})

    return {
        "dry_run": dry_run,
        "imported": imported,
        "failed": failed,
        "unmatched_pilot_tags": sorted(unmatched_pilot_tags),
        "ambiguous_pilot_tags": ambiguous_pilot_tags,
    }


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


def domain_specific_averages(db: Session, pilot_tag: str, app_version: str):
    """
    Aggregate each survey's domain_specific responses, grouped by the schema_id
    that was active when it was submitted (different versions of a pilot can
    have different custom question sets, so there's no single fixed key set
    to aggregate against like SUS/Ethics).

    Returns:
      { "schemas": [
          { "schema_id": "...", "name": "...", "version": 1, "respondent_count": 12,
            "questions": [
              {"id": "q1", "label": "...", "type": "likert", "avg": 4.2, "count": 12},
              {"id": "q2", "label": "...", "type": "single", "distribution": {"Yes": 8, "No": 4}, "count": 12},
              {"id": "q3", "label": "...", "type": "text", "answers": ["...", "..."], "count": 5},
            ] },
          ...
      ] }
    """
    surveys = (
        db.query(Survey)
        .filter(
            Survey.pilot_tag == pilot_tag,
            Survey.app_version == app_version,
            Survey.schema_id.isnot(None),
        )
        .all()
    )

    by_schema: Dict[str, List[Survey]] = {}
    for s in surveys:
        if not s.domain_specific:
            continue
        by_schema.setdefault(str(s.schema_id), []).append(s)

    schemas_out = []
    for schema_id, group in by_schema.items():
        schema = fetch_schema_by_id(db, schema_id, raise_if_missing=False)
        if not schema:
            continue

        questions_out = []
        for q in schema.questions:
            qid, qtype = q["id"], q["type"]
            answers = [
                s.domain_specific[qid]
                for s in group
                if s.domain_specific and qid in s.domain_specific and s.domain_specific[qid] is not None
            ]
            if not answers:
                continue

            if qtype in ("likert", "number"):
                questions_out.append({
                    "id": qid, "label": q["label"], "type": qtype,
                    "avg": sum(answers) / len(answers), "count": len(answers),
                })
            elif qtype == "multi":
                dist: Dict[str, int] = {}
                for val in answers:
                    for opt in (val or []):
                        dist[opt] = dist.get(opt, 0) + 1
                questions_out.append({
                    "id": qid, "label": q["label"], "type": qtype,
                    "distribution": dist, "count": len(answers),
                })
            elif qtype in ("single", "boolean"):
                dist: Dict[str, int] = {}
                for val in answers:
                    key = str(val)
                    dist[key] = dist.get(key, 0) + 1
                questions_out.append({
                    "id": qid, "label": q["label"], "type": qtype,
                    "distribution": dist, "count": len(answers),
                })
            else:  # text or unrecognized types: nothing to average, list the actual answers
                questions_out.append({
                    "id": qid, "label": q["label"], "type": qtype,
                    "answers": answers, "count": len(answers),
                })

        schemas_out.append({
            "schema_id": schema_id,
            "name": schema.name,
            "version": schema.version,
            "respondent_count": len(group),
            "questions": questions_out,
        })

    return {"schemas": schemas_out}


def list_comments(db: Session, pilot_tag: str, app_version: Optional[str] = None):
    """
    Raw free-text comments submitted alongside a survey response. Not
    aggregated like domain_specific_averages() - "comment" is a synthetic
    key (see PublicSurveyPage.jsx), not a real schema question, so it's
    silently skipped by that aggregation. There's nothing numeric to average
    for free text anyway, so this just lists it directly.

    Deliberately excludes user_id - only comment text, app_version, and
    timestamp, so this is safe to show in the UI without exposing respondent
    identity.
    """
    query = db.query(Survey).filter(Survey.pilot_tag == pilot_tag)
    if app_version:
        query = query.filter(Survey.app_version == app_version)

    comments = []
    for s in query.all():
        text_val = (s.domain_specific or {}).get("comment")
        if text_val:
            comments.append({
                "app_version": s.app_version,
                "comment": text_val,
                "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            })

    comments.sort(key=lambda c: c["timestamp"] or "", reverse=True)
    return comments


def raw_survey_responses(db: Session, pilot_tag: str, app_version: Optional[str] = None):
    """
    One row per survey submission, for an analytic (non-aggregated) CSV export.
    Flattens tam_sus_responses/ethics_responses/domain_specific into prefixed
    columns (sus_*/ethics_*/domain_*) since each is stored as a JSON blob per
    row; different rows can have different domain_* keys (schema varies by
    version), so callers should take the union of keys across rows for a CSV
    header rather than assuming a fixed column set.

    respondent_id is the client-generated anonymous id (see makeAnonymousUserId
    in the frontend), not a real identity - safe to include for spotting
    duplicate/repeat submissions.
    """
    query = db.query(Survey).filter(Survey.pilot_tag == pilot_tag)
    if app_version:
        query = query.filter(Survey.app_version == app_version)

    rows = []
    for s in query.order_by(Survey.timestamp).all():
        row = {
            "respondent_id": s.user_id,
            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            "app_version": s.app_version,
            "ai_model_version": s.ai_model_version,
        }
        for k, v in (s.tam_sus_responses or {}).items():
            row[f"sus_{k}"] = v
        for k, v in (s.ethics_responses or {}).items():
            row[f"ethics_{k}"] = v
        for k, v in (s.domain_specific or {}).items():
            row[f"domain_{k}"] = v
        rows.append(row)
    return rows


def full_survey_export(db: Session, pilot_tag: Optional[str] = None) -> List[Dict[str, Any]]:
    """
    Full-fidelity row-per-submission export, including survey_id,
    configuration_id, and schema_id - unlike raw_survey_responses() (GET
    /survey/raw), which is analytics-oriented and deliberately drops those
    three for a flattened CSV shape. Each row here is shaped to be POSTed
    back as-is to POST /survey (see SurveyCreate) on another environment,
    for migrating survey data between deployments.
    """
    query = db.query(Survey)
    if pilot_tag:
        query = query.filter(Survey.pilot_tag == pilot_tag)

    rows = []
    for s in query.order_by(Survey.timestamp).all():
        rows.append({
            "survey_id": str(s.survey_id),
            "user_id": s.user_id,
            "timestamp": s.timestamp.isoformat() if s.timestamp else None,
            "pilot_tag": s.pilot_tag,
            "app_version": s.app_version,
            "ai_model_version": s.ai_model_version,
            "schema_id": str(s.schema_id) if s.schema_id else None,
            "tam_sus_responses": s.tam_sus_responses,
            "ethics_responses": s.ethics_responses,
            "domain_specific": s.domain_specific,
            "configuration_id": s.configuration_id,
        })
    return rows