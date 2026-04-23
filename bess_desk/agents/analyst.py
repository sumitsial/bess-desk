"""
Fundamentals Analyst. Reads market context (TTF, weather, outages) and
writes narrative memos the Forecaster and Strategists use as input.

In replay mode, "news" is stubbed from the data bundle. In live mode,
this agent polls external APIs (TTF prices, weather, ENTSO-E outage data).
"""

from __future__ import annotations

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType


class AnalystAgent(Agent):
    def act(self, context: HeartbeatContext) -> Ticket | None:
        # TODO: implement full version
        #   - Pull TTF gas price + delta vs. yesterday
        #   - Pull weather forecast (wind/solar outlook NL)
        #   - Pull planned outages from ENTSO-E (replay: from bundle)
        #   - LLM prompt: "given these inputs, what's the narrative?"
        #   - Return NARRATIVE_MEMO ticket
        ticket = Ticket(
            type=TicketType.NARRATIVE_MEMO,
            author=self.id,
            body={
                "summary": "STUB: implement analyst agent",
                "ttf_close": None,
                "wind_outlook": None,
                "outages": [],
            },
            status=TicketStatus.PUBLISHED,
        )
        return ticket
