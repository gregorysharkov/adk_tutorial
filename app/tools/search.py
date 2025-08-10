from typing import TypedDict


class SearchResult(TypedDict):
    title: str
    url: str
    snippet: str


def web_search(
    query: str, *, timeout_s: float = 10.0, max_results: int = 5
) -> list[SearchResult]:
    # Placeholder implementation
    return [
        {
            "title": "Example",
            "url": "https://example.com",
            "snippet": f"Result for {query}",
        }
    ]
