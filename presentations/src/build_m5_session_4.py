"""Build deck: M5 Session 4 - Sub-agents, Teams and the Discipline.

Theory: why isolate context, the research system, sub-agents vs teams vs
handoffs, orchestration as code vs model decision, failure modes, the
discipline of harness engineering, the future.
Practice: notebook 04 (lead vs sub-agents vs solo, the team board, the
handoff, the runaway loop, the eight pieces students built).
Practice numbers come from the M5 course brief appendix (deterministic
ScriptedModel runs); the runaway-loop bars are one run of the course library
with a policy that never stops and max_turns=8. Every external fact is
attributed on the slide.
"""
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

import deck_style as ds

FIGS = "/tmp/deck-workshop/figs-m5"
os.makedirs(FIGS, exist_ok=True)
pal = ds.mpl_theme()
COURSE = "Harness Engineering - Module 5"
FOOTER = "M5 Session 4 - Sub-agents, Teams and the Discipline"


def notes(slide, text):
    """Speaker notes: a plain-text talk track plus one class question."""
    slide.notes_slide.notes_text_frame.text = text


# ---------------------------------------------------------------- helpers
def box(ax, x, y, w, h, head, sub="", fc=None, ec=None, hc=None, sc=None,
        hs=11, ss=8.8, ls="-", lw=1.5):
    fc = fc or pal["panel"]
    ec = ec or pal["blue"]
    hc = hc or pal["navy"]
    sc = sc or pal["gray"]
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.04",
                                facecolor=fc, edgecolor=ec, lw=lw,
                                linestyle=ls))
    if sub:
        ax.text(x + w / 2, y + h * 0.68, head, ha="center", va="center",
                color=hc, fontweight="bold", fontsize=hs)
        ax.text(x + w / 2, y + h * 0.30, sub, ha="center", va="center",
                color=sc, fontsize=ss, linespacing=1.25)
    else:
        ax.text(x + w / 2, y + h / 2, head, ha="center", va="center",
                color=hc, fontweight="bold", fontsize=hs)


def arrow(ax, p0, p1, color=None, lw=1.6, rad=0.0, ms=16, ls="-"):
    ax.add_patch(FancyArrowPatch(p0, p1, arrowstyle="-|>", mutation_scale=ms,
                                 color=color or pal["blue"], lw=lw,
                                 linestyle=ls,
                                 connectionstyle=f"arc3,rad={rad}"))


