import hashlib
import json
from typing import Any, Dict

def compute_config_hash(cfg: Dict[str, Any]) -> str:
    """
    Produce a stable hash for the loaded YAML config dict. Ensures keys are sorted
    and non-ASCII preserved.
    """
    payload = json.dumps(cfg, sort_keys=True, ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()[:12]