"""Schema generation, risk levels and permission rules."""
from __future__ import annotations

from typing import Literal

import pytest

from harness import ToolRegistry, allow_all, deny_risk, tool


@tool(risk="write")
def save_report(title: str, pages: int = 1, kind: Literal["pdf", "html"] = "pdf") -> str:
    """Save a report to disk.

    Use it after the analysis is complete.

    title: the report title
    pages: how many pages to render
    kind: output format
    """
    return f"{title} ({pages} {kind})"


def test_schema_from_signature_and_docstring():
    schema = save_report.schema()
    assert schema["name"] == "save_report"
    assert schema["description"] == "Save a report to disk. Use it after the analysis is complete."
    props = schema["input_schema"]["properties"]
    assert props["title"] == {"type": "string", "description": "the report title"}
    assert props["pages"] == {"type": "integer", "description": "how many pages to render"}
    assert props["kind"]["enum"] == ["pdf", "html"]
    assert schema["input_schema"]["required"] == ["title"]


def test_tool_is_still_callable_and_carries_risk():
    assert save_report(title="Q3", pages=2) == "Q3 (2 pdf)"
    assert save_report.risk == "write"


def test_bad_risk_is_rejected():
    with pytest.raises(ValueError):
        tool(risk="scary")(lambda x: x)


def test_registry_sorts_schemas_and_wraps_plain_functions():
    def zeta(a: str) -> str:
        """Zeta."""
        return a

    registry = ToolRegistry([save_report, zeta])
    assert [s["name"] for s in registry.schemas()] == ["save_report", "zeta"]
    assert registry.get("zeta").risk == "read"
    assert "save_report" in registry and len(registry) == 2


def test_permission_rules():
    deny = deny_risk("danger")
    assert deny(save_report) is True
    assert deny_risk("write", "danger")(save_report) is False
    assert allow_all(save_report) is True
