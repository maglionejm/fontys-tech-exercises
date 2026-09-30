"""Build deck: M5 Session 4 - Sub-agents, Teams and the Discipline.

Theory: why isolate context, the research system, sub-agents vs teams vs
handoffs, orchestration as code vs model decision, failure modes, the
discipline of harness engineering, the future.
Practice: notebook 04 on real Claude models (a lead with a delegate tool vs
a solo agent, the orchestrator vs the lead, a team on a task board, a
handoff, the two seatbelts on an open-ended task, the bill) and lab 4
(Claude Code subagents, hooks, permission rules and modes, agent teams).
Every Part 2 number is read from the executed notebook's outputs or from
the observed runs quoted in the lab guide; captions say which run.
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
RUN = ("Recorded run on claude-opus-5 (lead) and claude-sonnet-5 (workers), "
       "30 Sep 2026; live runs vary.")
LAB = "Observed with Claude Code 2.1.278 on 30 Sep 2026, claude -p from lab/; live runs vary."


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


# ---------------------------------------------------------------- figures (theory)
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


# ---------------------------------------------------------------- figures (notebook 04)
def make_lead_context_fig():
    """Where the reading happened: final context of the lead, the sum of its
    workers' final contexts, and the solo agent's final context
    (notebook 04, cells 8, 10 and 11: count_tokens on the final messages)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = ["Lead: its own final context\n(2 model calls; holds 3 reports)",
              "Workers: final contexts summed\n(2,230 + 1,137 + 1,799; never in the lead)",
              "Solo: its own final context\n(3 model calls; holds 3 files)"]
    vals = [1527, 5166, 3985]
    texts = ["1,527 tokens", "5,166 tokens", "3,985 tokens"]
    colors = [pal["navy"], pal["sky"], pal["navy"]]
    bars = ax.barh(labels, vals, color=colors, height=0.55)
    ax.invert_yaxis()
    for bar, v, t in zip(bars, vals, texts):
        ax.text(v + 90, bar.get_y() + bar.get_height() / 2, t, va="center",
                color=pal["ink"], fontsize=11.5, fontweight="bold")
    ax.set_xlim(0, 7400)
    ax.set_xlabel("Tokens (count_tokens on the final message list)")
    ax.set_title("Where the reading happened: one compound question, three files")
    ax.tick_params(axis="y", labelsize=10)
    ax.text(7300, 0, "Both architectures answered 3 of 3 parts.\n"
            "Lead + workers 0.0444 USD in 25.8 s;\nsolo 0.0402 USD in 7.5 s.",
            ha="right", va="center", color=pal["gray"], fontsize=9,
            style="italic", linespacing=1.3)
    ax.set_ylim(2.6, -0.6)
    fig.savefig(f"{FIGS}/s4_lead_context.png")
    plt.close(fig)


