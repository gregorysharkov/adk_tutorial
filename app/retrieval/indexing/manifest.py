from dataclasses import dataclass


@dataclass
class IndexManifest:
    company: str
    version: str
    embedding_model: str
    chunk_size: int
    chunk_overlap: int
