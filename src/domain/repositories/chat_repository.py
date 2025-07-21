from abc import ABC, abstractmethod
from src.domain.entities.chat_interaction import ChatInteraction


class ChatSaveError(Exception):
    """Exception raised when a chat interaction cannot be saved."""
    pass


class ChatRepository(ABC):
    @abstractmethod
    async def create_chat_interaction(self, chat_interaction: ChatInteraction) -> ChatInteraction:
        """
        Abstract method to create a new chat interaction.
        """
        pass
