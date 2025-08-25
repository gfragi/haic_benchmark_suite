
## Defines base interfaces for all core elements.

from abc import ABC, abstractmethod

class Component(ABC):
    @abstractmethod
    def to_dict(self):
        pass
