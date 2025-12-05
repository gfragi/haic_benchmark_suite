from datetime import datetime, timezone
import json, os, io, uuid
import logging
from typing import Dict, Any, List
from collections import defaultdict
from statistics import mean
from sqlalchemy.orm import Session

from app.models import LogEntry
from app.models.configuration import EvaluationConfig
from app.services.metrics_adapter import compute_from_log
from app.utils.minio_utils import get_minio_client, put_json
import re

logger = logging.getLogger(__name__)
MINIO_BUCKET = os.getenv("MINIO_BUCKET")

class LogService:
    def __init__(self):
        self.minio_client = get_minio_client()

    def _sanitize(self, s: str) -> str:
        if s is None:
            return "Unknown"
        s = re.sub(r"[^A-Za-z0-9._-]+", "_", str(s)).strip("_")
        return s or "Unknown"

    def _mean_map(self, dicts: List[Dict], key: str) -> Dict[str, Any]:
        items = [d.get(key) for d in dicts if isinstance(d, dict) and d.get(key) is not None]
        out = {}
        if items:
            keys = set().union(*(x.keys() for x in items if isinstance(x, dict)))
            for k in keys:
                vals = [x.get(k) for x in items if isinstance(x, dict) and isinstance(x.get(k), (int, float))]
                out[k] = mean(vals) if vals else None
        return out

    def process_uploaded_log(self, configuration_id: int, payload: Any, filename: str, raw_bytes: bytes, db: Session) -> Dict[str, Any]:
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        stem = (filename.rsplit(".", 1)[0] if filename and "." in filename
                else (filename or f"log-{uuid.uuid4().hex}"))

        # Store original upload once
        orig_name = f"{configuration_id}/uploads/{stem}.{ts}.json"
        try:
            self.minio_client.put_object(
                bucket_name=MINIO_BUCKET,
                object_name=orig_name,
                data=io.BytesIO(raw_bytes),
                length=len(raw_bytes),
                content_type="application/json",
            )
        except Exception as e:
            raise Exception(f"MinIO upload failed: {e}")

        results = {"original": orig_name, "derived_by_version": {}}

        def _write_derived(ver: str, derived: dict):
            derived_name = f"{configuration_id}/uploads/{stem}.{ts}.v{ver}.derived.json"
            enc = json.dumps(derived, ensure_ascii=False, indent=2).encode("utf-8")
            self.minio_client.put_object(
                MINIO_BUCKET, derived_name, io.BytesIO(enc), len(enc),
                content_type="application/json"
            )
            results["derived_by_version"][ver] = {"path": derived_name, "summary": derived}
            return derived_name

        try:
            if isinstance(payload, dict):
                # Single session
                ver = self._sanitize(payload.get("ai_model_version") or "Unknown")
                derived = compute_from_log(payload)
                _write_derived(ver, derived)

            elif isinstance(payload, list):
                # Group by ai_model_version
                groups = defaultdict(list)
                for p in payload:
                    if isinstance(p, dict):
                        ver = self._sanitize(p.get("ai_model_version") or "Unknown")
                        groups[ver].append(p)

                for ver, logs in groups.items():
                    derived_list = [compute_from_log(p) for p in logs]
                    derived = {
                        "by_metric": self._mean_map(derived_list, "by_metric"),
                        "by_pillar": self._mean_map(derived_list, "by_pillar"),
                        "interaction": self._mean_map(derived_list, "interaction"),
                        "count": len(logs),
                        "ai_model_version": ver,
                    }
                    _write_derived(ver, derived)
            else:
                raise ValueError("JSON must be an object or an array of objects")
        except Exception as e:
            raise Exception(f"Processing failed: {e}")

        # Update the config to point at the original upload (evaluation reads this)
        config = db.query(EvaluationConfig).get(configuration_id)
        if not config:
            raise ValueError("Evaluation configuration not found.")
        config.minio_path = orig_name
        db.add(config)
        db.commit()
        db.refresh(config)

        return results

    def register_log(self, log_data: Dict[str, Any], configuration_id: int, db: Session) -> Dict[str, Any]:
        # 0) Ensure configuration exists
        config = db.get(EvaluationConfig, configuration_id)
        if not config:
            raise ValueError("Evaluation configuration not found.")

        # 1) Per-session derived metrics
        derived = compute_from_log(log_data)

        # 2) Build deterministic names
        session_part = log_data.get("session_id") or "log"
        ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S")
        original_name = f"uploads/{session_part}.{ts}.json"
        derived_name = f"uploads/{session_part}.{ts}.derived.json"

        raw_path = f"{configuration_id}/{original_name}"
        derived_path = f"{configuration_id}/{derived_name}"

        # 3) Store original + derived in MinIO
        put_json(configuration_id, original_name, log_data)
        put_json(configuration_id, derived_name, derived)

        # 4) Create a Log row linked to this config
        log_row = LogEntry(
            configuration_id=configuration_id,
            session_id=session_part,
            raw_minio_path=raw_path,
            derived_minio_path=derived_path,
            status="ingested",
            created_at=datetime.now(timezone.utc),
        )
        db.add(log_row)
        db.commit()
        db.refresh(log_row)

        return {
            "detail": "Registered log.",
            "configuration_id": configuration_id,
            "log_id": log_row.id,
            "minio_paths": {
                "original": raw_path,
                "derived": derived_path,
            },
            "derived": derived,
        }
