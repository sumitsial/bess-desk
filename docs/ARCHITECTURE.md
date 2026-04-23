# Architecture

This document explains how bess-desk is organized, what decisions were made and why, and where the boundaries are.

## Design principles

Four principles drive every decision in this repo.

**1. LLMs advise, code executes.** Research, forecasting narrative, strategy proposals, and reporting are LLM work. Bid construction, LP solving, SoC enforcement, and P&L accounting are deterministic code. The boundary is strict: no LLM output ever bypasses the execution layer.

**2. Every decision is auditable.** A bid that was placed must trace back through the proposal that generated it, the memos that informed that proposal, the forecasts those memos referenced, and the raw inputs those forecasts consumed. The audit log is append-only and the system must be replayable from it.

**3. Humans approve strategy; code enforces risk.** Strategy changes (new allocations, new risk limits, new market participation) flow through a human approval gate. Risk limits (SoC bounds, cycle budgets, VaR caps) are enforced in code and cannot be overridden by LLM agents.

**4. Market adapters are pluggable.** Replay, live, and sim modes expose the same interface. A strategy that works in replay should run unchanged against live data (and vice versa). No conditional logic for "are we backtesting or not" anywhere outside the market layer.

---

## Three-layer architecture

### Layer 1: Agents (LLM-powered)

Agents produce **memos and proposals**. Never bids. Never dispatch commands.

A memo is a structured object — markdown body + typed metadata (confidence, horizon, inputs referenced). A proposal is a memo plus a structured recommendation the execution layer knows how to interpret (e.g., "target DA position = +5 MW for PTUs 72–80, rationale = morning peak + low wind forecast").

Agents run on **heartbeats** — scheduled wakeups that check for new context, produce output, and go back to sleep. They do not run continuously and do not loop. This is deliberate: continuous loops burn tokens and create race conditions; heartbeats make the system debuggable.

Each agent has:
- A **role** (what it does)
- A **goal** (what success looks like for it)
- A **heartbeat schedule** (when it wakes)
- A **budget** (monthly token cap; hitting it pauses the agent)
- A **boss** (who reviews its output)
- A **skills package** (domain knowledge injected at runtime)

### Layer 2: Execution (deterministic)

Execution takes approved proposals and turns them into bids, dispatch, and P&L. Zero LLM calls here.

Core modules:
- `battery.py` — SoC dynamics, round-trip efficiency, C-rate, degradation accounting
- `optimizer.py` — cvxpy LP that co-optimizes DA + FCR under battery and risk constraints
- `bidder.py` — converts LP output into EPEX-shaped bid curves (96 PTUs × price-quantity pairs)
- `dispatcher.py` — real-time SoC management once the gate closes
- `pnl.py` — revenue attribution by product (DA, FCR, degradation cost, opportunity cost)

The LP is the heart of the execution layer. It sees battery state, price forecasts (from agents), risk limits (from config), and market structure (from the market adapter). It does not see memos or narrative — only numbers.

### Layer 3: Markets (pluggable)

Three adapters implement the same `MarketAdapter` interface:

- **Replay** — reads historical CSVs (your existing NL 2026 Q1 data), advances a simulated clock, serves prices in order
- **Live** — polls ENTSO-E for DA prices and Regelleistung for FCR results; read-only, never places orders
- **Sim** — generates synthetic prices with configurable volatility, jumps, and seasonality

The interface exposes `get_da_forecast_window()`, `get_fcr_block_prices()`, `advance_clock()`, `log_bid()` (to a simulated order book, never a real one), and `realize_pnl()`. Whatever's behind the interface is an implementation detail.

---

## How a trade happens

Worked example — a single day of operation in replay mode:

1. **05:00** — Market adapter advances clock to the DA gate window. Fires event.
2. **06:00** — Forecaster heartbeat. Agent reads last 7 days of DA prices, current weather forecast, TTF close. Publishes `forecast_memo` with 96 PTU price estimates + confidence intervals.
3. **06:30** — Analyst heartbeat. Reads news feed (stubbed in replay mode), writes `narrative_memo`. E.g., "Cold snap + low wind forecast → expect evening peak >€200/MWh."
4. **07:00** — DA Strategist heartbeat. Reads both memos + current battery state. Proposes a bid curve as a `da_proposal` object.
5. **07:00** — FCR Strategist heartbeat. Independently proposes FCR block participation as `fcr_proposal`.
6. **07:10** — Head of Trading heartbeat. Reads both proposals, checks for SoC conflicts (e.g., DA wants to be empty at 18:00 but FCR needs ±5 MW headroom). Produces `consolidated_proposal`.
7. **07:15** — Risk Officer heartbeat. Runs the consolidated proposal through deterministic risk checks (cycle budget, VaR, concentration). Can veto, downsize, or pass through. Produces `risk_approved_proposal`.
8. **07:20** — Human approval gate. Dashboard shows the proposal + full memo stack. Human approves, rejects, or modifies.
9. **07:30** — Execution layer takes the approved proposal. LP solver produces optimal bid curves given the strategic target. Bid curves logged to audit ledger.
10. **12:00** — DA gate closes in the market adapter. Realized clearing prices logged. Dispatch schedule fixed.
11. **Throughout day** — Dispatcher manages intraday SoC, responds to FCR activations (simulated).
12. **22:00** — Reporter heartbeat. Computes P&L. Writes attribution memo: "€X from DA arbitrage, €Y from FCR capacity, €Z degradation cost."

