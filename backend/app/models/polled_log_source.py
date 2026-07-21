import datetime
from sqlalchemy import Column, String, Integer, ForeignKey, Boolean, DateTime, Text
from sqlalchemy.orm import relationship
from app.utils.database import Base


class PolledLogSource(Base):
    """
    A source we periodically poll for new session logs, as an alternative to
    requiring manual file uploads via the UI. Two kinds:

      - "http_endpoint": a partner-owned HTTP endpoint (endpoint_url,
        auth_header).
      - "minio_bucket": a bucket/prefix on the same consortium MinIO instance
        this backend already authenticates to (minio_bucket, minio_prefix) -
        most partners are on shared infra with the benchmarking-suite service
        account already granted read access to their bucket, so this needs no
        separate credentials at all.

    See app/services/log_polling_service.py for the poll contract and loop.
    """
    __tablename__ = "polled_log_sources"

    id = Column(Integer, primary_key=True, index=True)
    configuration_id = Column(Integer, ForeignKey("configurations.id", ondelete="CASCADE"), nullable=False)
    source_type = Column(String, nullable=False, default="http_endpoint")  # "http_endpoint" | "minio_bucket"

    # source_type == "http_endpoint"
    endpoint_url = Column(String, nullable=True)
    auth_header = Column(String, nullable=True)  # sent as-is as the Authorization header, e.g. "Bearer xyz"

    # source_type == "minio_bucket"
    minio_bucket = Column(String, nullable=True)
    minio_prefix = Column(String, nullable=True)

    poll_interval_seconds = Column(Integer, nullable=False, default=300)
    is_active = Column(Boolean, nullable=False, default=True)
    last_polled_at = Column(DateTime, nullable=True)
    last_success_at = Column(DateTime, nullable=True)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=datetime.datetime.utcnow)

    configuration = relationship("EvaluationConfig")
