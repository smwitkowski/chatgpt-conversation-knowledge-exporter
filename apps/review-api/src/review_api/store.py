"""KnowledgeStore: loads and indexes topic/conversation/atom data."""

import json
import sys
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

# Add parent src to path for ck_exporter imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from ck_exporter.atoms_schema import Atom, DecisionAtom, OpenQuestion
from ck_exporter.topic_schema import ConversationTopics, Topic, TopicAssignment, TopicRegistry


class KnowledgeStore:
    """Read-only store that loads and indexes knowledge artifacts."""

    def __init__(self, base_path: Path):
        """
        Initialize store from base directory containing output/, docs/, _atoms/, _evidence/.

        Args:
            base_path: Root directory of the project (should contain output/, docs/, etc.)
        """
        self.base_path = Path(base_path).resolve()
        self.output_dir = self.base_path / "output"
        self.docs_dir = self.base_path / "docs"
        self.atoms_dir = self.base_path / "_atoms"
        self.evidence_dir = self.base_path / "_evidence"

        # In-memory indexes
        self.topics: Dict[int, Topic] = {}
        self.topic_registry: Optional[TopicRegistry] = None
        self.assignments: Dict[str, ConversationTopics] = {}
        self.review_queue: List[Dict[str, Any]] = []
        self.conversation_index: Dict[str, Dict[str, Any]] = {}
        self.topic_to_conversations: Dict[int, List[str]] = defaultdict(list)

        self._load_all()

    def _load_all(self) -> None:
        """Load all data sources and build indexes."""
        # Load topic registry
        registry_path = self.output_dir / "topic_registry.json"
        if registry_path.exists():
            with registry_path.open("r", encoding="utf-8") as f:
                data = json.load(f)
                self.topic_registry = TopicRegistry(**data)
                for topic in self.topic_registry.topics:
                    self.topics[topic.topic_id] = topic

        # Load assignments
        assignments_path = self.output_dir / "assignments.jsonl"
        if assignments_path.exists():
            with assignments_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        data = json.loads(line)
                        assignment = ConversationTopics(**data)
                        self.assignments[assignment.conversation_id] = assignment

                        # Build topic -> conversations index
                        for topic_assignment in assignment.topics:
                            if topic_assignment.rank == "primary":
                                self.topic_to_conversations[topic_assignment.topic_id].append(
                                    assignment.conversation_id
                                )
                    except (json.JSONDecodeError, Exception) as e:
                        continue

        # Load review queue
        review_path = self.output_dir / "review_queue.jsonl"
        if review_path.exists():
            with review_path.open("r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if not line:
                        continue
                    try:
                        self.review_queue.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Build conversation index
        for conv_id, assignment in self.assignments.items():
            self.conversation_index[conv_id] = {
                "title": assignment.title,
                "project_id": assignment.project_id,
                "project_name": assignment.project_name,
                "topics": [t.model_dump() for t in assignment.topics],
                "atom_count": assignment.atom_count,
                "review_flag": assignment.review_flag,
            }

    def get_topics_summary(self) -> List[Dict[str, Any]]:
        """Get list of topics with counts (without embeddings)."""
        result = []
        for topic_id, topic in self.topics.items():
            conv_ids = self.topic_to_conversations.get(topic_id, [])
            flagged_count = sum(
                1
                for conv_id in conv_ids
                if self.assignments.get(conv_id, ConversationTopics(
                    conversation_id=conv_id, title="", topics=[], atom_count=0
                )).review_flag
            )

            # Count atoms for this topic's conversations
            atom_count = sum(
                self.assignments.get(conv_id, ConversationTopics(
                    conversation_id=conv_id, title="", topics=[], atom_count=0
                )).atom_count
                for conv_id in conv_ids
            )

            result.append({
                "topic_id": topic.topic_id,
                "name": topic.name,
                "description": topic.description,
                "keywords": topic.keywords[:10],  # Limit for UI
                "conversation_count": len(conv_ids),
                "atom_count": atom_count,
                "flagged_count": flagged_count,
            })
        return sorted(result, key=lambda x: x["conversation_count"], reverse=True)

    def get_topic_detail(self, topic_id: int) -> Optional[Dict[str, Any]]:
        """Get topic details with conversations."""
        topic = self.topics.get(topic_id)
        if not topic:
            return None

        conv_ids = self.topic_to_conversations.get(topic_id, [])
        conversations = []
        for conv_id in conv_ids:
            assignment = self.assignments.get(conv_id)
            if assignment:
                conversations.append({
                    "conversation_id": assignment.conversation_id,
                    "title": assignment.title,
                    "project_id": assignment.project_id,
                    "project_name": assignment.project_name,
                    "atom_count": assignment.atom_count,
                    "review_flag": assignment.review_flag,
                    "topics": [
                        {
                            "topic_id": t.topic_id,
                            "name": t.name,
                            "score": t.score,
                            "rank": t.rank,
                        }
                        for t in assignment.topics
                    ],
                })

        return {
            "topic_id": topic.topic_id,
            "name": topic.name,
            "description": topic.description,
            "keywords": topic.keywords,
            "representative_conversations": topic.representative_conversations,
            "conversations": conversations,
        }

    def get_conversation_detail(self, conversation_id: str) -> Optional[Dict[str, Any]]:
        """Get conversation details with atoms and doc list."""
        assignment = self.assignments.get(conversation_id)
        if not assignment:
            return None

        # Load atoms (prefer per-conversation, fallback to consolidated)
        atoms = self._load_conversation_atoms(conversation_id)
        # Filter by type (atoms are dicts, not Pydantic models at this point)
        facts = [a for a in atoms if isinstance(a, dict) and a.get("type") != "decision" and a.get("type") != "question"]
        decisions = [a for a in atoms if isinstance(a, dict) and a.get("type") == "decision"]
        questions = [a for a in atoms if isinstance(a, dict) and a.get("type") == "question"]

        # List available docs
        docs = self._list_conversation_docs(conversation_id)

        return {
            "conversation_id": assignment.conversation_id,
            "title": assignment.title,
            "project_id": assignment.project_id,
            "project_name": assignment.project_name,
            "topics": [t.model_dump() for t in assignment.topics],
            "atom_count": assignment.atom_count,
            "review_flag": assignment.review_flag,
            "facts": facts,  # Already dicts
            "decisions": decisions,  # Already dicts
            "questions": questions,  # Already dicts
            "docs": docs,
        }

    def _load_conversation_atoms(self, conversation_id: str) -> List[Dict[str, Any]]:
        """Load atoms for a conversation, preferring per-conversation files."""
        atoms = []

        # Try per-conversation atoms first
        conv_atoms_dir = self.atoms_dir / conversation_id
        if conv_atoms_dir.exists():
            for file_name in ["facts.jsonl", "decisions.jsonl", "open_questions.jsonl"]:
                file_path = conv_atoms_dir / file_name
                if file_path.exists():
                    atoms.extend(self._read_jsonl(file_path))
        else:
            # Fallback: slice from consolidated files
            consolidated_dir = self.output_dir / "project"
            for file_name in ["atoms.jsonl", "decisions.jsonl", "open_questions.jsonl"]:
                file_path = consolidated_dir / file_name
                if file_path.exists():
                    for obj in self._read_jsonl(file_path):
                        if obj.get("source_conversation_id") == conversation_id:
                            atoms.append(obj)

        return atoms

    def _read_jsonl(self, file_path: Path) -> List[Dict[str, Any]]:
        """Read JSONL file."""
        result = []
        if not file_path.exists():
            return result
        with file_path.open("r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    result.append(json.loads(line))
                except json.JSONDecodeError:
                    continue
        return result

    def _list_conversation_docs(self, conversation_id: str) -> List[Dict[str, str]]:
        """List available markdown docs for a conversation."""
        docs = []
        conv_docs_dir = self.docs_dir / conversation_id
        if conv_docs_dir.exists():
            for md_file in conv_docs_dir.glob("*.md"):
                docs.append({
                    "name": md_file.name,
                    "path": str(md_file.relative_to(self.base_path)),
                })

        # Also check ADRs
        adr_dir = self.docs_dir / "decisions" / conversation_id
        if adr_dir.exists():
            for md_file in adr_dir.glob("*.md"):
                docs.append({
                    "name": f"adrs/{md_file.name}",
                    "path": str(md_file.relative_to(self.base_path)),
                })

        return docs

    def get_doc_content(self, conversation_id: str, doc_name: str) -> Optional[str]:
        """Get markdown content for a doc."""
        # Handle ADR paths
        if doc_name.startswith("adrs/"):
            adr_path = self.docs_dir / "decisions" / conversation_id / doc_name.replace("adrs/", "")
            if adr_path.exists():
                return adr_path.read_text(encoding="utf-8")
        else:
            doc_path = self.docs_dir / conversation_id / doc_name
            if doc_path.exists():
                return doc_path.read_text(encoding="utf-8")
        return None

    def get_review_queue(self) -> List[Dict[str, Any]]:
        """Get review queue items."""
        return self.review_queue

    def get_conversation_file_paths(self, conversation_id: str) -> Dict[str, Path]:
        """Get file paths for bundling a conversation."""
        paths = {}

        # Docs
        conv_docs_dir = self.docs_dir / conversation_id
        if conv_docs_dir.exists():
            paths["docs"] = conv_docs_dir

        # ADRs
        adr_dir = self.docs_dir / "decisions" / conversation_id
        if adr_dir.exists():
            paths["adrs"] = adr_dir

        # Atoms
        conv_atoms_dir = self.atoms_dir / conversation_id
        if conv_atoms_dir.exists():
            paths["atoms"] = conv_atoms_dir
        else:
            # Will need to slice from consolidated
            paths["atoms_consolidated"] = self.output_dir / "project"
            paths["conversation_id"] = conversation_id  # Marker for slicing

        # Evidence
        evidence_path = self.evidence_dir / conversation_id / "conversation.md"
        if evidence_path.exists():
            paths["evidence"] = evidence_path

        return paths

    def get_topic_conversation_ids(self, topic_id: int) -> List[str]:
        """Get all conversation IDs for a topic (primary assignments)."""
        return self.topic_to_conversations.get(topic_id, [])
