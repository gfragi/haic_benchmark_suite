from .base import Component



class Agent(Component):
    def __init__(self, name, capabilities, modality):
        self.name = name
        self.capabilities = capabilities  # e.g., ['view', 'ask', 'act']
        self.modality = modality          # e.g., 'text', 'gui', 'multimodal'

    def to_dict(self):
        return {
            "name": self.name,
            "capabilities": self.capabilities,
            "modality": self.modality
        }