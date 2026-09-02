import uuid
from datetime import datetime

from sqlalchemy import Column, DateTime, Integer, String, UniqueConstraint, Index
from sqlalchemy.dialects.postgresql import JSONB, UUID

from app.utils.database import Base


def _uuid():
    return uuid.uuid4()


class OntologyEntity(Base):
    __tablename__ = "ontology_entities"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    label = Column(String, nullable=False)
    description = Column(String, nullable=True)
    properties = Column(JSONB, nullable=False, default=dict)
    status = Column(String, nullable=False, default="active")
    created_by = Column(String, nullable=False, default="system")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    version = Column(Integer, nullable=False, default=1)

    __table_args__ = (
        UniqueConstraint("entity_type", "entity_id", name="uq_ontology_entities_type_id"),
    )


class ScenarioEntityUsage(Base):
    __tablename__ = "scenario_entity_usage"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    scenario_id = Column(String, nullable=False)
    entity_type = Column(String, nullable=False)
    entity_id = Column(String, nullable=False)
    role = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)

    __table_args__ = (
        Index("ix_scenario_entity_usage_type_id", "entity_type", "entity_id"),
    )
