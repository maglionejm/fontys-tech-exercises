"""Build deck: M5 Session 1 - From Prompts to Harnesses.

Theory from the Module 5 course brief (timeline, definitions, evidence, the
eight pieces); practice numbers from notebook 01 as recorded in the brief's
appendix (bare prompt 26 tokens; harness 4 model calls, 3 tool calls,
~1,980 tokens). Every fact is attributed on its slide.
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


def make_trace_fig():
    """The trace of the harnessed run in notebook 01: 4 model calls and
    3 tool calls, in order. Steps from the brief's appendix."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    my, ty = 3.3, 1.35
    steps = [
        ("m", "model call 1\nasks for\nsearch_docs"),
        ("t", "search_docs\nreturns\n3 matches"),
        ("m", "model call 2\nasks for\nread_doc"),
        ("t", "read_doc\nreturns the\nfull text"),
        ("m", "model call 3\nasks for\ncheck_citation"),
        ("t", "check_citation\nreturns\nOK"),
        ("m", "model call 4\nfinal answer\n+ [source: ...]"),
    ]
    bw, bh = 1.46, 1.25
    xs = [0.25 + i * 1.56 for i in range(len(steps))]
    for i, (x, (kind, label)) in enumerate(zip(xs, steps)):
        y = my if kind == "m" else ty
        fc = pal["blue"] if kind == "m" else pal["panel"]
        tc = "white" if kind == "m" else pal["navy"]
        ax.add_patch(FancyBboxPatch((x, y), bw, bh, boxstyle="round,pad=0.04",
                                    facecolor=fc, edgecolor=pal["blue"],
                                    lw=1.3))
        ax.text(x + bw / 2, y + bh / 2, label, ha="center", va="center",
                color=tc, fontsize=7.8, linespacing=1.25,
                fontweight="bold" if kind == "m" and i == 6 else "normal")
        if i:
            px = xs[i - 1] + bw
            py = my + bh / 2 if steps[i - 1][0] == "m" else ty + bh / 2
            ax.add_patch(FancyArrowPatch((px, py), (x, y + bh / 2),
                                         arrowstyle="-|>", mutation_scale=12,
                                         color=pal["gray"], lw=1.2,
                                         shrinkA=1, shrinkB=1))
    ax.text(-0.05, my + bh / 2, "MODEL\n(4 calls)", ha="right", va="center",
            fontsize=9, fontweight="bold", color=pal["blue"])
    ax.text(-0.05, ty + bh / 2, "TOOLS\n(3 calls)", ha="right", va="center",
            fontsize=9, fontweight="bold", color=pal["navy"])
    ax.text(xs[-1] + bw / 2, my + bh + 0.25, "the loop stops:\nno tool call left",
            ha="center", va="bottom", fontsize=8.2, color=pal["gray"],
            linespacing=1.2)
    ax.text(5.35, 0.55, "one run, ~1,980 estimated tokens across the 4 model "
            "calls;\nthe answer carries [source: model-context-protocol]",
            ha="center", va="center", fontsize=9, color=pal["navy"],
            fontweight="bold", linespacing=1.3)
    ax.set_xlim(-1.3, 11.2)
    ax.set_ylim(0.1, 5.4)
    ax.axis("off")
    ax.set_title("The trace: every step of the harnessed run, in order",
                 fontsize=12.5)
    fig.savefig(f"{FIGS}/s1_trace.png")
    plt.close(fig)


