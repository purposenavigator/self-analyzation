from app.packages.mongodb import update_or_append_field_by_id
import pytest
from unittest.mock import AsyncMock, patch
from bson import ObjectId


@pytest.mark.asyncio
@patch("app.packages.database.conversation_collection", new_callable=AsyncMock)
async def test_update_or_append_field_by_id(mock_collection):
    # Mock the return value of update_one
    mock_update_result = AsyncMock(matched_count=1, modified_count=1)
    mock_collection.update_one.return_value = mock_update_result
    
    conversation_id = str(ObjectId())  # Use a valid ObjectId
    field_name = "test_field"
    key = "some_key"
    value = "some_value"

    # Patch the function to use the mocked collection
    with patch("app.packages.mongodb.conversation_collection", mock_collection):
        # Call the async function
        await update_or_append_field_by_id(conversation_id, field_name, key, value)

    # Verify update_one was called with the correct arguments
    mock_collection.update_one.assert_called_once_with(
        {"_id": ObjectId(conversation_id)},
        {
            "$set": {f"{field_name}.{key}": value}
        },
        upsert=True
    )

    # Optionally, verify matched_count and modified_count if needed
    assert mock_update_result.matched_count == 1
    assert mock_update_result.modified_count == 1
