from bson import ObjectId
import pytest
from motor.motor_asyncio import AsyncIOMotorClient
from unittest.mock import AsyncMock
from fastapi import HTTPException
from datetime import datetime, timezone
from bson import ObjectId

from app.packages.models.conversation_models import UserConversation
from app.packages.mongodb import create_conversation

@pytest.fixture
def mock_db():
    client = AsyncIOMotorClient()
    return client['test_db']

@pytest.fixture
def mock_collection(mock_db, mocker):
    collection = mock_db['user_conversations']
    mocker.patch.object(collection, 'insert_one', new_callable=AsyncMock)
    return collection

@pytest.fixture
def user_conversation():
    return UserConversation(
        user_id="123",
        conversation_id=str(ObjectId()),  # Generating a new ObjectId for the conversation
        topic="Testing create_conversation",
        summaries=["summary 1"],
        questions=["question 1"],
        answers=["answer 1"],
        analyze=["analyze 1"],
        title="Conversation Title",
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        status="active",
        is_favorite=False,
        deleted_at=None
    )

@pytest.mark.asyncio
async def test_create_conversation_success(mock_collection, user_conversation):
    mock_collection.insert_one.return_value = AsyncMock()

    result = await create_conversation(user_conversation)
    assert ObjectId.is_valid(result), "The result should be a valid ObjectId"

@pytest.mark.asyncio
async def test_create_conversation_failure(mock_collection, user_conversation):
    mock_collection.insert_one.side_effect = Exception("Mocked insert failure")

    with pytest.raises(HTTPException) as exc_info:
        await create_conversation(user_conversation)

    assert exc_info.value.status_code == 500
    assert exc_info.value.detail == "Internal server error while creating conversation."

