# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- **Human-readable CLI logging**: New `--log-mode` option with `human`, `hybrid`, `machine`, and `auto` modes for optimized logging based on use case (interactive development vs CI/CD)
- **Hybrid logging mode**: Rich console output for human readability + structured JSON logs to file for programmatic analysis
- **Automatic mode detection**: `--log-mode auto` (default) automatically selects appropriate mode based on TTY detection and `--log-file` presence
- **Conditional progress bars**: Rich progress spinners are automatically disabled in non-interactive/machine modes to prevent log corruption
- **Persistent terminal dashboard for `run-all`**: Live, non-scrolling dashboard showing pipeline step status, progress bars, elapsed time, rate, ETA, and log tail panel. Auto-enabled in interactive terminals with `--dashboard/--no-dashboard` controls and `--dashboard-log-lines` option
- Initial scaffold with packaging (pyproject.toml, Makefile, README)
- CLI structure with Typer
- Linearization step to extract conversations from ChatGPT export JSON
- OpenAI-backed knowledge atom extraction
- Documentation compilation from atoms
- Support for `uv` package manager
- `--conversation-id` option for single-conversation testing
- Per-chunk progress feedback during extraction
- Project knowledge compilation prompt for synthesizing docs with AI assistants
- Support for single-conversation JSON files (objects with `mapping`/`current_node`) in addition to list-based exports
- Automatic conversation ID injection from filename when `id`/`conversation_id` is missing in single conversation files
- Support for directory inputs containing per-conversation ChatGPT JSON files (e.g. `chatgpt-conversations/`)
- Support for Claude AI export JSON inputs (converted to ChatGPT-style mapping internally)
- `consolidate` command to aggregate per-conversation outputs into project-wide knowledge packet with exact-match deduplication
- `discover-topics` command for BERTopic-based topic discovery from conversation artifacts
- `assign-topics` command for multi-label topic assignment with confidence scores
- OpenRouter-based embedding client for consistent API usage across pipeline
- Topic schema models (TopicRegistry, ConversationTopics)
- Support for automatic review flagging of low-confidence assignments
- Optional `[topics]` dependency group for topic modeling libraries
- Makefile targets: `discover-topics`, `assign-topics`, `topics`, `all-with-topics`
- Claude project metadata support (`project_uuid` → `project_id`/`project_name`) surfaced into normalized conversations, linearized markdown, and topic assignment outputs
- **Ports and adapters architecture**: Refactored codebase to use hexagonal architecture pattern with explicit port interfaces (`core/ports/`) and adapter implementations (`adapters/`)
- **Bootstrap module** (`bootstrap.py`): Centralized composition root for wiring adapters based on environment variables (`CKX_ATOM_REFINER_IMPL`, `CKX_TOPIC_LABELER_IMPL`)
- **DSPy integration**: Optional DSPy adapters for topic labeling (`DspyTopicLabeler`) and atom refinement (`DspyAtomRefiner`, `HybridAtomExtractor`)
- **CLI package structure**: Converted CLI into a package (`cli/`) with separate command modules for better organization
- **Pipeline module**: Extracted orchestration logic into `pipeline/` that depends only on ports, not concrete adapters
- **Offline integration tests**: Added tests for extraction and topics pipelines using fake adapters (no API calls required)

### Changed
- Switched from traditional venv/pip to `uv` for faster dependency management
- Default OpenRouter/DSPy LLM model identifiers now default to `z-ai/glm-4.7` for both Pass 1 and Pass 2
- **Refactored shims**: `extract_openai.py`, `topic_discovery.py`, and `embeddings.py` now delegate adapter selection to `bootstrap.py` instead of containing branching logic
- **CLI structure**: Split monolithic `cli.py` into package with separate command modules (`cli/commands/*.py`)
- **Pipeline imports**: `pipeline/topics.py` now imports models from `core/models` instead of direct schema imports
- **Module migration**: Moved root-level modules into organized packages:
  - Schemas (`atoms_schema.py`, `topic_schema.py`) → `core/models/` (atoms.py, topics.py)
  - Operations (`linearize.py`, `compile_docs.py`, `consolidate.py`, `topic_assignment.py`) → `pipeline/`
  - I/O (`input_normalize.py`, `export_schema.py`) → `pipeline/io/` (load.py, schema_helpers.py)
  - Utilities (`chunking.py`) → `utils/chunking.py`
  - Root-level modules now serve as backward-compatibility shims that re-export from canonical locations
- **BREAKING: Removed non-key root shims**: Deleted backward-compatibility shims for schemas, operations, I/O, and utilities (`atoms_schema.py`, `topic_schema.py`, `linearize.py`, `compile_docs.py`, `consolidate.py`, `topic_assignment.py`, `input_normalize.py`, `export_schema.py`, `chunking.py`). Import from canonical locations instead:
  - `ck_exporter.core.models` for schemas
  - `ck_exporter.pipeline.*` for operations
  - `ck_exporter.pipeline.io.*` for I/O utilities
  - `ck_exporter.utils.*` for general utilities
  - Only key entrypoint shims remain: `cli.py`, `extract_openai.py`, `topic_discovery.py`, `embeddings.py`

### Fixed
- Claude export format parsing to handle newer format where message text is in `content[]` array instead of direct `text` field
- `load_conversations()` now converts Claude exports even when the input JSON is a list of Claude conversations (fixes “Skipping conversation without ID” for list inputs)

## [0.1.0] - 2024-12-XX

### Added
- Initial release
