import json
from dataclasses import asdict

from .domain import Action, Recommendation


def render(recs: list[Recommendation], fresh_capital: float, reserve_pct: float) -> str:
    actionable = [r for r in recs if r.action != Action.WATCH]
    lines = ["EGX PORTFOLIO ACTIONS", "=" * 82,
             f"Fresh capital: EGP {fresh_capital:,.0f} | minimum reserve: EGP {fresh_capital*reserve_pct:,.0f}", ""]
    for r in actionable:
        size = f"EGP {r.allocation_egp:,.0f} / {r.shares} shares" if r.allocation_egp else "no new cash"
        reason = "; ".join(r.reasons[:3]) or "composite model score"
        extra = f" -> {r.rotate_to}" if r.action == Action.ROTATE and r.rotate_to else ""
        lines.append(f"{r.action.value:<6} {r.ticker:<5}{extra:<10} {r.strategy.value:<6} score {r.score:>4.1f} | data {r.data_quality:>3.0f} | {size}")
        if r.action in {Action.BUY, Action.ADD}:
            lines.append(f"       entry {r.entry_low:.2f}-{r.entry_high:.2f} | stop {r.stop:.2f} | targets {r.target_1:.2f}/{r.target_2:.2f}")
        lines.append(f"       {reason}")
    watches = sorted((r for r in recs if r.action == Action.WATCH), key=lambda x: x.score, reverse=True)[:7]
    if watches:
        lines.extend(["", "WATCH: " + ", ".join(f"{r.ticker} {r.score:.0f} (data {r.data_quality:.0f})" for r in watches)])
    lines.extend(["", "Safety rule: normal scans never fabricate missing price history. Low-data names stay HOLD/WATCH until real data is loaded."])
    return "\n".join(lines)


def as_json(recs: list[Recommendation]) -> str:
    rows = []
    for r in recs:
        row = asdict(r); row["strategy"] = r.strategy.value; row["action"] = r.action.value; rows.append(row)
    return json.dumps(rows, indent=2)
