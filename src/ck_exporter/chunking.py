"""Text chunking utilities for conversation processing."""

from typing import List, Optional

try:
    import tiktoken
    HAS_TIKTOKEN = True
except ImportError:
    HAS_TIKTOKEN = False


def estimate_tokens(text: str, model: str = "gpt-5.2") -> int:
    """Estimate token count for text."""
    if HAS_TIKTOKEN:
        try:
            encoding = tiktoken.encoding_for_model(model)
            return len(encoding.encode(text))
        except Exception:
            pass

    # Fallback: rough estimate (1 token ≈ 4 characters)
    return len(text) // 4


def chunk_text(
    text: str,
    max_tokens: int = 8000,
    overlap_tokens: int = 200,
    model: str = "gpt-5.2",
) -> List[str]:
    """
    Split text into chunks with token-based sizing.

    Args:
        text: Text to chunk
        max_tokens: Maximum tokens per chunk
        overlap_tokens: Token overlap between chunks
        model: Model name for tokenization

    Returns:
        List of text chunks
    """
    if not text.strip():
        return []

    # Estimate total tokens
    total_tokens = estimate_tokens(text, model)

    if total_tokens <= max_tokens:
        return [text]

    chunks = []
    current_pos = 0
    text_length = len(text)

    while current_pos < text_length:
        # Try to find a good break point
        end_pos = min(current_pos + max_tokens * 4, text_length)  # Rough char estimate

        # If not at end, try to break at sentence boundary
        if end_pos < text_length:
            # Look for sentence endings
            for punct in [".\n\n", ".\n", ". ", "!\n\n", "!\n", "! ", "?\n\n", "?\n", "? "]:
                last_break = text.rfind(punct, current_pos, end_pos)
                if last_break > current_pos:
                    end_pos = last_break + len(punct)
                    break

        chunk = text[current_pos:end_pos].strip()
        if chunk:
            chunks.append(chunk)

        # Move forward with overlap
        if end_pos >= text_length:
            break
        current_pos = max(current_pos + 1, end_pos - overlap_tokens * 4)

    return chunks


def chunk_messages(
    messages: List[dict],
    max_tokens: int = 8000,
    overlap_tokens: int = 200,
    model: str = "gpt-5.2",
) -> List[List[dict]]:
    """
    Chunk a list of messages into groups that fit within token limits.

    Returns:
        List of message groups (each group is a list of messages)
    """
    if not messages:
        return []

    chunks = []
    current_chunk = []
    current_tokens = 0

    for msg in messages:
        msg_text = msg.get("text", "")
        msg_tokens = estimate_tokens(msg_text, model)

        # If single message exceeds limit, add it alone
        if msg_tokens > max_tokens:
            if current_chunk:
                chunks.append(current_chunk)
                current_chunk = []
            chunks.append([msg])
            current_tokens = 0
            continue

        # Check if adding this message would exceed limit
        if current_tokens + msg_tokens > max_tokens and current_chunk:
            chunks.append(current_chunk)
            current_chunk = []
            current_tokens = 0

        current_chunk.append(msg)
        current_tokens += msg_tokens

    if current_chunk:
        chunks.append(current_chunk)

    return chunks
