# DataNet Review Recording Fixture

This directory is a small, self-contained fixture used to demonstrate the
**DataNet Code Review Agent**'s on-demand review flow end to end (triggered
by the "Run Code Review" GitHub Check Run action).

It is not part of the Kung Fu Chess application: nothing else in this
repository imports it, and nothing here changes the behavior of the game
server, its tests, or its CI.

## Contents

- `rag_client.py` - a small client for a DataNet-style RAG/Search Service:
  sends a query, parses the response, ranks the returned passages by
  relevance, and returns the top results.

## Safe to remove

This directory can be deleted at any time without affecting the Kung Fu
Chess application - no other file in this repository depends on it.
