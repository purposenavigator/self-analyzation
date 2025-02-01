import pytest
from bson import ObjectId
from unittest.mock import AsyncMock, patch

from app.packages.mongodb import get_conversation_by_id

@pytest.mark.asyncio
async def test_get_conversation_by_id_success():
    # Mock conversation data
    mock_conversation_id = str(ObjectId())
    mock_conversation = {"_id": ObjectId(mock_conversation_id), "title": "Sample Conversation"}

    with patch('app.packages.database.conversation_collection.find_one', new_callable=AsyncMock) as mock_find_one:
        # Configure the mock to return the conversation
        mock_find_one.return_value = mock_conversation

        # Call the function
        result = await get_conversation_by_id(mock_conversation_id)

        # Assertions
        assert result == mock_conversation
        mock_find_one.assert_called_once_with({"_id": ObjectId(mock_conversation_id)})

@pytest.mark.asyncio
async def test_get_conversation_by_id_not_found():
    mock_conversation_id = str(ObjectId())

    with patch('app.packages.database.conversation_collection.find_one', new_callable=AsyncMock) as mock_find_one:
        # Configure the mock to return None (not found)
        mock_find_one.return_value = None

        # Call the function
        result = await get_conversation_by_id(mock_conversation_id)

        # Assertions
        assert result is None
        mock_find_one.assert_called_once_with({"_id": ObjectId(mock_conversation_id)})

@pytest.mark.asyncio
async def test_get_conversation_by_id_exception():
    mock_conversation_id = str(ObjectId())

    with patch('app.packages.database.conversation_collection.find_one', new_callable=AsyncMock) as mock_find_one:
        # Configure the mock to raise an exception
        mock_find_one.side_effect = Exception("Database connection error")

        # Test that the function raises a general Exception for other errors
        with pytest.raises(Exception, match="An error occurred while fetching the conversation: Database connection error"):
            await get_conversation_by_id(mock_conversation_id)
