
from typing import NotRequired
from typing import TypedDict, List
from bson import ObjectId

class Message(TypedDict):
    role: str
    content: str

class Conversation(TypedDict):
    _id: NotRequired[ObjectId]
    user_id: int
    messages: List[Message]
