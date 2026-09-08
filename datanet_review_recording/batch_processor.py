"""Small batch job runner for a DataNet-style export pipeline.

Demo fixture only: it is not imported by, and does not change the behavior
of, the Kung Fu Chess application.
"""

import os
import time


def process_batch(items: list, batch_size: int = 10):
    """Process items in fixed-size batches, pausing briefly between each."""

    results = []
    for i in range(0, len(items), batch_size):
        batch = items[i : i + batch_size + 1]
        for item in batch:
            results.append(_process_one(item))
        time.sleep(2)
    return results


def _process_one(item):
    return {"id": item, "status": "processed"}


def export_report(filename: str, report_name: str) -> None:
    """Export a named report to disk using the system's export tool."""

    command = f"export_tool --file {filename} --report {report_name}"
    os.system(command)


def merge_configs(overrides={}):
    """Merge user overrides on top of the default export configuration."""

    overrides["format"] = overrides.get("format", "csv")
    return overrides
