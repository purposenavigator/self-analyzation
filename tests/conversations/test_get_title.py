import pytest
from unittest.mock import AsyncMock, patch

from app.openai_resolvers.get_title import ask_title, create_client_role, retrieve_title, get_title

# Mock data
mock_sentences = [
    "This project focuses on creating a better user interface.",
    "It should be user-friendly and accessible.",
    "The design should also reflect modern aesthetics."
]

class MockMessage:
    def __init__(self, content):
        self.content = content

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

mock_response = MockResponse(choices=[MockChoice(message=MockMessage(content="User-Friendly Interface Design for Modern Aesthetics"))])

class AsyncMockMessage(AsyncMock):
    def __init__(self, content):
        super().__init__()
        self.content = content

class AsyncMockChoice(AsyncMock):
    def __init__(self, message):
        super().__init__()
        self.message = message

class AsyncMockResponse(AsyncMock):
    def __init__(self, choices):
        super().__init__()
        self.choices = choices

# Define the async mock response structure
async_mock_response = AsyncMockResponse(choices=[AsyncMockChoice(message=AsyncMockMessage(content="User-Friendly Interface Design for Modern Aesthetics"))])


# Test `create_client_role` function
def test_create_client_role():
    expected_output = {
        "role": "user",
        "content": "This project focuses on creating a better user interface. It should be user-friendly and accessible. The design should also reflect modern aesthetics."
    }
    assert create_client_role(mock_sentences) == expected_output

# Test `retrieve_title` function
def test_retrieve_title():
    assert retrieve_title(mock_response) == "User-Friendly Interface Design for Modern Aesthetics"

# Test `ask_title` function with mock
@pytest.mark.asyncio
async def test_ask_title():
    with patch("app.openai_resolvers.get_title.client.chat.completions.create", new_callable=AsyncMock) as mock_create:
        mock_create.return_value = mock_response
        response = await ask_title(mock_sentences)
        assert response == mock_response
        mock_create.assert_called_once_with(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are a title generation assistant. Your task is to read through a set of sentences provided by the user and create a concise, compelling, and relevant title that captures the main theme or purpose of the sentences. Ensure that the title is engaging and aligns with the content, using language that is clear and impactful. Avoid using overly complex or ambiguous words, and aim for a length of no more than 8-10 words unless otherwise specified."
                },
                {
                    "role": "user",
                    "content": "This project focuses on creating a better user interface. It should be user-friendly and accessible. The design should also reflect modern aesthetics."
                }
            ]
        )

@pytest.mark.asyncio
async def test_get_title():
    with patch("app.openai_resolvers.get_title.ask_title", new_callable=AsyncMock) as mock_ask_title:
        mock_ask_title.return_value = async_mock_response
        title = await get_title(mock_sentences)  # mock_sentences should be defined as needed
        assert title == retrieve_title(mock_response)
