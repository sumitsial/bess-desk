"""
Risk Officer. This is a hybrid agent by design:

  - The *checks* are deterministic code (SoC, cycles, VaR, concentration).
    They cannot be overridden by the LLM.
  - The *commentary* is LLM-written. The Risk Officer produces a
    human-readable assessment that accompanies the pass/flag/veto.

This matters: risk enforcement must be auditable and reproducible.
Letting an LLM veto trades would introduce nondeterminism at the worst
possible place in the pipeline.
"""

from __future__ import annotations

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType
from bess_desk.execution.risk import check_proposal


class RiskOfficerAgent(Agent):
    def act(self, context: HeartbeatContext) -> Ticket | None:
        # Find the most recent consolidated proposal awaiting assessment
        recent_consolidated = [
            t for t in context.recent_tickets
            if t.type == TicketType.CONSOLIDATED_PROPOSAL
        ]
        if not recent_consolidated:
            return None
        proposal = recent_consolidated[-1]

        # Deterministic checks
        result = check_proposal(proposal, context.battery_state)

        # TODO: LLM writes the human-readable commentary given the check result
        ticket = Ticket(
            type=TicketType.RISK_ASSESSMENT,
            author=self.id,
            inputs=[proposal.id],
            body={
                "decision": result.decision,           # "pass" | "flag" | "veto"
                "breaches": result.breaches,
                "suggested_modifications": result.suggested_modifications,
                "commentary": "STUB: LLM commentary here",
            },
            status=TicketStatus.PUBLISHED,
        )
        return ticket
