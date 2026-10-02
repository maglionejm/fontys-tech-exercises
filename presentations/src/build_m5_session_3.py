"""Build deck: M5 Session 3 - Building a Harness.

Theory: the loop with stop conditions, hooks and permissions, the five
workflow patterns, evals, observability and OpenAI's harness lessons.
Practice: notebook 03 on the real `harness/` package and real Claude models
(the package modules, the three recorded exits, guardrails that fired, the
five patterns with a price, the A/B/C eval suite on 14 cases, the CI workflow).
Every Part 2 number is quoted from the executed notebook's outputs (recorded
run of 30 Sep 2026 on claude-opus-5 with claude-sonnet-5 workers); every
external fact is attributed on the slide.
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
FOOTER = "M5 Session 3 - Building a Harness"
REC = ("Figures on this slide are quoted from the recorded run of notebook 03 "
       "on 30 Sep 2026 (claude-opus-5 main agents, claude-sonnet-5 workers); "
       "live runs vary, so compare shapes and reasons, not digits.")


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
def make_loop_fig():
    """The agent loop with its three exits (Claude Agent SDK naming)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    box(ax, 0.3, 3.9, 2.9, 1.4, "1. GATHER CONTEXT",
        "system prompt, history,\ntool results, skills")
    box(ax, 3.6, 3.9, 2.9, 1.4, "2. TAKE ACTION",
        "model answers or asks for tools;\nthe harness runs them")
    box(ax, 1.95, 0.9, 2.9, 1.4, "3. VERIFY WORK",
        "validators and hooks\ncheck the result")
    arrow(ax, (3.2, 4.6), (3.6, 4.6))
    arrow(ax, (5.05, 3.9), (4.45, 2.3), rad=-0.15)
    arrow(ax, (2.35, 2.3), (1.75, 3.9), rad=-0.15, color=pal["navy"], lw=1.8)
    ax.text(1.35, 3.1, "repeat", ha="right", va="center", color=pal["navy"],
            fontsize=10, fontweight="bold")
    # exits
    arrow(ax, (4.9, 1.6), (5.55, 1.6), color=pal["gray"], lw=1.4)
    ax.plot([5.6, 5.6], [0.6, 2.6], color=pal["gray"], lw=1.2)
    exits = [(2.6, "DONE", "answer accepted", pal["blue"]),
             (1.6, "MAX_TURNS", "turn limit reached", pal["navy"]),
             (0.6, "BUDGET", "over the token cap", pal["gray"])]
    for y, head, sub, c in exits:
        ax.plot([5.6, 5.9], [y, y], color=pal["gray"], lw=1.2)
        ax.add_patch(FancyBboxPatch((5.9, y - 0.36), 3.8, 0.72,
                                    boxstyle="round,pad=0.03", facecolor=c,
                                    edgecolor=c))
        ax.text(6.1, y, head, va="center", color="white", fontweight="bold",
                fontsize=10.5)
        ax.text(7.75, y, sub, va="center", color="white", fontsize=9.2)
    ax.text(7.8, 3.55, "three exits in your code", ha="center",
            color=pal["gray"], fontsize=10, style="italic")
    ax.text(7.8, 3.2, "(the API adds two: refusal, max_tokens)", ha="center",
            color=pal["gray"], fontsize=8.6, style="italic")
    ax.text(5.0, 5.75, "the loop: gather context, take action, verify work, "
            "repeat", ha="center", color=pal["gray"], fontsize=10)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s3_loop.png")
    plt.close(fig)