# ---------------------------------------------------------------- figures
def make_isolate_fig():
    """Lead context small; sub-agents each in their own window, returning
    short summaries (Anthropic, context engineering, Sep 2025)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    box(ax, 0.3, 2.25, 2.5, 1.6, "LEAD AGENT",
        "own context stays small:\nthe plan + three summaries",
        fc=pal["blue"], ec=pal["blue"], hc="white", sc=pal["sky"])
    ys = [4.3, 2.25, 0.2]
    for i, y in enumerate(ys, start=1):
        box(ax, 5.3, y, 4.5, 1.6, f"SUB-AGENT {i}",
            "own context window: tens of\nthousands of tokens of search,\n"
            "reading and checking", ss=8.4)
        arrow(ax, (2.8, 3.45), (5.3, y + 1.1), color=pal["gray"], lw=1.3,
              rad=-0.1)
        arrow(ax, (5.3, y + 0.5), (2.8, 2.7), color=pal["blue"], lw=1.8,
              rad=-0.1)
    ax.text(0.3, 0.95, "gray arrow: the brief goes out", color=pal["gray"],
            fontsize=8.8)
    ax.text(0.3, 0.55, "blue arrow: a 1,000-2,000 token\nsummary comes back",
            color=pal["blue"], fontsize=8.8, fontweight="bold", va="top")
    ax.text(1.55, 1.95, "the details never\nenter this window", ha="center",
            va="top", color=pal["gray"], fontsize=8.8, style="italic")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.1)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s4_isolate.png")
    plt.close(fig)


def make_shapes_fig():
    """Three shapes of multi-agent work: hierarchy, flat team, handoff."""
    fig, axes = plt.subplots(1, 3, figsize=(11.5, 5))
    # sub-agents: hierarchy
    ax = axes[0]
    box(ax, 2.2, 3.7, 1.6, 0.7, "lead", fc=pal["blue"], ec=pal["blue"],
        hc="white", hs=10)
    for x in (0.3, 2.2, 4.1):
        box(ax, x, 1.5, 1.6, 0.7, "sub-agent", hs=9.5)
        arrow(ax, (3.0, 3.7), (x + 0.65, 2.2), color=pal["gray"], lw=1.3,
              ms=11)
        arrow(ax, (x + 0.95, 2.2), (3.0, 3.7), color=pal["blue"], lw=1.5,
              ms=11)
    ax.plot([1.95, 2.15], [1.85, 1.85], color=pal["gray"], lw=1, ls="--")
    ax.plot([3.85, 4.05], [1.85, 1.85], color=pal["gray"], lw=1, ls="--")
    for x in (2.05, 3.95):
        ax.text(x, 1.85, "x", ha="center", va="center", color=pal["navy"],
                fontsize=11, fontweight="bold")
    ax.text(3.0, 0.75, "briefs go down, reports go up;\nno lateral talk, "
            "results never mix", ha="center", va="center", color=pal["gray"],
            fontsize=9.2)
    ax.set_title("Sub-agents: a hierarchy", fontsize=12)
    # agent teams: flat with a shared list
    ax = axes[1]
    box(ax, 1.9, 2.05, 2.2, 0.9, "SHARED\nTASK LIST", fc=pal["navy"],
        ec=pal["navy"], hc="white", hs=9)
    box(ax, 2.2, 3.85, 1.6, 0.7, "lead", fc=pal["blue"], ec=pal["blue"],
        hc="white", hs=10)
    mates = [(0.15, 2.15), (4.25, 2.15), (2.2, 0.45)]
    for x, y in mates:
        box(ax, x, y, 1.6, 0.7, "teammate", hs=9.5)
    arrow(ax, (3.0, 3.85), (3.0, 2.95), color=pal["blue"], lw=1.4, ms=11)
    arrow(ax, (1.75, 2.5), (1.9, 2.5), color=pal["blue"], lw=1.4, ms=11)
    arrow(ax, (4.25, 2.5), (4.1, 2.5), color=pal["blue"], lw=1.4, ms=11)
    arrow(ax, (3.0, 1.15), (3.0, 2.05), color=pal["blue"], lw=1.4, ms=11)
    arrow(ax, (1.0, 2.15), (2.6, 1.15), color=pal["gray"], lw=1.1, ms=9,
          rad=0.3, ls="--")
    arrow(ax, (3.4, 1.15), (5.0, 2.15), color=pal["gray"], lw=1.1, ms=9,
          rad=0.3, ls="--")
    ax.text(3.0, -0.15, "everyone claims from one list;\nteammates message "
            "each other (dashed)", ha="center", va="center", color=pal["gray"],
            fontsize=9.2)
    ax.set_title("Agent teams: flat, one list", fontsize=12)
    # handoffs
    ax = axes[2]
    box(ax, 0.2, 2.15, 1.6, 0.9, "agent A", "triage", hs=9.5, ss=8,
        fc="white", ec=pal["gray"], hc=pal["gray"])
    box(ax, 2.2, 2.15, 1.6, 0.9, "agent B", "specialist", hs=9.5, ss=8,
        fc=pal["blue"], ec=pal["blue"], hc="white", sc=pal["sky"])
    box(ax, 4.2, 2.15, 1.6, 0.9, "agent C", "if needed", hs=9.5, ss=8,
        fc="white", ec=pal["gray"], hc=pal["gray"], ls="--")
    arrow(ax, (1.8, 2.6), (2.2, 2.6), color=pal["navy"], lw=1.8, ms=13)
    arrow(ax, (3.8, 2.6), (4.2, 2.6), color=pal["gray"], lw=1.3, ms=11,
          ls="--")
    ax.text(2.0, 3.35, "the whole\nconversation", ha="center", va="center",
            color=pal["navy"], fontsize=8.6)
    ax.text(3.0, 0.75, "control transfers once, one way;\nA steps back, "
            "B inherits the history", ha="center", va="center",
            color=pal["gray"], fontsize=9.2)
    ax.set_title("Handoffs: transfer of control", fontsize=12)
    for ax in axes:
        ax.set_xlim(0, 6)
        ax.set_ylim(-0.5, 4.9)
        ax.axis("off")
    fig.tight_layout(w_pad=1.0)
    fig.savefig(f"{FIGS}/s4_shapes.png")
    plt.close(fig)


def make_signposts_fig():
    """Four signposts for where the field is going (all dated and sourced)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    cards = [
        (0.3, 3.2, "AGENT-FIRST REPOSITORIES", "~1M lines",
         "of production code in five months,\nzero written by hand\n"
         "OpenAI, Feb 2026"),
        (5.2, 3.2, "SKILLS AS AN OPEN STANDARD", "40+ platforms",
         "load the same SKILL.md folder\nAnthropic, Dec 2025, adopted 2026"),
        (0.3, 0.3, "A YOUNG, CROWDED FIELD", "21,500 repos",
         "'agent harness' repositories created\nin 2026; median age 8.7 months\n"
         "Marmelab, Sep 2026"),
        (5.2, 0.3, "A NAMED DISCIPLINE", "2026",
         "named in February (OpenAI), studied\nin July: eleven harnesses, "
         "source code\nBarbaste et al., arXiv 2609.00006"),
    ]
    for x, y, head, big, sub in cards:
        ax.add_patch(FancyBboxPatch((x, y), 4.5, 2.5, boxstyle="round,pad=0.04",
                                    facecolor=pal["panel"], edgecolor=pal["sky"],
                                    lw=1.2))
        ax.text(x + 0.25, y + 2.15, head, color=pal["blue"], fontweight="bold",
                fontsize=9.5, va="center")
        ax.text(x + 0.25, y + 1.45, big, color=pal["navy"], fontweight="bold",
                fontsize=20, va="center")
        ax.text(x + 0.25, y + 0.55, sub, color=pal["gray"], fontsize=8.6,
                va="center", linespacing=1.3)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s4_signposts.png")
    plt.close(fig)


