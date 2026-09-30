"""Build deck: M5 Session 3 - Building a Harness.

Theory: the loop with stop conditions, hooks and permissions, the five
workflow patterns, evals, observability and OpenAI's harness lessons.
Practice: notebook 03 (patterns, a validator retry, the A/B/C eval suite).
All practice numbers come from the M5 course brief appendix (deterministic
ScriptedModel runs); every external fact is attributed on the slide.
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
             (1.6, "MAX TURNS", "turn limit reached", pal["navy"]),
             (0.6, "BUDGET", "token or cost cap hit", pal["gray"])]
    for y, head, sub, c in exits:
        ax.plot([5.6, 5.9], [y, y], color=pal["gray"], lw=1.2)
        ax.add_patch(FancyBboxPatch((5.9, y - 0.36), 3.8, 0.72,
                                    boxstyle="round,pad=0.03", facecolor=c,
                                    edgecolor=c))
        ax.text(6.1, y, head, va="center", color="white", fontweight="bold",
                fontsize=10.5)
        ax.text(7.75, y, sub, va="center", color="white", fontsize=9.2)
    ax.text(7.8, 3.2, "three exits", ha="center", color=pal["gray"],
            fontsize=10, style="italic")
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
         ["validate: format, citation",
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
    for j, line in enumerate(["code: contains, cites, used_tool",
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


def make_validator_trace_fig():
    """The shape of a validated run's trace: reject, retry, accept."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    cols = [(0.25, "turn"), (0.95, "kind"), (1.95, "who"), (3.2, "detail")]
    ax.add_patch(FancyBboxPatch((0.1, 5.05), 6.5, 0.55, boxstyle="round,pad=0.02",
                                facecolor=pal["navy"], edgecolor=pal["navy"]))
    for x, h in cols:
        ax.text(x, 5.32, h, va="center", color="white", fontweight="bold",
                fontsize=9.5)
    rows = [("1", "model", "lazy",
             "answers from memory, no source", "white"),
            ("1", "note", "validator",
             "the answer has no [source: ...] citation.", pal["sky"]),
            ("2-4", "tool", "3 tools",
             "search_docs, read_doc, check_citation:\nthe model researches instead of guessing", "white"),
            ("5", "model", "lazy",
             "cited answer with a [source: ...] tag", "white"),
            ("5", "final", "validated", "stopped_because = 'done'", pal["panel"])]
    ys = [4.45, 3.7, 2.95, 2.2, 1.45]
    for (turn, kind, who, detail, fc), y in zip(rows, ys):
        ax.add_patch(FancyBboxPatch((0.1, y - 0.35), 6.5, 0.7,
                                    boxstyle="round,pad=0.02", facecolor=fc,
                                    edgecolor=pal["sky"], lw=0.8))
        for x, val in zip([c[0] for c in cols], [turn, kind, who, detail]):
            ax.text(x, y, val, va="center", color=pal["ink"], fontsize=8.2,
                    fontweight="bold" if x < 3 else "normal", linespacing=1.2)
    # callouts
    ax.add_patch(FancyBboxPatch((6.85, 3.05), 3.0, 1.45, boxstyle="round,pad=0.03",
                                facecolor=pal["panel"], edgecolor=pal["blue"],
                                lw=1.2))
    ax.text(7.0, 4.25, "REJECTED", color=pal["navy"], fontweight="bold",
            fontsize=9.5, va="center")
    ax.text(7.0, 3.65, "the harness appends a user message:\n'Your answer was "
            "rejected: ... Fix it\nand answer again.' - and loops",
            color=pal["ink"], fontsize=8, va="center", linespacing=1.25)
    arrow(ax, (6.85, 3.7), (6.6, 3.7), ms=10)
    ax.add_patch(FancyBboxPatch((6.85, 0.95), 3.0, 1.55, boxstyle="round,pad=0.03",
                                facecolor=pal["panel"], edgecolor=pal["blue"],
                                lw=1.2))
    ax.text(7.0, 2.3, "ACCEPTED after 1 retry", color=pal["navy"],
            fontweight="bold", fontsize=9.5, va="center")
    ax.text(7.0, 1.6, "whole run: 5 model calls, 3 tool\ncalls, ~2,163 tokens. "
            "Retries are\ncapped, so the loop cannot hang",
            color=pal["ink"], fontsize=8, va="center", linespacing=1.25)
    arrow(ax, (6.85, 1.45), (6.6, 1.45), ms=10)
    ax.text(0.1, 0.45, "a bare model with the same validator: 2 model calls, "
            "0 tools, ~73 tokens - still wrong; a guard cannot add ability",
            color=pal["gray"], fontsize=8.4, style="italic", va="center")
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5.8)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s3_validator_trace.png")
    plt.close(fig)


