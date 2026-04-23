"""
DA + FCR co-optimization LP.

Formulation (high level):

  Decision variables (per PTU t ∈ 1..96):
    p_ch[t], p_dis[t] ≥ 0    # DA charge / discharge (MW)
    f[b] ≥ 0                 # FCR capacity reserved per 4h block b
    soc[t]                   # state of charge (MWh)

  Objective:
    maximize  Σ_t price_da[t] * (p_dis[t] - p_ch[t]) * Δt
            + Σ_b price_fcr[b] * f[b] * 4h
            - degradation_cost * Σ_t (p_ch[t] + p_dis[t]) * Δt

  Constraints:
    soc[t] = soc[t-1] + η * p_ch[t] * Δt − (1/η) * p_dis[t] * Δt
    soc[t] ∈ [E_min + headroom(f[b(t)]), E_max − headroom(f[b(t)])]
    p_ch[t] + p_dis[t] + f[b(t)] ≤ P_max
    Σ_t (p_ch[t] + p_dis[t]) * Δt / (2E) ≤ cycle_limit

The FCR headroom on SoC is the interesting modeling choice: reserving
F MW of symmetric FCR for a 4h block means we must keep F*4h of both
charge and discharge headroom in SoC during that block.

Solver: cvxpy with HiGHS. Free, fast, LP is small (~500 vars for a day).

Stubbed — real implementation next.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np

from bess_desk.execution.battery import BatteryConfig, BatteryState


@dataclass
class OptimizationResult:
    p_charge: np.ndarray         # Shape (96,)
    p_discharge: np.ndarray      # Shape (96,)
    fcr_reserved: np.ndarray     # Shape (6,) — one per 4h block
    soc_trajectory: np.ndarray   # Shape (97,) — 96 PTUs + start
    expected_revenue: float
    solve_status: str


def optimize_day(
    da_prices: np.ndarray,           # Shape (96,) €/MWh
    fcr_prices: np.ndarray,          # Shape (6,) €/MW/4h
    battery_config: BatteryConfig,
    initial_state: BatteryState,
    cycle_budget: float | None = None,
    degradation_cost_per_mwh: float = 0.0,
) -> OptimizationResult:
    """
    Solve the DA+FCR co-optimization for one day.

    TODO: full cvxpy implementation. Signature is final — body is stubbed.
    """
    # Stub return so downstream code can be wired up before the LP is ready
    return OptimizationResult(
        p_charge=np.zeros(96),
        p_discharge=np.zeros(96),
        fcr_reserved=np.zeros(6),
        soc_trajectory=np.full(97, initial_state.soc) * battery_config.energy_mwh,
        expected_revenue=0.0,
        solve_status="stub",
    )
