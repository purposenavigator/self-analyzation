from fastapi import HTTPException
import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.packages.schemas.user_schema import UserCreate
from unittest.mock import patch

client = TestClient(app)

@pytest.fixture
def new_user():
    return UserCreate(username="testuser", password="testpassword")

@pytest.fixture
def existing_user():
    return UserCreate(username="existinguser", password="existingpassword")

@patch("app.main.register")
def test_register_new_user(mock_register, new_user):
    mock_register.return_value = {"username": new_user.username}
    response = client.post("/register", json=new_user.model_dump())
    assert response.status_code == 200
    assert response.json()["username"] == new_user.username

@patch("app.main.register")
def test_register_existing_user(mock_register, existing_user):
    mock_register.side_effect = HTTPException(
        status_code=400, detail="Username already taken"
    )
    
    # Attempt to register the same user again
    response = client.post("/register", json=existing_user.model_dump ())
    assert response.status_code == 400
    assert response.json()["detail"] == "Username already taken"
