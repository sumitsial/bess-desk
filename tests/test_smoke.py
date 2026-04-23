"""Smoke tests — verify the scaffolding actually works."""

from __future__ import annotations

from pathlib import Path

import pytest

from bess_desk.company.tickets import Ticket, TicketStatus, TicketStore, TicketType


def test_ticket_store_append_and_query(tmp_path: Path) -> None:
    store = TicketStore(path=tmp_path / "tickets.jsonl")
    t = Ticket(
        type=TicketType.FORECAST_MEMO,
        author="forecaster-v1",
        body={"note": "hello"},
    )
    store.append(t)

    results = store.query(type=TicketType.FORECAST_MEMO)
    assert len(results) == 1
    assert results[0].id == t.id


def test_ticket_is_immutable(tmp_path: Path) -> None:
    store = TicketStore(path=tmp_path / "tickets.jsonl")
    t = Ticket(type=TicketType.FORECAST_MEMO, author="x", body={})
    store.append(t)
    with pytest.raises(ValueError, match="immutable"):
        store.append(t)


def test_ticket_lineage(tmp_path: Path) -> None:
    store = TicketStore(path=tmp_path / "tickets.jsonl")

    forecast = Ticket(type=TicketType.FORECAST_MEMO, author="f", body={})
    store.append(forecast)

    proposal = Ticket(
        type=TicketType.DA_PROPOSAL,
        author="s",
        inputs=[forecast.id],
        body={},
    )
    store.append(proposal)

    consolidated = Ticket(
        type=TicketType.CONSOLIDATED_PROPOSAL,
        author="h",
        inputs=[proposal.id],
        body={},
    )
    store.append(consolidated)

    lineage = store.lineage(consolidated.id)
    assert len(lineage) == 3
    assert lineage[0].id == forecast.id
    assert lineage[-1].id == consolidated.id


def test_ticket_publish_transitions() -> None:
    t = Ticket(type=TicketType.FORECAST_MEMO, author="x", body={})
    assert t.status == TicketStatus.DRAFT
    t.publish()
    assert t.status == TicketStatus.PUBLISHED
    with pytest.raises(ValueError):
        t.publish()


def test_battery_dispatch_respects_limits() -> None:
    from bess_desk.execution.battery import Battery, BatteryConfig, BatteryState

    battery = Battery(
        config=BatteryConfig(power_mw=10.0, energy_mwh=20.0),
        state=BatteryState(soc=0.5),
    )
    # Discharge at rated power for 1h; SoC should drop
    battery.dispatch(power_mw=10.0, duration_hours=1.0)
    assert battery.state.soc < 0.5
    assert battery.state.cycles_today > 0
