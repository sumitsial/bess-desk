"""
Forecaster agent. Publishes DA price forecasts for the next 96 PTUs.

This is the canonical agent implementation — every other agent follows
the same pattern:
  1. Read relevant recent tickets + world state from context
  2. Build an LLM prompt with structured output schema
  3. Call the LLM, parse the result
  4. Return a Ticket

The interesting design choice: the LLM does NOT produce numeric price
forecasts directly. It picks a forecasting *strategy* (persistence,
seasonal-naive, or a note like "volatility elevated, widen intervals")
and deterministic code computes the numbers. This keeps the forecast
reproducible while letting the LLM reason about regime.
"""

from __future__ import annotations

from datetime import timedelta

from bess_desk.company.agent import Agent, HeartbeatContext
from bess_desk.company.tickets import Ticket, TicketStatus, TicketType
from bess_desk.llm.client import LLMClient


class ForecasterAgent(Agent):
    """Publishes DA price forecasts on each heartbeat."""

    def __init__(self, config, tickets, llm: LLMClient) -> None:
        super().__init__(config, tickets)
        self.llm = llm

    def act(self, context: HeartbeatContext) -> Ticket | None:
        # 1. Gather inputs: recent DA history, any relevant narrative memos
        narrative_memos = [
            t for t in context.recent_tickets if t.type == TicketType.NARRATIVE_MEMO
        ]
        da_history = context.market_state.get("da_history_7d", [])

        # 2. Ask the LLM to characterize the regime (not to produce numbers)
        regime_prompt = self._build_regime_prompt(da_history, narrative_memos)
        regime = self.llm.structured_call(
            prompt=regime_prompt,
            schema=_REGIME_SCHEMA,
            model=self.config.model,
        )
        self._charge_tokens(regime.get("_usage", {}).get("total_tokens", 0))

        # 3. Deterministic forecast computation (TODO: implement properly)
        forecast = self._compute_forecast(
            da_history,
            strategy=regime["strategy"],
            volatility_regime=regime["volatility_regime"],
        )

        # 4. Publish the memo as a ticket
        ticket = Ticket(
            type=TicketType.FORECAST_MEMO,
            author=self.id,
            inputs=[t.id for t in narrative_memos],
            body={
                "horizon_hours": 24,
                "ptu_forecasts": forecast,       # list of 96 dicts: {ts, p50, p10, p90}
                "regime_note": regime["note"],
                "strategy_used": regime["strategy"],
            },
            status=TicketStatus.PUBLISHED,
        )
        return ticket

    def _build_regime_prompt(
        self, da_history: list[dict], narrative_memos: list[Ticket]
    ) -> str:
        # TODO: proper prompt engineering; this is the skeleton
        narratives = "\n\n".join(
            f"[{m.created_at.isoformat()}] {m.body.get('summary', '')}"
            for m in narrative_memos[-3:]
        )
        return (
            "You are a power market forecaster. Based on the recent DA price history "
            "and the analyst memos below, characterize the current regime.\n\n"
            f"Recent DA history (last 7 days, hourly): {da_history[-24:]}\n\n"
            f"Recent narrative memos:\n{narratives}\n\n"
            "Return: forecasting strategy (persistence | seasonal_naive | "
            "seasonal_with_weather), volatility regime (low | normal | elevated), "
            "and a 1-2 sentence regime note explaining your choice."
        )

    def _compute_forecast(
        self, da_history: list[dict], strategy: str, volatility_regime: str
    ) -> list[dict]:
        """
        Deterministic forecast. Takes LLM-chosen strategy, produces numbers.

        TODO: implement persistence, seasonal-naive, and seasonal-with-weather.
        Current stub returns flat forecast at last-known price.
        """
        if not da_history:
            return []
        last_price = da_history[-1].get("price", 50.0)
        # Widen intervals when LLM flags elevated volatility
        spread = {"low": 10.0, "normal": 25.0, "elevated": 60.0}[volatility_regime]
        return [
            {
                "ptu_index": i,
                "p50": last_price,
                "p10": last_price - spread,
                "p90": last_price + spread,
            }
            for i in range(96)
        ]


# JSON schema for the LLM's structured output
_REGIME_SCHEMA = {
    "type": "object",
    "properties": {
        "strategy": {
            "type": "string",
            "enum": ["persistence", "seasonal_naive", "seasonal_with_weather"],
        },
        "volatility_regime": {
            "type": "string",
            "enum": ["low", "normal", "elevated"],
        },
        "note": {"type": "string", "maxLength": 400},
    },
    "required": ["strategy", "volatility_regime", "note"],
}
