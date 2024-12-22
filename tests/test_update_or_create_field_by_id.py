
from app.mongodb import update_or_append_field_by_id
import pytest
from unittest.mock import MagicMock, patch

# Replace 'your_module' with the actual module name where your function is located

@pytest.mark.asyncio
@patch("app.mongodb.collection")
async def test_update_or_append_field_by_id(mock_collection):
    # Mock the return value of update_one
    mock_update_result = MagicMock(matched_count=1, modified_count=1)
    mock_collection.update_one.return_value = mock_update_result
    
    conversation_id = "fake_conversation_id"
    field_name = "test_field"
    new_object = {"some_key": "some_value"}

    # Call the async function
    await update_or_append_field_by_id(conversation_id, field_name, new_object)

    # Verify update_one was called with the correct arguments
    mock_collection.update_one.assert_called_once_with(
        {"conversation_id": conversation_id},
        {
            "$setOnInsert": {field_name: []},
            "$push": {field_name: new_object}
        },
        upsert=True
    )

    # Optionally, verify matched_count and modified_count if needed
    assert mock_update_result.matched_count == 1
    assert mock_update_result.modified_count == 1