def make_routing_fig():
    """Routing: a classifier picks a label; each label owns a specialist."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    box(ax, 0.2, 4.2, 2.8, 1.0, "What is\n(891 - 179) / 891?", fc="white",
        ec=pal["sky"], hs=9.5)
    box(ax, 0.2, 1.0, 2.8, 1.0, "When was function calling\nintroduced by OpenAI?",
        fc="white", ec=pal["sky"], hs=9.5)
    box(ax, 3.7, 2.45, 2.3, 1.3, "ROUTER", "labels: calculation,\nresearch, general",
        fc=pal["blue"], ec=pal["blue"], hc="white", sc=pal["sky"])
    arrow(ax, (3.0, 4.7), (3.7, 3.4), rad=0.1, color=pal["gray"])
    arrow(ax, (3.0, 1.5), (3.7, 2.8), rad=-0.1, color=pal["gray"])
    box(ax, 6.7, 4.2, 3.1, 1.0, "calculation  ->  calc agent",
        "tool: calculator", hs=9.5, ss=8.5)
    box(ax, 6.7, 2.75, 3.1, 0.7, "general  ->  plain answer", fc="white",
        ec=pal["gray"], hc=pal["gray"], hs=9, ls="--")
    box(ax, 6.7, 1.0, 3.1, 1.0, "research  ->  research agent",
        "tools: search_docs, read_doc,\ncheck_citation", hs=9.5, ss=8)
    arrow(ax, (6.0, 3.4), (6.7, 4.7), rad=-0.1)
    arrow(ax, (6.0, 3.1), (6.7, 3.1), color=pal["gray"], ls="--")
    arrow(ax, (6.0, 2.8), (6.7, 1.5), rad=0.1)
    ax.text(8.25, 5.6, "->  0.799102", ha="center", color=pal["blue"],
            fontweight="bold", fontsize=12)
    ax.text(8.25, 0.55, "->  13 June 2023  [source: ...]", ha="center",
            color=pal["blue"], fontweight="bold", fontsize=11)
    ax.text(4.85, 1.75, "the router only chooses;\nit never answers",
            ha="center", color=pal["gray"], fontsize=8.6, style="italic")
    ax.set_xlim(0, 10)
    ax.set_ylim(0.2, 6)
    ax.axis("off")
    fig.savefig(f"{FIGS}/s3_routing.png")
    plt.close(fig)


def make_pass_rate_fig():
    """A/B/C pass rates on the 12-case suite (notebook 03)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = ["C: tools + verification", "B: tools, no verification",
              "A: bare model"]
    vals = [100.0, 91.7, 0.0]
    counts = ["12 of 12", "11 of 12", "0 of 12"]
    colors = [pal["blue"], pal["sky"], pal["gray"]]
    ax.barh(labels, vals, color=colors, height=0.55)
    for i, (v, c) in enumerate(zip(vals, counts)):
        ax.text(v + 1.5, i, f"{v:.1f}%  ({c})", va="center", color=pal["ink"],
                fontsize=12, fontweight="bold")
    ax.set_xlim(0, 128)
    ax.set_xlabel("Pass rate on the 12-case eval suite (%)")
    ax.set_title("Same model, three harnesses: only the harness changed")
    fig.savefig(f"{FIGS}/s3_pass_rates.png")
    plt.close(fig)


