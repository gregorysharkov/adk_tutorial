from typing import Dict, List, TypedDict


class Passage(TypedDict):
    text: str
    source_uri: str
    chunk_id: str
    score: float
    metadata: Dict[str, str]


def retrieve(query: str, *, top_k: int = 8, min_score: float = 0.3) -> List[Passage]:
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
