"""
Heartbeat scheduler. Wakes agents on their configured intervals and
passes them a `HeartbeatContext` assembled from the current world state.

Deliberately simple: one tick loop, synchronous execution, no parallelism.
Real trading desks run at human speeds (the DA gate is a daily event).
Microsecond concurrency is not the interesting problem here.
"""

from __future__ import annotations

from datetime import datetime

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStore, TicketStatus


class Scheduler:
    """Runs agents in priority order on each tick."""

    def __init__(self, tickets: TicketStore, agents: list[Agent]) -> None:
        self.tickets = tickets
        self.agents = agents

    def tick(
        self,
        now: datetime,
        battery_state: dict,
        market_state: dict,
        context_lookback_minutes: int = 24 * 60,
    ) -> list[Ticket]:
        """
        One scheduler tick. Runs all due agents, returns new tickets.
        """
        from datetime import timedelta

        since = now - timedelta(minutes=context_lookback_minutes)
        recent = self.tickets.query(since=since, status=TicketStatus.PUBLISHED)

        produced: list[Ticket] = []
        for agent in self.agents:
            if not agent.is_due(now):
                continue
            ctx = HeartbeatContext(
                now=now,
                recent_tickets=recent,
                battery_state=battery_state,
                market_state=market_state,
            )
            ticket = agent.tick(ctx)
            if ticket is not None:
                produced.append(ticket)
                # Fresh tickets become visible to agents that run later this tick
                recent.append(ticket)
        return produced
