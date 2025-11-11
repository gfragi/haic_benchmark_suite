from fastapi import APIRouter, HTTPException, Response
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from typing import List, Any, Dict
from pathlib import Path
import json, hashlib, datetime
from importlib import resources

def _config_dir() -> Path:
    # points inside the installed package dist-info location
    return Path(resources.files("haic_sim_mvp")).joinpath("configs")

router = APIRouter()

CONFIG_DIR = _config_dir()

# ---------- helpers ----------

def _iter_env_files():
    for p in sorted(CONFIG_DIR.glob("*.json")):
        if p.is_file():
            yield p

def _read_json(p: Path) -> Dict[str, Any]:
    return json.loads(p.read_text())

def _env_internal_id(doc: Dict[str, Any]) -> str | None:
    env = doc.get("environment") or {}
    return env.get("id")

def _file_etag(p: Path) -> str:
    h = hashlib.sha256()
    h.update(p.read_bytes())
    return h.hexdigest()[:16]

def _find_by_internal_id(target_id: str):
    """
    Returns (path, doc) for the first file whose environment.id == target_id.
    """
    for p in _iter_env_files():
        try:
            doc = _read_json(p)
        except Exception:
            continue
        if _env_internal_id(doc) == target_id:
            return p, doc
    return None, None

# ---------- schemas ----------

class EnvMeta(BaseModel):
    id: str                # environment.id
    name: str              # friendly name (fallback to file stem)
    sim_id: str | None = None
    domain: str | None = None
    task: str | None = None
    version: str | None = None
    updated_at: str | None = None

# ---------- endpoints ----------

@router.get("", response_model=List[EnvMeta])
def list_envs():
    metas: List[EnvMeta] = []
    for p in _iter_env_files():
        try:
            doc = _read_json(p)
        except Exception:
            continue
        env = (doc.get("environment") or {})
        attrs = env.get("attributes") or {}
        internal_id = _env_internal_id(doc)
        if not internal_id:
            # skip files missing environment.id
            continue
        metas.append(EnvMeta(
            id=internal_id,
            name=doc.get("name") or p.stem.replace("_", " "),
            sim_id=doc.get("sim_id"),
            domain=attrs.get("domain"),
            task=attrs.get("task"),
            version=str(doc.get("version") or doc.get("_version") or ""),
            updated_at=datetime.datetime.fromtimestamp(p.stat().st_mtime).isoformat()
        ))
    return metas

@router.get("/{env_id}")
def get_env(env_id: str):
    p, doc = _find_by_internal_id(env_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"env with environment.id '{env_id}' not found")
    etag = _file_etag(p)
    return JSONResponse(doc, headers={"ETag": etag, "Cache-Control": "public, max-age=60"})



@router.get("/{env_id}/blocks")
def get_env_blocks(env_id: str):
    p, doc = _find_by_internal_id(env_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"env with environment.id '{env_id}' not found")
    agents = (doc.get("agents") or [])
    objects = (doc.get("objects") or [])

    def mk_block(kind: str, item: Dict[str, Any]) -> Dict[str, Any]:
        return {
            "kind": kind,
            "id": item.get("id"),
            "class": item.get("class"),
            "model": item.get("model"),
            "attributes": item.get("attributes") or {},
            "affordances": item.get("affordances") or [],
            "label": f"{kind}:{item.get('id')}"
        }

    blocks = [mk_block("agent", a) for a in agents] + [mk_block("object", o) for o in objects]
    env = doc.get("environment", {})
    meta = {
        "env_id": _env_internal_id(doc),
        "sim_id": doc.get("sim_id"),
        "domain": (env.get("attributes") or {}).get("domain"),
        "task": (env.get("attributes") or {}).get("task"),
        "version": doc.get("version") or doc.get("_version")
    }
    return {"meta": meta, "blocks": blocks}
