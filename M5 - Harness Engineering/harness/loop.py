"""The loop: gather context, take action, verify work, repeat.

``Agent.run`` is the whole harness in one method: it calls the model, runs the
tools the model asks for (after the permission rule and the hooks have had
their say), feeds the results back, and stops for one of five reasons.
"""
from __future__ import annotations

import json
import time
from dataclasses import dataclass
from typing import Any, Callable, Iterable

from .client import MAIN_MODEL, Usage, cost_usd
from .hooks import Hooks, ToolRequest
from .tools import Tool, ToolRegistry, deny_risk
from .trace import Trace, short

STOP_REASONS = ("done", "max_turns", "budget", "refusal", "max_tokens")


@dataclass
class RunResult:
    """Everything one run produced, for reading, grading and replaying."""

    answer: str
    parsed: dict | None
    messages: list[dict]
    turns: int                 # model calls made (a budget stop before a call adds none)
    stopped_because: str
    usage: Usage
    cost_usd: float
    trace: Trace
    model: str
    name: str = "agent"
    seconds: float = 0.0

    def summary(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "model": self.model,
            "turns": self.turns,
            "stopped_because": self.stopped_because,
            **self.usage.as_dict(),
            "cost_usd": self.cost_usd,
            "seconds": round(self.seconds, 1),
        }


def text_of(response: Any) -> str:
    """Join the text blocks of a response (thinking and tool_use blocks are skipped)."""
    return "".join(block.text for block in response.content if block.type == "text").strip()


def json_schema_of(schema: Any) -> dict | None:
    """Accept a JSON schema dict or a pydantic model class; return a strict JSON schema."""
    if schema is None:
        return None
    if hasattr(schema, "model_json_schema"):
        schema = schema.model_json_schema()
    return {**schema, "additionalProperties": False} if schema.get("type") == "object" else schema


class Agent:
    """A model plus a harness: tools, hooks, a permission rule and stop conditions."""

    def __init__(
        self,
        client: Any,
        model: str = MAIN_MODEL,
        system: str = "",
        tools: Iterable[Tool | Callable[..., Any]] = (),
        hooks: Hooks | None = None,
        permission: Callable[[Tool], bool] | None = None,
        max_turns: int = 8,
        max_input_tokens: int | None = None,
        effort: str | None = "medium",
        max_tokens: int = 2000,
        output_schema: Any = None,
        name: str = "agent",
        answer_retries: int = 1,
    ) -> None:
        self.client = client
        self.model = model
        self.system = system
        self.tools = tools if isinstance(tools, ToolRegistry) else ToolRegistry(tools)
        self.hooks = hooks or Hooks()
        self.permission = permission or deny_risk("danger")
        self.max_turns = max_turns
        self.max_input_tokens = max_input_tokens
        self.effort = effort
        self.max_tokens = max_tokens
        self.output_schema = json_schema_of(output_schema)
        self.name = name
        self.answer_retries = answer_retries

    # -- the request -----------------------------------------------------------

    def request_kwargs(self, messages: list[dict]) -> dict[str, Any]:
        """The exact keyword arguments sent to ``client.messages.create``."""
        kwargs: dict[str, Any] = {"model": self.model, "max_tokens": self.max_tokens, "messages": list(messages)}
        if self.system:
            kwargs["system"] = self.system
        if len(self.tools):
            kwargs["tools"] = self.tools.schemas()
        output_config: dict[str, Any] = {}
        if self.effort:
            output_config["effort"] = self.effort
        if self.output_schema:
            output_config["format"] = {"type": "json_schema", "schema": self.output_schema}
        if output_config:
            kwargs["output_config"] = output_config
        return kwargs

    def count_tokens(self, messages: list[dict]) -> int:
        """Ask the API how many input tokens the next call would send."""
        kwargs = self.request_kwargs(messages)
        kwargs.pop("max_tokens")
        kwargs.pop("output_config", None)
        return self.client.messages.count_tokens(**kwargs).input_tokens

    # -- the loop --------------------------------------------------------------

    def run(self, task: str, history: list[dict] | None = None) -> RunResult:
        """Run the loop on ``task``; ``history`` is an earlier conversation to continue."""
        messages = list(history or []) + [{"role": "user", "content": task}]
        trace, usage, started = Trace(), Usage(), time.perf_counter()
        retries_left, answer, stopped, calls = self.answer_retries, "", "max_turns", 0
        for turn in range(1, self.max_turns + 1):
            if self.max_input_tokens is not None:
                pending = self.count_tokens(messages)
                if pending > self.max_input_tokens:
                    trace.add("budget", turn, self.model, f"next call would send {pending} tokens > {self.max_input_tokens}")
                    stopped = "budget"
                    break
            tick = time.perf_counter()
            response = self.client.messages.create(**self.request_kwargs(messages))
            calls += 1
            usage = usage + Usage.from_response(response.usage)
            trace.add("model", turn, self.model, f"stop={response.stop_reason} {short(text_of(response), 60)}",
                      input_tokens=response.usage.input_tokens, output_tokens=response.usage.output_tokens,
                      seconds=time.perf_counter() - tick)
            messages.append({"role": "assistant", "content": response.content})  # replayed verbatim
            if response.stop_reason == "tool_use":
                messages.append({"role": "user", "content": self._run_tools(response, turn, trace)})
                continue
            answer = text_of(response)
            if response.stop_reason in ("refusal", "max_tokens"):
                stopped = response.stop_reason
                break
            problem = self.hooks.validate(answer)
            if problem and retries_left > 0:
                retries_left -= 1
                trace.add("validator", turn, "validate_answer", problem)
                messages.append({"role": "user", "content": f"Your answer was rejected: {problem}"})
                continue
            stopped = "done"
            break
        parsed = self._parse(answer)
        return RunResult(answer, parsed, messages, calls, stopped, usage, cost_usd(usage, self.model), trace,
                         self.model, self.name, time.perf_counter() - started)

    def _parse(self, answer: str) -> dict | None:
        if not self.output_schema:
            return None
        try:
            return json.loads(answer)
        except (json.JSONDecodeError, TypeError):
            return None

    # -- the tools -------------------------------------------------------------

    def _run_tools(self, response: Any, turn: int, trace: Trace) -> list[dict]:
        """Execute every tool_use block; return one tool_result block per request."""
        results = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            request = ToolRequest(block.id, block.name, dict(block.input), turn)
            candidate = self.tools.get(block.name)
            reason = self._deny_reason(request, candidate)
            if reason:
                trace.add("denied", turn, block.name, reason)
                results.append({"type": "tool_result", "tool_use_id": block.id, "content": reason, "is_error": True})
                continue
            tick, is_error = time.perf_counter(), False
            try:
                output = str(candidate(**request.input))
            except Exception as exc:  # noqa: BLE001 - the model reads the error and adapts
                output, is_error = f"Error: {exc}", True
            output = self.hooks.apply_after(request, candidate, output)
            trace.add("tool", turn, block.name, f"{short(request.input, 40)} -> {short(output, 50)}",
                      seconds=time.perf_counter() - tick)
            result = {"type": "tool_result", "tool_use_id": block.id, "content": output}
            if is_error:
                result["is_error"] = True
            results.append(result)
        return results

    def _deny_reason(self, request: ToolRequest, candidate: Tool | None) -> str | None:
        """Permission rule first, then the before_tool hooks."""
        if candidate is None:
            return f"Unknown tool {request.name!r}. Available: {sorted(self.tools.tools)}."
        if not self.permission(candidate):
            return f"Tool {candidate.name!r} has risk {candidate.risk!r} and this harness does not permit it."
        return self.hooks.check_before(request, candidate)
