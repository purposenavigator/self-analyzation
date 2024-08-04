import os
import sys
import pytest
from unittest.mock import patch, AsyncMock
from fastapi import HTTPException

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from app.models import GPTRequest, UserConversation
from app.resolvers import generate_responses, process_answer_and_generate_followup, process_conversation


@pytest.mark.asyncio
@patch('app.resolvers.get_conversation', new_callable=AsyncMock)
@patch('app.resolvers.update_conversation', new_callable=AsyncMock)
@patch('app.resolvers.get_system_role')
async def test_process_conversation(get_system_role_mock, update_conversation_mock, get_conversation_mock):
    get_system_role_mock.return_value = {"question": {"role": "system", "content": "question"}, "summary": {"role": "system", "content": "summary"}}
    get_conversation_mock.return_value = UserConversation(user_id=123, conversation_id=None, topic="Test", questions=[], summaries=[])

    request = GPTRequest(conversation_id=None, user_id=123, topic="Test", prompt="Hello, how are you?")
    user_conversation = await process_conversation(request)

    assert user_conversation.user_id == 123
    assert user_conversation.topic == "Test"
    assert user_conversation.questions[-1]["content"] == "Hello, how are you?"
    assert user_conversation.summaries[-1]["content"] == "Hello, how are you?"

@pytest.mark.asyncio
@patch('app.resolvers.get_conversation', new_callable=AsyncMock)
async def test_process_conversation_user_id_string(get_conversation_mock):

    request = GPTRequest(conversation_id=None, user_id="123", topic="Test", prompt="Hello, how are you?")

    # Simulate an exception
    get_conversation_mock.side_effect = Exception("Test exception")
    with pytest.raises(HTTPException) as exc_info:
        await process_conversation(request)
    assert exc_info.value.status_code == 500
    assert "Internal server error while processing conversation." in str(exc_info.value.detail)

@pytest.mark.asyncio
async def test_process_conversation_invalid_topic():
    request = GPTRequest(topic="NonExistentTopic", conversation_id=None, user_id=123, prompt="Test prompt")
    with pytest.raises(HTTPException) as excinfo:
        await process_conversation(request)
    assert excinfo.value.status_code == 400
    assert excinfo.value.detail == "Invalid topic: NonExistentTopic"

@pytest.mark.asyncio
@patch('app.resolvers.get_conversation', return_value=UserConversation(conversation_id=None, user_id=123, topic="Test", questions=[], summaries=[]))
async def test_process_conversation_valid_topic(mock_get_conversation):
    request = GPTRequest(topic="Test", conversation_id=None, user_id=123, prompt="Test prompt")
    user_conversation = await process_conversation(request)

    assert user_conversation.conversation_id is not None
    assert any(q["role"] == "system" for q in user_conversation.questions)
    assert any(s["role"] == "system" for s in user_conversation.summaries)
    assert user_conversation.questions[-1]["content"] == request.prompt
    assert user_conversation.summaries[-1]["content"] == request.prompt