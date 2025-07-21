from abc import ABC, abstractmethod

class LLMGenerationError(Exception):
    """Exception raised when LLM fails to generate a response."""
    pass


class LLMClient(ABC):
    @abstractmethod
    def generate_text(prompt, config):
        pass

    @abstractmethod
    def get_model_name(self) -> str:
        """
        Abstract method to get the name of the LLM model being used.
        """
        pass