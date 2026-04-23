"""
Dispatcher. After the DA gate closes, manages real-time SoC against
the day's bid schedule and FCR activations.

In replay and sim modes, this is deterministic (we know activations).
In live mode, this would hook into metering and FCR signal feeds.
"""

from __future__ import annotations


def dispatch_ptu(ptu_index: int, scheduled_mw: float, fcr_activation_mw: float = 0.0):
    """TODO: apply scheduled DA commitment + FCR response to battery."""
    pass
