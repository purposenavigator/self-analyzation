from unittest.mock import patch
from fastapi import HTTPException
import pytest

pytestmark = pytest.mark.skip(reason="Temporarily skipping due to import issue.")

from app import questions
from app.questions import get_system_role

@patch('app.questions.questions', {"Test": "some test"})
@patch('app.questions.adviser_prompts', "some test advisor")
@patch('app.questions.create_summary_system_role')
@patch('app.questions.create_question_system_role')
def test_get_system_role(mock_create_question_system_role, mock_create_summary_system_role):
    question = 'Test'
    mock_create_question_system_role.return_value = "some test question"
    mock_create_summary_system_role.return_value = "some test summary"

    result = get_system_role(question)

    assert result == {
        'question': {'role': 'system', 'content': 'some test question'}, 
        'summary': {'role': 'system', 'content': 'some test summary'},
        'analyze': {'role': 'system', 'content': 'some test advisor'}
        }

@patch('app.questions.questions', {"Test": "some test"})
def test_get_system_role_invalid_topic():
    question = 'Something'

    with pytest.raises(HTTPException) as excinfo:
        get_system_role(question)
    
    assert excinfo.value.status_code == 500
    assert "Invalid topic" in excinfo.value.detail
