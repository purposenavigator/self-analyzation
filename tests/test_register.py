import pytest
from fastapi import HTTPException, Response
from unittest.mock import patch
from app.resolvers.user_resolvers import register
from app.packages.schemas.user_schema import UserCreate

@pytest.fixture
def new_user():
    return UserCreate(username="newuser", password="newpassword")

@pytest.fixture
def existing_user():
    return UserCreate(username="existinguser", password="existingpassword")

@patch("app.resolvers.user_resolvers.get_user")
@patch("app.resolvers.user_resolvers.create_user")
@patch("app.resolvers.user_resolvers.create_access_token")
@patch("app.resolvers.user_resolvers.hash_password")
@pytest.mark.asyncio
async def test_register_new_user(
        mock_hash_password, 
        mock_create_access_token, 
        mock_create_user, 
        mock_get_user, 
        new_user
    ):
    mock_get_user.return_value = None
    mock_create_user.return_value = {"username": new_user.username}
    mock_create_access_token.return_value = "fake_token"
    mock_hash_password.return_value = "hashed_password"
    
    response = Response()
    result = await register(new_user, response)
    
    assert result["username"] == new_user.username
    set_cookie_header = response.headers["set-cookie"]
    assert 'access_token="Bearer fake_token"; HttpOnly; Path=/; SameSite=lax; Secure' in set_cookie_header

@patch("app.resolvers.user_resolvers.get_user")
@pytest.mark.asyncio
async def test_register_existing_user(mock_get_user, existing_user):
    mock_get_user.return_value = {"username": existing_user.username}
    
    response = Response()
    with pytest.raises(HTTPException) as exc_info:
        await register(existing_user, response)
    
    assert exc_info.value.status_code == 400
    assert exc_info.value.detail == "Username already taken"