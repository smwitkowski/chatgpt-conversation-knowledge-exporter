"""DSPy signature and program for meeting atom extraction."""

import json
from typing import Any, Dict, List

try:
    import dspy
except ImportError:
    dspy = None  # type: ignore


if dspy:
    class ExtractMeetingAtoms(dspy.Signature):  # type: ignore
        """
        Extract universal atoms from meeting notes (Google Meet format).

        Extracts:
        - Meeting topics (key discussion topics)
        - Meeting decisions (with decided_by framing)
        - Action items / commitments (from checklists and commitment language)
        - Risks / blockers / dependencies (with closeable status)
        - Open questions (with consulting extensions: asked_of, owner)

        Args:
            conversation_id: Conversation identifier
            meeting_title: Meeting title
            meeting_metadata_json: JSON string of parsed meeting metadata
            linearized_content: Full linearized meeting content (notes + transcript)
            atoms_json: Universal atoms as JSON array string (schema v2)
            inferred_metadata_json: Inferred/refined metadata (meeting_kind, client_name, project_name) as JSON
        """

        conversation_id: str = dspy.InputField(desc="Conversation identifier")
        meeting_title: str = dspy.InputField(desc="Meeting title")
        meeting_metadata_json: str = dspy.InputField(desc="JSON string of parsed meeting metadata")
        linearized_content: str = dspy.InputField(desc="Full linearized meeting content")
        atoms_json: str = dspy.OutputField(
            desc="Universal atoms (schema v2) as JSON array. Each atom must have: schema_version=2, kind, statement, topic (optional), status, status_confidence (explicit|inferred|null), evidence[], extracted_at, meta{}"
        )
        inferred_metadata_json: str = dspy.OutputField(
            desc="Inferred metadata as JSON: {meeting_kind: internal|client|mixed|unknown, client_name?: string, project_name?: string}"
        )
else:
    # Placeholder when dspy is not installed
    class ExtractMeetingAtoms:  # type: ignore
        pass


def create_extract_meeting_atoms_program(lm: "dspy.LM") -> "dspy.Module":
    """
    Create a DSPy program for meeting atom extraction.

    Args:
        lm: Configured DSPy language model

    Returns:
        DSPy module for meeting extraction
    """
    if dspy is None:
        raise ImportError("dspy-ai is not installed. Install it with: uv sync --extra dspy")

    # Set the LM with LangSmith tracing if enabled
    from ck_exporter.observability.langsmith import configure_dspy_with_langsmith
    configure_dspy_with_langsmith(lm)

    # Create a chain-of-thought program
    class ExtractMeetingAtomsProgram(dspy.Module):
        def __init__(self):
            super().__init__()
            self.extractor = dspy.ChainOfThought(ExtractMeetingAtoms)

        def forward(
            self,
            conversation_id: str,
            meeting_title: str,
            meeting_metadata_json: str,
            linearized_content: str,
        ) -> Dict[str, Any]:
            result = self.extractor(
                conversation_id=conversation_id,
                meeting_title=meeting_title,
                meeting_metadata_json=meeting_metadata_json,
                linearized_content=linearized_content,
            )
            # Parse JSON outputs
            try:
                atoms = json.loads(result.atoms_json) if result.atoms_json else []
                inferred_metadata = json.loads(result.inferred_metadata_json) if result.inferred_metadata_json else {}
            except json.JSONDecodeError:
                # Fallback: return empty
                atoms = []
                inferred_metadata = {}

            return {
                "atoms": atoms,
                "inferred_metadata": inferred_metadata,
            }

    return ExtractMeetingAtomsProgram()


def extract_meeting_atoms_with_dspy(
    conversation: Dict[str, Any],
    conversation_id: str,
    meeting_metadata: Dict[str, Any],
    linearized_content: str,
    dspy_program: Any,
) -> Dict[str, Any]:
    """
    Extract meeting atoms using DSPy program.

    Args:
        conversation: Conversation dict
        meeting_metadata: Parsed meeting metadata
        linearized_content: Full linearized content
        dspy_program: Configured DSPy program

    Returns:
        Dict with "atoms" (list) and "inferred_metadata" (dict)
    """
    meeting_title = meeting_metadata.get("meeting_title", conversation.get("title", "Unknown Meeting"))

    result = dspy_program.forward(
        conversation_id=conversation_id,
        meeting_title=meeting_title,
        meeting_metadata_json=json.dumps(meeting_metadata),
        linearized_content=linearized_content,
    )

    return result

