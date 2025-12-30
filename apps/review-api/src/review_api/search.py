"""Full-text search index for topics, conversations, atoms, and docs."""

import json
from collections import defaultdict
from pathlib import Path
from typing import Any, Dict, List, Optional

from review_api.store import KnowledgeStore


class SearchIndex:
    """Simple full-text search index."""

    def __init__(self, store: KnowledgeStore):
        self.store = store
        self.index: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def build_index(self) -> None:
        """Build search index from store data."""
        self.index.clear()

        # Index topics
        for topic_id, topic in self.store.topics.items():
            text = f"{topic.name} {topic.description} {' '.join(topic.keywords)}"
            self._index_text("topic", topic_id, text, {"topic_id": topic_id, "name": topic.name})

        # Index conversations
        for conv_id, assignment in self.store.assignments.items():
            text = f"{assignment.title}"
            if assignment.project_name:
                text += f" {assignment.project_name}"
            # Add atom statements if available
            detail = self.store.get_conversation_detail(conv_id)
            if detail:
                for fact in detail.get("facts", []):
                    text += f" {fact.get('statement', '')}"
                for decision in detail.get("decisions", []):
                    text += f" {decision.get('statement', '')}"
                for question in detail.get("questions", []):
                    text += f" {question.get('question', '')}"

            self._index_text(
                "conversation",
                conv_id,
                text,
                {
                    "conversation_id": conv_id,
                    "title": assignment.title,
                    "project_name": assignment.project_name,
                },
            )

        # Index atoms
        for conv_id, assignment in self.store.assignments.items():
            detail = self.store.get_conversation_detail(conv_id)
            if detail:
                for i, fact in enumerate(detail.get("facts", [])):
                    text = f"{fact.get('statement', '')} {fact.get('topic', '')}"
                    self._index_text(
                        "atom",
                        f"{conv_id}-fact-{i}",
                        text,
                        {
                            "conversation_id": conv_id,
                            "type": "fact",
                            "statement": fact.get("statement", ""),
                            "topic": fact.get("topic", ""),
                        },
                    )
                for i, decision in enumerate(detail.get("decisions", [])):
                    text = f"{decision.get('statement', '')} {decision.get('topic', '')} {decision.get('rationale', '')}"
                    self._index_text(
                        "atom",
                        f"{conv_id}-decision-{i}",
                        text,
                        {
                            "conversation_id": conv_id,
                            "type": "decision",
                            "statement": decision.get("statement", ""),
                            "topic": decision.get("topic", ""),
                        },
                    )
                for i, question in enumerate(detail.get("questions", [])):
                    text = f"{question.get('question', '')} {question.get('topic', '')} {question.get('context', '')}"
                    self._index_text(
                        "atom",
                        f"{conv_id}-question-{i}",
                        text,
                        {
                            "conversation_id": conv_id,
                            "type": "question",
                            "question": question.get("question", ""),
                            "topic": question.get("topic", ""),
                        },
                    )

        # Index doc content (markdown)
        for conv_id in self.store.assignments.keys():
            docs = self.store._list_conversation_docs(conv_id)
            for doc in docs:
                content = self.store.get_doc_content(conv_id, doc["name"])
                if content:
                    self._index_text(
                        "doc",
                        f"{conv_id}/{doc['name']}",
                        content,
                        {
                            "conversation_id": conv_id,
                            "doc_name": doc["name"],
                            "path": doc["path"],
                        },
                    )

    def _index_text(self, doc_type: str, doc_id: str, text: str, metadata: Dict[str, Any]) -> None:
        """Index a text document."""
        # Simple word-based indexing (could be improved with stemming, etc.)
        words = text.lower().split()
        for word in words:
            if len(word) > 2:  # Skip very short words
                self.index[word].append({"type": doc_type, "id": doc_id, "metadata": metadata})

    def search(self, query: str, limit: int = 20) -> Dict[str, List[Dict[str, Any]]]:
        """Search across all indexed content."""
        query_words = query.lower().split()
        if not query_words:
            return {"topics": [], "conversations": [], "atoms": [], "docs": []}

        # Score results by word frequency
        scores: Dict[tuple, float] = defaultdict(float)
        result_metadata: Dict[tuple, Dict[str, Any]] = {}

        for word in query_words:
            if len(word) > 2 and word in self.index:
                for hit in self.index[word]:
                    key = (hit["type"], hit["id"])
                    scores[key] += 1.0
                    result_metadata[key] = hit["metadata"]

        # Sort by score and group by type
        sorted_results = sorted(scores.items(), key=lambda x: x[1], reverse=True)[:limit]

        results: Dict[str, List[Dict[str, Any]]] = {
            "topics": [],
            "conversations": [],
            "atoms": [],
            "docs": [],
        }

        for (doc_type, doc_id), score in sorted_results:
            metadata = result_metadata.get((doc_type, doc_id), {})
            result_item = {**metadata, "score": score, "id": doc_id}
            if doc_type == "topic":
                results["topics"].append(result_item)
            elif doc_type == "conversation":
                results["conversations"].append(result_item)
            elif doc_type == "atom":
                results["atoms"].append(result_item)
            elif doc_type == "doc":
                results["docs"].append(result_item)

        return results
