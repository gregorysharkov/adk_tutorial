from typing import TypedDict


class Passage(TypedDict):
    text: str
    source_uri: str
    chunk_id: str
    score: float
    metadata: dict[str, str]


def retrieve(query: str, *, top_k: int = 8, min_score: float = 0.3) -> list[Passage]:
    # Placeholder implementation
    return [
        {
            "text": "Company overview...",
            "source_uri": "doc://kb/acme/overview.md",
            "chunk_id": "1",
            "score": 0.85,
            "metadata": {"company": "acme"},
        }
    ]
