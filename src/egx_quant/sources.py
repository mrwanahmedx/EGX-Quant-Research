from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class SourceDefinition:
    source_id: str
    name: str
    source_url: str
    authority: str
    license_status: str
    coverage_claim: str
    approved_roles: tuple[str, ...]
    prohibited_roles: tuple[str, ...]
    point_in_time_membership_proven: bool
    notes: str = ""

    def allows(self, role: str) -> bool:
        return role in self.approved_roles and role not in self.prohibited_roles


def load_source_catalog(path: str | Path) -> tuple[SourceDefinition, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list) or not raw:
        raise ValueError("source catalog must be a non-empty list")

    sources = tuple(
        SourceDefinition(
            source_id=row["source_id"],
            name=row["name"],
            source_url=row["source_url"],
            authority=row["authority"],
            license_status=row["license_status"],
            coverage_claim=row["coverage_claim"],
            approved_roles=tuple(row["approved_roles"]),
            prohibited_roles=tuple(row["prohibited_roles"]),
            point_in_time_membership_proven=bool(
                row["point_in_time_membership_proven"]
            ),
            notes=row.get("notes", ""),
        )
        for row in raw
    )
    validate_source_catalog(sources)
    return sources


def validate_source_catalog(sources: Iterable[SourceDefinition]) -> None:
    sources = tuple(sources)
    ids = [source.source_id for source in sources]
    if len(ids) != len(set(ids)):
        raise ValueError("duplicate source IDs")

    for source in sources:
        if not source.source_url.startswith(("https://", "http://")):
            raise ValueError(f"source URL is not absolute: {source.source_id}")
        overlap = set(source.approved_roles) & set(source.prohibited_roles)
        if overlap:
            raise ValueError(
                f"source has contradictory role policy: "
                f"{source.source_id}: {sorted(overlap)}"
            )
        if (
            "historical_membership_source" in source.approved_roles
            and not source.point_in_time_membership_proven
        ):
            raise ValueError(
                f"{source.source_id} cannot provide historical membership "
                "without point-in-time evidence"
            )


def require_role(
    sources: Iterable[SourceDefinition],
    source_id: str,
    role: str,
) -> SourceDefinition:
    matches = [source for source in sources if source.source_id == source_id]
    if len(matches) != 1:
        raise RuntimeError(f"source not found or ambiguous: {source_id}")
    source = matches[0]
    if not source.allows(role):
        raise RuntimeError(
            f"source {source_id} is not approved for research role {role}"
        )
    return source
