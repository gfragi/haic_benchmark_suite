
from .base import Component

class Profile(Component):
    def __init__(self, id, skill_level, role):
        self.profile_id = id
        self.skill_level = skill_level
        self.role = role

    def to_dict(self):
        return {
            "id": self.profile_id,
            "skill_level": self.skill_level,
            "role": self.role
        }
