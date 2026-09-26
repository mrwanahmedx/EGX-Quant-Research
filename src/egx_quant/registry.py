from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any


@dataclass(frozen=True)
class Trial:
    trial_id: str
    family: str
    params: dict[str, Any]
    data_fingerprint: str
    feature_set: str
    target: str


@dataclass
class TrialRegistry:
    trials: list[Trial] = field(default_factory=list)

    def add(self, trial: Trial) -> None:
        if any(existing.trial_id == trial.trial_id for existing in self.trials):
            raise ValueError(f"duplicate trial id: {trial.trial_id}")
        self.trials.append(trial)

    def count_by_family(self) -> dict[str, int]:
        out: dict[str, int] = {}
        for trial in self.trials:
            out[trial.family] = out.get(trial.family, 0) + 1
        return out
