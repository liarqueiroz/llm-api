import pytest
from unittest.mock import AsyncMock, Mock
from datetime import datetime

from src.domain.clients.llm_client import LLMClient, LLMGenerationError
from src.domain.repositories.chat_repository import ChatRepository, ChatSaveError
from src.domain.entities.chat_interaction import ChatInteraction
from src.application.services.chat_service import ChatService, ChatProcessingError 

# Define common test data as module-level constants or within fixtures
TEST_PROMPT = "Hello, how are you?"
TEST_USER_ID = "user123"
TEST_LLM_RESPONSE = "I am doing well, thank you!"
TEST_CHAT_INTERACTION_ID = "chat_id_abc"

@pytest.fixture
def mock_llm_client():
    """
    Pytest fixture for a mocked LLMClient.
    """
    mock_client = Mock(spec=LLMClient)
    mock_client.get_model_name.return_value = "test-model"
    return mock_client

@pytest.fixture
def mock_chat_repository():
    """
    Pytest fixture for a mocked ChatRepository.
    """
    mock_repo = AsyncMock(spec=ChatRepository)
    return mock_repo

@pytest.fixture
def chat_service(mock_llm_client, mock_chat_repository):
    """
    Pytest fixture for the ChatService instance with mocked dependencies.
    """
    service = ChatService(mock_llm_client, mock_chat_repository)
    return service

@pytest.mark.asyncio
async def test_chat_success(chat_service, mock_llm_client, mock_chat_repository):
    """
    Test that the chat method successfully generates a response,
    saves the interaction, and returns the saved interaction.
    """
    mock_llm_client.generate_text.return_value = TEST_LLM_RESPONSE

    expected_chat_interaction = ChatInteraction(
        userId=TEST_USER_ID,
        prompt=TEST_PROMPT,
        response=TEST_LLM_RESPONSE,
        model=mock_llm_client.get_model_name(),
        timestamp=datetime.now()
    )
    # Simulate the repository adding an ID after creation
    expected_chat_interaction.id = TEST_CHAT_INTERACTION_ID
    mock_chat_repository.create_chat_interaction.return_value = expected_chat_interaction.id

    # Call the method under test
    returned_interaction = await chat_service.chat(TEST_PROMPT, TEST_USER_ID)

    # Assertions
    # 1. Verify LLMClient's generate_text was called correctly
    mock_llm_client.generate_text.assert_called_once_with(TEST_PROMPT)

    # 2. Verify ChatRepository's create_chat_interaction was called
    mock_chat_repository.create_chat_interaction.assert_called_once()
    # Get the ChatInteraction object passed to the repository
    called_chat_interaction = mock_chat_repository.create_chat_interaction.call_args[0][0]

    # 3. Verify the attributes of the ChatInteraction object passed to the repository
    assert called_chat_interaction.userId == TEST_USER_ID
    assert called_chat_interaction.prompt == TEST_PROMPT
    assert called_chat_interaction.response == TEST_LLM_RESPONSE
    assert called_chat_interaction.model == mock_llm_client.get_model_name()
    assert isinstance(called_chat_interaction.timestamp, datetime)

    # 4. Verify the returned interaction matches the expected one (with ID)
    assert returned_interaction.id == TEST_CHAT_INTERACTION_ID
    assert returned_interaction.userId == TEST_USER_ID
    assert returned_interaction.prompt == TEST_PROMPT
    assert returned_interaction.response == TEST_LLM_RESPONSE

@pytest.mark.asyncio
async def test_chat_llm_generation_error(chat_service, mock_llm_client, mock_chat_repository):
    """
    Test that the chat method raises ChatProcessingError when LLM generation fails.
    """
    # Configure the mock LLMClient to raise LLMGenerationError
    mock_llm_client.generate_text.side_effect = LLMGenerationError("LLM failed")

    # Call the method under test and assert that ChatProcessingError is raised
    with pytest.raises(ChatProcessingError, match="Failed to generate response due to LLM error."):
        await chat_service.chat(TEST_PROMPT, TEST_USER_ID)

    # Verify LLMClient's generate_text was called
    mock_llm_client.generate_text.assert_called_once_with(TEST_PROMPT)
    # Verify ChatRepository's create_chat_interaction was NOT called
    mock_chat_repository.create_chat_interaction.assert_not_called()

@pytest.mark.asyncio
async def test_chat_save_error(chat_service, mock_llm_client, mock_chat_repository):
    """
    Test that the chat method raises ChatProcessingError when saving to repository fails.
    """
    # Configure the mock LLMClient to return a successful response
    mock_llm_client.generate_text.return_value = TEST_LLM_RESPONSE

    # Configure the mock ChatRepository to raise ChatSaveError
    mock_chat_repository.create_chat_interaction.side_effect = ChatSaveError("DB save failed")

    # Call the method under test and assert that ChatProcessingError is raised
    with pytest.raises(ChatProcessingError, match="Failed to complete chat due to database error."):
        await chat_service.chat(TEST_PROMPT, TEST_USER_ID)

    # Verify LLMClient's generate_text was called
        mock_llm_client.generate_text.assert_called_once_with(TEST_PROMPT)
    # Verify ChatRepository's create_chat_interaction was called (as the error happens during save)
        mock_chat_repository.create_chat_interaction.assert_called_once()
