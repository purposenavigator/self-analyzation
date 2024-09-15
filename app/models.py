from typing import List, Optional
from pydantic import BaseModel

from app.type import Message


class GPTRequest(BaseModel):
    user_id: int
    conversation_id: Optional[str] = None
    prompt: str
    topic: str
    max_tokens: int = 150

class UserConversationRequest(BaseModel):
    user_id: int
    conversation_id: str

class SimpleConversationQuery:
    def __init__(self, user_id: int, conversation_id: str):
        self.user_id = user_id
        self.conversation_id = conversation_id

class UserConversationQuery:
    """
    UserConversationQuery is used to retrieve conversation history between the user and the OpenAI GPT API
    from the database. It holds the necessary attributes to query the conversation history.

    Attributes:
        user_id (int): The ID of the user.
        topic (str): The topic of the conversation.
        conversation_id (Optional[str]): The ID of the conversation. This is used for querying specific conversation history.
    """

    def __init__(self, user_id: int, topic: str, conversation_id: Optional[str] = None):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.topic = topic

class UserConversation:
    def __init__(
            self, user_id: int, 
            conversation_id: str, 
            topic: str,
            summaries: List[Message],
            questions: List[Message],
            analyze: List[Message],
            ):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.topic = topic
        self.summaries = summaries
        self.questions = questions
        self.analyze = analyze

class AnalayzeRequest(BaseModel):
    conversation_id: str


class AnalyzeQuery:
    def __init__(self, conversation_id: str):
        self.conversation_id = conversation_id

class Analyze:
    def __init__(self, conversation_id: str, analyze: List[Message]):
        self.conversation_id = conversation_id
        self.analyze = analyze

class Extract:
    def __init__(
            self, 
            user_id: int, 
            conversation_id: str, 
            extract: List[Message],
            ):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.extract = extract

