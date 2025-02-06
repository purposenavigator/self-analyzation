import pytest
from fastapi import HTTPException, Response
from unittest.mock import patch
from app.resolvers.user_resolvers import login
from app.packages.schemas.user_schema import UserLogin

@pytest.fixture
def valid_user():
    return UserLogin(username="validuser", password="validpassword")

@pytest.fixture
def invalid_user():
    return UserLogin(username="invaliduser", password="invalidpassword")

@patch("app.resolvers.user_resolvers.get_user")
@patch("app.resolvers.user_resolvers.verify_password")
@patch("app.resolvers.user_resolvers.create_access_token")
@pytest.mark.asyncio
async def test_login_valid_user(
        mock_create_access_token, 
        mock_verify_password, 
        mock_get_user, 
        valid_user
    ):
    mock_get_user.return_value = {"username": valid_user.username, "hashed_password": "hashed_password", "_id": "123"}
    mock_verify_password.return_value = True
    mock_create_access_token.return_value = "fake_token"
    
    response = Response()
    result = await login(valid_user, response)
    
    assert result["username"] == valid_user.username
    assert result["id"] == "123"
    set_cookie_header = response.headers["set-cookie"]
    assert 'access_token="Bearer fake_token"; HttpOnly; Path=/; SameSite=lax' in set_cookie_header

@patch("app.resolvers.user_resolvers.get_user")
@patch("app.resolvers.user_resolvers.verify_password")
@pytest.mark.asyncio
async def test_login_invalid_user(mock_verify_password, mock_get_user, invalid_user):
    mock_get_user.return_value = None
    mock_verify_password.return_value = False
    
    response = Response()
    with pytest.raises(HTTPException) as exc_info:
        await login(invalid_user, response)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"

@patch("app.resolvers.user_resolvers.get_user")
@patch("app.resolvers.user_resolvers.verify_password")
@pytest.mark.asyncio
async def test_login_correct_username_incorrect_password(mock_verify_password, mock_get_user):
    user = UserLogin(username="validuser", password="wrongpassword")
    mock_get_user.return_value = {"username": user.username, "hashed_password": "hashed_password", "_id": "123"}
    mock_verify_password.return_value = False
    
    response = Response()
    with pytest.raises(HTTPException) as exc_info:
        await login(user, response)
    
    assert exc_info.value.status_code == 401
    assert exc_info.value.detail == "Invalid credentials"