def make_lead_context_fig():
    """Where the tokens live: lead's window vs solo's window vs the work
    done inside the sub-agents (notebook 04)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = ["Inside the 3 sub-agents:\ntokens spent, never in the lead",
              "Solo agent: final context\n(answered part one only)",
              "Lead agent: final context\n(3 sub-agents did the work)"]
    vals = [5800, 800, 485]
    texts = ["~5,800 tokens (1,904 / 1,933 / 1,988)", "~800 tokens, 8 messages",
             "~485 tokens, 6 messages"]
    colors = [pal["sky"], pal["navy"], pal["navy"]]
    ax.barh(labels, vals, color=colors, height=0.55)
    for i, (v, t) in enumerate(zip(vals, texts)):
        ax.text(v + 90, i, t, va="center", color=pal["ink"], fontsize=11.5,
                fontweight="bold")
    ax.set_xlim(0, 9200)
    ax.set_xlabel("Estimated tokens")
    ax.set_title("Where the tokens live: the lead's window stays small")
    ax.tick_params(axis="y", labelsize=10.5)
    fig.savefig(f"{FIGS}/s4_lead_context.png")
    plt.close(fig)


def make_team_board_fig():
    """The task board after the run: 6 tasks, 3 teammates, 6 messages."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.add_patch(FancyBboxPatch((0.15, 5.3), 6.05, 0.55, boxstyle="round,pad=0.02",
                                facecolor=pal["navy"], edgecolor=pal["navy"]))
    ax.text(0.35, 5.575, "TASK BOARD  -  6 tasks, 3 teammates", va="center",
            color="white", fontweight="bold", fontsize=10)
    tasks = [("#1", "t0", "MCP open-source date"),
             ("#2", "t1", "MCP adopter in March 2025"),
             ("#3", "t2", "Agent Skills introduction date"),
             ("#4", "t0", "progressive disclosure levels"),
             ("#5", "t1", "research system gain"),
             ("#6", "t2", "Vercel tool cut")]
    for i, (tid, owner, desc) in enumerate(tasks):
        y = 4.75 - i * 0.72
        ax.add_patch(FancyBboxPatch((0.15, y - 0.28), 6.05, 0.56,
                                    boxstyle="round,pad=0.02",
                                    facecolor="white" if i % 2 else pal["panel"],
                                    edgecolor=pal["sky"], lw=0.8))
        ax.text(0.35, y, tid, va="center", color=pal["navy"], fontweight="bold",
                fontsize=9.5)
        ax.add_patch(FancyBboxPatch((0.95, y - 0.17), 0.85, 0.34,
                                    boxstyle="round,pad=0.02",
                                    facecolor=pal["blue"], edgecolor=pal["blue"]))
        ax.text(1.375, y, "done", ha="center", va="center", color="white",
                fontsize=8.5, fontweight="bold")
        ax.text(2.05, y, owner, va="center", color=pal["blue"], fontsize=9.5,
                fontweight="bold")
        ax.text(2.6, y, desc, va="center", color=pal["ink"], fontsize=9.2)
    # mailbox
    ax.add_patch(FancyBboxPatch((6.5, 1.0), 3.4, 4.85, boxstyle="round,pad=0.03",
                                facecolor="white", edgecolor=pal["blue"], lw=1.3))
    ax.add_patch(FancyBboxPatch((6.5, 5.3), 3.4, 0.55, boxstyle="round,pad=0.03",
                                facecolor=pal["blue"], edgecolor=pal["blue"]))
    ax.text(6.65, 5.575, "MAILBOX -> lead: 6 messages", va="center",
            color="white", fontweight="bold", fontsize=8.8)
    mails = ["t0: Task #1 done: 25 Nov 2024 ...",
             "t1: Task #2 done: OpenAI, 26 Mar 2025 ...",
             "t2: Task #3 done: 16 Oct 2025 ...",
             "t0: Task #4 done: three levels ...",
             "t1: Task #5 done: 90.2 percent, ~15x ...",
             "t2: Task #6 done: eighty percent ..."]
    for i, m in enumerate(mails):
        ax.text(6.65, 4.75 - i * 0.62, m, va="center", color=pal["ink"],
                fontsize=7.6)
    ax.text(8.2, 1.35, "each carries a [source: ...] tag", ha="center",
            va="center", color=pal["gray"], fontsize=8, style="italic")
    ax.add_patch(FancyBboxPatch((0.15, 0.15), 9.7, 0.55, boxstyle="round,pad=0.02",
                                facecolor=pal["navy"], edgecolor=pal["navy"]))
    ax.text(5.0, 0.425, "~12,000 tokens for the three teammates, plus ~394 "
            "for the lead's final call", ha="center",
            va="center", color="white", fontsize=9.5, fontweight="bold")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.1)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s4_team_board.png")
    plt.close(fig)


