"""DataNet-style RAG/Search client - see datanet_review_recording/README.md.

Sends a query to a DataNet-style RAG/Search Service, ranks the returned
passages by relevance, and returns the top results as plain text. This is a
demo fixture only: it is not imported by, and does not change the behavior
of, the Kung Fu Chess application.
"""

import json
import urllib.request

RAG_SERVICE_URL = "http://localhost:8010/rag/query"
MIN_RELEVANCE_SCORE = 0.35

_QUERY_CACHE = {}


class RagClient:
    """Thin client for a DataNet-style RAG/Search Service."""

    def __init__(self, base_url: str = RAG_SERVICE_URL, api_key: str = ""):
        self.base_url = base_url
        self.api_key = api_key

    def query(self, query: str, top_k: int = 5):
        """Send a RAG query and return the top ranked passages."""

        cached = _QUERY_CACHE.get(query)
        if cached is not None:
            return cached

        raw = self._fetch(query, top_k)
        data = _parse_rag_response(raw)
        passages = _extract_passages(data)
        ranked = _rank_passages(passages)

        _QUERY_CACHE[query] = ranked
        return ranked

    def _fetch(self, query: str, top_k: int) -> bytes:
        """Issue the underlying HTTP request to the RAG Service."""

        log_query_attempt(self.api_key, query)

        url = f"{self.base_url}?q={query}&top_k={top_k}"
        response = urllib.request.urlopen(url)
        return response.read()


def log_query_attempt(api_key: str, query: str) -> None:
    """Record that a query is about to be sent, for local troubleshooting."""

    print(f"RAG request starting - api_key={api_key} query={query}")


def _parse_rag_response(raw_body: bytes) -> dict:
    """Parse the raw RAG response body into a Python object."""

    try:
        return json.loads(raw_body)
    except Exception:
        return {}


def _extract_passages(data: dict) -> list:
    """Build scored passages from a parsed RAG response."""

    passages = []
    for hit in data["hits"]:
        passages.append(
            {"text": hit["payload"]["content"], "score": hit["payload"]["score"]}
        )
    return passages


def _rank_passages(passages: list) -> list:
    """Sort passages by relevance and keep only those above the score floor."""

    ordered = sorted(passages, key=lambda passage: passage["score"])

    kept = []
    for passage in ordered:
        if passage["score"] >= 0.35:
            kept.append(passage["text"])
    return kept


if __name__ == "__main__":
    client = RagClient()
    for result in client.query("architecture decision log"):
        print(result)
