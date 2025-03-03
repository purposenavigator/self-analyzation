from fastapi import HTTPException
import pytest
from datetime import datetime, timezone
from bson import ObjectId
from unittest.mock import AsyncMock, patch
from app.packages.mongodb import create_conversation
from app.type import Conversation

# Define the conversation object once
conversation = Conversation(
    user_id="test_user",
    conversation_id=None,
    topic="Test Topic",
    summaries=[{"role": "user", "content": "Summary 1"}],
    questions=[{"role": "user", "content": "Question 1"}],
    analyze=[{"role": "user", "content": "Analyze 1"}],
    answers=[{"role": "user", "content": "Answer 1"}],
    title="Test Title",
    created_at=datetime.now(timezone.utc),
    updated_at=datetime.now(timezone.utc),
    status="active",
    is_favorite=True,
    deleted_at=None
)

@pytest.mark.asyncio
@patch("app.packages.mongodb.conversation_collection.insert_one", new_callable=AsyncMock)
async def test_create_conversation(mock_insert_one):
    # Mock the insert_one method to return a mock result with an inserted_id
    mock_insert_one.return_value.inserted_id = ObjectId()

    # Call the create_conversation function
    conversation_id = await create_conversation(conversation)

    # Assertions to verify the conversation was created correctly
    mock_insert_one.assert_called_once()
    assert conversation_id is not None

@pytest.mark.asyncio
@patch("app.packages.mongodb.conversation_collection.insert_one", new_callable=AsyncMock)
async def test_create_conversation_raises_error(mock_insert_one):
    # Mock the insert_one method to raise an exception
    mock_insert_one.side_effect = Exception("Database error")

    # Call the create_conversation function and assert that it raises an HTTPException
    with pytest.raises(HTTPException) as exc_info:
        await create_conversation(conversation)

    assert exc_info.value.status_code == 500
    assert "Internal server error while creating conversation." in str(exc_info.value)
