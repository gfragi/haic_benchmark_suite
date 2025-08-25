from .base import Component

class Task(Component):
    def __init__(self, name, description, parameters):
        self.name = name
        self.description = description
        self.parameters = parameters

    def to_dict(self):
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters
        }
