"""
Pull-based log ingestion: periodically checks a registered source for new
session logs, instead of requiring a manual upload via the UI for every
batch. Two source types:

  "http_endpoint": GET <endpoint_url>?since=<ISO8601, omitted on first poll>,
    optional `Authorization: <auth_header>` header. Response: the same
    shapes /logs/upload already accepts - {"logs": [...]}, a bare list, or
    a single session dict. Empty/absent means "nothing new", not an error.

  "minio_bucket": lists <minio_bucket>/<minio_prefix> on the same consortium
    MinIO this backend already authenticates to (via get_minio_client()),
    picks up any .json object (not .derived.json) modified since the last
    successful poll, and ingests it. No separate credentials needed - most
    partners are on the shared instance with the benchmarking-suite service
    account already granted read access to their bucket.

Both reuse LogService.process_uploaded_log() for actual ingestion, so
polled logs go through the exact same validation/storage/evaluation-trigger
path as a manual upload - no separate parsing logic to keep in sync.
"""
from __future__ import annotations
import json
import logging
from datetime import datetime

import requests
from sqlalchemy.orm import Session

from app.models.polled_log_source import PolledLogSource
from app.services.log_service import LogService
from app.utils.minio_utils import get_minio_client

logger = logging.getLogger(__name__)
log_service = LogService()

POLL_TIMEOUT_S = 15


def _poll_http_endpoint(db: Session, source: PolledLogSource, now: datetime) -> None:
    params = {}
    if source.last_success_at:
        params["since"] = source.last_success_at.isoformat()

    headers = {}
    if source.auth_header:
        headers["Authorization"] = source.auth_header

    resp = requests.get(source.endpoint_url, params=params, headers=headers, timeout=POLL_TIMEOUT_S)
    resp.raise_for_status()
    raw_bytes = resp.content
    payload = resp.json()

    # Mirrors /logs/upload's own pre-processing exactly: unwrap {"logs":
    # [...]} before handing off, so both entry points behave identically.
    if isinstance(payload, dict) and isinstance(payload.get("logs"), list):
        payload = payload["logs"]

    if not payload:
        return  # nothing new - a normal, non-error outcome of a poll

    stem = f"polled-{now.strftime('%Y%m%dT%H%M%S')}"
    log_service.process_uploaded_log(source.configuration_id, payload, stem, raw_bytes, db)


def _poll_minio_bucket(db: Session, source: PolledLogSource, now: datetime) -> None:
    client = get_minio_client()
    objects = client.list_objects(source.minio_bucket, prefix=source.minio_prefix or "", recursive=True)

    new_sessions = []
    for obj in objects:
        name = obj.object_name
        if not name.endswith(".json") or name.endswith(".derived.json"):
            continue
        if source.last_success_at and obj.last_modified:
            # MinIO returns last_modified as a timezone-aware datetime;
            # last_success_at is stored naive-UTC (see poll_source) - compare
            # on naive UTC to avoid a naive/aware TypeError.
            if obj.last_modified.replace(tzinfo=None) <= source.last_success_at:
                continue

        resp = client.get_object(source.minio_bucket, name)
        try:
            raw = resp.read()
        finally:
            resp.close()
            resp.release_conn()

        parsed = json.loads(raw.decode("utf-8"))
        entries = parsed.get("logs") if isinstance(parsed, dict) else parsed
        if isinstance(entries, list):
            new_sessions.extend(entries)
        elif isinstance(parsed, dict):
            new_sessions.append(parsed)

    if not new_sessions:
        return  # nothing new since last poll

    stem = f"polled-{now.strftime('%Y%m%dT%H%M%S')}"
    raw_bytes = json.dumps({"logs": new_sessions}).encode("utf-8")
    log_service.process_uploaded_log(source.configuration_id, new_sessions, stem, raw_bytes, db)


def poll_source(db: Session, source: PolledLogSource) -> None:
    """Poll a single registered source once, ingesting anything new."""
    now = datetime.utcnow()
    source.last_polled_at = now

    try:
        if source.source_type == "minio_bucket":
            _poll_minio_bucket(db, source, now)
        else:
            _poll_http_endpoint(db, source, now)
        source.last_success_at = now
        source.last_error = None
    except Exception as e:
        source.last_error = str(e)[:2000]
        target = source.minio_bucket if source.source_type == "minio_bucket" else source.endpoint_url
        logger.warning("Poll failed for source %s (%s): %s", source.id, target, repr(e))

    db.add(source)
    db.commit()


def poll_due_sources(db: Session) -> int:
    """Poll every active source whose interval has elapsed. Returns count polled."""
    now = datetime.utcnow()
    sources = db.query(PolledLogSource).filter(PolledLogSource.is_active.is_(True)).all()
    polled = 0
    for source in sources:
        if source.last_polled_at is not None:
            elapsed = (now - source.last_polled_at).total_seconds()
            if elapsed < source.poll_interval_seconds:
                continue
        poll_source(db, source)
        polled += 1
    return polled
