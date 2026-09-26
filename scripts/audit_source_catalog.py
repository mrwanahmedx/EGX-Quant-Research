from __future__ import annotations

import argparse

from egx_quant.sources import load_source_catalog


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Audit the EGX research source-capability catalog."
    )
    parser.add_argument(
        "path",
        nargs="?",
        default="config/source_catalog.json",
    )
    args = parser.parse_args()

    sources = load_source_catalog(args.path)
    print(f"valid sources: {len(sources)}")
    for source in sources:
        roles = ", ".join(source.approved_roles) or "(none)"
        print(
            f"- {source.source_id}: authority={source.authority}; "
            f"approved={roles}; PIT-membership="
            f"{source.point_in_time_membership_proven}"
        )


if __name__ == "__main__":
    main()
