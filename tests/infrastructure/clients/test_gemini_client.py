# tests/unit/test_gemini_client.py

import pytest
from unittest.mock import MagicMock
from src.infrastructure.clients.gemini_client import GeminiClient
from src.domain.clients.llm_client import LLMGenerationError

@pytest.fixture
def mock_genai_client():
    """
    Fixture that provides a MagicMock representing a genai.Client instance.
    """
    return MagicMock()

@pytest.fixture
def gemini_client(mock_genai_client):
    """
    Fixture that provides an instance of GeminiClient for tests.
    """
    return GeminiClient(genai_client=mock_genai_client)


def test_gemini_client_initialization(gemini_client):
    """
    Tests if the GeminiClient is initialized correctly.
    """
    assert gemini_client.model_name == "gemini-2.5-flash"
    # We can't directly assert on self.client without more advanced mocking
    # but the subsequent tests will implicitly verify its usage.


def test_get_model_name(gemini_client):
    """
    Tests the get_model_name method.
    """
    assert gemini_client.get_model_name() == "gemini-2.5-flash"


def test_generate_text_success(gemini_client, mock_genai_client):
    """
    Tests successful text generation by mocking the genai client's response.
    """
    # Arrange: Configure the mock client to return a successful response
    mock_response_object = MagicMock()
    mock_response_object.text = "This is a brilliantly generated response from Gemini!"
    mock_genai_client.models.generate_content.return_value = mock_response_object

    prompt = "Tell me a fun fact about unit testing."
    
    # Act: Call the method under test
    response = gemini_client.generate_text(prompt)

    # Assertions:
    # 1. Check if the response matches what the mock returned
    assert response == "This is a brilliantly generated response from Gemini!"
    
    # 2. Verify that `generate_content` was called exactly once with the correct arguments
    mock_genai_client.models.generate_content.assert_called_once_with(
        model="gemini-2.5-flash",
        contents=prompt,
    )


def test_generate_text_llm_generation_error(gemini_client, mock_genai_client):
    """
    Tests error handling during text generation when the genai client raises an exception.
    """
    # Arrange: Configure the mock client to raise an exception
    mock_genai_client.models.generate_content.side_effect = Exception("API connection failed")

    prompt = "Generate a poem about a lost sock."

    # Act & Assert: Expect LLMGenerationError to be raised
    with pytest.raises(LLMGenerationError) as excinfo:
        gemini_client.generate_text(prompt)

    # Verify the error message contains the original exception details
    assert "An unexpected error occurred during LLM response generation: API connection failed" in str(excinfo.value)
    
    # Verify that `generate_content` was still called
    mock_genai_client.models.generate_content.assert_called_once_with(
        model="gemini-2.5-flash",
        contents=prompt,
    )