def make_tokens_fig():
    """A/B/C estimated tokens for the whole suite (notebook 03)."""
    fig, ax = plt.subplots(figsize=(7.6, 4.8))
    labels = ["C: tools + verification", "B: tools, no verification",
              "A: bare model"]
    vals = [24600, 11800, 170]
    texts = ["~24,600  (4.1 turns per case)", "~11,800  (3.0 turns per case)",
             "~170  (1 turn per case)"]
    colors = [pal["blue"], pal["sky"], pal["gray"]]
    ax.barh(labels, vals, color=colors, height=0.55)
    for i, (v, t) in enumerate(zip(vals, texts)):
        ax.text(v + 400, i, t, va="center", color=pal["ink"], fontsize=11.5,
                fontweight="bold")
    ax.annotate("", xy=(11800, 0.4), xytext=(24600, 0.4),
                arrowprops=dict(arrowstyle="<->", color=pal["navy"], lw=1.4))
    ax.text(18200, 0.55, "2.1x the tokens for the last case", ha="center",
            color=pal["navy"], fontsize=10.5, fontweight="bold")
    ax.set_xlim(0, 39000)
    ax.set_xlabel("Estimated tokens sent to the model, all 12 cases")
    ax.set_title("Verification is not free")
    fig.savefig(f"{FIGS}/s3_tokens.png")
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
        "change. Then notebook 03 runs the same model through three harnesses.",
        course=COURSE,
    )
    notes(s, "Frame the session: last time we looked at the parts on the "
             "bench - models, context, tools, skills. Today we bolt them into "
             "a car that drives and, more importantly, brakes. Part 1 is the "
             "theory of the loop, guardrails, patterns and evals; Part 2 is "
             "notebook 03, where one model runs through three harnesses and "
             "the pass rate goes from 0% to 100%. Ask the class: if the same "
             "model gives three different results, what exactly are we "
             "testing?")

    # 2. Part 1 divider
    s = ds.section_slide(
        prs, "01", "Part 1 - The theory: the loop, the guards, the proof",
        "How an agent runs, where the checks go, which pattern to pick, and "
        "how you know any of it works.")
    notes(s, "Four ideas in Part 1: the loop and its exits, guardrails at "
             "three checkpoints, five workflow patterns, and evals plus "
             "traces as the proof. Ask the class: which of the eight pieces "
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
            "Three exits: done, max turns, budget - a loop without exits is "
            "a runaway car",
            "Our library: Agent.run() is about 30 lines that do exactly this",
        ],
        caption="Illustration. Loop steps as named by Anthropic, Claude Agent "
                "SDK, Sep 2025. Exits as implemented in the course library "
                "(harness.agent).",
    )
    notes(s, "Walk the picture clockwise: gather, act, verify, repeat. Point "
             "at the three exits and insist on them - most demos online have "
             "only 'done'. Max turns protects against a model that never "
             "finishes; budget protects your wallet. In the library this is "
             "Agent.run(): a for-loop over turns, a model call, tool "
             "execution, validators, and the RunResult with stopped_because. "
             "Ask the class: which exit would you hit first if the model "
             "kept calling the same tool with the same arguments?")

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
            "Checkpoint 3, after the answer: validate format and citations; "
            "retry on failure",
            "The approval paradox: 93% of permission prompts get approved - "
            "a prompt is not a control",
            "Our library: run_python is 'danger', denied by default; "
            "Hooks.validate_answer retries",
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
             "are code, not questions. Ask the class: which of the three "
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
             "most safety is deterministic. In the course library the tool "
             "safeguard is the risk level on each @tool, the rules-based "
             "protection is a before_tool hook, and output validation is "
             "validate_answer. Ask the class: which two of the seven would "
             "you add first to a homework-helper agent, and why those two?")

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
             "the map; only an agent chooses the roads itself. Ask the "
             "class: which pattern is a spell-checker that rewrites a "
             "paragraph until a grammar tool is satisfied?")

    # 7. When to use which
    s = ds.table_slide(
        prs,
        "Simplest pattern first - the model drives when the path is unknown",
        ["Pattern", "Use when", "Course example (notebook 03)"],
        [
            ["Prompt chaining", "Fixed steps, each easy to check",
             "outline -> draft -> citation check"],
            ["Routing", "Inputs fall into a few known kinds",
             "calculation vs research vs general"],
            ["Parallelization", "Independent pieces, or a vote for robustness",
             "three sub-questions at once; three judges"],
            ["Orchestrator-workers", "You cannot predict the sub-tasks",
             "compound question split into 3, ~6,000 tokens"],
            ["Evaluator-optimizer", "Clear criteria and revision pays off",
             "generator + judge: bare fails twice, research passes round 1"],
            ["Agent (the model drives)", "Open-ended task, unknown number of steps",
             "the research loop: search, read, check, answer"],
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
             "column maps each pattern to a cell the students will run. Ask "
             "the class: a support bot that must answer billing, shipping "
             "and returns questions - workflow or agent, and which pattern?")

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
            "Code graders first: contains, cites, used_tool. LLM judges must "
            "be calibrated against humans",
            "One case proves nothing; a suite gives a pass rate you can "
            "compare",
            "Evals run like tests in CI: every harness change re-runs the "
            "suite",
        ],
        caption="Illustration. Anthropic, Demystifying evals for AI agents, "
                "Jan 2026. Grader names as in the course library "
                "(harness.evals).",
    )
    notes(s, "Students know unit tests; an eval is the same idea for a "
             "system that is not deterministic, so you measure a rate over "
             "many cases instead of one pass/fail. Outcome grading asks "
             "whether the answer is right; trajectory grading asks whether "
             "the steps were reasonable - a right answer reached by "
             "guessing is a failure waiting to happen. Code graders are "
             "cheap and exact; LLM judges are flexible but drift, so you "
             "calibrate them on human-labelled examples. Ask the class: what "
             "would the grader be for 'the agent must never run code'?")

    # 9. Observability
    s = ds.two_col_slide(
        prs,
        "A trace records every step - without it you are guessing",
        ("A trace records", [
            "Every model call, with the estimated tokens it was sent",
            "Every tool call: name, arguments, result",
            "Denials, compactions, validator notes, the final answer",
            "Turn numbers and seconds: where the time went",
            "In plain words: the dashboard and mirrors of the car",
        ]),
        ("What it buys you", [
            "Cost accounting: tokens times price per million - "
            "trace.cost(3.0)",
            "Debugging: the exact step where a run went wrong",
            "Comparison: harness A vs B on the same tasks, side by side",
            "Budgets: alarms on tokens, turns and cost before they run away",
            "No trace, no engineering - only anecdotes",
        ]),
        kicker="Observability",
        note="Anthropic, Demystifying evals for AI agents, Jan 2026; Claude "
             "Agent SDK, Sep 2025. Trace, Event and cost as in the course "
             "library (harness.trace).",
    )
    notes(s, "Every run in the notebooks ends with result.trace.show(): one "
             "line per event with the turn number, the kind, who acted and "
             "what happened. That is observability at teaching scale; in "
             "production the same record goes to a tracing tool. The right "
             "column is why you bother: you cannot price, debug or compare "
             "what you did not record. Ask the class: a run cost ten times "
             "more than yesterday - which three lines of the trace would you "
             "read first?")

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
             "optional to a model. Ask the class: what is one rule in your "
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
             "Ask the class: for which actions would you still insist on "
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
             "close. Ask the class: which is worse - a rule with no control, "
             "or no rule at all?")

    # 13. Part 2 divider
    s = ds.section_slide(
        prs, "02", "Part 2 - The practice: notebook 03",
        "Patterns you can run, a validator that retries, and an eval suite "
        "that puts a number and a price on three configurations of one "
        "harness.")
    notes(s, "Open notebook 03. Everything runs without an API key on the "
             "ScriptedModel, so the numbers on the next slides are the "
             "numbers students will see. Ask the class: before we run it, "
             "what pass rate do you expect from the bare model?")

    # 14. Validator retry in a trace
    s = ds.image_slide(
        prs,
        "Checkpoint 3 in action: the validator rejects, the loop retries",
        f"{FIGS}/s3_validator_trace.png",
        kicker="Notebook 03 - hooks",
        bullets=[
            "How to read it: one row per trace event - turn, kind, who, what",
            "Turn 1: a lazy policy answers from memory, no source; the "
            "validator rejects it",
            "The harness appends 'Your answer was rejected ... Fix it and "
            "answer again'",
            "Turns 2-5: the model searches, reads, checks and answers with a "
            "citation",
            "Whole run: 5 model calls, 3 tool calls, ~2,163 tokens; "
            "stopped_because = 'done'",
            "A bare model with the same validator: 2 calls, ~73 tokens, still "
            "wrong - a guard cannot add ability",
        ],
        caption="Notebook 03: Hooks.validate_answer on a lazy research policy; "
                "trace condensed, research turns 2-4 folded into one row. "
                "5 model calls, 3 tool calls, ~2,163 tokens.",
    )
    notes(s, "This is the smallest possible guardrail: a Python function "
             "that returns a problem string when the answer has no "
             "[source: ...] tag. The loop does the rest - it writes the "
             "problem back as a user message and gives the model another "
             "turn; the lazy policy then does the research it skipped, three "
             "tool calls and about 2,163 tokens in all. Point at the 'note "
             "validator' row: that is the guardrail leaving a footprint in "
             "the trace. Then the bottom line: the same validator on a bare "
             "model rejects, retries, and still gets a wrong answer for 73 "
             "tokens - a guard can refuse, it cannot research. Ask the class: what validator would you write for an "
             "agent that must answer in Dutch?")

    # 15. Routing example
    s = ds.image_slide(
        prs,
        "Routing sends each question to the agent built for it",
        f"{FIGS}/s3_routing.png",
        kicker="Notebook 03 - patterns.route",
        bullets=[
            "How to read it: a cheap classifier picks a label; each label "
            "owns a specialist agent",
            "'What is (891 - 179) / 891?' -> calculation -> calculator tool "
            "-> 0.799102",
            "'When was function calling introduced by OpenAI?' -> research "
            "-> 13 June 2023, cited",
            "The router never answers; it only chooses. Small model, big "
            "saving",
            "In plain words: a signpost at the junction - each road has its "
            "own driver",
        ],
        caption="patterns.route() in the course library, notebook 03; labels: "
                "calculation, research, general. Pattern: Anthropic, Building "
                "effective agents, Dec 2024.",
    )
    notes(s, "Two very different questions, one entry point. The router is "
             "an agent whose only job is to emit a label; the specialists "
             "carry the tools. 0.799102 is a number the students met in M2: "
             "the share of passengers left after the 179-row test split. "
             "The research branch pulls the function-calling date from the "
             "library with a source tag. Ask the class: what happens to a "
             "question the router labels 'general' - and is that the right "
             "default?")

    # 16. Eval pass rates
    s = ds.image_slide(
        prs,
        "Same model, three harnesses: 0%, 91.7%, 100% on twelve cases",
        f"{FIGS}/s3_pass_rates.png",
        kicker="Notebook 03 - the A/B/C eval",
        bullets=[
            "How to read it: one bar per configuration; length = share of "
            "the 12 cases passed",
            "A, bare model: 0 of 12 - stale memory, no source to cite",
            "B, tools without verification: 11 of 12 - it searches and "
            "reads but never checks",
            "C, tools + verification: 12 of 12 - check_citation catches the "
            "trap",
            "Only the harness changed; the model and the questions are "
            "identical",
        ],
        caption="Eval suite of 12 cases in notebook 03 (harness.evals.compare). "
                "Graders: contains(...) plus cites(...) per case.",
    )
    notes(s, "This is the payoff of the whole session in one chart. The bare "
             "model fails everything because our ScriptedModel, like a real "
             "model with a cutoff, remembers wrong dates and cannot cite. "
             "Adding search and read tools jumps to eleven of twelve. Adding "
             "one verification tool gets the last one. Ask the class: is a "
             "91.7% harness good enough? For what kind of question would you "
             "say yes, and for which would you say no?")

    # 17. Tokens
    s = ds.image_slide(
        prs,
        "Verification bought the last case at 2.1x the tokens",
        f"{FIGS}/s3_tokens.png",
        kicker="Notebook 03 - the price",
        bullets=[
            "How to read it: one bar per configuration; length = estimated "
            "tokens for all 12 cases",
            "A ~170 tokens: one call per case, no tools, no help",
            "B ~11,800: search and read results fill the context, 3.0 turns "
            "per case",
            "C ~24,600: an extra verification round, 4.1 turns per case",
            "From B to C: one more correct case for 12,814 more tokens, 2.1x",
            "Worth it? Depends on what one wrong answer costs you",
        ],
        caption="Estimated tokens from the traces, notebook 03 (prints 172 / "
                "11,766 / 24,580). 24,600 / 11,800 = 2.1. Prices vary by "
                "model; the ratio is the lesson.",
    )
    notes(s, "Now the other axis. Tokens rise by a factor of about seventy "
             "from A to B and double again from B to C. The engineering "
             "question is not 'is C better' - it is - but 'is one extra "
             "correct answer in twelve worth doubling the bill'. For a "
             "medical or legal assistant, obviously yes. For a chatbot "
             "suggesting playlists, probably not. Ask the class: how could "
             "you get most of C's accuracy at B's price? Hint: routing.")

    # 18. The no-answer trap
    s = ds.two_col_slide(
        prs,
        "B's one failure: confident and cited, on a question with no answer",
        ("B: tools, no verification", [
            "Case: 'How many employees does Anthropic have?' - not in the "
            "library",
            "search_docs returns the closest document anyway",
            "B reads it and answers with confidence, citing an unrelated "
            "document",
            "The grader wanted 'could not verify'; B fails this one case",
            "In plain words: a wrong answer wearing a real-looking source",
        ]),
        ("C: tools + verification", [
            "Same search, same unrelated document",
            "check_citation compares the claim with the cited text: no match",
            "The agent says 'could not verify' instead of guessing",
            "C passes: the honest 'I do not know' was a graded outcome",
            "In plain words: the harness made not-knowing the cheapest path",
        ]),
        kicker="Notebook 03 - the no-answer trap",
        note="Notebook 03, eval case 'no-answer'; grader contains('could not "
             "verify'). Lesson: write the trap into the suite, or you will "
             "never see it.",
    )
    notes(s, "The most important case in the suite is the one with no "
             "answer. B's failure is not a bug in search - search did what "
             "search does, it returned the nearest thing. The bug is that "
             "nothing checked whether the nearest thing supported the claim. "
             "C adds that check and the honest answer falls out. Notice the "
             "eval design: we graded for 'could not verify', so not-knowing "
             "was rewarded. Ask the class: how many of your own test cases "
             "have no right answer on purpose?")

    # 19. Cost
    s = ds.table_slide(
        prs,
        "trace.cost: a price per configuration and per thousand runs",
        ["Configuration", "Pass rate", "Tokens", "Cost at $3 per million tokens",
         "Per 1,000 runs"],
        [
            ["One cited research run (a single question)", "-", "~1,904",
             "$0.0057", "$5.71"],
            ["A: bare model, 12 cases", "0%", "~170", "$0.0005", "$0.51"],
            ["B: tools, no verification, 12 cases", "91.7%", "~11,800", "$0.035", "$35.40"],
            ["C: tools + verification, 12 cases", "100%", "~24,600", "$0.074", "$73.80"],
            ["C compared with B", "+1 case (+8.3 points)", "2.1x", "2.1x", "+$38.40"],
        ],
        kicker="Notebook 03 - cost accounting",
        note="Cost = tokens / 1,000,000 x 3, as in trace.cost(3.0) in the "
             "course library. The $3 price is a stand-in; real prices differ "
             "by model and between input and output tokens.",
        col_widths=[3.6, 1.2, 1.4, 2.8, 2.0],
    )
    notes(s, "Do the arithmetic on the slide: 24,600 tokens at three dollars "
             "per million is about seven cents for the whole suite - "
             "trivial once, seventy-four dollars per thousand runs, and the "
             "twelve cases stand in for real traffic. The point is the "
             "habit: every configuration gets a pass rate and a price, and "
             "the decision is made with both numbers on the table. Ask the "
             "class: at what price per wrong answer does C become cheaper "
             "than B?")

    # 20. Close
    s = ds.close_slide(
        prs,
        "You can now build a harness and prove it works",
        [
            "The loop: gather context, take action, verify work, repeat - "
            "with three exits",
            "Guardrails run outside the model: before input, before a tool, "
            "after the answer",
            "Five workflow patterns when the path is known; an agent when it "
            "is not",
            "An eval = task + grader + outcome; a suite gives a pass rate you "
            "can compare",
            "A trace records every call and token; cost = tokens x price",
            "Notebook 03: 0% -> 91.7% -> 100%, verification at 2.1x the "
            "tokens",
            "Next session: sub-agents, teams, failure modes and the "
            "discipline",
        ],
        course=COURSE,
    )
    notes(s, "Recap in one breath: a loop with exits, guards in code, "
             "patterns before agents, evals before opinions, traces before "
             "invoices. Homework is notebook 03's exercises - they add a "
             "case to the eval suite and a validator to the harness. Ask the "
             "class: which single piece from today would you add first to "
             "an agent you already use?")

    return prs


if __name__ == "__main__":
    make_loop_fig()
    make_checkpoints_fig()
    make_patterns_fig()
    make_evals_fig()
    make_validator_trace_fig()
    make_routing_fig()
    make_pass_rate_fig()
    make_tokens_fig()
    deck = slides()
    out = "../m5-session-3-building-a-harness.pptx"
    ds.save_deck(deck, out, FOOTER, author="M5 Harness Engineering course")
    print("Slides:", len(deck.slides._sldIdLst))
    print("Saved:", os.path.abspath(out))
