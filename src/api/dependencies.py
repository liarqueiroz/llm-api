## Dependency Injection Functions
from fastapi import Depends
from pymongo.database import Database

from src.domain.repositories.chat_repository import ChatRepository
from src.domain.clients.llm_client import LLMClient
from src.application.services.chat_service import ChatService

from src.infrastructure.clients.gemini_client import GeminiClient 
from src.infrastructure.persistence.db_chat_repository import DatabaseChatRepository 
from src.infrastructure.persistence.database import get_database

def get_llm_client_dependency() -> LLMClient:
    """
    Dependency to get a concrete instance of LLMClient.
    """
    return GeminiClient()

def get_chat_repository_dependency(database: Database = Depends(get_database)) -> ChatRepository:
    """
    Dependency to get a concrete instance of ChatRepository.
    """
    return DatabaseChatRepository(database=database)

def get_chat_service_dependency(
    llm_client: LLMClient = Depends(get_llm_client_dependency),
    chat_repository: ChatRepository = Depends(get_chat_repository_dependency)
) -> ChatService:
    """
    Dependency to get an instance of ChatService, injecting its required dependencies.
    """
    return ChatService(llm_client=llm_client, chat_repository=chat_repository)