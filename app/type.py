from typing import TypedDict, List, Dict, Optional
from bson import ObjectId
from dataclasses import dataclass, field
from datetime import datetime, timezone

@dataclass
class Message:
    role: str
    content: str

@dataclass
class Evaluation:
    label: str
    percentage: str

@dataclass
class AttributeExplanation:
    attribute: str
    explanation: str
    evaluation: Evaluation

@dataclass
class AnalyzeSummary:
    analyze_summary_text: str
    analyze_values: AttributeExplanation

@dataclass
class Conversation:
    _id: Optional[ObjectId] = None
    user_id: str = ""
    conversation_id: str = ""
    topic: str = ""
    summaries: List[Message] = field(default_factory=list)
    questions: List[Message] = field(default_factory=list)
    # Renamed 'analyzes' to 'analyze' to match your UserConversation.
    analyze: List[Message] = field(default_factory=list)
    # If you need a new field like 'answers'
    answers: List[Message] = field(default_factory=list)
    title: Optional[str] = None
    created_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = field(default_factory=lambda: datetime.now(timezone.utc))
    status: str = "active"
    is_favorite: bool = False
    deleted_at: Optional[datetime] = None
    # Detailed analysis summaries (optional, if needed)
    analysis_summaries: Dict[str, AnalyzeSummary] = field(default_factory=dict)


class SystemRole(TypedDict):
    role: str
    content: str

class SystemRoles(TypedDict):
    summary: SystemRole
    question: SystemRole
    analyze: SystemRole

class Excract(TypedDict):
    extract: SystemRole

class FlattenedAnalysisSummary(TypedDict):
    attribute: str
    explanation: str
    evaluation: Evaluation

class ConsolidatedAttribute(TypedDict):
    attribute: str
    explanation: str
    mean: float
    count: int
    relevance_score: float

class LabeledAttribute(TypedDict):
    attribute: str
    explanation: str
    mean: float
    count: int
    relevance_score: float
    label: str
