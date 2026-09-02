import time
from datetime import datetime
from typing import Any, Dict, List, Optional

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.ontology import OntologyEntity, ScenarioEntityUsage
from app.schemas.ontology import ENTITY_TYPES, OntologyEntityIn, OntologyEntityUpdate
from app.utils.errors import http_error

# entity_type (singular, DB value) -> top-level ontology JSON key (plural)
ENTITY_TYPE_TO_JSON_KEY = {
    "domain": "domains",
    "action_type": "action_types",
    "agent_role": "agent_roles",
    "persona_archetype": "persona_archetypes",
    "surrogate_tier": "surrogate_tiers",
    "metric_family": "metric_families",
    "template": "templates",
}

ONTOLOGY_SCHEMA = "haic.ontology.v1"
ONTOLOGY_VERSION = "1.0.0"

_CACHE_TTL_S = 30
_cache: Dict[str, Any] = {"data": None, "ts": 0.0}


def invalidate_cache() -> None:
    _cache["data"] = None
    _cache["ts"] = 0.0


def _entity_to_json_item(row: OntologyEntity) -> Dict[str, Any]:
    # entity_id is stored as TEXT for all entity types, but surrogate_tiers'
    # "id" is an integer in the original ontology JSON (0-3) - cast back so
    # GET /ontology stays byte-for-byte equivalent to the old file-based
    # response.
    entity_id: Any = int(row.entity_id) if row.entity_type == "surrogate_tier" else row.entity_id
    item = {"id": entity_id, "label": row.label, "description": row.description}
    item.update(row.properties or {})
    return item


def get_full_ontology(db: Session) -> Dict[str, Any]:
    if _cache["data"] is not None and (time.time() - _cache["ts"]) < _CACHE_TTL_S:
        return _cache["data"]

    rows = (
        db.query(OntologyEntity)
        .filter(OntologyEntity.status == "active")
        .order_by(OntologyEntity.entity_type, OntologyEntity.entity_id)
        .all()
    )

    grouped: Dict[str, List[Dict[str, Any]]] = {json_key: [] for json_key in ENTITY_TYPE_TO_JSON_KEY.values()}
    for row in rows:
        json_key = ENTITY_TYPE_TO_JSON_KEY.get(row.entity_type)
        if json_key is not None:
            grouped[json_key].append(_entity_to_json_item(row))

    data = {"schema": ONTOLOGY_SCHEMA, "version": ONTOLOGY_VERSION, **grouped}
    _cache["data"] = data
    _cache["ts"] = time.time()
    return data


def _check_entity_type(entity_type: str) -> None:
    if entity_type not in ENTITY_TYPES:
        http_error(404, "UNKNOWN_ENTITY_TYPE", f"'{entity_type}' is not a valid entity_type",
                   {"valid_entity_types": list(ENTITY_TYPES)})


def list_entities(db: Session, entity_type: str) -> List[OntologyEntity]:
    _check_entity_type(entity_type)
    return (
        db.query(OntologyEntity)
        .filter(OntologyEntity.entity_type == entity_type, OntologyEntity.status == "active")
        .order_by(OntologyEntity.entity_id)
        .all()
    )


def get_entity(db: Session, entity_type: str, entity_id: str) -> OntologyEntity:
    _check_entity_type(entity_type)
    row = (
        db.query(OntologyEntity)
        .filter(OntologyEntity.entity_type == entity_type, OntologyEntity.entity_id == entity_id)
        .first()
    )
    if not row:
        http_error(404, "ENTITY_NOT_FOUND", f"{entity_type}/{entity_id} not found")
    return row


def create_entity(db: Session, entity_type: str, payload: OntologyEntityIn) -> OntologyEntity:
    _check_entity_type(entity_type)
    existing = (
        db.query(OntologyEntity)
        .filter(OntologyEntity.entity_type == entity_type, OntologyEntity.entity_id == payload.entity_id)
        .first()
    )
    if existing:
        http_error(409, "ENTITY_ALREADY_EXISTS", f"{entity_type}/{payload.entity_id} already exists")

    row = OntologyEntity(
        entity_type=entity_type,
        entity_id=payload.entity_id,
        label=payload.label,
        description=payload.description,
        properties=payload.properties,
        status=payload.status,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    invalidate_cache()
    return row


def update_entity(db: Session, entity_type: str, entity_id: str, payload: OntologyEntityUpdate) -> OntologyEntity:
    row = get_entity(db, entity_type, entity_id)
    row.label = payload.label
    row.description = payload.description
    row.properties = payload.properties
    row.status = payload.status
    row.version += 1
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    invalidate_cache()
    return row


def deprecate_entity(db: Session, entity_type: str, entity_id: str) -> OntologyEntity:
    row = get_entity(db, entity_type, entity_id)
    row.status = "deprecated"
    row.updated_at = datetime.utcnow()
    db.commit()
    db.refresh(row)
    invalidate_cache()
    return row


def record_usage(db: Session, scenario_id: str, entity_type: str, entity_id: str, role: str) -> None:
    db.add(ScenarioEntityUsage(scenario_id=scenario_id, entity_type=entity_type, entity_id=entity_id, role=role))
    db.commit()


def get_usage(db: Session, entity_type: str, entity_id: str) -> Dict[str, Any]:
    count = (
        db.query(func.count(ScenarioEntityUsage.id))
        .filter(ScenarioEntityUsage.entity_type == entity_type, ScenarioEntityUsage.entity_id == entity_id)
        .scalar()
    )
    recent = (
        db.query(ScenarioEntityUsage.scenario_id)
        .filter(ScenarioEntityUsage.entity_type == entity_type, ScenarioEntityUsage.entity_id == entity_id)
        .order_by(ScenarioEntityUsage.created_at.desc())
        .limit(5)
        .all()
    )
    return {
        "entity_type": entity_type,
        "entity_id": entity_id,
        "usage_count": count or 0,
        "recent_scenarios": [r[0] for r in recent],
    }
