"""
Budget tracking. Each agent has a monthly token budget; hitting it pauses
the agent. This is a cost safety mechanism, not a performance mechanism.

Stubbed for v0 — the Agent base class tracks tokens per instance. A proper
implementation persists counters across restarts and supports per-agent
alerting.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class BudgetLedger:
    """TODO: persist to DB, alert on 80% utilization, support monthly reset."""

    monthly_cap: int
    used: int = 0

    def can_spend(self, tokens: int) -> bool:
        return self.used + tokens <= self.monthly_cap

    def charge(self, tokens: int) -> None:
        self.used += tokens

    @property
    def utilization(self) -> float:
        return self.used / self.monthly_cap if self.monthly_cap > 0 else 0.0