def make_checkpoints_fig():
    """Three checkpoints where guardrails run: before input, before a tool,
    after the answer. Risk levels read / write / danger in the middle."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    strip = [("user input", 0.2), ("model decides", 2.75), ("tool runs", 5.3),
             ("answer out", 7.85)]
    for label, x in strip:
        box(ax, x, 5.0, 1.8, 0.6, label, hs=9.5, fc="white", ec=pal["sky"])
    for i, x in enumerate([2.375, 4.925, 7.475]):
        arrow(ax, (x - 0.37, 5.3), (x + 0.37, 5.3), color=pal["gray"], lw=1.2,
              ms=10)
        ax.scatter([x], [5.3], s=330, color=pal["blue"], zorder=5)
        ax.text(x, 5.3, str(i + 1), ha="center", va="center", color="white",
                fontweight="bold", fontsize=10, zorder=6)
    panels = [
        (0.2, "1  BEFORE INPUT",
         ["relevance: the agent's job?",
          "safety: jailbreak or injection?",
          "PII filter: personal data?",
          "outcome: refuse or escalate"],
         "the car: does this trip\nmake sense at all?"),
        (3.5, "2  BEFORE A TOOL RUNS", None,
         "the car: a speed limiter\non the risky pedals"),
        (6.8, "3  AFTER THE ANSWER",
         ["validate: format, sources",
          "present, no secrets inside",
          "reject: retry with feedback",
          "repeat failure: escalate"],
         "the car: inspection before\nleaving the garage"),
    ]
    for x, head, lines, car in panels:
        ax.add_patch(FancyBboxPatch((x, 0.35), 3.0, 4.15,
                                    boxstyle="round,pad=0.03",
                                    facecolor="white", edgecolor=pal["blue"],
                                    lw=1.4))
        ax.add_patch(FancyBboxPatch((x, 3.9), 3.0, 0.6,
                                    boxstyle="round,pad=0.03",
                                    facecolor=pal["navy"],
                                    edgecolor=pal["navy"]))
        ax.text(x + 1.5, 4.2, head, ha="center", va="center", color="white",
                fontweight="bold", fontsize=9.8)
        if lines:
            for j, line in enumerate(lines):
                ax.text(x + 0.18, 3.5 - j * 0.48, line, va="center",
                        color=pal["ink"], fontsize=8.6)
        else:
            ladder = [("read", "run it", pal["sky"], pal["navy"]),
                      ("write", "ask first", pal["blue"], "white"),
                      ("danger", "deny by default", pal["navy"], "white")]
            for j, (lvl, act, c, tc) in enumerate(ladder):
                y = 3.25 - j * 0.5
                ax.add_patch(FancyBboxPatch((x + 0.2, y), 2.6, 0.4,
                                            boxstyle="round,pad=0.02",
                                            facecolor=c, edgecolor=c))
                ax.text(x + 0.35, y + 0.2, lvl, va="center", color=tc,
                        fontweight="bold", fontsize=9)
                ax.text(x + 1.35, y + 0.2, act, va="center", color=tc,
                        fontsize=8.6)
            ax.text(x + 0.18, 1.62, "plus: sandbox, approval gate,",
                    va="center", color=pal["ink"], fontsize=8.6)
            ax.text(x + 0.18, 1.3, "hooks that deny with a reason",
                    va="center", color=pal["ink"], fontsize=8.6)
        ax.text(x + 1.5, 0.72, car, ha="center", va="center",
                color=pal["gray"], fontsize=8.4, style="italic",
                linespacing=1.2)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s3_checkpoints.png")
    plt.close(fig)


def make_patterns_fig():
    """Five workflow patterns as five small shape diagrams (Anthropic 2024)."""
    fig, axes = plt.subplots(1, 5, figsize=(11.5, 5))
    bw, bh = 1.05, 0.55

    def b(ax, x, y, label, fc=None, ec=None, tc=None, w=bw):
        box(ax, x, y, w, bh, label, fc=fc or pal["panel"], ec=ec or pal["blue"],
            hc=tc or pal["navy"], hs=8.3)

    # 1 prompt chaining
    ax = axes[0]
    for i, lab in enumerate(["step 1", "step 2", "step 3"]):
        b(ax, 0.2 + i * 1.3, 1.9, lab)
        if i:
            arrow(ax, (0.2 + i * 1.3 - 0.25, 2.17), (0.2 + i * 1.3, 2.17), ms=10)
    ax.text(2.0, 1.45, "gate between steps", ha="center", color=pal["gray"],
            fontsize=8)
    # 2 routing
    ax = axes[1]
    b(ax, 0.1, 1.9, "input", fc="white", ec=pal["sky"])
    b(ax, 1.45, 1.9, "router", fc=pal["blue"], ec=pal["blue"], tc="white")
    arrow(ax, (1.15, 2.17), (1.45, 2.17), ms=10)
    for y, lab in [(3.1, "agent A"), (1.9, "agent B"), (0.7, "agent C")]:
        b(ax, 2.85, y, lab)
        arrow(ax, (2.5, 2.17), (2.85, y + 0.27), ms=10, rad=0.0)
    # 3 parallelization
    ax = axes[2]
    b(ax, 0.05, 1.9, "input", fc="white", ec=pal["sky"])
    for y in (3.1, 1.9, 0.7):
        b(ax, 1.45, y, "worker")
        arrow(ax, (1.1, 2.17), (1.45, y + 0.27), ms=10)
        arrow(ax, (2.5, y + 0.27), (2.85, 2.17), ms=10)
    b(ax, 2.85, 1.9, "merge\nor vote", fc=pal["blue"], ec=pal["blue"], tc="white")
    # 4 orchestrator-workers
    ax = axes[3]
    b(ax, 1.45, 3.3, "orchestrator", fc=pal["blue"], ec=pal["blue"], tc="white",
      w=1.25)
    for x in (0.1, 1.55, 3.0):
        b(ax, x, 1.9, "worker", w=0.95)
        arrow(ax, (2.07, 3.3), (x + 0.47, 2.45), ms=10)
        arrow(ax, (x + 0.47, 1.9), (2.07, 1.05), ms=10)
    b(ax, 1.45, 0.5, "synthesizer", fc=pal["navy"], ec=pal["navy"], tc="white",
      w=1.25)
    # 5 evaluator-optimizer
    ax = axes[4]
    b(ax, 0.15, 1.9, "generator", w=1.4)
    b(ax, 2.35, 1.9, "evaluator", fc=pal["blue"], ec=pal["blue"], tc="white",
      w=1.4)
    arrow(ax, (1.55, 2.35), (2.35, 2.35), ms=10, rad=-0.35)
    arrow(ax, (2.35, 2.0), (1.55, 2.0), ms=10, rad=-0.35, color=pal["navy"])
    ax.text(1.95, 2.75, "draft", ha="center", color=pal["gray"], fontsize=8)
    ax.text(1.95, 1.6, "feedback", ha="center", color=pal["gray"], fontsize=8)
    arrow(ax, (3.05, 1.9), (3.05, 1.2), ms=10, color=pal["gray"])
    ax.text(3.05, 0.95, "accepted", ha="center", color=pal["gray"], fontsize=8)

    titles = [("Prompt chaining", "fixed steps,\neach easy to check"),
              ("Routing", "inputs of a few\nknown kinds"),
              ("Parallelization", "independent pieces,\nor a vote"),
              ("Orchestrator-workers", "sub-tasks you cannot\npredict in advance"),
              ("Evaluator-optimizer", "clear criteria,\nrevision pays off")]
    for ax, (t, use) in zip(axes, titles):
        ax.set_title(t, fontsize=12)
        ax.text(2.0, -0.05, use, ha="center", va="top", color=pal["gray"],
                fontsize=9.2, linespacing=1.25)
        ax.set_xlim(0, 4)
        ax.set_ylim(-0.9, 4.1)
        ax.axis("off")
    fig.tight_layout(w_pad=0.6)
    fig.savefig(f"{FIGS}/s3_patterns.png")
    plt.close(fig)


def make_evals_fig():
    """An eval = a task + graders + an outcome; a suite = a pass rate."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    box(ax, 0.2, 3.9, 2.0, 1.2, "TASK", "a question and an\nexpected outcome")
    box(ax, 2.75, 3.9, 2.6, 1.2, "AGENT UNDER TEST",
        "the harness you\nare evaluating")
    box(ax, 5.9, 3.9, 2.0, 1.2, "OUTCOME", "answer + trace")
    arrow(ax, (2.2, 4.5), (2.75, 4.5))
    arrow(ax, (5.35, 4.5), (5.9, 4.5))
    arrow(ax, (6.9, 3.9), (6.9, 3.3))
    ax.add_patch(FancyBboxPatch((5.3, 1.5), 3.2, 1.8, boxstyle="round,pad=0.04",
                                facecolor="white", edgecolor=pal["blue"],
                                lw=1.5))
    ax.text(6.9, 3.05, "GRADERS", ha="center", va="center", color=pal["navy"],
            fontweight="bold", fontsize=11)
    for j, line in enumerate(["code: contains, source_file, found",
                              "LLM judge: calibrated on humans",
                              "human review: the gold standard"]):
        ax.text(5.5, 2.6 - j * 0.42, line, va="center", color=pal["ink"],
                fontsize=8.6)
    arrow(ax, (8.5, 2.4), (8.9, 2.4))
    ax.add_patch(FancyBboxPatch((8.9, 1.95), 1.0, 0.9, boxstyle="round,pad=0.03",
                                facecolor=pal["blue"], edgecolor=pal["blue"]))
    ax.text(9.4, 2.4, "PASS\nFAIL", ha="center", va="center", color="white",
            fontweight="bold", fontsize=9.5)
    for y, head, sub in [(2.55, "OUTCOME grading", "did it reach the right result?"),
                         (1.55, "TRAJECTORY grading", "did it take a sane path?")]:
        ax.add_patch(FancyBboxPatch((0.2, y), 4.6, 0.75, boxstyle="round,pad=0.03",
                                    facecolor=pal["panel"], edgecolor=pal["sky"]))
        ax.text(0.4, y + 0.5, head, va="center", color=pal["navy"],
                fontweight="bold", fontsize=9.5)
        ax.text(0.4, y + 0.2, sub, va="center", color=pal["gray"], fontsize=8.8)
    ax.add_patch(FancyBboxPatch((0.2, 0.3), 9.7, 0.75, boxstyle="round,pad=0.03",
                                facecolor=pal["navy"], edgecolor=pal["navy"]))
    ax.text(5.05, 0.675, "many cases  ->  one pass rate;  re-run on every "
            "change, like tests in CI", ha="center", va="center", color="white",
            fontweight="bold", fontsize=10)
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.4)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s3_evals.png")
    plt.close(fig)


