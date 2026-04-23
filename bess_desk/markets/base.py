"""
Market adapter interface. Replay, live, and sim all implement this.

No conditional logic for "are we backtesting" lives outside this module —
the whole point of the pattern is that agents and the execution layer
don't know which mode they're in.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timedelta
from enum import StrEnum
from typing import Protocol

import pandas as pd


class MarketEventType(StrEnum):
    DA_GATE_OPEN = "da_gate_open"
    DA_GATE_CLOSE = "da_gate_close"
    FCR_AUCTION = "fcr_auction"
    FCR_ACTIVATION = "fcr_activation"
    PTU_BOUNDARY = "ptu_boundary"


@dataclass
class MarketEvent:
    type: MarketEventType
    timestamp: datetime
    payload: dict


@dataclass
class BidReceipt:
    accepted: bool
    reason: str | None = None


class MarketAdapter(Protocol):
    """The interface every market mode must implement."""

    def now(self) -> datetime: ...

    def advance_to(self, ts: datetime) -> list[MarketEvent]:
        """Advance clock; return events that fired between previous `now` and `ts`."""
        ...

    def get_da_history(self, lookback: timedelta) -> pd.DataFrame:
        """Historical DA prices. Columns: timestamp, price_eur_mwh."""
        ...

    def get_fcr_history(self, lookback: timedelta) -> pd.DataFrame:
        """Historical FCR symmetric capacity prices. Columns: block_start, price_eur_mw_4h."""
        ...

    def submit_bid(self, bid) -> BidReceipt:
        """Submit a bid. In replay/sim: logged to local book. In live: NEVER sends."""
        ...

    def get_clearings(self, for_date) -> pd.DataFrame:
        """Return realized clearings for a given date."""
        ...
