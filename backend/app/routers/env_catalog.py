
from fastapi import APIRouter, HTTPException, Response, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Any, Dict, List
import json, hashlib, datetime, os, re

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
SAFE_FILENAME_RE = re.compile(r"[^A-Za-z0-9_.-]+")

# ---- helpers using Traversable OR filesystem ----
def _iter_env_files():
    # Filesystem configs are mutable and override packaged configs with the same environment.id.
    fs_root = _fs_configs_root()
    if fs_root and os.path.isdir(fs_root):
        for name in sorted(os.listdir(fs_root)):
            if name.endswith(".json"):
                yield ("fs", os.path.join(fs_root, name))

    if PKG_ROOT is not None:
        for entry in PKG_ROOT.iterdir():
            if entry.is_file() and entry.name.endswith(".json"):
                yield ("pkg", entry)  # (kind, handle)

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

def _handle_path(kind, handle) -> str | None:
    if kind == "fs":
        return handle
    try:
        return os.fspath(handle)
    except TypeError:
        return None

def _env_filename(env_id: str) -> str:
    safe_id = SAFE_FILENAME_RE.sub("_", env_id).strip("._")
    if not safe_id:
        raise HTTPException(status_code=400, detail="environment.id cannot be used as a filename")
    return f"{safe_id}.json"

def _write_root() -> str:
    fs_root = _fs_configs_root()
    if fs_root:
        os.makedirs(fs_root, exist_ok=True)
        return fs_root

    pkg_path = _handle_path("pkg", PKG_ROOT) if PKG_ROOT is not None else None
    if pkg_path and os.path.isdir(pkg_path) and os.access(pkg_path, os.W_OK):
        return pkg_path

    raise HTTPException(
        status_code=500,
        detail="HAIC_CONFIG_DIR is not set and packaged configs are not writable",
    )

def _validate_env_doc(doc: Dict[str, Any]) -> str:
    env_id = _env_internal_id(doc)
    if not env_id:
        raise HTTPException(status_code=400, detail="body must include environment.id")
    return env_id

def _write_env_doc(path: str, doc: Dict[str, Any]) -> None:
    tmp_path = f"{path}.tmp"
    try:
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(doc, f, indent=2, ensure_ascii=False)
            f.write("\n")
        os.replace(tmp_path, path)
    finally:
        if os.path.exists(tmp_path):
            os.remove(tmp_path)

def _mutable_path(kind, handle) -> str:
    path = _handle_path(kind, handle)
    if not path or not os.path.isfile(path) or not os.access(path, os.W_OK):
        raise HTTPException(
            status_code=409,
            detail="environment is packaged/read-only; set HAIC_CONFIG_DIR to replace or remove mutable configs",
        )
    return path

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
    seen_ids: set[str] = set()
    for kind, handle in _iter_env_files():
        try:
            doc = _read_json(kind, handle)
        except Exception:
            continue
        env = (doc.get("environment") or {})
        attrs = env.get("attributes") or {}
        internal_id = _env_internal_id(doc)
        if not internal_id or internal_id in seen_ids:
            continue
        seen_ids.add(internal_id)
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

@router.post("", status_code=status.HTTP_201_CREATED)
def add_env(doc: Dict[str, Any]):
    env_id = _validate_env_doc(doc)
    _, _, existing = _find_by_internal_id(env_id)
    if existing:
        raise HTTPException(status_code=409, detail=f"env with environment.id '{env_id}' already exists")

    path = os.path.join(_write_root(), _env_filename(env_id))
    _write_env_doc(path, doc)
    etag = hashlib.sha256(json.dumps(doc, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return JSONResponse(
        {"id": env_id},
        status_code=status.HTTP_201_CREATED,
        headers={"ETag": etag},
    )

@router.put("/{env_id}")
def replace_env(env_id: str, doc: Dict[str, Any]):
    body_env_id = _validate_env_doc(doc)
    if body_env_id != env_id:
        raise HTTPException(
            status_code=400,
            detail=f"body environment.id '{body_env_id}' does not match path env_id '{env_id}'",
        )

    kind, handle, existing = _find_by_internal_id(env_id)
    if not existing:
        raise HTTPException(status_code=404, detail=f"env with environment.id '{env_id}' not found")

    path = _mutable_path(kind, handle)
    _write_env_doc(path, doc)
    etag = hashlib.sha256(json.dumps(doc, sort_keys=True).encode("utf-8")).hexdigest()[:16]
    return JSONResponse({"id": env_id}, headers={"ETag": etag})

@router.delete("/{env_id}", status_code=status.HTTP_204_NO_CONTENT)
def remove_env(env_id: str):
    kind, handle, doc = _find_by_internal_id(env_id)
    if not doc:
        raise HTTPException(status_code=404, detail=f"env with environment.id '{env_id}' not found")

    os.remove(_mutable_path(kind, handle))
    return Response(status_code=status.HTTP_204_NO_CONTENT)

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
