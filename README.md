# ChatGPT Conversation Knowledge Exporter

Extract structured knowledge from ChatGPT conversation exports and compile into canonical project documentation.

## Overview

This tool processes ChatGPT export JSON files and transforms them into:

- **Evidence**: Linearized conversation markdown files (`_evidence/<conversation_id>/conversation.md`)
- **Atoms**: Extracted knowledge atoms in JSONL format (`_atoms/<conversation_id>/{facts,decisions,open_questions}.jsonl`)
- **Docs**: Compiled human-readable documentation (`docs/<conversation_id>/*.md` and `docs/decisions/<conversation_id>/ADR-*.md`)

## Quick Start

1. **Install `uv`** (if not already installed):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

2. **Install dependencies**:
   ```bash
   make install
   # or: uv sync --extra dev
   ```

3. **Set up environment**:
   ```bash
   cp .env.example .env
   # Edit .env and add your OPENAI_API_KEY
   ```

4. **Run the full pipeline**:
   ```bash
   make all
   ```

   Or run steps individually:
   ```bash
   make linearize     # Extract conversations to markdown
   make extract       # Extract knowledge atoms using OpenAI
   make compile       # Compile atoms into docs
   make consolidate   # Aggregate per-conversation outputs into project-wide packet
   ```

## Logging

The CLI provides flexible logging modes optimized for different use cases: interactive development, CI/CD pipelines, and automated analysis.

### Logging Modes

- **human** (default for interactive): Rich, colored console output optimized for readability
- **hybrid**: Rich console output + structured JSON logs written to a file (best of both worlds)
- **machine**: JSON logs only (to file or stderr), no progress bars or Rich formatting
- **auto** (default): Automatically selects mode based on context:
  - Interactive terminal (TTY) → `human`
  - Non-interactive with `--log-file` → `hybrid`
  - Non-interactive without `--log-file` → `human` (fallback)

### Log Formats (Low-level)

For advanced use cases, you can also control the low-level format:

- **JSON**: Structured JSON lines written to stderr
- **Rich**: Human-friendly colored output
- **Plain**: Simple text format

### Log Levels

- **DEBUG**: Detailed diagnostic information
- **INFO**: General informational messages (default)
- **WARNING**: Warning messages for recoverable issues
- **ERROR**: Error messages for failures

### CLI Flags

```bash
# Use human-readable mode (default for interactive)
ckx --log-mode human extract ...

# Use hybrid mode (Rich console + JSON file)
ckx --log-mode hybrid --log-file logs.jsonl extract ...

# Use machine mode (JSON only, no progress bars)
ckx --log-mode machine --log-file logs.jsonl extract ...

# Auto-detect mode (default)
ckx --log-mode auto extract ...

# Set log level
ckx --log-level DEBUG extract ...

# Change log format (low-level, for advanced use)
ckx --log-format rich extract ...

# Write logs to file
ckx --log-file logs.jsonl extract ...

# Control third-party library logs (BERTopic, etc.)
ckx --third-party-log-level WARNING extract ...

# Disable hybrid UI (only logs, no Rich banners)
ckx --no-hybrid-ui extract ...
```

### Environment Variables

- `CKX_LOG_MODE`: Logging mode (human, hybrid, machine, auto) - default: `auto`
- `CKX_LOG_FORMAT`: Log format (json, rich, plain) - default: `json`
- `CKX_LOG_LEVEL`: Log level (DEBUG, INFO, WARNING, ERROR) - default: `INFO`
- `CKX_LOG_FILE`: Optional file path for logs
- `CKX_THIRD_PARTY_LOG_LEVEL`: Third-party library log level - default: `WARNING`
- `CKX_HYBRID_UI`: Enable/disable hybrid UI mode (true/false) - default: `true`

### Usage Examples

**Interactive Development (default):**
```bash
# Automatically uses human mode with Rich output
ckx extract --input conversations/ --evidence _evidence --out _atoms
```

**CI/CD Pipeline (structured logs):**
```bash
# Hybrid mode: human console + JSON file
ckx --log-mode hybrid --log-file ci-logs.jsonl extract ...

# Or machine mode: JSON only
ckx --log-mode machine --log-file ci-logs.jsonl extract ...
```

**Makefile Integration:**
```bash
# Set mode via environment variable
CKX_LOG_MODE=hybrid CKX_LOG_FILE=logs.jsonl make all-with-topics
```