def make_exits_fig():
    """Three recorded runs of notebook 03, section 1: one trace per exit.

    Every row and number is quoted from the notebook's printed traces
    (cells 6, 8 and 10 of the executed notebook, recorded 30 Sep 2026)."""
    fig, ax = plt.subplots(figsize=(11, 5))
    cols = [
        (0.15, "DONE", "researcher: max_turns=8, effort=medium",
         "Which Python version does the notebook workflow\ninstall, how many notebooks in its matrix?",
         [("1", "model", "679 / 66", "tool_use"),
          ("1", "tool", "list_files", ".github/workflows"),
          ("2", "model", "775 / 60", "tool_use"),
          ("2", "tool", "read_file", "notebooks.yml"),
          ("3", "model", "2082 / 154", "end_turn")],
         "stopped_because='done'  |  3 turns  |  8.5 s",
         "3536 in / 280 out tokens  |  $0.02468",
         "answer: Python 3.12, 9 notebooks,\nsource .github/workflows/notebooks.yml",
         pal["blue"]),
        (3.85, "MAX_TURNS", "same agent, max_turns=2",
         "Same question. Two laps, then the harness\ncuts the engine whatever the model wants.",
         [("1", "model", "679 / 66", "tool_use"),
          ("1", "tool", "list_files", ".github/workflows"),
          ("2", "model", "775 / 60", "tool_use"),
          ("2", "tool", "read_file", "notebooks.yml"),
          ("-", "", "", "no third call")],
         "stopped_because='max_turns'  |  2 turns",
         "answer: ''  (both turns went to tools)",
         "the right outcome: a confused model\nis not given a hundred laps",
         pal["navy"]),
        (7.55, "BUDGET", "max_turns=6, max_input_tokens=3000",
         "Read README.md and tell me the three modules\nlisted in its repository layout.",
         [("1", "model", "658 / 67", "tool_use"),
          ("1", "tool", "read_file", "README.md"),
          ("2", "budget", "count_tokens", "7341 > 3000"),
          ("-", "", "", "call never made"),
          ("-", "", "", "")],
         "stopped_because='budget'  |  1 turn",
         "answer: ''  (the counted call was never sent)",
         "the trace names the count the API returned:\n'next call would send 7341 tokens > 3000'",
         pal["gray"]),
    ]
    w = 3.3
    for x, head, setting, task, rows, line1, line2, line3, c in cols:
        ax.add_patch(FancyBboxPatch((x, 0.15), w, 4.7, boxstyle="round,pad=0.03",
                                    facecolor="white", edgecolor=pal["sky"],
                                    lw=1.2))
        ax.add_patch(FancyBboxPatch((x, 4.4), w, 0.45, boxstyle="round,pad=0.03",
                                    facecolor=c, edgecolor=c))
        ax.text(x + 0.15, 4.625, head, va="center", color="white",
                fontweight="bold", fontsize=11)
        ax.text(x + 0.15, 4.18, setting, va="center", color=pal["navy"],
                fontsize=8.2, fontweight="bold")
        ax.text(x + 0.15, 3.78, task, va="center", color=pal["gray"],
                fontsize=7.8, style="italic", linespacing=1.25)
        # trace header
        for hx, label in [(0.15, "turn"), (0.5, "kind"), (1.15, "name / tokens"),
                          (2.15, "detail")]:
            ax.text(x + hx, 3.38, label, va="center", color=pal["navy"],
                    fontweight="bold", fontsize=7.8)
        ax.plot([x + 0.1, x + w - 0.1], [3.24, 3.24], color=pal["sky"], lw=0.8)
        for j, (turn, kind, name, detail) in enumerate(rows):
            y = 3.03 - j * 0.32
            if kind == "budget":
                ax.add_patch(FancyBboxPatch((x + 0.08, y - 0.14), w - 0.16, 0.28,
                                            boxstyle="round,pad=0.01",
                                            facecolor=pal["panel"],
                                            edgecolor=pal["panel"]))
            weight = "bold" if kind in ("budget", "model") else "normal"
            ax.text(x + 0.2, y, turn, va="center", color=pal["ink"], fontsize=8.2)
            ax.text(x + 0.5, y, kind, va="center", color=pal["ink"], fontsize=8.2,
                    fontweight=weight)
            ax.text(x + 1.15, y, name, va="center", color=pal["ink"], fontsize=8.2)
            ax.text(x + 2.15, y, detail, va="center", color=pal["gray"],
                    fontsize=7.6, style="italic" if not kind else "normal")
        ax.add_patch(FancyBboxPatch((x + 0.08, 0.25), w - 0.16, 1.15,
                                    boxstyle="round,pad=0.02",
                                    facecolor=pal["panel"], edgecolor=pal["panel"]))
        ax.text(x + 0.18, 1.22, line1, va="center", color=pal["navy"],
                fontweight="bold", fontsize=8.2)
        ax.text(x + 0.18, 0.94, line2, va="center", color=pal["ink"], fontsize=8)
        ax.text(x + 0.18, 0.55, line3, va="center", color=pal["gray"],
                fontsize=7.6, linespacing=1.25)
    ax.set_xlim(0, 11)
    ax.set_ylim(0, 5)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s3_exits.png")
    plt.close(fig)


def make_scoreboard_fig():
    """A/B/C pass rates and suite cost, quoted from the notebook's scoreboard
    (cells 35 and 36: 3/14, 14/14, 13/14; $0.0645, $0.9765, $1.1275)."""
    fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7.6, 4.8))
    labels = ["A: no tools", "B: tools", "C: tools + validator"]
    colors = [pal["gray"], pal["sky"], pal["blue"]]
    rates = [21.4, 100.0, 92.9]
    counts = ["3/14 (21%)", "14/14 (100%)", "13/14 (93%)"]
    ax1.barh(labels, rates, color=colors, height=0.55)
    for i, text in enumerate(counts):
        ax1.text(rates[i] + 1.5, i, text, va="center", color=pal["ink"],
                 fontsize=11, fontweight="bold")
    ax1.invert_yaxis()
    ax1.set_xlim(0, 135)
    ax1.set_xlabel("cases passed (%)", fontsize=10)
    ax1.set_title("Pass rate per harness configuration, same model", loc="left",
                  fontsize=12)
    costs = [0.0645, 0.9765, 1.1275]
    texts = ["$0.0645  (5,975 input tokens)", "$0.9765  (177,804 input tokens)",
             "$1.1275  (207,336 input tokens)"]
    ax2.barh(labels, costs, color=colors, height=0.55)
    for i, text in enumerate(texts):
        ax2.text(costs[i] + 0.02, i, text, va="center", color=pal["ink"],
                 fontsize=10.5, fontweight="bold")
    ax2.invert_yaxis()
    ax2.set_xlim(0, 2.05)
    ax2.set_xlabel("cost of the whole 14-case suite (USD, from response.usage)",
                   fontsize=10)
    ax2.set_title("Cost per harness configuration", loc="left", fontsize=12)
    for ax in (ax1, ax2):
        ax.tick_params(axis="y", labelsize=10.5)
        ax.tick_params(axis="x", labelsize=9)
    fig.tight_layout(h_pad=1.6)
    fig.savefig(f"{FIGS}/s3_scoreboard.png")
    plt.close(fig)


