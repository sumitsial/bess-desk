# bess-desk

**Open-source orchestration for a zero-human battery trading desk.**

[Quickstart](#quickstart) · [Docs](./docs) · [Architecture](./docs/ARCHITECTURE.md) · [Roadmap](./ROADMAP.md)

![License](https://img.shields.io/badge/license-MIT-blue)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![Status](https://img.shields.io/badge/status-alpha-orange)

---

> **⚠️ Paper trading only.** This repo is a demonstration of agent-orchestrated BESS trading. It does not connect to live markets and does not place real bids. Not financial advice.

---

## What is bess-desk?

**bess-desk is a Python framework that runs a battery trading desk as a team of AI agents.**

Assign roles. Set risk limits. Approve strategies. Monitor P&L.

It looks like a trading ops tool — but under the hood it has an org chart, a forecasting team, a risk officer with veto power, and a deterministic execution layer that turns agent recommendations into bid curves.

**Manage a trading desk, not a notebook.**

|    | Step | Example |
|----|------|---------|
| **01** | Define the mandate | *"Operate a 10 MW / 20 MWh BESS in the Netherlands. Stack DA arbitrage and FCR symmetric. Max 1.5 cycles/day."* |
| **02** | Hire the desk | Forecaster, Analyst, Strategist, Risk Officer, Reporter — any LLM, any provider. |
| **03** | Approve and run | Read the morning strategy memo. Approve or override. Watch the desk execute. |

---

## Why this is different

Most open-source BESS projects are **LP optimizers**. You feed them a price forecast, they give you a dispatch schedule.

Real trading desks don't work that way. They have **researchers** who read the news, **forecasters** who build views, **strategists** who propose allocations, **risk officers** who push back, and **reporters** who write up P&L. The LP is one tool in that workflow, not the whole workflow.

bess-desk models the whole workflow. LLMs do the parts LLMs are good at — reading, writing, reasoning under uncertainty. Deterministic code does the parts code is good at — solving LPs, enforcing SoC constraints, computing P&L.

---

## Architecture at a glance

```
┌──────────────────────────────────────────────────────────┐
│  AGENT LAYER  — LLM-powered research team                │
│  Forecaster · Analyst · Strategist · Risk · Reporter     │
│  Output: memos, forecasts, bid proposals (non-binding)   │
└──────────────────────────────────────────────────────────┘
                          ↓
                ┌─────────────────────┐
                │  HUMAN APPROVAL GATE │
                └─────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  EXECUTION LAYER  — deterministic, reproducible          │
│  Battery model · LP optimizer · Bid builder · Dispatcher │
│  Output: bid curves, dispatch schedule, P&L              │
└──────────────────────────────────────────────────────────┘
                          ↓
┌──────────────────────────────────────────────────────────┐
│  MARKET LAYER  — switchable                              │
│  Replay (historical) · Live feed · Simulation            │
└──────────────────────────────────────────────────────────┘
```

Full architecture in [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md).

---

## The org chart

Every agent has a role, a goal, a budget, and a boss.

| Role | Team | Heartbeat | What they do |
|------|------|-----------|--------------|
| **CEO** | C-suite | Weekly | Sets risk appetite, reviews P&L, approves mandate changes |
| **Head of Trading** | Desk | Daily | Resolves conflicts between DA and FCR allocations |
| **DA Strategist** | Desk | Daily (pre-gate) | Proposes DA position for next day's 96 PTUs |
| **FCR Strategist** | Desk | Daily (pre-gate) | Proposes FCR block participation |
| **Forecaster** | Research | Hourly | Publishes DA and imbalance price forecasts |
| **Fundamentals Analyst** | Research | 4×/day | Reads TTF, weather, outages, writes narrative memos |
| **Risk Officer** | Ops | Every proposal | Veto authority on SoC, cycle, VaR breaches |
| **Reporter** | Ops | Daily + weekly | Writes P&L reports and attribution |

Agents communicate through a **ticket system** with full audit trail. Every bid traces back to the memos that justified it.

---

## Problems bess-desk solves

| Without bess-desk | With bess-desk |
|---|---|
| ❌ You wire up an LP optimizer and a forecast model and call it a trading strategy. | ✅ A research team feeds the optimizer with forecasts, narratives, and revised strategies daily. |
| ❌ When the strategy loses money, you have no idea why — just that the LP returned a different schedule. | ✅ Every bid has a memo. Every memo has a forecast. Every forecast has inputs. Full attribution. |
| ❌ Co-optimizing DA and FCR requires a single monolithic LP that's painful to reason about. | ✅ Specialized agents propose their positions; a head-of-desk agent resolves conflicts under risk constraints. |
| ❌ Swapping from backtest to live to simulation means rewriting half the pipeline. | ✅ Market layer is a pluggable interface. Same agents, three modes. |
| ❌ Letting an LLM place trades feels reckless. Letting it do nothing feels like a waste. | ✅ LLMs write memos and propose. Deterministic code bids. Humans approve. Each layer does what it's best at. |

---

## What bess-desk is

- ✅ An **orchestration framework** for a multi-agent trading desk
- ✅ A **paper-trading sandbox** with three switchable market modes
- ✅ A **co-optimization engine** for DA + FCR symmetric revenue stacking
- ✅ A **Streamlit dashboard** for approvals, monitoring, and P&L attribution
- ✅ **Reproducible** — every run is replayable from the audit log

## What bess-desk is not

| | |
|---|---|
| **Not a live trading engine.** | No EPEX, TenneT, or Regelleistung execution. Paper trading only. |
| **Not a forecasting library.** | Bring your own forecast model. Simple baselines included. |
| **Not a market simulator.** | Simulation mode generates prices for testing, not realism. |
| **Not financial advice.** | This is a portfolio/research project. Do not trade real capital with it. |
| **Not a chatbot.** | Agents have jobs and tickets, not chat windows. |
| **Not an autonomous trader.** | Every bid goes through a human approval gate by default. |

---

## Market modes

bess-desk ships with three interchangeable market adapters. Swap them with a config flag.

| Mode | Use case | Data source |
|------|----------|-------------|
| **Replay** | Backtesting on historical data | Your CSV of EPEX DA + FCR prices |
| **Live** | Paper trading against real-time feeds | ENTSO-E, Regelleistung (read-only) |
| **Sim** | Stress-testing strategies | Synthetic AR + jump process |

---

## Quickstart

```bash
git clone https://github.com/<you>/bess-desk.git
cd bess-desk
uv sync                            # or: pip install -e .
cp .env.example .env               # add ANTHROPIC_API_KEY
bess-desk init --mandate nl-10mw   # scaffold a 10 MW desk
bess-desk run --mode replay --data data/nl_2026_q1.csv
bess-desk dashboard                # open http://localhost:8501
```

The dashboard shows:
- **Trading floor** — live agent activity and memos
- **Approvals** — pending strategy proposals awaiting your decision
- **P&L** — revenue by product (DA, FCR) with attribution
- **Audit log** — every memo, bid, and decision, replayable

**Requirements:** Python 3.11+, an Anthropic API key (or OpenAI — configurable), ~200MB for sample data.

---

## A typical day on the desk

```
06:00  Forecaster publishes DA price forecast for tomorrow
06:30  Analyst posts morning memo: "TTF spiked overnight on NS1 outage"
07:00  DA Strategist proposes bid curve for 96 PTUs
07:00  FCR Strategist proposes 6 blocks of symmetric capacity
07:15  Head of Trading resolves SoC conflict, routes to Risk Officer
07:20  Risk Officer flags: proposal exceeds 1.5 cycles/day — auto-downsizes
07:30  → HUMAN APPROVAL REQUIRED ←
       You review the memo stack, approve with one click
07:35  Execution layer builds bid curves, logs to audit ledger
12:00  DA gate closes — realized prices logged against forecast
22:00  Reporter publishes end-of-day P&L with attribution
```

Every line above is a ticket in the system. Every ticket is queryable. Every decision is reproducible.

---

## Why build this?

This is a portfolio project exploring two ideas:

1. **Agent orchestration belongs in quantitative workflows.** Trading desks already *are* multi-agent systems (of humans). Modeling them as software agents is a natural fit — especially for the research/analysis layer where context-heavy reasoning matters more than microsecond latency.

2. **LLMs shouldn't trade, but they should advise.** Deterministic execution + LLM research is the only architecture honest enough to ship as open source. This repo makes that separation a first-class design principle.

Built as a demonstration — not a product.

---

## Roadmap

- ✅ Multi-agent org with tickets and audit log
- ✅ DA + FCR symmetric co-optimization
- ✅ Replay / live / sim market modes
- ✅ Streamlit approval dashboard
- ⚪ aFRR up/down integration
- ⚪ Imbalance market (passive participation)
- ⚪ Multi-asset portfolio (N batteries)
- ⚪ Reinforcement learning strategist agent
- ⚪ Forecast model hub (bring your own model)
- ⚪ Multi-country (DE, BE) market adapters
- ⚪ Agent self-evaluation and strategy A/B testing

See [ROADMAP.md](./ROADMAP.md).

---

## Contributing

Issues and PRs welcome. See [CONTRIBUTING.md](./CONTRIBUTING.md). This is a research project, not a production system — expect breaking changes.

## License

MIT. See [LICENSE](./LICENSE).

## Acknowledgements

Architecture inspired by [Paperclip](https://github.com/paperclipai/paperclip)'s approach to agent orchestration. The domain translation (agents-running-a-business → agents-running-a-trading-desk) is the interesting bit.
