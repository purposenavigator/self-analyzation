from typing import List, Optional
from pydantic import BaseModel

from type import Message


class GPTRequest(BaseModel):
    user_id: int
    conversation_id: Optional[int] = None
    prompt: str
    topic: str
    max_tokens: int = 150

class ConversationQuery:
    def __init__(self, user_id: int, conversation_id: int):
        self.user_id = user_id
        self.conversation_id = conversation_id

    def __repr__(self):
        return f"Query(user_id={self.user_id}, conversation_id={self.conversation_id})"

class UserConversation:
    def __init__(
            self, user_id: int, 
            conversation_id: int, 
            summaries: List[Message],
            questions: List[Message],
            ):
        self.user_id = user_id
        self.conversation_id = conversation_id
        self.summaries = summaries
        self.questions = questions