def make_handoff_fig():
    """The handoff: the whole research conversation moves to the calculator."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.add_patch(FancyBboxPatch((0.2, 1.3), 3.5, 3.9, boxstyle="round,pad=0.04",
                                facecolor="white", edgecolor=pal["gray"], lw=1.3))
    ax.text(1.95, 4.85, "RESEARCH AGENT", ha="center", va="center",
            color=pal["gray"], fontweight="bold", fontsize=10.5)
    ax.text(1.95, 4.5, "steps back after the handoff", ha="center",
            va="center", color=pal["gray"], fontsize=8.4, style="italic")
    rows = ["user: the MCP question", "assistant: search_docs(...)",
            "tool: 3 matching documents", "assistant: read_doc(...)",
            "tool: the document text", "assistant: check_citation(...)",
            "tool: citation OK", "assistant: cited answer",
            "8 messages in all"]
    for i, r in enumerate(rows):
        y = 4.1 - i * 0.31
        ax.add_patch(FancyBboxPatch((0.4, y - 0.12), 3.1, 0.24,
                                    boxstyle="round,pad=0.01",
                                    facecolor=pal["panel"] if i < 8 else "white",
                                    edgecolor=pal["sky"] if i < 8 else "white",
                                    lw=0.6))
        ax.text(0.5, y, r, va="center", color=pal["ink"] if i < 8 else pal["gray"],
                fontsize=7.8, style="normal" if i < 8 else "italic")
    arrow(ax, (3.7, 3.25), (6.3, 3.25), color=pal["navy"], lw=2.2, ms=20)
    ax.text(5.0, 3.85, "handoff(calc,\nmessages, instruction)",
            ha="center", va="center", color=pal["navy"], fontsize=8.6,
            fontweight="bold", linespacing=1.3)
    ax.text(5.0, 2.7, "the whole\nconversation moves", ha="center",
            va="center", color=pal["gray"], fontsize=8.4, style="italic")
    ax.add_patch(FancyBboxPatch((6.3, 1.3), 3.5, 3.9, boxstyle="round,pad=0.04",
                                facecolor="white", edgecolor=pal["blue"], lw=1.5))
    ax.text(8.05, 4.85, "CALCULATOR AGENT", ha="center", va="center",
            color=pal["navy"], fontweight="bold", fontsize=10.5)
    ax.text(8.05, 4.5, "inherits all 8 messages, then:", ha="center",
            va="center", color=pal["gray"], fontsize=8.4, style="italic")
    rows2 = [("user: Now calculate (891-179)/891", pal["panel"], pal["ink"]),
             ("assistant: calculator('(891-179)/891')", pal["panel"], pal["ink"]),
             ("tool: 0.799102", pal["panel"], pal["ink"]),
             ("assistant: The result is 0.799102.", pal["blue"], "white")]
    for i, (r, fc, tc) in enumerate(rows2):
        y = 4.0 - i * 0.55
        ax.add_patch(FancyBboxPatch((6.45, y - 0.2), 3.2, 0.4,
                                    boxstyle="round,pad=0.02", facecolor=fc,
                                    edgecolor=pal["sky"] if fc != pal["blue"] else fc,
                                    lw=0.6))
        ax.text(6.55, y, r, va="center", color=tc, fontsize=7.8,
                fontweight="bold" if fc == pal["blue"] else "normal")
    ax.text(8.05, 1.65, "2 model calls, 1 tool call, ~1,440 tokens:\nthe "
            "inherited history is most of the bill", ha="center", va="center",
            color=pal["gray"], fontsize=8, linespacing=1.3)
    ax.text(5.0, 0.6, "(891 - 179) / 891 = 0.799102: the share of the M2 "
            "manifest left after the 179-row test split", ha="center",
            va="center", color=pal["navy"], fontsize=8.8)
    ax.set_xlim(0, 10)
    ax.set_ylim(0.2, 5.4)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s4_handoff.png")
    plt.close(fig)


def make_runaway_fig():
    """Tokens per turn for a policy that never stops; max_turns=8 ends it.
    Values from one deterministic run of the course library."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    turns = list(range(1, 7))
    tokens = [134, 288, 442, 596, 750, 904]
    ax.bar(turns, tokens, color=pal["blue"], width=0.7)
    for t, v in zip(turns, tokens):
        ax.text(t, v + 18, f"{v:,}", ha="center", color=pal["ink"], fontsize=9)
    ax.axvline(6.5, color=pal["navy"], lw=2, ls="--")
    ax.text(6.4, 1120, "max_turns = 6\nstops it here", color=pal["navy"],
            fontsize=10, fontweight="bold", va="top", ha="right")
    ax.axhline(422, color=pal["gray"], lw=1.2, ls=":")
    ax.text(7.05, 422, "~422 tokens:\nthe whole run of the\nfixed 'careful' "
            "policy\n(one search, done)", color=pal["gray"], fontsize=8.6,
            va="center", style="italic")
    ax.annotate("each turn re-sends the whole history:\n+154 tokens per turn",
                xy=(2.65, 380), xytext=(0.6, 960), color=pal["ink"], fontsize=9.5,
                arrowprops=dict(arrowstyle="-|>", color=pal["gray"], lw=1.2))
    ax.set_xticks(turns)
    ax.set_xlim(0.4, 9.2)
    ax.set_xlabel("Turn (the policy calls search_docs every time and never says done)")
    ax.set_ylabel("Context tokens the model saw on this turn")
    ax.set_ylim(0, 1150)
    ax.set_title("Six turns, ~3,114 tokens, an empty answer - then the brake")
    fig.savefig(f"{FIGS}/s4_runaway.png")
    plt.close(fig)


