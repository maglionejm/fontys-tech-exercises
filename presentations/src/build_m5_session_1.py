"""Build deck: M5 Session 1 - From Prompts to Harnesses.

Theory from the Module 5 course brief (timeline, definitions, evidence, the
eight pieces); practice numbers read from the executed notebook 01
(raw Anthropic SDK, recorded run on claude-opus-5, 30 Sep 2026): bare prompt
39 input tokens, careful prompt 115, hand-written loop 3 model calls, 3 tool
calls, 4,113 input tokens; SDK tool_runner 4,251. Every fact is attributed
on its slide.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import (Circle, FancyArrowPatch, FancyBboxPatch,
                                Polygon, Rectangle)

import deck_style as ds

FIGS = "/tmp/deck-workshop/figs-m5"
os.makedirs(FIGS, exist_ok=True)
pal = ds.mpl_theme()


def notes(slide, text):
    """Speaker notes: a plain-text talk track for the teacher."""
    slide.notes_slide.notes_text_frame.text = text


def _mono_first_column(slide, size=11):
    """Render the first column of a table slide in a code font."""
    for shp in slide.shapes:
        if not shp.has_table:
            continue
        table = shp.table
        for r in range(1, len(table.rows)):
            cell = table.cell(r, 0)
            for p in cell.text_frame.paragraphs:
                for run in p.runs:
                    run.font.name = "Courier New"
                    run.font.size = ds.Pt(size)
                    run.font.color.rgb = ds.NAVY


def _table_font(slide, size=11, header_size=None):
    """Shrink the body (and optionally header) text of the slide's table."""
    for shp in slide.shapes:
        if not shp.has_table:
            continue
        table = shp.table
        for r in range(len(table.rows)):
            for c in range(len(table.columns)):
                for p in table.cell(r, c).text_frame.paragraphs:
                    for run in p.runs:
                        if r == 0:
                            if header_size:
                                run.font.size = ds.Pt(header_size)
                        else:
                            run.font.size = ds.Pt(size)


def _panel_font(slide, size=12):
    """Shrink the 13 pt body lines of a two-column slide's panels."""
    for shp in slide.shapes:
        if not shp.has_text_frame:
            continue
        for p in shp.text_frame.paragraphs:
            for run in p.runs:
                if run.font.size == ds.Pt(13):
                    run.font.size = ds.Pt(size)


# ------------------------------------------------------------------ figures
def make_timeline_fig():
    """Twelve dated steps from few-shot prompting to the harness studies,
    evenly spaced (not to scale), colored by era. Dates from the brief."""
    events = [
        ("2020", "GPT-3: few-shot\nprompting", "prompt"),
        ("Jan 2022", "Chain-of-thought\nprompting", "prompt"),
        ("Oct 2022", "ReAct: reason,\nthen act", "prompt"),
        ("Jun 2023", "OpenAI function\ncalling", "prompt"),
        ("Nov 2024", "Anthropic open-\nsources MCP", "context"),
        ("Dec 2024", "Building effective\nagents", "context"),
        ("Jun 2025", "Context engineering;\nmulti-agent research", "context"),
        ("Sep 2025", "Context engineering\npost; Agent SDK", "context"),
        ("Oct 2025", "Agent Skills", "context"),
        ("Jan 2026", "Demystifying evals\nfor agents", "harness"),
        ("Feb 2026", "'Harness engineering'\nnamed (OpenAI)", "harness"),
        ("Jul 2026", "Eleven-harness\nsource study", "harness"),
    ]
    colors = {"prompt": pal["gray"], "context": pal["blue"],
              "harness": pal["navy"]}
    fig, ax = plt.subplots(figsize=(11.5, 5.0))
    step = 1.0
    xs = [0.7 + i * step for i in range(len(events))]
    ax.plot([0.2, xs[-1] + 0.5], [0, 0], color=pal["sky"], lw=3.5, zorder=1)
    for i, (x, (when, label, era)) in enumerate(zip(xs, events)):
        c = colors[era]
        ax.scatter([x], [0], s=170, color=c, zorder=3, edgecolor="white",
                   lw=1.5)
        up = i % 2 == 0
        sgn = 1 if up else -1
        ax.plot([x, x], [0, sgn * 0.38], color=c, lw=1.1, zorder=2)
        ax.text(x, sgn * 0.46, when, ha="center",
                va="bottom" if up else "top", fontsize=11, fontweight="bold",
                color=c)
        ax.text(x, sgn * 0.82, label, ha="center",
                va="bottom" if up else "top", fontsize=8.6, color=pal["ink"],
                linespacing=1.25)
    # era brackets, above the upper labels
    brackets = [
        (xs[0], xs[3], "PROMPT ERA - the words are the lever", "prompt"),
        (xs[4], xs[8], "CONTEXT ERA - what the model sees on one call",
         "context"),
        (xs[9], xs[11], "HARNESS ERA - the runtime", "harness"),
    ]
    for x0, x1, label, era in brackets:
        c = colors[era]
        ax.plot([x0 - 0.42, x0 - 0.42, x1 + 0.42, x1 + 0.42],
                [1.72, 1.86, 1.86, 1.72], color=c, lw=1.4)
        ax.text((x0 + x1) / 2, 1.95, label, ha="center", va="bottom",
                fontsize=9.8, fontweight="bold", color=c)
    for j, (era, lab) in enumerate([("prompt", "prompt engineering"),
                                    ("context", "context engineering"),
                                    ("harness", "harness engineering")]):
        ax.scatter([0.35 + j * 2.7], [-1.95], s=80, color=colors[era])
        ax.text(0.55 + j * 2.7, -1.95, lab, va="center", fontsize=9.5,
                color=pal["ink"])
    ax.text(xs[-1] + 0.5, -1.95, "six years from the prompt to the harness",
            ha="right", va="center", fontsize=9.5, color=pal["gray"],
            style="italic")
    ax.set_xlim(0, xs[-1] + 0.7)
    ax.set_ylim(-2.2, 2.5)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s1_timeline.png")
    plt.close(fig)


def _small_car(ax, x, y, w, color):
    """A tiny car glyph for the convoy."""
    ax.add_patch(FancyBboxPatch((x, y), w, w * 0.32, boxstyle="round,pad=0.02",
                                facecolor=color, edgecolor=color))
    ax.add_patch(Polygon([(x + w * 0.2, y + w * 0.32), (x + w * 0.32, y + w * 0.55),
                          (x + w * 0.72, y + w * 0.55), (x + w * 0.84, y + w * 0.32)],
                         closed=True, facecolor=color, edgecolor=color))
    for wx in (x + w * 0.24, x + w * 0.76):
        ax.add_patch(Circle((wx, y), w * 0.1, facecolor=pal["navy"],
                            edgecolor="white", lw=0.8, zorder=4))


