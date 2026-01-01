"""Pydantic models for knowledge atoms.

Universal Atom Base (v2): Stable schema with versioning and extensible meta namespace.
Domain-specific views: Typed projections for meetings vs AI vs docs.
"""

from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Evidence pointer linking an atom back to source messages."""

    message_id: Optional[str] = None
    time_iso: Optional[str] = None
    text_snippet: Optional[str] = Field(None, description="Relevant snippet from the message")
    conversation_id: Optional[str] = Field(None, description="Source conversation ID (added during consolidation)")


class Atom(BaseModel):
    """Universal knowledge atom (schema v2).

    Stable base contract for all knowledge extraction across meetings, AI conversations, and documents.
    Domain-specific semantics are stored in the `meta` namespace to avoid schema churn.
    """

    schema_version: int = Field(default=2, description="Schema version for forward compatibility")
    kind: Literal[
        "fact",
        "decision",
        "open_question",
        "action_item",
        "meeting_topic",
        "risk",
        "blocker",
        "dependency",
        "deliverable",
        "milestone",
        # Legacy types mapped to kind
        "requirement",
        "definition",
        "metric",
        "assumption",
        "constraint",
        "idea",
    ] = Field(..., description="Coarse atom category")
    statement: str = Field(..., description="The knowledge statement (or question text for open_question)")
    topic: Optional[str] = Field(None, description="Topic category (optional, used where meaningful)")
    status: str = Field(default="active", description="Status (string for forward compatibility)")
    status_confidence: Optional[Literal["explicit", "inferred"]] = Field(
        None, description="Whether status was explicitly stated or inferred"
    )
    evidence: List[Evidence] = Field(default_factory=list, description="Evidence pointers to source messages")
    extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="Extraction timestamp")
    meta: Dict[str, Any] = Field(default_factory=dict, description="Domain-specific metadata namespace")

    class Config:
        extra = "allow"  # Allow extra fields for backward compatibility during migration


# ============================================================================
# Typed Views (Pydantic subclasses for domain-specific usage)
# ============================================================================


class DecisionAtom(Atom):
    """Decision atom view with decision-specific fields in meta."""

    kind: Literal["decision"] = "decision"

    @property
    def alternatives(self) -> List[str]:
        """Alternatives considered."""
        return self.meta.get("decision", {}).get("alternatives", [])

    @property
    def rationale(self) -> Optional[str]:
        """Why this decision was made."""
        return self.meta.get("decision", {}).get("rationale")

    @property
    def consequences(self) -> Optional[str]:
        """Expected consequences."""
        return self.meta.get("decision", {}).get("consequences")


class MeetingDecisionAtom(DecisionAtom):
    """Meeting decision atom with meeting-specific framing."""

    @property
    def decided_by(self) -> Optional[Literal["client", "consultant", "joint", "unknown"]]:
        """Who made the decision (meeting context)."""
        return self.meta.get("meeting", {}).get("decision", {}).get("decided_by")


class OpenQuestionAtom(Atom):
    """Open question atom view."""

    kind: Literal["open_question"] = "open_question"

    @property
    def question(self) -> str:
        """Question text (aliased from statement)."""
        return self.statement

    @property
    def context(self) -> Optional[str]:
        """Additional context for the question."""
        return self.meta.get("question", {}).get("context")


class MeetingOpenQuestionAtom(OpenQuestionAtom):
    """Meeting open question with consulting-friendly extensions."""

    @property
    def asked_of(self) -> Optional[Literal["client", "internal", "vendor", "unknown"]]:
        """Who should answer this question."""
        return self.meta.get("meeting", {}).get("question", {}).get("asked_of")

    @property
    def owner(self) -> Optional[str]:
        """Person/team responsible for answering."""
        return self.meta.get("meeting", {}).get("question", {}).get("owner")


class ActionItemAtom(Atom):
    """Action item / task atom view."""

    kind: Literal["action_item"] = "action_item"

    @property
    def owner(self) -> Optional[str]:
        """Task owner (person/team)."""
        return self.meta.get("task", {}).get("owner") or self.meta.get("meeting", {}).get("task", {}).get("owner")

    @property
    def due(self) -> Optional[str]:
        """Due date/time (free text for v1)."""
        return self.meta.get("task", {}).get("due") or self.meta.get("meeting", {}).get("task", {}).get("due")


class RiskAtom(Atom):
    """Risk atom view (closeable)."""

    kind: Literal["risk"] = "risk"

    @property
    def owner(self) -> Optional[str]:
        """Risk owner (person/team)."""
        return self.meta.get("issue", {}).get("owner")


class BlockerAtom(Atom):
    """Blocker atom view (closeable)."""

    kind: Literal["blocker"] = "blocker"

    @property
    def owner(self) -> Optional[str]:
        """Blocker owner (person/team)."""
        return self.meta.get("issue", {}).get("owner")

    @property
    def blocked_by(self) -> Optional[str]:
        """What is blocking this."""
        return self.meta.get("issue", {}).get("blocked_by")


class DependencyAtom(Atom):
    """Dependency atom view (closeable)."""

    kind: Literal["dependency"] = "dependency"

    @property
    def owner(self) -> Optional[str]:
        """Dependency owner (person/team)."""
        return self.meta.get("issue", {}).get("owner")

    @property
    def depends_on(self) -> Optional[str]:
        """What this depends on."""
        return self.meta.get("issue", {}).get("depends_on")


class MeetingTopicAtom(Atom):
    """Meeting topic atom view."""

    kind: Literal["meeting_topic"] = "meeting_topic"

    @property
    def summary(self) -> Optional[str]:
        """Optional summary of the topic discussion."""
        return self.meta.get("meeting", {}).get("topic", {}).get("summary")


class DeliverableAtom(Atom):
    """Deliverable atom view (project-level, no extraction yet)."""

    kind: Literal["deliverable"] = "deliverable"

    @property
    def due(self) -> Optional[str]:
        """Due date/time."""
        return self.meta.get("deliverable", {}).get("due")


class MilestoneAtom(Atom):
    """Milestone atom view (project-level, no extraction yet)."""

    kind: Literal["milestone"] = "milestone"

    @property
    def target_date(self) -> Optional[str]:
        """Target date."""
        return self.meta.get("milestone", {}).get("target_date")


# ============================================================================
# Legacy models (for backward compatibility during migration)
# ============================================================================

# Keep these for now to avoid breaking imports, but they're deprecated
# New code should use Universal Atom + views


class OpenQuestion(BaseModel):
    """Legacy open question model (deprecated, use OpenQuestionAtom)."""

    question: str
    topic: str
    context: Optional[str] = None
    evidence: List[Evidence] = Field(default_factory=list)
    extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class ActionItem(BaseModel):
    """Legacy action item model (deprecated, use ActionItemAtom)."""

    statement: str = Field(..., description="The action item statement")
    evidence: List[Evidence] = Field(default_factory=list)
    extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat())