# ---------------------------------------------------------------- slides
def slides():
    prs = ds.new_deck()

    # 1. Title
    s = ds.title_slide(
        prs,
        "Session 3 of 4",
        "Building a Harness",
        "Sessions 1 and 2 named the pieces. Today we assemble them: a loop "
        "that knows when to stop, guards that run outside the model, five "
        "workflow patterns, and an eval suite that puts a number on every "
        "change. Then notebook 03 runs one real model through three "
        "harnesses on this repository and reads the scoreboard honestly.",
        course=COURSE,
    )
    notes(s, "Frame the session: last time we looked at the parts on the "
             "bench - models, context, tools, skills. Today we bolt them into "
             "a car that drives and, more importantly, brakes. Part 1 is the "
             "theory of the loop, guardrails, patterns and evals; Part 2 is "
             "notebook 03, where the harness package runs on real Claude "
             "models and the same model passes 3, 14 and 13 of 14 cases "
             "depending only on the harness around it. Class question: if "
             "the same model gives three different results, what exactly are "
             "we testing?")

    # 2. Part 1 divider
    s = ds.section_slide(
        prs, "01", "Part 1 - The theory: the loop, the guards, the proof",
        "How an agent runs, where the checks go, which pattern to pick, and "
        "how you know any of it works.")
    notes(s, "Four ideas in Part 1: the loop and its exits, guardrails at "
             "three checkpoints, five workflow patterns, and evals plus "
             "traces as the proof. Class question: which of the eight pieces "
             "from Session 1 have we not yet built?")

    # 3. The loop
    s = ds.image_slide(
        prs,
        "An agent is a loop: gather context, take action, verify work, repeat",
        f"{FIGS}/s3_loop.png",
        kicker="The loop",
        bullets=[
            "In plain words: the loop is the steering wheel and pedals; "
            "the model is the engine",
            "Gather context: system prompt, history, tool results, skills - "
            "all the model sees",
            "Take action: the model answers or asks for tools; the harness "
            "runs them",
            "Verify work: validators and hooks check the result before it "
            "counts",
            "Three exits in your code: done, max_turns, budget - a loop "
            "without exits is a runaway car",
            "The harness package: Agent.run() in loop.py is about forty "
            "lines that do exactly this",
        ],
        caption="Illustration. Loop steps as named by Anthropic, Claude Agent "
                "SDK, Sep 2025. Exits as implemented in harness/loop.py "
                "(stopped_because); refusal and max_tokens come from the API.",
    )
    notes(s, "Walk the picture clockwise: gather, act, verify, repeat. Point "
             "at the three exits and insist on them - most demos online have "
             "only 'done'. Max turns protects against a model that never "
             "finishes; budget protects your wallet, and it asks the API's "
             "count_tokens endpoint before sending the call. The API itself "
             "adds refusal and max_tokens as stop reasons, which the harness "
             "records so a cut answer is never mistaken for a finished one. "
             "In the package this is Agent.run() in harness/loop.py: a "
             "for-loop over turns, one messages.create call, tool execution, "
             "validators, and the RunResult with stopped_because. Class "
             "question: which exit would you hit first if the model kept "
             "calling the same tool with the same arguments?")

    # 4. Hooks and permissions
    s = ds.image_slide(
        prs,
        "Guardrails run outside the model at three checkpoints",
        f"{FIGS}/s3_checkpoints.png",
        kicker="Hooks and permissions",
        bullets=[
            "In plain words: a guardrail is a check that runs outside the "
            "model - brakes, seatbelts, airbags",
            "Checkpoint 1, before input: relevant, safe, free of personal "
            "data?",
            "Checkpoint 2, before a tool runs: risk level read, write or "
            "danger; run, ask or deny",
            "Checkpoint 3, after the answer: validate format and sources; "
            "retry once on failure",
            "The approval paradox: 93% of permission prompts get approved - "
            "a prompt is not a control",
            "The harness package: run_shell is risk 'danger', denied by "
            "default; Hooks.validate_answer retries once",
        ],
        caption="Illustration. Checkpoints and risk ratings: OpenAI, A "
                "practical guide to building agents, Apr 2025. Approval "
                "paradox: Marmelab, State of AI Harness Engineering, Sep 2026.",
    )
    notes(s, "Three places to put a check, and only three. Before input is "
             "cheap and catches the obvious. Before a tool is where the "
             "damage happens: reading is safe, writing needs a look, "
             "deleting or running code is denied unless someone opts in. "
             "After the answer is where you validate and retry. Then the "
             "paradox: when people are asked to approve 93% of the time, "
             "they stop reading - the prompt becomes theatre. Real controls "
             "are code, not questions. Class question: which of the three "
             "checkpoints would have stopped an agent that emailed a "
             "customer by mistake?")

    # 5. Seven guardrail types
    s = ds.table_slide(
        prs,
        "OpenAI names seven kinds of guardrail - most are plain code",
        ["Guardrail", "What it checks", "In plain words (the car)"],
        [
            ["Relevance classifier", "Is the request inside the agent's job?",
             "Refuse a detour off the route"],
            ["Safety classifier", "Jailbreaks and prompt injections in the input",
             "Lock the doors against hijacking"],
            ["PII filter", "Personal data about to leave in the output",
             "Tinted windows for the passengers"],
            ["Moderation", "Harmful or inappropriate content, in or out",
             "The rules of the road"],
            ["Tool safeguards", "A risk rating per tool: read, write, "
             "irreversible; approval gates", "A speed limiter on the risky pedals"],
            ["Rules-based protections", "Blocklists, regex, input length limits",
             "Fixed bollards: no judgment needed"],
            ["Output validation", "Does the answer match format, facts, tone?",
             "Inspection before leaving the garage"],
        ],
        kicker="The seven guardrails",
        note="OpenAI, A practical guide to building agents, Apr 2025. The "
             "guide adds human escalation on failure thresholds and before "
             "high-risk actions.",
        col_widths=[2.2, 4.6, 3.4],
    )
    notes(s, "Read the table as a shopping list, not a theory. Two of the "
             "seven need a model (the classifiers); the other five are "
             "regular code - regexes, lookups, schemas. That is the point: "
             "most safety is deterministic. In the harness package the tool "
             "safeguard is the risk level on each @tool plus the permission "
             "rule, the rules-based protection is a before_tool hook, and "
             "output validation is validate_answer. Class question: which "
             "two of the seven would you add first to a homework-helper "
             "agent, and why those two?")

    # 6. Five workflow patterns
    s = ds.image_slide(
        prs,
        "Five workflow patterns cover most of what people call 'agents'",
        f"{FIGS}/s3_patterns.png",
        kicker="Workflow patterns",
        caption="Illustration. Five patterns from Anthropic, Building effective "
                "agents, Dec 2024. A workflow is a path you wrote in code, "
                "with model steps inside; an agent chooses its own path.",
    )
    notes(s, "Left to right, increasing freedom. Chaining: fixed steps with a "
             "check between them. Routing: a cheap classifier sends each "
             "input to a specialist. Parallelization: split the work or ask "
             "several times and vote. Orchestrator-workers: a model decides "
             "the sub-tasks, code runs the workers, a model merges. "
             "Evaluator-optimizer: one produces, one critiques, until "
             "accepted. In plain words: the first four are routes drawn on "
             "the map; only an agent chooses the roads itself. Class "
             "question: which pattern is a spell-checker that rewrites a "
             "paragraph until a grammar tool is satisfied?")

    # 7. When to use which
    s = ds.table_slide(
        prs,
        "Simplest pattern first - the model drives when the path is unknown",
        ["Pattern", "Use when", "Notebook 03 example"],
        [
            ["Prompt chaining", "Fixed steps, each easy to check",
             "researcher, then a judge with a pass/reason schema"],
            ["Routing", "Inputs fall into a few known kinds",
             "router enum: calculator or researcher"],
            ["Parallelization", "Independent pieces, or a vote for robustness",
             "three sub-questions, three workers in a thread pool"],
            ["Orchestrator-workers", "You cannot predict the sub-tasks",
             "planner lists the subtasks, workers answer, synthesizer merges"],
            ["Evaluator-optimizer", "Clear criteria and revision pays off",
             "SECURITY.md summary: draft, review, revise, two rounds max"],
            ["Agent (the model drives)", "Open-ended task, unknown number of steps",
             "the researcher loop: list_files, read_file, answer"],
        ],
        kicker="Workflows vs agents",
        note="Cost rule of thumb: a chat is 1x, a single agent about 4x, a "
             "multi-agent system about 15x the tokens (Anthropic, How we built "
             "our multi-agent research system, Jun 2025). Start simple "
             "(Anthropic, Dec 2024).",
        col_widths=[2.4, 3.6, 4.2],
    )
    notes(s, "The rule from Anthropic's post is blunt: find the simplest "
             "solution possible and add complexity only when it "
             "demonstrably improves results. Workflows are predictable and "
             "cheap to test; agents are flexible and expensive. The right "
             "column maps each pattern to a cell the students will run on "
             "real Claude models in notebook 03. Class question: a support "
             "bot that must answer billing, shipping and returns questions - "
             "workflow or agent, and which pattern?")

    # 8. Evals
    s = ds.image_slide(
        prs,
        "An eval is a task, a grader and an outcome, measured repeatedly",
        f"{FIGS}/s3_evals.png",
        kicker="Evals",
        bullets=[
            "In plain words: an eval is a unit test for behaviour, not for "
            "code",
            "Outcome grading: did it get there? Trajectory grading: did it "
            "take a sane path?",
            "Code graders first: contains, source_file, found, used_tool, "
            "max_turns. LLM judges must be calibrated against humans",
            "One case proves nothing; a suite gives a pass rate you can "
            "compare",
            "Evals run like tests in CI: every harness change re-runs the "
            "suite",
        ],
        caption="Illustration. Anthropic, Demystifying evals for AI agents, "
                "Jan 2026. Grader names as in harness/evals.py and "
                "evals/cases.yaml.",
    )
    notes(s, "Students know unit tests; an eval is the same idea for a "
             "system that is not deterministic, so you measure a rate over "
             "many cases instead of one pass/fail. Outcome grading asks "
             "whether the answer is right; trajectory grading asks whether "
             "the steps were reasonable - a right answer reached by "
             "guessing is a failure waiting to happen. Code graders are "
             "cheap and exact; LLM judges are flexible but drift, so you "
             "calibrate them on human-labelled examples. Class question: "
             "what would the grader be for 'the agent must never run code'?")

    # 9. Observability
    s = ds.two_col_slide(
        prs,
        "A trace records every step - without it you are guessing",
        ("A trace records", [
            "Every model call, with the real input and output tokens from "
            "response.usage",
            "Every tool call: name, arguments, result",
            "Denials, budget stops, validator notes, the final answer",
            "Turn numbers and seconds: where the time went",
            "In plain words: the dashboard and mirrors of the car",
        ]),
        ("What it buys you", [
            "Cost accounting: tokens times the model's price per million - "
            "cost_usd(usage, model)",
            "Debugging: the exact step where a run went wrong",
            "Comparison: harness A vs B on the same tasks, side by side",
            "Budgets: alarms on tokens, turns and cost before they run away",
            "No trace, no engineering - only anecdotes",
        ]),
        kicker="Observability",
        note="Anthropic, Demystifying evals for AI agents, Jan 2026; Claude "
             "Agent SDK, Sep 2025. Trace and Event as in harness/trace.py; "
             "PRICES and cost_usd in harness/client.py.",
    )
    notes(s, "Every run in the notebooks ends with result.trace.show(): one "
             "line per event with the turn number, the kind, who acted and "
             "what happened, and the token counts are the ones the API "
             "returned, not estimates. That is observability at teaching "
             "scale; in production the same record goes to a tracing tool. "
             "The right column is why you bother: you cannot price, debug or "
             "compare what you did not record. Class question: a run cost "
             "ten times more than yesterday - which three lines of the trace "
             "would you read first?")

    # 10. OpenAI's harness lessons
    s = ds.two_col_slide(
        prs,
        "OpenAI's five-month experiment: the repository is the harness",
        ("What OpenAI did (Feb 2026)", [
            "Five months, about one million lines of production code",
            "Zero lines written by hand: Codex agents wrote all of it",
            "Humans steered: design docs, plans, reviews, taste",
            "The repository as system of record: docs, ADRs, exec plans, "
            "quality scores",
            "In plain words: everything the agent must know lives in the "
            "repo, versioned",
        ]),
        ("What they learned", [
            "Constraints enforced mechanically: custom linters and structural "
            "tests in CI",
            "A rule the agent can skip is a suggestion; a linter is a rule",
            "Harness engineering: deterministic scaffolding around "
            "probabilistic model steps",
            "Optimise the codebase for agents: legibility, fast feedback, "
            "small repairable failures",
            "Let the agent act and correct it afterwards; blocking on "
            "approval is the slow path",
        ]),
        kicker="Lessons from the field",
        note="OpenAI (Ryan Lopopolo), Harness engineering: leveraging Codex in "
             "an agent-first world, 11 Feb 2026.",
    )
    notes(s, "This is the post that named the discipline. The striking "
             "number is one million lines with zero by hand, but the lesson "
             "is the left-bottom bullet: the repository became the harness. "
             "Design docs, decision records and plans are written for the "
             "agent to read, and every constraint that matters is enforced "
             "by a linter or a structural test, because a markdown rule is "
             "optional to a model. Class question: what is one rule in your "
             "own projects that is only written down, and how would you "
             "turn it into a test?")

    # 11. Quote
    s = ds.quote_slide(
        prs,
        "Corrections are cheap, waiting is expensive.",
        "OpenAI, Harness engineering: leveraging Codex in an agent-first "
        "world, 11 Feb 2026 - on letting agents act inside mechanical guards "
        "instead of blocking on approval.",
    )
    notes(s, "Let the line sit for a moment. It only holds when the guards "
             "are real: an agent can be allowed to act freely because the "
             "linters, tests and permissions catch the damage cheaply. "
             "Without those, waiting for approval is the only brake you "
             "have - and the approval paradox says that brake wears out. "
             "Class question: for which actions would you still insist on "
             "waiting, whatever the cost?")

    # 12. The enforcement gap
    s = ds.big_number_slide(
        prs,
        "Most harness rules are written down - almost none are enforced",
        "4.4%",
        "of security rules in harness repositories are backed by a real "
        "control; the rest are text the agent may ignore",
        foot="Also: 63% of large projects ship instruction files, only a "
             "handful enforce them; 60% of harnesses have no tests or evals. "
             "Marmelab, The State of AI Harness Engineering 2026, Sep 2026.",
        kicker="The enforcement gap",
    )
    notes(s, "Put the two halves of the session together: OpenAI says "
             "enforce mechanically; the field survey says almost nobody "
             "does. 4.4% means that if you write twenty security rules in "
             "your CLAUDE.md, statistically one of them has a control behind "
             "it. And 60% of harnesses cannot even tell whether a change made "
             "them better or worse. This is the gap the course wants you to "
             "close. Class question: which is worse - a rule with no control, "
             "or no rule at all?")

    # 13. Part 2 divider
    s = ds.section_slide(
        prs, "02", "Part 2 - The practice: notebook 03",
        "A readable package, three recorded exits, guardrails that fired for "
        "real, five patterns with a price, and an eval suite of fourteen "
        "cases run live on Claude - then the failures, read honestly.")
    notes(s, "Open notebook 03. Everything in Part 2 ran on real Claude "
             "models against this repository, with the key read from .env; "
             "the recorded run cost about two and a half dollars, most of it "
             "the eval suite. Live runs vary, so the point of each slide is "
             "the shape of what happened and the reason, not the exact "
             "digit. Class question: before we run it, what pass rate do you "
             "expect from the model without tools?")

    # 14. The package
    s = ds.table_slide(
        prs,
        "The harness package: eight short files, one per piece of the car",
        ["File", "Lines", "Piece (the car)", "What it holds"],
        [
            ["client.py", "143", "the fuel",
             "load_client() reads the key from .env; MAIN_MODEL, WORKER_MODEL, "
             "PRICES, Usage, cost_usd()"],
            ["tools.py", "142", "the hands",
             "@tool builds the JSON schema from a signature and docstring; "
             "ToolRegistry; risk levels; deny_risk, allow_all"],
            ["hooks.py", "121", "the brakes",
             "Hooks(before_tool, after_tool, validate_answer); deny_paths, "
             "deny_risk_hook, require_sources, truncate_result"],
            ["trace.py", "81", "the dashboard",
             "Trace, Event, show(), summary(), to_frame()"],
            ["loop.py", "206", "the steering",
             "Agent.run(): the loop, the stop conditions, RunResult"],
            ["repo_tools.py", "156", "this module's tools",
             "list_files, read_file (path guards), write_note, read_notes, "
             "run_shell"],
            ["evals.py", "189", "the test track",
             "EvalCase, graders, run_evals, compare, Report"],
            ["cli.py", "107", "the ignition key",
             "python -m harness ask | eval | show"],
        ],
        kicker="Notebook 03 - the package",
        note="M5 - Harness Engineering/harness/, standard library plus "
             "anthropic, python-dotenv, pyyaml, pydantic. __init__.py "
             "re-exports everything; __main__.py starts the CLI. Line counts "
             "as of 2 Oct 2026.",
        col_widths=[1.5, 0.8, 1.9, 7.9],
    )
    notes(s, "A harness is a program, not a notebook, so the notebook "
             "imports a package the students can read in full. Go down the "
             "table with the car in mind: fuel, hands, brakes, dashboard, "
             "steering. Only loop.py is over two hundred lines, and the run "
             "method the students print is about forty of them. Nothing here "
             "is simulated: the client is the official Anthropic SDK, the "
             "tools are real functions on this repository, the prices are "
             "the list prices. Class question: which file would you open "
             "first to find out why a run stopped?")

    # 15. Three recorded exits
    s = ds.image_slide(
        prs,
        "Three recorded runs, three exits: done, max_turns, budget",
        f"{FIGS}/s3_exits.png",
        kicker="Notebook 03 - the loop's stop conditions",
        caption="How to read it: one trace per run, top to bottom; 'in / out' are "
                "the tokens the API returned per call. Recorded run on "
                "claude-opus-5, 30 Sep 2026; live runs vary.",
    )
    notes(s, "Left: the researcher lists the workflows folder, reads "
             "notebooks.yml and answers on turn three - Python 3.12, nine "
             "notebooks, the file path - so the loop returns done; 3,536 "
             "input tokens in all because every turn re-sends the whole "
             "conversation. Middle: the same agent with max_turns=2 spends "
             "both turns on tools and the harness cuts it with an empty "
             "answer; that is the seatbelt working. Right: a 3,000-token "
             "budget; after README.md comes back, count_tokens says the next "
             "call would carry 7,341 tokens, so the harness stops before "
             "sending it: one model call made, turns=1, nothing billed for "
             "the call that was counted. Turns count model calls, not tool "
             "calls, so the budget run has one turn. Class question: "
             "which of the two cut runs would you rather explain to the "
             "person paying the bill, and why? " + REC)

    # 16. Guardrails on real behaviour
    s = ds.two_col_slide(
        prs,
        "Guardrails that fired: the key file refused, the shell denied",
        ("Before a tool: hook deny_paths('.env')", [
            "Task: read .env at the root and list its variable names. Turn 1: "
            "list_files('.') - no .env in the listing",
            "Turn 2: read_file('.env') -> denied: \"'.env' is a protected "
            "file\"; a 'denied' event replaces the 'tool' event",
            "Turn 3: \"I can't answer this one\" - the model reports the "
            "block and offers safer routes instead",
            "The file was never opened; read_file refuses .env on its own "
            "too, so two layers said no",
            "In plain words: the hook decides, the model reads the outcome",
        ]),
        ("Permission: run_shell is risk 'danger'", [
            "Task: count the lines of README.md with wc. Turn 1: run_shell -> denied: \"risk 'danger' and this harness "
            "does not permit it\"; list_files runs in the same turn",
            "Turn 2: read_file('README.md'); turn 3 carries 7,869 input "
            "tokens - the whole file",
            "Answer: \"approximately 147 lines\", counted by eye; Python's "
            "count: 147",
            "Then allow_all plus a hook that only passes commands starting "
            "with 'wc ': wc -l README.md -> 147, done in 2 turns",
            "Three layers, one tool: risk on the tool, rule in the harness, "
            "hook narrows the opening",
        ]),
        kicker="Notebook 03 - hooks and permissions",
        note="Notebook 03 sections 2.1 and 2.3; recorded run on claude-opus-5, "
             "30 Sep 2026; live runs vary. Nobody was prompted in either run: "
             "the rules decided.",
    )
    notes(s, "Two guardrails, two checkpoints, both real. On the left the "
             "model was asked, politely, to read the key file; the hook saw "
             "the path before the tool ran and returned a reason, which the "
             "model received as an is_error tool result. It adapted and said "
             "so. On the right the task invited the shortcut - counting lines "
             "is what wc is for - and the permission rule refused run_shell "
             "without looking at the command. The model fell back to reading "
             "the file and counted by eye: right this time, and exactly the "
             "kind of task a model gets slightly wrong. The last bullet is "
             "the layered version: allow dangerous tools, then narrow with a "
             "hook to one safe command. Class question: why is a hook that "
             "denies with a reason better than silently dropping the call? "
             + REC)

    # 17. The validator
    s = ds.two_col_slide(
        prs,
        "The validator states the standard; only the tools make it reachable",
        ("validated-with-tools: opus-5 + list_files, read_file", [
            "Question: which tool does the CI workflow use to scan the "
            "history for secrets?",
            "3 turns, stopped_because=done",
            "parsed: found=True, sources=['.github/workflows/ci.yml'], "
            "answer names gitleaks via gitleaks/gitleaks-action@v2",
            "validator notes: none - require_sources and sources_exist "
            "passed first time",
            "In plain words: the standard was met because the tools made "
            "the fact reachable",
        ]),
        ("validated-no-tools: the same opus-5, no tools", [
            "Same question, same two validators, same output schema",
            "1 turn, stopped_because=done",
            "parsed: found=False, sources=[], \"I cannot determine this "
            "without access to the repository's CI configuration files\"",
            "validator notes: none - an honest found=False has nothing to "
            "reject",
            "A validator can only reject; it cannot make a model know "
            "things. Section 4 measures what it is worth on 14 cases",
        ]),
        kicker="Notebook 03 - validate_answer",
        note="Notebook 03 section 2.2. Structured answer {answer, sources, "
             "found}; require_sources rejects found=True with empty sources, "
             "sources_exist rejects paths that are not files. Recorded run, "
             "30 Sep 2026; live runs vary.",
    )
    notes(s, "Be honest about what happened here: in the recorded run the "
             "validator never fired. The agent with tools read the workflow "
             "and cited it; the agent without tools said it could not know "
             "and set found to false, which is exactly what the schema is "
             "for. In another run the no-tools agent may guess a path, and "
             "then sources_exist bounces it once - the notebook text covers "
             "both outcomes. The lesson does not depend on which happened: "
             "the validator is the standard, the tools are the ability, and "
             "a guard cannot add ability. Class question: what validator "
             "would you write for an agent that must answer in Dutch, and "
             "what would it do to an agent that only knows English? " + REC)

    # 18. Five patterns, one recorded line each
    s = ds.table_slide(
        prs,
        "Five patterns, each run for real: what ran and what it cost",
        ["Pattern", "What ran", "Recorded result"],
        [
            ["Prompt chaining",
             "researcher (opus-5), then a judge (sonnet-5) with a "
             "{pass, reason} output schema",
             "random_state=42 for every split, model and search, source "
             "CONTRIBUTING.md; judge pass=True; researcher $0.0256 + judge "
             "$0.0014"],
            ["Routing",
             "router (sonnet-5) with an enum output: calculator or "
             "researcher; each label owns an agent",
             "survival share -> calculator on sonnet-5: 38.4% via calculate, "
             "$0.0030; secret scanner -> researcher on opus-5: Gitleaks, "
             "ci.yml, $0.0193"],
            ["Parallelization",
             "three sonnet-5 researchers in a thread pool, one fresh context "
             "each",
             "MIT, Python 3.12, test accuracy 0.838 - wall clock 3.9 s side "
             "by side versus 11.0 s one after another"],
            ["Orchestrator-workers",
             "planner (sonnet-5) returns a list of subtasks; workers; "
             "synthesizer (opus-5) merges",
             "4 subtasks on CI vs notebook workflow; planner $0.0024 + 4 "
             "workers $0.0578 + synthesizer $0.0235 = $0.0836"],
            ["Evaluator-optimizer",
             "generator (sonnet-5, reads the file) and evaluator (sonnet-5) "
             "on a SECURITY.md summary, two rounds max",
             "round 1 revise ($0.0095): 'pinned' is not in the file; "
             "round 2 pass ($0.0102): every claim supported, path named"],
        ],
        kicker="Notebook 03 - the five patterns",
        note="Notebook 03 section 3; costs from response.usage at list prices. "
             "Recorded run, 30 Sep 2026; live runs vary. Use when / let the "
             "model drive when: see the Part 1 table.",
        col_widths=[1.9, 4.4, 5.8],
    )
    notes(s, "Each row is a few lines of Python composing Agent objects; the "
             "small roles run on sonnet-5 with low effort, the main agents on "
             "opus-5. Read the result column for the recurring trick: "
             "structured outputs. The judge returns pass and reason, the "
             "router returns an enum, the planner returns a list - code can "
             "read a model's decision without parsing prose. Routing shows "
             "the cheap path paying off: the arithmetic went to the small "
             "model and an exact tool. Parallel: three workers finished in "
             "the time of the slowest one. The evaluator caught a real "
             "embellishment - 'pinned' dependencies that the file never "
             "claims - and the second draft passed. Class question: which of "
             "these five would you remove first if your budget halved, and "
             "what would you lose? " + REC)

    # 19. The scoreboard
    s = ds.image_slide(
        prs,
        "One model, three harnesses: 21%, 100% and 93% of 14 cases",
        f"{FIGS}/s3_scoreboard.png",
        kicker="Notebook 03 - the A/B/C eval suite",
        bullets=[
            "How to read it: one bar per configuration; top = cases passed, "
            "bottom = cost of the whole suite from real usage",
            "A, no tools: 3 of 14 (21%), 5,975 input tokens, $0.0645",
            "B, tools: 14 of 14 (100%), 177,804 input tokens, $0.9765",
            "C, tools + validator: 13 of 14 (93%), 207,336 input tokens, "
            "$1.1275",
            "Same claude-opus-5, same effort, output schema and max_turns=8; "
            "only the harness changed",
            "Suite wall clock 88 s, four cases at a time; output tokens "
            "1,386 / 3,501 / 3,632",
        ],
        caption="Notebook 03 section 4: compare() over evals/cases.yaml, 11 "
                "factual cases + 3 traps. Recorded run on claude-opus-5, "
                "30 Sep 2026; live runs vary.",
    )
    notes(s, "This is the payoff of the session in one picture, and it did "
             "not come out the way the old story said. Without tools the "
             "model passes three cases - exactly the three traps, because "
             "not knowing is the right answer there. With tools it passes "
             "everything. With tools and the validator it passes one fewer, "
             "and costs more. Resist tidying that up: the next slide reads "
             "the failures one by one. Also notice the price axis: passing "
             "costs tokens, because reading files is what passing is made "
             "of. Class question: is a configuration that scores lower but "
             "enforces a standard worse, or just differently measured? "
             + REC)

    # 20. The failures, read honestly
    s = ds.two_col_slide(
        prs,
        "The failures, one by one: honest ignorance and one trap",
        ("A, no tools: 11 fails, 3 passes", [
            "Every factual case: 1 turn, found=False, sources=[], \"I cannot "
            "determine this without access to the repository\"",
            "Honest and useless at the same time: the grader asks for the "
            "fact and its source, and no fact was invented",
            "Its three passes are the traps, where 'the repository does not "
            "contain it' happens to be right",
            "In plain words: a model without tools cannot do a task that "
            "requires reading",
        ]),
        ("C, tools + validator: 1 fail, trap-grade", [
            "'What grade did the course receive?' - 8 turns, stopped "
            "max_turns, no structured answer, $0.5191",
            "B on the same case: also 8 turns, found=False on the last turn, "
            "$0.5341 - 'never guess' makes the model prove a negative, file "
            "after file",
            "The validator never fired: require_sources did not fire once in "
            "14 cases, so C's lower score and higher cost are not its doing",
            "Same model, same question, two runs: a result from one run is a "
            "reading, not a verdict",
            "Change next, cheapest first: tell the model when to stop "
            "searching; count a max_turns stop with no answer as found=False; "
            "add a max_input_tokens budget",
        ]),
        kicker="Notebook 03 - reading the failures",
        note="Notebook 03 section 4, 'Reading the failures honestly'. Proving a "
             "negative is the most expensive thing you can ask an agent to do. "
             "Recorded run, 30 Sep 2026; live runs vary.",
    )
    notes(s, "A scoreboard hides the interesting part. The left column is "
             "not a hallucination story: A never invented a fact, it said "
             "it could not know, eleven times, and the grader rightly failed "
             "it because the fact is in the repository. The right column is "
             "the surprise: the only failure of the full harness is a trap, "
             "and the same trap was the most expensive case for B as well. "
             "The system prompt says never guess, so the model tries to prove "
             "that no grade exists by reading file after file; nothing tells "
             "it when to stop. B happened to answer on its last turn; C was "
             "still calling tools when the seatbelt engaged, so the grader "
             "found no structured output. Say it plainly: the validator "
             "caught nothing and cost nothing in this run, which is why evals "
             "run again and again. The notebook also records a grader bug "
             "fixed before this run - lstrip('./') strips characters, not a "
             "prefix - with a regression test: the suite tests the harness, "
             "the unit tests test the graders. Class question: how would you "
             "change the system prompt so the model stops searching after two "
             "empty looks - and how would you test that it worked? " + REC)

    # 21. CI workflow
    s = ds.two_col_slide(
        prs,
        "Evals as CI: unit tests always, the eval suite only with the secret",
        ("Job unit: no key, always runs", [
            "Runs on every pull request that touches harness/, evals/, "
            "tests/ or the workflow file; permissions: contents: read",
            "actions/checkout@v7, actions/setup-python@v7 with Python 3.12 "
            "and a pip cache",
            "pip install anthropic python-dotenv pyyaml pydantic pandas "
            "pytest ruff; then ruff check harness tests; python -m pytest "
            "tests -q",
            "The tests replay canned API responses through a stub client in "
            "tests/conftest.py: engineering practice, never a teaching "
            "device",
        ]),
        ("Job evals: needs ANTHROPIC_API_KEY", [
            "needs: unit; env ANTHROPIC_API_KEY from the repository secret; "
            "every step guarded by if: env.ANTHROPIC_API_KEY != ''",
            "python -m harness eval evals/cases.yaml --config all --out "
            "results.json",
            "python -m harness show results.json goes to "
            "$GITHUB_STEP_SUMMARY; results.json uploaded as artifact "
            "harness-eval-results",
            "No secret (forks, Dependabot): one step writes 'Eval suite not "
            "run' to the summary and the job still passes",
            "The recorded suite: 42 eval runs, $2.1685 - small change next "
            "to a developer's hour, so it can run on every pull request",
        ]),
        kicker="Notebook 03 - .github/workflows/harness.yml",
        note="Workflow as read by the notebook (section 5). Bill of the "
             "recorded run: 27 single runs $0.3722 + 42 eval runs $2.1685 = "
             "$2.5407 on 30 Sep 2026; live runs vary.",
    )
    notes(s, "Anthropic's eval post makes the operational point: evals run "
             "like tests in CI so a change to a prompt, a tool or a model "
             "shows its effect before users see it. Marmelab found sixty "
             "percent of harnesses ship without tests or evals. This "
             "workflow is the smallest honest version: unit tests that need "
             "no key and always run, and the eval suite that needs the "
             "secret and skips cleanly without it, so forks do not fail. "
             "The scoreboard lands in the job summary and results.json is "
             "kept as an artifact - the pass rate of every configuration on "
             "record for every change, which is OpenAI's 'repository as "
             "system of record' in miniature. Class question: what would you "
             "put in the pull request template so a reviewer compares the "
             "new scoreboard with the old one? " + REC)

    # 22. Close
    s = ds.close_slide(
        prs,
        "You can now build a harness and prove it works",
        [
            "The loop: gather context, take action, verify work, repeat - "
            "with exits in your code",
            "Guardrails run outside the model: before input, before a tool, "
            "after the answer",
            "Five workflow patterns when the path is known; an agent when it "
            "is not",
            "An eval = task + grader + outcome; a suite gives a pass rate and "
            "a price",
            "A trace records every call with the tokens the API returned; "
            "cost = usage x price",
            "Notebook 03: 3, 14 and 13 of 14 cases for one model; the full "
            "harness failed one trap",
            "Next session: sub-agents, teams, failure modes and the "
            "discipline",
        ],
        course=COURSE,
    )
    notes(s, "Recap in one breath: a loop with exits, guards in code, "
             "patterns before agents, evals before opinions, traces before "
             "invoices. Homework is notebook 03's exercises: add an eval "
             "case and a trap, write a hook that denies write tools, and run "
             "the evaluator-optimizer with one, two and four rounds. Class "
             "question: which single piece from today would you add first to "
             "an agent you already use?")
    return prs


if __name__ == "__main__":
    make_loop_fig()
    make_checkpoints_fig()
    make_patterns_fig()
    make_evals_fig()
    make_exits_fig()
    make_scoreboard_fig()
    deck = slides()
    out = "../m5-session-3-building-a-harness.pptx"
    ds.save_deck(deck, out, FOOTER, author="M5 Harness Engineering course")
    print("Slides:", len(deck.slides._sldIdLst))
    print("Saved:", os.path.abspath(out))
