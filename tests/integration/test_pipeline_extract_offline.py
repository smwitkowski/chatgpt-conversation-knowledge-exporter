"""Integration tests for extraction pipeline (offline, using fake LLM)."""

import json
from pathlib import Path
from tempfile import TemporaryDirectory
from typing import Any

import pytest

from ck_exporter.adapters.openrouter_atom_extractor import OpenRouterAtomExtractor
from ck_exporter.core.ports.atom_extractor import AtomExtractor
from ck_exporter.core.ports.llm import LLMClient
from ck_exporter.pipeline.extract import extract_conversation


class FakeLLMClient:
    """Fake LLM client that returns canned responses."""

    def __init__(self, responses: dict[str, str]):
        """
        Initialize fake LLM client.

        Args:
            responses: Dict mapping (model, user_prompt_prefix) -> response_text
        """
        self.responses = responses
        self.call_count = 0

    def chat(
        self,
        model: str,
        system: str,
        user: str,
        *,
        temperature: float = 0.3,
        json_object: bool = False,
    ) -> str:
        """Return canned response based on model and user prompt."""
        self.call_count += 1
        # Look for matching response by checking if user prompt contains key phrases
        for (resp_model, key_phrase), response in self.responses.items():
            if resp_model == model and key_phrase in user:
                return response
        # Default response
        return json.dumps({"facts": [], "decisions": [], "open_questions": []})


@pytest.fixture
def fake_llm_client():
    """Create a fake LLM client with canned responses."""
    # Pass 1 response (fast extraction)
    pass1_response = json.dumps({
        "facts": [
            {
                "type": "fact",
                "topic": "testing",
                "statement": "This is a test fact",
                "status": "active",
                "evidence": [{"message_id": "msg-1", "time_iso": "2025-01-01T00:00:00"}],
            }
        ],
        "decisions": [],
        "open_questions": [],
    })

    # Pass 2 response (refinement)
    pass2_response = json.dumps({
        "facts": [
            {
                "type": "fact",
                "topic": "testing",
                "statement": "This is a test fact",
                "status": "active",
                "evidence": [{"message_id": "msg-1", "time_iso": "2025-01-01T00:00:00"}],
            }
        ],
        "decisions": [],
        "open_questions": [],
    })

    responses = {
        ("z-ai/glm-4.7", "Conversation chunk:"): pass1_response,
        ("z-ai/glm-4.7", "Candidates to refine:"): pass2_response,
    }
    return FakeLLMClient(responses)


@pytest.fixture
def sample_conversation():
    """Create a sample conversation dict."""
    return {
        "id": "test-conv-1",
        "conversation_id": "test-conv-1",
        "title": "Test Conversation",
        "mapping": {
            "msg-1": {
                "id": "msg-1",
                "parent": None,
                "message": {
                    "id": "msg-1",
                    "author": {"role": "user"},
                    "create_time": 1704067200.0,
                    "content": {"parts": ["Hello, this is a test message."]},
                },
            }
        },
        "current_node": "msg-1",
    }


def test_extract_conversation_creates_outputs(
    fake_llm_client: FakeLLMClient, sample_conversation: dict[str, Any], tmp_path: Path
):
    """Test that extraction creates expected JSONL output files."""
    # Create fake extractor
    fast_llm = fake_llm_client
    big_llm = fake_llm_client
    extractor: AtomExtractor = OpenRouterAtomExtractor(
        fast_llm=fast_llm, big_llm=big_llm, fast_model="z-ai/glm-4.7", big_model="z-ai/glm-4.7"
    )

    evidence_dir = tmp_path / "evidence"
    atoms_dir = tmp_path / "atoms"
    evidence_dir.mkdir()
    atoms_dir.mkdir()

    # Create evidence file
    evidence_path = evidence_dir / "test-conv-1" / "conversation.md"
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_text("# Test Conversation\n\n## User\n\nHello, this is a test message.\n\n")

    # Run extraction
    extract_conversation(
        conversation=sample_conversation,
        evidence_dir=evidence_dir,
        atoms_dir=atoms_dir,
        extractor=extractor,
        skip_existing=False,
    )

    # Check outputs
    facts_path = atoms_dir / "test-conv-1" / "facts.jsonl"
    assert facts_path.exists()

    # Read and verify structure
    facts = []
    with facts_path.open() as f:
        for line in f:
            if line.strip():
                facts.append(json.loads(line))

    assert len(facts) > 0
    assert "statement" in facts[0]
    assert "type" in facts[0]
