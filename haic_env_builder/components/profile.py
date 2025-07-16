from .base import Component

class Profile(Component):
    def __init__(self, profile_id, skill_level, role):
        self.profile_id = profile_id
        self.skill_level = skill_level
        self.role = role

    def to_dict(self):
        return {
            "id": self.profile_id,
            "skill_level": self.skill_level,
            "role": self.role
        }
