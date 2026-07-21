from typing import Optional, Literal
from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.orm import Session

from app.utils.database import get_db
from app.models.polled_log_source import PolledLogSource
from app.models.configuration import EvaluationConfig
from app.services.log_polling_service import poll_source

router = APIRouter()


class RegisterPolledSourceBody(BaseModel):
    source_type: Literal["http_endpoint", "minio_bucket"] = "http_endpoint"
    # source_type == "http_endpoint"
    endpoint_url: Optional[str] = None
    auth_header: Optional[str] = None
    # source_type == "minio_bucket"
    minio_bucket: Optional[str] = None
    minio_prefix: Optional[str] = None

    poll_interval_seconds: int = Field(default=300, ge=30)

    @model_validator(mode="after")
    def _check_required_fields(self):
        if self.source_type == "http_endpoint" and not self.endpoint_url:
            raise ValueError("endpoint_url is required for source_type=http_endpoint")
        if self.source_type == "minio_bucket" and not self.minio_bucket:
            raise ValueError("minio_bucket is required for source_type=minio_bucket")
        return self


def _serialize(s: PolledLogSource) -> dict:
    return {
        "id": s.id,
        "configuration_id": s.configuration_id,
        "source_type": s.source_type,
        "endpoint_url": s.endpoint_url,
        "minio_bucket": s.minio_bucket,
        "minio_prefix": s.minio_prefix,
        "poll_interval_seconds": s.poll_interval_seconds,
        "is_active": s.is_active,
        "last_polled_at": s.last_polled_at.isoformat() if s.last_polled_at else None,
        "last_success_at": s.last_success_at.isoformat() if s.last_success_at else None,
        "last_error": s.last_error,
    }


@router.post("/polled-sources", summary="Register a source (HTTP endpoint or MinIO bucket) to poll for new logs")
def register_polled_source(
    body: RegisterPolledSourceBody,
    configuration_id: int = Query(...),
    db: Session = Depends(get_db),
):
    config = db.get(EvaluationConfig, configuration_id)
    if not config:
        raise HTTPException(status_code=404, detail="Evaluation configuration not found.")

    source = PolledLogSource(
        configuration_id=configuration_id,
        source_type=body.source_type,
        endpoint_url=body.endpoint_url,
        auth_header=body.auth_header,
        minio_bucket=body.minio_bucket,
        minio_prefix=body.minio_prefix,
        poll_interval_seconds=body.poll_interval_seconds,
    )
    db.add(source)
    db.commit()
    db.refresh(source)
    return _serialize(source)


@router.get("/polled-sources", summary="List registered polling sources for a configuration")
def list_polled_sources(configuration_id: int = Query(...), db: Session = Depends(get_db)):
    sources = (
        db.query(PolledLogSource)
        .filter(PolledLogSource.configuration_id == configuration_id)
        .all()
    )
    return [_serialize(s) for s in sources]


@router.delete("/polled-sources/{source_id}", summary="Stop polling a registered source")
def delete_polled_source(source_id: int, db: Session = Depends(get_db)):
    source = db.get(PolledLogSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Not found.")
    db.delete(source)
    db.commit()
    return {"detail": "Deleted."}


@router.post("/polled-sources/{source_id}/poll-now", summary="Trigger an immediate poll (doesn't wait for the interval)")
def poll_now(source_id: int, db: Session = Depends(get_db)):
    source = db.get(PolledLogSource, source_id)
    if not source:
        raise HTTPException(status_code=404, detail="Not found.")
    poll_source(db, source)
    db.refresh(source)
    return _serialize(source)