def make_car_fig():
    """The car: a side view with each harness piece pinned to a part.
    Synthetic - captioned as illustration on the slide."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    # body and cabin (front points right)
    bx, by, bw, bh = 3.2, 1.9, 6.3, 1.25
    ax.add_patch(FancyBboxPatch((bx, by), bw, bh, boxstyle="round,pad=0.08",
                                facecolor=pal["panel"], edgecolor=pal["blue"],
                                lw=1.8))
    ax.add_patch(Polygon([(4.2, by + bh), (5.0, by + bh + 1.15),
                          (7.6, by + bh + 1.15), (8.5, by + bh)],
                         closed=True, facecolor="white", edgecolor=pal["blue"],
                         lw=1.8))
    for wx in (4.6, 8.2):
        ax.add_patch(Circle((wx, by), 0.5, facecolor=pal["navy"],
                            edgecolor="white", lw=1.5, zorder=4))
    # engine (front), steering wheel, dashboard, glovebox, brakes
    ax.add_patch(Rectangle((8.35, by + 0.25), 0.9, 0.75, facecolor=pal["blue"],
                           edgecolor="none"))
    ax.text(8.8, by + 0.62, "engine", ha="center", va="center", color="white",
            fontsize=7.5, fontweight="bold")
    ax.add_patch(Circle((6.95, by + bh + 0.35), 0.22, facecolor="white",
                        edgecolor=pal["navy"], lw=1.8))
    ax.add_patch(Rectangle((7.15, by + bh + 0.05), 0.5, 0.55,
                           facecolor=pal["sky"], edgecolor=pal["navy"], lw=1))
    ax.add_patch(Rectangle((6.05, by + bh + 0.05), 0.6, 0.32,
                           facecolor="white", edgecolor=pal["navy"], lw=1))
    ax.text(6.35, by + bh + 0.21, "glove\nbox", ha="center", va="center",
            fontsize=5.2, color=pal["navy"], linespacing=0.95)
    for wx in (4.6, 8.2):
        ax.add_patch(Circle((wx, by), 0.2, facecolor=pal["blue"],
                            edgecolor="none", zorder=5))
    # trailer hitch and trailer at the back
    ax.plot([bx, bx - 0.55], [by + 0.45, by + 0.45], color=pal["navy"], lw=2.2)
    ax.add_patch(Circle((bx - 0.6, by + 0.45), 0.12, facecolor=pal["navy"],
                        edgecolor="none"))
    ax.add_patch(FancyBboxPatch((0.9, by + 0.05), 1.6, 1.15,
                                boxstyle="round,pad=0.05", facecolor="white",
                                edgecolor=pal["navy"], lw=1.6, ls="--"))
    ax.text(1.7, by + 0.62, "tools", ha="center", va="center",
            color=pal["navy"], fontsize=9, fontweight="bold")
    ax.add_patch(Circle((1.7, by), 0.28, facecolor=pal["navy"],
                        edgecolor="white", lw=1.2, zorder=4))
    # callouts: (anchor x, anchor y, text x, text y, label)
    callouts = [
        (8.8, by + 1.0, 9.3, 5.05, "engine = model"),
        (6.95, by + bh + 0.57, 5.0, 5.05, "steering, pedals = the loop"),
        (7.4, by + bh + 0.62, 7.2, 4.55, "dashboard, mirrors =\ncontext + observability"),
        (6.35, by + bh + 0.05, 5.7, 1.2, "glovebox manuals = skills"),
        (8.2, by - 0.5, 9.0, 0.55, "brakes, belts, airbags =\nguardrails + permissions"),
        (bx - 0.6, by + 0.45, 2.2, 3.55, "hitch = tools\n(MCP = the standard coupling)"),
    ]
    for ax_, ay_, tx, ty, label in callouts:
        ax.annotate(label, xy=(ax_, ay_), xytext=(tx, ty), fontsize=8.6,
                    color=pal["navy"], fontweight="bold", ha="center",
                    va="center", linespacing=1.2,
                    arrowprops=dict(arrowstyle="-", color=pal["gray"], lw=0.9,
                                    shrinkA=0, shrinkB=2))
    # the convoy: lead car with two followers, bottom left
    for i, cx in enumerate((0.4, 1.35, 2.3)):
        _small_car(ax, cx, 0.42, 0.75,
                   pal["blue"] if i == 2 else pal["sky"])
    ax.text(1.75, 1.15, "convoy = lead agent + sub-agents", ha="center",
            fontsize=8.6, color=pal["navy"], fontweight="bold")
    ax.set_xlim(0, 10.6)
    ax.set_ylim(0.1, 5.5)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s1_car.png")
    plt.close(fig)


def make_harness_effect_fig():
    """Same model, different harness: two benchmarks, horizontal bars."""
    fig, axes = plt.subplots(2, 1, figsize=(7.6, 4.8))
    panels = [
        ("SWE-bench Pro - Claude Opus 4.5, two harnesses",
         ["Standardized SEAL scaffold", "Claude Code"], [45.9, 55.4],
         "+9.5 points"),
        ("Terminal-Bench 2 pass@1 - same model, harness changed",
         ["Original harness", "Revised harness"], [69.7, 77.0],
         "+7.3 points"),
    ]
    for ax, (title, names, vals, delta) in zip(axes, panels):
        colors = [pal["sky"], pal["blue"]]
        ax.barh(names, vals, color=colors, height=0.55)
        for i, v in enumerate(vals):
            ax.text(v + 0.8, i, f"{v:.1f}%", va="center", color=pal["ink"],
                    fontsize=11, fontweight="bold")
        ax.text(vals[1] + 15, 1, delta, va="center", color=pal["blue"],
                fontsize=11, fontweight="bold")
        ax.set_xlim(0, 100)
        ax.set_title(title, fontsize=11.5, loc="left")
        ax.set_xlabel("")
        ax.tick_params(axis="y", labelsize=10.5)
        ax.tick_params(axis="x", labelsize=9)
        ax.invert_yaxis()
    axes[1].set_xlabel("score (%) - bar length = share of tasks solved",
                       fontsize=9.5)
    fig.tight_layout(h_pad=1.4)
    fig.savefig(f"{FIGS}/s1_harness_effect.png")
    plt.close(fig)


def make_eight_pieces_fig():
    """The eight pieces: the model at the center, seven pieces in a ring,
    in the canon order. Synthetic - captioned as illustration."""
    import math
    fig, ax = plt.subplots(figsize=(11.5, 5.0))
    cx, cy = 6.25, 2.7
    ax.add_patch(Circle((cx, cy), 0.95, facecolor=pal["blue"],
                        edgecolor=pal["blue"], zorder=3))
    ax.text(cx, cy + 0.2, "1. MODEL", ha="center", va="center", color="white",
            fontsize=12.5, fontweight="bold", zorder=4)
    ax.text(cx, cy - 0.2, "the engine", ha="center", va="center",
            color=pal["sky"], fontsize=10, zorder=4)
    pieces = [
        ("2. Context", "everything the model sees\non one call - a budget"),
        ("3. Tools", "functions it may call by name;\nMCP is the plug"),
        ("4. Skills", "folders of instructions,\nloaded on demand"),
        ("5. The loop", "gather context, act,\nverify, repeat - then stop"),
        ("6. Guardrails", "checks outside the model:\nbefore, during, after"),
        ("7. Orchestration", "workflows, agents,\nsub-agents, teams"),
        ("8. Evals + traces", "task + grader + outcome;\nevery step recorded"),
    ]
    rx, ry = 4.55, 1.95
    bw, bh = 2.55, 1.0
    for i, (name, plain) in enumerate(pieces):
        theta = math.radians(90 - i * 360 / 7)
        x, y = cx + rx * math.cos(theta), cy + ry * math.sin(theta)
        ax.plot([cx, x], [cy, y], color=pal["sky"], lw=1.4, zorder=1)
        ax.add_patch(FancyBboxPatch((x - bw / 2, y - bh / 2), bw, bh,
                                    boxstyle="round,pad=0.05",
                                    facecolor="white", edgecolor=pal["blue"],
                                    lw=1.5, zorder=2))
        ax.text(x, y + 0.24, name, ha="center", va="center", color=pal["navy"],
                fontsize=11.5, fontweight="bold", zorder=4)
        ax.text(x, y - 0.2, plain, ha="center", va="center", color=pal["gray"],
                fontsize=8.6, linespacing=1.2, zorder=4)
    ax.set_xlim(0, 12.5)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s1_eight_pieces.png")
    plt.close(fig)


RUN = "recorded run on claude-opus-5, 30 Sep 2026; live runs vary"
RUN_CAP = "Recorded run on claude-opus-5, 30 Sep 2026; live runs vary"


def make_trace_fig():
    """The route of the hand-written loop in notebook 01 (cell 23 output):
    3 model calls and 3 tool calls, in order, with the usage per call."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    my, ty = 3.3, 1.35
    steps = [
        ("m", "model call 1\ninput 702\noutput 111\nasks 2 listings"),
        ("t", "list_files('.')\nreturns\n288 chars"),
        ("t", "list_files\n(.github/\nworkflows)\n42 chars"),
        ("m", "model call 2\ninput 1,052\noutput 60\nasks read_file"),
        ("t", "read_file\n(notebooks.yml)\n2,809 chars"),
        ("m", "model call 3\ninput 2,359\noutput 179\nend_turn: answer"),
    ]
    bw, bh = 1.78, 1.25
    xs = [0.25 + i * 1.88 for i in range(len(steps))]
    for i, (x, (kind, label)) in enumerate(zip(xs, steps)):
        y = my if kind == "m" else ty
        fc = pal["blue"] if kind == "m" else pal["panel"]
        tc = "white" if kind == "m" else pal["navy"]
        ax.add_patch(FancyBboxPatch((x, y), bw, bh, boxstyle="round,pad=0.04",
                                    facecolor=fc, edgecolor=pal["blue"],
                                    lw=1.3))
        ax.text(x + bw / 2, y + bh / 2, label, ha="center", va="center",
                color=tc, fontsize=7.6, linespacing=1.25)
        if i:
            px = xs[i - 1] + bw
            py = my + bh / 2 if steps[i - 1][0] == "m" else ty + bh / 2
            ax.add_patch(FancyArrowPatch((px, py), (x, y + bh / 2),
                                         arrowstyle="-|>", mutation_scale=12,
                                         color=pal["gray"], lw=1.2,
                                         shrinkA=1, shrinkB=1))
    ax.text(-0.05, my + bh / 2, "MODEL\n(3 calls)", ha="right", va="center",
            fontsize=9, fontweight="bold", color=pal["blue"])
    ax.text(-0.05, ty + bh / 2, "TOOLS\n(3 calls)", ha="right", va="center",
            fontsize=9, fontweight="bold", color=pal["navy"])
    ax.text(xs[-1] + bw / 2, my + bh + 0.25,
            "no tool_use block:\nstop_reason end_turn",
            ha="center", va="bottom", fontsize=8.2, color=pal["gray"],
            linespacing=1.2)
    ax.text(5.35, 0.55, "3 model calls, 3 tool calls: 4,113 input tokens, "
            "350 output tokens, 0.0293 USD\n" + RUN,
            ha="center", va="center", fontsize=9, color=pal["navy"],
            fontweight="bold", linespacing=1.3)
    ax.set_xlim(-1.3, 11.6)
    ax.set_ylim(0.1, 5.4)
    ax.axis("off")
    ax.set_title("What the loop printed: every tool_use and tool_result, in order",
                 fontsize=12.5)
    fig.savefig(f"{FIGS}/s1_trace.png")
    plt.close(fig)


