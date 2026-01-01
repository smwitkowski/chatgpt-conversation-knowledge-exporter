"""Extraction pipeline orchestration."""

import contextvars
import os
import traceback
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Callable, Optional

import typer
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

from ck_exporter.adapters.fs_jsonl import write_jsonl
from ck_exporter.utils.chunking import chunk_messages
from ck_exporter.config import get_chunk_max_concurrency, get_max_concurrency
from ck_exporter.core.ports.atom_extractor import AtomExtractor
from ck_exporter.logging import get_logger, should_show_progress, with_context
from ck_exporter.observability.langsmith import traceable_call, tracing_context
from ck_exporter.pipeline.action_items import extract_action_items_from_conversation
from ck_exporter.pipeline.atom_converter import (
    convert_action_items_to_universal,
    convert_decisions_to_universal,
    convert_facts_to_universal,
    convert_open_questions_to_universal,
)
from ck_exporter.pipeline.io import get_conversation_id, get_title, load_conversations
from ck_exporter.pipeline.linearize import linearize_conversation
from ck_exporter.pipeline.meeting_metadata import extract_meeting_metadata, infer_meeting_kind


def _extract_meeting_atoms_with_dspy(
    conversation: dict[str, Any],
    conversation_id: str,
    linearized_content: str,
    conv_logger: Any,
) -> list[dict[str, Any]] | None:
    """
    Extract meeting atoms using DSPy (if available).

    Returns list of universal atoms if successful, None if DSPy not available or extraction fails.
    """
    try:
        from ck_exporter.adapters.dspy_lm import get_dspy_lm_for_meeting_extraction
        from ck_exporter.programs.dspy.extract_meeting_atoms import (
            create_extract_meeting_atoms_program,
            extract_meeting_atoms_with_dspy,
        )

        # Try to get meeting metadata
        # For now, we'll infer from conversation_id and content
        # In a full implementation, we'd track the source file path
        meeting_metadata = {
            "source_system": "google_meet",
            "meeting_title": get_title(conversation) or "Unknown Meeting",
            "participants": [],
            "links": {},
        }

        # Create DSPy LM and program
        lm = get_dspy_lm_for_meeting_extraction(use_openrouter=True)
        dspy_program = create_extract_meeting_atoms_program(lm)

        # Extract atoms
        result = extract_meeting_atoms_with_dspy(
            conversation=conversation,
            conversation_id=conversation_id,
            meeting_metadata=meeting_metadata,
            linearized_content=linearized_content,
            dspy_program=dspy_program,
        )

        atoms = result.get("atoms", [])
        if atoms:
            # Ensure all atoms have conversation_id in evidence
            for atom in atoms:
                for ev in atom.get("evidence", []):
                    if isinstance(ev, dict) and not ev.get("conversation_id"):
                        ev["conversation_id"] = conversation_id

        return atoms if atoms else None

    except ImportError:
        # DSPy not available
        return None
    except Exception as e:
        conv_logger.warning(
            "DSPy extraction error",
            extra={"event": "extract.meeting.dspy.error", "error": str(e)},
        )
        return None

logger = get_logger(__name__)


def format_chunk_for_extraction(messages: list[dict[str, Any]]) -> str:
    """Format a message chunk as text for extraction."""
    lines = []
    for msg in messages:
        role = msg.get("role", "unknown")
        text = msg.get("text", "")
        time_iso = msg.get("time_iso", "")
        msg_id = msg.get("id", "")

        lines.append(f"[{role.upper()}] {time_iso} (ID: {msg_id})")
        lines.append(text)
        lines.append("")

    return "\n".join(lines)


def _conversation_outputs_exist(conv_id: str, atoms_dir: Path) -> bool:
    """Check if final outputs already exist for a conversation."""
    atoms_path = atoms_dir / conv_id / "atoms.jsonl"
    # Consider it complete if atoms.jsonl exists and is non-empty
    return atoms_path.exists() and atoms_path.stat().st_size > 0


