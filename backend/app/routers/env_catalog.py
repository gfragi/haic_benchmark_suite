
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List
import json, hashlib, datetime, os

router = APIRouter()

# ---- locate configs (package first, then env/volume) ----
def _pkg_configs_root():
    try:
        from importlib import resources
        return resources.files("haic_sim_mvp").joinpath("configs")  # Traversable
    except Exception:
        return None

def _fs_configs_root():
    root = os.getenv("HAIC_CONFIG_DIR")  # e.g. /data/haic_configs (mounted)
    return root

PKG_ROOT = _pkg_configs_root()
FS_ROOT = _fs_configs_root()

# ---- helpers using Traversable OR filesystem ----
def _iter_env_files():
    # Prefer packaged resources
    if PKG_ROOT is not None:
        for entry in PKG_ROOT.iterdir():
            if entry.is_file() and entry.name.endswith(".json"):
                yield ("pkg", entry)  # (kind, handle)
        return
    # Fallback to filesystem directory from env var
    if FS_ROOT and os.path.isdir(FS_ROOT):
        for name in sorted(os.listdir(FS_ROOT)):
            if name.endswith(".json"):
                yield ("fs", os.path.join(FS_ROOT, name))

def _read_bytes(kind, handle):
    if kind == "pkg":
        return handle.read_bytes()        # Traversable method
    return open(handle, "rb").read()      # filesystem path

def _read_json(kind, handle):
    data = _read_bytes(kind, handle)
    return json.loads(data)

def _mtime_iso(kind, handle):
    if kind == "pkg":
        # importlib.resources Traversable doesn’t expose mtime; use now
        return datetime.datetime.utcnow().isoformat() + "Z"
    ts = os.path.getmtime(handle)
    return datetime.datetime.fromtimestamp(ts).isoformat()

def _file_etag(kind, handle):
    h = hashlib.sha256()
    h.update(_read_bytes(kind, handle))
    return h.hexdigest()[:16]

def _env_internal_id(doc: Dict[str, Any]) -> str | None:
    return ((doc.get("environment") or {}).get("id"))

def _find_by_internal_id(target_id: str):
    for kind, handle in _iter_env_files():
        try:
            doc = _read_json(kind, handle)
        except Exception:
            continue
        if _env_internal_id(doc) == target_id:
            return (kind, handle, doc)
    return (None, None, None)

# ---- schema ----
class EnvMeta(BaseModel):
    id: str
    name: str
    sim_id: str | None = None
    domain: str | None = None
    task: str | None = None
    version: str | None = None
    updated_at: str | None = None

# ---- routes ----
@router.get("", response_model=List[EnvMeta])
def list_envs():
    metas: List[EnvMeta] = []
    for kind, handle in _iter_env_files():
        try:
            doc = _read_json(kind, handle)
        except Exception:
            continue
        env = (doc.get("environment") or {})
        attrs = env.get("attributes") or {}
        internal_id = _env_internal_id(doc)
        if not internal_id:
            continue
        metas.append(EnvMeta(
            id=internal_id,
            name=doc.get("name") or (getattr(handle, "name", str(handle)).replace("_", " ")).removesuffix(".json"),
            sim_id=doc.get("sim_id"),
            domain=attrs.get("domain"),
            task=attrs.get("task"),
            version=str(doc.get("version") or doc.get("_version") or ""),
            updated_at=_mtime_iso(kind, handle),
        ))
    return metas

@router.get("/{env_id}")
def get_env(env_id: str):
    kind, handle, doc = _find_by_internal_id(env_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"env with environment.id '{env_id}' not found")
    etag = _file_etag(kind, handle)
    return JSONResponse(doc, headers={"ETag": etag, "Cache-Control": "public, max-age=60"})


@router.get("/{env_id}/blocks")
def get_env_blocks(env_id: str):
    kind, handle, doc = _find_by_internal_id(env_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"env with environment.id '{env_id}' not found")
    agents = (doc.get("agents") or [])
    objects = (doc.get("objects") or [])
    def mk(kind, item):
        return {
            "kind": kind,
            "id": item.get("id"),
            "class": item.get("class"),
            "model": item.get("model"),
            "attributes": item.get("attributes") or {},
            "affordances": item.get("affordances") or [],
            "label": f"{kind}:{item.get('id')}"
        }
    blocks = [mk("agent", a) for a in agents] + [mk("object", o) for o in objects]
    env = doc.get("environment", {})
    meta = {
        "env_id": _env_internal_id(doc),
        "sim_id": doc.get("sim_id"),
        "domain": (env.get("attributes") or {}).get("domain"),
        "task": (env.get("attributes") or {}).get("task"),
        "version": doc.get("version") or doc.get("_version"),
    }
    return {"meta": meta, "blocks": blocks}
