import logging
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from src.application.services.chat_service import ChatService
from src.api.dependencies import get_chat_service_dependency
from src.application.services.chat_service import ChatProcessingError

logger = logging.getLogger(__name__)
api_router = APIRouter()


class ChatRequest(BaseModel):
    userId: str
    prompt: str

class ChatResponse(BaseModel):
    id: str
    userId: str
    prompt: str
    response: str
    model: str
    timestamp: str


## API Endpoints
@api_router.post("/v1/chat", response_model=ChatResponse)
async def chat(
    chat_request: ChatRequest,
    chat_service: ChatService = Depends(get_chat_service_dependency)
):
    """
    Handles chat requests, processes them using the ChatService, and returns a ChatResponse.
    """
    try:
        # Call the application service's chat method
        chat_interaction = await chat_service.chat(chat_request.prompt, chat_request.userId)

        # Construct the response model
        chat_response = ChatResponse(
            id=chat_interaction.id,
            userId=chat_interaction.userId,
            prompt=chat_request.prompt,
            response=chat_interaction.response,
            model=chat_interaction.model,
            timestamp=chat_interaction.timestamp.isoformat()
        )
        return chat_response
    except ChatProcessingError as e:
        logger.error(f"API Error: Chat processing failed for user {chat_request.userId}. Details: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An unexpected error happening while processing the chat request."
        ) from e
