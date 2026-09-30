"""Skills: folders of instructions the agent opens only when needed.

A skill is a directory with a SKILL.md file. The file starts with a small
front matter block (name, description) followed by the instructions. Progressive
disclosure means the agent sees only names and descriptions at first (level 1),
loads the instructions when a task matches (level 2), and reads extra files or
scripts only while executing (level 3).
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from .messages import estimate_tokens
from .tools import Tool, tool

SKILLS_DIR = Path(__file__).parent / "skills"


@dataclass
class Skill:
    name: str
    description: str
    body: str
    path: Path
    resources: list[str] = field(default_factory=list)

    @property
    def catalog_line(self) -> str:
        return f"- {self.name}: {self.description}"


def parse_skill_md(text: str) -> tuple[dict[str, str], str]:
    """Split SKILL.md into its front matter (key: value lines) and body."""
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, text
    meta: dict[str, str] = {}
    for i, line in enumerate(lines[1:], start=1):
        if line.strip() == "---":
            return meta, "\n".join(lines[i + 1:]).strip()
        key, sep, value = line.partition(":")
        if sep:
            meta[key.strip()] = value.strip().strip('"')
    return meta, text


def load_skills(directory: str | Path = SKILLS_DIR) -> dict[str, Skill]:
    skills: dict[str, Skill] = {}
    for skill_md in sorted(Path(directory).glob("*/SKILL.md")):
        meta, body = parse_skill_md(skill_md.read_text(encoding="utf-8"))
        name = meta.get("name", skill_md.parent.name)
        resources = sorted(p.name for p in skill_md.parent.iterdir() if p.name != "SKILL.md")
        skills[name] = Skill(name, meta.get("description", ""), body, skill_md.parent, resources)
    return skills


class SkillIndex:
    """The three levels of progressive disclosure, with a token count for each."""

    def __init__(self, directory: str | Path = SKILLS_DIR):
        self.directory = Path(directory)
        self.skills = load_skills(self.directory)

    def names(self) -> list[str]:
        return list(self.skills)

    def catalog(self) -> str:
        """Level 1: names and descriptions only."""
        return "\n".join(s.catalog_line for s in self.skills.values())

    def load(self, name: str) -> str:
        """Level 2: the full instructions of one skill."""
        skill = self.skills.get(name)
        if skill is None:
            return f"Error: no skill named '{name}'. Available: {', '.join(self.names())}."
        extra = f"\n\nFiles in this skill: {', '.join(skill.resources)}" if skill.resources else ""
        return f"# Skill: {skill.name}\n\n{skill.body}{extra}"

    def resource(self, name: str, filename: str) -> str:
        """Level 3: one supporting file of a skill."""
        skill = self.skills.get(name)
        if skill is None:
            return f"Error: no skill named '{name}'."
        target = (skill.path / filename).resolve()
        if skill.path.resolve() not in target.parents or not target.exists():
            return f"Error: '{filename}' is not a file of skill '{name}'. Files: {skill.resources}"
        return target.read_text(encoding="utf-8")

    def catalog_tokens(self) -> int:
        return estimate_tokens(self.catalog())

    def full_tokens(self) -> int:
        return sum(estimate_tokens(s.body) for s in self.skills.values())

    def tools(self) -> list[Tool]:
        """Two tools that let an agent walk down the levels itself."""
        index = self

        @tool(name="load_skill")
        def load_skill(name: str) -> str:
            """Load the full instructions of a skill from the catalog when the task matches its description.

            name: the skill name exactly as listed in the catalog
            """
            return index.load(name)

        @tool(name="read_skill_file")
        def read_skill_file(name: str, filename: str) -> str:
            """Read a supporting file (script, reference, template) that a loaded skill mentions.

            name: the skill name
            filename: the file name listed in the skill
            """
            return index.resource(name, filename)

        return [load_skill, read_skill_file]
