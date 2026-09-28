"""Build the M4 Session 1 deck: The Power of Prompting.

Part 1 is theory (what a prompt is, in-context learning, the ladder, self-generation prompting),
Part 2 is the practice of notebook M4-01. Every practice number is read from the notebook's saved
results (outputs/m4_results.json next to the notebook, written when it runs)
when that file is
absent the frozen values from the committed notebook run are used, so the deck always rebuilds.
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch

import deck_style as ds

HERE = Path(__file__).resolve().parent
FIGS = Path("/tmp/deck-workshop/figs-m4")
FIGS.mkdir(parents=True, exist_ok=True)
pal = ds.mpl_theme()
COURSE = "Prompting and Language Models - Module 4"

# ------------------------------------------------------------------ numbers
RESULTS_PATH = HERE.parent.parent / "M4 - Prompting and Language Models" / "outputs" / "m4_results.json"
FROZEN = json.loads(Path(__file__).with_name("m4_frozen_results.json").read_text())
R = json.loads(RESULTS_PATH.read_text()) if RESULTS_PATH.exists() else FROZEN
LADDER = ["0 vague ask", "1 + specification", "2 + rules", "3 + role", "4 + examples"]
SELF = ["self-examples", "self-refine", "APE best", "OPRO best"]
FIELDS = ["Pclass", "Sex", "Age", "SibSp", "Parch", "Embarked"]
import re
_m = re.search(r"(\d+(?:\.\d+)?)B", R["model"])
WORKER_B = _m.group(1) if _m else "?"
FAM = R["fields_dev"]["4 + examples"]
FAM_PCT = f"{(FAM['SibSp'] + FAM['Parch']) / 2 * 100:.0f}%"


def pct(x):
    return f"{x * 100:.0f}%"


def notes(slide, text):
    slide.notes_slide.notes_text_frame.text = text


# ------------------------------------------------------------------ figures
def fig_prompt_is_steering():
    """Illustration: the prompt is the only input at run time."""
    fig, ax = plt.subplots(figsize=(7.6, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 5)
    ax.axis("off")
    boxes = [(0.2, "PROMPT\nthe only thing\nyou control", pal["blue"], "white"),
             (3.55, "MODEL\npredicts the next token,\nagain and again", pal["panel"], pal["navy"]),
             (6.9, "OUTPUT\nthe most likely\ncontinuation", pal["panel"], pal["navy"])]
    for x, label, fc, tc in boxes:
        ax.add_patch(FancyBboxPatch((x, 1.6), 2.9, 1.9, boxstyle="round,pad=0.05", facecolor=fc,
                                    edgecolor=pal["blue"], lw=1.5))
        ax.text(x + 1.45, 2.55, label, ha="center", va="center", fontsize=10, color=tc, fontweight="bold")
    for x0, x1 in ((3.15, 3.5), (6.5, 6.85)):
        ax.add_patch(FancyArrowPatch((x0, 2.55), (x1, 2.55), arrowstyle="-|>", mutation_scale=16,
                                     color=pal["blue"], lw=1.8))
    ax.text(5.0, 0.7, "Everything you do not say, the model guesses.", ha="center", fontsize=12.5,
            color=pal["navy"], fontweight="bold")
    ax.text(5.0, 4.5, "Illustration: no memory of you, no goals, no settings to open. Words in, words out.",
            ha="center", fontsize=9.5, color=pal["gray"])
    fig.savefig(FIGS / "steering.png")
    plt.close(fig)
    return str(FIGS / "steering.png")


def fig_search_loop():
    """Illustration: prompt optimization is a search loop."""
    fig, ax = plt.subplots(figsize=(7.6, 4.4))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6)
    ax.axis("off")
    steps = [(0.6, 4.2, "1  PROPOSE\na candidate prompt\n(a human, or the model)"),
             (6.3, 4.2, "2  SCORE\nrun it on examples\nwith known answers"),
             (6.3, 0.9, "3  KEEP\nthe best so far"),
             (0.6, 0.9, "4  LEARN\nshow scores and failures\nto the author")]
    for x, y, label in steps:
        ax.add_patch(FancyBboxPatch((x, y), 3.1, 1.5, boxstyle="round,pad=0.05", facecolor=pal["panel"],
                                    edgecolor=pal["blue"], lw=1.5))
        ax.text(x + 1.55, y + 0.75, label, ha="center", va="center", fontsize=9.5, color=pal["navy"], fontweight="bold")
    arrows = [((3.75, 4.95), (6.25, 4.95)), ((7.85, 4.15), (7.85, 2.45)), ((6.25, 1.65), (3.75, 1.65)), ((2.15, 2.45), (2.15, 4.15))]
    for (x0, y0), (x1, y1) in arrows:
        ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle="-|>", mutation_scale=16, color=pal["blue"], lw=1.8))
    ax.text(5.0, 3.05, "the prompt is a hyperparameter made of words", ha="center", fontsize=11, color=pal["gray"], style="italic")
    ax.text(5.0, 5.85, "Illustration: the same loop as hyperparameter search in M2 notebook 3.", ha="center", fontsize=9.5, color=pal["gray"])
    fig.savefig(FIGS / "loop.png")
    plt.close(fig)
    return str(FIGS / "loop.png")


def fig_scores(names, split, title, fname, note):
    data = R[split]
    fa = [data[n]["field_accuracy"] * 100 for n in names]
    pr = [data[n]["perfect_rows"] * 100 for n in names]
    fig, ax = plt.subplots(figsize=(7.6, 0.62 * len(names) + 1.9))
    y = list(range(len(names)))
    ax.barh([i - 0.19 for i in y], fa, height=0.38, color=pal["blue"], label="fields exactly right (%)")
    ax.barh([i + 0.19 for i in y], pr, height=0.38, color=pal["sky"], label="passengers perfect in all 6 fields (%)")
    for i, (a, b) in enumerate(zip(fa, pr)):
        ax.text(a + 1, i - 0.19, f"{a:.0f}", va="center", fontsize=9, color=pal["navy"])
        ax.text(b + 1, i + 0.19, f"{b:.0f}", va="center", fontsize=9, color=pal["gray"])
    ax.set_yticks(y)
    ax.set_yticklabels(names)
    ax.invert_yaxis()
    ax.set_xlim(0, 110)
    ax.set_xlabel(f"score on the {split} set, 10 passengers (%)")
    ax.set_title(title, loc="left")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.16), ncol=2, frameon=False, fontsize=8.5)
    fig.savefig(FIGS / fname)
    plt.close(fig)
    return str(FIGS / fname)


def fig_fields():
    """Per-field accuracy of the top rung: where the small model hits its ceiling."""
    d = R["fields_dev"]["4 + examples"]
    fig, ax = plt.subplots(figsize=(7.6, 3.9))
    vals = [d[f] * 100 for f in FIELDS]
    colors = [pal["blue"] if v >= 85 else pal["sky"] for v in vals]
    bars = ax.bar(FIELDS, vals, color=colors, width=0.6)
    for b, v in zip(bars, vals):
        ax.text(b.get_x() + b.get_width() / 2, v + 2, f"{v:.0f}", ha="center", fontsize=10, color=pal["navy"], fontweight="bold")
    ax.set_ylim(0, 112)
    ax.set_ylabel("field correct (%), rung 4, dev set")
    weak = sorted(FIELDS, key=lambda f: d[f])[:2]
    ax.set_title(f"Where the errors live: {weak[0]} at {d[weak[0]] * 100:.0f}% and {weak[1]} at {d[weak[1]] * 100:.0f}%")
    ax.axhline(100, color=pal["gray"], lw=0.8, ls=":")
    fig.savefig(FIGS / "fields.png")
    plt.close(fig)
    return str(FIGS / "fields.png")


def fig_opro():
    best = [b * 100 for b in R["opro_best_so_far"]]
    fig, ax = plt.subplots(figsize=(7.6, 3.8))
    ax.plot(range(len(best)), best, marker="o", color=pal["blue"], lw=2.2)
    for x, b in enumerate(best):
        ax.text(x, b + 2.5, f"{b:.0f}", ha="center", fontsize=10, color=pal["navy"], fontweight="bold")
    ax.set_xticks(range(len(best)))
    ax.set_xlabel("optimizer round (0 = the better of the two starting prompts)")
    ax.set_ylabel("best dev field accuracy (%)")
    ax.set_ylim(0, 112)
    ax.set_title("The optimizer loop can only go up or stay flat")
    fig.savefig(FIGS / "opro.png")
    plt.close(fig)
    return str(FIGS / "opro.png")


# ------------------------------------------------------------------ deck
prs = ds.new_deck()

s = ds.title_slide(prs, "Session 1", "The Power of Prompting",
                   "Why the words you send a language model decide what comes back, how to measure it, "
                   "and how to make the model write its own prompts.", course=COURSE)
notes(s, "Talk track: this session has two halves. First the theory of why prompts work and a ladder of techniques. "
         "Then the notebook: a small model on your own laptop, one real job, a scoreboard, and a loop in which the model "
         "writes and improves its own instructions. Class question to open: who has been frustrated by an AI answer this week, and what did you type?")

ds.section_slide(prs, "01", "Part 1 - The theory", "What a prompt is, why words work, and the loop that writes prompts")

s = ds.image_slide(prs, "A language model continues text. The prompt is the only steering wheel", fig_prompt_is_steering(),
                   kicker="What a prompt really is",
                   bullets=["A model predicts the next token, given the text so far. In plain words: autocomplete that read a library.",
                            "No memory of you, no goals, no settings to change at run time. You can only write words.",
                            "So every detail you leave out is a detail the model must guess.",
                            "Concrete first: \"extract the passenger data\" gets whatever a stranger thinks that means."],
                   caption="How to read it: left to right, the only box you control is the first one.")
notes(s, "Talk track: anchor on the new-colleague picture before any theory. Same colleague, two requests, two very different outputs; the colleague did not change. "
         "Class question: what would you tell a new colleague so they could not misunderstand 'extract the passenger data'?")

s = ds.table_slide(prs, "Chat prompts have three roles, and the model learned them as a strong convention",
                   ["Role", "Who speaks", "What it is for"],
                   [["system", "the operator (you, the developer)", "who the model is, the standing rules, the output format; set once"],
                    ["user", "the person asking", "the actual request and the text to work on"],
                    ["assistant", "the model", "its answers; you may write these yourself as examples of what you want"]],
                   kicker="What a prompt really is", col_widths=[1, 2, 5],
                   note="Under the hood a template glues the roles into one string. Roles are text, but text the model was trained to respect.")
notes(s, "Talk track: the system message is where rules live because training taught the model to weigh it. Writing assistant turns yourself is how few-shot examples work in chat models.")

s = ds.bullets_slide(prs, "Why words change the output: the model learns your task from the prompt itself",
                     ["Brown et al. 2020 (GPT-3): a large model learns a new task from a few examples placed in the prompt, with no training. They called it in-context learning.",
                      "Zero-shot, one-shot, few-shot: the number of examples became a dial, and accuracy rose with it on task after task.",
                      "In plain words: the model treats your prompt as a pattern and continues the pattern.",
                      "Under the hood: P(next token | prompt). Change the prompt, change the probability of every token that follows.",
                      "Limit: a prompt can only unlock what training put in. It cannot add a skill the model never learned."],
                     kicker="In-context learning",
                     note="Source: Brown et al., Language Models are Few-Shot Learners, NeurIPS 2020.")
notes(s, "Talk track: this is the one paper to remember. The dial from zero-shot to few-shot is why examples are a rung of the ladder. "
         "Class question: if the model only predicts likely continuations, why would 'answer in JSON' work at all? Because JSON after 'answer in JSON' is the likely continuation.")

s = ds.table_slide(prs, "The prompt ladder: each rung removes one kind of guess",
                   ["Rung", "What you add", "The guess it removes", "Where it comes from"],
                   [["0", "a vague ask", "nothing; the baseline", ""],
                    ["1", "specification: task, fields, allowed values, exact format", "what you want and in what shape", "requirements writing"],
                    ["2", "rules: your conventions and edge cases", "how to handle the ambiguous cases", "the model cannot know your conventions"],
                    ["3", "role in a system message", "how to behave when the text pulls it off course", "chat training"],
                    ["4", "examples: two to four input-output pairs, as conversation turns", "what a perfect answer looks like", "Brown et al. 2020"],
                    ["+", "reasoning steps: \"think step by step\"", "how to solve multi-step problems", "Wei et al. 2022; Kojima et al. 2022"]],
                   kicker="The ladder", col_widths=[0.6, 3, 3, 2.4],
                   note="In plain words: say what you want, say how to handle the tricky cases, say who the model is, show what good looks like. Examples get copied: keep them representative, give them as turns.")
notes(s, "Talk track: the order is roughly the order of return on effort. Most real gains are rungs 1 to 3. "
         "Chain-of-thought is real and large on arithmetic with big models, but on a strict-format job with a small model it often hurts; the notebook measures it as an exercise.")

s = ds.image_slide(prs, "Self-generation: a prompt is text, the model writes text, so the model can write prompts", fig_search_loop(),
                   kicker="Prompts that write prompts",
                   bullets=["Generate candidate prompts, score them on examples with known answers, keep the best, repeat.",
                            "This is a search loop. The prompt is the variable; the scorer is the judge.",
                            "You met this shape in M2 notebook 3: grid and random search over hyperparameters.",
                            "Two hats for one model: the worker runs the prompt, the author writes it."],
                   caption="How to read it: clockwise from the top left; step 4 is what turns blind search into optimization.")
notes(s, "Talk track: this is the slide that should make prompting feel like engineering. Once there is a scorer, everything becomes a loop. "
         "Class question: what do you need before you can run this loop at all? Examples with known answers.")

s = ds.table_slide(prs, "Four flavours of self-generation, each with a paper behind it",
                   ["Flavour", "What the model writes", "Paper", "What they found"],
                   [["self-generated examples", "its own input-output demonstrations", "Kim et al. 2022 (SG-ICL); Zhang et al. 2022 (Auto-CoT)", "demonstrations matter more than who wrote them"],
                    ["self-refine", "a critique of its own draft, then a revision", "Madaan et al. 2023", "gains across dialogue, math and code with no extra training"],
                    ["instruction induction (APE)", "the instruction that would produce given outputs; many candidates, keep the best", "Zhou et al. 2022", "a searched prompt beat the human \"Let's think step by step\""],
                    ["optimizer loop (OPRO, GEPA)", "a better instruction after reading past scores (2023) or the actual failures (2025)", "Yang et al. 2023; Agrawal et al. 2025", "\"Take a deep breath and work on this problem step-by-step\""]],
                   kicker="Prompts that write prompts", col_widths=[1.8, 3, 2.4, 3],
                   note="In plain words: the model writes the examples, grades its own homework, writes the instruction, or reads the scoreboard and writes a better one.")
notes(s, "Talk track: name the four, then say the notebook runs all four. Students do not need to memorize authors; they need to recognize the loop in each.")

s = ds.table_slide(prs, "Prompts found by search beat prompts written by people, on the same benchmarks",
                   ["Benchmark", "Human prompt", "Score", "Prompt found by search", "Score"],
                   [["MultiArith (APE, Zhou et al. 2022)", "\"Let's think step by step\"", "78.7", "\"Let's work this out in a step by step way to be sure we have the right answer\"", "82.0"],
                    ["GSM8K (APE, Zhou et al. 2022)", "\"Let's think step by step\"", "40.7", "same searched prompt", "43.0"],
                    ["GSM8K, PaLM 2-L (OPRO, Yang et al. 2023)", "\"Let's think step by step\"", "71.8", "\"Take a deep breath and work on this problem step-by-step\"", "80.2"]],
                   kicker="Prompts that write prompts", col_widths=[2.6, 2.2, 0.8, 3.6, 0.8],
                   note="Scores are accuracy in percent as reported in the papers. Nobody typed the winning prompts; a loop like the one on the previous slide found them.")
notes(s, "Talk track: the surprise is not the size of the gain, it is that a program found wording no human proposed. "
         "Class question: why might 'take a deep breath' help a model that does not breathe? Because in its training text those words precede careful, step-by-step writing.")

s = ds.two_col_slide(prs, "Where this is going: prompt optimization as software, and a division of labour",
                     ("Programming, not prompting", ["Khattab et al. 2023 (DSPy): declare inputs, outputs and a scorer; an optimizer writes the instructions and picks the examples.",
                                                     "Every major provider now ships a \"generate a prompt for me\" button.",
                                                     "The scorer is the part you cannot outsource: it encodes what good means for you."]),
                     ("Big writes, small runs", ["A frontier model writes and tunes the prompt once.",
                                                 "A small, cheap model runs it millions of times.",
                                                 "The notebook shows why: the small model is a fair worker and a weak author.",
                                                 "Optional section 10 lets a frontier model be the author, key kept in memory only."]),
                     kicker="Prompts that write prompts")
notes(s, "Talk track: this is the industry pattern behind most production LLM systems in 2026. The author and the worker need not be the same model.")

s = ds.two_col_slide(prs, "The honesty rule from M2 applies to prompts: choose on dev, report on test",
                     ("Choosing", ["Score every candidate prompt on a development set.",
                                   "Pick the winner by that score.",
                                   "That score is now optimistic: you picked the winner because it did well there."]),
                     ("Reporting", ["Keep a test set the choice never touched.",
                                    "Score the chosen prompt there once.",
                                    "In plain words: the exam you studied from is not the exam that counts.",
                                    "Ten rows is a classroom ruler: one row is ten points."]),
                     kicker="Measure, do not argue",
                     note="Selection versus assessment, exactly as in M2 notebook 2. The notebook splits 24 passengers into 4 demo, 10 dev and 10 test.")
notes(s, "Talk track: students who did M2 should recognize this instantly. Make them say it: dev is for choosing, test is for reporting.")

ds.section_slide(prs, "02", "Part 2 - Practice", "Notebook M4-01: a small model, one job, a scoreboard, and a loop")

s = ds.bullets_slide(prs, "The job: turn a sentence about a passenger into the JSON the M3 API expects",
                     ["Input: \"Florence Cumings, 38, travelled first class with her husband John; they embarked at Cherbourg.\"",
                      "Output: {\"Pclass\": 1, \"Sex\": \"female\", \"Age\": 38, \"SibSp\": 1, \"Parch\": 0, \"Embarked\": \"C\"}",
                      "24 real passengers from the course dataset, each written as one sentence; the true row is the answer key.",
                      "Conventions the model cannot guess: SibSp counts siblings and spouses, Parch parents and children, \"steerage\" is class 3, ports are letters.",
                      f"Worker: {R['model']}, about {WORKER_B} billion parameters, runs on a laptop GPU or Apple silicon (a 0.5B sibling on plain CPUs). Small on purpose: it is sensitive to the prompt, so the rungs show."],
                     kicker="The setup",
                     note="A frontier model would do this well with any prompt and teach nothing. Everything learned here transfers upward.")
notes(s, "Talk track: read the sentence and the JSON aloud. Ask the class which parts are easy (age, port) and which need a convention (husband: SibSp or Parch?).")

s = ds.table_slide(prs, "Three numbers per prompt, and each tells a different story",
                   ["Metric", "Question it answers", "Why it matters"],
                   [["valid_json", "did the model answer in the right shape?", "no JSON means the API call fails before any field is read"],
                    ["field_accuracy", "of all fields across all passengers, what share is exactly right?", "the headline number; six fields times ten passengers"],
                    ["perfect_rows", "what share of passengers is right in all six fields?", "what the API would actually accept"]],
                   kicker="The scorer", col_widths=[1.4, 3.4, 3.6],
                   note="The scorer is strict on purpose: \"Southampton\" where \"S\" is expected is a failed request, not a near miss.")
notes(s, "Talk track: strictness is a design decision. Ask: should the scorer accept 'Southampton'? If it did, the prompt would never learn to say the code.")

s = ds.image_slide(prs, f"Rung 1 alone takes the model from {pct(R['dev']['0 vague ask']['field_accuracy'])} to {pct(R['dev']['1 + specification']['field_accuracy'])} of fields right",
                   fig_scores(LADDER, "dev", "The prompt ladder on the dev set", "ladder.png", ""),
                   kicker="Climbing the ladder",
                   bullets=[f"Rung 0 produced valid JSON for {pct(R['dev']['0 vague ask']['valid_json'])} of passengers: prose, lists, questions back.",
                            "Specification is the cheapest rung and the largest jump: fields, allowed values, \"JSON only\".",
                            "Rules, examples and the role move the score by a few points on this small model, up and down.",
                            "Ten passengers: one passenger is ten points of perfect_rows. Read small gaps as noise."],
                   caption="How to read it: one row per rung, top to bottom; dark bar = share of fields right, light bar = passengers perfect in all six.")
notes(s, "Talk track: the shape repeats on every machine, the exact numbers wobble. The lesson is the size of the first step. "
         "Class question: why would examples ever make a small model worse? Longer prompts, more to attend to, and the examples may not match the case at hand.")

s = ds.image_slide(prs, "Class, age and port are solved by rung 1 or 2; the two family counts stay near " + FAM_PCT + " on every rung", fig_fields(),
                   kicker="Where prompting stops",
                   bullets=["Class, age and port: the specification and one rule about \"steerage\" settle them. Sex slips on one unusual first name.",
                            "SibSp and Parch: the model reads \"with her mother and her sister\" and must route each relative to the right counter, a two-step job.",
                            "Rules and examples move these two columns a little; no rung brings them level with the others.",
                            "When no wording moves a column any more, you have found a skill the model lacks: the line between a better prompt and a bigger model."],
                   caption="How to read it: one bar per field, rung 4, dev set; dark bars are at or above 85 percent, light bars mark the ceiling.")
notes(s, "Talk track: this chart earns the whole module its honesty. Ask students where they would spend the next hour: on the prompt, or on the model?")

s = ds.image_slide(prs, "Self-generated prompts, scored once on the sealed test set next to the hand-written rungs",
                   fig_scores(LADDER + SELF, "test", "Test set: every approach scored once", "scoreboard.png", ""),
                   kicker="The honest scoreboard",
                   bullets=["self-examples: the model invented its own demonstrations. When they are inconsistent, the worker learns the inconsistency.",
                            "self-refine: draft, critique, revise. Fixes slips, cannot fix conventions the critic does not know.",
                            "APE best: the best of six instructions the model wrote from four input-output pairs.",
                            "OPRO best: the winner of three reflective rounds. In this run it copied dev passengers with their answers into the prompt: top score on dev, points back on test."],
                   caption="How to read it: the top five rows are human-written rungs, the bottom four are model-written; longer is better.")
notes(s, "Talk track: point at the model-written rows. Without a human writing a single rule, search found an instruction in the league of the human rungs. "
         "Then point at the gap to the top human rung: the small author is the weak link.")

s = ds.image_slide(prs, "The optimizer reads its own failures, edits the instruction, keeps the best: a climb in three rounds", fig_opro(),
                   kicker="OPRO with a reflection step",
                   bullets=["Round 0 starts from the better of two seeds: the human specification and the best APE candidate.",
                            "Each round: show the best instruction and three passengers it gets wrong, ask for an edit that keeps what works and fixes the failures, sample two, score them.",
                            "The line can only go up or stay flat: we always keep the best.",
                            "The pure scoreboard version (OPRO 2023) stayed flat with this small author; the reflective version (GEPA 2025) climbs. Measured, not assumed."],
                   caption="How to read it: x is the round, y is the best dev score so far; the numbers are percent of fields right.")
notes(s, "Talk track: this is the smallest possible version of the loop that found 'take a deep breath', with the 2025 twist: traces instead of scores. Same mechanism, smaller author, smaller budget.")

gap_rows = [[n, pct(R["dev"][n]["field_accuracy"]), pct(R["test"][n]["field_accuracy"]),
             f"{(R['test'][n]['field_accuracy'] - R['dev'][n]['field_accuracy']) * 100:+.0f}"] for n in ["1 + specification", "4 + examples", "APE best", "OPRO best"]]
s = ds.table_slide(prs, "Dev versus test: prompts chosen by their dev score lose the most on test",
                   ["Prompt", "dev (used to choose)", "test (sealed)", "gap, points"], gap_rows,
                   kicker="The honesty rule in numbers", col_widths=[2.4, 2, 2, 1.6],
                   note="Hand-written rungs were chosen by no score, so they move less. With ten rows, a gap of one row is about two points of field accuracy: read only the large gaps.")
notes(s, "Talk track: the selection effect made visible. Ask: which number would you put in a report to your manager, and why?")

ds.close_slide(prs, "What to take home", [
    "The prompt is the only steering wheel: everything you do not say, the model guesses.",
    "In-context learning is why words work; specification, rules and examples each remove a kind of guess.",
    "Measure, do not argue: a scored set turns prompting into engineering. Choose on dev, report on test.",
    "Self-generation is a search loop: propose, score, keep, learn. APE and OPRO found prompts no human wrote.",
    "A weak author writes weak prompts: big writes, small runs.",
    "Prompting unlocks, it does not add: when no rung helps, change the model.",
], course=COURSE)

out = HERE.parent / "m4-session-1-the-power-of-prompting.pptx"
ds.save_deck(prs, str(out), "M4 Session 1 - The Power of Prompting")
print(f"wrote {out} ({len(prs.slides)} slides)")
