import uuid
from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import relationship

from app.utils.database import Base


def _uuid():
    return uuid.uuid4()


class ExperimentRun(Base):
    __tablename__ = "experiment_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    domain = Column(String, nullable=False)
    source_model_id = Column(String, nullable=False)
    n_sessions = Column(Integer, nullable=False, default=20)
    n_items = Column(Integer, nullable=False, default=164)
    smooth_epsilon = Column(Float, nullable=False, default=0.005)
    # Adds 'cancelled' beyond the task's literal status list, since
    # DELETE /experiments/{id} is specced to soft-delete by setting
    # status='cancelled' - that value has to be a legal state.
    status = Column(String, nullable=False, default="created")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    sealed_at = Column(DateTime(timezone=True), nullable=True)
    revealed_at = Column(DateTime(timezone=True), nullable=True)

    models = relationship("ExperimentModel", cascade="all, delete-orphan", passive_deletes=True)
    results = relationship("ExperimentResult", cascade="all, delete-orphan", passive_deletes=True)


class ExperimentModel(Base):
    __tablename__ = "experiment_models"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False)
    model_id = Column(String, nullable=False)
    model_label = Column(String, nullable=True)
    role = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    log_file_path = Column(String, nullable=True)
    fitted_model_path = Column(String, nullable=True)
    ai_action_frequency = Column(JSONB, nullable=True)
    status = Column(String, nullable=False, default="registered")
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)


class ExperimentResult(Base):
    __tablename__ = "experiment_results"

    id = Column(UUID(as_uuid=True), primary_key=True, default=_uuid)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiment_runs.id", ondelete="CASCADE"), nullable=False)
    model_a_id = Column(String, nullable=False)
    model_b_id = Column(String, nullable=False)
    comparison_type = Column(String, nullable=False)

    pred_Tr = Column(Float, nullable=True)
    pred_Tr_std = Column(Float, nullable=True)
    pred_HCL = Column(Float, nullable=True)
    pred_HCL_std = Column(Float, nullable=True)
    pred_EL = Column(Float, nullable=True)
    pred_EL_std = Column(Float, nullable=True)
    pred_F = Column(Float, nullable=True)
    pred_F_std = Column(Float, nullable=True)

    real_Tr = Column(Float, nullable=True)
    real_HCL = Column(Float, nullable=True)
    real_EL = Column(Float, nullable=True)
    real_F = Column(Float, nullable=True)

    err_Tr_pct = Column(Float, nullable=True)
    err_HCL_pct = Column(Float, nullable=True)
    err_EL_pct = Column(Float, nullable=True)
    err_F_pct = Column(Float, nullable=True)

    S_cross = Column(Float, nullable=True)
    S_cross_per_action = Column(JSONB, nullable=True)

    h1_supported = Column(Boolean, nullable=True)
    h2_supported = Column(Boolean, nullable=True)
    h3_supported = Column(Boolean, nullable=True)

    notes = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), nullable=False, default=datetime.utcnow)
