"""
Replay adapter. Reads historical CSVs of DA and FCR prices, advances a
virtual clock through them, serves prices in order.

This is the market mode for backtesting. Bids are logged to a local
order book but never sent anywhere.

TODO: full implementation.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from pathlib import Path

import pandas as pd

from bess_desk.markets.base import BidReceipt, MarketAdapter, MarketEvent


class ReplayAdapter:
    """Implements MarketAdapter by replaying historical price data."""

    def __init__(
        self,
        da_csv: str | Path,
        fcr_csv: str | Path | None = None,
        start: datetime | None = None,
        end: datetime | None = None,
    ) -> None:
        self.da_csv = Path(da_csv)
        self.fcr_csv = Path(fcr_csv) if fcr_csv else None
        self._clock: datetime | None = start
        self._end = end
        self._bid_book: list = []   # Local "submitted" bids
        # TODO: load CSVs into pandas, index by timestamp

    def now(self) -> datetime:
        if self._clock is None:
            raise RuntimeError("Clock not initialized; pass `start` to constructor")
        return self._clock

    def advance_to(self, ts: datetime) -> list[MarketEvent]:
        """TODO: emit DA gate open/close, FCR auction, PTU boundaries."""
        self._clock = ts
        return []

    def get_da_history(self, lookback: timedelta) -> pd.DataFrame:
        """TODO: read CSV, filter to [now - lookback, now]."""
        return pd.DataFrame(columns=["timestamp", "price_eur_mwh"])

    def get_fcr_history(self, lookback: timedelta) -> pd.DataFrame:
        return pd.DataFrame(columns=["block_start", "price_eur_mw_4h"])

    def submit_bid(self, bid) -> BidReceipt:
        self._bid_book.append(bid)
        return BidReceipt(accepted=True)

    def get_clearings(self, for_date) -> pd.DataFrame:
        return pd.DataFrame()
