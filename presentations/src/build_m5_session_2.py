"""Build deck: M5 Session 2 - Models, Context, Tools and Skills.

Theory from the Module 5 course brief (model interface and tiers, context as
a budget, tool design rules, MCP, skills and progressive disclosure);
practice numbers from the executed notebook 02 (raw Anthropic SDK, real
Claude models, recorded run of 30 Sep 2026) and from lab 2 (Claude Code
2.1.278 on the lab/ project). Every number on a Part 2 slide is quoted from
a printed notebook output or from the lab guide's observed output, and the
slide names the section it came from.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Rectangle

import deck_style as ds

FIGS = "/tmp/deck-workshop/figs-m5"
os.makedirs(FIGS, exist_ok=True)
pal = ds.mpl_theme()

RUN = "recorded run of 30 Sep 2026; live runs vary"
RUN_CAP = "Recorded run of 30 Sep 2026; live runs vary"


def notes(slide, text):
    """Speaker notes: a plain-text talk track for the teacher."""
    slide.notes_slide.notes_text_frame.text = text


def _mono_columns(slide, columns, size=10.5):
    """Render the given table columns in a code font."""
    for shp in slide.shapes:
        if not shp.has_table:
            continue
        table = shp.table
        for r in range(1, len(table.rows)):
            for c in columns:
                for p in table.cell(r, c).text_frame.paragraphs:
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


def _mono_row(slide, row, size=9.5):
    """Render one table row in a code font (for JSON keys)."""
    for shp in slide.shapes:
        if not shp.has_table:
            continue
        table = shp.table
        for c in range(len(table.columns)):
            for p in table.cell(row, c).text_frame.paragraphs:
                for run in p.runs:
                    run.font.name = "Courier New"
                    run.font.size = ds.Pt(size)
                    run.font.color.rgb = ds.NAVY


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
def make_model_interface_fig():
    """One interface: context in, next message out; three real models plug
    in. Model facts from client.models.retrieve (notebook 02, section 1.2);
    the layout itself is an illustration, captioned as such on the slide."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    y0, h = 3.0, 1.6
    ax.add_patch(FancyBboxPatch((0.2, y0), 2.7, h, boxstyle="round,pad=0.05",
                                facecolor=pal["panel"], edgecolor=pal["sky"],
                                lw=1.5))
    ax.text(1.55, y0 + h - 0.32, "CONTEXT IN", ha="center", color=pal["navy"],
            fontsize=11, fontweight="bold")
    ax.text(1.55, y0 + 0.62, "system prompt\nmessages so far\ntool schemas",
            ha="center", va="center", color=pal["gray"], fontsize=9.2,
            linespacing=1.3)
    ax.add_patch(FancyBboxPatch((3.7, y0), 2.9, h, boxstyle="round,pad=0.05",
                                facecolor=pal["blue"], edgecolor=pal["blue"]))
    ax.text(5.15, y0 + h - 0.36, "THE MODEL", ha="center", color="white",
            fontsize=12, fontweight="bold")
    ax.text(5.15, y0 + 0.6, "client.messages.create(\nmodel, system,\n"
            "messages, tools)", ha="center", va="center", color=pal["sky"],
            fontsize=9, family="monospace", linespacing=1.25)
    ax.add_patch(FancyBboxPatch((7.4, y0), 2.7, h, boxstyle="round,pad=0.05",
                                facecolor=pal["panel"], edgecolor=pal["sky"],
                                lw=1.5))
    ax.text(8.75, y0 + h - 0.32, "NEXT MESSAGE OUT", ha="center",
            color=pal["navy"], fontsize=11, fontweight="bold")
    ax.text(8.75, y0 + 0.62, "content blocks: text,\nor a tool_use with JSON\n"
            "arguments; stop_reason; usage", ha="center", va="center",
            color=pal["gray"], fontsize=8.6, linespacing=1.3)
    for x0, x1 in ((2.95, 3.65), (6.65, 7.35)):
        ax.add_patch(FancyArrowPatch((x0, y0 + h / 2), (x1, y0 + h / 2),
                                     arrowstyle="-|>", mutation_scale=18,
                                     color=pal["navy"], lw=2))
    # the plugs: the three models notebook 02 reads from the Models API
    plugs = [("claude-opus-5", "Claude Opus 5\n1,000,000 in / 128,000 out\n"
              "effort: yes"),
             ("claude-sonnet-5", "Claude Sonnet 5\n1,000,000 in / 128,000 out\n"
              "effort: yes"),
             ("claude-haiku-4-5", "Claude Haiku 4.5\n200,000 in / 64,000 out\n"
              "effort: no (400 if sent)")]
    pw = 2.55
    for i, (name, sub) in enumerate(plugs):
        x = 1.2 + i * 2.9
        ax.add_patch(FancyBboxPatch((x, 0.3), pw, 1.35,
                                    boxstyle="round,pad=0.05",
                                    facecolor="white", edgecolor=pal["blue"],
                                    lw=1.5))
        ax.text(x + pw / 2, 1.4, name, ha="center", color=pal["navy"],
                fontsize=10, fontweight="bold", family="monospace")
        ax.text(x + pw / 2, 0.78, sub, ha="center", va="center",
                color=pal["gray"], fontsize=8.2, linespacing=1.3)
        ax.add_patch(FancyArrowPatch((x + pw / 2, 1.7), (5.15, y0 - 0.08),
                                     arrowstyle="-|>", mutation_scale=13,
                                     color=pal["sky"], lw=1.4,
                                     connectionstyle="arc3,rad=0"))
    ax.text(5.15, 2.55, "same request shape, any model id", ha="center",
            color=pal["blue"], fontsize=9.5, fontweight="bold",
            bbox=dict(boxstyle="round,pad=0.25", facecolor="white",
                      edgecolor="none"))
    ax.set_xlim(0, 10.3)
    ax.set_ylim(0.1, 4.9)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s2_model_interface.png")
    plt.close(fig)


