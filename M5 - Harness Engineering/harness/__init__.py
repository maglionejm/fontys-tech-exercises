"""harness - a small, readable agent harness for the Harness Engineering module.

Everything here is teaching code: plain Python, no framework, no API key
required. Import what a notebook needs:

    from harness import Agent, ScriptedModel, ToolRegistry, tool
    from harness.demo_tools import search_docs, read_doc, check_citation
    from harness.policies import research_policy
"""
from .agent import Agent, Hooks, RunResult, allow_all, deny_risk
from .context import ContextWindow, Notes
from .messages import Message, ToolCall, estimate_tokens, total_tokens
from .models import ModelView, ScriptedModel, call, calls, say
from .skills import Skill, SkillIndex, load_skills
from .tools import Tool, ToolRegistry, tool
from .trace import Event, Trace

__version__ = "0.1.1"
__all__ = ["Agent", "Hooks", "RunResult", "allow_all", "deny_risk", "ContextWindow", "Notes",
           "Message", "ToolCall", "estimate_tokens", "total_tokens", "ModelView",
           "ScriptedModel", "call", "calls", "say", "Skill", "SkillIndex", "load_skills",
           "Tool", "ToolRegistry", "tool", "Event", "Trace"]
