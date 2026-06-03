from __future__ import annotations
from sqlalchemy.orm import Session
from app.models import EvaluationConfig
from app.models.logs import LogEntry
from datetime import datetime, timedelta
from pathlib import Path
import os, json, glob, random
from app.utils.minio_utils import get_minio_client, MINIO_BUCKET


def get_config_by_id(configuration_id: int, db: Session):
    return db.query(EvaluationConfig).filter(EvaluationConfig.id == configuration_id).first()


def save_log_entry(log_entry: LogEntry, db: Session):
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry



def random_date(start: datetime, end: datetime) -> datetime:
    """Generate a random datetime between `start` and `end`."""
    delta = end - start
    random_seconds = random.randint(0, int(delta.total_seconds()))
    return start + timedelta(seconds=random_seconds)


def _data_root() -> Path:
    return Path(os.getenv("ARTIFACTS_ROOT", "storage")).resolve()

def _find_latest_json(root: Path, rel_globs: list[str]) -> Path | None:
    candidates: list[Path] = []
    for pat in rel_globs:
        candidates += [Path(p) for p in glob.glob(str(root / pat))]
    if not candidates:
        return None
    candidates.sort(key=lambda p: p.stat().st_mtime, reverse=True)
    return candidates[0]

def _load_json_file(p: Path) -> dict:
    with p.open("r", encoding="utf-8") as f:
        return json.load(f)

# ---- MinIO helpers (using your Keycloak-auth MinIO client) ----
def _minio_list_candidates(config_id: int) -> list:
    """
    Return keys under {config_id}/ that look like merged event logs.
    Prefers 'uploads/events.all*.json' then any 'events*.json'.
    """
    client = get_minio_client()
    pref = f"{config_id}/"
    keys = []
    for obj in client.list_objects(MINIO_BUCKET, prefix=pref, recursive=True):
        k = obj.object_name
        if not k.endswith(".json"): 
            continue
        # prefer merged/all files
        if "events" in k:
            keys.append((k, obj.last_modified))
    # sort by last_modified (newest last)
    keys.sort(key=lambda t: t[1])
    return [k for k, _ in keys]

def _minio_get_json(key: str) -> dict:
    client = get_minio_client()
    resp = client.get_object(MINIO_BUCKET, key)
    try:
        return json.loads(resp.read().decode("utf-8"))
    finally:
        resp.close()
        resp.release_conn()

def _minio_list_any_json(config_id: int) -> list[str]:
    client = get_minio_client()
    pref = f"{config_id}/"
    keys = []
    for obj in client.list_objects(MINIO_BUCKET, prefix=pref, recursive=True):
        if obj.object_name.endswith(".json"):
            keys.append((obj.object_name, obj.last_modified))
    keys.sort(key=lambda t: t[1])
    return [k for k,_ in keys]

def _sniff_is_log_root(obj: dict) -> bool:
    # Accept {"logs":[...]} or a single-session {"decisions":[...]} (wrap later)
    if isinstance(obj, dict):
        if isinstance(obj.get("logs"), list): return True
        if isinstance(obj.get("decisions"), list): return True
    return False

def load_merged_log_for_config(configuration_id: int, db: Session) -> dict:
    """
    Load merged events JSON for a configuration, trying in order:
      1) Local file at storage/{id}/uploads/events.all*.json (or events*.json)
      2) MinIO object named by a recorded 'source_log_path' (if present)
      3) MinIO scan under {id}/ for the newest events*.json
    """
    # 1) Local filesystem
    root = _data_root()
    p = _find_latest_json(root, [
        f"{configuration_id}/uploads/events.all*.json",
        f"{configuration_id}/uploads/events*.json",
        f"{configuration_id}/events.all*.json",
        f"{configuration_id}/events*.json",
    ])
    if p and p.exists():
        return _load_json_file(p)

    for key in reversed(_minio_list_any_json(configuration_id)):
        try:
            obj = _minio_get_json(key)
            if _sniff_is_log_root(obj):
                # normalize single-session to multi-session root
                if "logs" not in obj and "decisions" in obj:
                    obj = {"logs":[obj], "extras":{}}
                return obj
        except Exception:
            continue
    raise FileNotFoundError(f"No parsable log JSON for configuration {configuration_id}.")