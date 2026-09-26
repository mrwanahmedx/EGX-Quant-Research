from __future__ import annotations

import json
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Iterable


@dataclass(frozen=True)
class ReviewMember:
    company_name: str
    canonical_security_id: str | None
    identity_status: str


@dataclass(frozen=True)
class IndexReviewEvent:
    index_id: str
    published_date: date
    effective_date: date
    source_url: str
    source_type: str
    additions: tuple[ReviewMember, ...]
    deletions: tuple[ReviewMember, ...]
    notes: str = ""

    def __post_init__(self) -> None:
        if self.effective_date < self.published_date:
            raise ValueError("index review cannot be effective before publication")
        if self.source_type not in {
            "official",
            "official_republication",
            "secondary_reporting",
        }:
            raise ValueError("unsupported index-review source type")


@dataclass(frozen=True)
class MembershipDelta:
    index_id: str
    effective_date: date
    canonical_security_id: str
    action: str
    source_url: str
    published_date: date

    def __post_init__(self) -> None:
        if self.action not in {"add", "delete"}:
            raise ValueError("action must be add or delete")


def load_index_review_events(
    path: str | Path,
) -> tuple[IndexReviewEvent, ...]:
    raw = json.loads(Path(path).read_text(encoding="utf-8"))
    if not isinstance(raw, list):
        raise ValueError("index-review evidence must be a list")

    events = []
    for row in raw:
        member = lambda item: ReviewMember(
            company_name=item["company_name"],
            canonical_security_id=item.get("canonical_security_id"),
            identity_status=item["identity_status"],
        )
        events.append(
            IndexReviewEvent(
                index_id=row["index_id"],
                published_date=date.fromisoformat(row["published_date"]),
                effective_date=date.fromisoformat(row["effective_date"]),
                source_url=row["source_url"],
                source_type=row["source_type"],
                additions=tuple(member(x) for x in row["additions"]),
                deletions=tuple(member(x) for x in row["deletions"]),
                notes=row.get("notes", ""),
            )
        )
    validate_review_sequence(events)
    return tuple(events)


def validate_review_sequence(events: Iterable[IndexReviewEvent]) -> None:
    last_effective: dict[str, date] = {}
    seen: set[tuple[str, date]] = set()
    for event in sorted(events, key=lambda e: (e.index_id, e.effective_date)):
        key = (event.index_id, event.effective_date)
        if key in seen:
            raise ValueError(f"duplicate index review event: {key}")
        seen.add(key)
        previous = last_effective.get(event.index_id)
        if previous is not None and event.effective_date <= previous:
            raise ValueError("index review effective dates are not increasing")
        last_effective[event.index_id] = event.effective_date


def canonical_identity_complete(event: IndexReviewEvent) -> bool:
    members = event.additions + event.deletions
    return all(
        member.identity_status == "verified"
        and bool(member.canonical_security_id)
        for member in members
    )


def unresolved_identity_count(events: Iterable[IndexReviewEvent]) -> int:
    return sum(
        1
        for event in events
        for member in event.additions + event.deletions
        if member.identity_status != "verified"
        or not member.canonical_security_id
    )


def apply_review_event(
    membership: set[str],
    event: IndexReviewEvent,
    *,
    as_of: date,
) -> set[str]:
    """Apply one dated review only when identity mapping is complete and effective."""
    if as_of < event.effective_date:
        return set(membership)
    if not canonical_identity_complete(event):
        raise RuntimeError(
            f"cannot apply {event.index_id} review {event.effective_date}: "
            "canonical identity mapping is incomplete"
        )
    output = set(membership)
    for member in event.deletions:
        output.discard(member.canonical_security_id)  # type: ignore[arg-type]
    for member in event.additions:
        output.add(member.canonical_security_id)  # type: ignore[arg-type]
    return output


def materialize_membership_deltas(
    events: Iterable[IndexReviewEvent],
    *,
    decision_date: date,
    strict: bool = True,
) -> tuple[MembershipDelta, ...]:
    """Materialize only review changes known by decision_date.

    Date-only publication evidence is treated conservatively: an event is only
    visible when published_date <= decision_date. In strict mode, any unresolved
    company identity in a visible review blocks materialisation.
    """
    output: list[MembershipDelta] = []

    for event in sorted(events, key=lambda e: (e.index_id, e.effective_date)):
        if event.published_date > decision_date:
            continue

        changes = [
            ("add", member) for member in event.additions
        ] + [
            ("delete", member) for member in event.deletions
        ]

        for action, member in changes:
            if (
                member.identity_status != "verified"
                or not member.canonical_security_id
            ):
                if strict:
                    raise RuntimeError(
                        "index membership reconstruction blocked by unresolved "
                        f"identity: {event.index_id} / {member.company_name} / "
                        f"{event.effective_date.isoformat()}"
                    )
                continue

            output.append(
                MembershipDelta(
                    index_id=event.index_id,
                    effective_date=event.effective_date,
                    canonical_security_id=member.canonical_security_id,
                    action=action,
                    source_url=event.source_url,
                    published_date=event.published_date,
                )
            )

    return tuple(
        sorted(
            output,
            key=lambda x: (
                x.index_id,
                x.effective_date,
                x.canonical_security_id,
                x.action,
            ),
        )
    )


def reconstruct_membership(
    *,
    seed_members: Iterable[str],
    deltas: Iterable[MembershipDelta],
    index_id: str,
    as_of: date,
) -> frozenset[str]:
    """Apply effective deltas to an explicit dated seed constituent set."""
    members = set(seed_members)
    for delta in sorted(
        (
            d
            for d in deltas
            if d.index_id == index_id and d.effective_date <= as_of
        ),
        key=lambda x: (x.effective_date, x.canonical_security_id, x.action),
    ):
        if delta.action == "add":
            members.add(delta.canonical_security_id)
        else:
            members.discard(delta.canonical_security_id)
    return frozenset(members)
