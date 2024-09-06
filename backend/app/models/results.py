import datetime
from sqlalchemy import Column, DateTime, Float, Integer, ForeignKey, String
from sqlalchemy.orm import relationship
from app.utils.database import Base


class MetricGroup(Base):
    __tablename__ = 'metric_groups'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    # Relationship with Metric
    metrics = relationship("Metric", back_populates="group")


class Metric(Base):
    __tablename__ = 'metrics'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(String, nullable=True)

    # Relationship with MetricGroup
    group_id = Column(Integer, ForeignKey('metric_groups.id'))
    group = relationship("MetricGroup", back_populates="metrics")



class EvaluationResult(Base):
    __tablename__ = "results"

    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id', ondelete='CASCADE'), nullable=False)

    # Date of the evaluation
    evaluation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)

    # Path to the JSON result file stored in MinIO or other storage
    result_minio_path = Column(String, nullable=False)

    # Relationships
    configuration = relationship("EvaluationConfig", back_populates="results")
