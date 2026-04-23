"""
Minimal end-to-end demo: one forecaster agent ticks once with mocked LLM.

Run:
    python examples/00_hello_desk.py

Should produce a ticket, print it, and save it to audit/tickets.jsonl.
No API keys required (uses LLM mock mode).
"""

from __future__ import annotations

import os
from datetime import timedelta
from pathlib import Path

# Force mock mode before importing the LLM client
os.environ["BESS_DESK_LLM_MOCK"] = "true"

from bess_desk.agents.forecaster import ForecasterAgent  # noqa: E402
from bess_desk.company.agent import AgentConfig, HeartbeatContext, now_utc  # noqa: E402
from bess_desk.company.tickets import TicketStore  # noqa: E402
from bess_desk.llm.client import LLMClient  # noqa: E402


def main() -> None:
    # Use a local audit dir for this example
    audit_path = Path(__file__).parent.parent / "audit" / "hello_desk.jsonl"
    audit_path.parent.mkdir(exist_ok=True)
    if audit_path.exists():
        audit_path.unlink()  # fresh start each run

    tickets = TicketStore(path=audit_path)
    llm = LLMClient(mock=True)

    config = AgentConfig(
        id="forecaster-v1",
        role="DA Price Forecaster",
        goal="Publish a DA forecast each hour",
        heartbeat=timedelta(hours=1),
    )
    agent = ForecasterAgent(config, tickets, llm)

    # Build a minimal context
    ctx = HeartbeatContext(
        now=now_utc(),
        recent_tickets=[],
        battery_state={"soc": 0.5, "cycles_today": 0.0},
        market_state={
            "da_history_7d": [
                {"ts": f"2026-04-{d:02d}T12:00", "price": 55.0 + d}
                for d in range(1, 8)
            ]
        },
    )

    print(f"Agent {agent.id} ticking...")
    ticket = agent.tick(ctx)

    if ticket is None:
        print("No ticket produced.")
        return

    print(f"\n✓ Ticket produced: {ticket.type}")
    print(f"  ID:          {ticket.id}")
    print(f"  Author:      {ticket.author}")
    print(f"  Created at:  {ticket.created_at}")
    print(f"  Status:      {ticket.status}")
    print(f"  Strategy:    {ticket.body.get('strategy_used')}")
    print(f"  Regime:      {ticket.body.get('regime_note')}")
    print(f"  Forecasts:   {len(ticket.body.get('ptu_forecasts', []))} PTUs")
    print(f"\nFull ticket saved to: {audit_path}")


if __name__ == "__main__":
    main()
