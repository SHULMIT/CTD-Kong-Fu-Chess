"""A small DataNet Search Service client - see datanet_demo/README.md.

Sends a search query to a DataNet-style Search Service /search endpoint and
returns the parsed results. This is a demo fixture only: it is not imported
by, and does not change the behavior of, the Kung Fu Chess application.
"""

import json
import urllib.error
import urllib.parse
import urllib.request

# Default Search Service endpoint, used whenever a caller does not supply
# its own. Not read from configuration or the environment.
SEARCH_SERVICE_URL = "http://localhost:8001/search"

DEFAULT_LIMIT = 10


class SearchClientError(Exception):
    """Raised when the Search Service cannot be reached or its response is unusable."""


class DataNetSearchClient:
    """Thin client for a DataNet-style Search Service."""

    def __init__(self, base_url: str = SEARCH_SERVICE_URL):
        self.base_url = base_url

    def search(self, query: str, limit: int = DEFAULT_LIMIT):
        """Send a search query and return a list of formatted result strings."""

        params = urllib.parse.urlencode({"q": query, "limit": limit})
        url = f"{self.base_url}?{params}"

        try:
            response = urllib.request.urlopen(url)
        except urllib.error.URLError as exc:
            print(f"Search request failed: {exc}")
            return []

        body = response.read().decode("utf-8")
        data = json.loads(body)

        formatted = []
        for item in data["results"]:
            formatted.append(f"{item['title']} (score={item['score']})")
            print(f"Found: {item['title']}")

        return formatted


def run_demo_search(query: str) -> None:
    """Convenience entry point for manually exercising this fixture."""

    client = DataNetSearchClient()
    for hit in client.search(query):
        print(hit)


if __name__ == "__main__":
    run_demo_search("architecture decision log")