### JSON Log Schema

Each log line is a JSON object with the following structure:

```json
{
  "ts": "2025-12-30T12:34:56.789Z",
  "level": "INFO",
  "logger": "ck_exporter.pipeline.extract",
  "message": "Processing conversation",
  "event": "extract.conversation.start",
  "conversation_id": "abc-123",
  "num_chunks": 3,
  "num_messages": 42
}
```

**Common fields:**
- `ts`: ISO 8601 timestamp (UTC)
- `level`: Log level (DEBUG, INFO, WARNING, ERROR)
- `logger`: Logger name (module path)
- `message`: Human-readable message
- `event`: Structured event identifier (e.g., `extract.conversation.start`)
- `conversation_id`: Conversation ID (when applicable)
- `topic_id`: Topic ID (when applicable)
- `exception`: Exception details (when errors occur)

**Event types:**
- `extract.*`: Extraction pipeline events
- `linearize.*`: Linearization events
- `compile.*`: Documentation compilation events
- `topics.*`: Topic discovery and labeling events
- `assignment.*`: Topic assignment events
- `consolidate.*`: Consolidation events

### Filtering Logs

Since logs are JSON, you can use `jq` or similar tools to filter:

```bash
# Extract only ERROR logs
ckx extract ... 2>&1 | jq 'select(.level == "ERROR")'

# Filter by conversation ID
ckx extract ... 2>&1 | jq 'select(.conversation_id == "abc-123")'

# Filter by event type
ckx extract ... 2>&1 | jq 'select(.event | startswith("extract."))'

# Count events by type
ckx extract ... 2>&1 | jq -r '.event' | sort | uniq -c
```

### Redirecting Logs

Logs are written to stderr by default, so you can redirect them separately from stdout:

```bash
# Save logs to file while seeing output
ckx extract ... 2> logs.jsonl

# Pipe logs to another tool
ckx extract ... 2>&1 | your-log-processor

# Suppress logs entirely (only see Rich UI if enabled)
ckx extract ... 2>/dev/null
```

## CLI Usage

The CLI accepts three input formats:
- **Standard export**: A JSON file containing a list of conversations (standard ChatGPT export format)
- **Single ChatGPT conversation**: A JSON file containing a single conversation object with `mapping` and `current_node` fields
- **Claude conversation**: A JSON file containing a Claude AI export with `platform="CLAUDE_AI"` and `chat_messages[]` array
- **Per-conversation directory**: A directory containing many `.json` files (each file is a single conversation object, like `chatgpt-conversations/`)

```bash
# Linearize conversations (works with all formats)
ckx linearize --input chatgpt-export.json --out _evidence
ckx linearize --input single-conversation.json --out _evidence
ckx linearize --input claude-export.json --out _evidence
ckx linearize --input chatgpt-conversations/ --out _evidence

# Extract knowledge atoms (all conversations)
ckx extract --input chatgpt-export.json --evidence _evidence --out _atoms

# Extract from a single conversation file
ckx extract --input single-conversation.json --evidence _evidence --out _atoms
ckx extract --input claude-export.json --evidence _evidence --out _atoms
ckx extract --input chatgpt-conversations/ --evidence _evidence --out _atoms

# Extract from a specific conversation in a list (for testing)
ckx extract --input chatgpt-export.json --evidence _evidence --out _atoms \
  --conversation-id 69335397-c5f4-832a-a049-8fd3cfcbf588

# Limit number of conversations processed (deterministic: first N by sorted filename)
ckx extract --input chatgpt-conversations/ --evidence _evidence --out _atoms --limit 50
ckx linearize --input chatgpt-conversations/ --out _evidence --limit 50
ckx run-all --input chatgpt-conversations/ --limit 50

# Compile docs from atoms
ckx compile --atoms _atoms --out docs

# Run all steps (works with all formats)
ckx run-all --input chatgpt-export.json
ckx run-all --input single-conversation.json
ckx run-all --input claude-export.json
ckx run-all --input chatgpt-conversations/

# Run all steps on a single conversation (for testing)
ckx run-all --input chatgpt-export.json --conversation-id 69335397-c5f4-832a-a049-8fd3cfcbf588

# Run with persistent dashboard (auto-enabled in interactive terminals)
ckx run-all --input chatgpt-conversations/ --dashboard
ckx run-all --input chatgpt-conversations/ --dashboard --dashboard-log-lines 100

# Disable dashboard (useful for CI or when piping output)
ckx run-all --input chatgpt-conversations/ --no-dashboard

# Consolidate per-conversation outputs into project-wide knowledge packet
ckx consolidate --atoms _atoms --docs docs --out output

# Consolidate without concatenating markdown docs
ckx consolidate --atoms _atoms --docs docs --out output --no-include-docs
```

