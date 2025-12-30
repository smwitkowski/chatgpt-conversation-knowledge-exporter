"""Topic discovery and assignment commands."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from ck_exporter.pipeline.assignment import assign_topics, load_topic_registry, save_assignments
from ck_exporter.topic_discovery import (
    build_conversation_documents,
    discover_topics as discover_topics_func,
    label_topics_with_llm,
    save_topic_registry,
)

console = Console()


def discover_topics_command(
    input: Path = typer.Option(..., "--input", "-i", help="Path to conversation JSON file(s)"),
    atoms: Path = typer.Option(Path("output/project"), "--atoms", "-a", help="Path to consolidated atoms.jsonl directory"),
    out: Path = typer.Option(Path("output"), "--out", "-o", help="Output directory"),
    target_topics: int = typer.Option(50, "--target-topics", help="Target number of topics"),
    embedding_model: str = typer.Option("openai/text-embedding-3-small", "--embedding-model", help="OpenRouter embedding model"),
    label_model: str = typer.Option(None, "--label-model", help="LLM model for topic labeling (default: z-ai/glm-4.7)"),
    skip_labeling: bool = typer.Option(False, "--skip-labeling/--no-skip-labeling", help="Skip LLM labeling of topics"),
    use_openrouter: bool = typer.Option(True, "--openrouter/--no-openrouter", help="Use OpenRouter API (default: True)"),
    pooling: bool = typer.Option(True, "--pooling/--no-pooling", help="Use chunked pooling for embeddings (default: True)"),
    chunk_tokens: int = typer.Option(600, "--chunk-tokens", help="Maximum tokens per chunk when pooling (default: 600)"),
    chunk_overlap: int = typer.Option(80, "--chunk-overlap", help="Token overlap between chunks when pooling (default: 80)"),
    embedding_cache_dir: Path = typer.Option(None, "--embedding-cache-dir", help="Directory for caching embeddings (default: .cache/embeddings)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit number of conversations to process (deterministic: first N by sorted filename)"),
) -> None:
    """Discover topics from conversation artifacts using BERTopic."""
    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(1)

    atoms_path = atoms / "atoms.jsonl" if atoms.is_dir() else atoms
    decisions_path = atoms / "decisions.jsonl" if atoms.is_dir() else atoms.parent / "decisions.jsonl"
    questions_path = atoms / "open_questions.jsonl" if atoms.is_dir() else atoms.parent / "open_questions.jsonl"

    if not atoms_path.exists():
        console.print(f"[red]Atoms file not found: {atoms_path}[/red]")
        raise typer.Exit(1)

    console.print("[bold]Building conversation documents...[/bold]")
    documents, titles = build_conversation_documents(input, atoms_path, decisions_path, questions_path, limit=limit)

    if not documents:
        console.print("[red]No conversations found[/red]")
        raise typer.Exit(1)

    console.print(f"[green]✓ Built documents for {len(documents)} conversations[/green]")

    console.print("[bold]Discovering topics...[/bold]")
    cache_dir = embedding_cache_dir if embedding_cache_dir else Path(".cache/embeddings")
    topic_model, embeddings, doc_ids = discover_topics_func(
        documents,
        embedding_model=embedding_model,
        target_topics=target_topics,
        use_openrouter=use_openrouter,
        use_pooling=pooling,
        chunk_tokens=chunk_tokens,
        overlap_tokens=chunk_overlap,
        cache_dir=cache_dir,
    )

    doc_texts = [documents[conv_id] for conv_id in doc_ids]
    topics_out = topic_model.topics_

    if skip_labeling:
        console.print("[yellow]Skipping LLM labeling[/yellow]")
        # Create basic topics without LLM labels
        topic_info = topic_model.get_topic_info()
        topics = []
        for idx, row in topic_info.iterrows():
            topic_id = int(row["Topic"])
            if topic_id == -1:
                continue
            topic_words = topic_model.get_topic(topic_id)
            keywords = [word for word, _ in topic_words[:10]] if topic_words else []
            topics.append(
                {
                    "topic_id": topic_id,
                    "name": f"Topic {topic_id}",
                    "description": f"Topic {topic_id} with keywords: {', '.join(keywords[:5])}",
                    "keywords": keywords,
                    "representative_conversations": [],
                }
            )
        from ck_exporter.core.models import Topic
        topics = [Topic(**t) for t in topics]
    else:
        console.print("[bold]Labeling topics with LLM...[/bold]")
        topics = label_topics_with_llm(
            topic_model,
            documents,
            doc_ids,
            doc_texts,
            embedding_model=embedding_model,
            use_openrouter=use_openrouter,
            label_model=label_model,
        )

    registry_path = out / "topic_registry.json"
    save_topic_registry(
        topics,
        topic_model,
        embeddings,
        topics_out,
        doc_ids,
        embedding_model,
        registry_path,
    )

    console.print(f"[bold green]✓ Topic discovery complete![/bold green]")
    console.print(f"   Registry saved to: {registry_path}")


def assign_topics_command(
    input: Path = typer.Option(..., "--input", "-i", help="Path to conversation JSON file(s)"),
    atoms: Path = typer.Option(Path("output/project"), "--atoms", "-a", help="Path to consolidated atoms.jsonl directory"),
    registry: Path = typer.Option(..., "--registry", "-r", help="Path to topic_registry.json"),
    out: Path = typer.Option(Path("output"), "--out", "-o", help="Output directory"),
    embedding_model: str = typer.Option("openai/text-embedding-3-small", "--embedding-model", help="OpenRouter embedding model"),
    primary_threshold: float = typer.Option(0.60, "--primary-threshold", help="Minimum score for primary topic"),
    secondary_threshold: float = typer.Option(0.55, "--secondary-threshold", help="Minimum score for secondary topics"),
    use_openrouter: bool = typer.Option(True, "--openrouter/--no-openrouter", help="Use OpenRouter API (default: True)"),
    pooling: bool = typer.Option(True, "--pooling/--no-pooling", help="Use chunked pooling for embeddings (default: True)"),
    chunk_tokens: int = typer.Option(600, "--chunk-tokens", help="Maximum tokens per chunk when pooling (default: 600)"),
    chunk_overlap: int = typer.Option(80, "--chunk-overlap", help="Token overlap between chunks when pooling (default: 80)"),
    embedding_cache_dir: Path = typer.Option(None, "--embedding-cache-dir", help="Directory for caching embeddings (default: .cache/embeddings)"),
    limit: Optional[int] = typer.Option(None, "--limit", "-n", help="Limit number of conversations to process (deterministic: first N by sorted filename)"),
) -> None:
    """Assign conversations to discovered topics (multi-label)."""
    if not input.exists():
        console.print(f"[red]Input file not found: {input}[/red]")
        raise typer.Exit(1)

    if not registry.exists():
        console.print(f"[red]Topic registry not found: {registry}[/red]")
        raise typer.Exit(1)

    atoms_path = atoms / "atoms.jsonl" if atoms.is_dir() else atoms
    decisions_path = atoms / "decisions.jsonl" if atoms.is_dir() else atoms.parent / "decisions.jsonl"
    questions_path = atoms / "open_questions.jsonl" if atoms.is_dir() else atoms.parent / "open_questions.jsonl"

    if not atoms_path.exists():
        console.print(f"[red]Atoms file not found: {atoms_path}[/red]")
        raise typer.Exit(1)

    console.print("[bold]Loading topic registry...[/bold]")
    topic_registry = load_topic_registry(registry)

    console.print(f"[green]✓ Loaded {topic_registry.num_topics} topics[/green]")

    console.print("[bold]Assigning topics to conversations...[/bold]")
    cache_dir = embedding_cache_dir if embedding_cache_dir else Path(".cache/embeddings")
    assignments = assign_topics(
        input,
        atoms_path,
        decisions_path,
        questions_path,
        topic_registry,
        embedding_model=embedding_model,
        primary_threshold=primary_threshold,
        secondary_threshold=secondary_threshold,
        use_openrouter=use_openrouter,
        use_pooling=pooling,
        chunk_tokens=chunk_tokens,
        overlap_tokens=chunk_overlap,
        cache_dir=cache_dir,
        limit=limit,
    )

    assignments_path = out / "assignments.jsonl"
    save_assignments(assignments, assignments_path)

    console.print(f"[bold green]✓ Topic assignment complete![/bold green]")
    console.print(f"   Assignments saved to: {assignments_path}")
