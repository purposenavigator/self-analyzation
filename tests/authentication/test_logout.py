import pytest
from fastapi import Response
from unittest.mock import patch
from app.resolvers.user_resolvers import login, logout
from app.packages.schemas.user_schema import UserLogin

@pytest.fixture
def valid_user():
    return UserLogin(username="validuser", password="validpassword")

@patch("app.resolvers.user_resolvers.get_user")
@patch("app.resolvers.user_resolvers.verify_password")
@patch("app.resolvers.user_resolvers.create_access_token")
@pytest.mark.asyncio
async def test_login_and_logout(
        mock_create_access_token, 
        mock_verify_password, 
        mock_get_user, 
        valid_user
    ):
    # Mocking the login p
    mock_get_user.return_value = {"username": valid_user.username, "hashed_password": "hashed_password", "_id": "123"}
    mock_verify_password.return_value = True
    mock_create_access_token.return_value = "fake_token"
    
    login_response = Response()
    login_result = await login(valid_user, login_response)
    
    assert login_result["username"] == valid_user.username
    set_cookie_header = login_response.headers["set-cookie"]
    assert 'access_token="Bearer fake_token"; HttpOnly; Path=/; SameSite=lax' in set_cookie_header
    
    # Mocking the logout process
    logout_response = Response()
    logout_result = await logout(logout_response)
    
    assert logout_result["message"] == "Logged out successfully"
    assert "Bearer fake_token" not in logout_response.headers.get("set-cookie", "")
