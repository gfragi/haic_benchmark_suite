
## Defines base interfaces for all core elements.
# haic_env_builder/components/base.py

from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def to_dict(self):
        pass
