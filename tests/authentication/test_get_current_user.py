import pytest
from fastapi import HTTPException, Request
from unittest.mock import patch
from app.packages.repositories.user.auth import get_current_user

@pytest.fixture
def mock_request():
    class MockRequest:
        def __init__(self, cookies):
            self.cookies = cookies
    return MockRequest

@pytest.mark.asyncio
async def test_get_current_user_without_login(mock_request):
    request = mock_request(cookies={})
    
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"

@patch("app.packages.repositories.user.auth.get_user")
@patch("app.packages.repositories.user.auth.jwt.decode")
@pytest.mark.asyncio
async def test_get_current_user_with_login(mock_jwt_decode, mock_get_user, mock_request):
    mock_jwt_decode.return_value = {"sub": "validuser"}
    mock_get_user.return_value = {"username": "validuser", "_id": "123"}
    
    request = mock_request(cookies={"access_token": "Bearer fake_token"})
    result = await get_current_user(request)
    
    assert result["username"] == "validuser"
    assert result["id"] == "123"

@patch("app.packages.repositories.user.auth.get_user")
@patch("app.packages.repositories.user.auth.jwt.decode")
@pytest.mark.asyncio
async def test_get_current_user_with_login_and_logout(mock_jwt_decode, mock_get_user, mock_request):
    mock_jwt_decode.return_value = {"sub": "validuser"}
    mock_get_user.return_value = {"username": "validuser", "_id": "123"}
    
    # Simulate login
    request = mock_request(cookies={"access_token": "Bearer fake_token"})
    result = await get_current_user(request)
    
    assert result["username"] == "validuser"
    assert result["id"] == "123"
    
    # Simulate logout by clearing the cookie
    request = mock_request(cookies={})
    with pytest.raises(HTTPException) as exc_info:
        await get_current_user(request)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Not authenticated"
