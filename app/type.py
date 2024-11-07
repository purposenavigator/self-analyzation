
from typing import NotRequired
from typing import TypedDict, List
from bson import ObjectId

class Message(TypedDict):
    role: str
    content: str

class Conversation(TypedDict):
    _id: NotRequired[ObjectId]
    user_id: int
    summaries: List[Message]
    questions: List[Message]
    analyzes: List[Message]
    keywords: List[Message]
    topic: str
    title: NotRequired[str]
    created_at: NotRequired[str]
    updated_at: NotRequired[str]
    status: NotRequired[str]
    is_favorite: NotRequired[bool]
    deleted_at: NotRequired[str]

class SystemRole(TypedDict):
    role: str
    content: str

class SystemRoles(TypedDict):
    summary: SystemRole
    question: SystemRole
    analyze: SystemRole

class Excract(TypedDict):
    extract: SystemRole