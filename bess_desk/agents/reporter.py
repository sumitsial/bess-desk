"""
Reporter. Writes daily and weekly P&L memos with attribution.

Input: fills from the market adapter, bids from the execution layer.
Output: a PNL_REPORT ticket with structured revenue breakdown plus
an LLM-written narrative.
"""

from __future__ import annotations

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType


class ReporterAgent(Agent):
    def act(self, context: HeartbeatContext) -> Ticket | None:
        # TODO:
        #   - Aggregate FILL tickets for the period
        #   - Compute P&L by product (DA, FCR, degradation cost)
        #   - LLM writes narrative: what went well, what didn't, attribution
        ticket = Ticket(
            type=TicketType.PNL_REPORT,
            author=self.id,
            body={
                "period": "STUB",
                "revenue_by_product": {},
                "narrative": "STUB",
            },
            status=TicketStatus.PUBLISHED,
        )
        return ticket