### Limiting Conversations

Use the `--limit` (or `-n`) option to process only the first N conversations from a large input:

- **Directory inputs**: Selects first N files by sorted filename (deterministic ordering)
- **List exports**: Returns first N conversations after normalization
- **Single file**: Limits to N conversations (typically 1)

This is useful for testing or processing subsets of large conversation directories:

```bash
# Process only first 50 conversations from a directory
ckx run-all --input /path/to/conversations/ --limit 50

# Use with Makefile
make INPUT=/path/to/conversations/ LIMIT=50 all-with-topics
```

**Notes**:
- For single ChatGPT conversation files without an `id` or `conversation_id` field, the tool automatically uses the filename (without extension) as the conversation ID.
- Claude exports are automatically converted to ChatGPT-style format internally, using the Claude `uuid` as the conversation ID.

### Persistent Dashboard

The `run-all` command includes a **persistent terminal dashboard** that provides a live, non-scrolling view of pipeline progress:

- **Status table**: Shows all pipeline steps (Linearize, Extract, Compile) with current status, progress counts, elapsed time, rate, and ETA
- **Progress bars**: Visual progress indicators for active steps
- **Log tail**: Last N log lines displayed in a fixed panel (no scrolling flood)

The dashboard is **automatically enabled** when:
- Running in an interactive terminal (TTY detected)
- Log mode is not `machine` (human/hybrid/auto modes)

**Dashboard options:**

```bash
# Explicitly enable dashboard
ckx run-all --input conversations/ --dashboard

# Adjust number of log lines shown (default: 50)
ckx run-all --input conversations/ --dashboard-log-lines 100

# Disable dashboard (useful for CI or when piping)
ckx run-all --input conversations/ --no-dashboard
```

**Example dashboard output:**

```
┌──────────────────────────────────────────────────────────────┐
│  CKX Pipeline                                     00:35 ⏱️   │
├──────────────────────────────────────────────────────────────┤
│  Step      Status    Progress          Elapsed  Rate    ETA │
│  Linearize ✓         10/10             4.8s     2.1/s   —   │
│  Extract   ⠋         3/10 (abc-123)   12.5s    0.28/s  ~25s │
│  Compile   ○         —                 —        —      —   │
├──────────────────────────────────────────────────────────────┤
│  [Recent Logs]                                               │
│  INFO     extract: Processing conversation                   │
│  INFO     extract: Pass 2: Refining candidates              │
│  ...                                                         │
└──────────────────────────────────────────────────────────────┘
```

The dashboard updates in real-time, providing at-a-glance visibility into pipeline progress without terminal scrolling.

## Project Structure

