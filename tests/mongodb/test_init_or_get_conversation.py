import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException
from bson import ObjectId

from app.type import Conversation
from app.packages.models.conversation_models import UserConversationQuery
from app.packages.mongodb import init_or_get_conversation

# Assuming these imports are available in your project

# Mock data for an existing conversation
existing_conversation = {
    "_id": ObjectId(),
    "user_id": "123",
    "summaries": [{"role": "user", "content": "Summary message"}],
    "questions": [{"role": "user", "content": "Question message"}],
    "analyze": [{"role": "user", "content": "Analyze message"}],
    "keywords": [{"role": "user", "content": "Keyword message"}],
    "topic": "Sample Topic",
    "created_at": "2024-01-01T00:00:00",
    "status": "active",
    "is_favorite": True,
    "answers": [{"role": "user", "content": "Answer message"}]
}

@pytest.mark.asyncio
async def test_init_or_get_conversation_existing():
    query = UserConversationQuery(
        user_id="123",
        conversation_id=str(existing_conversation["_id"]),
        topic="Sample Topic"
    )

    # Mock get_conversation_by_id to return the existing conversation
    with patch("app.packages.mongodb.get_conversation_by_id", AsyncMock(return_value=existing_conversation)):
        result = await init_or_get_conversation(query)
        
        assert isinstance(result, Conversation)
        assert result.user_id == query.user_id
        assert result.conversation_id == query.conversation_id
        assert result.topic == query.topic
        assert result.questions == existing_conversation["questions"]
        assert result.summaries == existing_conversation["summaries"]
        assert result.analyze == existing_conversation["analyze"]
        assert result.created_at == existing_conversation["created_at"]
        assert result.status == existing_conversation["status"]
        assert result.is_favorite == existing_conversation["is_favorite"]
        assert result.answers == existing_conversation["answers"]

@pytest.mark.asyncio
async def test_init_or_get_conversation_non_existing():
    query = UserConversationQuery(
        user_id=123,
        conversation_id="non_existing_id",
        topic="New Topic"
    )

    # Mock get_conversation_by_id to return None for a non-existing conversation
    with patch("app.packages.mongodb.get_conversation_by_id", AsyncMock(return_value=None)):
        result = await init_or_get_conversation(query)
        
        assert isinstance(result, Conversation)
        assert result.user_id == query.user_id
        assert result.conversation_id == None
        assert result.topic == query.topic
        assert result.questions == []
        assert result.summaries == []
        assert result.analyze == []

@pytest.mark.asyncio
async def test_init_or_get_conversation_error():
    query = UserConversationQuery(
        user_id=123,
        conversation_id="error_id",
        topic="Error Topic"
    )

    # Mock get_conversation_by_id to raise an exception
    with patch("app.packages.mongodb.get_conversation_by_id", AsyncMock(side_effect=Exception("Database error"))):
        with pytest.raises(HTTPException) as exc_info:
            await init_or_get_conversation(query)
        
        assert exc_info.value.status_code == 500
        assert exc_info.value.detail == "Internal server error while fetching conversation."
