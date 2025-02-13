import pytest
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from app.resolvers.conversation_resolvers import process_answer_and_generate_followup_resolver
from app.packages.models.conversation_models import GPTRequest
from app.type import Conversation

@pytest.mark.asyncio
@patch("app.resolvers.conversation_resolvers.process_conversation", new_callable=AsyncMock)
@patch("app.resolvers.conversation_resolvers.generate_responses", new_callable=AsyncMock)
@patch("app.resolvers.conversation_resolvers.update_conversation", new_callable=AsyncMock)
@patch("app.resolvers.conversation_resolvers.get_title", new_callable=AsyncMock)
async def test_process_answer_and_generate_followup_resolver(
    mock_get_title, mock_update_conversation, 
    mock_generate_responses, mock_process_conversation
):
    # Arrange
    user_id = "test_user"
    request = GPTRequest(
        topic="test_topic", prompt="test_prompt", 
        conversation_id=None, is_title_generate=True
    )
    conversation = Conversation(
        conversation_id="123", title=None, questions=[], 
        summaries=[], analyze=[], answers=[], 
        user_id=user_id, topic=request.topic
    )
    
    mock_process_conversation.return_value = conversation
    mock_generate_responses.return_value = (
        "ai_question_response", "ai_summary_response", 
        "ai_analyze_response", "ai_answers_response"
    )
    mock_get_title.return_value = "Generated Title"
    
    # Act
    response = await process_answer_and_generate_followup_resolver(request, user_id)
    
    # Assert
    assert response["user_prompt"] == "test_prompt"
    assert response["summary_response"] == "ai_summary_response"
    assert response["question_response"] == "ai_question_response"
    assert response["analyze_response"] == "ai_analyze_response"
    assert response["answers_response"] == "ai_answers_response"
    assert response["conversation_id"] == "123"
    assert response["title"] == "Generated Title"
    
    mock_process_conversation.assert_awaited_once_with(request, user_id)
    mock_generate_responses.assert_awaited_once_with(conversation)
    mock_update_conversation.assert_awaited()
    mock_get_title.assert_awaited_once_with(["ai_summary_response"])
