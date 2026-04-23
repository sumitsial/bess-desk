"""
CEO agent. Weekly heartbeat. Reviews P&L reports, adjusts risk appetite,
can propose mandate changes (subject to human approval).

This agent is mostly ceremonial in the demo — real CEO decisions happen
from the human-in-the-loop. But modeling it as an agent means weekly
strategic memos get the same audit-trail treatment as everything else.
"""

from __future__ import annotations

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType


class CEOAgent(Agent):
    def act(self, context: HeartbeatContext) -> Ticket | None:
        # TODO: read past week's PNL_REPORTS, write strategic memo
        return None
