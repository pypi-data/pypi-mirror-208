from abc import ABC, abstractmethod


class Validate(ABC):
    @abstractmethod
    def execute(self):
        pass
