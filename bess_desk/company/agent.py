"""
Base Agent class. All LLM-powered agents inherit from this.

The heartbeat pattern: agents don't loop. They wake on a schedule,
read context (tickets from other agents), produce output (a new ticket),
and sleep. No continuous execution, no race conditions.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone

from bess_desk.company.tickets import Ticket, TicketStore


@dataclass
class AgentConfig:
    """Configuration for a single agent."""

    id: str                              # Unique ID, e.g. "forecaster-v1"
    role: str                            # Human-readable role, e.g. "Price Forecaster"
    goal: str                            # What success looks like for this agent
    heartbeat: timedelta                 # How often it wakes
    boss: str | None = None              # ID of the agent that reviews its output
    monthly_token_budget: int = 1_000_000  # Hard cap; paused when hit
    model: str = "claude-sonnet-4-5"     # LLM model to use
    skills: list[str] = field(default_factory=list)  # Paths to skill files


@dataclass
class HeartbeatContext:
    """Everything an agent needs to know when it wakes up."""

    now: datetime
    recent_tickets: list[Ticket]         # Published tickets the agent should read
    battery_state: dict                  # SoC, cycles-today, etc. (stub for now)
    market_state: dict                   # Current prices, upcoming gates


class Agent(ABC):
    """
    Base class for all LLM-powered agents.

    Subclasses implement `act()` — the logic that runs on each heartbeat.
    The base class handles: fetching context, tracking budget, writing the
    resulting ticket to the store.
    """

    def __init__(self, config: AgentConfig, tickets: TicketStore) -> None:
        self.config = config
        self.tickets = tickets
        self._tokens_used_this_month = 0
        self._last_heartbeat: datetime | None = None

    @property
    def id(self) -> str:
        return self.config.id

    def is_due(self, now: datetime) -> bool:
        """Should this agent run at `now`?"""
        if self._last_heartbeat is None:
            return True
        return (now - self._last_heartbeat) >= self.config.heartbeat

    def is_paused(self) -> bool:
        """Has this agent hit its budget?"""
        return self._tokens_used_this_month >= self.config.monthly_token_budget

    def tick(self, context: HeartbeatContext) -> Ticket | None:
        """
        Run one heartbeat. Returns the ticket produced (if any).

        Framework method — do not override. Override `act()` instead.
        """
        if self.is_paused():
            return None
        ticket = self.act(context)
        if ticket is not None:
            self.tickets.append(ticket)
        self._last_heartbeat = context.now
        return ticket

    @abstractmethod
    def act(self, context: HeartbeatContext) -> Ticket | None:
        """
        The agent's core logic. Implemented by subclasses.

        Read context, decide what to do, build a ticket, return it.
        Return None if there's nothing meaningful to say this heartbeat.
        """
        ...

    def _charge_tokens(self, n: int) -> None:
        """Subclasses call this after each LLM call to track budget."""
        self._tokens_used_this_month += n


# Convenience constructor for cases where we want to register an agent
# declaratively (e.g. from a YAML config in the future)
def now_utc() -> datetime:
    return datetime.now(timezone.utc)
