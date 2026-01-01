"""Core domain models (re-export schemas)."""

# Re-export from canonical locations
from ck_exporter.core.models.atoms import (
    ActionItem,
    ActionItemAtom,
    Atom,
    BlockerAtom,
    DecisionAtom,
    DeliverableAtom,
    DependencyAtom,
    Evidence,
    MeetingDecisionAtom,
    MeetingOpenQuestionAtom,
    MeetingTopicAtom,
    MilestoneAtom,
    OpenQuestion,
    OpenQuestionAtom,
    RiskAtom,
)
from ck_exporter.core.models.topics import (
    ConversationTopics,
    Topic,
    TopicAssignment,
    TopicRegistry,
)

__all__ = [
    # Universal base
    "Atom",
    "Evidence",
    # View models
    "DecisionAtom",
    "MeetingDecisionAtom",
    "OpenQuestionAtom",
    "MeetingOpenQuestionAtom",
    "ActionItemAtom",
    "RiskAtom",
    "BlockerAtom",
    "DependencyAtom",
    "MeetingTopicAtom",
    "DeliverableAtom",
    "MilestoneAtom",
    # Legacy (deprecated)
    "ActionItem",
    "OpenQuestion",
    # Topics
    "Topic",
    "TopicRegistry",
    "TopicAssignment",
    "ConversationTopics",
]
