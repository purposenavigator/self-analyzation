import pytest
from unittest.mock import AsyncMock, patch
from app.models import GPTRequest, UserConversation
from app.resolvers import process_answer_and_generate_followup_resolver
from datetime import datetime, timezone
from fastapi import HTTPException

@pytest.mark.asyncio
async def test_process_answer_and_generate_followup_resolver():
    # Create a mock GPTRequest object
    request = GPTRequest(prompt="Test prompt", user_id=1, question_id="test_question_id", topic="Test Topic", is_title_generate=False)
    
    # Mock the functions that are called within the resolver
    with patch("app.resolvers.process_conversation", new_callable=AsyncMock) as mock_process_conversation, \
         patch("app.resolvers.generate_responses", new_callable=AsyncMock) as mock_generate_responses, \
         patch("app.resolvers.logger") as mock_logger:

        # Set up the return value for process_conversation
        mock_conversation = UserConversation(
            user_id=1,
            conversation_id="test_conversation_id",
            question_id="test_question_id",
            topic="Sample Topic",
            summaries=[],
            questions=[],
            analyze=[],
            title=None
        )
        mock_process_conversation.return_value = mock_conversation

        # Mock the string responses from generate_responses
        mock_generate_responses.return_value = (
            "Sample question response",
            "Sample summary response",
            "Sample analyze response"
        )

        # Call the function with the mocked data
        response = await process_answer_and_generate_followup_resolver(request)

        # Check if the function returns the expected result
        assert response == {
            "user_prompt": "Test prompt",
            "summary_response": "Sample summary response",
            "question_response": "Sample question response",
            "analyze_response": "Sample analyze response",
            "conversation_id": "test_conversation_id",
            "title": "Test"
        }

        # Ensure the mocked functions were called as expected
        mock_process_conversation.assert_awaited_once_with(request)
        mock_generate_responses.assert_awaited_once_with(mock_conversation)

    # Test the exception handling
    with patch("app.resolvers.process_conversation", new_callable=AsyncMock) as mock_process_conversation, \
         patch("app.resolvers.logger") as mock_logger:
        
        # Make process_conversation raise an exception
        mock_process_conversation.side_effect = Exception("Test exception")

        with pytest.raises(HTTPException) as excinfo:
            await process_answer_and_generate_followup_resolver(request)

        assert excinfo.value.status_code == 500
        assert str(excinfo.value.detail) == "Test exception"
        mock_logger.error.assert_called_once()
