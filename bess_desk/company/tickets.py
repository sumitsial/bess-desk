"""
Ticket system — the single source of truth for everything the desk does.

Every memo, forecast, proposal, approval, bid, and report is a ticket.
Tickets reference other tickets via `inputs`, forming a DAG that makes
the entire trading day replayable and auditable.

The design principle: if it's not in the ticket store, it didn't happen.
"""

from __future__ import annotations

from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any
from uuid import UUID, uuid4

from pydantic import BaseModel, Field


class TicketType(StrEnum):
    """The fixed taxonomy of ticket types. Add new types sparingly."""

    FORECAST_MEMO = "forecast_memo"           # Forecaster → DA/FCR price views
    NARRATIVE_MEMO = "narrative_memo"         # Analyst → fundamentals writeup
    DA_PROPOSAL = "da_proposal"               # DA Strategist → bid curve proposal
    FCR_PROPOSAL = "fcr_proposal"             # FCR Strategist → block proposal
    CONSOLIDATED_PROPOSAL = "consolidated"    # Head of Trading → reconciled
    RISK_ASSESSMENT = "risk_assessment"       # Risk Officer → pass/flag/veto
    APPROVAL = "approval"                     # Human → approve/reject/modify
    BID = "bid"                               # Execution → actual bid submitted
    FILL = "fill"                             # Market → clearing result
    PNL_REPORT = "pnl_report"                 # Reporter → daily/weekly P&L


class TicketStatus(StrEnum):
    DRAFT = "draft"
    PUBLISHED = "published"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXECUTED = "executed"
    FAILED = "failed"


class Ticket(BaseModel):
    """A single unit of desk activity. Immutable after publication."""

    id: UUID = Field(default_factory=uuid4)
    type: TicketType
    author: str                      # Agent ID or "human"
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    inputs: list[UUID] = Field(default_factory=list)   # Parent ticket IDs
    body: dict[str, Any]             # Type-specific content; validate per type
    status: TicketStatus = TicketStatus.DRAFT
    metadata: dict[str, Any] = Field(default_factory=dict)

    def publish(self) -> None:
        """Move from draft to published. Ticket becomes visible to the desk."""
        if self.status != TicketStatus.DRAFT:
            raise ValueError(f"Cannot publish ticket in status {self.status}")
        self.status = TicketStatus.PUBLISHED


class TicketStore:
    """
    Append-only ticket store backed by SQLite (or Postgres in prod).

    Stubbed here — the JSONL fallback is enough for a demo.
    """

    def __init__(self, path: Path | str = "audit/tickets.jsonl") -> None:
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self._cache: dict[UUID, Ticket] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            return
        with self.path.open() as f:
            for line in f:
                if line.strip():
                    t = Ticket.model_validate_json(line)
                    self._cache[t.id] = t

    def append(self, ticket: Ticket) -> Ticket:
        """Persist a ticket. Raises if ID already exists (tickets are immutable)."""
        if ticket.id in self._cache:
            raise ValueError(f"Ticket {ticket.id} already exists; tickets are immutable")
        with self.path.open("a") as f:
            f.write(ticket.model_dump_json() + "\n")
        self._cache[ticket.id] = ticket
        return ticket

    def get(self, ticket_id: UUID) -> Ticket | None:
        return self._cache.get(ticket_id)

    def query(
        self,
        *,
        type: TicketType | None = None,
        author: str | None = None,
        since: datetime | None = None,
        status: TicketStatus | None = None,
    ) -> list[Ticket]:
        """Filter tickets. No query language — just predicates."""
        results = list(self._cache.values())
        if type is not None:
            results = [t for t in results if t.type == type]
        if author is not None:
            results = [t for t in results if t.author == author]
        if since is not None:
            results = [t for t in results if t.created_at >= since]
        if status is not None:
            results = [t for t in results if t.status == status]
        return sorted(results, key=lambda t: t.created_at)

    def lineage(self, ticket_id: UUID) -> list[Ticket]:
        """Return the ticket plus all ancestors (recursive), in creation order."""
        seen: set[UUID] = set()
        result: list[Ticket] = []

        def walk(tid: UUID) -> None:
            if tid in seen:
                return
            seen.add(tid)
            t = self._cache.get(tid)
            if t is None:
                return
            for parent_id in t.inputs:
                walk(parent_id)
            result.append(t)

        walk(ticket_id)
        return result
