"""Addon system for extending review UI capabilities."""

import json
import sys
from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent src to path for ck_exporter imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from review_api.store import KnowledgeStore


class Addon(ABC):
    """Base class for addons."""

    @property
    @abstractmethod
    def addon_id(self) -> str:
        """Unique identifier for this addon."""
        pass

    @property
    @abstractmethod
    def name(self) -> str:
        """Human-readable name."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """Description of what this addon does."""
        pass

    @property
    @abstractmethod
    def capabilities(self) -> List[str]:
        """List of capabilities: 'exporter', 'panel', etc."""
        pass


class ExporterAddon(Addon):
    """Addon that exports additional files for bundles."""

    @abstractmethod
    def export_topic(self, topic_id: int, store: KnowledgeStore) -> Dict[str, bytes]:
        """
        Export files for a topic.

        Returns:
            Dict mapping file paths (relative to bundle root) to file contents (bytes)
        """
        pass

    @abstractmethod
    def export_conversation(self, conversation_id: str, store: KnowledgeStore) -> Dict[str, bytes]:
        """
        Export files for a conversation.

        Returns:
            Dict mapping file paths (relative to bundle root) to file contents (bytes)
        """
        pass


class PanelAddon(Addon):
    """Addon that provides UI panel data."""

    @abstractmethod
    def get_panel_data_topic(self, topic_id: int, store: KnowledgeStore) -> Dict[str, Any]:
        """Get panel data for a topic."""
        pass

    @abstractmethod
    def get_panel_data_conversation(self, conversation_id: str, store: KnowledgeStore) -> Dict[str, Any]:
        """Get panel data for a conversation."""
        pass


class TopicBriefExporter(ExporterAddon):
    """Export a markdown brief summarizing a topic."""

    @property
    def addon_id(self) -> str:
        return "topic-brief"

    @property
    def name(self) -> str:
        return "Topic Brief"

    @property
    def description(self) -> str:
        return "Generate a markdown brief summarizing the topic and its conversations"

    @property
    def capabilities(self) -> List[str]:
        return ["exporter"]

    def export_topic(self, topic_id: int, store: KnowledgeStore) -> Dict[str, bytes]:
        """Generate topic brief."""
        topic = store.topics.get(topic_id)
        if not topic:
            return {}

        conv_ids = store.get_topic_conversation_ids(topic_id)
        conversations = []
        total_atoms = 0

        for conv_id in conv_ids:
            assignment = store.assignments.get(conv_id)
            if assignment:
                conversations.append(assignment)
                total_atoms += assignment.atom_count

        brief = f"""# Topic: {topic.name}

## Description

{topic.description}

## Keywords

{', '.join(topic.keywords[:10])}

## Statistics

- **Conversations**: {len(conversations)}
- **Total Atoms**: {total_atoms}
- **Representative Conversations**: {len(topic.representative_conversations)}

## Conversations