def make_context_budget_fig():
    """The context window as a container filling up, with the three
    techniques that keep it under budget. Segment sizes are illustrative."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    wx, ww, wy0 = 1.35, 2.9, 0.4
    segments = [("system prompt", 0.45, pal["navy"], "white"),
                ("instruction files", 0.45, pal["blue"], "white"),
                ("conversation history", 0.9, pal["sky"], pal["navy"]),
                ("tool results", 1.25, pal["panel"], pal["navy"]),
                ("retrieved documents", 0.95, pal["sky"], pal["navy"]),
                ("notes", 0.3, pal["blue"], "white")]
    y = wy0
    for name, hgt, fc, tc in segments:
        ax.add_patch(Rectangle((wx, y), ww, hgt, facecolor=fc,
                               edgecolor="white", lw=1.2))
        ax.text(wx + ww / 2, y + hgt / 2, name, ha="center", va="center",
                color=tc, fontsize=8.2 if hgt < 0.4 else 9)
        y += hgt
    budget = wy0 + 3.75
    ax.add_patch(Rectangle((wx, wy0), ww, budget - wy0, facecolor="none",
                           edgecolor=pal["navy"], lw=2))
    ax.plot([wx - 0.25, wx + ww + 0.25], [budget, budget], ls="--",
            color=pal["navy"], lw=1.6)
    ax.text(wx - 0.32, budget, "the\nbudget", va="center", ha="right",
            fontsize=9.5, color=pal["navy"], fontweight="bold",
            linespacing=1.2)
    ax.add_patch(Rectangle((wx, budget), ww, y - budget, facecolor="none",
                           edgecolor=pal["gray"], lw=1.2, hatch="////",
                           alpha=0.6))
    ax.text(wx + ww + 0.2, budget + 0.08, "over budget:\nquality drops",
            va="bottom", ha="left", fontsize=7.8, color=pal["gray"],
            linespacing=1.2)
    ax.text(wx + ww / 2, wy0 - 0.22, "THE CONTEXT WINDOW", ha="center",
            va="top", fontsize=10, fontweight="bold", color=pal["navy"])
    # three techniques
    techs = [
        ("1. Compaction", "fold old turns into one summary\nnote; keep the "
         "task and the last turns"),
        ("2. Structured notes", "write memory outside the window\n(a file), "
         "reload only what is needed"),
        ("3. Sub-agents", "work in their own window and return\na "
         "1,000-2,000 token summary"),
    ]
    tx, tw, th = 5.8, 4.3, 1.15
    for i, (head, body) in enumerate(techs):
        ty = 3.55 - i * 1.45
        ax.add_patch(FancyBboxPatch((tx, ty), tw, th, boxstyle="round,pad=0.05",
                                    facecolor="white", edgecolor=pal["blue"],
                                    lw=1.4))
        ax.text(tx + 0.2, ty + th - 0.3, head, fontsize=10.5,
                fontweight="bold", color=pal["navy"], va="center")
        ax.text(tx + 0.2, ty + 0.38, body, fontsize=8.4, color=pal["gray"],
                va="center", linespacing=1.25)
        ax.add_patch(FancyArrowPatch((tx - 0.1, ty + th / 2),
                                     (wx + ww + 0.05, budget - 0.2 - i * 0.9),
                                     arrowstyle="-|>", mutation_scale=12,
                                     color=pal["sky"], lw=1.3))
    ax.text(tx + tw / 2, 5.0, "three ways to stay under budget", ha="center",
            fontsize=10, fontweight="bold", color=pal["blue"])
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0, 5.3)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s2_context_budget.png")
    plt.close(fig)


def make_mcp_fig():
    """MCP as the standard plug (top) and its short timeline (bottom)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    y0, h = 3.15, 1.4
    ax.add_patch(FancyBboxPatch((0.3, y0), 3.0, h, boxstyle="round,pad=0.05",
                                facecolor=pal["blue"], edgecolor=pal["blue"]))
    ax.text(1.8, y0 + h - 0.35, "ANY MODEL CLIENT", ha="center",
            color="white", fontsize=10.5, fontweight="bold")
    ax.text(1.8, y0 + 0.5, "Claude Code, Codex, Gemini CLI,\nyour own harness",
            ha="center", va="center", color=pal["sky"], fontsize=8.6,
            linespacing=1.25)
    ax.add_patch(FancyBboxPatch((6.9, y0), 3.0, h, boxstyle="round,pad=0.05",
                                facecolor=pal["panel"], edgecolor=pal["blue"],
                                lw=1.5))
    ax.text(8.4, y0 + h - 0.35, "ANY TOOL SERVER", ha="center",
            color=pal["navy"], fontsize=10.5, fontweight="bold")
    ax.text(8.4, y0 + 0.5, "files, databases, web search,\ncalendars, "
            "your company's API", ha="center", va="center", color=pal["gray"],
            fontsize=8.6, linespacing=1.25)
    # the plug in the middle: a socket and a plug
    ax.plot([3.3, 4.6], [y0 + h / 2, y0 + h / 2], color=pal["navy"], lw=3)
    ax.add_patch(Rectangle((4.6, y0 + 0.35), 0.5, 0.7, facecolor=pal["navy"],
                           edgecolor="none"))
    for py in (y0 + 0.5, y0 + 0.9):
        ax.plot([5.1, 5.45], [py, py], color=pal["navy"], lw=3)
    ax.add_patch(Rectangle((5.45, y0 + 0.2), 0.55, 1.0, facecolor="white",
                           edgecolor=pal["navy"], lw=2))
    ax.plot([6.0, 6.9], [y0 + h / 2, y0 + h / 2], color=pal["navy"], lw=3)
    ax.text(5.1, y0 + h + 0.15, "MCP", ha="center", va="bottom",
            color=pal["navy"], fontsize=13, fontweight="bold")
    ax.text(5.1, y0 - 0.15, "one protocol: list tools, call a tool,\nget the "
            "result as text", ha="center", va="top", color=pal["gray"],
            fontsize=8.6, linespacing=1.25)
    # the timeline
    ty = 1.0
    ax.plot([0.5, 9.7], [ty, ty], color=pal["sky"], lw=3.5, zorder=1)
    events = [(1.6, "13 Jun 2023", "OpenAI function calling:\nstructured tool "
               "calls, one vendor", pal["gray"]),
              (5.1, "25 Nov 2024", "Anthropic open-sources the\nModel Context "
               "Protocol", pal["blue"]),
              (8.6, "26 Mar 2025", "OpenAI adopts MCP: Agents SDK,\nthen "
               "ChatGPT and Responses API", pal["navy"])]
    for x, when, label, c in events:
        ax.scatter([x], [ty], s=150, color=c, zorder=3, edgecolor="white",
                   lw=1.5)
        ax.text(x, ty + 0.22, when, ha="center", va="bottom", fontsize=10,
                fontweight="bold", color=c)
        ax.text(x, ty - 0.22, label, ha="center", va="top", fontsize=8.2,
                color=pal["ink"], linespacing=1.25)
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0.05, 5.2)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s2_mcp.png")
    plt.close(fig)


