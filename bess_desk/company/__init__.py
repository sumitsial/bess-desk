"""Orchestration primitives: tickets, agents, heartbeats, approvals."""

from bess_desk.company.agent import Agent, AgentConfig
from bess_desk.company.tickets import Ticket, TicketStore, TicketType

__all__ = ["Agent", "AgentConfig", "Ticket", "TicketStore", "TicketType"]
