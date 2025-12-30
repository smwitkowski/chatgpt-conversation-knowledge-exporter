# Source Files Directory

This directory contains the raw input files for knowledge extraction, organized by source type.

## Directory Structure

- **`ai_conversations/`** - AI conversation exports (ChatGPT, Claude, Gemini, etc.)
  - JSON files containing conversation exports
  - Supports standard export formats, single conversation files, and per-conversation directories

- **`meeting_artifacts/`** - Meeting notes and transcripts
  - Markdown files (`.md`) - Google Meet notes, Zoom notes, etc.
  - Plain text files (`.txt`) - Teams transcripts, Zoom transcripts, etc.

## Usage

Process all sources:

```bash
# Process AI conversations
ckx run-all --input _sources/ai_conversations/

# Process meeting artifacts
ckx run-all --input _sources/meeting_artifacts/

# Or process individual files/directories
ckx linearize --input _sources/ai_conversations/chatgpt_export.json
ckx extract --input _sources/meeting_artifacts/meeting_notes.md
```

## File Organization

- Place your conversation exports in `ai_conversations/`
- Place your meeting notes and transcripts in `meeting_artifacts/`
- The pipeline will process all supported file types in each directory
- Outputs will be written to `_evidence/` and `_atoms/` directories

