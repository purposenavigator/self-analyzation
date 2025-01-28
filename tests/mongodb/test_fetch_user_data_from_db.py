import pytest
from fastapi import HTTPException
from unittest.mock import AsyncMock, patch
from app.packages.mongodb import fetch_user_data_from_db

@pytest.mark.asyncio
@patch("app.packages.mongodb.conversation_collection.find")
async def test_fetch_user_data_from_db(mock_find):
    # Mock the find method to return user data
    mock_find.return_value.to_list = AsyncMock(return_value=[
        {"_id": "60d5ec49f1b2b2a5d4f1e8b1", "user_id": 1, "questions": ["question1"], "summaries": ["summary1"]},
        {"_id": "60d5ec49f1b2b2a5d4f1e8b2", "user_id": 1, "questions": ["question2"], "summaries": ["summary2"]}
    ])

    user_id = 1
    result = await fetch_user_data_from_db(user_id)

    assert result == [
        {"_id": "60d5ec49f1b2b2a5d4f1e8b1", "user_id": 1, "questions": ["question1"], "summaries": ["summary1"]},
        {"_id": "60d5ec49f1b2b2a5d4f1e8b2", "user_id": 1, "questions": ["question2"], "summaries": ["summary2"]}
    ]

@pytest.mark.asyncio
@patch("app.packages.mongodb.conversation_collection.find")
async def test_fetch_user_data_from_db_no_data(mock_find):
    # Mock the find method to return no data
    mock_find.return_value.to_list = AsyncMock(return_value=[])

    user_id = 1
    result = await fetch_user_data_from_db(user_id)

    assert result == []

@pytest.mark.asyncio
@patch("app.packages.mongodb.conversation_collection.find")
async def test_fetch_user_data_from_db_internal_error(mock_find):
    # Mock the find method to raise an exception
    mock_find.side_effect = Exception("Database error")

    user_id = 1

    with pytest.raises(HTTPException) as exc_info:
        await fetch_user_data_from_db(user_id)

    assert exc_info.value.status_code == 500
    assert str(exc_info.value.detail) == "Internal server error while fetching data."
