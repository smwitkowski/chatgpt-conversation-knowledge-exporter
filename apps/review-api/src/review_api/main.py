"""FastAPI application for review UI."""

import json
import os
import sys
from pathlib import Path
from typing import Any, Dict

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import Response, StreamingResponse

# Add parent src to path for ck_exporter imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent.parent / "src"))

from review_api.addons import AddonRegistry, PanelAddon
from review_api.bundler import ZipBundler
from review_api.search import SearchIndex
from review_api.store import KnowledgeStore

# Determine base path (project root)
BASE_PATH = Path(__file__).parent.parent.parent.parent.parent.resolve()

app = FastAPI(title="Topic Review API", version="0.1.0")

# CORS middleware for React dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://localhost:5174"],  # Vite default ports
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize store, addon registry, search index, and bundler
store = KnowledgeStore(BASE_PATH)
addon_registry = AddonRegistry()
bundler = ZipBundler(store, addon_registry)
search_index = SearchIndex(store)
search_index.build_index()


@app.get("/api/topics")
async def list_topics():
    """List all topics with counts."""
    return {"topics": store.get_topics_summary()}


@app.get("/api/topics/{topic_id}")
async def get_topic(topic_id: int):
    """Get topic details with conversations."""
    detail = store.get_topic_detail(topic_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Topic not found")
    return detail


@app.get("/api/conversations/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation details with atoms and docs."""
    detail = store.get_conversation_detail(conversation_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Conversation not found")
    return detail


@app.get("/api/conversations/{conversation_id}/doc/{doc_name:path}")
async def get_doc(conversation_id: str, doc_name: str):
    """Get markdown content for a doc."""
    content = store.get_doc_content(conversation_id, doc_name)
    if content is None:
        raise HTTPException(status_code=404, detail="Doc not found")
    return Response(content=content, media_type="text/markdown")


@app.post("/api/bundles/topic/{topic_id}")
async def download_topic_bundle(topic_id: int):
    """Download zip bundle for a topic."""
    zip_data = bundler.bundle_topic(topic_id)
    if not zip_data:
        raise HTTPException(status_code=404, detail="Topic not found or no conversations")

    topic = store.topics.get(topic_id)
    filename = f"topic-{topic_id}-{topic.name.replace(' ', '-') if topic else 'unknown'}.zip"

    return StreamingResponse(
        iter([zip_data]),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.post("/api/bundles/conversation/{conversation_id}")
async def download_conversation_bundle(conversation_id: str):
    """Download zip bundle for a conversation."""
    zip_data = bundler.bundle_conversation(conversation_id)
    if not zip_data:
        raise HTTPException(status_code=404, detail="Conversation not found")

    assignment = store.assignments.get(conversation_id)
    title_safe = (assignment.title if assignment else conversation_id).replace(" ", "-")[:50]
    filename = f"conversation-{conversation_id[:8]}-{title_safe}.zip"

    return StreamingResponse(
        iter([zip_data]),
        media_type="application/zip",
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )


@app.get("/api/review-queue")
async def get_review_queue():
    """Get review queue items."""
    return {"items": store.get_review_queue()}


@app.get("/api/conversations/{conversation_id}/atoms")
async def get_conversation_atoms(
    conversation_id: str,
    atom_type: str | None = None,
    status: str | None = None,
    atom_topic: str | None = None,
    page: int = 1,
    page_size: int = 50,
):
    """Get filtered atoms for a conversation with pagination."""
    detail = store.get_conversation_detail(conversation_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Combine all atoms
    all_atoms = detail["facts"] + detail["decisions"] + detail["questions"]

    # Apply filters
    filtered = all_atoms
    if atom_type:
        filtered = [a for a in filtered if a.get("type") == atom_type]
    if status:
        filtered = [a for a in filtered if a.get("status") == status]
    if atom_topic:
        filtered = [a for a in filtered if a.get("topic") == atom_topic]

    # Paginate
    start = (page - 1) * page_size
    end = start + page_size
    paginated = filtered[start:end]

    return {
        "atoms": paginated,
        "total": len(filtered),
        "page": page,
        "page_size": page_size,
        "total_pages": (len(filtered) + page_size - 1) // page_size,
    }


@app.post("/api/conversations/{conversation_id}/atoms/export")
async def export_selected_atoms(conversation_id: str, atom_ids: list[str] | None = None):
    """Export selected atoms as JSONL."""
    detail = store.get_conversation_detail(conversation_id)
    if not detail:
        raise HTTPException(status_code=404, detail="Conversation not found")

    # Combine all atoms
    all_atoms = detail["facts"] + detail["decisions"] + detail["questions"]

    # Filter by IDs if provided
    if atom_ids:
        # Create a simple ID based on index for now (could be improved with actual IDs)
        selected = []
        for idx, atom in enumerate(all_atoms):
            atom_id = f"{conversation_id}-{idx}"
            if atom_id in atom_ids:
                selected.append(atom)
        atoms_to_export = selected
    else:
        atoms_to_export = all_atoms

    # Convert to JSONL
    jsonl_lines = [json.dumps(atom, ensure_ascii=False) for atom in atoms_to_export]
    jsonl_content = "\n".join(jsonl_lines)

    return Response(
        content=jsonl_content,
        media_type="application/x-ndjson",
        headers={
            "Content-Disposition": f'attachment; filename="atoms-{conversation_id[:8]}.jsonl"'
        },
    )


@app.get("/api/search")
async def search(q: str = Query(..., min_length=1), limit: int = Query(20, ge=1, le=100)):
    """Full-text search across topics, conversations, atoms, and docs."""
    results = search_index.search(q, limit=limit)
    return results


@app.get("/api/addons")
async def list_addons():
    """List all available addons."""
    return {"addons": addon_registry.list_all()}


@app.post("/api/addons/{addon_id}/run")
async def run_addon(addon_id: str, target: Dict[str, Any]):
    """Run an addon on a topic or conversation."""
    addon = addon_registry.get(addon_id)
    if not addon:
        raise HTTPException(status_code=404, detail="Addon not found")

    kind = target.get("kind")
    target_id = target.get("id")

    if kind == "topic":
        if not isinstance(addon, PanelAddon):
            raise HTTPException(status_code=400, detail="Addon does not support topic panels")
        data = addon.get_panel_data_topic(int(target_id), store)
        return {"addon_id": addon_id, "data": data}
    elif kind == "conversation":
        if not isinstance(addon, PanelAddon):
            raise HTTPException(status_code=400, detail="Addon does not support conversation panels")
        data = addon.get_panel_data_conversation(str(target_id), store)
        return {"addon_id": addon_id, "data": data}
    else:
        raise HTTPException(status_code=400, detail="Invalid target kind")


@app.post("/api/refresh")
async def refresh_index():
    """Rebuild search index and reload store data."""
    global store, search_index, bundler
    store = KnowledgeStore(BASE_PATH)
    bundler = ZipBundler(store, addon_registry)
    search_index = SearchIndex(store)
    search_index.build_index()
    return {
        "status": "ok",
        "topics_loaded": len(store.topics),
        "conversations_loaded": len(store.assignments),
        "index_built": True,
    }


@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "topics_loaded": len(store.topics), "conversations_loaded": len(store.assignments)}


def main():
    """Run the API server."""
    import uvicorn

    port = int(os.getenv("PORT", "8001"))
    uvicorn.run(app, host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()
