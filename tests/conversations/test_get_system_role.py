from unittest.mock import patch
from fastapi import HTTPException
import pytest

from app.services.get_system_role import get_system_role
from app.openai_resolvers.keyword_extraction import adviser_prompts

@patch('app.data.questions.questions', {"Test": "some test"})
@patch('app.services.get_system_role.create_summary_system_role')
@patch('app.services.get_system_role.create_question_system_role')
@patch('app.services.get_system_role.create_answers_system_role')
def test_get_system_role(
    mock_create_question_system_role, 
    mock_create_summary_system_role, 
    mock_create_answers_system_role
    ):
    question = 'Test'
    mock_value = "some test content"
    mock_create_question_system_role.return_value = mock_value
    mock_create_summary_system_role.return_value = mock_value
    mock_create_answers_system_role.return_value = mock_value

    result = get_system_role(question)

    assert result == {
        'question': {'role': 'system', 'content': mock_value}, 
        'summary': {'role': 'system', 'content': mock_value},
        'analyze': {'role': 'system', 'content': adviser_prompts},
        'answers': {'role': 'system', 'content': mock_value}
        }

@patch('app.data.questions.questions', {"Test": "some test"})
def test_get_system_role_invalid_topic():
    question = 'Something'

    with pytest.raises(HTTPException) as excinfo:
        get_system_role(question)
    
    assert excinfo.value.status_code == 500
    assert "Invalid topic" in excinfo.value.detail
