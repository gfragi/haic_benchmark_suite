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
    # schema_id of the SurveyQuestionSet attached to this config's public survey link,
    # so the link keeps pointing at the exact question set it was built with rather
    # than whatever happens to be "latest" for the pilot_tag at link-open time.
    schema_id = Column(String, nullable=True)


    # Relationship to associate with logs
    logs = relationship("LogEntry", back_populates="configuration")
    # passive_deletes=True: results.configuration_id is NOT NULL with an
    # ON DELETE CASCADE FK at the DB level. Without this, SQLAlchemy's default
    # ORM-level cascade tries to UPDATE results SET configuration_id=NULL
    # before deleting the parent, which violates the NOT NULL constraint for
    # any configuration that actually has results rows. This tells the ORM to
    # trust the DB's own cascade instead of managing the FK itself.
    results = relationship("EvaluationResult", back_populates="configuration", passive_deletes=True)
