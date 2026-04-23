# Roadmap

Status legend: ✅ done · 🟡 in progress · ⚪ planned · 💭 idea

## v0.1 — Skeleton (current)

- ✅ Ticket system with JSONL persistence and lineage queries
- ✅ Base `Agent` class with heartbeat pattern
- ✅ Scheduler tick loop
- ✅ Human approval gate
- ✅ Battery physics model (SoC, efficiency, cycles)
- ✅ Market adapter interface
- ✅ LLM client wrapper with mock mode
- ✅ CLI scaffold
- ✅ Smoke tests

## v0.2 — Minimum viable desk

- 🟡 Forecaster agent — proper Anthropic tool-use call
- ⚪ Analyst agent — TTF + weather + outages → narrative memo
- ⚪ DA Strategist — reads forecast, proposes bid intent
- ⚪ FCR Strategist — reads FCR history, proposes blocks
- ⚪ Head of Trading — SoC conflict resolution
- ⚪ Risk Officer — deterministic checks + LLM commentary
- ⚪ Reporter — daily P&L with attribution
- ⚪ Replay adapter — full CSV reader with PTU/block clock
- ⚪ LP optimizer — cvxpy implementation of DA + FCR co-opt
- ⚪ End-to-end example on NL Q1 2026 data

## v0.3 — Dashboard & demo polish

- ⚪ Streamlit: trading floor page (live agent activity)
- ⚪ Streamlit: approvals page (proposal review + memo stack)
- ⚪ Streamlit: P&L page (revenue attribution chart)
- ⚪ Streamlit: audit log page (ticket DAG viewer)
- ⚪ 30-second demo GIF for README
- ⚪ Dockerfile + docker-compose

## v0.4 — Live paper trading

- ⚪ Live adapter: ENTSO-E DA prices
- ⚪ Live adapter: Regelleistung FCR results
- ⚪ Live adapter: TTF spot from an open source
- ⚪ Paper order book (bids never leave the machine)

## v0.5+ — Stretch

- ⚪ aFRR up/down integration
- ⚪ Imbalance market passive participation
- ⚪ Multi-asset portfolio (N batteries)
- ⚪ Forecast model hub (plug in your own)
- ⚪ Strategy A/B testing with agent self-evaluation
- 💭 RL strategist agent that proposes policies evaluated in replay
- 💭 Multi-country adapter (DE, BE)
- 💭 Retail battery aggregation mode
