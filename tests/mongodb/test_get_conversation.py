import pytest
from unittest.mock import patch, AsyncMock
from bson import ObjectId
from fastapi import HTTPException
from app.packages.mongodb import get_conversation, SimpleConversationQuery, Conversation

@pytest.mark.asyncio
@patch('app.packages.mongodb.get_conversation_by_id')
async def test_get_conversation_success(mock_get_conversation_by_id):
    # Arrange
    mock_conversation_id = str(ObjectId())
    mock_user_id = "user123"
    mock_query = SimpleConversationQuery(user_id=mock_user_id, conversation_id=mock_conversation_id)
    
    mock_conversation = {
        "_id": ObjectId(mock_conversation_id),
        "topic": "Sample Topic",
        "questions": ["What is your favorite color?", "Why do you value honesty?"],
        "summaries": ["Summary 1", "Summary 2"],
        "analyze": {"key": "value"}
    }
    mock_get_conversation_by_id.return_value = mock_conversation
    
    # Act
    result = await get_conversation(mock_query)
    
    # Assert
    assert isinstance(result, Conversation)
    assert result.user_id == mock_user_id
    assert result.conversation_id == mock_conversation_id
    assert result.topic == mock_conversation['topic']
    assert result.questions == mock_conversation["questions"]
    assert result.summaries == mock_conversation["summaries"]
    assert result.analyze == mock_conversation["analyze"]

@pytest.mark.asyncio
@patch('app.packages.mongodb.get_conversation_by_id')
async def test_get_conversation_not_found(mock_get_conversation_by_id):
    # Arrange
    mock_conversation_id = str(ObjectId())
    mock_user_id = "user123"
    mock_query = SimpleConversationQuery(user_id=mock_user_id, conversation_id=mock_conversation_id)

    mock_get_conversation_by_id.return_value = None
    
    # Act
    result = await get_conversation(mock_query)
    
    # Assert
    assert result is None

@pytest.mark.asyncio
@patch('app.packages.mongodb.get_conversation_by_id')
async def test_get_conversation_raises_exception(mock_get_conversation_by_id):
    # Arrange
    mock_conversation_id = str(ObjectId())
    mock_user_id = "user123"
    mock_query = SimpleConversationQuery(user_id=mock_user_id, conversation_id=mock_conversation_id)

    mock_get_conversation_by_id.side_effect = Exception("Database error")

    # Act & Assert
    with pytest.raises(HTTPException) as excinfo:
        await get_conversation(mock_query)
    
    assert excinfo.value.status_code == 500
    assert "Internal server error while fetching conversation." in str(excinfo.value.detail)
