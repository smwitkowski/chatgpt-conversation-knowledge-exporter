"""Pydantic models for topic discovery and assignment."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Topic(BaseModel):
    """A discovered topic with metadata."""

    topic_id: int
    name: str = Field(..., description="Short topic name (3-5 words)")
    description: str = Field(..., description="1-2 sentence description")
    keywords: List[str] = Field(default_factory=list, description="Top representative terms")
    representative_conversations: List[str] = Field(
        default_factory=list, description="conversation_ids that represent this topic"
    )
    centroid_embedding: Optional[List[float]] = Field(
        None, description="Embedding vector for topic centroid"
    )


class TopicRegistry(BaseModel):
    """Registry of discovered topics."""

    generated_at: str = Field(default_factory=lambda: datetime.now().isoformat())
    embedding_model: str
    num_topics: int
    topics: List[Topic]


class TopicAssignment(BaseModel):
    """A topic assignment for a conversation."""

    topic_id: int
    name: str
    score: float = Field(..., ge=0.0, le=1.0, description="Cosine similarity score 0-1")
    rank: Literal["primary", "secondary"]


class ConversationTopics(BaseModel):
    """Topic assignments for a conversation."""

    conversation_id: str
    title: str
    project_id: Optional[str] = None
    project_name: Optional[str] = None
    topics: List[TopicAssignment]
    atom_count: int
    review_flag: bool = Field(
        False, description="True if assignment needs human review"
    )
