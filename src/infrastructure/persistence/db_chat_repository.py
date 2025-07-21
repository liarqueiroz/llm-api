import logging

from src.domain.repositories.chat_repository import ChatRepository
from pymongo.database import Database
from pymongo.errors import PyMongoError
from src.domain.entities.chat_interaction import ChatInteraction
from src.domain.repositories.chat_repository import ChatSaveError


logger = logging.getLogger(__name__)


class DatabaseChatRepository(ChatRepository):
    def __init__(self, database: Database):
        self.collection = database["chat_interactions"]

    async def create_chat_interaction(self, chat_interaction: ChatInteraction) -> ChatInteraction:
        """
        Creates a new chat interaction in the database.
        """
        try:
            result = await self.collection.insert_one(chat_interaction.model_dump(by_alias=True, exclude_none=True))
        
            if not chat_interaction.id and result.inserted_id:
                logger.info(f"Chat interaction created with ID: {result.inserted_id}")
                return str(result.inserted_id)
        except PyMongoError as e:
            logger.error(f"Error creating chat interaction: {e}")
            raise ChatSaveError(f"Failed to save chat interaction to database: {e}")
