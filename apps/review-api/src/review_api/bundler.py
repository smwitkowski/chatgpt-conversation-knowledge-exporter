"""Zip bundle generation for topics and conversations."""

import json
import sys
import zipfile
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add parent src to path for ck_exporter imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from review_api.addons import AddonRegistry, ExporterAddon
from review_api.store import KnowledgeStore


class ZipBundler:
    """Generate zip bundles for topics and conversations."""

    def __init__(self, store: KnowledgeStore, addon_registry: Optional[AddonRegistry] = None):
        self.store = store
        self.addon_registry = addon_registry or AddonRegistry()

    def bundle_conversation(self, conversation_id: str) -> Optional[bytes]:
        """Create a zip bundle for a single conversation."""
        assignment = self.store.assignments.get(conversation_id)
        if not assignment:
            return None

        import io

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add manifest
            manifest = {
                "kind": "conversation",
                "conversation_id": conversation_id,
                "title": assignment.title,
                "project_id": assignment.project_id,
                "project_name": assignment.project_name,
                "topics": [t.model_dump() for t in assignment.topics],
                "atom_count": assignment.atom_count,
                "review_flag": assignment.review_flag,
                "generated_at": datetime.now().isoformat(),
            }
            zip_file.writestr("manifest.json", json.dumps(manifest, indent=2))

            # Get file paths
            paths = self.store.get_conversation_file_paths(conversation_id)

            # Add docs
            if "docs" in paths:
                docs_dir = paths["docs"]
                for md_file in docs_dir.glob("*.md"):
                    arc_name = f"docs/{md_file.name}"
                    zip_file.write(md_file, arc_name)

            # Add ADRs
            if "adrs" in paths:
                adr_dir = paths["adrs"]
                for md_file in adr_dir.glob("*.md"):
                    arc_name = f"adrs/{md_file.name}"
                    zip_file.write(md_file, arc_name)

            # Add atoms
            if "atoms" in paths:
                atoms_dir = paths["atoms"]
                for jsonl_file in atoms_dir.glob("*.jsonl"):
                    arc_name = f"atoms/{jsonl_file.name}"
                    zip_file.write(jsonl_file, arc_name)
            elif "atoms_consolidated" in paths:
                # Slice from consolidated files
                consolidated_dir = paths["atoms_consolidated"]
                for file_name in ["atoms.jsonl", "decisions.jsonl", "open_questions.jsonl"]:
                    source_file = consolidated_dir / file_name
                    if source_file.exists():
                        # Filter by conversation_id
                        filtered_lines = []
                        with source_file.open("r", encoding="utf-8") as f:
                            for line in f:
                                line = line.strip()
                                if not line:
                                    continue
                                try:
                                    obj = json.loads(line)
                                    if obj.get("source_conversation_id") == conversation_id:
                                        filtered_lines.append(line)
                                except json.JSONDecodeError:
                                    continue
                        if filtered_lines:
                            arc_name = f"atoms/{file_name}"
                            zip_file.writestr(arc_name, "\n".join(filtered_lines) + "\n")

            # Add evidence
            if "evidence" in paths:
                evidence_file = paths["evidence"]
                zip_file.write(evidence_file, "evidence/conversation.md")

            # Add addon exports
            for exporter in self.addon_registry.get_exporters():
                try:
                    addon_files = exporter.export_conversation(conversation_id, self.store)
                    for file_path, content in addon_files.items():
                        zip_file.writestr(f"addons/{exporter.addon_id}/{file_path}", content)
                except Exception as e:
                    # Skip addon if it fails
                    continue

        zip_buffer.seek(0)
        return zip_buffer.read()

    def bundle_topic(self, topic_id: int) -> Optional[bytes]:
        """Create a zip bundle for a topic (all primary conversations)."""
        topic = self.store.topics.get(topic_id)
        if not topic:
            return None

        conv_ids = self.store.get_topic_conversation_ids(topic_id)
        if not conv_ids:
            return None

        import io

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zip_file:
            # Add manifest
            manifest = {
                "kind": "topic",
                "topic_id": topic_id,
                "topic_name": topic.name,
                "topic_description": topic.description,
                "keywords": topic.keywords,
                "conversation_count": len(conv_ids),
                "conversation_ids": conv_ids,
                "generated_at": datetime.now().isoformat(),
            }
            zip_file.writestr("manifest.json", json.dumps(manifest, indent=2))

            # Bundle each conversation
            for conv_id in conv_ids:
                conv_zip = self.bundle_conversation(conv_id)
                if conv_zip:
                    # Extract and add to main zip
                    import io as io_module
                    import zipfile as zipfile_module

                    conv_zip_buffer = io_module.BytesIO(conv_zip)
                    with zipfile_module.ZipFile(conv_zip_buffer, "r") as conv_zip_file:
                        for item in conv_zip_file.namelist():
                            # Prefix with conversation_id
                            new_name = f"conversations/{conv_id}/{item}"
                            zip_file.writestr(new_name, conv_zip_file.read(item))

            # Add topic-level addon exports
            for exporter in self.addon_registry.get_exporters():
                try:
                    addon_files = exporter.export_topic(topic_id, self.store)
                    for file_path, content in addon_files.items():
                        zip_file.writestr(f"addons/{exporter.addon_id}/{file_path}", content)
                except Exception as e:
                    # Skip addon if it fails
                    continue

        zip_buffer.seek(0)
        return zip_buffer.read()
