"""Tools: Python functions the model may ask the harness to run.

``@tool`` turns a function into a ``Tool`` whose JSON schema (the API's
``input_schema``) is built from the signature and the docstring, so the
description the model reads and the code that runs never drift apart.
"""
from __future__ import annotations

import inspect
import re
import typing
from dataclasses import dataclass, field
from typing import Any, Callable, Iterable

RISK_LEVELS = ("read", "write", "danger")
_JSON_TYPES = {str: "string", int: "integer", float: "number", bool: "boolean", list: "array", dict: "object"}
_PARAM_LINE = re.compile(r"^\s*(\w+)\s*:\s*(.+?)\s*$")


@dataclass
class Tool:
    """One tool: a callable plus what the model is told about it."""

    name: str
    description: str
    input_schema: dict
    fn: Callable[..., Any]
    risk: str = "read"

    def schema(self) -> dict:
        """The dict the Messages API expects in ``tools=[...]``."""
        return {"name": self.name, "description": self.description, "input_schema": self.input_schema}

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.fn(*args, **kwargs)


def _json_type(annotation: Any) -> dict:
    """Map a Python annotation to a JSON schema fragment (strings by default)."""
    origin = typing.get_origin(annotation)
    if origin is typing.Literal:
        return {"type": "string", "enum": list(typing.get_args(annotation))}
    if origin in (list, typing.List):
        args = typing.get_args(annotation)
        return {"type": "array", "items": _json_type(args[0]) if args else {"type": "string"}}
    return {"type": _JSON_TYPES.get(annotation, "string")}


def schema_from_function(fn: Callable[..., Any]) -> tuple[str, dict]:
    """Return (description, input_schema) from a function's signature and docstring.

    Docstring lines shaped ``name: text`` describe the parameter ``name``; every
    other line becomes part of the tool description.
    """
    signature = inspect.signature(fn)
    hints = typing.get_type_hints(fn)
    param_docs: dict[str, str] = {}
    description_lines: list[str] = []
    for line in inspect.getdoc(fn).splitlines() if fn.__doc__ else []:
        match = _PARAM_LINE.match(line)
        if match and match.group(1) in signature.parameters:
            param_docs[match.group(1)] = match.group(2)
        else:
            description_lines.append(line)
    properties: dict[str, dict] = {}
    required: list[str] = []
    for name, param in signature.parameters.items():
        prop = _json_type(hints.get(name, str))
        if name in param_docs:
            prop["description"] = param_docs[name]
        properties[name] = prop
        if param.default is inspect.Parameter.empty:
            required.append(name)
    description = " ".join(" ".join(description_lines).split()) or fn.__name__
    schema: dict = {"type": "object", "properties": properties, "required": required}
    return description, schema


def tool(fn: Callable[..., Any] | None = None, *, risk: str = "read", name: str | None = None):
    """Decorator: ``@tool`` or ``@tool(risk="write")``.

    ``risk`` is one of ``read`` (looks at things), ``write`` (changes files or
    state) or ``danger`` (can run arbitrary code, spend money, reach outside).
    The permission rule of an ``Agent`` decides by this label.
    """
    if risk not in RISK_LEVELS:
        raise ValueError(f"risk must be one of {RISK_LEVELS}, got {risk!r}")

    def wrap(function: Callable[..., Any]) -> Tool:
        description, schema = schema_from_function(function)
        return Tool(name or function.__name__, description, schema, function, risk)

    return wrap(fn) if fn is not None else wrap


@dataclass
class ToolRegistry:
    """The tools one agent may use, looked up by name."""

    tools: dict[str, Tool] = field(default_factory=dict)

    def __init__(self, tools: Iterable[Tool | Callable[..., Any]] = ()):
        self.tools = {}
        for item in tools:
            self.add(item)

    def add(self, item: Tool | Callable[..., Any]) -> Tool:
        entry = item if isinstance(item, Tool) else tool(item)
        self.tools[entry.name] = entry
        return entry

    def get(self, name: str) -> Tool | None:
        return self.tools.get(name)

    def schemas(self) -> list[dict]:
        """Sorted by name so the request prefix (and the prompt cache) stays stable."""
        return [self.tools[name].schema() for name in sorted(self.tools)]

    def __iter__(self):
        return iter(self.tools.values())

    def __len__(self) -> int:
        return len(self.tools)

    def __contains__(self, name: object) -> bool:
        return name in self.tools


def deny_risk(*levels: str) -> Callable[[Tool], bool]:
    """A permission rule that refuses every tool whose risk is in ``levels``."""
    denied = set(levels)

    def permission(candidate: Tool) -> bool:
        return candidate.risk not in denied

    permission.__name__ = f"deny_risk({', '.join(levels)})"
    return permission


def allow_all(candidate: Tool) -> bool:
    """A permission rule that lets every tool run (use it knowingly)."""
    return True
