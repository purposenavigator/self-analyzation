from typing import List, Optional
from pydantic import BaseModel

from app.type import Message


class GPTRequest(BaseModel):
    user_id: int
    conversation_id: Optional[str] = None
    prompt: str
    topic: str
    max_tokens: int = 150

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
            ):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.topic = topic
        self.summaries = summaries
        self.questions = questions