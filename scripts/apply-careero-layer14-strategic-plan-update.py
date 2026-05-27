#!/usr/bin/env python3
"""Retired helper for the superseded combined Layer 14 strategic-plan update.

The former combined Layer 14 plan bundled model catalog / prompt architecture /
credits with API job-source ingestion and source-governed research. That planning
boundary has been split:

- Layer 14: docs/careero-layer-14-model-catalog-and-prompt-architecture.md
- Layer 15: docs/careero-layer-15-api-job-sources-and-managed-deltas.md

The canonical matrix and build order now live in:

- docs/careero-application-plan-and-layer-status.md

This script intentionally performs no mutation. It remains only as a compatibility
breadcrumb for anyone who finds the old script name in history.
"""

from __future__ import annotations


def main() -> None:
    print(
        "This helper is retired. Use docs/careero-application-plan-and-layer-status.md "
        "plus the split Layer 14 and Layer 15 docs instead."
    )


if __name__ == "__main__":
    main()
