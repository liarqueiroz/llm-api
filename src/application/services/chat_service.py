import logging

from datetime import datetime
from src.domain.clients.llm_client import LLMClient, LLMGenerationError
from src.domain.repositories.chat_repository import ChatRepository, ChatSaveError
from src.domain.entities.chat_interaction import ChatInteraction

logger = logging.getLogger(__name__)


class ChatProcessingError(Exception):
    """Exception raised when chat processing fails."""
    pass


class ChatService():
    def __init__(self, llm_client: LLMClient, chat_repository: ChatRepository):
        self.llm_client = llm_client
        self.chat_repository = chat_repository

    async def chat(self, prompt, user_id: str = None):
        try:
            logger.info(f"Processing new chat interaction")
            answer = self.llm_client.generate_text(prompt)

            chat_interaction = ChatInteraction(
                userId=user_id,
                prompt=prompt,
                response=answer,
                model=self.llm_client.get_model_name(),
                timestamp=datetime.now()
            )
            chat_interaction.id = await self.chat_repository.create_chat_interaction(
                chat_interaction
            )
            return chat_interaction
        except LLMGenerationError as e:
            logger.error(f"LLM generation failed for user {user_id}: {e}")
            raise ChatProcessingError(f"Failed to generate response due to LLM error.")
        except ChatSaveError as e:
            logger.error(f"Failed to save chat interaction for user {user_id}: {e}")
            raise ChatProcessingError(f"Failed to complete chat due to database error.")
        except Exception as e:
            logger.error(f"An unexpected error occurred during chat processing for user {user_id}: {e}")
            raise ChatProcessingError(f"An unexpected error occurred during chat processing: {e}") from e

