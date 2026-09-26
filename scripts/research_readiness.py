from __future__ import annotations

import argparse
import json

from egx_quant.readiness import build_repository_readiness_report


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Report whether the repository is ready for real model development."
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Emit JSON instead of human-readable output.",
    )
    args = parser.parse_args()

    report = build_repository_readiness_report()

    payload = {
        "modeling_authorized": report.modeling_authorized,
        "checks": [
            {
                "check_id": check.check_id,
                "passed": check.passed,
                "detail": check.detail,
            }
            for check in report.checks
        ],
    }

    if args.json:
        print(json.dumps(payload, indent=2, sort_keys=True))
    else:
        state = "AUTHORIZED" if report.modeling_authorized else "BLOCKED"
        print(f"REAL MODEL DEVELOPMENT: {state}")
        for check in report.checks:
            marker = "PASS" if check.passed else "BLOCK"
            print(f"[{marker}] {check.check_id}: {check.detail}")

    if not report.modeling_authorized:
        raise SystemExit(2)


if __name__ == "__main__":
    main()
