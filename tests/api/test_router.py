import pytest
from fastapi import FastAPI, status
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock, patch

from src.api.router import api_router
from src.application.services.chat_service import ChatService, ChatProcessingError
from src.domain.entities.chat_interaction import ChatInteraction  # Assuming this model exists

app = FastAPI()
app.include_router(api_router)

client = TestClient(app) 

# --- Fixtures for Mocking Dependencies ---

@pytest.fixture
def mock_chat_service():
    """
    Fixture to provide a mock ChatService.
    We use AsyncMock because the chat method is an async function.
    """
    return AsyncMock(spec=ChatService)

@pytest.fixture
def mock_llm_client():
    """
    Fixture to provide a mock LLMClient.
    """
    # Assuming LLMClient has a 'generate' or similar method
    mock_client = MagicMock()
    mock_client.generate.return_value = "Mocked LLM response."
    return mock_client

@pytest.fixture
def mock_chat_repository():
    """
    Fixture to provide a mock ChatRepository.
    """
    # Assuming ChatRepository has a 'save_chat_interaction' or similar method
    mock_repo = MagicMock()
    mock_repo.save_chat_interaction = AsyncMock(return_value=None) # If it's an async method
    return mock_repo

@pytest.fixture(autouse=True)
def override_dependency(mock_chat_service):
    """
    Fixture to override the get_chat_service_dependency for testing.
    This ensures our mock_chat_service is used when the endpoint is called.
    """
    from src.api.dependencies import get_chat_service_dependency, get_llm_client_dependency, get_chat_repository_dependency
    print("Overriding get_chat_service_dependency with mock_chat_service")
    app.dependency_overrides[get_chat_service_dependency] = lambda: mock_chat_service
    app.dependency_overrides[get_llm_client_dependency] = lambda: mock_llm_client
    app.dependency_overrides[get_chat_repository_dependency] = lambda: mock_chat_repository


# --- Unit Tests for the /v1/chat Endpoint ---

def test_chat_success(mock_chat_service):
    """
    Test case for a successful chat request.
    Verifies that the API returns a ChatResponse with correct data.
    """
    # Define the expected return value from the mock chat service

    mock_chat_interaction = ChatInteraction(
        id="test-id-123",
        userId="user123",
        prompt="Hello, AI!",
        response="Hi there!",
        model="gpt-3.5-turbo",
        timestamp="2024-07-21T10:00:00Z" # Use ISO format for consistency
    )
    mock_chat_service.chat.return_value = mock_chat_interaction

    # Define the request payload
    chat_request_payload = {
        "userId": "user123",
        "prompt": "Hello, AI!"
    }

    # Make the POST request to the endpoint
    response = client.post("/v1/chat", json=chat_request_payload)

    # Assert the HTTP status code is 200 OK
    print(response.json())
    assert response.status_code == status.HTTP_200_OK
    

    # Assert the response body matches the expected ChatResponse structure and data
    response_data = response.json()
    assert response_data["id"] == mock_chat_interaction.id
    assert response_data["userId"] == mock_chat_interaction.userId
    assert response_data["prompt"] == chat_request_payload["prompt"]
    assert response_data["response"] == mock_chat_interaction.response
    assert response_data["model"] == mock_chat_interaction.model
    assert response_data["timestamp"] == mock_chat_interaction.timestamp.isoformat()

    # Verify that the chat service's chat method was called with the correct arguments
    mock_chat_service.chat.assert_called_once_with(
        chat_request_payload["prompt"],
        chat_request_payload["userId"]
    )

def test_chat_processing_error(mock_chat_service):
    """
    Test case for when the ChatService raises a ChatProcessingError.
    Verifies that the API returns a 500 Internal Server Error.
    """
    # Configure the mock chat service to raise a ChatProcessingError
    mock_chat_service.chat.side_effect = ChatProcessingError("Failed to process chat.")

    # Define the request payload
    chat_request_payload = {
        "userId": "user456",
        "prompt": "Tell me a story."
    }

    # Make the POST request to the endpoint
    response = client.post("/v1/chat", json=chat_request_payload)

    # Assert the HTTP status code is 500 Internal Server Error
    assert response.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR

    # Assert the error detail message
    response_data = response.json()
    assert response_data["detail"] == "An unexpected error happening while processing the chat request."

    # Verify that the chat service's chat method was called
    mock_chat_service.chat.assert_called_once_with(
        chat_request_payload["prompt"],
        chat_request_payload["userId"]
    )

def test_chat_validation_error_missing_field():
    """
    Test case for a validation error (e.g., missing required field in request).
    FastAPI handles this automatically, returning a 422 Unprocessable Entity.
    """
    # Request payload missing 'prompt'
    chat_request_payload = {
        "userId": "user789"
        # 'prompt' is missing
    }

    # Make the POST request to the endpoint
    response = client.post("/v1/chat", json=chat_request_payload)

    # Assert the HTTP status code is 422 Unprocessable Entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Assert that the response contains validation error details
    response_data = response.json()
    assert "detail" in response_data
    assert any("Field required" in error["msg"] for error in response_data["detail"] if error["loc"][1] == "prompt")

def test_chat_validation_error_invalid_type():
    """
    Test case for a validation error (e.g., incorrect type for a field).
    """
    # Request payload with 'userId' as an integer instead of string
    chat_request_payload = {
        "userId": 123, # Should be string
        "prompt": "Hello"
    }

    # Make the POST request to the endpoint
    response = client.post("/v1/chat", json=chat_request_payload)

    # Assert the HTTP status code is 422 Unprocessable Entity
    assert response.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY

    # Assert that the response contains validation error details
    response_data = response.json()
    assert "detail" in response_data
    assert any("string_type" in error["type"] for error in response_data["detail"] if error["loc"][1] == "userId")