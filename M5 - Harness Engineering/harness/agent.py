"""The agent loop: gather context, take action, verify work, repeat.

Everything a harness adds to a model meets here: the system prompt and
skill catalog (context), the tool registry (abilities), hooks and permissions
(guardrails), the context window (budget), the trace (observability) and the
stop conditions (max turns, budget, done).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Iterable

from .context import ContextWindow
from .messages import Message, ToolCall, estimate_tokens
from .models import Model
from .skills import SkillIndex
from .tools import Tool, ToolRegistry
from .trace import Trace

BeforeTool = Callable[[ToolCall, Tool | None], str | None]   # return a reason to deny
AfterTool = Callable[[ToolCall, str], str]                   # may rewrite the result
Validator = Callable[[str], str | None]                      # return a problem to fix


@dataclass
class Hooks:
    """Deterministic checks that run around every tool call and final answer."""

    before_tool: list[BeforeTool] = field(default_factory=list)
    after_tool: list[AfterTool] = field(default_factory=list)
    validate_answer: list[Validator] = field(default_factory=list)


@dataclass
class RunResult:
    answer: str
    messages: list[Message]
    trace: Trace
    turns: int
    stopped_because: str

    @property
    def tokens(self) -> int:
        return self.trace.tokens

    def __repr__(self) -> str:
        return (f"RunResult(answer={self.answer[:80]!r}, turns={self.turns}, "
                f"tokens~{self.tokens}, stopped_because={self.stopped_because!r})")


def deny_risk(*levels: str) -> Callable[[Tool], bool]:
    """Permission rule: refuse tools whose risk is in the given levels."""
    blocked = set(levels)
    return lambda t: t.risk not in blocked


def allow_all(_: Tool) -> bool:
    return True


class Agent:
    def __init__(self, model: Model, tools: Iterable[Tool] | ToolRegistry = (),
                 system: str = "", skills: SkillIndex | None = None,
                 max_turns: int = 8, context: ContextWindow | None = None,
                 hooks: Hooks | None = None,
                 permission: Callable[[Tool], bool] | None = None,
                 name: str = "agent", answer_retries: int = 1):
        self.model = model
        self.tools = tools if isinstance(tools, ToolRegistry) else ToolRegistry(tools)
        self.base_system = system
        self.skills = skills
        if skills is not None:
            for t in skills.tools():
                self.tools.add(t)
        self.max_turns = max_turns
        self.context = context or ContextWindow(budget_tokens=10_000_000)
        self.hooks = hooks or Hooks()
        self.permission = permission or deny_risk("danger")
        self.name = name
        self.answer_retries = answer_retries

    def system_prompt(self) -> str:
        parts = [self.base_system.strip()] if self.base_system.strip() else []
        if len(self.tools):
            parts.append("Tools available:\n" + self.tools.describe())
        if self.skills is not None and self.skills.skills:
            parts.append("Skills available (load one with load_skill when the task "
                         "matches its description):\n" + self.skills.catalog())
        return "\n\n".join(parts)

    def _execute(self, request: ToolCall, turn: int, trace: Trace) -> str:
        tool = self.tools.get(request.name)
        if tool is not None and not self.permission(tool):
            reason = f"Denied: '{tool.name}' has risk level '{tool.risk}' and is not permitted here."
            trace.add("denied", turn, request.name, reason)
            return reason
        for hook in self.hooks.before_tool:
            reason = hook(request, tool)
            if reason:
                trace.add("denied", turn, request.name, reason)
                return f"Denied: {reason}"
        result = self.tools.call(request)
        for hook in self.hooks.after_tool:
            result = hook(request, result)
        args = ", ".join(f"{k}={str(v)[:40]!r}" for k, v in request.arguments.items())
        trace.add("tool", turn, request.name, f"({args}) -> {result[:200]}",
                  tokens=estimate_tokens(result))
        return result

    def run(self, task: str, history: list[Message] | None = None) -> RunResult:
        trace = Trace(agent=self.name)
        system = self.system_prompt()
        messages: list[Message] = list(history or []) + [Message("user", task)]
        retries_left = self.answer_retries

        for turn in range(1, self.max_turns + 1):
            if self.context.over_budget(system, messages):
                messages, summary = self.context.compact(messages)
                trace.add("compact", turn, "context", summary)
            trace.add("model", turn, self.model.name, "",
                      tokens=self.context.tokens(system, messages))
            reply = self.model.complete(system, messages, self.tools.schemas())
            messages.append(reply)
            trace.events[-1].detail = reply.as_text()

            if not reply.tool_calls:
                problem = next((p for v in self.hooks.validate_answer
                                for p in [v(reply.content)] if p), None)
                if problem and retries_left > 0:
                    retries_left -= 1
                    trace.add("note", turn, "validator", problem)
                    messages.append(Message("user", f"Your answer was rejected: {problem} "
                                                    f"Fix it and answer again."))
                    continue
                trace.add("final", turn, self.name, reply.content)
                return RunResult(reply.content, messages, trace, turn, "done")

            for request in reply.tool_calls:
                result = self._execute(request, turn, trace)
                messages.append(Message("tool", result, tool_call_id=request.id,
                                        name=request.name))

        trace.add("final", self.max_turns, self.name, "(stopped: max turns)")
        last_text = next((m.content for m in reversed(messages)
                          if m.role == "assistant" and m.content), "")
        return RunResult(last_text, messages, trace, self.max_turns, "max_turns")