def make_tokens_fig():
    """Estimated tokens per approach in notebook 01 (brief appendix)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    names = ["Bare prompt\n(1 model call, no tools)",
             "Prompt-engineered\n(1 model call, no tools)",
             "Harness\n(4 model calls, 3 tool calls)"]
    vals = [26, 39, 1980]
    labels = ["~26 tokens, wrong", "~39 tokens, wrong", "~1,980 tokens, right and cited"]
    ax.barh(names, vals, color=[pal["sky"], pal["sky"], pal["blue"]], height=0.5)
    for i, (v, lab) in enumerate(zip(vals, labels)):
        ax.text(v + 25, i, lab, va="center", fontsize=11,
                fontweight="bold", color=pal["ink"])
    ax.text(1500, 1.55, "about 76x the tokens of the bare prompt -\nand the "
            "only right answer", ha="center", va="center", fontsize=10.5,
            color=pal["navy"], fontweight="bold", linespacing=1.3)
    ax.set_xlim(0, 2650)
    ax.set_ylim(-0.6, 2.6)
    ax.invert_yaxis()
    ax.set_xlabel("estimated tokens for the whole run (bar length = cost)")
    ax.tick_params(axis="y", labelsize=10.5)
    ax.set_title("What each approach cost in notebook 01")
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
                "canon order used in every deck and in the harness library. "
                "Pieces 1-4 are Session 2; 5, 6, 8 are Session 3; 7 is Session 4.",
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
             "context to the next message", "model_for('research'): Claude "
             "with a key in .env, the stand-in without"],
            ["Prompt", "The words you send", "The bare and the improved "
             "prompt"],
            ["Context", "Everything the model sees in one call",
             "The system prompt plus the tool results in the trace"],
            ["Tool", "A function the model asks for by name, with JSON "
             "arguments; the harness runs it", "search_docs, read_doc, "
             "check_citation"],
            ["Harness", "The runtime around the model: loop, tools, context, "
             "checks", "The 15-line loop"],
            ["Trace", "The record of every step: messages, tool calls, "
             "tokens, time", "result.trace.show()"],
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
        "Part 2 - The practice: one question, three ways",
        "Notebook 01: a bare prompt, a better prompt, and a 15-line harness "
        "answer the same question. Then we read the trace.",
    )
    notes(s, "Open notebook 01 in Colab now; the first cell downloads the "
             "small harness library, no key needed. Everything in Part 2 is "
             "printed by the notebook, so students can follow on their own "
             "screen. Class question: what do you expect the bare model to "
             "answer, and why?")

    # 14. Same question, three ways
    s = ds.table_slide(
        prs,
        "One question, three answers: only the harness gets the facts and "
        "shows its source",
        ["Approach", "What we send", "What comes back", "Verdict"],
        [
            ["Bare model", "The question, nothing else",
             "'Anthropic released the Model Context Protocol in 2023 and "
             "Google adopted it in 2024.'",
             "Wrong year, wrong company, no source. 1 turn, ~26 tokens"],
            ["Prompt-engineered",
             "The question plus 'If you are not sure, say so'",
             "'I am not certain. From memory: ...' then the same wrong facts",
             "Hedges, still wrong, no source. 1 turn, ~39 tokens"],
            ["Harness",
             "The question, three tools, a loop with stop conditions",
             "'Anthropic open-sourced the Model Context Protocol on 25 "
             "November 2024 ... On 26 March 2025 OpenAI announced support for "
             "MCP in its Agents SDK ... [source: model-context-protocol]'",
             "Both parts correct, cited. 4 model calls, 3 tool calls, "
             "~1,980 tokens"],
            ["Live demo (claude-opus-5)",
             "A 2026 question no model knows from training: what share of "
             "security rules in instruction files is backed by a real control?",
             "'4.4% ...' with a [source: id] citation - wording varies run "
             "to run",
             "Real Claude, real tokens; the harness supplies the fact"],
        ],
        kicker="Notebook 01, sections 1-3",
        note="Rows 1-3: reference run on the deterministic stand-in; the live "
             "run on Claude varies and reports real tokens. Row 4: the "
             "notebook's live demo (Marmelab, Sep 2026 figure).",
        col_widths=[1.1, 1.9, 3.0, 2.2],
    )
    notes(s, "Run the three cells live if you can. The same model answers "
             "all three times; the only thing that changes is what surrounds "
             "it. Better words do not add facts the model does not have - the "
             "prompt-engineered version is more polite and equally wrong. The "
             "harness adds a library, a way to search it, and a check before "
             "answering. The first three rows are the reference run on the "
             "stand-in, so the numbers are exact; the fourth row is the live "
             "demo on claude-opus-5 with a 2026 fact no model can know from "
             "training, and its wording changes every run. Class question: "
             "what would you have to add to the prompt to make the bare model "
             "right, and would that scale to the next question?")

    # 15. The three tools
    s = ds.table_slide(
        prs,
        "The harness could call three tools - each one a plain Python "
        "function with a docstring",
        ["Tool", "What its description tells the model", "What it returns",
         "Step in the trace"],
        [
            ["search_docs(query, k=3)",
             "Search the course library for documents about a topic; a few "
             "key terms, no full sentences",
             "The best matches as JSON: id, title, score, snippet",
             "1 - finds model-context-protocol"],
            ["read_doc(doc_id)",
             "Read one document in full, by the id search_docs returned",
             "The document text", "2 - reads the full text"],
            ["check_citation(answer, question)",
             "Check that the draft answer's [source: id] tag names a document "
             "that supports it",
             "OK, or PROBLEM with a reason", "3 - returns OK"],
        ],
        kicker="Notebook 01, section 3",
        note="In plain words: a tool is a function the model asks for by name "
             "with JSON arguments; the harness runs it and pastes the result "
             "back. Tool design is Session 2.",
        col_widths=[1.9, 2.7, 2.2, 1.6],
    )
    _mono_first_column(s, size=11)
    notes(s, "Point at the docstrings in the notebook: the first paragraph "
             "becomes the description the model reads, and each 'argument: "
             "explanation' line becomes the schema of that argument. Nothing "
             "is hidden. Class question: what happens if search_docs's "
             "description just said 'Searches'?")

    # 16. The trace
    s = ds.image_slide(
        prs,
        "The trace shows the loop working: search, read, check, then answer",
        f"{FIGS}/s1_trace.png",
        kicker="Notebook 01, section 4",
        bullets=[
            "How to read it: top lane = model calls, bottom lane = tool calls, "
            "left to right in time",
            "Call 1 asks for search_docs; the result names the document "
            "model-context-protocol",
            "Call 2 asks for read_doc; call 3 asks check_citation, which "
            "returns OK",
            "Call 4 has no tool call, so the loop stops and the answer carries "
            "its source",
            "In plain words: a trace is the record of every step - messages, "
            "tool calls, tokens, time",
            "result.trace.show() prints exactly this list",
        ],
        caption="Reference run on the deterministic stand-in (4 model calls, "
                "3 tool calls, ~1,980 estimated tokens); the live run on "
                "Claude varies and reports real tokens.",
    )
    notes(s, "This picture is what every harness produces if you ask it to. "
             "Read it as a story: the model did not know the date, so it "
             "searched; it found a document, so it read it; it drafted an "
             "answer and had it checked; the check passed, so it answered. The "
             "trace is also where debugging happens in Session 3. On live "
             "Claude the trace has the same shape but the number of calls and "
             "the tokens differ from run to run. Class question: where in "
             "this trace would a wrong answer have been "
             "caught?")

    # 17. Tokens per approach
    s = ds.image_slide(
        prs,
        "The right answer cost about 76 times the tokens of the wrong one",
        f"{FIGS}/s1_tokens.png",
        kicker="Notebook 01, section 4",
        bullets=[
            "How to read it: bar length = estimated tokens for the whole run",
            "Bare prompt ~26 tokens, prompt-engineered ~39: one call each, "
            "both wrong",
            "Harness: four calls plus three tool results, ~1,980 tokens, "
            "right on both parts and cited",
            "The tool results are most of the cost: the full document enters "
            "the context",
            "In plain words: a harness trades tokens for facts and checks - "
            "measure the trade",
            "Session 2 shows how to keep that bill down: token-efficient "
            "tools and compaction",
        ],
        caption="Reference run on the deterministic stand-in; the live run on "
                "Claude varies and reports real tokens. Anthropic's research "
                "system ran at ~15x a chat's tokens (Jun 2025).",
    )
    notes(s, "Nothing is free. Every tool result is pasted into the context "
             "and the model reads it again on the next call. That is why "
             "Session 2 spends time on token-efficient tools and on "
             "compaction. Anthropic reported that its multi-agent research "
             "system used about 15 times the tokens of a chat, and accepted "
             "the bill because the task was worth it. The live Claude run "
             "prints real usage from the API instead of the estimate. Class "
             "question: for "
             "which questions would you refuse to pay 76x?")

    # 18. The smallest harness
    s = ds.table_slide(
        prs,
        "The smallest harness fits in 15 lines: a loop, a model call, a tool "
        "call, a stop",
        ["Pseudo-code", "In plain words"],
        [
            ["messages = [user(question)]", "Start the context with the task"],
            ["for turn in range(max_turns):",
             "Stop condition 1: never loop forever"],
            ["    reply = model.complete(system, messages, tool_schemas)",
             "Context in, next message out - the whole model contract"],
            ["    if not reply.tool_calls: return reply.text",
             "Stop condition 2: no tool asked for means done"],
            ["    for call in reply.tool_calls:",
             "The model may ask for several tools in one turn"],
            ["        if not permitted(call): result = 'Denied: ...'",
             "A guardrail outside the model (Session 3)"],
            ["        else: result = tools.run(call.name, call.args)",
             "The harness runs the function and keeps the text"],
            ["        messages.append(tool_result(call, result))",
             "Paste the result back so the next call sees it"],
        ],
        kicker="Notebook 01, section 3",
        note="How to read it: left, the loop notebook 01 writes inline (same "
             "loop for the stand-in and for Claude); right, what each line "
             "does. Anthropic, Claude Agent SDK, Sep 2025.",
        col_widths=[3.0, 2.6],
    )
    _mono_first_column(s, size=11.5)
    notes(s, "Have the students count the lines: eight shown here, fifteen "
             "with the Message class and the tool registry. Everything else "
             "in a production harness - permissions, compaction, traces, "
             "sub-agents - is added around these lines, never instead of "
             "them. Class question: which line would you change first to "
             "add a token budget?")

    # 19. Big number: 9.5
    s = ds.big_number_slide(
        prs,
        "One number to keep: the same model, two harnesses, 9.5 points apart",
        "9.5",
        "points of harness-only variation on SWE-bench Pro for Claude Opus "
        "4.5: 45.9% under SEAL, 55.4% under Claude Code",
        foot="arXiv 2605.23950, May 2026; arXiv 2609.11987, Sep 2026. Our "
             "notebook shows the same effect at toy scale: the stand-in "
             "reference run is wrong without a harness and cited with it; "
             "the live Claude run varies and reports real tokens.",
        kicker="Takeaway",
    )
    notes(s, "Close the loop with the evidence slide. At benchmark scale the "
             "harness moves the score by 9.5 points; at notebook scale it "
             "moves the answer from wrong to right and cited. Same lesson, "
             "two scales. Class question: if you could only change the model "
             "or only change the harness for your project, which would you "
             "pick and why?")

    # 20. Close
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
            "Notebook 01: the same question three ways; only the harness "
            "answers right, with a source, at ~76x the tokens",
            "Two engines, one harness: model_for(role) returns Claude when a "
            "key is present, the stand-in otherwise - notebook 01 runs either "
            "way",
        ],
        course=course,
    )
    notes(s, "Recap the seven lines. The last one is the course mechanics: "
             "with an ANTHROPIC_API_KEY in a git-ignored .env the notebooks run "
             "on real Claude; without one they run on the deterministic "
             "stand-in, which is where every number on these slides comes "
             "from. Then point at the exercises at the end "
             "of notebook 01: they extend the 15-line loop. Next session opens "
             "the four pieces the model sees: models, context, tools and "
             "skills. Class question to close: which of the eight pieces did "
             "notebook 01's harness NOT have, and what could go wrong because "
             "of it?")

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
