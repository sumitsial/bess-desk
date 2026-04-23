"""
Head of Trading. Reads DA and FCR proposals, resolves SoC conflicts,
produces a consolidated proposal. Pure coordination logic — much of this
could be deterministic, but the LLM is useful for writing the human-
readable rationale that accompanies the numbers.
"""

from __future__ import annotations

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType


class HeadOfTradingAgent(Agent):
    def act(self, context: HeartbeatContext) -> Ticket | None:
        # TODO:
        #   - Fetch latest DA_PROPOSAL and FCR_PROPOSAL
        #   - Check for conflicts (deterministic SoC feasibility check)
        #   - If conflict: LLM picks which to downsize + writes rationale
        #   - Emit CONSOLIDATED_PROPOSAL
        ticket = Ticket(
            type=TicketType.CONSOLIDATED_PROPOSAL,
            author=self.id,
            body={"status": "STUB"},
            status=TicketStatus.PUBLISHED,
        )
        return ticket
