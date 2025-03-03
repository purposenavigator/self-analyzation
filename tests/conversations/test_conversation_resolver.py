import os
import sys
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app.packages.models.conversation_models import GPTRequest
from app.services.conversation_services import process_conversation
from app.type import Conversation


@pytest.mark.asyncio
@patch('app.packages.mongodb.get_conversation', new_callable=AsyncMock)
@patch('app.services.conversation_services.get_system_role')
async def test_process_conversation_init_success(mock_get_system_role, mock_get_conversation):
    mock_get_system_role.return_value = {
        'question': {'role': 'system', 'content': 'some test question'}, 
        'summary': {'role': 'system', 'content': 'some test summary'},
        'analyze': {'role': 'system', 'content': 'some test advisor'},
        'answers': {'role': 'system', 'content': 'some test advisor'}
        }
    mock_get_conversation.return_value = Conversation(
            user_id="123", 
            conversation_id=None, 
            topic="Test",
            questions=[], 
            summaries=[],
            answers=[],
            analyze=[]
        )

    request = GPTRequest(conversation_id=None, user_id="123", topic="Test", prompt="Hello, how are you?")
    conversation = await process_conversation(request, user_id="123")

    assert conversation.user_id == "123"
    assert conversation.topic == "Test"
    assert conversation.questions[-1]["content"] == "Hello, how are you?"
    assert conversation.summaries[-1]["content"] == "Hello, how are you?"

@pytest.mark.asyncio
async def test_process_conversation_invalid_topic():
    request = GPTRequest(topic="NonExistentTopic", conversation_id=None, user_id=123, prompt="Test prompt")
    with pytest.raises(HTTPException) as excinfo:
        await process_conversation(request, user_id="123")
    assert excinfo.value.status_code == 500
    assert excinfo.value.detail == "Invalid topic: NonExistentTopic"
