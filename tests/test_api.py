import pytest
from httpx import AsyncClient
from fastapi import FastAPI, HTTPException
from app.main import app  # Replace with your actual FastAPI app import
from app.packages.models.conversation_models import UserConversationRequest
from unittest.mock import patch
from bson import ObjectId  # Add this import

@pytest.mark.asyncio
@patch('app.main.get_conversation_resolver')  # Replace with actual module path where `get_conversation_resolver` is defined
async def test_api_get_conversation_success(mock_get_conversation_resolver):
    # Arrange
    valid_object_id = str(ObjectId())  # Generate a valid ObjectId
    mock_request_data = UserConversationRequest(user_id=1, conversation_id=valid_object_id)
    mock_response_data = {
        "user_id": 1,
        "conversation_id": valid_object_id,
        "topic": "sample topic",
        "questions": ["What is your favorite color?"],
        "summaries": ["This is a summary"],
        "analyze": {"key": "value"},
        "question_id": "question123"
    }
    mock_get_conversation_resolver.return_value = mock_response_data

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Act
        response = await client.post("/get_conversation", json=mock_request_data.model_dump())  # Use params instead of json

    # Assert
    assert response.status_code == 200
    assert response.json() == mock_response_data

@pytest.mark.asyncio
@patch('app.main.get_conversation_resolver')  # Changed to mock the resolver instead of mongodb function
async def test_api_get_conversation_failure(mock_get_conversation_resolver):
    # Arrange
    valid_object_id = str(ObjectId())
    mock_request_data = UserConversationRequest(user_id=1, conversation_id=valid_object_id)
    mock_get_conversation_resolver.side_effect = HTTPException(status_code=500, detail="Error fetching conversation")

    async with AsyncClient(app=app, base_url="http://test") as client:
        # Act
        response = await client.post("/get_conversation", json=mock_request_data.model_dump())

    # Assert
    assert response.status_code == 500
    assert "detail" in response.json()
    assert response.json()["detail"] == "Error fetching conversation"
