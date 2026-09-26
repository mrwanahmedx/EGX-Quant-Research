from __future__ import annotations

import argparse

from egx_quant.readiness_snapshot import write_readiness_snapshot


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Write the repository's current model-development readiness state."
    )
    parser.add_argument("--output", default="readiness_snapshot.json")
    parser.add_argument(
        "--generated-at",
        default=None,
        help="Optional fixed ISO timestamp for reproducible tests.",
    )
    args = parser.parse_args()

    payload = write_readiness_snapshot(
        args.output,
        generated_at=args.generated_at,
    )
    state = "AUTHORIZED" if payload["modeling_authorized"] else "BLOCKED"
    print(
        f"{state}: {payload['blocker_count']} blocker(s); "
        f"snapshot written to {args.output}"
    )


if __name__ == "__main__":
    main()