def make_tokens_fig():
    """Input tokens per approach in notebook 01 (cell 25 table)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    names = ["Bare prompt\n(1 model call, no tools)",
             "Careful system prompt\n(1 model call, no tools)",
             "Harness: two tools, a loop\n(3 model calls, 3 tool calls)"]
    vals = [39, 115, 4113]
    labels = ["39 in, 549 out, 0.0139 USD, no checkable fact",
              "115 in, 481 out, 0.0126 USD, no checkable fact",
              "4,113 in, 350 out, 0.0293 USD, the fact and the file"]
    ax.barh(names, vals, color=[pal["sky"], pal["sky"], pal["blue"]], height=0.5)
    for i, (v, lab) in enumerate(zip(vals, labels)):
        if i < 2:
            ax.text(v + 45, i, lab, va="center", fontsize=10.5,
                    fontweight="bold", color=pal["ink"])
        else:
            ax.text(v - 60, i, lab, va="center", ha="right", fontsize=10.5,
                    fontweight="bold", color="white")
    ax.set_xlim(0, 5000)
    ax.set_ylim(-0.6, 2.6)
    ax.invert_yaxis()
    ax.set_xlabel("input tokens sent to the model, all calls added up "
                  "(bar length = what the model had to read)")
    ax.tick_params(axis="y", labelsize=10.5)
    ax.set_title("Same question, three approaches, model: claude-opus-5")
    ax.grid(axis="x", alpha=0.3)
    ax.set_axisbelow(True)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/s1_tokens.png")
    plt.close(fig)


# ------------------------------------------------------------------ slides
def slides():
    prs = ds.new_deck()
    course = "Harness Engineering - Module 5"

    # 1. Title
    s = ds.title_slide(
        prs,
        "Session 1 of 4",
        "From Prompts to Harnesses",
        "Same model, two harnesses, 9.5 points apart. In six years the lever "
        "moved from the words you send to the runtime around the model. "
        "First the ideas, then one question answered three ways.",
        course=course,
    )
    notes(s, "Welcome to Module 5. Four sessions, four notebooks, one idea: "
             "an agent is a model plus a harness, and the harness is where "
             "most of the engineering happens. Today: where the word comes "
             "from, what a harness is made of, and one question answered "
             "three ways in notebook 01. Class question to open: what do you "
             "think happens between your message and the model's answer in "
             "a tool like Claude Code or Codex?")

    # 2. Part 1 divider
    s = ds.section_slide(
        prs, "01",
        "Part 1 - The theory: from the prompt to the harness",
        "Where the word comes from, what a harness is made of, and the "
        "evidence that it changes results.",
    )
    notes(s, "Part 1 is ideas only, about 35 minutes: the timeline, three "
             "definitions, the car, the evidence, the eight pieces, workflows "
             "against agents, and the vocabulary. Class question: before we "
             "start, in one sentence, what is prompt engineering?")

    # 3. Timeline
    s = ds.image_slide(
        prs,
        "Six years moved the lever from the words you send to the runtime "
        "around the model",
        f"{FIGS}/s1_timeline.png",
        kicker="The timeline",
        caption="How to read it: left to right in time, evenly spaced (not to "
                "scale). Gray = prompt era, blue = context era, navy = harness "
                "era. Dates from the cited papers and posts.",
    )
    notes(s, "Walk the line left to right. 2020 to 2023 is the prompt era: "
             "few-shot prompting (Brown et al.), chain-of-thought (Wei et al., "
             "Jan 2022), ReAct (Yao et al., Oct 2022) which interleaves "
             "reasoning and actions and is the seed of the agent loop, and "
             "OpenAI function calling (13 Jun 2023) which made structured tool "
             "calls a product feature. 2024-2025 is the context era: MCP "
             "(25 Nov 2024), Building effective agents (19 Dec 2024), context "
             "engineering replacing prompt engineering in Jun 2025, "
             "Anthropic's context-engineering post and the Agent SDK "
             "(29 Sep 2025), Agent Skills (16 Oct 2025). 2026 is the harness "
             "era: evals (Jan), OpenAI names harness engineering (11 Feb), "
             "the eleven-harness source study (Jul). Class question: which of "
             "these twelve steps have you already used, knowingly or not?")

    # 4. A young field (big number)
    s = ds.big_number_slide(
        prs,
        "The field is young: most harnesses are less than a year old",
        "21,500",
        "'agent harness' repositories created in 2026; median harness age "
        "8.7 months",
        foot="Marmelab, The State of AI Harness Engineering 2026, 24 Sep 2026. "
             "In plain words: almost everyone building this is a beginner too "
             "- the discipline is being written now.",
        kicker="Why now",
    )
    notes(s, "Two numbers to set expectations: 21,500 repositories in one "
             "year, and a median age of 8.7 months. Nobody has ten years of "
             "harness experience. The practices we teach in this module are "
             "the ones that survived the first two years. Class question: "
             "what does a median age of 8.7 months tell you about the "
             "tutorials you find online?")

    # 5. The definition (quote)
    s = ds.quote_slide(
        prs,
        "“An agent is a model plus a harness: the runtime that couples an "
        "LLM to the world through a loop, tools, context management, safety "
        "controls, orchestration, and extension surfaces. Harness "
        "engineering, named as a discipline in early 2026, is the design and "
        "evolution of that runtime.”",
        "Barbaste, Darrigol, Vu and Wiltberger, Harness Engineering: Anatomy, "
        "Architecture, and Evolution of Coding Agents, arXiv 2609.00006, "
        "Jul 2026 - a source-code study of eleven coding agents",
    )
    notes(s, "Read it aloud once, then unpack it: a loop, tools, context "
             "management, safety controls, orchestration, extension surfaces. "
             "Those six words are the table of contents of this module. The "
             "paper read the source code of eleven systems (Claude Code, Codex "
             "CLI, Gemini CLI, Aider, OpenHands, mini-SWE-agent, Hermes, Pi, "
             "OpenCode, OpenClaw, Mistral Vibe) and found that 'the field runs "
             "on hand-rolled async loops and deterministic retrieval'. Class "
             "question: which of the six words do you think is hardest to get "
             "right, and why?")

    # 6. Agent = Model + Harness, and OpenAI's framing
    s = ds.two_col_slide(
        prs,
        "Agent = Model + Harness: one equation, two framings",
        ("Agent = Model + Harness", [
            "Birgitta Bockeler's one-line canon, quoted in Marmelab, Sep 2026",
            "In plain words: the model is the engine; the harness is the "
            "rest of the car",
            "The model maps a context to the next message - nothing else",
            "The harness decides what the model sees, what it may do, and "
            "when to stop",
            "Swap the harness and the same model behaves differently "
            "(evidence in two slides)",
        ]),
        ("OpenAI's framing, Feb 2026", [
            "Five-month experiment: about one million lines of production "
            "code, zero written by hand",
            "The repository is the system of record: design docs, decision "
            "records, plans, quality scores",
            "Constraints enforced mechanically: custom linters and structural "
            "tests in CI",
            "Harness engineering = deterministic scaffolding around "
            "probabilistic model steps",
            "Ryan Lopopolo, Harness engineering: leveraging Codex in an "
            "agent-first world, 11 Feb 2026",
        ]),
        kicker="Three definitions, one idea",
        note="Sources: Marmelab, The State of AI Harness Engineering 2026, "
             "24 Sep 2026; OpenAI, 11 Feb 2026; arXiv 2609.00006, Jul 2026.",
    )
    notes(s, "Left: the shortest definition we have, and the plain-words "
             "version we will repeat all module - the model is the engine, "
             "the harness is the rest of the car. Right: OpenAI's experiment "
             "makes it concrete. When no human writes code by hand, everything "
             "that keeps quality up must live in the harness: documents in the "
             "repository that the agent reads, and checks in CI that the agent "
             "cannot skip. 'Deterministic scaffolding around probabilistic "
             "model steps' is the phrase to remember. Class question: if the "
             "model is probabilistic, which parts of the car must not be?")

    # 7. The car
    s = ds.image_slide(
        prs,
        "Concretely: a model called in a loop, with tools and checks. In "
        "plain words: an engine inside a car",
        f"{FIGS}/s1_car.png",
        kicker="The metaphor for this module",
        bullets=[
            "Concrete first: Claude Code is a program that calls a model in a "
            "loop, runs tools, and checks permissions",
            "Engine = the model; steering and pedals = the loop that picks "
            "the next step",
            "Dashboard and mirrors = context and observability: what the "
            "driver sees",
            "Brakes, belts, airbags = guardrails and permissions, outside the "
            "model",
            "Glovebox manuals = skills, opened only when needed; hitch = "
            "tools, MCP the standard coupling",
            "Convoy with a lead car = orchestrator and sub-agents (Session 4)",
        ],
        caption="Illustration. How to read it: each label pins one harness "
                "piece to one car part. The route on the GPS (the plan) and "
                "the drivers' job board (teams) come in Sessions 3 and 4.",
    )
    notes(s, "Always the concrete thing first, then the picture. Claude Code, "
             "Codex CLI and Gemini CLI are all the same shape: a program calls "
             "a model, the model asks for a tool, the program runs it and "
             "pastes the result back, until the model says it is done. The car "
             "gives us one word per piece for the rest of the module. Class "
             "question: which car part is missing when an agent deletes a "
             "file it should not have touched?")

    # 8. The harness effect (evidence)
    s = ds.image_slide(
        prs,
        "Same model, different harness: up to 9.5 points of harness-only "
        "variation on SWE-bench Pro",
        f"{FIGS}/s1_harness_effect.png",
        kicker="Evidence",
        bullets=[
            "How to read it: each pair of bars is one model; only the "
            "harness around it changes",
            "Claude Opus 4.5 on SWE-bench Pro: 45.9% under the SEAL scaffold, "
            "55.4% under Claude Code",
            "Three harnesses on that same model spanned 50.2% to 55.4%",
            "Terminal-Bench 2 pass@1: 69.7% to 77.0% by changing only the "
            "harness",
            "Third-party monitoring: up to 11 points for GPT-5, 15 points for "
            "Kimi K2 Thinking on SWE-bench Verified",
            "Wording matters: harness-only variation, not 'the harness beats "
            "the model'",
        ],
        caption="Sources: Stop Comparing LLM Agents Without Disclosing the "
                "Harness, arXiv 2605.23950, May 2026; Harness or Model? "
                "Isolating the Harness Effect, arXiv 2609.11987, Sep 2026.",
    )
    notes(s, "This is the slide that justifies the module. The model is held "
             "fixed and the score moves by 7 to 15 points depending on the "
             "runtime around it. Be careful with the wording: the harness "
             "does not beat the model, it changes how much of the model's "
             "capability reaches the task. That is why the May 2026 paper "
             "asks every benchmark to disclose the harness. Class question: "
             "if two papers report different scores for the same model, what "
             "is the first question you now ask?")

    # 9. The eight pieces
    s = ds.image_slide(
        prs,
        "A harness has eight pieces - the model is one of them, the other "
        "seven surround it",
        f"{FIGS}/s1_eight_pieces.png",
        kicker="Anatomy",
        caption="Illustration. How to read it: the numbered order is the "
                "canon order of every deck and of the harness package. "
                "Pieces 1-4: Session 2; 5, 6, 8: Session 3; 7: Sessions 3-4.",
    )
    notes(s, "Read the ring clockwise from the top and give each piece its "
             "plain-words line: context is everything the model sees on one "
             "call; a tool is a function the model asks for by name with JSON "
             "arguments; a skill is a folder of instructions opened when the "
             "task matches; the loop is gather context, act, verify, repeat, "
             "with stop conditions; guardrails are checks that run outside "
             "the model; orchestration is workflows when the path is known and "
             "agents when it is not; evals are a task, a grader and an outcome, "
             "and a trace records every step. Class question: which of the "
             "eight would you build first if you had one afternoon?")

    # 10. Workflows vs agents
    s = ds.two_col_slide(
        prs,
        "Workflows when the path is known, agents when it is not",
        ("Workflow", [
            "'LLMs and tools orchestrated through predefined code paths'",
            "In plain words: a path you wrote in code, with model steps inside",
            "Five patterns: prompt chaining, routing, parallelization, "
            "orchestrator-workers, evaluator-optimizer",
            "Predictable cost and behavior; easy to test step by step",
            "Use it when you can draw the flowchart before you start",
        ]),
        ("Agent", [
            "'LLMs dynamically direct their own processes and tool usage'",
            "In plain words: the model decides the path, step by step, "
            "until done",
            "Needs stop conditions: done, max turns, budget",
            "Higher cost and variance; needs guardrails and a trace",
            "Use it when the steps depend on what the last step found",
        ]),
        kicker="Two ways to orchestrate",
        note="Anthropic, Building effective agents, 19 Dec 2024 - three "
             "principles: simplicity, transparency, invest in the "
             "agent-computer interface.",
    )
    notes(s, "Anthropic's December 2024 post drew this line and it has held. "
             "Start with the simplest thing: a single model call with "
             "retrieval. Move to a workflow when you can draw the steps. Move "
             "to an agent only when the steps depend on what the previous step "
             "found, and then pay for it with stop conditions and traces. "
             "Class question: booking a flight from a fixed form - workflow or "
             "agent? Debugging a failing test - workflow or agent?")

    # 11. Prompt vs context vs harness engineering
    s = ds.table_slide(
        prs,
        "Three disciplines, one direction: from the words to the runtime",
        ["", "Prompt engineering", "Context engineering",
         "Harness engineering"],
        [
            ["What you control", "The words of one message",
             "Everything the model sees on one call: system prompt, files, "
             "history, tool results",
             "The runtime: loop, tools, context, guardrails, orchestration, "
             "evals"],
            ["What you measure", "One answer, judged by eye",
             "Tokens per call; does the right fact reach the model in time",
             "Pass rate on an eval suite; cost and steps per task; traces"],
            ["When it breaks", "The task needs facts or actions the words "
             "cannot supply",
             "The window fills; old or wrong material crowds out the "
             "relevant part",
             "No stop condition, no check outside the model, no test - "
             "failures repeat"],
            ["Named", "2020-2022 (few-shot, chain-of-thought)",
             "Jun 2025 (Lutke; Karpathy)", "11 Feb 2026 (OpenAI)"],
            ["In plain words", "Choose the words well",
             "Decide what goes in, what stays out, when to summarize",
             "Build the car around the engine"],
        ],
        kicker="Vocabulary",
        note="Sources: Wei et al., arXiv 2201.11903, Jan 2022; Karpathy, "
             "25 Jun 2025; OpenAI, 11 Feb 2026; Anthropic, Effective context "
             "engineering for AI agents, 29 Sep 2025.",
        col_widths=[1.1, 2.0, 2.6, 2.6],
    )
    notes(s, "Nothing here replaces the previous column; each contains the "
             "one before. Prompt engineering is still inside context "
             "engineering (the system prompt is words), and context "
             "engineering is inside harness engineering (the harness decides "
             "what enters the window). What changes is what you control and, "
             "above all, what you measure. Class question: which row would "
             "your current chatbot project fail on first?")

    # 12. Glossary for today
    s = ds.table_slide(
        prs,
        "The words of this session, in plain words",
        ["Term", "In plain words", "Where you will meet it today"],
        [
            ["Model", "The text-in, text-out engine; anything that maps a "
             "context to the next message", "client.messages.create(model="
             "'claude-opus-5'); client.models.retrieve for its real facts"],
            ["Prompt", "The words you send", "The bare prompt and the careful "
             "system prompt"],
            ["Context", "Everything the model sees in one call",
             "The system prompt, the messages list and every tool result; "
             "usage.input_tokens counts it"],
            ["Tool", "A function the model asks for by name, with JSON "
             "arguments; the harness runs it", "list_files and read_file, "
             "once as Python and once as JSON (name, description, "
             "input_schema)"],
            ["Harness", "The runtime around the model: loop, tools, context, "
             "checks", "The forty-line loop run_agent; then the SDK's "
             "tool_runner"],
            ["Usage", "The receipt the API returns with every response: "
             "input_tokens and output_tokens", "response.usage after every "
             "call; cost_usd turns it into dollars; the bill at the end"],
        ],
        kicker="Glossary",
        note="Definitions follow the Module 5 course brief; the same lines "
             "appear in the notebooks the first time each word is used.",
        col_widths=[1.0, 3.2, 2.6],
    )
    notes(s, "Say each line once and make the students say it back. These six "
             "words carry the whole practice part. Class question: in one "
             "sentence, what is the difference between a prompt and a context?")

    # 13. Part 2 divider
    s = ds.section_slide(
        prs, "02",
        "Part 2 - The practice: one question, three ways, on the raw SDK",
        "Notebook 01: a bare prompt, a careful system prompt, and a "
        "forty-line loop with two tools answer the same question about this "
        "repository, on the real claude-opus-5.",
    )
    notes(s, "Open notebook 01 now. It needs an ANTHROPIC_API_KEY in a "
             "git-ignored .env at the repository root, or a Colab secret; the "
             "setup cell stops with one sentence if it finds none. Everything "
             "in Part 2 is printed by the notebook from a real run, recorded "
             "on 30 Sep 2026. A live run today differs in wording, route and "
             "tokens, and the notebook says 'in the run recorded here' "
             "wherever it quotes a result. Class question: what do you expect "
             "the bare model to answer about a repository it has never seen, "
             "and why?")

    # 14. The setup, the question, the three answers in words
    s = ds.two_col_slide(
        prs,
        "The setup: a real client, a real model, and a question no model can "
        "know from training",
        ("What we send", [
            "The official Anthropic SDK 1.9.0; the key comes from .env "
            "through dotenv_values and goes to the client, nowhere else",
            "client.models.retrieve: Claude Opus 5, a 1,000,000-token "
            "context window, 128,000 output tokens at most",
            "Every call: max_tokens 2000 and effort medium, so only the "
            "machinery around the model changes",
            "The question: which Python version does the notebook workflow "
            "use, and how many notebooks does its matrix run?",
            "The file that settles it, .github/workflows/notebooks.yml: "
            "python-version 3.12 and 9 notebooks in the matrix",
        ]),
        ("What came back, in the recorded run", [
            "Bare prompt: 'I don't have access to the repository you're "
            "referring to ... Paste the workflow YAML and I'll give you the "
            "exact version and count.'",
            "Careful system prompt: 'I can't answer that - I have no access "
            "to this repository's files', then the file name as a place to "
            "look",
            "Harness, two tools and a loop: 'Python 3.12, and the execute "
            "job's matrix runs 9 notebooks ... Source: "
            ".github/workflows/notebooks.yml'",
            "Same model, same effort, three times; only the third answer can "
            "be checked by opening the file",
        ]),
        kicker="Notebook 01, setup and section 3",
        note=RUN_CAP + " in wording and route. Model facts from "
             "client.models.retrieve; the expected answer is parsed from the "
             "workflow file by the notebook itself, not typed by hand.",
    )
    _panel_font(s, 12)
    notes(s, "Three things to point at in the setup cell: the key never "
             "appears in an output, the client is created once, and the "
             "model facts come from the API, not from memory. The question is "
             "chosen so that no model can know it and one file in this "
             "repository settles it. Read the three answers aloud. The first "
             "two are honest about not knowing, which is good behaviour, but "
             "they contain no checkable fact. The third gives the version, "
             "the count and the path. Class question: the first two answers "
             "both mention notebooks.yml; does that mean the model knew the "
             "file, or guessed a conventional name?")

    # 15. The forty-line loop
    s = ds.table_slide(
        prs,
        "The forty-line loop: messages in, tool_use out, tool_result back, "
        "until the model stops asking",
        ["The line, from run_agent in notebook 01", "In plain words"],
        [
            ['messages = [{"role": "user", "content": question}]',
             "The context starts with the task; everything the model sees "
             "is in this list"],
            ["for turn in range(1, max_turns + 1):",
             "Stop condition 1: a ceiling on model calls, so an agent never "
             "runs forever"],
            ['response = client.messages.create(model=model, max_tokens=2000, '
             'system=system, tools=tools, messages=messages, '
             'output_config={"effort": effort})',
             "One real API call; tools is the JSON list of names, "
             "descriptions and input schemas"],
            ['messages.append({"role": "assistant", "content": '
             'response.content})',
             "Replay the whole reply verbatim: thinking, text and tool_use "
             "blocks"],
            ['if response.stop_reason != "tool_use": break',
             "Stop condition 2: end_turn means answered; max_tokens and "
             "refusal stop the loop too"],
            ['for block in response.content: if block.type == "tool_use": '
             'output = functions[block.name](**block.input)',
             "Your code runs the function the model asked for by name, with "
             "its JSON arguments"],
            ['{"type": "tool_result", "tool_use_id": block.id, "content": '
             'output, "is_error": True}  # is_error only on failure',
             "Each result answers one request by id; a failure goes back as "
             "an error the model can read, not a crash"],
            ['messages.append({"role": "user", "content": results})',
             "All results of one turn travel in one user message; then the "
             "loop goes round again"],
        ],
        kicker="Notebook 01, section 3.3",
        note="How to read it: left, the lines of run_agent (about forty with "
             "printing and bookkeeping, which are left out here); right, what "
             "each line does. The loop printed every tool_use and tool_result "
             "as it ran.",
        col_widths=[3.1, 2.5],
    )
    _table_font(s, 11.5)
    _mono_first_column(s, size=9.5)
    notes(s, "Walk the eight lines in order and name the four shapes the "
             "model and the harness exchange: the messages list, the tools "
             "parameter, the tool_use block the model returns, and the "
             "tool_result block you send back. Two stop conditions, both in "
             "your code: the ceiling on turns and the stop reason. Everything "
             "else in a production harness, permissions, budgets, traces, "
             "sub-agents, is added around these lines, never instead of them. "
             "Class question: which line would you change first to add a "
             "token budget, and which one to refuse a dangerous tool?")

    # 16. What the loop printed (the trace of the recorded run)
    s = ds.image_slide(
        prs,
        "What the loop printed: two listings, one read, then the answer, in "
        "3 model calls",
        f"{FIGS}/s1_trace.png",
        kicker="Notebook 01, section 3.3, recorded run",
        bullets=[
            "How to read it: top lane = model calls, bottom lane = tool "
            "calls, left to right in time",
            "Call 1 asks for two listings at once; the loop runs both and "
            "returns both in one message",
            "Call 2 asks to read notebooks.yml; 2,809 characters come back "
            "as one tool_result",
            "Call 3 has no tool_use block: stop_reason end_turn, the loop "
            "stops. 3 model calls, 3 tool calls",
            "Input tokens grow call by call: 702, then 1,052, then 2,359. "
            "Each call carries all of it",
            "In plain words: the model never got smarter; it was given a "
            "way to look and a loop that kept asking",
        ],
        caption=RUN_CAP + " in route and tokens. Total 4,113 input and 350 "
                "output tokens, 0.0293 USD.",
    )
    notes(s, "Read it as a story. The model cannot know where the workflow "
             "file is, so it lists the root and the workflows folder in one "
             "turn; the loop runs both tools and sends both results back "
             "together. It then reads the one file that matters and answers "
             "with the fact and the path. Point at the input tokens: 702, "
             "1,052, 2,359. Every call re-sends the whole conversation, "
             "including the 2,809-character file, which is where the cost of "
             "a harness goes and the subject of Session 2. Class question: "
             "what would the third call have cost if the README, at almost "
             "17,000 characters, had been read instead of the workflow file?")

    # 17. Three ways side by side (the notebook's table)
    s = ds.table_slide(
        prs,
        "Three ways side by side: only the harness gives the fact, and it "
        "pays for it in input tokens",
        ["Approach", "Model calls", "Tool calls", "Input tokens",
         "Output tokens", "Cost (USD)", "Gives the fact", "Names the file"],
        [
            ["Bare prompt", "1", "0", "39", "549", "0.0139", "No", "Yes"],
            ["Careful prompt", "1", "0", "115", "481", "0.0126", "No", "Yes"],
            ["Harness: two tools, a loop", "3", "3", "4,113", "350", "0.0293",
             "Yes", "Yes"],
        ],
        kicker="Notebook 01, section 3.4",
        note=RUN_CAP + ". 'Gives the fact': the answer holds 3.12 and 9, "
             "parsed from the workflow file by the notebook. 'Names the "
             "file': it mentions notebooks.yml. All three name it; only the "
             "harness read it.",
        col_widths=[2.1, 1.0, 0.9, 1.1, 1.2, 1.0, 1.2, 1.2],
    )
    notes(s, "This is the notebook's own table, checked mechanically: the "
             "checker parses notebooks.yml for the Python version and the "
             "matrix size, so the notebook cannot drift from the repository. "
             "The column that matters is 'gives the fact'. 'Names the file' "
             "is weaker evidence: the two prompt-only answers offer "
             "notebooks.yml as a typical name to go and look for, the harness "
             "cites it as the file it read. Class question: which column "
             "would you add to catch an answer that names the right file but "
             "quotes the wrong version?")

    # 18. Tokens per approach
    s = ds.image_slide(
        prs,
        "The fact cost 4,113 input tokens; the two prompts cost 39 and 115 "
        "and gave none",
        f"{FIGS}/s1_tokens.png",
        kicker="Notebook 01, section 3.4",
        bullets=[
            "How to read it: bar length = input tokens one approach sent, "
            "all its calls added up",
            "Bare prompt 39, careful prompt 115: one call each, almost no "
            "context, no checkable fact",
            "Harness 4,113 over 3 calls: tool descriptions plus every tool "
            "result so far, on every call",
            "Output went the other way: 549 and 481 tokens of hedging "
            "against 350 tokens of answer",
            "Cost: 0.0139 and 0.0126 USD without the fact, 0.0293 USD with "
            "the fact and the file",
            "In plain words: tokens are the currency of harness "
            "engineering; spend them where they buy facts",
        ],
        caption=RUN_CAP + ". Prices from the Claude API reference: 5.00 USD "
                "per million input tokens, 25.00 per million output tokens.",
    )
    notes(s, "Nothing is free. Every tool result is pasted into the context "
             "and the model reads it again on the next call. Note the "
             "surprise in the output column: the two prompt-only answers "
             "wrote more, because they spent their output explaining what "
             "they would need; the harness wrote less, because it had the "
             "fact. Session 2 is about keeping the input bill down: context "
             "budgets, compaction, notes outside the window. Class question: "
             "for which questions would you refuse to pay 0.03 USD, and for "
             "which would you happily pay 3 USD?")

    # 19. The SDK ships the loop
    s = ds.two_col_slide(
        prs,
        "The SDK ships the loop: beta_tool and tool_runner do in ten lines "
        "what you wrote in forty",
        ("Ten lines on the SDK", [
            "beta_tool(list_files), beta_tool(read_file): the JSON "
            "description is generated from the signature and the docstring",
            "Same name, description and schema as the hand-written dicts, "
            "plus a title per argument and additionalProperties: false",
            "client.beta.messages.tool_runner(model, max_tokens, system, "
            "tools, messages, max_iterations=8)",
            "One iteration per model call; generate_tool_call_response() "
            "runs the requested tools and returns the tool_result message",
            "Beta in the Python SDK, hence client.beta; the right default "
            "for a small agent",
        ]),
        ("What it produced in the recorded run", [
            "The same route as your loop: list the root and "
            ".github/workflows, read notebooks.yml, answer",
            "3 model calls, 4,251 input tokens, 358 output tokens, "
            "0.0302 USD (your loop: 4,113 and 350, 0.0293 USD)",
            "The same answer: Python 3.12, 9 notebooks, source notebooks.yml; "
            "gives the fact = True for both loops",
            "The same message shape: a user question, then assistant turns "
            "with tool_use blocks and user turns of tool_result blocks",
            "In plain words: the runner saves the typing; it decides nothing "
            "about what surrounds the loop. That is the harness",
        ]),
        kicker="Notebook 01, section 4",
        note=RUN_CAP + ". The runner sent a conversation of the same shape "
             "and size as the hand-written loop; what it does not decide is "
             "which tools to offer, what to refuse, when to stop, what to "
             "measure, how to test.",
    )
    _panel_font(s, 12)
    notes(s, "Show the generated schema next to the hand-written one: the "
             "decorator kept the docstring, turned the type hint into the "
             "schema and added additionalProperties false. Then the runner: "
             "one for loop, one call to generate_tool_call_response per "
             "iteration, and the same three calls as before. This is the "
             "right default for a small agent, and it is also the point "
             "where the harness starts: tools, refusals, stop conditions, "
             "measurement and tests are yours to add. Session 3 builds them "
             "as a small package with a trace, a budget, hooks and an eval "
             "suite. Class question: name one thing the runner cannot decide "
             "for you.")

    # 20. The eight pieces, mapped to where they live in the module
    s = ds.table_slide(
        prs,
        "The eight pieces and where each one lives in this module: SDK, "
        "harness package, Claude Code, CI",
        ["Piece", "Anthropic SDK (Sessions 1-2)",
         "harness package (Sessions 3-4)", "Claude Code labs (Sessions 2, 4)",
         "CI (Session 3)"],
        [
            ["1 Model", "messages.create(model=...), models.retrieve; "
             "choose by capability, cost, latency", "MAIN_MODEL opus-5, "
             "WORKER_MODEL sonnet-5", "-", "-"],
            ["2 Context", "system, messages, usage.input_tokens; "
             "count_tokens, compaction, notes", "max_input_tokens budget "
             "stop", "CLAUDE.md in the project", "-"],
            ["3 Tools", "raw tool dicts, tool_use, tool_result, beta_tool",
             "@tool(risk=...), ToolRegistry", "MCP servers: claude mcp add",
             "-"],
            ["4 Skills", "a load_skill tool; SKILL.md measured on the real "
             "tokenizer", "-", ".claude/skills/<name>/SKILL.md", "-"],
            ["5 The loop", "run_agent, tool_runner", "Agent.run, "
             "stopped_because", "the CLI's own loop", "-"],
            ["6 Guardrails", "the .env refusal inside read_file",
             "Hooks.before_tool, deny_risk", "settings.json hooks, "
             "permission modes", "unit job: pytest on the path guard"],
            ["7 Orchestration", "-", "five workflow patterns; delegate, "
             "TaskBoard", ".claude/agents/*.md, agent teams", "-"],
            ["8 Evals + observability", "usage, the cost table, the ledger",
             "Trace, evals/cases.yaml, run_evals", "/cost",
             "evals job, only with the secret: results.json"],
        ],
        kicker="Notebook 01, section 5",
        note="How to read it: one row per piece, in the canon order; each "
             "cell names the real artefact you will touch; a dash means none "
             "of its own there.",
        col_widths=[1.4, 2.6, 2.3, 2.3, 1.7],
    )
    _table_font(s, 10, header_size=11.5)
    notes(s, "You have already met four pieces today on the raw SDK: the "
             "model behind one call, the context as a messages list, tools "
             "as JSON, and the loop. Read the other columns as the map of "
             "the module: Session 3 turns the loop into a package with hooks, "
             "a trace and evals; the labs show the same pieces inside Claude "
             "Code as files you can open; CI runs the unit tests always and "
             "the evals when the key is present. Class question: which of "
             "the eight would you build first if you had one afternoon, and "
             "which would you borrow?")

    # 21. Big number: 9.5
    s = ds.big_number_slide(
        prs,
        "One number to keep: the same model, two harnesses, 9.5 points apart",
        "9.5",
        "points of harness-only variation on SWE-bench Pro for Claude Opus "
        "4.5: 45.9% under SEAL, 55.4% under Claude Code",
        foot="arXiv 2605.23950, May 2026; arXiv 2609.11987, Sep 2026. "
             "Notebook 01 shows the same effect at small scale: the same "
             "claude-opus-5 gave no checkable fact without a harness and the "
             "fact with its file inside one (recorded run, 30 Sep 2026).",
        kicker="Takeaway",
    )
    notes(s, "Close the loop with the evidence slide. At benchmark scale the "
             "harness moves the score by 9.5 points; at notebook scale it "
             "moves the answer from 'I cannot know' to the fact and the file. "
             "Same lesson, two scales. Class question: if you could only "
             "change the model or only change the harness for your project, "
             "which would you pick and why?")

    # 22. Close
    s = ds.close_slide(
        prs,
        "You now know what a harness is - next session you build its pieces",
        [
            "Agent = Model + Harness: the model is the engine, the harness is "
            "the rest of the car",
            "Six years moved the lever from the words (prompt) to the window "
            "(context) to the runtime (harness)",
            "Same model, different harness: 9.5 points on SWE-bench Pro - "
            "harness-only variation",
            "Eight pieces: model, context, tools, skills, loop, guardrails, "
            "orchestration, evals and traces",
            "Workflows when the path is known; agents when the steps depend on "
            "the last result",
            "Notebook 01: one question three ways on the raw SDK; only the "
            "forty-line loop gives the fact and the file, at 4,113 input "
            "tokens against 39",
            "The SDK ships the loop (tool_runner); the harness is everything "
            "around it, and Session 3 builds it as a package",
        ],
        course=course,
    )
    notes(s, "Recap the seven lines, then point at the exercises at the end "
             "of notebook 01, all with executed solutions from the same "
             "recorded run: a third tool count_lines (the model called it "
             "straight away and got 49 lines in 2 model calls); max_turns=1 "
             "(the model asked for 2 listings, the tools ran, and the only "
             "answer was 'I'll explore the repository structure first.', "
             "stopped because max_turns); the trap question 'How many "
             "students took this course?' (3 model calls, 2 tool calls, "
             "0.0562 USD, the most expensive run in the notebook, and a plain "
             "'the repository doesn't contain that'); and claude-sonnet-5 on "
             "the same harness (3 model calls, 2 tool calls, 3,783 input "
             "tokens, 0.0106 USD against 0.0293, both give the fact). The "
             "whole notebook billed 17 model calls, 24,077 input tokens, "
             "2,704 output tokens and 0.1720 USD. Next session opens the four "
             "pieces the model sees: models, context, tools and skills. Class "
             "question to close: which of the eight pieces did notebook 01's "
             "loop NOT have, and what could go wrong because of it?")

    return prs


if __name__ == "__main__":
    make_timeline_fig()
    make_car_fig()
    make_harness_effect_fig()
    make_eight_pieces_fig()
    make_trace_fig()
    make_tokens_fig()
    prs = slides()
    out = "../m5-session-1-from-prompts-to-harnesses.pptx"
    ds.save_deck(prs, out, "M5 Session 1 - From Prompts to Harnesses", author="M5 Harness Engineering course")
    print("Slides:", len(prs.slides._sldIdLst))
    print("Saved:", os.path.abspath(out))
