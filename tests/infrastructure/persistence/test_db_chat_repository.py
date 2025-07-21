import pytest
from unittest.mock import MagicMock, AsyncMock
from pymongo.errors import PyMongoError
from pymongo.database import Database
from src.infrastructure.persistence.db_chat_repository import DatabaseChatRepository
from src.domain.entities.chat_interaction import ChatInteraction
from src.domain.repositories.chat_repository import ChatSaveError


@pytest.fixture
def mock_collection():
    """
    Fixture to provide a mocked MongoDB collection.
    AsyncMock is used for methods that are awaited (like insert_one).
    MagicMock is used for the collection object itself.
    """
    mock_coll = MagicMock()
    mock_coll.insert_one = AsyncMock()
    return mock_coll

@pytest.fixture
def mock_database(mock_collection):
    """
    Fixture to provide a mocked MongoDB database.
    It ensures that accessing database["chat_interactions"] returns our mock_collection.
    """
    mock_db = MagicMock(spec=Database)
    mock_db.__getitem__.return_value = mock_collection
    return mock_db

@pytest.fixture
def chat_repository(mock_database):
    """
    Fixture to provide an instance of DatabaseChatRepository with mocked dependencies.
    """
    return DatabaseChatRepository(mock_database)

@pytest.fixture
def sample_chat_interaction():
    """
    Fixture to provide a sample ChatInteraction object for testing.
    """
    return ChatInteraction(
        model="test-model",
        userId="user123",
        prompt="Hello, bot!",
        response="Hi there!",
        timestamp="2023-10-27T10:00:00Z"
    )

@pytest.mark.asyncio
async def test_create_chat_interaction_success(chat_repository, mock_collection, sample_chat_interaction):
    """
    Tests successful creation of a chat interaction.
    Verifies that insert_one is called and the ID is updated.
    """
    # Simulate a successful insert operation
    inserted_id = "653b6e8a1a2b3c4d5e6f7a8b"
    mock_collection.insert_one.return_value = MagicMock(inserted_id=inserted_id)

    # Call the method under test
    result_id = await chat_repository.create_chat_interaction(sample_chat_interaction)

    # Assertions
    # Ensure insert_one was called exactly once
    mock_collection.insert_one.assert_called_once()
    expected_data = sample_chat_interaction.model_dump(by_alias=True, exclude_none=True)
    mock_collection.insert_one.assert_called_once_with(expected_data)
    assert result_id == inserted_id

@pytest.mark.asyncio
async def test_create_chat_interaction_pymongo_error(chat_repository, mock_collection, sample_chat_interaction):
    """
    Tests error handling when PyMongoError occurs during insertion.
    Verifies that ChatSaveError is raised.
    """
    # Simulate PyMongoError during insert operation
    mock_collection.insert_one.side_effect = PyMongoError("Connection lost")

    # Expect ChatSaveError to be raised
    with pytest.raises(ChatSaveError) as excinfo:
        await chat_repository.create_chat_interaction(sample_chat_interaction)

    # Assertions
    mock_collection.insert_one.assert_called_once()
    assert "Failed to save chat interaction to database: Connection lost" in str(excinfo.value)