def extract_conversation(
    conversation: dict[str, Any],
    evidence_dir: Path,
    atoms_dir: Path,
    extractor: AtomExtractor,
    max_chunk_tokens: int = 8000,
    skip_existing: bool = True,
    chunk_max_concurrency: int | None = None,
) -> None:
    """
    Extract atoms from a single conversation using two-pass pipeline.

    Args:
        conversation: Conversation dict
        evidence_dir: Directory with linearized markdown evidence
        atoms_dir: Output directory for atoms JSONL files
        extractor: Atom extractor implementation
        max_chunk_tokens: Maximum tokens per chunk
        skip_existing: Skip if outputs already exist
    """
    conv_id = get_conversation_id(conversation)
    if not conv_id:
        logger.warning(
            "Skipping conversation without ID",
            extra={"event": "extract.conversation.skipped", "reason": "no_id"},
        )
        return

    conv_logger = with_context(logger, conversation_id=conv_id)

    # Check if outputs already exist
    if skip_existing and _conversation_outputs_exist(conv_id, atoms_dir):
        conv_logger.debug(
            "Skipping conversation (outputs already exist)",
            extra={"event": "extract.conversation.skipped", "reason": "exists"},
        )
        return

    # Check if this is a meeting artifact (conversation_id starts with "meeting__")
    is_meeting = conv_id.startswith("meeting__")

    # Load linearized messages
    evidence_path = evidence_dir / conv_id / "conversation.md"
    if not evidence_path.exists():
        conv_logger.info(
            "No evidence found, linearizing",
            extra={"event": "extract.linearize.triggered"},
        )
        messages = linearize_conversation(conversation)
    else:
        # Re-linearize to get message structure
        messages = linearize_conversation(conversation)

    if not messages:
        conv_logger.warning(
            "No messages found",
            extra={"event": "extract.conversation.skipped", "reason": "no_messages"},
        )
        return

    def _run_extract() -> None:
        # For meetings, try DSPy extraction first
        if is_meeting:
            try:
                # Try to get the source file path from conversation metadata or infer from conv_id
                # For now, we'll use the linearized markdown content
                linearized_content = (
                    evidence_path.read_text(encoding="utf-8") if evidence_path.exists() else None
                )

                if linearized_content:
                    # Try DSPy extraction (will fall through if DSPy not available)
                    with tracing_context(
                        conversation_id=conv_id,
                        document_id=conv_id,
                        step="extract_meeting_atoms",
                    ):
                        meeting_atoms = _extract_meeting_atoms_with_dspy(
                            conversation, conv_id, linearized_content, conv_logger
                        )
                    if meeting_atoms:
                        # Write DSPy-extracted atoms
                        atoms_path = atoms_dir / conv_id / "atoms.jsonl"
                        write_jsonl(atoms_path, meeting_atoms)
                        conv_logger.info(
                            "Meeting extraction complete (DSPy)",
                            extra={
                                "event": "extract.meeting.dspy.complete",
                                "total_atoms": len(meeting_atoms),
                                "atoms_file": str(atoms_path),
                            },
                        )
                        return
            except Exception as e:
                conv_logger.warning(
                    "DSPy meeting extraction failed, falling back to standard extraction",
                    extra={
                        "event": "extract.meeting.dspy.fallback",
                        "error": str(e),
                    },
                )
                # Fall through to standard extraction

        # Chunk messages
        chunks = chunk_messages(messages, max_tokens=max_chunk_tokens, model="gpt-4")

        conv_logger.info(
            "Processing conversation",
            extra={
                "event": "extract.conversation.start",
                "num_chunks": len(chunks),
                "num_messages": len(messages),
            },
        )

        # Pass 1: Extract candidates from each chunk (parallelized)
        all_candidates = {"facts": [], "decisions": [], "open_questions": []}

        # Determine chunk concurrency (default: use config or conservative default)
        nonlocal chunk_max_concurrency
        if chunk_max_concurrency is None:
            chunk_max_concurrency = get_chunk_max_concurrency()

        # For single chunk or very few chunks, use sequential processing
        if len(chunks) <= 1 or chunk_max_concurrency <= 1:
            for i, chunk in enumerate(chunks, 1):
                chunk_text = format_chunk_for_extraction(chunk)
                with tracing_context(
                    conversation_id=conv_id,
                    document_id=conv_id,
                    step="extract_pass1",
                    chunk_index=i,
                    total_chunks=len(chunks),
                ):
                    result = extractor.extract_from_chunk(chunk_text)

                # Collect candidates
                num_facts = len(result.get("facts", []))
                num_decisions = len(result.get("decisions", []))
                num_questions = len(result.get("open_questions", []))
                all_candidates["facts"].extend(result.get("facts", []))
                all_candidates["decisions"].extend(result.get("decisions", []))
                all_candidates["open_questions"].extend(result.get("open_questions", []))

                conv_logger.debug(
                    "Pass 1 chunk extracted",
                    extra={
                        "event": "extract.pass1.chunk",
                        "chunk_num": i,
                        "total_chunks": len(chunks),
                        "facts": num_facts,
                        "decisions": num_decisions,
                        "questions": num_questions,
                    },
                )
        else:
            # Parallel chunk extraction with deterministic ordering
            chunk_results: list[tuple[int, dict[str, Any]]] = []

            def extract_chunk(idx_and_chunk: tuple[int, list[dict[str, Any]]]) -> tuple[int, dict[str, Any]]:
                """Extract from a single chunk, returning (index, result) for ordering."""
                idx, chunk = idx_and_chunk
                chunk_text = format_chunk_for_extraction(chunk)
                with tracing_context(
                    conversation_id=conv_id,
                    document_id=conv_id,
                    step="extract_pass1",
                    chunk_index=idx + 1,
                    total_chunks=len(chunks),
                ):
                    result = extractor.extract_from_chunk(chunk_text)
                return (idx, result)

            with ThreadPoolExecutor(max_workers=chunk_max_concurrency) as executor:
                # Submit all chunks with their indices (propagate contextvars for LangSmith nesting)
                futures: dict[Any, int] = {}
                for i, chunk in enumerate(chunks):
                    ctx = contextvars.copy_context()
                    future = executor.submit(ctx.run, extract_chunk, (i, chunk))
                    futures[future] = i

                # Collect results as they complete
                for future in as_completed(futures):
                    try:
                        idx, result = future.result()
                        chunk_results.append((idx, result))

                        num_facts = len(result.get("facts", []))
                        num_decisions = len(result.get("decisions", []))
                        num_questions = len(result.get("open_questions", []))

                        conv_logger.debug(
                            "Pass 1 chunk extracted",
                            extra={
                                "event": "extract.pass1.chunk",
                                "chunk_num": idx + 1,
                                "total_chunks": len(chunks),
                                "facts": num_facts,
                                "decisions": num_decisions,
                                "questions": num_questions,
                            },
                        )
                    except Exception as e:
                        chunk_idx = futures[future]
                        conv_logger.exception(
                            "Error extracting chunk",
                            extra={
                                "event": "extract.pass1.chunk.error",
                                "chunk_num": chunk_idx + 1,
                                "total_chunks": len(chunks),
                            },
                        )

            # Sort by index to maintain deterministic order, then aggregate
            chunk_results.sort(key=lambda x: x[0])
            for idx, result in chunk_results:
                all_candidates["facts"].extend(result.get("facts", []))
                all_candidates["decisions"].extend(result.get("decisions", []))
                all_candidates["open_questions"].extend(result.get("open_questions", []))

        # Pass 2: Refine and consolidate all candidates
        conv_logger.info(
            "Pass 2: Refining candidates",
            extra={
                "event": "extract.pass2.start",
                "candidate_facts": len(all_candidates["facts"]),
                "candidate_decisions": len(all_candidates["decisions"]),
                "candidate_questions": len(all_candidates["open_questions"]),
            },
        )
        conversation_title = get_title(conversation)
        with tracing_context(conversation_id=conv_id, document_id=conv_id, step="refine_atoms"):
            refined = extractor.refine_atoms(all_candidates, conv_id, conversation_title)

        final_facts = refined.get("facts", [])
        final_decisions = refined.get("decisions", [])
        final_questions = refined.get("open_questions", [])

        conv_logger.info(
            "Pass 2: Refinement complete",
            extra={
                "event": "extract.pass2.complete",
                "final_facts": len(final_facts),
                "final_decisions": len(final_decisions),
                "final_questions": len(final_questions),
            },
        )

        # Extract action items deterministically (for meeting notes)
        # TODO: This will be replaced by DSPy meeting extraction, but keeping for now as fallback
        action_items_legacy = extract_action_items_from_conversation(conversation, conv_id)

        # Convert all atoms to Universal Atom format
        all_universal_atoms = []
        all_universal_atoms.extend(convert_facts_to_universal(final_facts, conv_id))
        all_universal_atoms.extend(convert_decisions_to_universal(final_decisions, conv_id))
        all_universal_atoms.extend(convert_open_questions_to_universal(final_questions, conv_id))
        all_universal_atoms.extend(convert_action_items_to_universal(action_items_legacy, conv_id))

        # Write universal atoms.jsonl (single file per conversation)
        atoms_path = atoms_dir / conv_id / "atoms.jsonl"
        if all_universal_atoms:
            write_jsonl(atoms_path, all_universal_atoms)

        conv_logger.info(
            "Extraction complete",
            extra={
                "event": "extract.conversation.complete",
                "total_universal_atoms": len(all_universal_atoms),
                "atoms_file": str(atoms_path),
            },
        )

    # Root run for LangSmith waterfall (children include pass1/pass2 LLM calls)
    traceable_call(
        _run_extract,
        name="extract_conversation",
        run_type="chain",
        metadata={"conversation_id": conv_id, "document_id": conv_id, "step": "extract_conversation"},
        tags=["extract", "conversation"],
    )


