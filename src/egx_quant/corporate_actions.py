from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from typing import Iterable


@dataclass(frozen=True)
class CorporateAction:
    action_id: str
    canonical_security_id: str
    action_type: str
    effective_date: date
    published_at: datetime
    source_url: str
    status: str
    adjustment_basis: str | None = None

    def __post_init__(self) -> None:
        if self.status not in {"resolved", "unresolved"}:
            raise ValueError("unsupported corporate-action status")
        if self.status == "resolved" and self.adjustment_basis is None:
            raise ValueError(
                "resolved corporate action requires documented adjustment basis"
            )


def unresolved_actions_in_window(
    actions: Iterable[CorporateAction],
    *,
    canonical_security_id: str,
    entry_date: date,
    exit_date: date,
) -> tuple[CorporateAction, ...]:
    if exit_date < entry_date:
        raise ValueError("exit date precedes entry date")
    return tuple(
        action
        for action in actions
        if action.canonical_security_id == canonical_security_id
        and entry_date < action.effective_date <= exit_date
        and action.status != "resolved"
    )


def require_target_window_resolved(
    actions: Iterable[CorporateAction],
    *,
    canonical_security_id: str,
    entry_date: date,
    exit_date: date,
) -> None:
    unresolved = unresolved_actions_in_window(
        actions,
        canonical_security_id=canonical_security_id,
        entry_date=entry_date,
        exit_date=exit_date,
    )
    if unresolved:
        ids = ", ".join(action.action_id for action in unresolved)
        raise RuntimeError(
            f"target window crosses unresolved corporate action(s): {ids}"
        )


def action_known_by(
    action: CorporateAction,
    *,
    decision_time: datetime,
) -> bool:
    return action.published_at <= decision_time
