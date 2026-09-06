# DataNet Integration Demo

This directory is a small, self-contained fixture used to exercise the
**DataNet Code Review Agent**'s on-demand review flow (triggered by the
"Run Code Review" GitHub Check Run action).

It is not part of the Kung Fu Chess application: nothing else in this
repository imports it, and nothing here changes the behavior of the game
server, its tests, or its CI. It exists only so the Code Review Agent's
reviewers have a small, realistic piece of DataNet-style code to analyze.

This fixture is used for webhook and Check Run integration testing.

## Contents

- `search_client.py` - a small client for a DataNet-style Search Service
  `/search` endpoint: sends a query, parses the JSON response, and returns
  formatted results. It deliberately includes a few realistic, demo-only
  issues for the reviewers to find - a hardcoded default service URL, a
  network call with no timeout, incomplete error handling, and unvalidated
  response parsing. None of them are dangerous, exploitable, or capable of
  affecting this repository or the machine running it.

## Safe to remove

This directory can be deleted at any time without affecting the Kung Fu
Chess application - no other file in this repository depends on it.

Permission-update webhook retest.