Every step produces a ticket. Every ticket is linked to the ticket(s) that produced its inputs. The audit log is the ground truth.

---

## The ticket system

Borrowed directly from Paperclip's model.

A ticket has:
- `id` — UUID
- `type` — `memo | proposal | bid | approval | report`
- `author` — agent ID or `human`
- `created_at` — timestamp
- `inputs` — list of ticket IDs this one references
- `body` — structured content (schema depends on type)
- `status` — `draft | published | approved | rejected | executed`

Everything in the system is a ticket. Forecasts are tickets. Approvals are tickets. Bids are tickets. This uniformity is what makes replay possible — to re-run a day, you replay the ticket stream.

---

## The approval gate

This is the most important design decision.

By default, **nothing that moves money (even paper money) passes without human approval.** The gate can be relaxed for autonomous backtest runs (`--auto-approve`) but that mode is clearly marked in outputs and audit logs.

What the human sees at the gate:
1. The consolidated proposal (what the desk wants to do)
2. The memo stack (why the desk wants to do it)
3. The risk assessment (what could go wrong)
4. A single-page P&L projection (best / expected / worst case from the LP)
5. Three buttons: approve, reject, modify

Modify opens a simple editor over the proposal JSON. The modified version re-enters the risk check before execution.

---

## Risk enforcement

Risk is enforced in **code**, not by an agent. The Risk Officer agent can comment, flag, and recommend — but the actual constraints live in `execution/risk.py` as deterministic checks:

- **SoC bounds** — hard [5%, 95%] unless configured otherwise
- **Cycle budget** — configurable daily/monthly limit; hitting it disables further discharging commitments
- **Power limits** — C-rate enforcement
- **Concentration** — max % of revenue from single product type per day
- **VaR cap** — parametric VaR against proposal P&L distribution

If a proposal fails any of these, the execution layer refuses it. No agent — not even the CEO agent — can override.

---

## The market adapter interface

```python
class MarketAdapter(Protocol):
    def now(self) -> datetime: ...
    def advance_to(self, ts: datetime) -> list[MarketEvent]: ...
    def get_da_history(self, lookback: timedelta) -> pd.DataFrame: ...
    def get_fcr_history(self, lookback: timedelta) -> pd.DataFrame: ...
    def submit_bid(self, bid: BidCurve) -> BidReceipt: ...
    def get_clearings(self, for_date: date) -> pd.DataFrame: ...
```

Three implementations:

- `ReplayAdapter(csv_path, start_date, end_date)` — advances a virtual clock through historical data
- `LiveAdapter(entsoe_token, regelleistung_token)` — polls real APIs, logs bids to a local sandbox
- `SimAdapter(seed, volatility, jump_intensity)` — synthetic prices for stress testing

---

## Why Anthropic Claude as the default LLM

Three reasons:

1. **Structured outputs via tool use** — proposals must match a schema. Claude's tool-calling is robust for this.
2. **Long context** — the agents pass memos to each other; the context window grows through the day. Claude 200K handles a full trading day of memos without truncation.
3. **Cost control** — Claude's per-token pricing plus deterministic heartbeats (not continuous loops) makes monthly budgets predictable.

The LLM client is wrapped behind an interface. Swapping to OpenAI, local Llama, or any other provider is a config change.

---

## What's intentionally missing

To keep the project focused and the demo clean, these are **out of scope**:

- **Real market execution.** No broker integrations, no order book connectivity. A live execution adapter is a different project with legal and operational requirements this repo will not meet.
- **Intraday continuous trading.** The demo focuses on DA + FCR. Intraday is a microstructure problem agents are poorly suited for.
- **Price forecasting models.** A simple persistence forecaster is included for completeness. Replacing it with a real model is left as an exercise (and documented in the Forecaster agent's skills package).
- **Portfolio optimization across multiple assets.** Single battery only for v1. Multi-asset is on the roadmap.
- **UI beyond Streamlit.** A React/Next dashboard would be nicer; Streamlit is sufficient for a demo and keeps the repo Python-only.

---

## Where to start reading the code

For the impatient:

1. `bess_desk/company/agent.py` — base Agent class, understand the heartbeat model
2. `bess_desk/agents/forecaster.py` — simplest agent, end-to-end example
3. `bess_desk/execution/optimizer.py` — the LP, where the actual trading logic lives
4. `bess_desk/markets/replay.py` — the market adapter pattern in its simplest form
5. `examples/01_replay_q1_2026.py` — full end-to-end run on historical data

If you want to understand the philosophy before the code, read `docs/DESIGN_DECISIONS.md` (coming soon).