def extract_export(
    input_path: Path,
    evidence_dir: Path,
    atoms_dir: Path,
    extractor: AtomExtractor,
    max_concurrency: int | None = None,
    skip_existing: bool = True,
    conversation_id: Optional[str] = None,
    limit: Optional[int] = None,
    progress_cb: Optional[Callable[[int, int, Optional[dict]], None]] = None,
    non_json_kind: str = "meeting",
) -> None:
    """
    Process export(s) and extract atoms for all conversations.

    Args:
        input_path: Path to conversation export JSON or directory of per-conversation JSON files
        evidence_dir: Directory with linearized markdown evidence
        atoms_dir: Output directory for atoms JSONL files
        extractor: Atom extractor implementation
        max_concurrency: Maximum concurrent conversations
        skip_existing: Skip conversations with existing outputs
        conversation_id: Optional filter to single conversation ID
        limit: Optional limit on number of conversations to process
        progress_cb: Optional callback(completed, total, context) for progress updates
        non_json_kind: How to interpret non-JSON files ("meeting" or "document")
    """
    # Set max_concurrency from config if not provided
    if max_concurrency is None:
        max_concurrency = get_max_concurrency()

    logger.info(
        "Loading export",
        extra={
            "event": "extract.export.load",
            "input_path": str(input_path),
            "limit": limit,
            "non_json_kind": non_json_kind,
        },
    )

    conversations = load_conversations(input_path, limit=limit, non_json_kind=non_json_kind)

    # Filter to single conversation if requested
    if conversation_id:
        conversations = [
            conv for conv in conversations if get_conversation_id(conv) == conversation_id
        ]
        if not conversations:
            logger.error(
                "Conversation not found in export",
                extra={
                    "event": "extract.export.error",
                    "conversation_id": conversation_id,
                },
            )
            raise typer.Exit(1)
        logger.info(
            "Filtering to single conversation",
            extra={
                "event": "extract.export.filter",
                "conversation_id": conversation_id,
            },
        )

    # Filter out conversations that already have outputs (if skip_existing)
    if skip_existing:
        original_count = len(conversations)
        conversations = [
            conv
            for conv in conversations
            if not _conversation_outputs_exist(get_conversation_id(conv) or "", atoms_dir)
        ]
        skipped_count = original_count - len(conversations)
        if skipped_count > 0:
            logger.debug(
                "Skipped conversations with existing outputs",
                extra={
                    "event": "extract.export.skipped",
                    "skipped_count": skipped_count,
                },
            )

    if not conversations:
        logger.warning(
            "No conversations to process",
            extra={"event": "extract.export.empty"},
        )
        return

    logger.info(
        "Processing conversations",
        extra={
            "event": "extract.export.start",
            "num_conversations": len(conversations),
            "max_concurrency": max_concurrency,
        },
    )

    # Notify progress callback of total
    if progress_cb:
        progress_cb(0, len(conversations), {})

    # Process conversations with bounded concurrency
    with ThreadPoolExecutor(max_workers=max_concurrency) as executor:
        futures = {}
        for conv in conversations:
            conv_id = get_conversation_id(conv) or "unknown"
            future = executor.submit(
                extract_conversation,
                conv,
                evidence_dir,
                atoms_dir,
                extractor,
                skip_existing=skip_existing,
            )
            futures[future] = conv_id

        # Track completion count for progress callback
        completed_count = 0

        if should_show_progress():
            console = Console(stderr=True)
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"Extracting atoms from {len(conversations)} conversation(s)...",
                    total=len(conversations),
                )

                for future in as_completed(futures):
                    conv_id = futures[future]
                    try:
                        future.result()
                    except Exception as e:
                        logger.exception(
                            "Error processing conversation",
                            extra={
                                "event": "extract.conversation.error",
                                "conversation_id": conv_id,
                            },
                        )
                    progress.advance(task)
                    completed_count += 1
                    if progress_cb:
                        progress_cb(completed_count, len(conversations), {"conversation_id": conv_id})
        else:
            # Non-interactive mode or dashboard mode: process without progress bar
            for future in as_completed(futures):
                conv_id = futures[future]
                try:
                    future.result()
                except Exception as e:
                    logger.exception(
                        "Error processing conversation",
                        extra={
                            "event": "extract.conversation.error",
                            "conversation_id": conv_id,
                        },
                    )
                completed_count += 1
                if progress_cb:
                    progress_cb(completed_count, len(conversations), {"conversation_id": conv_id})

    logger.info(
        "Extraction complete",
        extra={"event": "extract.export.complete"},
    )
