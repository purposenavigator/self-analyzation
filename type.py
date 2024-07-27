
from typing import Optional
from pydantic import BaseModel

class GPTRequest(BaseModel):
    user_id: int
    conversation_id: Optional[int] = None
    prompt: str
    topic: str
    max_tokens: int = 150

class Query:
    def __init__(self, user_id: int, conversation_id: int):
        self.user_id = user_id
        self.conversation_id = conversation_id

    def __repr__(self):
        return f"Query(user_id={self.user_id}, conversation_id={self.conversation_id})"