def make_team_board_fig():
    """The task board after the run and what the team saved
    (notebook 04, cells 18 to 20, and exercise 2 in cell 40)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.add_patch(FancyBboxPatch((0.15, 5.3), 6.0, 0.55, boxstyle="round,pad=0.02",
                                facecolor=pal["navy"], edgecolor=pal["navy"]))
    ax.text(0.35, 5.575, "TASK BOARD  -  6 tasks, 3 teammates", va="center",
            color="white", fontweight="bold", fontsize=9.5)
    tasks = [("#1", "teammate-1", "Which licence does the repo use?"),
             ("#2", "teammate-2", "Copyright holder and year"),
             ("#3", "teammate-3", "Titanic passengers and survivors"),
             ("#4", "teammate-2", "Secret scanner in the CI workflow"),
             ("#5", "teammate-1", "random_state in CONTRIBUTING"),
             ("#6", "teammate-3", "Notebook matrix; the Module 5 job")]
    for i, (tid, owner, desc) in enumerate(tasks):
        y = 4.8 - i * 0.58
        ax.add_patch(FancyBboxPatch((0.15, y - 0.24), 6.0, 0.48,
                                    boxstyle="round,pad=0.02",
                                    facecolor="white" if i % 2 else pal["panel"],
                                    edgecolor=pal["sky"], lw=0.8))
        ax.text(0.35, y, tid, va="center", color=pal["navy"], fontweight="bold",
                fontsize=9.2)
        ax.add_patch(FancyBboxPatch((0.85, y - 0.15), 0.72, 0.3,
                                    boxstyle="round,pad=0.02",
                                    facecolor=pal["blue"], edgecolor=pal["blue"]))
        ax.text(1.21, y, "done", ha="center", va="center", color="white",
                fontsize=7.8, fontweight="bold")
        ax.text(1.75, y, owner, va="center", color=pal["blue"], fontsize=8.4,
                fontweight="bold")
        ax.text(3.0, y, desc, va="center", color=pal["ink"], fontsize=7.9)
    log = ["board log (t1 = teammate-1):  t1 claims #1 | t2 claims #2 | t3 claims #3 |",
           "t2 done #2 | t2 claims #4 | t1 done #1 | t1 claims #5 | t3 done #3 |",
           "t3 claims #6 | t1 done #5 | t2 done #4 | t3 done #6.  Nobody assigned; the board did."]
    for i, line in enumerate(log):
        ax.text(0.2, 1.5 - i * 0.26, line, va="center", color=pal["gray"], fontsize=6.9)
    # right panel: what the team saved
    ax.add_patch(FancyBboxPatch((6.45, 1.0), 3.4, 4.85, boxstyle="round,pad=0.03",
                                facecolor="white", edgecolor=pal["blue"], lw=1.3))
    ax.add_patch(FancyBboxPatch((6.45, 5.3), 3.4, 0.55, boxstyle="round,pad=0.03",
                                facecolor=pal["blue"], edgecolor=pal["blue"]))
    ax.text(6.6, 5.575, "WHAT THE TEAM SAVED", va="center",
            color="white", fontweight="bold", fontsize=8.6)
    scale = 2.3 / 19.9
    ax.text(6.6, 4.95, "3 teammates in parallel (wall-clock)", va="center",
            color=pal["ink"], fontsize=7.8)
    ax.add_patch(FancyBboxPatch((6.6, 4.5), 7.5 * scale, 0.3,
                                boxstyle="square,pad=0", facecolor=pal["blue"],
                                edgecolor=pal["blue"]))
    ax.text(6.6 + 7.5 * scale + 0.1, 4.65, "7.5 s", va="center",
            color=pal["navy"], fontsize=9.5, fontweight="bold")
    ax.text(6.6, 4.05, "the same six runs one after another", va="center",
            color=pal["ink"], fontsize=7.8)
    ax.add_patch(FancyBboxPatch((6.6, 3.6), 19.9 * scale, 0.3,
                                boxstyle="square,pad=0", facecolor=pal["sky"],
                                edgecolor=pal["sky"]))
    ax.text(6.6 + 19.9 * scale + 0.1, 3.75, "19.9 s", va="center",
            color=pal["navy"], fontsize=9.5, fontweight="bold")
    lines = [("17 model calls, 10 tool calls", "normal"),
             ("24,611 input tokens, 0.0706 USD", "bold"),
             ("each teammate took 2 tasks", "normal"),
             ("exercise 2, four teammates:", "normal"),
             ("7.9 s and 0.0715 USD", "bold")]
    for i, (line, weight) in enumerate(lines):
        ax.text(6.6, 3.0 - i * 0.4, line, va="center", color=pal["ink"],
                fontsize=7.8, fontweight=weight)
    ax.add_patch(FancyBboxPatch((0.15, 0.15), 9.7, 0.55, boxstyle="round,pad=0.02",
                                facecolor=pal["navy"], edgecolor=pal["navy"]))
    ax.text(5.0, 0.425, "Same six worker runs either way: parallel work moves "
            "the clock, not the tokens", ha="center",
            va="center", color="white", fontsize=9.5, fontweight="bold")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.1)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s4_team_board.png")
    plt.close(fig)


def make_handoff_fig():
    """The handoff: the research worker's whole conversation moves to the
    calculator specialist (notebook 04, cell 23)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    ax.add_patch(FancyBboxPatch((0.15, 1.3), 3.7, 3.9, boxstyle="round,pad=0.04",
                                facecolor="white", edgecolor=pal["gray"], lw=1.3))
    ax.text(2.0, 4.85, "RESEARCH WORKER (sonnet-5)", ha="center", va="center",
            color=pal["gray"], fontweight="bold", fontsize=9)
    ax.text(2.0, 4.5, "steps back after the handoff", ha="center",
            va="center", color=pal["gray"], fontsize=8, style="italic")
    rows = ["user: passengers and survivors?",
            "assistant: tool_use", "user: tool_result",
            "assistant: tool_use", "user: tool_result",
            "assistant: 891 passengers, 342 survivors",
            "6 messages in all"]
    for i, r in enumerate(rows):
        y = 4.05 - i * 0.36
        last = i == len(rows) - 1
        ax.add_patch(FancyBboxPatch((0.3, y - 0.14), 3.4, 0.28,
                                    boxstyle="round,pad=0.01",
                                    facecolor="white" if last else pal["panel"],
                                    edgecolor="white" if last else pal["sky"],
                                    lw=0.6))
        ax.text(0.4, y, r, va="center", color=pal["gray"] if last else pal["ink"],
                fontsize=7.2, style="italic" if last else "normal")
    arrow(ax, (3.85, 3.25), (6.15, 3.25), color=pal["navy"], lw=2.2, ms=20)
    ax.text(5.0, 3.9, "specialist.run(task,\nhistory=research_run.messages)",
            ha="center", va="center", color=pal["navy"], fontsize=6.6,
            fontweight="bold", linespacing=1.3)
    ax.text(5.0, 2.7, "the whole\nconversation moves", ha="center",
            va="center", color=pal["gray"], fontsize=8, style="italic")
    ax.add_patch(FancyBboxPatch((6.15, 1.3), 3.7, 3.9, boxstyle="round,pad=0.04",
                                facecolor="white", edgecolor=pal["blue"], lw=1.5))
    ax.text(8.0, 4.85, "CALCULATOR (sonnet-5)", ha="center",
            va="center", color=pal["navy"], fontweight="bold", fontsize=9)
    ax.text(8.0, 4.5, "inherits all 6 messages, then 4 new:", ha="center",
            va="center", color=pal["gray"], fontsize=8, style="italic")
    rows2 = [("user: what share of passengers survived?", pal["panel"], pal["ink"]),
             ("assistant: calculate('342/891*100')", pal["panel"], pal["ink"]),
             ("tool: 38.38383838383838", pal["panel"], pal["ink"]),
             ("assistant: About 38.4% of the passengers\nsurvived (342/891).", pal["blue"], "white")]
    for i, (r, fc, tc) in enumerate(rows2):
        y = 4.0 - i * 0.55
        h = 0.5 if i == 3 else 0.4
        ax.add_patch(FancyBboxPatch((6.3, y - h / 2), 3.4, h,
                                    boxstyle="round,pad=0.02", facecolor=fc,
                                    edgecolor=pal["sky"] if fc != pal["blue"] else fc,
                                    lw=0.6))
        ax.text(6.4, y, r, va="center", color=tc, fontsize=7.2,
                fontweight="bold" if fc == pal["blue"] else "normal",
                linespacing=1.2)
    ax.text(8.0, 1.62, "first model call: 7,539 input tokens\nfresh "
            "calculator, same sum: 522\ninherited: 7,017 tokens",
            ha="center", va="center", color=pal["navy"], fontsize=7.4,
            linespacing=1.3, fontweight="bold")
    ax.text(5.0, 0.6, "The handoff (research, then calculator) cost 0.0514 USD "
            "for one answer; the fresh calculator 0.0029 USD.", ha="center",
            va="center", color=pal["gray"], fontsize=8.2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0.2, 5.4)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s4_handoff.png")
    plt.close(fig)


