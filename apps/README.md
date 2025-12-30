# Review UI & API

Topic review interface for browsing discovered topics and conversations.

## Architecture

- **review-api**: Python FastAPI service that reads from `output/`, `docs/`, `_atoms/`, `_evidence/`
- **review-ui**: React frontend (Vite + TypeScript)
- **review-addons**: Directory for custom addons

## Quick Start

### 1. Start the API

```bash
cd apps/review-api
pip install -e .
python -m review_api.main
```

The API will run on http://localhost:8000

### 2. Start the UI

```bash
cd apps/review-ui
npm install
npm run dev
```

The UI will run on http://localhost:5173

### 3. Open in Browser

Navigate to http://localhost:5173

## Features

- **Topic Browser**: Browse discovered topics with conversation counts and atom statistics
- **Conversation Detail**: View compiled docs, facts, decisions, and questions
- **Atom Explorer**: Filter atoms by type, status, and topic tag; export selected atoms
- **Full-Text Search**: Search across topics, conversations, atoms, and docs
- **Review Queue**: View conversations flagged for manual review
- **Download Bundles**: Download zip bundles for topics or conversations (includes docs, ADRs, atoms, evidence)
- **Addons**: Extensible addon system for exporters and UI panels

## API Endpoints

- `GET /api/topics` - List all topics
- `GET /api/topics/{topic_id}` - Get topic details
- `GET /api/conversations/{conversation_id}` - Get conversation details
- `GET /api/conversations/{conversation_id}/doc/{doc_name}` - Get markdown doc content
- `POST /api/bundles/topic/{topic_id}` - Download topic bundle
- `POST /api/bundles/conversation/{conversation_id}` - Download conversation bundle
- `GET /api/search?q=...` - Full-text search
- `GET /api/review-queue` - Get review queue
- `POST /api/refresh` - Rebuild search index
- `GET /api/addons` - List available addons
- `POST /api/addons/{addon_id}/run` - Run an addon

## Addons

Built-in addons:
- **Topic Brief**: Generates markdown brief for topics
- **Atoms CSV**: Exports atoms as CSV
- **Topic Statistics**: Panel showing topic stats and distributions

Custom addons can be added in `apps/review-addons/` by implementing the `Addon` interface.
