"""Pydantic models for knowledge atoms."""

from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, Field


class Evidence(BaseModel):
    """Evidence pointer linking an atom back to source messages."""

    message_id: Optional[str] = None
    time_iso: Optional[str] = None
    text_snippet: Optional[str] = Field(None, description="Relevant snippet from the message")


class Atom(BaseModel):
    """A knowledge atom extracted from conversation."""

    type: Literal[
        "decision",
        "requirement",
        "definition",
        "metric",
        "risk",
        "assumption",
        "constraint",
        "idea",
        "fact",
    ]
    topic: str = Field(..., description="Topic category (e.g., 'pricing', 'architecture', 'ICP')")
    statement: str = Field(..., description="The actual knowledge statement")
    status: Literal["active", "deprecated", "uncertain"] = "active"
    evidence: List[Evidence] = Field(default_factory=list)
    extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat())


class DecisionAtom(Atom):
    """A decision atom with additional context."""

    type: Literal["decision"] = "decision"
    alternatives: List[str] = Field(default_factory=list, description="Alternatives considered")
    rationale: Optional[str] = Field(None, description="Why this decision was made")
    consequences: Optional[str] = Field(None, description="Expected consequences")


class OpenQuestion(BaseModel):
    """An open question or uncertainty."""

    question: str
    topic: str
    context: Optional[str] = None
    evidence: List[Evidence] = Field(default_factory=list)
    extracted_at: str = Field(default_factory=lambda: datetime.now().isoformat())
