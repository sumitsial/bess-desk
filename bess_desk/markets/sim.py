"""
Simulation adapter. Generates synthetic DA and FCR prices from a
configurable process (AR(1) + seasonal + jumps). Useful for stress-
testing strategies against regimes not present in historical data.

TODO: full implementation.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from bess_desk.markets.base import BidReceipt, MarketEvent


class SimAdapter:
    """Generates synthetic market data."""

    def __init__(
        self,
        seed: int = 42,
        volatility: float = 30.0,
        jump_intensity: float = 0.02,
        start: datetime | None = None,
    ) -> None:
        self.seed = seed
        self.volatility = volatility
        self.jump_intensity = jump_intensity
        self._clock = start
        # TODO: pre-generate price path from seed

    def now(self) -> datetime:
        if self._clock is None:
            raise RuntimeError("Clock not initialized")
        return self._clock

    def advance_to(self, ts: datetime) -> list[MarketEvent]:
        self._clock = ts
        return []

    def get_da_history(self, lookback: timedelta) -> pd.DataFrame:
        return pd.DataFrame(columns=["timestamp", "price_eur_mwh"])

    def get_fcr_history(self, lookback: timedelta) -> pd.DataFrame:
        return pd.DataFrame(columns=["block_start", "price_eur_mw_4h"])

    def submit_bid(self, bid) -> BidReceipt:
        return BidReceipt(accepted=True)

    def get_clearings(self, for_date) -> pd.DataFrame:
        return pd.DataFrame()
