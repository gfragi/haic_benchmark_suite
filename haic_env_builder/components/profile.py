# haic_env_builder/components/profile.py
from __future__ import annotations
from typing import Any, Dict, Optional

class Profile:
    def __init__(
        self,
        profile_id: Optional[str] = None,
        role: Optional[str] = None,
        skill_level: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        **kwargs: Any,  # swallow unknown keys
    ) -> None:
        self.profile_id = profile_id
        self.role = role
        self.skill_level = skill_level
        self.metadata = dict(metadata) if metadata else {}
        self.extra: Dict[str, Any] = dict(kwargs)

    def __repr__(self) -> str:
        return f"Profile(id={self.profile_id!r}, role={self.role!r})"

    def to_dict(self) -> Dict[str, Any]:
        out = {
            "profile_id": self.profile_id,
            "role": self.role,
            "skill_level": self.skill_level,
            "metadata": self.metadata or {},
        }
        if self.extra:
            out["extra"] = self.extra
        return out
