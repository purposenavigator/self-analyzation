import pytest
from fastapi.testclient import TestClient

import app
from app import questions


client = TestClient(app)

questions.questions = {
    "topic1": "explanation1",
    "topic2": "explanation2"
}

@pytest.mark.parametrize("topic, expected_status, expected_response", [
    ("topic1", 200, {"title": "topic1", "explanation": "explanation1"}),
    ("topic2", 200, {"title": "topic2", "explanation": "explanation2"}),
    ("unknown", 404, {"detail": "Topic 'unknown' not found."}),
])
def test_get_question(topic, expected_status, expected_response):
    response = client.get(f"/questions/{topic}")
    assert response.status_code == expected_status
    assert response.json() == expected_response