def make_skills_levels_fig():
    """Progressive disclosure: three levels, with the token costs measured
    with count_tokens on the two lab skills (notebook 02, section 4.2)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    levels = [
        (0.3, 3.75, 6.3, 1.15, "LEVEL 1 - the catalog", "name + description "
         "of every skill,\nalways in the context", "152 tokens for 2 skills",
         pal["blue"], "white", pal["sky"]),
        (0.3, 2.2, 7.4, 1.15, "LEVEL 2 - the body", "the SKILL.md "
         "instructions,\nloaded when the task matches", "580 tokens for both "
         "bodies (3.8x)", pal["sky"], pal["navy"], pal["navy"]),
        (0.3, 0.65, 8.4, 1.15, "LEVEL 3 - the resources", "the files a "
         "step names, scripts,\ntemplates - opened only during execution",
         "docs/glossary.md", pal["panel"], pal["navy"], pal["navy"]),
    ]
    for x, y, w, h, head, body, cost, fc, tc, cc in levels:
        ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.05",
                                    facecolor=fc, edgecolor=pal["blue"],
                                    lw=1.4))
        ax.text(x + 0.25, y + h - 0.27, head, fontsize=10.5, fontweight="bold",
                color=tc, va="center")
        ax.text(x + w - 0.25, y + h - 0.27, cost, fontsize=10,
                fontweight="bold", color=cc, ha="right", va="center")
        ax.text(x + 0.25, y + 0.36, body, fontsize=8.4, color=tc,
                va="center", linespacing=1.25)
    ax.add_patch(FancyArrowPatch((9.3, 4.7), (9.3, 0.8), arrowstyle="-|>",
                                 mutation_scale=16, color=pal["navy"], lw=1.8))
    ax.text(9.55, 2.75, "loaded later,\nonly if needed", rotation=-90,
            ha="center", va="center", fontsize=9, color=pal["navy"],
            fontweight="bold")
    ax.text(0.3, 5.05, "the lab's skills: repo-answers, explain-term "
            "(lab/.claude/skills/); counts with count_tokens on claude-opus-5",
            fontsize=8.8, color=pal["gray"], va="center")
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0.3, 5.3)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s2_skills_levels.png")
    plt.close(fig)


# The eleven prompt sizes of the five-question session (notebook 02, section
# 2.2), as labelled on the notebook's own chart. The per-question sums the
# notebook printed guard the transcription.
SESSION_CALLS = [
    ("Q1 call 1", 785, False), ("Q1 call 2", 868, False), ("Q1 call 3", 2175, True),
    ("Q2 call 4", 2265, False),
    ("Q3 call 5", 2408, False), ("Q3 call 6", 2619, False), ("Q3 call 7", 3186, True),
    ("Q4 call 8", 3255, False), ("Q4 call 9", 8088, True),
    ("Q5 call 10", 8195, False), ("Q5 call 11", 9265, True),
]
PRINTED_PER_QUESTION = {"Q1": 3828, "Q2": 2265, "Q3": 8213, "Q4": 11343, "Q5": 17460}
for _q, _total in PRINTED_PER_QUESTION.items():
    assert sum(v for lbl, v, _ in SESSION_CALLS if lbl.startswith(_q + " ")) == _total, _q
assert sum(v for _, v, _ in SESSION_CALLS) == 43109


def make_session_growth_fig():
    """Prompt size of every model call in the five-question session on
    claude-sonnet-5 (notebook 02, section 2.2). Navy bars are the calls
    that follow a file read."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = [lbl for lbl, _, _ in SESSION_CALLS]
    vals = [v for _, v, _ in SESSION_CALLS]
    colors = [pal["navy"] if after_read else pal["blue"]
              for _, _, after_read in SESSION_CALLS]
    ys = range(len(vals))
    ax.barh(list(ys), vals, color=colors, height=0.68)
    ax.invert_yaxis()
    for y, v in zip(ys, vals):
        ax.text(v + 120, y, f"{v:,}", va="center", fontsize=9.5,
                color=pal["ink"], fontweight="bold")
    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=9.5)
    ax.set_xlim(0, 11200)
    ax.set_xlabel("input tokens sent to the model (usage.input_tokens)")
    ax.set_title("Prompt size of every model call in the session "
                 "(claude-sonnet-5, low effort)", loc="left", fontsize=12.5)
    ax.text(10900, 4.2, "navy = the call right after\na file read entered "
            "the history", ha="right", va="center", fontsize=9,
            color=pal["navy"], fontweight="bold", linespacing=1.3)
    ax.text(10900, 6.1, "11 calls, 43,109 prompt tokens,\n0.0953 USD, 22 "
            "messages kept", ha="right", va="center", fontsize=9,
            color=pal["gray"], linespacing=1.3)
    fig.tight_layout()
    fig.savefig(f"{FIGS}/s2_session_growth.png")
    plt.close(fig)


