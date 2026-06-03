import datetime
from sqlalchemy import Column, DateTime, Float, ForeignKey, String, Integer, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base


class EvaluationConfig(Base):
    __tablename__ = "configurations"

    STATUS_PENDING = "pending"
    STATUS_RUNNING = "running"
    STATUS_COMPLETED = "completed"
    STATUS_FAILED = "failed"

    id = Column(Integer, primary_key=True, index=True)
    application_name = Column(String, index=True)
    ai_model_name = Column(String)
    ai_model_type = Column(String)
    description = Column(String, nullable=True)
    metrics = Column(JSON)  # Directly storing metrics as JSON
    evaluation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    config_type = Column(String, nullable=True)
    evaluation_status = Column(String,default=STATUS_PENDING)
    minio_path = Column(String, nullable=True)
    pilot_tag = Column(String, nullable=True)
    baseline_s = Column(Float, nullable=True)


    # Relationship to associate with logs
    logs = relationship("LogEntry", back_populates="configuration")
    results = relationship("EvaluationResult", back_populates="configuration")
