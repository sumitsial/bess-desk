"""
Battery model. Tracks SoC, accounts for round-trip efficiency, enforces
power and SoC limits, tracks cycles for degradation budget.

Deliberately simple: a CC/CV or voltage model is overkill for a
day-ahead / FCR optimizer. Energy-based bookkeeping is sufficient.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class BatteryConfig:
    """Static nameplate parameters."""

    power_mw: float                      # Rated power (symmetric charge/discharge)
    energy_mwh: float                    # Rated energy capacity
    roundtrip_efficiency: float = 0.86   # η_charge * η_discharge
    soc_min: float = 0.05                # Hard lower bound (fraction)
    soc_max: float = 0.95                # Hard upper bound (fraction)
    daily_cycle_limit: float = 1.5       # Soft cap; risk officer enforces

    @property
    def one_way_efficiency(self) -> float:
        return self.roundtrip_efficiency ** 0.5


@dataclass
class BatteryState:
    """Mutable state. Updated after every dispatch interval."""

    soc: float                           # Current state of charge (fraction)
    cycles_today: float = 0.0
    cycles_total: float = 0.0
    last_updated: str | None = None      # ISO timestamp

    def to_dict(self) -> dict:
        return {
            "soc": self.soc,
            "cycles_today": self.cycles_today,
            "cycles_total": self.cycles_total,
            "last_updated": self.last_updated,
        }


@dataclass
class Battery:
    """Battery with config + current state. Operated via dispatch()."""

    config: BatteryConfig
    state: BatteryState = field(default_factory=lambda: BatteryState(soc=0.5))

    def dispatch(self, power_mw: float, duration_hours: float) -> float:
        """
        Apply a dispatch command for `duration_hours`.
        Positive power = discharge, negative = charge.
        Returns the energy delivered to / drawn from the grid (MWh).

        Clips to power and SoC limits; never raises.
        """
        # Clip to power rating
        power_mw = max(-self.config.power_mw, min(self.config.power_mw, power_mw))

        # Compute energy change in the battery (accounting for efficiency)
        if power_mw >= 0:
            # Discharge: battery loses more than grid gets
            energy_from_battery = power_mw * duration_hours / self.config.one_way_efficiency
            energy_to_grid = power_mw * duration_hours
        else:
            # Charge: grid delivers more than battery stores
            energy_from_battery = power_mw * duration_hours * self.config.one_way_efficiency
            energy_to_grid = power_mw * duration_hours  # negative

        # Apply SoC change, clip to bounds
        new_soc = self.state.soc - energy_from_battery / self.config.energy_mwh
        clipped_soc = max(self.config.soc_min, min(self.config.soc_max, new_soc))

        # Cycle accounting: half-cycle per throughput-equivalent discharge
        soc_delta = abs(self.state.soc - clipped_soc)
        self.state.cycles_today += soc_delta / 2
        self.state.cycles_total += soc_delta / 2

        self.state.soc = clipped_soc
        return energy_to_grid

    def reset_daily(self) -> None:
        self.state.cycles_today = 0.0
