"""
Human approval gate. The bottleneck between agent proposals and execution.

By default, no consolidated proposal reaches the execution layer without
a human clicking approve. An `auto_approve` mode exists for backtests but
is clearly marked in the audit log.
"""

from __future__ import annotations

import os
from uuid import UUID

from bess_desk.company.tickets import Ticket, TicketStore, TicketStatus, TicketType


class ApprovalGate:
    """Gatekeeper between consolidated proposals and execution."""

    def __init__(self, tickets: TicketStore, auto_approve: bool | None = None) -> None:
        self.tickets = tickets
        if auto_approve is None:
            auto_approve = os.getenv("BESS_DESK_AUTO_APPROVE", "false").lower() == "true"
        self.auto_approve = auto_approve

    def pending(self) -> list[Ticket]:
        """Consolidated proposals that have a risk assessment but no approval."""
        proposals = self.tickets.query(
            type=TicketType.CONSOLIDATED_PROPOSAL, status=TicketStatus.PUBLISHED
        )
        approvals = self.tickets.query(type=TicketType.APPROVAL)
        approved_parents = {pid for a in approvals for pid in a.inputs}
        return [p for p in proposals if p.id not in approved_parents]

    def approve(
        self,
        proposal_id: UUID,
        approver: str = "human",
        notes: str = "",
        modifications: dict | None = None,
    ) -> Ticket:
        """Record an approval. Returns the approval ticket."""
        proposal = self.tickets.get(proposal_id)
        if proposal is None:
            raise ValueError(f"Proposal {proposal_id} not found")
        if proposal.type != TicketType.CONSOLIDATED_PROPOSAL:
            raise ValueError(f"Can only approve consolidated proposals, got {proposal.type}")

        ticket = Ticket(
            type=TicketType.APPROVAL,
            author=approver,
            inputs=[proposal_id],
            body={
                "decision": "approved",
                "notes": notes,
                "modifications": modifications or {},
                "auto_approved": approver == "auto",
            },
            status=TicketStatus.PUBLISHED,
        )
        return self.tickets.append(ticket)

    def reject(self, proposal_id: UUID, reason: str, approver: str = "human") -> Ticket:
        """Reject a proposal. Execution layer must not act on it."""
        proposal = self.tickets.get(proposal_id)
        if proposal is None:
            raise ValueError(f"Proposal {proposal_id} not found")

        ticket = Ticket(
            type=TicketType.APPROVAL,
            author=approver,
            inputs=[proposal_id],
            body={"decision": "rejected", "reason": reason},
            status=TicketStatus.PUBLISHED,
        )
        return self.tickets.append(ticket)

    def auto_approve_if_enabled(self, proposal_id: UUID) -> Ticket | None:
        """Called by the scheduler when auto_approve mode is on."""
        if not self.auto_approve:
            return None
        return self.approve(
            proposal_id,
            approver="auto",
            notes="AUTO-APPROVED (backtest mode)",
        )