"""
        for conv in conversations[:20]:  # Limit to first 20
            brief += f"- **{conv.title}** ({conv.atom_count} atoms)\n"
            if conv.project_name:
                brief += f"  - Project: {conv.project_name}\n"
            brief += "\n"

        return {"topic-brief.md": brief.encode("utf-8")}

    def export_conversation(self, conversation_id: str, store: KnowledgeStore) -> Dict[str, bytes]:
        """Not applicable for conversation exports."""
        return {}


class AtomsCSVExporter(ExporterAddon):
    """Export atoms as CSV."""

    @property
    def addon_id(self) -> str:
        return "atoms-csv"

    @property
    def name(self) -> str:
        return "Atoms CSV"

    @property
    def description(self) -> str:
        return "Export atoms as CSV for spreadsheet analysis"

    @property
    def capabilities(self) -> List[str]:
        return ["exporter"]

    def export_topic(self, topic_id: int, store: KnowledgeStore) -> Dict[str, bytes]:
        """Export all atoms from topic conversations as CSV."""
        import csv
        import io

        conv_ids = store.get_topic_conversation_ids(topic_id)
        all_atoms = []

        for conv_id in conv_ids:
            detail = store.get_conversation_detail(conv_id)
            if detail:
                for atom in detail.get("facts", []) + detail.get("decisions", []) + detail.get("questions", []):
                    all_atoms.append({
                        "conversation_id": conv_id,
                        "type": atom.get("type", ""),
                        "topic": atom.get("topic", ""),
                        "statement": atom.get("statement", atom.get("question", "")),
                        "status": atom.get("status", ""),
                        "extracted_at": atom.get("extracted_at", ""),
                    })

        output = io.StringIO()
        if all_atoms:
            writer = csv.DictWriter(output, fieldnames=["conversation_id", "type", "topic", "statement", "status", "extracted_at"])
            writer.writeheader()
            writer.writerows(all_atoms)

        return {"atoms.csv": output.getvalue().encode("utf-8")}

    def export_conversation(self, conversation_id: str, store: KnowledgeStore) -> Dict[str, bytes]:
        """Export conversation atoms as CSV."""
        import csv
        import io

        detail = store.get_conversation_detail(conversation_id)
        if not detail:
            return {}

        all_atoms = []
        for atom in detail.get("facts", []) + detail.get("decisions", []) + detail.get("questions", []):
            all_atoms.append({
                "type": atom.get("type", ""),
                "topic": atom.get("topic", ""),
                "statement": atom.get("statement", atom.get("question", "")),
                "status": atom.get("status", ""),
                "extracted_at": atom.get("extracted_at", ""),
            })

        output = io.StringIO()
        if all_atoms:
            writer = csv.DictWriter(output, fieldnames=["type", "topic", "statement", "status", "extracted_at"])
            writer.writeheader()
            writer.writerows(all_atoms)

        return {"atoms.csv": output.getvalue().encode("utf-8")}


class TopicStatsPanel(PanelAddon):
    """Panel showing topic statistics."""

    @property
    def addon_id(self) -> str:
        return "topic-stats"

    @property
    def name(self) -> str:
        return "Topic Statistics"

    @property
    def description(self) -> str:
        return "Display statistics and aggregations for a topic"

    @property
    def capabilities(self) -> List[str]:
        return ["panel"]

    def get_panel_data_topic(self, topic_id: int, store: KnowledgeStore) -> Dict[str, Any]:
        """Get stats for a topic."""
        topic = store.topics.get(topic_id)
        if not topic:
            return {}

        conv_ids = store.get_topic_conversation_ids(topic_id)
        atom_types = {}
        atom_topics = {}
        status_counts = {"active": 0, "deprecated": 0, "uncertain": 0}

        for conv_id in conv_ids:
            detail = store.get_conversation_detail(conv_id)
            if detail:
                for atom in detail.get("facts", []) + detail.get("decisions", []) + detail.get("questions", []):
                    atom_type = atom.get("type", "unknown")
                    atom_types[atom_type] = atom_types.get(atom_type, 0) + 1
                    atom_topic = atom.get("topic", "uncategorized")
                    atom_topics[atom_topic] = atom_topics.get(atom_topic, 0) + 1
                    status = atom.get("status", "active")
                    if status in status_counts:
                        status_counts[status] += 1

        return {
            "conversation_count": len(conv_ids),
            "atom_type_distribution": atom_types,
            "atom_topic_distribution": dict(sorted(atom_topics.items(), key=lambda x: x[1], reverse=True)[:10]),
            "status_distribution": status_counts,
        }

    def get_panel_data_conversation(self, conversation_id: str, store: KnowledgeStore) -> Dict[str, Any]:
        """Not applicable for conversations."""
        return {}


class AddonRegistry:
    """Registry of available addons."""

    def __init__(self):
        self.addons: Dict[str, Addon] = {}
        self._register_builtin()

    def _register_builtin(self) -> None:
        """Register built-in addons."""
        self.register(TopicBriefExporter())
        self.register(AtomsCSVExporter())
        self.register(TopicStatsPanel())

    def register(self, addon: Addon) -> None:
        """Register an addon."""
        self.addons[addon.addon_id] = addon

    def get(self, addon_id: str) -> Optional[Addon]:
        """Get an addon by ID."""
        return self.addons.get(addon_id)

    def list_all(self) -> List[Dict[str, Any]]:
        """List all registered addons."""
        return [
            {
                "addon_id": addon.addon_id,
                "name": addon.name,
                "description": addon.description,
                "capabilities": addon.capabilities,
            }
            for addon in self.addons.values()
        ]

    def get_exporters(self) -> List[ExporterAddon]:
        """Get all exporter addons."""
        return [addon for addon in self.addons.values() if isinstance(addon, ExporterAddon)]

    def get_panels(self) -> List[PanelAddon]:
        """Get all panel addons."""
        return [addon for addon in self.addons.values() if isinstance(addon, PanelAddon)]
