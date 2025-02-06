from app.resolvers import get_analyze_resolver
import pytest
import hashlib
from unittest.mock import AsyncMock, patch
from fastapi import HTTPException
from bson import ObjectId  # Add this import

# Adjust the import to your actual module & function name


@pytest.mark.asyncio
async def test_get_analyze_resolver_success():
    """
    Tests that get_analyze_resolver successfully returns the expected keywords
    and updates the conversation accordingly.
    """
    # Given
    conversation_id = str(ObjectId())  # Convert ObjectId to string
    conversation_data = {
        "summaries": [
            {"role": "assistant", "content": "Assistant content 1"},
            {"role": "user", "content": "User content"},
            {"role": "assistant", "content": "Assistant content 2"},
        ]
    }
    
    # This is what we expect to see after joining assistant contents
    summaries_content = "Assistant content 1 Assistant content 2"
    expected_hash = hashlib.sha256(summaries_content.encode("utf-8")).hexdigest()
    
    # Mock a response structure from your `fetch_keywords_from_api_only_one`
    # that resembles what you'd get from OpenAI or another LLM.
    mock_api_response = type("MockResponse", (), {
        "choices": [
            type("MockChoice", (), {
                "message": type("MockMessage", (), {"content": "keyword1, keyword2"})
            })()
        ]
    })()

    # When
    with patch("app.packages.mongodb.get_conversation_by_id", new=AsyncMock(return_value=conversation_data)), \
         patch("app.openai_resolvers.keyword_extraction.fetch_keywords_from_api_only_one", new=AsyncMock(return_value=mock_api_response)), \
         patch("app.packages.mongodb.update_or_append_field_by_id", new=AsyncMock()) as mock_update, \
         patch("app.packages.mongodb.get_analysis_summary_by_sha", new=AsyncMock(return_value="summary")):
        
        # Call the function
        result = await get_analyze_resolver(conversation_id)
        
        # Then
        # Check that the result matches the "keywords" from the mock response
        assert result == "keyword1, keyword2"
        
        # Confirm we updated the conversation with the correct hash -> analysis mapping
        mock_update.assert_awaited_once_with(
            conversation_id,
            "analysis_summaries",
            {expected_hash: "keyword1, keyword2"}
        )


@pytest.mark.asyncio
async def test_get_analyze_resolver_exception():
    """
    Tests that get_analyze_resolver raises an HTTPException with status code 500
    if an exception occurs (e.g., when fetching conversation data).
    """
    # Given
    conversation_id = str(ObjectId())  # Convert ObjectId to string
    
    # Simulate an exception during get_conversation_by_id
    with patch("app.packages.mongodb.get_conversation_by_id", new=AsyncMock(side_effect=Exception("Some error"))):
        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            await get_analyze_resolver(conversation_id)
        assert exc_info.value.status_code == 500
        assert "Internal server error while fetching data." in exc_info.value.detail