def make_compaction_fig():
    """count_tokens on the same session before and after compaction, plus
    the prompt of the sixth question answered from the summary (notebook
    02, sections 2.3)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = ["before compaction\n22 messages", "after compaction\n6 messages",
              "next call, answered\nfrom the summary"]
    vals = [9465, 2681, 2781]
    colors = [pal["blue"], pal["navy"], pal["sky"]]
    ys = range(len(vals))
    ax.barh(list(ys), vals, color=colors, height=0.6)
    ax.invert_yaxis()
    for y, v in zip(ys, vals):
        ax.text(v + 120, y, f"{v:,} tokens", va="center", fontsize=11,
                fontweight="bold", color=pal["ink"])
    ax.annotate("72% smaller: the summary written by\nclaude-sonnet-5 "
                "replaced 16 older messages", xy=(2681, 1.0),
                xytext=(6200, 1.55), fontsize=9.5, color=pal["navy"],
                ha="center", linespacing=1.3,
                arrowprops=dict(arrowstyle="-|>", color=pal["navy"], lw=1.4))
    ax.set_yticks(list(ys))
    ax.set_yticklabels(labels, fontsize=10.5)
    ax.set_xlim(0, 12000)
    ax.set_xlabel("input tokens the next call would send (count_tokens)")
    ax.set_title("The same session measured before and after compaction",
                 loc="left")
    fig.tight_layout()
    fig.savefig(f"{FIGS}/s2_compaction.png")
    plt.close(fig)


# ------------------------------------------------------------------ slides
def slides():
    prs = ds.new_deck()
    course = "Harness Engineering - Module 5"

    # 1. Title
    s = ds.title_slide(
        prs,
        "Session 2 of 4",
        "Models, Context, Tools and Skills",
        "The four pieces the model sees: an engine behind one interface, a "
        "window with a budget, functions it may call, and manuals it opens "
        "only when needed. First the rules, then notebook 02 and lab 2.",
        course=course,
    )
    notes(s, "Session 2 opens the first four pieces of the harness: the "
             "model, the context, the tools and the skills. These are the "
             "pieces the model sees; Session 3 builds the loop and the checks "
             "around them. Class question to open: what did the loop in "
             "notebook 01 put into the model's context that the bare prompt "
             "did not?")

    # 2. Part 1 divider
    s = ds.section_slide(
        prs, "01",
        "Part 1 - The theory: the four pieces the model sees",
        "Pieces 1 to 4 of the harness: model, context, tools, skills. Each "
        "with its plain-words line and its design rules.",
    )
    notes(s, "About 40 minutes of theory, one piece at a time, each with its "
             "plain-words line and the published rules behind it. Class "
             "question: which of the four do you think costs the most tokens "
             "in a long task?")

    # 3. The model behind one interface
    s = ds.image_slide(
        prs,
        "The model sits behind one interface: context in, next message out",
        f"{FIGS}/s2_model_interface.png",
        kicker="Piece 1 - the model",
        bullets=[
            "How to read it: the blue box is the whole contract; any model "
            "id that fits the request fills it",
            "In plain words: the model is the text-in, text-out engine; it "
            "never runs a tool, it asks for one by name with JSON arguments",
            "One request: model, max_tokens, system, messages, tools, "
            "output_config (effort) - nothing else reaches the model",
            "One response: content blocks (text or tool_use), stop_reason "
            "(end_turn, tool_use, max_tokens, refusal) and usage",
            "client.models.retrieve says what a model can do: read it before "
            "you send a parameter it may reject",
            "The harness does not change when the model id does - that is "
            "the point of the interface",
        ],
        caption="Illustration. Model facts from client.models.retrieve in "
                "notebook 02 (section 1.2). The key lives in .env, never in "
                "a cell, never committed.",
    )
    notes(s, "Start with the contract, not the vendor. A model takes the "
             "system prompt, the messages so far and the tool schemas, and "
             "returns one message: text, or a request to call a tool. That is "
             "all a harness needs to know. On the Claude API the contract is "
             "one call, client.messages.create, and the response carries "
             "content, stop_reason and usage. The three plugs are the three "
             "models notebook 02 reads from the Models API: two with a "
             "million-token window, one smaller and cheaper that rejects the "
             "effort parameter. Class question: which of the three inputs "
             "would you expect to grow the most during a long task?")

    # 4. Tiers and routing
    s = ds.table_slide(
        prs,
        "Choose a model by capability, cost and latency - and route cheap "
        "models to easy steps",
        ["Tier", "Capability", "Cost per token", "Latency",
         "Give it these steps"],
        [
            ["Frontier (e.g. Opus-class)", "Highest: planning, synthesis, "
             "hard reasoning", "Highest", "Slowest",
             "Lead agent: plan, delegate, write the final answer"],
            ["Mid (e.g. Sonnet-class)", "High: focused tasks with tools",
             "Lower", "Faster",
             "Workers: search, read, summarize one sub-question"],
            ["Small (e.g. Haiku-class)", "Good at narrow, well-specified "
             "steps", "Lowest", "Fastest",
             "Classify, route, extract fields, check a format"],
        ],
        kicker="Piece 1 - tiers and routing",
        note="Anthropic, How we built our multi-agent research system, "
             "13 Jun 2025: an Opus lead plans and spawns 3-5 Sonnet workers. "
             "Anthropic, Building effective agents, Dec 2024: routing sends "
             "each input to the specialized step.",
        col_widths=[1.6, 2.2, 1.1, 0.9, 2.6],
    )
    notes(s, "The tiers are qualitative on purpose: prices and speeds change "
             "every quarter, the shape of the decision does not. The research "
             "system is the canonical example: the expensive model plans and "
             "synthesizes, cheaper models do the parallel legwork. Routing is "
             "the workflow pattern that makes this automatic: a small model "
             "labels the input, the harness picks the path. This module "
             "routes by role: claude-opus-5 for main agents, claude-sonnet-5 "
             "for workers, judges, routers and planners. Class question: "
             "which steps of notebook 01's loop would you hand to the "
             "cheapest tier?")

    # 5. Context is a budget
    s = ds.image_slide(
        prs,
        "Context is a finite budget: what goes in, what stays out, when to "
        "summarize",
        f"{FIGS}/s2_context_budget.png",
        kicker="Piece 2 - context",
        bullets=[
            "How to read it: the window fills from the bottom; the dashed "
            "line is the budget",
            "In plain words: context is everything the model sees in one call",
            "System prompt, instruction files, history, tool results, "
            "retrieved documents, notes - all compete",
            "Compaction folds old turns into one note; structured notes move "
            "memory to a file",
            "Sub-agents spend tens of thousands of tokens and return "
            "1,000-2,000 token summaries",
            "Karpathy, Jun 2025: 'filling the context window with just the "
            "right information for the next step'",
        ],
        caption="Illustration; segment sizes not to scale. Anthropic, "
                "Effective context engineering for AI agents, 29 Sep 2025; "
                "Karpathy, 25 Jun 2025.",
    )
    notes(s, "Everything the model sees competes for the same window, and "
             "attention gets worse as it fills. Anthropic's post names three "
             "techniques and we build all three in this module: compaction "
             "today, notes today, sub-agents in Session 4. Class question: in "
             "notebook 01's loop, which segment of this window was the "
             "largest?")

    # 6. Instruction files
    s = ds.two_col_slide(
        prs,
        "Instruction files: short, human-written, and enforced - or not at all",
        ("What they are", [
            "CLAUDE.md, AGENTS.md: a file the harness pastes into every call",
            "In plain words: the standing orders the model reads before "
            "every task",
            "63% of large projects ship one; only a handful enforce what it "
            "says",
            "Only 4.4% of security rules in them are backed by a real control",
            "A rule nobody checks is a wish, not a guardrail (Session 3)",
        ]),
        ("What the evidence says", [
            "Human-written instruction files: about +4% task success",
            "Machine-generated ones: worse than having none",
            "When everything is important, nothing is - long files dilute "
            "the rules that matter",
            "Keep the file short, concrete, and about this repository only",
            "Move procedures into skills (piece 4) so they load only when "
            "needed",
        ]),
        kicker="Piece 2 - instruction files",
        note="Marmelab, The State of AI Harness Engineering 2026, 24 Sep "
             "2026. Anthropic, Effective context engineering for AI agents, "
             "29 Sep 2025: system prompts at 'the right altitude'.",
    )
    notes(s, "Two findings and one rule. Findings: a short, human-written "
             "file helps a little; a long, generated one hurts, because it "
             "buries the three rules that matter under fifty that do not. "
             "Rule: when everything is important, nothing is. The 4.4% number "
             "connects to Session 3: a rule in a markdown file is not a "
             "guardrail until something outside the model checks it. The lab "
             "folder ships a CLAUDE.md of about twenty lines. Class question: "
             "what are the three lines you would put in your project's "
             "instruction file?")

    # 7. Tools are prompt engineering for machines
    s = ds.two_col_slide(
        prs,
        "Tool design is prompt engineering for machines",
        ("Anthropic's rules, Sep 2025", [
            "In plain words: a tool is a function the model asks for by "
            "name; the harness runs it",
            "The description says when to use the tool and what it returns",
            "Name tools as verb phrases the model can reason with: "
            "list_files, read_file, write_note - not 'lookup' with an "
            "argument 'q'",
            "Token-efficient results: filter, truncate, paginate; return ids, "
            "not whole documents",
            "Errors that teach: say what went wrong and what to try next",
        ]),
        ("One anecdote", [
            "A web-search tool kept appending '2025' to every query",
            "The model had learned the habit from the tool's vague description",
            "The fix was not code: a better description of the query argument",
            "Lesson: the model reads the description before every call - "
            "write it as a prompt",
            "Anthropic, Writing effective tools for agents, Sep 2025",
        ]),
        kicker="Piece 3 - tools",
        note="Anthropic, Building effective agents, Dec 2024: 'invest as much "
             "effort in the agent-computer interface as in the human one.'",
    )
    notes(s, "The model never sees your code; it sees the name, the "
             "description and the argument schema. Those are a prompt, and "
             "the same care applies: say when to use the tool, what it "
             "returns, and what the arguments look like. The '2025' story is "
             "the best illustration: a behavior bug fixed by rewriting a "
             "sentence. Class question: how would you rewrite the "
             "description 'lookup: Searches.' in one sentence?")

    # 8. Fewer tools (big number)
    s = ds.big_number_slide(
        prs,
        "Fewer, better tools beat many tools",
        "80%",
        "of its tools removed by Vercel: task success rose from 80% to 100%, "
        "tokens halved, latency fell from 724 s to 141 s",
        foot="Vercel's agent, as reported in Marmelab, The State of AI Harness "
             "Engineering 2026, 24 Sep 2026. In plain words: every extra tool "
             "is another schema in the context and another wrong choice to "
             "make.",
        kicker="Piece 3 - how many tools",
    )
    notes(s, "Every tool schema is pasted into the context on every call, and "
             "every extra tool is one more way to pick the wrong one. Vercel "
             "cut 80% of theirs and got faster, cheaper and more reliable at "
             "once. Class question: notebook 02's agents carry two to five "
             "tools - which one would you remove, and what would break?")

    # 9. MCP
    s = ds.image_slide(
        prs,
        "MCP is the standard plug: any tool server fits any model client",
        f"{FIGS}/s2_mcp.png",
        kicker="Piece 3 - the plug",
        bullets=[
            "How to read it: top, the plug between clients and servers; "
            "bottom, the dates",
            "In plain words: MCP is a standard plug, so any tool server fits "
            "any model client",
            "Before: each product wrote its own adapter for each tool "
            "(function calling, Jun 2023)",
            "25 Nov 2024: Anthropic open-sources the Model Context Protocol",
            "26 Mar 2025: OpenAI adopts it - Agents SDK, then ChatGPT and the "
            "Responses API",
            "One protocol: list the tools, call a tool, get the result as "
            "text - lab 2 plugs one in with claude mcp add",
        ],
        caption="Illustration. Dates: Anthropic, Introducing the Model Context "
                "Protocol, 25 Nov 2024; OpenAI Agents SDK release notes, "
                "26 Mar 2025.",
    )
    notes(s, "Function calling gave us structured tool calls in 2023, but "
             "every vendor and every tool needed its own adapter. MCP "
             "standardizes the socket: a server lists its tools, a client "
             "calls them, results come back as text. When the second big "
             "vendor adopted it four months later, it became the plug. An "
             "MCP tool is still a name, a description and a JSON schema, so "
             "everything on the tools slides applies over the plug. Class "
             "question: what is the USB of your daily life, and what did the "
             "world look like before it?")

    # 10. Skills and progressive disclosure
    s = ds.image_slide(
        prs,
        "Skills load in three levels - the catalog is always there, the "
        "manual opens on demand",
        f"{FIGS}/s2_skills_levels.png",
        kicker="Piece 4 - skills",
        bullets=[
            "How to read it: each step down is loaded later and costs more; "
            "numbers from the two lab skills on the real tokenizer",
            "In plain words: a skill is a folder with a SKILL.md and optional "
            "files; read the description first",
            "Level 1: name + description of every skill, 152 tokens for the "
            "two skills",
            "Level 2: the body of the one that matches, 580 tokens if both "
            "were loaded (3.8x)",
            "Level 3: docs/glossary.md and the other files a step names - "
            "opened only while executing",
            "Skills teach procedures; tools give abilities; prompts give the "
            "task",
        ],
        caption="Token counts with count_tokens on claude-opus-5 (notebook 02, "
                "section 4.2). Anthropic, Agent Skills, 16 Oct 2025; open "
                "standard 18 Dec 2025, 40+ platforms.",
    )
    notes(s, "Progressive disclosure is the context-budget idea applied to "
             "instructions. The agent always sees the catalog, a few tens of "
             "tokens per skill; it opens the body when the task matches, and "
             "the resources only while executing. The two skills live in "
             "lab/.claude/skills/, where Claude Code looks for them, and "
             "notebook 02 measures them with the API's token counter. Skills "
             "became an open standard in December 2025 and are supported by "
             "more than forty platforms. Class question: which of your own "
             "recurring procedures would you write as a SKILL.md first?")

    # 11. Skills vs tools vs prompts
    s = ds.table_slide(
        prs,
        "Prompts give the task, tools give abilities, skills teach procedures",
        ["", "Prompt", "Tool", "Skill"],
        [
            ["What it is", "The words you send for this task",
             "A function the model may call by name, with JSON arguments",
             "A folder: SKILL.md (name, description, steps) plus scripts and "
             "references"],
            ["What the model gets", "The goal and the constraints",
             "An ability: list, read, calculate, check",
             "A procedure: which tools, in which order, with which checks"],
            ["When it loads", "Every call", "Schema on every call; result "
             "when called", "Description always; body when the task matches; "
             "resources during execution"],
            ["In this module", "'Which licence does this repository use?'",
             "list_files, read_file, write_note, read_notes, load_skill",
             "repo-answers, explain-term in lab/.claude/skills/"],
            ["Who writes it", "The user, each time", "A developer, once",
             "A domain expert, once - reused across tasks and platforms"],
        ],
        kicker="Piece 4 - the three compared",
        note="Anthropic, Agent Skills, 16 Oct 2025; Anthropic, Writing "
             "effective tools for agents, Sep 2025.",
        col_widths=[1.3, 2.2, 2.5, 3.0],
    )
    notes(s, "Students mix these three up for weeks, so draw the line hard. "
             "A prompt is the task. A tool is an ability the harness "
             "executes. A skill is a procedure: which tools, in which order, "
             "with which checks. Class question: 'always end with a Source: "
             "line naming the file' - prompt, tool or skill?")

    # 12. Part 2 divider
    s = ds.section_slide(
        prs, "02",
        "Part 2 - The practice: notebook 02 and lab 2",
        "Three models read from the API, a session that grows and gets "
        "compacted, a vague tool against a clear one, skills measured on the "
        "real tokenizer - then Claude Code loading a skill and an MCP server.",
    )
    notes(s, "Open notebook 02; it needs the ANTHROPIC_API_KEY in the "
             "repository .env or the Colab secret, and it stops with one "
             "sentence if none is found. Every number that follows is from "
             "the run recorded in the notebook on 30 September 2026: 49 model "
             "calls, 0.4797 USD in total (section 9). Live runs vary; say so "
             "whenever a student's number differs. Class question: which of "
             "the four pieces do you expect to be the easiest to get wrong "
             "in your own project?")

    # 13. Three models, read from the API and priced
    s = ds.table_slide(
        prs,
        "Three models, read from the API and priced on the same question",
        ["Model", "Context window", "Max output", "Effort parameter",
         "Input tokens", "Output tokens", "Seconds", "Cost USD"],
        [
            ["claude-opus-5", "1,000,000", "128,000", "yes", "1,321", "50",
             "1.7", "0.00785"],
            ["claude-sonnet-5", "1,000,000", "128,000", "yes", "1,321", "37",
             "1.2", "0.00301"],
            ["claude-haiku-4-5", "200,000", "64,000", "no (400 if sent)",
             "945", "29", "0.9", "0.00109"],
        ],
        kicker="Notebook 02 - the model",
        note="Left: client.models.retrieve (1.2). Right: the same workflow "
             "file and question to all three; all answered Python 3.12 and 9 "
             "notebooks (1.3). Haiku 4.5 rejects effort, so the notebook reads "
             "capabilities first. " + RUN_CAP + ".",
        col_widths=[1.7, 1.2, 1.0, 1.4, 1.0, 1.0, 0.8, 0.9],
    )
    _mono_columns(s, [0], size=11)
    notes(s, "Two tables from the notebook on one slide. The left half is "
             "read from the Models API, not remembered: display name, window, "
             "maximum output, and a capability tree. The smallest model does "
             "not accept the effort parameter at all, the API answers 400 if "
             "you send it, and it has no adaptive thinking or server-side "
             "compaction; all three support structured outputs. That is why "
             "the notebook builds each request from the capability table. "
             "The right half is the same document and question on all three: "
             "identical answers, three prices, and note that the two large "
             "models count 1,321 input tokens while Haiku counts 945 for the "
             "same text, because each family has its own tokenizer. Class "
             "question: when would the cheapest row be the wrong choice even "
             "though it answered correctly here?")

    # 14. The session grows
    s = ds.image_slide(
        prs,
        "Every call re-sends everything before it: five questions, 11 model "
        "calls, 43,109 prompt tokens",
        f"{FIGS}/s2_session_growth.png",
        kicker="Notebook 02 - context",
        bullets=[
            "How to read it: one bar per model call, in order; each bar is "
            "the whole conversation so far, navy bars follow a file read",
            "Counted first with count_tokens: system prompt 87 tokens, the "
            "two tool schemas 609, README.md as read_file returns it 4,777",
            "Five questions on claude-sonnet-5 at low effort: 11 model calls, "
            "43,109 prompt tokens, 0.0953 USD, 22 messages in the history",
            "Question 1 took 3 calls and 3,828 input tokens; question 5 took "
            "2 calls and 17,460, because every earlier file read rode along",
            "The same README counts 4,777 tokens on opus-5 and sonnet-5 but "
            "3,557 on haiku-4-5: always count with the model you will call",
            "In plain words: a file you read once is paid for again on every "
            "later call of the session",
        ],
        caption="Notebook 02, sections 2.1 and 2.2, values as printed by the "
                "notebook; " + RUN + ".",
    )
    notes(s, "Run this section live if you can: the loop prints every tool "
             "call and the answer to each question, and the chart shows the "
             "real input tokens of each call. The steps are file reads "
             "entering the conversation and staying there: after the README "
             "read during question 4 the prompt jumps from 3,255 to 8,088 "
             "tokens. Point out the first table too: the first tool you add "
             "costs 438 tokens because the API prepends its tool-use "
             "preamble, both tools 609, and one README read costs more than "
             "fifty system prompts. Class question: what would the eleventh "
             "bar look like after fifty questions, and what would you do "
             "about it?")

    # 15. Compaction and notes
    s = ds.image_slide(
        prs,
        "Compaction cuts the next prompt from 9,465 to 2,681 tokens; notes "
        "survive a fresh session",
        f"{FIGS}/s2_compaction.png",
        kicker="Notebook 02 - context",
        bullets=[
            "How to read it: the same session counted twice; bar 2 keeps "
            "the last question plus a summary",
            "The summary by claude-sonnet-5: 1,296 in, 586 out, 0.0085 USD; "
            "22 messages became 6, 72% smaller",
            "A sixth question answered from the summary alone: 1 model call, "
            "0 tool calls, 2,781 input tokens",
            "Lossy on purpose: what the summary drops is gone; the "
            "summarizing prompt is context engineering",
            "Notes are two ordinary tools, write_note and read_notes; the "
            "agent saved 2 facts with their sources",
            "A fresh session read them back: 2 model calls, 1 tool call, "
            "2,096 input tokens, 0.0156 USD",
        ],
        caption="Notebook 02, section 2.3 (compaction) and 2.4 (notes); "
                + RUN + ". Anthropic, Effective context engineering, 29 Sep "
                "2025.",
    )
    notes(s, "Compaction done the real way, in three visible steps: split the "
             "history at the last question, ask the worker model for a "
             "summary that keeps facts, sources and files read but drops raw "
             "file contents, and rebuild the message list with the summary in "
             "front. Read the summary the model wrote aloud: it lists the "
             "three files and every fact. Then the sixth question proves the "
             "session still works. Notes are the second technique: two plain "
             "tools and a file in the temporary folder; a brand-new context "
             "reads both facts back. That is the mechanism behind CLAUDE.md "
             "and auto-memory in coding agents. Class question: what would "
             "you lose if the compaction summary were just 'earlier "
             "conversation omitted'?")

    # 16. Five recorded runs on the same tools
    s = ds.table_slide(
        prs,
        "Five recorded runs on the same tools: the description, the error "
        "text and the gate decide the outcome",
        ["Run (section)", "Model calls", "Tool calls", "Failed or denied",
         "Input tokens", "Output tokens", "Cost USD", "Time (s)",
         "What happened"],
        [
            ["vague lookup: 'Searches.', argument q (3.2)", "5", "5",
             "1 failed", "6,474", "399", "0.0423", "19.1",
             "First call sent a search phrase, not a path; the error text "
             "taught it; answered 3.12 and named the file"],
            ["clear read_file (3.2)", "3", "3", "0", "4,207", "284", "0.0281",
             "5.4", "Listed the folder, read the file, answered 3.12 and "
             "named the file"],
            ["error recovery: read docs/README.md (3.3)", "4", "4",
             "1 failed", "9,176", "626", "0.0615", "10.4",
             "Error said 'call list_files'; it listed docs/, said the file "
             "does not exist, answered from docs/index.html"],
            ["strict tools, claude-sonnet-5 (3.4)", "3", "2", "0", "3,158",
             "170", "0.0080", "4.7",
             "Arguments guaranteed to match the schema; quoted anthropic, "
             "python-dotenv, pyyaml from requirements.txt"],
            ["gated: deny the docs/ folder (3.5)", "4", "7", "1 denied",
             "14,407", "523", "0.0851", "15.8",
             "DENIED on list_files('docs'); kept searching other files; "
             "max_turns=4 stopped it with no answer"],
        ],
        kicker="Notebook 02 - tools",
        note="One row per run on the repository; rows 1-3 and 5 on "
             "claude-opus-5, row 4 on claude-sonnet-5. The two tool schemas "
             "add 609 tokens to every call, 438 for the first alone (3.1). "
             + RUN_CAP + ".",
        col_widths=[2.1, 0.7, 0.7, 0.85, 0.85, 0.85, 0.8, 0.8, 3.15],
    )
    _table_font(s, size=11, header_size=11.5)
    notes(s, "Read the rows as five experiments on the same two tools. Rows "
             "one and two are the vague-tool experiment as it actually went: "
             "both runs reached the right answer and named the file, so the "
             "vague description did not break the agent, it made it pay: the "
             "first lookup call sent 'python-version notebook workflow' as "
             "q and failed, and the guess cost 2 extra model calls, 2,267 "
             "extra input tokens and 0.0142 USD more. Row three: the error "
             "message named the next step, so the model listed the folder "
             "and answered honestly that the file does not exist. Row four: "
             "strict tools guarantee the arguments, not the choice of tool. "
             "Row five is the honest one: the gate denied docs/ as designed, "
             "but our denial text offered 'use other files', the model took "
             "the offer and kept searching until max_turns stopped it with "
             "no answer. A gate should say exactly what to do instead, and "
             "max_turns is itself a brake. Class question: rewrite the "
             "denial message so the model stops and reports instead of "
             "searching on.")

    # 17. Skills measured and loaded
    s = ds.table_slide(
        prs,
        "Skills on the real tokenizer: 152 tokens of catalog on every call, "
        "580 of bodies opened on demand",
        ["Skill (lab/.claude/skills/)", "Level 1 - catalog line (tokens)",
         "Level 2 - full body (tokens)", "What the description triggers on"],
        [
            ["repo-answers", "68", "306",
             "what the project, its docs or its configuration say; a fact to "
             "look up rather than remember"],
            ["explain-term", "84", "274",
             "what a term means, a plain-words explanation, how a concept "
             "fits the car metaphor"],
            ["both skills", "152", "580 (3.8x)",
             "the catalog rides along on every call; a body only when a task "
             "matches its description"],
        ],
        kicker="Notebook 02 - skills",
        note="count_tokens on claude-opus-5 (4.2). The load_skill run (4.3): "
             "turn 1 load_skill('repo-answers'), then list, read, cite; 3 "
             "model calls, 5,007 input tokens, 0.0303 USD, answer ends "
             "'Source: LICENSE'. " + RUN_CAP + ".",
        col_widths=[1.8, 1.6, 1.6, 4.0],
    )
    _mono_columns(s, [0], size=11)
    notes(s, "The skills are real files in the lab folder, parsed with plain "
             "Python and counted with the API's token counter. Level 1 is one "
             "line per skill, level 2 the body: 152 against 580 tokens for "
             "the two, 3.8 times more. Then the notebook appends the catalog "
             "to the system prompt and adds a load_skill tool: on the licence "
             "question the model's first action was load_skill for "
             "repo-answers, and it followed the procedure it had just read, "
             "ending with a Source line. Exercise 1's count-things skill "
             "measured 54 and 112 tokens. Class question: which of the two "
             "descriptions would you rewrite, and why?")

    # 18. Lab: the skill loads in Claude Code
    s = ds.two_col_slide(
        prs,
        "Lab 2: Claude Code loads the same skill from lab/.claude/skills/ - "
        "watch it happen in stream-json",
        ("What you type, from the lab/ folder", [
            "claude --version -> 2.1.278 (Claude Code); claude auth status "
            "-> \"loggedIn\": true (Claude Code does not read the repository "
            ".env)",
            "The project: CLAUDE.md, .claude/skills/repo-answers/SKILL.md, "
            ".claude/skills/explain-term/SKILL.md, docs/ with three files",
            "claude -p \"Which two Claude models does this module use, and "
            "for which roles?\" --max-turns 3 --output-format stream-json "
            "--verbose",
            "Interactively: /explain-term compaction invokes a skill by "
            "name; /skills and /context show what each one costs",
        ]),
        ("What you see (observed on 30 Sep 2026)", [
            "system/init lists both project skills by name: the level-1 "
            "catalog",
            "First action: the Skill tool with {\"skill\": \"repo-answers\"} "
            "-> 'Launching skill: repo-answers' - the level-2 load, Claude "
            "Code's load_skill",
            "Then the procedure: grep over docs/ through Bash, an answer "
            "naming claude-opus-5 and claude-sonnet-5, two Source: lines",
            "result: num_turns 4, total_cost_usd 0.4069 on claude-fable-5-1 "
            "with about 82,000 cached tokens of plugins; --model sonnet "
            "costs cents",
            "Nothing forced the load: the description matched, so it opened "
            "the manual",
        ]),
        kicker="Lab 2 - skills in Claude Code",
        note="Lab guide: lab/02-lab-claude-code-skills-and-mcp.md, parts 0 to "
             "2. Every claude -p run costs real money on the student's own "
             "login; the recorded runs cost 0.04 to 0.41 USD each.",
    )
    _panel_font(s, size=12)
    notes(s, "Switch from the notebook to the terminal. The lab folder is a "
             "complete Claude Code project: an instruction file, two skills, "
             "three documents. The json output format hides the steps, so "
             "the lab uses stream-json with verbose to see one event per "
             "line, the way run_agent printed the loop. The first event the "
             "model produced was the Skill tool call for repo-answers, which "
             "is exactly the load_skill call of section 4.3; then it followed "
             "the procedure and cited two files. The 0.41 USD is honest and "
             "worth a minute: the author's default model was the most "
             "expensive tier and the machine carried many plugins whose tool "
             "descriptions sat in the context; a fresh install on sonnet "
             "pays cents. Class question: what in the description of "
             "repo-answers made this question match it?")

    # 19. Lab: MCP
    s = ds.two_col_slide(
        prs,
        "Lab 2: one command adds an MCP server; approval and permissions "
        "still gate every call",
        ("What you type", [
            "claude mcp add -s project filesystem -- npx -y "
            "@modelcontextprotocol/server-filesystem docs -> writes "
            ".mcp.json (type stdio; only docs/ is exposed)",
            "claude mcp list -> 'filesystem: ... Pending approval (run "
            "claude to approve)': a project server never starts until you "
            "approve it once",
            "claude -p \"Using only the filesystem MCP server's tools, list "
            "the docs folder and tell me the first heading of each file.\" "
            "--max-turns 4 --output-format stream-json --verbose "
            "--mcp-config .mcp.json --strict-mcp-config --model sonnet",
            "Second run adds --allowedTools mcp__filesystem__list_directory "
            "mcp__filesystem__read_text_file",
        ]),
        ("What you see (observed, claude-sonnet-5)", [
            "init: mcp_servers filesystem connected; 14 new tools named "
            "mcp__filesystem__<tool>, schemas fetched with ToolSearch",
            "Run 1: list_directory denied twice ('you haven't granted it "
            "yet'); the model stopped and asked - num_turns 4, 0.1132 USD",
            "Run 2: the listing came through the plug (faq.md, glossary.md, "
            "module-overview.md); read_multiple_files denied, read_text_file "
            "with head 5 allowed",
            "--max-turns 4 cut run 2 one turn before the answer: "
            "error_max_turns, num_turns 5, 0.0406 USD; --max-turns 6 lets "
            "it finish",
            "In plain words: the trailer hitch fits, and the brakes still "
            "work on whatever is towed",
        ]),
        kicker="Lab 2 - MCP in Claude Code",
        note="Lab guide parts 3 and 4. Reference server: "
             "@modelcontextprotocol/server-filesystem. Undo with claude mcp "
             "remove filesystem -s project.",
    )
    _panel_font(s, size=11.5)
    notes(s, "One command writes a JSON entry, and the server's tools appear "
             "next to the built-in ones with the mcp__server__tool naming. "
             "Three harness behaviours show themselves in the recorded runs. "
             "Project servers wait for a one-time approval, because a "
             ".mcp.json arrives with a clone and could start anything. Tool "
             "calls wait for permission: in print mode nobody answers, so "
             "the first run was denied and the model asked instead of "
             "guessing. And max-turns stopped the second run one turn before "
             "the final sentence, the same brake as the gated run in the "
             "notebook. Class question: which of the fourteen filesystem "
             "tools would you never pre-approve, and why?")

    # 20. Lab: read the bill
    s = ds.table_slide(
        prs,
        "Lab 2: read the bill from the JSON result (total_cost_usd, usage, "
        "modelUsage) or type /usage",
        ["Run", "Model", "Turns", "Input tokens", "Cache write tokens",
         "Cache read tokens", "Output tokens", "Cost USD"],
        [
            ["JSON key", "modelUsage key", "num_turns", "input_tokens",
             "cache_creation_input_tokens", "cache_read_input_tokens",
             "output_tokens", "total_cost_usd"],
            ["Part 2, skill question", "claude-fable-5-1", "4", "37",
             "29,201", "52,521", "567", "0.4069"],
            ["Part 4, first MCP run (denied)", "claude-sonnet-5", "4", "8",
             "34,451", "101,472", "672", "0.1132"],
            ["Part 4, second MCP run (approved)", "claude-sonnet-5", "5", "8",
             "1,406", "135,182", "1,006", "0.0406"],
        ],
        kicker="Lab 2 - the bill",
        note="Claude Code 2.1.278: the result event carries total_cost_usd, "
             "usage and modelUsage (per model, with costUSD), plus num_turns "
             "and duration_ms; there is no cost object. In a session type "
             "/usage. Row 3 read almost everything from cache, at a tenth of "
             "the input price.",
        col_widths=[1.75, 1.6, 0.9, 1.05, 2.2, 2.05, 1.15, 1.35],
    )
    _table_font(s, size=11.5, header_size=11.5)
    _mono_columns(s, [1], size=10)
    _mono_row(s, 1, size=8)
    notes(s, "Two places show what a session cost. Interactively, /usage "
             "prints a session block with the total at list price and one "
             "line per model; some documents still call it /cost, but on "
             "2.1.278 the listed command is /usage. Non-interactively, every "
             "json and stream-json result carries the same numbers, and a "
             "script pulls them with jq -r '.total_cost_usd'. Read row three "
             "against row two: almost the whole prompt came from the cache "
             "because the second run repeated the first run's prefix within "
             "five minutes; that is the caching the notebook's cost_usd "
             "function priced at one tenth. Class question: which of the "
             "four token counts would you watch to catch a runaway agent, "
             "and why not the cost alone?")

    # 21. Close
    s = ds.close_slide(
        prs,
        "You now know the four pieces the model sees - next session you build "
        "the loop around them",
        [
            "Model: one request, one response; read capabilities first, "
            "choose by capability, cost and latency",
            "Context is a budget: compaction cut the next prompt by 72%; "
            "notes outside the window outlive a session",
            "Instruction files: short and human-written help; when "
            "everything is important, nothing is",
            "A tool is its description: the vague one paid 2 extra calls; "
            "errors and gates belong to the interface",
            "Skills load in three levels: 152 tokens of catalog for two "
            "skills, 580 of bodies on demand",
            "MCP is the plug: claude mcp add, approval, permissions; read "
            "the bill via total_cost_usd and /usage",
            "Practice now: notebook 02 with your key in .env, then lab 2 "
            "from lab/; exercises before solutions",
        ],
        course=course,
    )
    notes(s, "Recap the seven lines and point at notebook 02's exercises: "
             "write a skill, tune the vague description, make an error "
             "message helpful, count what a long tool result costs. Then the "
             "lab's three tries: a third skill, a trap question, the MCP run "
             "with max-turns 6. Next session: the harness package, hooks and "
             "permissions, the five workflow patterns, and evals. Class "
             "question to close: if you could add one tool and one skill to "
             "notebook 02's agent, which would they be?")

    return prs


if __name__ == "__main__":
    make_model_interface_fig()
    make_context_budget_fig()
    make_mcp_fig()
    make_skills_levels_fig()
    make_session_growth_fig()
    make_compaction_fig()
    prs = slides()
    out = "../m5-session-2-models-context-tools-and-skills.pptx"
    ds.save_deck(prs, out, "M5 Session 2 - Models, Context, Tools and Skills", author="M5 Harness Engineering course")
    print("Slides:", len(prs.slides._sldIdLst))
    print("Saved:", os.path.abspath(out))
