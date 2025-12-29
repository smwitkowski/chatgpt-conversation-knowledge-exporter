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
   make linearize  # Extract conversations to markdown
   make extract    # Extract knowledge atoms using OpenAI
   make compile    # Compile atoms into docs
   ```

## CLI Usage

```bash
# Linearize conversations
ckx linearize --input chatgpt-export.json --out _evidence

# Extract knowledge atoms (all conversations)
ckx extract --input chatgpt-export.json --evidence _evidence --out _atoms

# Extract from a single conversation (for testing)
ckx extract --input chatgpt-export.json --evidence _evidence --out _atoms \
  --conversation-id 69335397-c5f4-832a-a049-8fd3cfcbf588

# Compile docs from atoms
ckx compile --atoms _atoms --out docs

# Run all steps
ckx run-all --input chatgpt-export.json

# Run all steps on a single conversation (for testing)
ckx run-all --input chatgpt-export.json --conversation-id 69335397-c5f4-832a-a049-8fd3cfcbf588
```

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
├── docs/              # Compiled documentation
│   ├── <conversation_id>/
│   │   ├── overview.md
│   │   ├── architecture.md
│   │   └── ...
│   └── decisions/
│       └── <conversation_id>/
│           └── ADR-*.md
└── src/ck_exporter/   # Source code
```

## Development

```bash
make install   # Install dependencies (uv sync)
make test      # Run tests
uv run ckx     # Run CLI commands directly
```

## License

MIT
