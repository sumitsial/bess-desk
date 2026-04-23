"""The research team — LLM-powered agents that produce memos and proposals.

Agents are imported lazily via their modules to avoid pulling in heavy
deps (anthropic, openai) when someone only wants the ticket system.
"""

# Intentionally empty. Import agents directly, e.g.:
#   from bess_desk.agents.forecaster import ForecasterAgent
