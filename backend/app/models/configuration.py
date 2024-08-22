from sqlalchemy import Column, ForeignKey, String, Integer, Table, JSON
from sqlalchemy.orm import relationship
from app.utils.database import Base


config_metric_association = Table(
    'config_metric_association',
    Base.metadata,
    Column('configuration_id', Integer, ForeignKey('configurations.id', ondelete='CASCADE')),
    Column('metric_id', Integer, ForeignKey('metrics.id'))
)


class EvaluationConfig(Base):
    __tablename__ = "configurations"

    id = Column(Integer, primary_key=True, index=True)
    application_name = Column(String, index=True)
    ai_model_name = Column(String)
    description = Column(String, nullable=True)
    metrics = Column(JSON)
    evaluation_date = Column(String, nullable=True)
    config_type = Column(String, nullable=True)

    metrics = relationship(
        "Metric",
        secondary=config_metric_association,
        back_populates="configurations"
    )

    # Relationship to associate with logs
    logs = relationship("LogEntry", back_populates="configuration")

class Metric(Base):
    __tablename__ = "metrics"

    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String, index=True)

    configurations = relationship(
        "EvaluationConfig",
        secondary=config_metric_association,
        back_populates="metrics"
    )
