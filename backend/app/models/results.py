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


class EvaluationResultMetric(Base):
    __tablename__ = 'evaluation_result_metrics'
    id = Column(Integer, primary_key=True, index=True)

    # Foreign keys for association
    result_id = Column(Integer, ForeignKey('evaluation_results.id', ondelete='CASCADE'), nullable=False)
    metric_id = Column(Integer, ForeignKey('metrics.id'), nullable=False)

    value = Column(Float, nullable=True)  # Value for the particular metric

    # Establish relationships
    result = relationship("EvaluationResult", back_populates="metrics")
    metric = relationship("Metric")


class EvaluationResult(Base):
    __tablename__ = "evaluation_results"

    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey('configurations.id', ondelete='CASCADE'), nullable=False)

    # Date of the evaluation
    evaluation_date = Column(DateTime, default=datetime.datetime.utcnow, nullable=False)
    result_minio_path = Column(String, nullable=True)


    # Relationships
    configuration = relationship("EvaluationConfig", back_populates="evaluation_results")
    metrics = relationship("EvaluationResultMetric", back_populates="result", cascade="all, delete-orphan")
