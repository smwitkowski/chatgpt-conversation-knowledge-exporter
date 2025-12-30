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

The CLI accepts three input formats:
- **Standard export**: A JSON file containing a list of conversations (standard ChatGPT export format)
- **Single ChatGPT conversation**: A JSON file containing a single conversation object with `mapping` and `current_node` fields
- **Claude conversation**: A JSON file containing a Claude AI export with `platform="CLAUDE_AI"` and `chat_messages[]` array

```bash
# Linearize conversations (works with all formats)
ckx linearize --input chatgpt-export.json --out _evidence
ckx linearize --input single-conversation.json --out _evidence
ckx linearize --input claude-export.json --out _evidence

# Extract knowledge atoms (all conversations)
ckx extract --input chatgpt-export.json --evidence _evidence --out _atoms

# Extract from a single conversation file
ckx extract --input single-conversation.json --evidence _evidence --out _atoms
ckx extract --input claude-export.json --evidence _evidence --out _atoms

# Extract from a specific conversation in a list (for testing)
ckx extract --input chatgpt-export.json --evidence _evidence --out _atoms \
  --conversation-id 69335397-c5f4-832a-a049-8fd3cfcbf588

# Compile docs from atoms
ckx compile --atoms _atoms --out docs

# Run all steps (works with all formats)
ckx run-all --input chatgpt-export.json
ckx run-all --input single-conversation.json
ckx run-all --input claude-export.json

# Run all steps on a single conversation (for testing)
ckx run-all --input chatgpt-export.json --conversation-id 69335397-c5f4-832a-a049-8fd3cfcbf588
```

**Notes**:
- For single ChatGPT conversation files without an `id` or `conversation_id` field, the tool automatically uses the filename (without extension) as the conversation ID.
- Claude exports are automatically converted to ChatGPT-style format internally, using the Claude `uuid` as the conversation ID.

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