def make_runaway_fig():
    """Input tokens per model call on the open-ended task with
    max_input_tokens=12_000; the sixth call was measured by count_tokens and
    never sent (notebook 04, cells 26 and 27). The max_turns=4 run is the
    text box."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    calls = [1, 2, 3, 4, 5]
    tokens = [738, 991, 2197, 3587, 4112]
    ax.bar(calls, tokens, color=pal["blue"], width=0.7)
    for c, v in zip(calls, tokens):
        ax.text(c, v + 350, f"{v:,}", ha="center", color=pal["ink"], fontsize=9)
    ax.bar([6], [17810], width=0.7, facecolor="white", edgecolor=pal["navy"],
           hatch="///", lw=1.4)
    ax.text(6, 17810 + 350, "17,810", ha="center", color=pal["navy"],
            fontsize=9.5, fontweight="bold")
    ax.text(5.55, 15800, "never sent:\ncount_tokens\nmeasured it first", ha="right",
            va="center", color=pal["navy"], fontsize=8.6, style="italic",
            linespacing=1.3)
    ax.axhline(12000, color=pal["navy"], lw=1.6, ls="--")
    ax.text(0.65, 12350, "max_input_tokens = 12,000  ->  stopped_because = 'budget'",
            color=pal["navy"], fontsize=9.5, fontweight="bold", va="bottom")
    ax.text(0.65, 20500, "The other seatbelt, max_turns=4, on the same task:\n"
            "stopped after 4 model calls and 23 tool calls, 0.0279 USD.\n"
            "Neither run produced a summary.",
            color=pal["gray"], fontsize=8.8, va="top", linespacing=1.3)
    ax.annotate("call 5 asked for a whole batch of files at once",
                xy=(5.35, 4112), xytext=(2.9, 7600), color=pal["ink"], fontsize=8.8,
                arrowprops=dict(arrowstyle="-|>", color=pal["gray"], lw=1.2))
    ax.set_xticks(calls + [6])
    ax.set_xticklabels([f"call {c}" for c in calls] + ["call 6"])
    ax.set_xlim(0.4, 6.7)
    ax.set_ylim(0, 21500)
    ax.set_xlabel("Model call ('Read every file in this repository and summarise each one')")
    ax.set_ylabel("Input tokens of that call")
    ax.set_title("An open-ended task: the context grows every call until the budget stops it")
    ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: f"{int(v):,}"))
    fig.savefig(f"{FIGS}/s4_runaway.png")
    plt.close(fig)


# ---------------------------------------------------------------- figures (lab 4)
def make_subagent_fig():
    """Lab 4: the subagent definition file and the PostToolUse log of the
    first observed run (lab guide, sections 1.1 and 1.2)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    # left card: the definition file
    ax.add_patch(FancyBboxPatch((0.15, 0.2), 4.7, 5.65, boxstyle="round,pad=0.03",
                                facecolor="white", edgecolor=pal["blue"], lw=1.3))
    ax.add_patch(FancyBboxPatch((0.15, 5.3), 4.7, 0.55, boxstyle="round,pad=0.03",
                                facecolor=pal["blue"], edgecolor=pal["blue"]))
    ax.text(0.3, 5.575, ".claude/agents/repo-researcher.md", va="center",
            color="white", fontweight="bold", fontsize=9, family="monospace")
    front = ["---",
             "name: repo-researcher",
             "description: Answers factual questions about",
             "  this repository by reading its files. Use",
             "  it whenever the user asks what a workflow,",
             "  notebook, README, licence or changelog",
             "  says. Read-only; it reports the file used.",
             "tools: Read, Grep, Glob",
             "model: sonnet",
             "maxTurns: 10",
             "---"]
    for i, line in enumerate(front):
        ax.text(0.3, 5.0 - i * 0.25, line, va="center", color=pal["navy"],
                fontsize=6.8, family="monospace",
                fontweight="bold" if line.startswith(("tools", "model", "maxT")) else "normal")
    ax.text(0.3, 2.1, "description = the delegate tool's docstring, for a\n"
            "machine; tools = the allow-list; model = WORKER_MODEL;\n"
            "maxTurns = max_turns",
            va="center", color=pal["blue"], fontsize=6.6, style="italic",
            linespacing=1.3)
    body = ["You answer questions about this repository,",
            "and only from its files. Rules: 1. find the",
            "file first, read only the part you need",
            "2. five sentences at most; quote the line,",
            "give the path  3. if absent, say so  4. never",
            "open .env  5. no tools that edit or run code"]
    for i, line in enumerate(body):
        ax.text(0.3, 1.55 - i * 0.22, line, va="center", color=pal["gray"],
                fontsize=6.6, family="monospace")
    # right card: the log and the bill
    ax.add_patch(FancyBboxPatch((5.15, 0.2), 4.7, 5.65, boxstyle="round,pad=0.03",
                                facecolor="white", edgecolor=pal["gray"], lw=1.2))
    ax.add_patch(FancyBboxPatch((5.15, 5.3), 4.7, 0.55, boxstyle="round,pad=0.03",
                                facecolor=pal["navy"], edgecolor=pal["navy"]))
    ax.text(5.3, 5.575, ".claude/tool-calls.log after run 1", va="center",
            color="white", fontweight="bold", fontsize=9, family="monospace")
    ax.text(5.3, 4.95, "tool   input                     result_chars",
            va="center", color=pal["gray"], fontsize=6.6, family="monospace")
    log = [("Grep ", "python-version", "458"),
           ("Glob ", ".github/workflows/*.yaml", "116"),
           ("Glob ", ".github/workflows/*.yml", "367"),
           ("Grep ", "python-version", "174"),
           ("Grep ", "python-version", "174"),
           ("Grep ", "python-version", "174"),
           ("Read ", ".github/workflows/notebooks.yml", "2583"),
           ("Agent", "Find notebook workflow Python v.", "3284")]
    for i, (tool, inp, chars) in enumerate(log):
        y = 4.6 - i * 0.29
        fc = pal["panel"] if i < 7 else pal["blue"]
        tc = pal["ink"] if i < 7 else "white"
        ax.add_patch(FancyBboxPatch((5.3, y - 0.125), 4.4, 0.25,
                                    boxstyle="round,pad=0.01", facecolor=fc,
                                    edgecolor=fc, lw=0.5))
        ax.text(5.38, y, f"{tool}  {inp:<32}{chars:>5}", va="center", color=tc,
                fontsize=6.6, family="monospace",
                fontweight="bold" if i == 7 else "normal")
    ax.text(5.3, 2.15, "shaded rows: 7 calls inside the subagent,\n"
            "never seen by the main agent.\nBlue row: the one result the main agent got.",
            va="center", color=pal["gray"], fontsize=6.6, style="italic",
            linespacing=1.3)
    bill = ["num_turns = 2      total_cost_usd = 0.1709",
            "claude-fable-5-1 (main agent)   0.1168 USD",
            "  34 input, 685 output, 46,296 cache-read",
            "claude-sonnet-5 (the subagent)  0.0541 USD",
            "  8 input, 2,226 output, 23,657 cache-read"]
    for i, line in enumerate(bill):
        ax.text(5.3, 1.6 - i * 0.25, line, va="center",
                color=pal["navy"] if i in (0, 1, 3) else pal["gray"],
                fontsize=6.8, family="monospace",
                fontweight="bold" if i == 0 else "normal")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.1)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s4_lab_subagent.png")
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
        "lead with sub-agents, a team, a handoff and an open-ended task on "
        "real Claude models, and lab 4 finds the same parts in Claude Code.",
        course=COURSE,
    )
    notes(s, "Last session we built one harness and measured it. Today the "
             "question is what happens when one agent is not enough: the "
             "context fills up, the task has independent parts, or a "
             "specialist is needed. We cover the shapes - sub-agents, teams, "
             "handoffs - the failure modes, and then step back to what the "
             "discipline demands. Part 2 is notebook 04 and lab 4. Class "
             "question: when you split a job between people, what usually goes "
             "wrong first?")

    # 2. Part 1 divider
    s = ds.section_slide(
        prs, "01", "Part 1 - The theory: many agents, one harness",
        "Why to isolate context, three shapes of multi-agent work, how they "
        "fail, and what the discipline of harness engineering looks like.")
    notes(s, "Part 1 moves from one agent to many: why to isolate context, "
             "the three shapes, the failure modes, and then the discipline "
             "itself. Class question: what is the most agents you have seen "
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
             "brief out, blue summary back, nothing else crosses. Class "
             "question: what would you lose if the sub-agent returned its whole "
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
             "the previous slide. Class question: which kinds of task would "
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
             "brief. Class question: write a one-line brief for a sub-agent "
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
             "convoy, a crew with one job board, a change of drivers. Class "
             "question: which shape is a hospital triage desk?")

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
             "summarized, the receiver gets everything. Class question: you "
             "have 40 independent documents to summarize - which column, and "
             "what is the risk?")

    # 8. Orchestration as code vs model decision
    s = ds.two_col_slide(
        prs,
        "Who orchestrates: your code, or the lead model?",
        ("As code: the orchestrator-workers pattern", [
            "A planner agent splits the task; code loops over the sub-tasks",
            "Code starts one worker per sub-task, in a thread pool, and "
            "collects the results",
            "A synthesizer agent writes the final answer",
            "You see and test every step; the structure cannot drift",
            "Use when the shape of the work is known: split, solve, merge",
            "Notebook 04: 4 sub-questions, workers in parallel in 6.0 s, "
            "0.0415 USD in all",
        ]),
        ("As a model decision: a delegate tool", [
            "The lead has one tool, delegate(task), that starts a fresh "
            "worker Agent",
            "The model decides when, how many, and with what brief",
            "Flexible: it can delegate twice, or not at all",
            "Harder to test; needs max_turns and a token budget",
            "Use when the sub-tasks only appear as you go",
            "Notebook 04: 3 sub-questions, delegations run one after "
            "another, 0.0444 USD in all",
        ]),
        kicker="Orchestration",
        note="Both run in notebook 04 on the same compound question about the "
             "repository: planner and synthesizer as harness Agents (the "
             "planner with a JSON-schema output), delegate as an @tool that "
             "starts a worker Agent. Anthropic, Building effective agents, "
             "Dec 2024.",
    )
    notes(s, "This is Session 3's workflow-versus-agent choice, one level "
             "up. On the left, orchestration is a Python function: the plan "
             "is a list, the loop is a for-loop, the merge is a call. On the "
             "right, orchestration is a tool the lead may call, and the "
             "structure lives in the model's head. Notebook 04 runs both on "
             "the same three-part question; the totals came out close "
             "(0.0415 against 0.0444 USD) because the reading is the same "
             "and only the coordination differs: two cheap planner and "
             "synthesizer calls against two calls on the expensive lead "
             "model. Class question: which side would you pick for a nightly "
             "report that must look the same every day?")

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
             "An open-ended task: the agent keeps listing and reading and "
             "never says done",
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
             "A before_tool hook caps delegations at two; told about the "
             "cap, the lead planned two workers and still answered all "
             "three parts (notebook 04, exercise 1)"],
        ],
        kicker="Failure modes",
        note="Handoffs and reviewer findings: Marmelab, The State of AI Harness Engineering 2026, Sep 2026. 15x tokens: Anthropic, Jun 2025. Delegation cap: notebook 04 exercise 1, recorded run: 2 workers started, 0 denied, 0.0424 USD.",
        col_widths=[2.2, 4.6, 4.2],
    )
    notes(s, "Every row is a real incident type; the last one is the notebook's "
             "own exercise - a before_tool hook that denies a third "
             "delegation. In the recorded run the hook never had to fire: "
             "told about the cap in its system prompt, the lead planned two "
             "workers, one of them covering two files, and answered all "
             "three parts for slightly less than the uncapped lead. The two "
             "survey findings deserve emphasis: chains of more than four "
             "handoffs almost always failed - each handoff loses intent - "
             "and adding a reviewer agent made things worse by eight points, "
             "probably because the reviewer second-guessed correct answers. "
             "The lesson is not 'never add agents'; it is 'never add an "
             "agent without an eval that shows it helped'. Class question: "
             "which of these six would a trace catch first?")

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
             "deterministic - engineering, not magic. Class question: which "
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
             "tool registries and file search, written by hand. The harness "
             "package in this course is the same species, smaller. Class "
             "question: after four sessions, which line of the harness package "
             "would you now want to read in one of those eleven?")

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
             "built. Class question: which of the eight pieces do you think "
             "will be standardized next, after tools (MCP) and skills?")

    # 13. Part 2 divider
    s = ds.section_slide(
        prs, "02", "Part 2 - The practice: notebook 04 and lab 4",
        "A lead with sub-agents against a solo agent, a team of three on a "
        "six-task board, a handoff, two seatbelts on an open-ended task, the "
        "bill - then the same parts as Claude Code features.")
    notes(s, "Open notebook 04. Everything runs on real Claude models: "
             "claude-opus-5 leads and synthesizes, claude-sonnet-5 does the "
             "reading, and the agents read files of this repository, so "
             "every answer can be checked by opening the file. The key sits "
             "in the git-ignored .env at the repository root and only "
             "load_client() reads it. The numbers on the next slides are "
             "from the run recorded on 30 September 2026, which cost 0.4413 "
             "USD for the whole notebook; a live run will differ in wording, "
             "in the route the model takes and in cents. Class question: "
             "which of the three shapes do you expect to cost the most "
             "tokens, and why?")

    # 14. Lead vs solo: where the reading happened
    s = ds.image_slide(
        prs,
        "Lead: 1,527 tokens of final context; solo agent: 3,985",
        f"{FIGS}/s4_lead_context.png",
        kicker="Notebook 04 - sub-agents",
        bullets=[
            "How to read it: navy bars = one agent's own context when it "
            "finished; sky bar = the workers' contexts, which the lead never saw",
            "The lead (opus-5) has no read_file: its only tool is "
            "delegate(task), which starts a fresh worker Agent on sonnet-5",
            "It made 3 delegate calls in one turn and 2 model calls; it "
            "holds three reports, not three files: 1,527 tokens",
            "The solo agent read the same three files itself: 3 model "
            "calls, 5 tool calls, 3,985 tokens, about 2.5x the lead",
            "Plainly: the solo agent was not polluted here. It answered 3 "
            "of 3 parts, cheaper (0.0402 vs 0.0444 USD) and faster",
            "Isolation pays when the question or the files outgrow one "
            "context; on three facts the strong model coped",
        ],
        caption=RUN + " count_tokens on each agent's final message list "
                "(notebook 04, section 1).",
    )
    notes(s, "The chart has two kinds of bar on purpose. The navy bars are "
             "context sizes - what one agent was carrying at the end, "
             "counted by the API on the exact messages. The sky bar is the "
             "sum of the three workers' final contexts, which never touched "
             "the lead's window. Say the honest part out loud: on this "
             "three-part question the solo agent on opus-5 was not polluted. "
             "It read exactly the three files it needed, answered all three "
             "parts, and cost less and finished in a third of the time "
             "because it made no detours. The lesson is 'scale effort to "
             "the query': the sub-agent design earns its cost when the "
             "question has ten facts or the files are ten times longer, "
             "because then the solo context keeps growing and you cannot "
             "tell which fact it dropped without a grader. Class question: "
             "how would you change the question so that the solo agent "
             "does drop a part?")

    # 15. The team board
    s = ds.image_slide(
        prs,
        "Three teammates cleared six tasks in 7.5 s, not 19.9 s",
        f"{FIGS}/s4_team_board.png",
        kicker="Notebook 04 - agent teams",
        bullets=[
            "How to read it: one row per task, the owner is the teammate "
            "that claimed it; right, wall-clock against the summed run times",
            "A TaskBoard with a lock: claim() moves a task todo -> doing; "
            "three teammate threads claim, run a fresh worker, post, repeat",
            "Nobody assigned anything: each teammate took one task, and "
            "whoever finished first took the next; two each in this run",
            "17 model calls, 10 tool calls, 0.0706 USD including the "
            "team lead's briefing on opus-5; the six answers are gradable",
            "Exercise 2, four teammates: 7.9 s and 0.0715 USD - the same "
            "within noise, because six tasks still take two rounds",
            "Claude Code's agent teams do this natively, plus a mailbox "
            "between teammates: see the lab",
        ],
        caption=RUN + " TaskBoard, three threads, tasks from evals/cases.yaml "
                "(notebook 04, section 3).",
    )
    notes(s, "Walk the board top to bottom: the three teammates claimed one "
             "task each at the start, and whoever finished first took the "
             "next open task, so each ended with two. The right panel is "
             "the only thing the team buys: the clock. The six worker runs "
             "happen either way, so the tokens and the cost are the same; "
             "parallel work moved 19.9 seconds of work into 7.5. The "
             "four-teammate exercise makes the point twice: with six tasks "
             "and four hands you still need two rounds, so nothing is saved "
             "and the cost is unchanged. Class question: what breaks first "
             "if two teammates claim the same task at the same time, and "
             "which line of TaskBoard prevents it?")

    # 16. The handoff
    s = ds.image_slide(
        prs,
        "A handoff carries everything: 7,017 inherited tokens",
        f"{FIGS}/s4_handoff.png",
        kicker="Notebook 04 - handoff",
        bullets=[
            "How to read it: the conversation moves right; the research "
            "worker steps back",
            "One argument does it: run(task, history=research_run.messages); "
            "6 inherited messages, 4 new",
            "The calculator called its tool once (342/891*100): about 38.4% "
            "of the passengers survived",
            "First model call: 7,539 input tokens; a fresh calculator on the "
            "same sum: 522. Inherited: 7,017",
            "0.0514 USD for one answer, 0.0029 fresh. Delegation asks for a "
            "report; a handoff hands over",
            "Marmelab 2026: more than four handoffs almost always failed; "
            "the history goes stale",
        ],
        caption=RUN + " Input tokens from the trace of the first model call "
                "(notebook 04, section 4).",
    )
    notes(s, "The handoff is the simplest of the three shapes and the "
             "easiest to overuse. The calculator specialist gets the entire "
             "research conversation and one new instruction; it needs only "
             "the two numbers, but pays for the README the worker read, its "
             "tool calls and its answer - 7,017 tokens on the first call and "
             "again on the second. That is why the survey found chains of "
             "more than four handoffs almost always fail: the history grows "
             "and the intent blurs. Class question: when is inheriting the "
             "full history actually necessary, and what would a summary "
             "lose in that case?")

    # 17. Runaway prevention: the two seatbelts
    s = ds.image_slide(
        prs,
        "An open-ended task never says done; two seatbelts stop it",
        f"{FIGS}/s4_runaway.png",
        kicker="Notebook 04 - stop conditions",
        bullets=[
            "How to read it: one bar per model call, in order; height = "
            "input tokens the API billed for that call, the context it saw",
            "The task: 'read every file in this repository and summarise "
            "each one'. Nothing staged; the worker just keeps going",
            "Seatbelt 1, max_turns=4: stopped_because = 'max_turns' after "
            "4 model calls and 23 tool calls, 0.0279 USD",
            "Seatbelt 2, max_input_tokens=12,000: the calls saw 738, 991, "
            "2,197, 3,587 and 4,112 tokens as folders were listed",
            "Then the worker asked for a whole batch of files; count_tokens "
            "measured the next call at 17,810 and the loop refused to send it",
            "stopped_because = 'budget', 37 tool calls, 0.0450 USD, no "
            "summary. Both runs together: 0.0729 USD for nothing",
        ],
        caption=RUN + " Trace input tokens per call; call 6 is the "
                "count_tokens figure (nb 04, 5.1).",
    )
    notes(s, "This is Session 3's stop conditions made visible on a real "
             "model. Nothing is staged: the task is simply open-ended, and "
             "a worker will list folders and read files for as long as it "
             "is allowed. Each call re-sends the previous tool results, so "
             "the bars grow, slowly while it lists and then in a jump when "
             "it asks for fourteen files at once. The dashed line is the "
             "budget; the hatched bar is the call the harness measured with "
             "count_tokens and never sent. The text box is the other "
             "seatbelt, max_turns=4, which stopped a second run after four "
             "calls. Neither produced a summary; together they cost about "
             "seven cents. A trace is how you notice a runaway before the "
             "invoice does. Class question: what would a smarter guard look "
             "at, so it could stop this task after the second call instead "
             "of the fifth?")

    # 18. The bill: cost multiplication
    s = ds.table_slide(
        prs,
        "Every context that reads pays: the bill per architecture",
        ["Architecture", "Model calls", "Tool calls", "Input tokens",
         "Output tokens", "Cost (USD)", "Answered", "USD per answer", "x solo"],
        [
            ["Lead + workers", "9", "7", "10,081", "995", "0.0444", "3", "0.0148", "1.1"],
            ["Solo agent", "3", "5", "5,702", "469", "0.0402", "3", "0.0134", "1.0"],
            ["Orchestrator-workers", "12", "6", "12,519", "1,074", "0.0415", "3", "0.0138", "1.0"],
            ["Team of 3 + lead", "17", "10", "24,611", "1,322", "0.0706", "6", "0.0118", "1.8"],
            ["Handoff (research, then calculator)", "5", "3", "24,469", "242", "0.0514", "1", "0.0514", "1.3"],
            ["Fresh calculator (for comparison)", "2", "1", "1,110", "71", "0.0029", "1", "0.0029", "0.1"],
            ["Runaway prevention (two capped runs)", "10", "60", "18,958", "3,495", "0.0729", "0", "-", "1.8"],
        ],
        kicker="Notebook 04 - cost multiplication",
        note="How to read it: one row per architecture, every model call it made, workers included. Compare USD per answer: flat at 0.0118 to 0.0148 except the handoff, whose two specialist calls each carried 7,017 inherited tokens. " + RUN,
        col_widths=[3.15, 1.0, 0.95, 1.15, 1.2, 1.05, 1.15, 1.25, 0.8],
    )
    notes(s, "Read the table with the 'answered' column in hand. The team "
             "answered six questions, the others the same three-part "
             "question, so the number to compare is the cost per answered "
             "question - and in this run it was roughly flat everywhere, "
             "between 1.2 and 1.5 cents, because every answer needs its own "
             "listing, reading and writing. The team cost 1.8 times the "
             "solo agent for twice the questions. The one outlier is the "
             "handoff: five cents for a single answer, because the "
             "specialist carried the whole research conversation on both "
             "of its calls. What multiplies is the number of contexts doing "
             "the reading, plus the coordination on top, and coordination "
             "on the strong model is the expensive part. Anthropic's "
             "research system paid fifteen times the tokens for its 90.2 "
             "percent gain: a good trade for a hard question, a terrible "
             "one for a lookup. Class question: which row would you delete "
             "from your own design first, and what eval would you run "
             "before adding it back?")

    # 19. Lab 4: subagents
    s = ds.image_slide(
        prs,
        "Lab 4: a subagent is one Markdown file with its own context",
        f"{FIGS}/s4_lab_subagent.png",
        kicker="Lab 4 - Claude Code subagents",
        bullets=[
            "You type: 'Use the repo-researcher subagent to find the Python "
            "version of the notebook workflow'",
            "You see: Python 3.12, quoting .github/workflows/notebooks.yml; "
            "2 turns, total_cost_usd 0.1709",
            "Inside: 7 tool calls, one 2,583-character Read; out: a single "
            "3,284-character result",
            "modelUsage bills each model: main agent 0.1168 USD, the sonnet "
            "subagent 0.0541 USD",
            "Trap question (the dean): 'not in the repository', 0.2455 USD; "
            "it only searched lab/ - teach delegation",
            "In plain words: the notebook's delegate tool, shipped as a "
            "feature you configure in a file",
        ],
        caption=LAB + " Files: lab/.claude/agents/*.md, log "
                "lab/.claude/tool-calls.log (lab guide, section 1).",
    )
    notes(s, "Left is the whole subagent: YAML front matter and a system "
             "prompt. Map the fields to the notebook - name is "
             "Agent(name=...), description is the delegate tool's docstring "
             "written for a machine, tools is the allow-list, model is "
             "WORKER_MODEL, maxTurns is max_turns. Right is the PostToolUse "
             "log after the first observed run: seven tool calls happened "
             "inside the subagent, including a 2,583-character file read, "
             "and the main agent received a single 3,284-character result. "
             "That is section 1 of the notebook in eight log lines. The "
             "trap question is the second lesson: the subagent answered "
             "correctly that the repository does not contain a dean, but it "
             "searched only the lab folder, because --add-dir allows a read "
             "and does not tell the model where to look - teach the "
             "orchestrator how to delegate. Class question: which front "
             "matter field would you change so that the fact-checker "
             "subagent can never be given write tools by mistake?")

    # 20. Lab 4: hooks, permissions, teams
    s = ds.two_col_slide(
        prs,
        "Lab 4: hooks are the brake, rules the law, teams a preview",
        ("Hooks and rules in .claude/settings.json", [
            "PreToolUse on Bash runs block_env_access.py: any command "
            "touching .env exits 2 and the reason goes back to the model",
            "Run 2, 'cat ../../.env': the model refused on its own, 1 turn, "
            "0.1500 USD. CLAUDE.md held; on its own it is the weakest layer",
            "Run 4, 'check the size of ../../.env': the model tried stat, "
            "the hook blocked it, 2 turns, 0.2522 USD; it reported the "
            "block and offered alternatives",
            "PostToolUse on * logs tool, input and result size, never the "
            "result; the blocked call left no line",
            "deny: Read(**/.env) blocks in every mode; a blocking hook beats "
            "an allow rule such as Bash(cat *)",
        ]),
        ("Modes, agent teams and the bill", [
            "--permission-mode: default (reads only), acceptEdits, plan, "
            "auto, dontAsk, bypassPermissions",
            "For scripts and CI: dontAsk plus an exact --allowedTools list; "
            "anything else is denied, not asked",
            "Agent teams are experimental and off: \"env\": "
            "{\"CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS\": \"1\"} in "
            "settings.json switches them on",
            "Teams need an interactive terminal; named subagents become "
            "teammates; the docs quote about 7x the tokens of a session",
            "/usage shows the session bill; the four recorded -p runs cost "
            "0.8186 USD, mostly cache reads",
        ]),
        kicker="Lab 4 - hooks, permissions, agent teams",
        note=LAB + " Interactive-only behaviour is 'expected' per "
             "code.claude.com/docs. Files: lab/.claude/settings.json, "
             "lab/.claude/hooks/*.py (lab guide, sections 2 to 5).",
    )
    notes(s, "Two layers, two observed runs. Asked outright to cat the key "
             "file, the model refused by itself and no tool ran - the "
             "instruction file worked, and the lab says why that is not "
             "enough: a differently worded request, a long session or a "
             "compaction can make a sentence go missing. Asked for something "
             "that sounds harmless - does the file exist and how big is it - "
             "the model tried, and the hook stopped the call before it ran; "
             "the model read the reason and adapted instead of retrying, "
             "which is notebook 03's is_error tool result as a product. "
             "Notice the log has no line for the blocked call: the brakes and "
             "the dashboard are different instruments. On the right, the "
             "modes are the permission argument with more shapes, dontAsk is "
             "what you use when nobody is there to answer, and agent teams "
             "are one environment variable away - interactive only, so the "
             "recorded runs could not form one. Class question: which of "
             "these four controls would you add to your notebook 03 harness "
             "first, and why that one?")

    # 21. The eight pieces mapped
    s = ds.table_slide(
        prs,
        "The eight pieces of a harness - and what you built for each",
        ["Piece", "In the car", "What you built (notebooks 01 to 04, labs 2 and 4)"],
        [
            ["1. Model", "the engine",
             "Nb 01: messages.create on the raw SDK and its cost; nb 02: three Claude models"],
            ["2. Context", "dashboard and mirrors",
             "Nb 02: count_tokens, growing session, compaction, notes; nb 04: a small lead"],
            ["3. Tools", "the trailer hitch",
             "Nb 01: list_files, read_file as JSON schemas, 40-line loop; nb 02: vague tool"],
            ["4. Skills", "the glovebox manuals",
             "Nb 02: a real SKILL.md, catalog vs body tokens, load_skill; lab 2: Claude Code"],
            ["5. The loop", "steering wheel and pedals",
             "Nb 01: loop by hand, then tool_runner; nb 03: Agent.run() stops; nb 04: budget"],
            ["6. Guardrails", "brakes, seatbelts, airbags",
             "Nb 03: before_tool, validate_answer, deny_risk; nb 04: cap; lab 4: PreToolUse"],
            ["7. Orchestration", "convoy and job board",
             "Nb 03: five workflow patterns; nb 04: delegate, TaskBoard, handoff; lab 4: teams"],
            ["8. Evals and observability", "the logbook",
             "Nb 03: eval suite over three configs, CI workflow; nb 04: cost table, a judge"],
        ],
        kicker="Anatomy, revisited",
        note="Canon order from Session 1. The harness package sits next to the notebooks; "
             "the lab folder holds the Claude Code artefacts.",
        col_widths=[2.0, 2.2, 7.9],
    )
    notes(s, "Close the loop with Session 1's anatomy slide: the same eight "
             "pieces, now with the notebook or lab where each one was built "
             "on real components - the Anthropic SDK, the harness package, "
             "Claude Code and GitHub Actions. Students have run every one of "
             "them. The point of the middle column is that the car metaphor "
             "was never decoration - each piece answers one question a "
             "driver would ask. Class question: which piece would you replace "
             "first if this harness went to production, and with what?")

    # 22. Close
    s = ds.close_slide(
        prs,
        "What you can now build",
        [
            "A harness on the real SDK: model + loop + tools + skills + "
            "guardrails + traces, the key in a git-ignored .env",
            "A workflow when the path is known; an agent when it is not",
            "Sub-agents to keep the lead small; teams for parallel tasks; "
            "handoffs for specialists - each with its measured price",
            "An eval suite that puts a pass rate and a price on every change",
            "Guards that run in code: risk levels, validators, max turns, "
            "token budgets, hooks",
            "The discipline: instruction files, executable guards, evals in "
            "CI, observability, permission design",
            "The same parts in Claude Code: SKILL.md, .claude/agents, "
            "settings.json hooks and rules, agent teams",
        ],
        course=COURSE,
    )
    notes(s, "End on capability, not theory. Every line is something they "
             "ran this module, on real models and real tools, with the bill "
             "printed after every experiment. The last line is the "
             "invitation: the parts they built by hand exist as product "
             "features, and now they can read those features for what they "
             "are. Class question: what is the first agent you would build "
             "with this, and which of the eight pieces would you spend most "
             "of your time on?")
    return prs


if __name__ == "__main__":
    make_isolate_fig()
    make_shapes_fig()
    make_signposts_fig()
    make_lead_context_fig()
    make_team_board_fig()
    make_handoff_fig()
    make_runaway_fig()
    make_subagent_fig()
    deck = slides()
    out = "../m5-session-4-sub-agents-teams-and-the-discipline.pptx"
    ds.save_deck(deck, out, FOOTER, author="M5 Harness Engineering course")
    print("Slides:", len(deck.slides._sldIdLst))
    print("Saved:", os.path.abspath(out))
