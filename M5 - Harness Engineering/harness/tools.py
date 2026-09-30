"""Tools: Python functions the model may call by name.

A tool has a name, a description the model reads, a JSON schema for its
arguments, the function itself, and a risk level the harness can gate on.
"""
from __future__ import annotations

import inspect
import json
import typing
from dataclasses import dataclass
from typing import Any, Callable

from .messages import ToolCall

JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean",
              list: "array", dict: "object"}
RISK_LEVELS = ("read", "write", "danger")


@dataclass
class Tool:
    name: str
    description: str
    parameters: dict[str, Any]
    fn: Callable[..., Any]
    risk: str = "read"

    def schema(self) -> dict[str, Any]:
        """What the model sees: name, description, argument schema."""
        return {"name": self.name, "description": self.description,
                "parameters": self.parameters}

    def call(self, arguments: dict[str, Any]) -> str:
        """Run the tool. Errors come back as text the model can act on."""
        try:
            result = self.fn(**arguments)
        except TypeError as exc:
            expected = list(self.parameters.get("properties", {}))
            return f"Error: bad arguments for {self.name}: {exc}. Expected {expected}."
        except Exception as exc:  # noqa: BLE001 - the model must see any failure
            return f"Error: {self.name} failed with {type(exc).__name__}: {exc}"
        if isinstance(result, str):
            return result
        return json.dumps(result, ensure_ascii=False)


def tool(fn: Callable | None = None, *, name: str | None = None,
         description: str | None = None, risk: str = "read") -> Any:
    """Decorator: build a Tool from a function's signature and docstring.

    The first paragraph of the docstring becomes the description the model
    reads. Lines of the form "argument: explanation" describe each argument.
    """
    if risk not in RISK_LEVELS:
        raise ValueError(f"risk must be one of {RISK_LEVELS}")

    def wrap(f: Callable) -> Tool:
        sig = inspect.signature(f)
        hints = typing.get_type_hints(f)
        props: dict[str, Any] = {}
        required: list[str] = []
        for pname, param in sig.parameters.items():
            ptype = hints.get(pname, str)
            origin = typing.get_origin(ptype) or ptype
            props[pname] = {"type": JSON_TYPES.get(origin, "string")}
            if param.default is inspect.Parameter.empty:
                required.append(pname)
            else:
                props[pname]["default"] = param.default
        doc = inspect.getdoc(f) or ""
        for line in doc.splitlines():
            key, sep, desc = line.partition(":")
            if sep and key.strip() in props and desc.strip():
                props[key.strip()]["description"] = desc.strip()
        summary = doc.split("\n\n")[0].strip() if doc else f"Call {f.__name__}."
        return Tool(name=name or f.__name__, description=description or summary,
                    parameters={"type": "object", "properties": props, "required": required},
                    fn=f, risk=risk)

    return wrap(fn) if fn is not None else wrap


class ToolRegistry:
    """The toolbox the harness hands to the model."""

    def __init__(self, tools: typing.Iterable[Tool] = ()):
        self._tools: dict[str, Tool] = {}
        for t in tools:
            self.add(t)

    def add(self, t: Tool) -> Tool:
        self._tools[t.name] = t
        return t

    def remove(self, name: str) -> None:
        self._tools.pop(name, None)

    def get(self, name: str) -> Tool | None:
        return self._tools.get(name)

    def names(self) -> list[str]:
        return list(self._tools)

    def schemas(self) -> list[dict[str, Any]]:
        return [t.schema() for t in self._tools.values()]

    def describe(self) -> str:
        """A compact catalog for a system prompt: one line per tool."""
        return "\n".join(f"- {t.name}: {t.description}" for t in self._tools.values())

    def call(self, request: ToolCall) -> str:
        t = self.get(request.name)
        if t is None:
            return (f"Error: unknown tool '{request.name}'. "
                    f"Available tools: {', '.join(self.names()) or 'none'}.")
        return t.call(request.arguments)

    def __len__(self) -> int:
        return len(self._tools)

    def __iter__(self):
        return iter(self._tools.values())

    def __contains__(self, name: str) -> bool:
        return name in self._tools
