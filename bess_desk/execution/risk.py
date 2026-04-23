"""
Risk checks. Deterministic, enforceable in code, never overridden by LLMs.

Four categories:
  - SoC feasibility (is the trajectory reachable given physics?)
  - Cycle budget (does the proposal fit the daily/monthly limit?)
  - Concentration (any single PTU / product too exposed?)
  - VaR (parametric, against forecast distribution)

Each returns a list of breaches. A proposal with any breach gets "flag";
with a critical breach gets "veto". The Risk Officer agent adds commentary
but cannot change the decision.
"""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass
class RiskCheckResult:
    decision: str                    # "pass" | "flag" | "veto"
    breaches: list[dict] = field(default_factory=list)
    suggested_modifications: dict = field(default_factory=dict)


def check_proposal(proposal, battery_state: dict) -> RiskCheckResult:
    """
    TODO:
      - soc_feasibility_check(proposal, battery_state)
      - cycle_budget_check(proposal, battery_state)
      - concentration_check(proposal)
      - var_check(proposal, forecast_distribution)

    Each returns a list of Breach objects. If any critical → veto;
    any non-critical → flag; none → pass.
    """
    return RiskCheckResult(decision="pass")
