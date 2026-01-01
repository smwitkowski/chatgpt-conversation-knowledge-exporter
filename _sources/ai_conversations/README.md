# AI Conversations

This directory contains AI conversation exports from various platforms.

## Supported Formats

- **ChatGPT exports**: JSON files (list of conversations or single conversation objects)
- **Claude exports**: JSON files with `platform="CLAUDE_AI"` and `chat_messages[]`
- **Per-conversation files**: Directory containing multiple `.json` files, one per conversation

## File Examples

- `chatgpt-export.json` - Standard ChatGPT export (list of conversations)
- `claude-export.json` - Claude AI export
- `chatgpt-conversations/` - Directory with per-conversation JSON files

## Usage

```bash
# Process all conversations in this directory
ckx run-all --input _sources/ai_conversations/

# Process a specific export file
ckx linearize --input _sources/ai_conversations/chatgpt-export.json
```

