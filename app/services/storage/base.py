from abc import ABC, abstractmethod

from app.models.result_models import ProcessingResult


class ResultWriter(ABC):
    @abstractmethod
    def save(self, result: ProcessingResult) -> str:
        """Persist a processed invoice result and return the saved path."""
        pass