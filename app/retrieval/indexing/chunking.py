from typing import List


def chunk_text(text: str, size: int = 800, overlap: int = 150) -> List[str]:
    if not text:
        return []
    # Minimal placeholder chunker
    return [text[:size]]
