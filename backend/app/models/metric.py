import uuid
from sqlalchemy import Column, Text, TIMESTAMP
from sqlalchemy.dialects.postgresql import UUID, JSONB
from datetime import datetime
from app.utils.database import Base

class MetricDefinition(Base):
    __tablename__ = "metric_definitions"

    metric_id = Column(Text, primary_key=True, index=True)
    display_name = Column(Text, nullable=False)
    description = Column(Text, nullable=False)
    formula_tex = Column(Text, nullable=False)
    required_fields = Column(JSONB, nullable=False)    # e.g. ["latency_ms","num_errors",...]
    example_payload = Column(JSONB, nullable=True)      # e.g. {"latency_ms": [120, 230, 310]}
    created_at = Column(TIMESTAMP(timezone=True), default=datetime.utcnow, nullable=False)


# Purpose: Stores every supported metric. Each row holds:

# metric_id (e.g. "avg_latency")
# display_name (e.g. "Average Latency (ms)")
# description (a short English description)
# formula_tex (a LaTeX string or human‐readable formula)
# required_fields (JSONB array of strings, e.g. ["latency_ms"])
# example_payload (JSONB; an example snippet so the wizard can show sample JSON)