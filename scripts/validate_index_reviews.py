from __future__ import annotations

import argparse
import json
from datetime import date

from egx_quant.index_reviews import (
    load_index_review_events,
    materialize_membership_deltas,
    unresolved_identity_count,
)


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Validate dated EGX index-review evidence."
    )
    parser.add_argument(
        "--reviews",
        default="evidence/index_reviews/egx30_review_events_2024_2025.json",
    )
    parser.add_argument(
        "--decision-time",
        default="2026-01-31T23:59:59Z",
    )
    parser.add_argument(
        "--allow-unresolved",
        action="store_true",
        help="Report resolved deltas without failing on unresolved identities.",
    )
    args = parser.parse_args()

    events = load_index_review_events(args.reviews)
    decision_date = date.fromisoformat(args.decision_time[:10])
    unresolved = unresolved_identity_count(events)

    try:
        deltas = materialize_membership_deltas(
            events,
            decision_date=decision_date,
            strict=not args.allow_unresolved,
        )
        blocked = False
    except RuntimeError as exc:
        deltas = ()
        blocked = True
        error = str(exc)

    payload = {
        "review_event_count": len(events),
        "unresolved_identity_count": unresolved,
        "materialized_delta_count": len(deltas),
        "decision_date": decision_date.isoformat(),
        "blocked": blocked,
    }
    if blocked:
        payload["error"] = error

    print(json.dumps(payload, indent=2, sort_keys=True))
    if blocked:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
