"""Build deck: M5 Session 2 - Models, Context, Tools and Skills.

Theory from the Module 5 course brief (model interface and tiers, context as
a budget, tool design rules, MCP, skills and progressive disclosure);
practice numbers from notebook 02 as recorded in the brief's appendix
(compaction 8 -> 16 -> 24 -> 11 -> 19; skills catalog 98 vs 321 tokens;
the exact permission denial). Every fact is attributed on its slide.
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


# ------------------------------------------------------------------ figures
def make_model_interface_fig():
    """One interface: context in, next message out; three models plug in.
    Synthetic - captioned as illustration on the slide."""
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
    ax.text(5.15, y0 + 0.6, "complete(system,\nmessages, tools)", ha="center",
            va="center", color=pal["sky"], fontsize=9.5, family="monospace",
            linespacing=1.3)
    ax.add_patch(FancyBboxPatch((7.4, y0), 2.7, h, boxstyle="round,pad=0.05",
                                facecolor=pal["panel"], edgecolor=pal["sky"],
                                lw=1.5))
    ax.text(8.75, y0 + h - 0.32, "NEXT MESSAGE OUT", ha="center",
            color=pal["navy"], fontsize=11, fontweight="bold")
    ax.text(8.75, y0 + 0.62, "text for the user,\nor a tool call\nwith JSON "
            "arguments", ha="center", va="center", color=pal["gray"],
            fontsize=9.2, linespacing=1.3)
    for x0, x1 in ((2.95, 3.65), (6.65, 7.35)):
        ax.add_patch(FancyArrowPatch((x0, y0 + h / 2), (x1, y0 + h / 2),
                                     arrowstyle="-|>", mutation_scale=18,
                                     color=pal["navy"], lw=2))
    # the plugs
    plugs = [("ScriptedModel", "deterministic stand-in,\nno API key"),
             ("AnthropicModel", "claude-opus-5 via\nproviders.connect"),
             ("OpenAIModel", "gpt-5 via\nproviders.connect")]
    pw = 2.55
    for i, (name, sub) in enumerate(plugs):
        x = 1.2 + i * 2.9
        ax.add_patch(FancyBboxPatch((x, 0.35), pw, 1.25,
                                    boxstyle="round,pad=0.05",
                                    facecolor="white", edgecolor=pal["blue"],
                                    lw=1.5, ls="-" if i == 0 else "--"))
        ax.text(x + pw / 2, 1.28, name, ha="center", color=pal["navy"],
                fontsize=10.5, fontweight="bold", family="monospace")
        ax.text(x + pw / 2, 0.75, sub, ha="center", va="center",
                color=pal["gray"], fontsize=8.6, linespacing=1.25)
        ax.add_patch(FancyArrowPatch((x + pw / 2, 1.65), (5.15, y0 - 0.08),
                                     arrowstyle="-|>", mutation_scale=13,
                                     color=pal["sky"], lw=1.4,
                                     connectionstyle="arc3,rad=0"))
    ax.text(5.15, 2.55, "same slot, any engine", ha="center",
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
    on the course's three sample skills (brief appendix)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    levels = [
        (0.3, 3.75, 5.6, 1.15, "LEVEL 1 - the catalog", "name + description "
         "of every skill,\nalways in the context", "98 tokens for 3 skills",
         pal["blue"], "white", pal["sky"]),
        (0.3, 2.2, 7.0, 1.15, "LEVEL 2 - the body", "the SKILL.md "
         "instructions,\nloaded when the task matches", "321 tokens for all "
         "3 bodies (3.3x)", pal["sky"], pal["navy"], pal["navy"]),
        (0.3, 0.65, 8.4, 1.15, "LEVEL 3 - the resources", "scripts, "
         "checklists, templates,\nopened only during execution",
         "checklist.md, template.md", pal["panel"], pal["navy"], pal["navy"]),
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
    ax.text(0.3, 5.05, "our library: cite-sources, safe-calculations, "
            "summarize-brief", fontsize=9.5, color=pal["gray"], va="center")
    ax.set_xlim(0, 10.2)
    ax.set_ylim(0.3, 5.3)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s2_skills_levels.png")
    plt.close(fig)


def make_compaction_fig():
    """Messages in the history after each of five questions with a
    2,500-token budget (brief appendix): 8, 16, 24, then compaction to 11,
    then 19."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = ["after Q1", "after Q2", "after Q3", "after Q4\n(compacted)",
              "after Q5"]
    vals = [8, 16, 24, 11, 19]
    colors = [pal["blue"], pal["blue"], pal["blue"], pal["navy"], pal["blue"]]
    xs = range(len(vals))
    ax.bar(xs, vals, color=colors, width=0.62)
    for x, v in zip(xs, vals):
        ax.text(x, v + 0.5, str(v), ha="center", va="bottom", fontsize=11.5,
                fontweight="bold", color=pal["ink"])
    ax.annotate("during question 4 the budget check fires:\n24 messages "
                "fold into 11 (task + summary note + last turns)",
                xy=(3.0, 13.4), xytext=(2.9, 26.2), fontsize=9.2,
                color=pal["navy"], ha="center", linespacing=1.3,
                arrowprops=dict(arrowstyle="-|>", color=pal["navy"], lw=1.4))
    ax.text(0.5, 26.6, "every answer stays cited,\nbefore and after",
            ha="center", va="center", fontsize=9.5, color=pal["blue"],
            fontweight="bold", linespacing=1.3)
    ax.set_xticks(list(xs))
    ax.set_xticklabels(labels, fontsize=10)
    ax.set_ylim(0, 30)
    ax.set_ylabel("messages in the history (bar height = count)")
    ax.set_title("A five-question session with a 2,500-token budget")
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
        "only when needed. First the rules, then notebook 02.",
        course=course,
    )
    notes(s, "Session 2 opens the first four pieces of the harness: the "
             "model, the context, the tools and the skills. These are the "
             "pieces the model sees; Session 3 builds the loop and the checks "
             "around them. Class question to open: what did the harness in "
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
            "How to read it: the blue box is the whole contract; anything "
            "that fills it is a model",
            "In plain words: the model is the text-in, text-out engine",
            "It never runs a tool itself; it only asks for one, by name, "
            "with JSON arguments",
            "The library's ScriptedModel fills the slot deterministically - "
            "no key, same output every run",
            "A real model plugs into the same slot: connect('anthropic') "
            "asks for a key with getpass, never stores it",
            "The harness does not change when the engine does - that is the "
            "point of the interface",
        ],
        caption="Illustration. Interface from the harness library "
                "(harness.models.Model); adapters AnthropicModel and "
                "OpenAIModel in harness.providers.",
    )
    notes(s, "Start with the contract, not the vendor. A model takes the "
             "system prompt, the messages so far and the tool schemas, and "
             "returns one message: text, or a request to call a tool. That is "
             "all a harness needs to know. Our ScriptedModel implements the "
             "same contract with a hand-written policy, so the notebooks run "
             "without a key and give the same answer every time. Class "
             "question: which of the three inputs would you expect to grow "
             "the most during a long task?")

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
             "labels the input, the harness picks the path. Class question: "
             "which steps of notebook 01's harness would you hand to the "
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
             "notebook 01's trace, which segment of this window was the "
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
             "guardrail until something outside the model checks it. Class "
             "question: what are the three lines you would put in your "
             "project's instruction file?")

    # 7. Tools are prompt engineering for machines
    s = ds.two_col_slide(
        prs,
        "Tool design is prompt engineering for machines",
        ("Anthropic's rules, Sep 2025", [
            "In plain words: a tool is a function the model asks for by "
            "name; the harness runs it",
            "The description says when to use the tool and what it returns",
            "Namespace tools by system: search_docs, read_doc, not 'search' "
            "and 'get'",
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
             "description 'search: searches things' in one sentence?")

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
             "once. Class question: notebook 01's harness has three tools - "
             "which one would you remove, and what would break?")

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
            "One protocol: list the tools, call a tool, get the result as text",
        ],
        caption="Illustration. Dates: Anthropic, Introducing the Model Context "
                "Protocol, 25 Nov 2024; OpenAI Agents SDK release notes, "
                "26 Mar 2025.",
    )
    notes(s, "Function calling gave us structured tool calls in 2023, but "
             "every vendor and every tool needed its own adapter. MCP "
             "standardizes the socket: a server lists its tools, a client "
             "calls them, results come back as text. When the second big "
             "vendor adopted it four months later, it became the plug. Class "
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
            "numbers from our three skills",
            "In plain words: a skill is a folder with a SKILL.md and optional "
            "scripts; read the description first",
            "Level 1: name + description of every skill, 98 tokens for three",
            "Level 2: the body of the one that matches, 321 tokens if all "
            "three were loaded (3.3x)",
            "Level 3: checklist.md, template.md - opened only while executing",
            "Skills teach procedures; tools give abilities; prompts give the "
            "task",
        ],
        caption="Token counts from the course library (notebook 02). Anthropic, "
                "Equipping agents for the real world with Agent Skills, "
                "16 Oct 2025; open standard 18 Dec 2025, 40+ platforms.",
    )
    notes(s, "Progressive disclosure is the context-budget idea applied to "
             "instructions. The agent always sees the catalog, a few tens of "
             "tokens per skill; it opens the body when the task matches, and "
             "the resources only while executing. Skills became an open "
             "standard in December 2025 and are supported by more than forty "
             "platforms. Class question: which of your own recurring "
             "procedures would you write as a SKILL.md first?")

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
             "An ability: search, read, calculate, check",
             "A procedure: which tools, in which order, with which checks"],
            ["When it loads", "Every call", "Schema on every call; result "
             "when called", "Description always; body when the task matches; "
             "resources during execution"],
            ["In our library", "'When did Anthropic open-source MCP?'",
             "search_docs, read_doc, check_citation, calculator",
             "cite-sources, safe-calculations, summarize-brief"],
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
             "with which checks. Class question: 'always verify a citation "
             "before answering' - prompt, tool or skill?")

    # 12. Part 2 divider
    s = ds.section_slide(
        prs, "02",
        "Part 2 - The practice: notebook 02",
        "Compaction under a small budget, a tool schema built from a "
        "docstring, a vague tool against a good one, a denied permission, "
        "and the skills catalog.",
    )
    notes(s, "Open notebook 02 in Colab; same bootstrap cell, no key. Five "
             "printed results follow, one per slide, all deterministic. Class "
             "question: which of the four pieces do you expect to be the "
             "easiest to get wrong in your own project?")

    # 13. The compaction session
    s = ds.image_slide(
        prs,
        "Under a 2,500-token budget the history grows, folds to 11 messages, "
        "and keeps working",
        f"{FIGS}/s2_compaction.png",
        kicker="Notebook 02 - context",
        bullets=[
            "How to read it: bar height = messages in the history after each "
            "question; navy = the compaction",
            "Five questions in one session: 8, 16, 24 messages - then the "
            "budget check fires",
            "Compaction fires during question 4: '22 earlier messages "
            "summarized' into one note; the history ends at 11",
            "The session continues: 19 messages after question five, every "
            "answer still cited",
            "In plain words: compaction is summarizing the old part of the "
            "conversation to make room",
            "ContextWindow(budget_tokens=2500) in the library; the default "
            "budget is 6,000",
        ],
        caption="Counts from notebook 02 (deterministic ScriptedModel). "
                "Technique: Anthropic, Effective context engineering for AI "
                "agents, 29 Sep 2025.",
    )
    notes(s, "Run this cell live: the notebook prints the message count after "
             "each question and the compaction note itself. Point at the "
             "note: it names which tools ran and what came back, so the model "
             "can still answer follow-ups. Class question: what would you lose "
             "if the compaction summary were just 'earlier conversation "
             "omitted'?")

    # 14. The tool schema from a docstring
    s = ds.table_slide(
        prs,
        "One decorator turns a docstring into the schema the model reads",
        ["What you write (Python)", "What the model sees (JSON schema)"],
        [
            ["@tool", '"name": "search_docs"'],
            ["def search_docs(query: str, k: int = 3) -> str:",
             '"parameters": {"type": "object", "required": ["query"], ...'],
            ['    """Search the course library for documents about a '
             'topic. Returns the best matches as JSON ...',
             '"description": "Search the course library for documents about '
             'a topic. Returns the best matches as JSON ..."'],
            ["    query: the key terms to look for, a few words, no full "
             "sentences",
             '"query": {"type": "string", "description": "the key terms to '
             'look for, a few words, no full sentences"}'],
            ["    k: how many results to return, default 3",
             '"k": {"type": "integer", "default": 3, "description": "how many '
             'results to return, default 3"}'],
        ],
        kicker="Notebook 02 - tools",
        note="How to read it: each line on the left becomes the field on the "
             "right. The first docstring paragraph is the description; "
             "'argument: explanation' lines describe the arguments. From "
             "harness.tools.tool.",
        col_widths=[1.0, 1.0],
    )
    _mono_columns(s, [0, 1], size=10)
    notes(s, "The @tool decorator reads the signature for names and types and "
             "the docstring for the words. Nothing on the right is written by "
             "hand. This is why the docstring deserves the same care as a "
             "prompt: the model reads exactly this. Class question: what "
             "changes in the schema if you remove the default value of k?")

    # 15. Vague tool vs good tool
    s = ds.two_col_slide(
        prs,
        "A vague tool and a good tool do the same work - the model only "
        "succeeds with one",
        ("The vague tool", [
            "name: search - description: 'Searches.' (2 tokens)",
            "One argument, q, with no explanation",
            "Returns every matching document in full: thousands of tokens",
            "On failure: an empty string, or a stack trace",
            "The model guesses when to call it, what to pass, and what "
            "came back",
        ]),
        ("The good tool", [
            "name: search_docs - a 42-token description says what it "
            "searches and what it returns",
            "query: 'a few words, no full sentences'; k: 'how many results, "
            "default 3'",
            "Returns the top 3 as JSON: id, title, score, snippet - and says "
            "to call read_doc next",
            "On failure: a message that names the problem and what to try",
            "The model calls it at the right time, with the right words, and "
            "knows the next step",
        ]),
        kicker="Notebook 02 - tools",
        note="Rules: Anthropic, Writing effective tools for agents, Sep 2025. "
             "The good tool is the library's search_docs; the vague one is "
             "notebook 02's counter-example.",
    )
    notes(s, "Notebook 02 runs both against the ScriptedModel and prints the "
             "two traces side by side. The vague tool wastes the budget on "
             "whole documents and gives the model nothing to decide with. "
             "Class question: which of the four differences would you fix "
             "first if you could only fix one?")

    # 16. Permission denial
    s = ds.two_col_slide(
        prs,
        "A permission check runs outside the model - the default says no to "
        "'danger'",
        ("What the notebook prints", [
            "Denied: 'run_python' has risk level 'danger' and is not "
            "permitted here.",
            "Every tool carries a risk level: read, write or danger; "
            "run_python is danger",
            "The default permission denies danger; the denial goes back to "
            "the model as a tool result",
            "The loop continues - the model can explain, or try another tool",
            "permission=allow_all runs the same call; that is a decision, "
            "not a default",
        ]),
        ("Why it matters", [
            "In plain words: a guardrail is a check that runs outside the "
            "model",
            "OpenAI, A practical guide to building agents, Apr 2025: tool "
            "safeguards with risk ratings",
            "93% of permission prompts get approved - the approval paradox "
            "(Marmelab, Sep 2026)",
            "So the default must be safe without a human clicking",
            "Session 3 builds hooks, risk levels and approval gates in full",
        ]),
        kicker="Notebook 02 - permissions",
        note="Message text from the harness library (harness.agent), printed "
             "by notebook 02. Risk levels: read, write, danger "
             "(harness.tools.RISK_LEVELS).",
    )
    notes(s, "Read the message aloud: it names the tool, the risk level and "
             "the decision, and it goes back to the model so the loop can "
             "continue. Then flip permission to allow_all and show the same "
             "call running. The approval paradox is the reason defaults "
             "matter: when a human is asked, they say yes 93% of the time. "
             "Class question: which tools in your own projects deserve the "
             "'danger' label?")

    # 17. The skills catalog
    s = ds.table_slide(
        prs,
        "The skills catalog: three descriptions the agent always sees, three "
        "bodies it opens on demand",
        ["Skill", "Level 1 - description, always in context",
         "Level 3 - resource opened during execution"],
        [
            ["cite-sources", "Answer factual questions from the course "
             "library with a [source: id] citation, verified with "
             "check_citation before replying.", "checklist.md"],
            ["safe-calculations", "Do every calculation with the calculator "
             "tool, never in your head, and show the exact expression you "
             "evaluated.", "(none)"],
            ["summarize-brief", "Turn one library document into a five-line "
             "brief with exactly one concrete number or date per line.",
             "template.md"],
        ],
        kicker="Notebook 02 - skills",
        note="Catalog (level 1) = 98 tokens; all three bodies (level 2) = "
             "321 tokens, 3.3x; a run that loads a skill costs ~1,800 tokens "
             "more than a plain run. Notebook 02; Anthropic, Agent Skills, "
             "16 Oct 2025.",
        col_widths=[1.3, 4.2, 1.9],
    )
    _mono_columns(s, [0], size=11)
    notes(s, "This is exactly what the agent sees at startup: three lines, 98 "
             "tokens. When a question asks for a fact, the cite-sources "
             "description matches and the body loads - the five numbered "
             "steps of search, read, draft, check, reply. Class question: "
             "which of the three descriptions would you rewrite, and why?")

    # 18. Swapping the engine
    s = ds.two_col_slide(
        prs,
        "The last section swaps the engine: same harness, a real model, "
        "no key stored",
        ("ScriptedModel - the stand-in", [
            "A hand-written policy decides the next message from what it "
            "sees",
            "Deterministic: same input, same output, every run, in CI and "
            "in Colab",
            "Shows the mechanics of the loop without an account or a key",
            "Its limits are the point: it knows only what the policy encodes",
        ]),
        ("A real model - optional", [
            "RUN_REAL = False by default; set True to try it",
            "connect('anthropic') or connect('openai') asks for the key with "
            "getpass",
            "The key lives in memory for the session and is never written "
            "anywhere",
            "Everything else in the notebook stays the same: tools, budget, "
            "permissions, skills",
        ]),
        kicker="Notebook 02 - the optional real model",
        note="Repository rule: no secrets ever, in code, outputs or metadata. "
             "Default models: claude-opus-5 and gpt-5 (harness.providers).",
    )
    notes(s, "End of the notebook, and the payoff of the interface slide: the "
             "harness does not change when the engine does. If a student has "
             "a key, they paste it into a hidden prompt and run the same "
             "cells. Repeat the repository rule: no key is ever stored or "
             "committed. Class question: what would you compare between the "
             "scripted and the real run to judge the harness, not the model?")

    # 19. Close
    s = ds.close_slide(
        prs,
        "You now know the four pieces the model sees - next session you build "
        "the loop around them",
        [
            "Model: one interface, context in and next message out; route "
            "cheap models to easy steps",
            "Context is a budget: compaction, notes and sub-agents keep it "
            "under the line",
            "Instruction files: short and human-written help; when "
            "everything is important, nothing is",
            "Tools are prompt engineering for machines; fewer tools win; MCP "
            "is the plug",
            "Skills load in three levels: 98 tokens of catalog, bodies on "
            "demand, resources in execution",
            "Notebook 02: compaction 24 to 11, a schema from a docstring, a "
            "denied 'danger' tool, three skills",
            "Practice now: notebook 02 in Colab, Runtime > Run all, the "
            "exercises before the solutions",
        ],
        course=course,
    )
    notes(s, "Recap the seven lines and point at notebook 02's exercises: "
             "write a tool description, tune the budget, add a skill. Next "
             "session: the loop, hooks and permissions, the five workflow "
             "patterns, and evals. Class question to close: if you could add "
             "one tool and one skill to notebook 02's harness, which would "
             "they be?")

    return prs


if __name__ == "__main__":
    make_model_interface_fig()
    make_context_budget_fig()
    make_mcp_fig()
    make_skills_levels_fig()
    make_compaction_fig()
    prs = slides()
    out = "../m5-session-2-models-context-tools-and-skills.pptx"
    ds.save_deck(prs, out, "M5 Session 2 - Models, Context, Tools and Skills", author="M5 Harness Engineering course")
    print("Slides:", len(prs.slides._sldIdLst))
    print("Saved:", os.path.abspath(out))
