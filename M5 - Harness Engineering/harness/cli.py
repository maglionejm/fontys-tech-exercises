"""Command line: ``python -m harness ask|eval|show`` from the module folder.

Configurations: A = no tools, B = tools without the validator, C = tools plus
``require_sources`` (sources must not be empty when found is true).
"""
from __future__ import annotations

import argparse
import sys
from typing import Callable

from .client import MAIN_MODEL, load_client
from .evals import ANSWER_SCHEMA, RESEARCHER_SYSTEM, RESEARCHER_SYSTEM_NO_TOOLS, compare, load_cases, read_results, write_results
from .hooks import Hooks, require_sources
from .loop import Agent
from .repo_tools import list_files, read_file

CONFIGS = ("A", "B", "C")


def make_factory(config: str, client, model: str = MAIN_MODEL, max_turns: int = 8, effort: str = "medium") -> Callable[[], Agent]:
    """A function that builds a fresh researcher for configuration A, B or C."""
    if config not in CONFIGS:
        raise ValueError(f"config must be one of {CONFIGS}")

    def factory() -> Agent:
        common = dict(model=model, output_schema=ANSWER_SCHEMA, max_turns=max_turns, effort=effort,
                      name=f"researcher-{config}")
        if config == "A":
            return Agent(client, system=RESEARCHER_SYSTEM_NO_TOOLS, tools=[], **common)
        hooks = Hooks(validate_answer=[require_sources]) if config == "C" else Hooks()
        return Agent(client, system=RESEARCHER_SYSTEM, tools=[list_files, read_file], hooks=hooks, **common)

    return factory


def cmd_ask(args: argparse.Namespace) -> int:
    agent = make_factory(args.config, load_client(), args.model, args.max_turns)()
    result = agent.run(args.question)
    data = result.parsed or {}
    print(data.get("answer", result.answer))
    print(f"found: {data.get('found')}   sources: {data.get('sources', [])}")
    print(f"[{result.stopped_because} after {result.turns} turn(s), {result.usage.total_input} in / "
          f"{result.usage.output_tokens} out tokens, ${result.cost_usd:.4f} on {result.model}]")
    if args.trace:
        result.trace.show()
    return 0


def cmd_eval(args: argparse.Namespace) -> int:
    client = load_client()
    cases = load_cases(args.cases)
    configs = CONFIGS if args.config == "all" else (args.config,)
    reports = compare({c: make_factory(c, client, args.model, args.max_turns) for c in configs}, cases)
    for report in reports.values():
        report.show()
    if args.out:
        print(f"written: {write_results(reports, args.out)}")
    return 0


def cmd_show(args: argparse.Namespace) -> int:
    print(f"{'config':<8} {'pass rate':>9} {'cases':>6} {'in tokens':>10} {'out tokens':>10} {'cost USD':>9}")
    for report in read_results(args.results):
        usage = report["usage"]
        total_in = usage["input_tokens"] + usage["cache_read_input_tokens"] + usage["cache_creation_input_tokens"]
        print(f"{report['name']:<8} {report['pass_rate']:>9.0%} {len(report['rows']):>6} {total_in:>10} "
              f"{usage['output_tokens']:>10} {report['cost_usd']:>9.4f}")
        for row in report["rows"]:
            if not row["passed"]:
                print(f"    FAIL {row['case']}: {'; '.join(row['failures'])}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="python -m harness", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    ask = sub.add_parser("ask", help="ask the researcher one question about the repository")
    ask.add_argument("question")
    ask.add_argument("--model", default=MAIN_MODEL)
    ask.add_argument("--max-turns", type=int, default=8)
    ask.add_argument("--config", choices=CONFIGS, default="C")
    ask.add_argument("--trace", action="store_true", help="print the step log")
    ask.set_defaults(func=cmd_ask)

    ev = sub.add_parser("eval", help="run the eval cases through one or all configurations")
    ev.add_argument("cases")
    ev.add_argument("--config", choices=(*CONFIGS, "all"), default="all")
    ev.add_argument("--model", default=MAIN_MODEL)
    ev.add_argument("--max-turns", type=int, default=8)
    ev.add_argument("--out", help="write results as JSON")
    ev.set_defaults(func=cmd_eval)

    show = sub.add_parser("show", help="print the scoreboard of a results file")
    show.add_argument("results")
    show.set_defaults(func=cmd_show)
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
