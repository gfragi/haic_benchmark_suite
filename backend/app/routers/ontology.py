from typing import Any, Dict, List

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.ontology import (
    ENTITY_TYPES,
    OntologyDeleteResponse,
    OntologyEntityIn,
    OntologyEntityOut,
    OntologyEntityUpdate,
    OntologyResponse,
    OntologyUsageResponse,
)
from app.services import ontology_service
from app.utils.database import get_db

router = APIRouter()


def _load_ontology(db: Session) -> Dict[str, Any]:
    """Assembled from ontology_entities (DB-backed, 30s cache) - see
    app.services.ontology_service.get_full_ontology(). Kept as a
    module-level function since app.routers.simulator imports it directly."""
    return ontology_service.get_full_ontology(db)


def _to_out(row) -> OntologyEntityOut:
    return OntologyEntityOut(
        id=row.entity_id, label=row.label, description=row.description,
        status=row.status, properties=row.properties, version=row.version,
    )


@router.get("", response_model=OntologyResponse, summary="Full HAIC ontology (domains, action types, personas, metrics, templates)")
def get_ontology(db: Session = Depends(get_db)):
    return _load_ontology(db)


@router.get("/templates", response_model=List[Dict[str, Any]], summary="Scenario templates only")
def get_templates(db: Session = Depends(get_db)):
    return _load_ontology(db).get("templates", [])


@router.get("/{entity_type}", response_model=List[OntologyEntityOut], summary="List active entities of one type")
def list_entities(entity_type: str, db: Session = Depends(get_db)):
    rows = ontology_service.list_entities(db, entity_type)
    return [_to_out(r) for r in rows]


@router.get("/{entity_type}/{entity_id}/usage", response_model=OntologyUsageResponse, summary="Usage stats for one entity")
def get_entity_usage(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    return ontology_service.get_usage(db, entity_type, entity_id)


@router.get("/{entity_type}/{entity_id}", response_model=OntologyEntityOut, summary="Get one entity")
def get_entity(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    row = ontology_service.get_entity(db, entity_type, entity_id)
    return _to_out(row)


@router.post("/{entity_type}", response_model=OntologyEntityOut, status_code=201, summary="Create an entity")
def create_entity(entity_type: str, payload: OntologyEntityIn, db: Session = Depends(get_db)):
    row = ontology_service.create_entity(db, entity_type, payload)
    return _to_out(row)


@router.put("/{entity_type}/{entity_id}", response_model=OntologyEntityOut, summary="Update an entity")
def update_entity(entity_type: str, entity_id: str, payload: OntologyEntityUpdate, db: Session = Depends(get_db)):
    row = ontology_service.update_entity(db, entity_type, entity_id, payload)
    return _to_out(row)


@router.delete("/{entity_type}/{entity_id}", response_model=OntologyDeleteResponse, summary="Deprecate an entity (soft delete)")
def delete_entity(entity_type: str, entity_id: str, db: Session = Depends(get_db)):
    ontology_service.deprecate_entity(db, entity_type, entity_id)
    return OntologyDeleteResponse(message="Entity deprecated", entity_id=entity_id)
