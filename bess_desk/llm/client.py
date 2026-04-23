"""
LLM client wrapper.

One interface, pluggable providers. Agents call `structured_call()` with a
JSON schema and get back a parsed dict. Provider-specific quirks (Anthropic
tool use vs. OpenAI function calling) are hidden here.

Stubbed — real implementation calls the providers. The mock mode lets the
rest of the system run end-to-end without API keys during development.
"""

from __future__ import annotations

import json
import os
from typing import Any


class LLMClient:
    """Unified LLM client over Anthropic / OpenAI / mock."""

    def __init__(
        self,
        provider: str | None = None,
        model: str | None = None,
        mock: bool = False,
    ) -> None:
        self.provider = provider or os.getenv("BESS_DESK_LLM_PROVIDER", "anthropic")
        self.model = model or os.getenv("BESS_DESK_LLM_MODEL", "claude-sonnet-4-5")
        self.mock = mock or os.getenv("BESS_DESK_LLM_MOCK", "false").lower() == "true"
        self._client = None
        if not self.mock:
            self._client = self._init_client()

    def _init_client(self) -> Any:
        if self.provider == "anthropic":
            from anthropic import Anthropic
            return Anthropic()
        elif self.provider == "openai":
            from openai import OpenAI
            return OpenAI()
        raise ValueError(f"Unknown provider: {self.provider}")

    def structured_call(
        self,
        prompt: str,
        schema: dict,
        model: str | None = None,
        max_tokens: int = 1024,
    ) -> dict:
        """
        Call LLM with a JSON schema, return parsed dict.

        In mock mode, returns a deterministic stub that matches the schema —
        useful for dev without API keys and for tests.
        """
        if self.mock:
            return _mock_response(schema)

        model = model or self.model
        if self.provider == "anthropic":
            return self._anthropic_call(prompt, schema, model, max_tokens)
        elif self.provider == "openai":
            return self._openai_call(prompt, schema, model, max_tokens)
        raise ValueError(f"Unknown provider: {self.provider}")

    def _anthropic_call(self, prompt: str, schema: dict, model: str, max_tokens: int) -> dict:
        """Use Anthropic tool-use for structured output."""
        # TODO: proper tool-use implementation.
        # Sketch:
        #   tool = {"name": "respond", "description": "...", "input_schema": schema}
        #   resp = self._client.messages.create(
        #       model=model, max_tokens=max_tokens,
        #       tools=[tool], tool_choice={"type": "tool", "name": "respond"},
        #       messages=[{"role": "user", "content": prompt}],
        #   )
        #   return resp.content[0].input | {"_usage": {...}}
        raise NotImplementedError("TODO: implement Anthropic structured call")

    def _openai_call(self, prompt: str, schema: dict, model: str, max_tokens: int) -> dict:
        """Use OpenAI function-calling / structured outputs."""
        raise NotImplementedError("TODO: implement OpenAI structured call")


def _mock_response(schema: dict) -> dict:
    """Produce a deterministic stub matching `schema` for dev/testing."""
    result: dict = {}
    props = schema.get("properties", {})
    for name, spec in props.items():
        if spec.get("enum"):
            result[name] = spec["enum"][0]
        elif spec.get("type") == "string":
            result[name] = f"[mock {name}]"
        elif spec.get("type") == "number":
            result[name] = 0.0
        elif spec.get("type") == "integer":
            result[name] = 0
        elif spec.get("type") == "array":
            result[name] = []
        elif spec.get("type") == "object":
            result[name] = {}
        elif spec.get("type") == "boolean":
            result[name] = False
    result["_usage"] = {"total_tokens": 0}
    return result
