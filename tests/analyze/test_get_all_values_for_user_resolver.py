import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from app.resolvers.analyze_resolvers import get_all_values_for_user_resolver
from app.packages.models.conversation_models import UserIdRequest

@pytest.mark.asyncio
@patch("app.resolvers.analyze_resolvers.extract_analysis_summaries", new_callable=AsyncMock)
@patch("app.packages.mongodb.fetch_user_data_from_db", new_callable=AsyncMock)
async def test_get_all_values_for_user_resolver(mock_fetch_user_data_from_db, mock_extract_analysis_summaries):
    # Mock the fetch_user_data_from_db function
    mock_fetch_user_data_from_db.return_value = [
        {"_id": "60d5ec49f1b2b2a5d4f1e8b1", "user_id": 1},
        {"_id": "60d5ec49f1b2b2a5d4f1e8b2", "user_id": 1},
        {"_id": "60d5ec49f1b2b2a5d4f1e8b3", "user_id": 1}  # No analysis_summaries
    ]

    # Mock the extract_analysis_summaries function
    mock_extract_analysis_summaries.return_value = [
        {"hash1": "summary1"},
        {"hash2": "summary2"}
    ]

    user_request = UserIdRequest(user_id=1)
    result = await get_all_values_for_user_resolver(user_request)

    assert result == [
        {"hash1": "summary1"},
        {"hash2": "summary2"}
    ]

@pytest.mark.asyncio
@patch("app.resolvers.analyze_resolvers.extract_analysis_summaries", new_callable=AsyncMock)
@patch("app.packages.mongodb.fetch_user_data_from_db", new_callable=AsyncMock)
async def test_get_all_values_for_user_resolver_no_data(mock_fetch_user_data_from_db, mock_extract_analysis_summaries):
    # Mock the fetch_user_data_from_db function to return no data
    mock_fetch_user_data_from_db.return_value = []

    # Mock the extract_analysis_summaries function
    mock_extract_analysis_summaries.return_value = []

    user_request = UserIdRequest(user_id=1)
    result = await get_all_values_for_user_resolver(user_request)

    assert result == []

@pytest.mark.asyncio
@patch("app.resolvers.analyze_resolvers.extract_analysis_summaries", new_callable=AsyncMock)
@patch("app.packages.mongodb.fetch_user_data_from_db", new_callable=AsyncMock)
async def test_get_all_values_for_user_resolver_internal_error(mock_fetch_user_data_from_db, mock_extract_analysis_summaries):
    # Mock the fetch_user_data_from_db function to raise an exception
    mock_fetch_user_data_from_db.side_effect = Exception("Database error")

    user_request = UserIdRequest(user_id=1)

    with pytest.raises(HTTPException) as exc_info:
        await get_all_values_for_user_resolver(user_request)

    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Internal server error while fetching data."

if __name__ == "__main__":
    import asyncio
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    pytest.main()
