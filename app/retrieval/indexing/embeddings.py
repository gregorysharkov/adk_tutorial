from typing import List


def embed_texts(
    texts: List[str], model: str = "text-embedding-004"
) -> List[List[float]]:
    # Placeholder embedding vectors
    return [[0.0, 0.0, 0.0] for _ in texts]
