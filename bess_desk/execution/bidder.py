"""
Bid curve construction. Takes LP output (target power per PTU) and
builds EPEX-shaped bid curves (price-quantity pairs).

Two strategies, selected by proposal aggressiveness:
  - "limit": bid exactly at the forecast P50; take only if price is right
  - "aggressive": fan out bids around P50 to capture more volume

Stubbed — signature is final.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class BidCurve:
    """A single PTU's bid curve: price-quantity pairs, signed."""

    ptu_index: int
    price_quantity: list[tuple[float, float]]   # [(price, mw), ...]


def build_bid_curves(
    target_power: np.ndarray,        # From optimizer (96,) — positive = discharge
    forecast_p10: np.ndarray,
    forecast_p50: np.ndarray,
    forecast_p90: np.ndarray,
    aggressiveness: str = "normal",
) -> list[BidCurve]:
    """
    TODO: build proper staircase bid curves.
    """
    return []