```
.
├── _evidence/          # Linearized conversation markdown
│   └── <conversation_id>/
│       └── conversation.md
├── _atoms/            # Extracted knowledge atoms (JSONL)
│   └── <conversation_id>/
│       ├── facts.jsonl
│       ├── decisions.jsonl
│       └── open_questions.jsonl
├── docs/              # Compiled documentation (per-conversation)
│   ├── <conversation_id>/
│   │   ├── overview.md
│   │   ├── architecture.md
│   │   └── ...
│   └── decisions/
│       └── <conversation_id>/
│           └── ADR-*.md
├── output/            # Consolidated project-wide outputs
│   └── project/
│       ├── atoms.jsonl
│       ├── decisions.jsonl
│       ├── open_questions.jsonl
│       ├── manifest.md
│       ├── docs_concat.md      # (optional) Concatenated docs
│       └── adrs_concat.md      # (optional) Concatenated ADRs
└── src/ck_exporter/   # Source code
    ├── core/          # Domain models and port interfaces
    │   ├── models/    # Pydantic models (Atom, Topic, etc.)
    │   │   ├── atoms.py    # Atom, DecisionAtom, Evidence, OpenQuestion
    │   │   └── topics.py   # Topic, TopicRegistry, TopicAssignment, ConversationTopics
    │   └── ports/     # Protocol interfaces (LLMClient, Embedder, AtomExtractor, TopicLabeler)
    ├── adapters/      # Implementations of ports
    │   ├── openrouter_llm.py      # OpenRouter-backed LLM client
    │   ├── openrouter_embedder.py # OpenRouter-backed embedder
    │   ├── openrouter_atom_extractor.py  # OpenRouter-backed atom extractor
    │   └── dspy_*.py  # DSPy-backed adapters (optional)
    ├── programs/      # LLM programs (prompts, JSON parsing, DSPy signatures)
    ├── pipeline/      # Pipeline orchestration
    │   ├── extract.py      # Atom extraction pipeline
    │   ├── topics.py      # Topic discovery and labeling pipeline
    │   ├── linearize.py   # Conversation linearization
    │   ├── compile.py     # Documentation compilation
    │   ├── consolidate.py # Project-wide consolidation
    │   ├── assignment.py  # Topic assignment
    │   └── io/            # I/O utilities
    │       ├── load.py         # Input normalization (load_conversations, Claude conversion)
    │       └── schema_helpers.py  # Export schema helpers
    ├── utils/         # General utilities
    │   └── chunking.py    # Text chunking utilities
    ├── bootstrap.py   # Composition root for wiring adapters
    └── cli/           # CLI package
        ├── app.py     # Main Typer application
        └── commands/  # Command modules (linearize, extract, compile, etc.)
```

## Architecture

The codebase uses a **ports and adapters** (hexagonal) architecture pattern to enable swappable implementations:

- **Ports** (`core/ports/`): Protocol interfaces defining contracts for LLM, embeddings, atom extraction, and topic labeling
- **Adapters** (`adapters/`): Concrete implementations (OpenRouter-backed by default, DSPy optional)
- **Pipeline** (`pipeline/`): Orchestration logic that depends on ports, not concrete adapters
- **Bootstrap** (`bootstrap.py`): Composition root that wires adapters based on environment variables

This design enables:
- **DSPy integration**: DSPy programs/modules can be plugged in as new adapters without rewriting pipeline code
- **Testability**: Fake adapters can be injected for offline testing
- **Flexibility**: Easy to swap LLM providers or add new extraction strategies
- **Single source of truth**: All adapter selection logic lives in `bootstrap.py`

The existing modules (`extract_openai.py`, `embeddings.py`, `topic_discovery.py`) are backward-compatible shims that delegate to the new architecture through the bootstrap module.

### DSPy Integration (Optional)

DSPy can be used for topic labeling and atom refinement (Pass 2). This is a **wire-only** implementation (no teleprompter optimization yet).

**Installation:**
```bash
uv sync --extra dspy
```

**Enable DSPy implementations:**

Set environment variables to use DSPy adapters:

```bash
# Use DSPy for topic labeling
export CKX_TOPIC_LABELER_IMPL=dspy

# Use DSPy for atom refinement (Pass 2)
export CKX_ATOM_REFINER_IMPL=dspy

# Optional: Configure DSPy models (defaults shown)
export CKX_DSPY_LABEL_MODEL=z-ai/glm-4.7
export CKX_DSPY_REFINE_MODEL=z-ai/glm-4.7
```

**Default behavior:**
- If DSPy is not installed or env vars are unset, the system uses OpenRouter adapters (default)
- If DSPy is requested but not installed, a clear error message is shown with installation instructions

**Current DSPy implementations:**
- **Topic Labeling**: `DspyTopicLabeler` - Uses DSPy ChainOfThought to generate topic names and descriptions
- **Atom Refinement**: `DspyAtomRefiner` - Uses DSPy ChainOfThought for Pass 2 refinement/deduplication
- **Hybrid Extractor**: `HybridAtomExtractor` - Combines OpenRouter (Pass 1) with DSPy (Pass 2)

## Development

```bash
make install   # Install dependencies (uv sync)
make test      # Run tests
uv run ckx     # Run CLI commands directly
```

### Running Tests

```bash
# Run all tests
pytest

# Run unit tests only
pytest tests/unit/

# Run integration tests only
pytest tests/integration/

# Run with coverage
pytest --cov=ck_exporter --cov-report=html
```

Tests are designed to run offline (no API keys required) using fake adapters for LLM/embedding services.

## License

MIT