# ---------------------------------------------------------------- slides
def slides():
    prs = ds.new_deck()

    # 1. Title
    s = ds.title_slide(
        prs,
        "Session 4 of 4",
        "Sub-agents, Teams and the Discipline",
        "One agent runs out of context; several agents multiply the cost. "
        "This session shows how to split work between agents without losing "
        "control, where multi-agent systems fail, and what harness "
        "engineering asks of you as a discipline. Then notebook 04 runs a "
        "lead with sub-agents, a team, a handoff and a runaway loop.",
        course=COURSE,
    )
    notes(s, "Last session we built one harness and measured it. Today the "
             "question is what happens when one agent is not enough: the "
             "context fills up, the task has independent parts, or a "
             "specialist is needed. We cover the shapes - sub-agents, teams, "
             "handoffs - the failure modes, and then step back to what the "
             "discipline demands. Part 2 is notebook 04. Ask the class: when "
             "you split a job between people, what usually goes wrong first?")

    # 2. Part 1 divider
    s = ds.section_slide(
        prs, "01", "Part 1 - The theory: many agents, one harness",
        "Why to isolate context, three shapes of multi-agent work, how they "
        "fail, and what the discipline of harness engineering looks like.")
    notes(s, "Part 1 moves from one agent to many: why to isolate context, "
             "the three shapes, the failure modes, and then the discipline "
             "itself. Ask the class: what is the most agents you have seen "
             "cooperate on one task, and did it help?")

    # 3. Why isolate context
    s = ds.image_slide(
        prs,
        "Sub-agents exist to keep the lead's context small",
        f"{FIGS}/s4_isolate.png",
        kicker="Why isolate context",
        bullets=[
            "In plain words: a sub-agent is a fresh agent with a clean "
            "context, one task, a short report back",
            "Context is a finite budget; search results and long documents "
            "burn it fast",
            "A sub-agent spends tens of thousands of tokens exploring in its "
            "own window",
            "It returns a 1,000-2,000 token summary; only that enters the "
            "lead's context",
            "The lead keeps the plan; the details never pollute it",
            "The car: a convoy - the lead car reads the map, scouts drive the "
            "side roads",
        ],
        caption="Illustration. Sub-agent architectures and the 1,000-2,000 "
                "token summaries: Anthropic, Effective context engineering "
                "for AI agents, 29 Sep 2025.",
    )
    notes(s, "Start from the problem, not the pattern: in Session 2 the "
             "context window was a budget, and compaction was the emergency "
             "brake. Sub-agents are the structural fix - the expensive "
             "exploration happens in a window you throw away, and only a "
             "short summary comes back. Point at the arrow widths: gray "
             "brief out, blue summary back, nothing else crosses. Ask the "
             "class: what would you lose if the sub-agent returned its whole "
             "transcript instead of a summary?")

    # 4. The research system
    s = ds.big_number_slide(
        prs,
        "Splitting the work beat one big agent - at a price",
        "90.2%",
        "better than a single Opus 4 agent on Anthropic's internal research "
        "eval - at about 15x the tokens of a chat",
        foot="A lead agent (Opus) plans and spawns 3-5 Sonnet sub-agents in "
             "parallel, each with its own context; a separate citation pass at "
             "the end. Anthropic, How we built our multi-agent research "
             "system, 13 Jun 2025.",
        kicker="The research system",
    )
    notes(s, "The number that made multi-agent systems respectable: a lead "
             "Opus with parallel Sonnet sub-agents beat a lone Opus by 90.2% "
             "on breadth-first research questions. Then say the second half "
             "of the label louder than the first: fifteen times the tokens "
             "of a normal chat. The gain came from parallel exploration "
             "across separate context windows - exactly the isolation from "
             "the previous slide. Ask the class: which kinds of task would "
             "NOT benefit from splitting - and why?")

    # 5. Lessons from the research system
    s = ds.two_col_slide(
        prs,
        "The research system's lessons: teach delegation, scale the effort",
        ("What the lead agent must learn", [
            "Teach delegation: each sub-agent gets an objective, output "
            "format, tools and boundaries",
            "Vague briefs made sub-agents duplicate work or wander off",
            "Scale effort to complexity: a simple fact needs one agent; a "
            "survey needs ten or more",
            "Explicit rules for how many sub-agents and how many tool calls",
            "In plain words: the lead writes a good ticket, not a vague wish",
        ]),
        ("What the harness must provide", [
            "Parallel execution: sub-agents run at once and the wall clock "
            "drops sharply",
            "External memory: the lead saves its plan before context nears "
            "the limit",
            "A separate citation pass: one agent checks sources after the "
            "research",
            "Evals with calibrated LLM judges to compare versions",
            "Cost awareness: at ~15x tokens the task must be worth it",
        ]),
        kicker="Orchestrator-workers in production",
        note="Anthropic, How we built our multi-agent research system, "
             "13 Jun 2025.",
    )
    notes(s, "Two columns, two owners. The left is prompt work for the lead: "
             "it must brief its workers like a good manager - objective, "
             "format, tools, boundaries - and decide how much effort a "
             "question deserves. The right is harness work: parallelism, "
             "memory, a citation pass, evals. Notice that the fix for "
             "wandering sub-agents was not a smarter model; it was a better "
             "brief. Ask the class: write a one-line brief for a sub-agent "
             "that should find when function calling shipped - what would "
             "you include?")

    # 6. Three shapes
    s = ds.image_slide(
        prs,
        "Three shapes of multi-agent work: hierarchy, flat team, handoff",
        f"{FIGS}/s4_shapes.png",
        kicker="Sub-agents, teams, handoffs",
        caption="Illustration. Sub-agents: Claude Code, GA 2025. Agent teams: "
                "Claude Code research preview, Feb 2026. Handoffs: OpenAI, A "
                "practical guide to building agents, Apr 2025.",
    )
    notes(s, "Same three pictures every time you design a multi-agent "
             "system. Hierarchy: one lead, workers that report up and never "
             "talk sideways - simple and predictable. Flat team: a shared "
             "task list, teammates that claim work and message each other, a "
             "lead that assigns and synthesizes - more parallel, harder to "
             "reason about. Handoff: the conversation itself moves to a "
             "specialist and the first agent steps back. In plain words: a "
             "convoy, a crew with one job board, a change of drivers. Ask "
             "the class: which shape is a hospital triage desk?")

    # 7. Table: sub-agents vs teams vs handoffs
    s = ds.table_slide(
        prs,
        "Which shape when: sub-agents, agent teams and handoffs compared",
        ["", "Sub-agents", "Agent teams", "Handoffs"],
        [
            ["Shape", "Hierarchy: a lead spawns workers",
             "Flat: peers share one task list",
             "Chain: one agent replaces another"],
            ["Communication", "Results flow up only; no lateral talk",
             "Direct messages between teammates; a shared board",
             "The whole conversation moves, once"],
            ["Who decides", "The lead assigns and synthesizes",
             "The lead assigns; teammates claim and coordinate",
             "The current agent picks the next one"],
            ["Context", "Each worker has its own clean window",
             "Each teammate has its own window; the board is shared",
             "The receiver inherits the full history"],
            ["When to use", "Isolation: research, review, long reads",
             "Parallel work on many independent tasks",
             "Specialists: triage to billing, research to calculator"],
            ["Source", "Claude Code sub-agents, GA 2025",
             "Claude Code agent teams, Feb 2026",
             "OpenAI, Apr 2025: the decentralized pattern"],
        ],
        kicker="Sub-agents, teams, handoffs",
        note="OpenAI's manager pattern = sub-agents used as tools; its "
             "decentralized pattern = handoffs. OpenAI, A practical guide to "
             "building agents, Apr 2025.",
        col_widths=[1.6, 3.2, 3.4, 3.2],
    )
    notes(s, "Use the table as a decision aid, row by row. The "
             "communication row is the one students miss: sub-agents cannot "
             "talk to each other by design, which is a feature - no "
             "cross-contamination - until two of them need the same fact. "
             "Teams fix that with a board and a mailbox at the price of "
             "coordination. Handoffs are different in kind: nothing is "
             "summarized, the receiver gets everything. Ask the class: you "
             "have 40 independent documents to summarize - which column, and "
             "what is the risk?")

    # 8. Orchestration as code vs model decision
    s = ds.two_col_slide(
        prs,
        "Who orchestrates: your code, or the lead model?",
        ("As code: patterns.orchestrate(...)", [
            "A planner agent splits the task; code loops over the sub-tasks",
            "Code spawns one worker per sub-task and collects the results",
            "A synthesizer agent writes the final answer",
            "You see and test every step; the structure cannot drift",
            "Use when the shape of the work is known: split, solve, merge",
            "Notebook 04: ~6,021 tokens for 3 workers plus the synthesizer",
        ]),
        ("As a model decision: a delegate tool", [
            "The lead has one tool, delegate(task), that spawns a sub-agent",
            "The model decides when, how many, and with what brief",
            "Flexible: it can delegate twice, or not at all",
            "Harder to test; needs max_turns and a token budget",
            "Use when the sub-tasks only appear as you go",
            "Notebook 04: ~6,333 tokens for lead plus sub-agents; same "
            "subtasks, same final text",
        ]),
        kicker="Orchestration",
        note="Both live in the course library: harness.patterns.orchestrate "
             "and harness.multi.SubAgentPool.delegate_tool(). Workflows vs "
             "agents: Anthropic, Building effective agents, Dec 2024.",
    )
    notes(s, "This is Session 3's workflow-versus-agent choice, one level "
             "up. On the left, orchestration is a Python function: the plan "
             "is a list, the loop is a for-loop, the merge is a call. On the "
             "right, orchestration is a tool the lead may call, and the "
             "structure lives in the model's head. Notebook 04 runs both on "
             "the same three-part question. Ask the class: which side would "
             "you pick for a nightly report that must look the same every "
             "day?")

    # 9. Failure modes
    s = ds.table_slide(
        prs,
        "Six ways multi-agent systems fail - and the guard for each",
        ["Failure mode", "What it looks like", "The guard"],
        [
            ["Context pollution",
             "Sub-agent details and tool dumps flood the lead's window",
             "Isolation: summaries in, details stay out"],
            ["Runaway loops",
             "An agent repeats the same tool call and never says done",
             "max_turns, a token budget, a validator that fails loudly"],
            ["Cost multiplication",
             "Multi-agent ~15x the tokens of a chat; teams multiply again",
             "Trace every run; scale the number of agents to the task"],
            ["Too many handoffs",
             "Problems needing more than four handoffs almost always failed",
             "Fewer, clearer specialists; a router instead of a chain"],
            ["The extra reviewer",
             "Adding a reviewer agent lowered success by 8%",
             "Evals before adding an agent; more agents is not more quality"],
            ["Unbounded delegation",
             "The lead keeps spawning sub-agents until the budget is gone",
             "A before_tool hook caps delegations: at 2, the third is denied; "
             "~4,223 vs ~6,333 tokens (notebook 04)"],
        ],
        kicker="Failure modes",
        note="Handoffs and reviewer findings: Marmelab, The State of AI "
             "Harness Engineering 2026, Sep 2026. 15x tokens: Anthropic, "
             "Jun 2025. Delegation cap: notebook 04, 2 started, 1 denied.",
        col_widths=[2.2, 4.6, 4.2],
    )
    notes(s, "Every row is a real incident type; the last one is the notebook's "
             "own demo - a before_tool hook that denies the third delegation "
             "and saves a third of the tokens. The two survey findings "
             "deserve emphasis: chains of more than four handoffs almost "
             "always failed - each handoff loses intent - and adding a "
             "reviewer agent made things worse by eight points, probably "
             "because the reviewer second-guessed correct answers. The "
             "lesson is not 'never add agents'; it is 'never add an agent "
             "without an eval that shows it helped'. Ask the class: which "
             "of these five would a trace catch first?")

    # 10. The discipline
    s = ds.two_col_slide(
        prs,
        "The discipline: six things every harness needs, few have them",
        ("The checklist", [
            "Instruction files in the repo (CLAUDE.md, AGENTS.md): what the "
            "agent must know",
            "Executable guards: linters, structural tests, hooks - rules the "
            "agent cannot skip",
            "Permission design: a risk level per tool; deny danger by default",
            "Evals in CI: a suite with a pass rate, re-run on every change",
            "Observability: a trace of every call, token and second",
            "Cost budgets: max turns, token caps, alarms",
        ]),
        ("The field in 2026", [
            "63% of large projects ship instruction files; only a handful "
            "enforce them",
            "4.4% of security rules are backed by a real control",
            "60% of harnesses have no tests or evals",
            "93% of permission prompts get approved",
            "Eleven harnesses studied: 'hand-rolled async loops and "
            "deterministic retrieval'",
            "In plain words: most harnesses are cars with the brakes drawn "
            "on paper",
        ]),
        kicker="Harness engineering as a discipline",
        note="Marmelab, The State of AI Harness Engineering 2026, Sep 2026; "
             "Barbaste, Darrigol, Vu and Wiltberger, Harness Engineering: "
             "Anatomy, Architecture, and Evolution of Coding Agents, arXiv "
             "2609.00006, Jul 2026.",
    )
    notes(s, "Left column is the course in six lines; right column is the "
             "gap. Read them as pairs: instruction files exist but are not "
             "enforced; security rules exist but 4.4% have a control; "
             "permission prompts exist but 93% are waved through; and 60% of "
             "harnesses could not tell you whether their last change helped. "
             "The eleven-harness study found the same thing from the code "
             "side: the loops are hand-rolled and the retrieval is "
             "deterministic - engineering, not magic. Ask the class: which "
             "of the six did your notebook 03 harness already have?")

    # 11. Quote
    s = ds.quote_slide(
        prs,
        "The field runs on hand-rolled async loops and deterministic "
        "retrieval.",
        "Barbaste, Darrigol, Vu and Wiltberger - Harness Engineering: Anatomy, "
        "Architecture, and Evolution of Coding Agents (arXiv 2609.00006, Jul "
        "2026), a source-code study of eleven coding-agent harnesses.",
    )
    notes(s, "Read it twice. It is the most reassuring sentence in the "
             "module: the systems students read about - Claude Code, Codex "
             "CLI, Gemini CLI, Aider, OpenHands and the rest - are loops, "
             "tool registries and file search, written by hand. The 300 "
             "lines of harness in this course are the same species, "
             "smaller. Ask the class: after four sessions, which line of "
             "the course library would you now want to read in one of "
             "those eleven?")

    # 12. The future
    s = ds.image_slide(
        prs,
        "Where this is going: agent-first repositories and shared standards",
        f"{FIGS}/s4_signposts.png",
        kicker="The future",
        bullets=[
            "Agent-first repositories: about one million lines in five "
            "months, zero by hand",
            "The repo becomes the system of record: docs, decisions and "
            "plans written for agents",
            "Skills are an open standard since Dec 2025; 40+ platforms load "
            "the same SKILL.md",
            "21,500 harness repositories created in 2026, median age 8.7 "
            "months: a young field",
            "The job moves from writing prompts to engineering the runtime "
            "around the model",
            "In plain words: the engine is bought; the car is what you build",
        ],
        caption="Illustration. OpenAI, Harness engineering, Feb 2026; "
                "Anthropic, Agent Skills open standard, Dec 2025; Marmelab, "
                "Sep 2026; Barbaste et al., Jul 2026.",
    )
    notes(s, "Four signposts, all dated, none speculative. Repositories are "
             "being rewritten for agent readers; skills let one folder work "
             "across forty platforms; twenty-one thousand harness repos in "
             "one year says everyone is building the same car; and the "
             "discipline now has a name and a first anatomy paper. The "
             "closing line of the module: models are bought, harnesses are "
             "built. Ask the class: which of the eight pieces do you think "
             "will be standardized next, after tools (MCP) and skills?")

    # 13. Part 2 divider
    s = ds.section_slide(
        prs, "02", "Part 2 - The practice: notebook 04",
        "A lead with sub-agents against a solo agent, a team of three on a "
        "six-task board, a handoff, a runaway loop - and the eight pieces "
        "you built.")
    notes(s, "Open notebook 04. Same library, same ScriptedModel, no API key; "
             "the runs are deterministic so the numbers match the slides. Ask "
             "the class: which of the three shapes do you expect to cost the "
             "most tokens, and why?")

    # 14. Lead context vs sub-agents vs solo
    s = ds.image_slide(
        prs,
        "Lead window ~485 tokens; its sub-agents spend ~5,800 elsewhere",
        f"{FIGS}/s4_lead_context.png",
        kicker="Notebook 04 - sub-agents",
        bullets=[
            "How to read it: navy bars = what one agent's window holds at "
            "the end; sky bar = work done elsewhere",
            "The lead ends with 6 messages, ~485 tokens: its plan and three "
            "short reports",
            "Its three sub-agents spent ~5,800 tokens searching and reading; "
            "none of it in the lead",
            "A solo agent on the same compound question holds ~800 tokens "
            "and answers part one only",
            "Total work went up roughly eightfold; the lead's window shrank. "
            "That is the trade",
        ],
        caption="Notebook 04: lead with a delegate tool vs a solo research "
                "agent on the three-part question; tokens estimated by the "
                "course library (harness.multi.context_size).",
    )
    notes(s, "The chart has two kinds of bar on purpose. The navy bars are "
             "context sizes - what one agent was carrying at the end. The "
             "sky bar is total work done by the three sub-agents, which "
             "never touched the lead's window. The solo agent is the "
             "control: on the same three-part question it filled its window "
             "and still only answered the first part. Ask the class: the "
             "sub-agent version costs roughly eight times more in total - for "
             "which question is that obviously worth it, and for which is it "
             "not?")

    # 15. The team board
    s = ds.image_slide(
        prs,
        "Three teammates clear a six-task board and mail the lead six times",
        f"{FIGS}/s4_team_board.png",
        kicker="Notebook 04 - agent teams",
        bullets=[
            "How to read it: one row per task; the tag shows which teammate "
            "claimed it",
            "3 teammates, 6 tasks: each claims the next open task, works, "
            "marks it done",
            "6 mailbox messages to the lead: 'Task #n done: ...' with a cited "
            "answer",
            "~12,000 tokens for the three teammates, plus ~394 for the "
            "lead's final call",
            "A 4-teammate run gives the identical total: more hands, same "
            "work, same cost",
            "In plain words: a team of drivers sharing one job board",
        ],
        caption="Notebook 04: harness.multi.Team with TaskBoard and Mailbox; "
                "the six tasks come from the eval suite. Claude Code agent "
                "teams: research preview, Feb 2026.",
    )
    notes(s, "Walk the board top to bottom: tasks one to six, owners t0, t1, "
             "t2 in rotation because each teammate claims the next open task "
             "when it finishes. The mailbox on the right is the only channel "
             "to the lead - six short messages, each carrying a source tag. "
             "Compare with the sub-agent slide: here the lead did not even "
             "plan; the board did. The four-teammate run costs exactly the "
             "same: the board holds six tasks whoever claims them. Ask the class: what breaks first if two "
             "teammates claim the same task at the same time, and which "
             "piece of the harness should prevent it?")

    # 16. The handoff
    s = ds.image_slide(
        prs,
        "A handoff moves the whole conversation to a specialist",
        f"{FIGS}/s4_handoff.png",
        kicker="Notebook 04 - handoff",
        bullets=[
            "How to read it: the conversation moves right; the research "
            "agent steps back",
            "handoff(to_agent, history, instruction): 8 messages plus one "
            "new user message",
            "The calculator agent calls its tool once and answers 0.799102 in "
            "2 turns",
            "Its first call sees ~715 tokens of inherited history; a fresh "
            "calculator agent sees ~36",
            "Whole run ~1,440 tokens: routing sent only the question; a "
            "handoff sends everything",
            "In plain words: change drivers, keep the passengers - useful, "
            "not free",
        ],
        caption="Notebook 04: harness.multi.handoff. (891 - 179) / 891 = "
                "0.799102, the M2 train share. Handoffs: OpenAI, A practical "
                "guide to building agents, Apr 2025.",
    )
    notes(s, "The handoff is the simplest of the three shapes and the "
             "easiest to overuse. The calculator agent gets the entire "
             "research conversation and one new instruction; it needs only "
             "the instruction, but pays for everything. That is why the "
             "survey found chains of more than four handoffs almost always "
             "fail: the history grows and the intent blurs. Ask the class: "
             "when is inheriting the full history actually necessary, and "
             "what would a summary lose in that case?")

    # 17. The runaway loop
    s = ds.image_slide(
        prs,
        "A runaway loop costs more every turn - max_turns is the brake",
        f"{FIGS}/s4_runaway.png",
        kicker="Notebook 04 - stop conditions",
        bullets=[
            "How to read it: one bar per turn; height = context tokens the "
            "model saw on that turn",
            "A policy that always calls search_docs never says done",
            "Every turn re-sends the whole history, so cost grows: 134 to "
            "904 tokens, +154 per turn",
            "Six turns cost ~3,114 tokens and return an empty answer",
            "max_turns = 6 stops it: stopped_because = 'max_turns', not "
            "'done'",
            "The fixed 'careful' policy searches once and finishes for ~422 "
            "tokens",
        ],
        caption="Notebook 04: a looping policy that always calls search_docs, "
                "max_turns=6; context tokens per turn read from the trace. "
                "The careful policy: one search, done, ~422 tokens.",
    )
    notes(s, "This is Session 3's third exit made visible. The policy is "
             "deliberately broken: it calls the same search on every turn. "
             "Because the loop re-sends the full history each time, the "
             "per-turn cost climbs by 154 tokens each time and the total "
             "reaches about 3,114 for an empty answer. The dashed line is "
             "max_turns doing its job, and the result reports stopped_because "
             "equal to 'max_turns' so the caller knows it did not finish. "
             "The dotted line is the fix: a policy that searches once and "
             "answers costs about 422 tokens for the whole run. Ask the "
             "class: what would a smarter guard look at, so it could stop "
             "this loop at turn three instead of turn six?")

    # 18. The eight pieces mapped
    s = ds.table_slide(
        prs,
        "The eight pieces of a harness - and what you built for each",
        ["Piece", "In the car", "What you built (harness/ folder)"],
        [
            ["1. Model", "the engine",
             "ScriptedModel and ModelView; optional Anthropic or OpenAI "
             "adapters (models.py)"],
            ["2. Context", "dashboard and mirrors",
             "ContextWindow budget and compaction, Notes (context.py)"],
            ["3. Tools", "the trailer hitch",
             "@tool to JSON schema, ToolRegistry, risk levels (tools.py)"],
            ["4. Skills", "the glovebox manuals",
             "SKILL.md loader, three-level progressive disclosure (skills.py)"],
            ["5. The loop", "steering wheel and pedals",
             "Agent.run: gather, act, verify; exits done, max_turns, budget "
             "(agent.py)"],
            ["6. Guardrails", "brakes, seatbelts, airbags",
             "Hooks before_tool, after_tool, validate_answer; permissions "
             "(agent.py)"],
            ["7. Orchestration", "convoy and job board",
             "chain, route, parallel, orchestrate, evaluate_optimize; "
             "SubAgentPool, Team, handoff (patterns.py, multi.py)"],
            ["8. Evals and observability", "the logbook",
             "EvalCase, graders, compare; Trace, show, cost (evals.py, "
             "trace.py)"],
        ],
        kicker="Anatomy, revisited",
        note="Canon order from the course brief (Session 1). Every module "
             "lives in the harness/ folder next to the notebooks and runs "
             "without an API key.",
        col_widths=[2.3, 2.6, 7.2],
    )
    notes(s, "Close the loop with Session 1's anatomy slide: the same eight "
             "pieces, now with a file name each. Students have run every one "
             "of them. The point of the middle column is that the car "
             "metaphor was never decoration - each piece answers one "
             "question a driver would ask. Ask the class: which piece would "
             "you replace first if this harness went to production, and "
             "with what?")

    # 19. Close
    s = ds.close_slide(
        prs,
        "What you can now build",
        [
            "A harness: model + loop + tools + skills + guardrails + traces, "
            "with no API key needed",
            "A workflow when the path is known; an agent when it is not",
            "Sub-agents to keep the lead small; teams for parallel tasks; "
            "handoffs for specialists",
            "An eval suite that puts a pass rate and a price on every change",
            "Guards that run in code: risk levels, validators, max turns, "
            "budgets",
            "The discipline: instruction files, executable guards, evals in "
            "CI, observability",
            "Swap the ScriptedModel for a real one with providers.connect: "
            "same harness",
        ],
        course=COURSE,
    )
    notes(s, "End on capability, not theory. Every line is something they "
             "ran this module. The last line is the invitation: the "
             "notebooks' optional section connects a real model through the "
             "same interface, and nothing else in the harness changes - "
             "which is the whole argument of the module. Ask the class: what "
             "is the first agent you would build with this, and which of the "
             "eight pieces would you spend most of your time on?")

    return prs


if __name__ == "__main__":
    make_isolate_fig()
    make_shapes_fig()
    make_signposts_fig()
    make_lead_context_fig()
    make_team_board_fig()
    make_handoff_fig()
    make_runaway_fig()
    deck = slides()
    out = "../m5-session-4-sub-agents-teams-and-the-discipline.pptx"
    ds.save_deck(deck, out, FOOTER, author="M5 Harness Engineering course")
    print("Slides:", len(deck.slides._sldIdLst))
    print("Saved:", os.path.abspath(out))
