"""
DA Strategist. Reads forecast + narrative + battery state, proposes
a target DA position for tomorrow's 96 PTUs.

Important: the agent proposes *strategic intent* (charge hours, discharge
hours, aggressiveness). The actual bid curve is constructed by the
execution layer's bidder from this intent.
"""

from __future__ import annotations

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType


class DAStrategistAgent(Agent):
    def act(self, context: HeartbeatContext) -> Ticket | None:
        # TODO: read latest FORECAST_MEMO + NARRATIVE_MEMO, compose prompt,
        #       return DA_PROPOSAL with structured body:
        #         {
        #           "target_mw_per_ptu": [...96 floats...],
        #           "aggressiveness": "low" | "normal" | "high",
        #           "rationale": "...",
        #           "linked_forecast_id": UUID,
        #         }
        ticket = Ticket(
            type=TicketType.DA_PROPOSAL,
            author=self.id,
            body={"status": "STUB"},
            status=TicketStatus.PUBLISHED,
        )
        return ticket
