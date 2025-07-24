from .base import Component
from typing import List
import random

class Agent(Component):
    def __init__(self, name, capabilities, modality):
        self.name = name
        self.capabilities = capabilities
        self.modality = modality

    def act(self, task):
        if "classify" in self.capabilities:
            return f"classifying for task {task.name}"
        elif self.capabilities:
            return f"performing {random.choice(self.capabilities)}"
        return "idle"

    def to_dict(self):
        return {
            "name": self.name,
            "capabilities": self.capabilities,
            "modality": self.modality
        }