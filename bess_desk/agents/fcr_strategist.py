"""
FCR Strategist. Proposes FCR symmetric block participation for tomorrow.

NL FCR is 4-hour blocks (6 per day). Proposal is per-block: reserved
capacity in MW and whether to participate at all.
"""

from __future__ import annotations

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType


class FCRStrategistAgent(Agent):
    def act(self, context: HeartbeatContext) -> Ticket | None:
        # TODO: full implementation
        #   - Read FCR capacity price history (past N days)
        #   - Read forecast memo (DA spread matters — if DA spread is wide,
        #     opportunity cost of FCR reservation is high)
        #   - Propose MW per block for 6 blocks
        ticket = Ticket(
            type=TicketType.FCR_PROPOSAL,
            author=self.id,
            body={
                "blocks": [
                    {"block": i, "mw_reserved": 0, "participate": False}
                    for i in range(6)
                ],
                "rationale": "STUB",
            },
            status=TicketStatus.PUBLISHED,
        )
        return ticket
