"""
P&L accounting with attribution by product.

For each day: revenue from DA arbitrage, revenue from FCR capacity,
degradation cost charged against cycle throughput.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DailyPnL:
    date: str
    da_revenue: float = 0.0
    fcr_revenue: float = 0.0
    degradation_cost: float = 0.0
    cycles_used: float = 0.0

    @property
    def net(self) -> float:
        return self.da_revenue + self.fcr_revenue - self.degradation_cost


def compute_daily_pnl(fills, bids, battery_state_start, battery_state_end) -> DailyPnL:
    """TODO: full implementation from fill tickets."""
    return DailyPnL(date="STUB")
